#!/usr/bin/env python3
"""microgpt_lab.py — microgpt.py(@karpathy)を実験用にパラメータ化したもの。

アルゴリズムは microgpt.py と同一(純Python・依存ライブラリなしの文字レベルGPT)。
違いは「実験のしやすさ」だけ:

  - 学習データ・ステップ数・モデルサイズ・文脈長をコマンドラインで変えられる
  - 1回の訓練で複数の温度(temperature)のサンプルをまとめて出力できる
  - 進捗(loss と経過時間)を定期的に表示する
  - --chat で、訓練後に「双子」と対話できる(文の出だしを与えると続きを書く)

使い方の例:
  python3 microgpt_lab.py --input input.txt
  python3 microgpt_lab.py --input input_haiku.txt --steps 500 --block-size 32
  python3 microgpt_lab.py --input input.txt --temperatures 0.1 0.5 1.0 2.0
  python3 microgpt_lab.py --input input_me.txt --steps 600 --block-size 40 --chat

  # 1回だけ学習して保存 → 次からは読み込んで(学習せずに)チャットだけ
  python3 microgpt_lab.py --input input_me.txt --steps 600 --block-size 40 --save twin.json
  python3 microgpt_lab.py --load twin.json --chat

元コード: https://github.com/karpathy (microgpt)
"""

import argparse
import json
import math
import random
import time


# ---- Autograd(microgpt.py と同じ) ----
class Value:
    __slots__ = ('data', 'grad', '_children', '_local_grads')

    def __init__(self, data, children=(), local_grads=()):
        self.data = data
        self.grad = 0
        self._children = children
        self._local_grads = local_grads

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        return Value(self.data + other.data, (self, other), (1, 1))

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        return Value(self.data * other.data, (self, other), (other.data, self.data))

    def __pow__(self, other): return Value(self.data**other, (self,), (other * self.data**(other-1),))
    def log(self): return Value(math.log(self.data), (self,), (1/self.data,))
    def exp(self): return Value(math.exp(self.data), (self,), (math.exp(self.data),))
    def relu(self): return Value(max(0, self.data), (self,), (float(self.data > 0),))
    def __neg__(self): return self * -1
    def __radd__(self, other): return self + other
    def __sub__(self, other): return self + (-other)
    def __rsub__(self, other): return other + (-self)
    def __rmul__(self, other): return self * other
    def __truediv__(self, other): return self * other**-1
    def __rtruediv__(self, other): return other * self**-1

    def backward(self):
        topo = []
        visited = set()
        def build_topo(v):
            if v not in visited:
                visited.add(v)
                for child in v._children:
                    build_topo(child)
                topo.append(v)
        build_topo(self)
        self.grad = 1
        for v in reversed(topo):
            for child, local_grad in zip(v._children, v._local_grads):
                child.grad += local_grad * v.grad


def main():
    ap = argparse.ArgumentParser(description="microgpt experiment lab")
    ap.add_argument("--input", default="input.txt", help="学習データ(1行=1ドキュメント)")
    ap.add_argument("--steps", type=int, default=1000, help="訓練ステップ数(既定: 1000)")
    ap.add_argument("--block-size", type=int, default=16, help="文脈長。行の最初の何文字まで学べるか(既定: 16)")
    ap.add_argument("--n-layer", type=int, default=1, help="層の数(既定: 1)")
    ap.add_argument("--n-embd", type=int, default=16, help="埋め込みの幅。4の倍数(既定: 16)")
    ap.add_argument("--temperatures", type=float, nargs="+", default=[0.5], help="サンプル生成の温度(複数可)")
    ap.add_argument("--num-samples", type=int, default=10, help="温度ごとのサンプル数(既定: 10)")
    ap.add_argument("--seed", type=int, default=42, help="乱数シード(既定: 42)")
    ap.add_argument("--chat", action="store_true", help="訓練後に対話モードに入る。文の出だしを入力すると双子が続きを書く")
    ap.add_argument("--save", default=None, help="訓練後にモデルを保存するJSONファイル(例: twin.json)")
    ap.add_argument("--load", default=None, help="保存済みモデルを読み込み、訓練せずに生成・チャットする(例: twin.json)")
    args = ap.parse_args()

    random.seed(args.seed)
    n_head = 4

    if args.load:
        # 保存済みモデルを読み込む。データ読み込みと訓練はスキップして、生成・チャットへ。
        with open(args.load, encoding="utf-8") as f:
            ckpt = json.load(f)
        n_layer, n_embd, block_size = ckpt["n_layer"], ckpt["n_embd"], ckpt["block_size"]
        uchars = ckpt["uchars"]
        state_dict = {k: [[Value(x) for x in row] for row in mat] for k, mat in ckpt["state_dict"].items()}
        params, docs = [], []
        args.steps = 0  # 訓練ループは回さない
        print(f"loaded model: {args.load} | vocab: {len(uchars) + 1} | block_size: {block_size}")
    else:
        n_layer, n_embd, block_size = args.n_layer, args.n_embd, args.block_size
        # データセット: 1行 = 1ドキュメント
        docs = [line.strip() for line in open(args.input, encoding="utf-8") if line.strip()]
        random.shuffle(docs)
        uchars = sorted(set("".join(docs)))
        print(f"docs: {len(docs)} | vocab: {len(uchars) + 1} | block_size: {block_size}")
        if len(uchars) + 1 > 200:
            print("warning: 語彙(ユニーク文字数)が多いので訓練がかなり遅くなります。"
                  "データをひらがな化・ASCII化すると速くなります")
        # パラメータ初期化(microgpt.py と同じ構成)
        matrix = lambda nout, nin, std=0.08: [[Value(random.gauss(0, std)) for _ in range(nin)] for _ in range(nout)]
        state_dict = {'wte': matrix(len(uchars) + 1, n_embd), 'wpe': matrix(block_size, n_embd), 'lm_head': matrix(len(uchars) + 1, n_embd)}
        for i in range(n_layer):
            state_dict[f'layer{i}.attn_wq'] = matrix(n_embd, n_embd)
            state_dict[f'layer{i}.attn_wk'] = matrix(n_embd, n_embd)
            state_dict[f'layer{i}.attn_wv'] = matrix(n_embd, n_embd)
            state_dict[f'layer{i}.attn_wo'] = matrix(n_embd, n_embd)
            state_dict[f'layer{i}.mlp_fc1'] = matrix(4 * n_embd, n_embd)
            state_dict[f'layer{i}.mlp_fc2'] = matrix(n_embd, 4 * n_embd)
        params = [p for mat in state_dict.values() for row in mat for p in row]
        print(f"params: {len(params)}")

    assert n_embd % n_head == 0, "--n-embd は 4 の倍数にしてください"
    head_dim = n_embd // n_head
    stoi = {ch: i for i, ch in enumerate(uchars)}
    BOS = len(uchars)
    vocab_size = len(uchars) + 1

    def linear(x, w):
        return [sum(wi * xi for wi, xi in zip(wo, x)) for wo in w]

    def softmax(logits):
        max_val = max(val.data for val in logits)
        exps = [(val - max_val).exp() for val in logits]
        total = sum(exps)
        return [e / total for e in exps]

    def rmsnorm(x):
        ms = sum(xi * xi for xi in x) / len(x)
        scale = (ms + 1e-5) ** -0.5
        return [xi * scale for xi in x]

    def gpt(token_id, pos_id, keys, values):
        tok_emb = state_dict['wte'][token_id]
        pos_emb = state_dict['wpe'][pos_id]
        x = [t + p for t, p in zip(tok_emb, pos_emb)]
        x = rmsnorm(x)
        for li in range(n_layer):
            x_residual = x
            x = rmsnorm(x)
            q = linear(x, state_dict[f'layer{li}.attn_wq'])
            k = linear(x, state_dict[f'layer{li}.attn_wk'])
            v = linear(x, state_dict[f'layer{li}.attn_wv'])
            keys[li].append(k)
            values[li].append(v)
            x_attn = []
            for h in range(n_head):
                hs = h * head_dim
                q_h = q[hs:hs+head_dim]
                k_h = [ki[hs:hs+head_dim] for ki in keys[li]]
                v_h = [vi[hs:hs+head_dim] for vi in values[li]]
                attn_logits = [sum(q_h[j] * k_h[t][j] for j in range(head_dim)) / head_dim**0.5 for t in range(len(k_h))]
                attn_weights = softmax(attn_logits)
                head_out = [sum(attn_weights[t] * v_h[t][j] for t in range(len(v_h))) for j in range(head_dim)]
                x_attn.extend(head_out)
            x = linear(x_attn, state_dict[f'layer{li}.attn_wo'])
            x = [a + b for a, b in zip(x, x_residual)]
            x_residual = x
            x = rmsnorm(x)
            x = linear(x, state_dict[f'layer{li}.mlp_fc1'])
            x = [xi.relu() for xi in x]
            x = linear(x, state_dict[f'layer{li}.mlp_fc2'])
            x = [a + b for a, b in zip(x, x_residual)]
        logits = linear(x, state_dict['lm_head'])
        return logits

    # Adam オプティマイザ
    learning_rate, beta1, beta2, eps_adam = 0.01, 0.85, 0.99, 1e-8
    m = [0.0] * len(params)
    v = [0.0] * len(params)

    # 訓練ループ
    num_steps = args.steps
    t0 = time.time()
    report_every = max(1, num_steps // 10)
    for step in range(num_steps):
        doc = docs[step % len(docs)]
        tokens = [BOS] + [stoi[ch] for ch in doc] + [BOS]
        n = min(block_size, len(tokens) - 1)

        keys, values = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]
        losses = []
        for pos_id in range(n):
            token_id, target_id = tokens[pos_id], tokens[pos_id + 1]
            logits = gpt(token_id, pos_id, keys, values)
            probs = softmax(logits)
            loss_t = -probs[target_id].log()
            losses.append(loss_t)
        loss = (1 / n) * sum(losses)
        loss.backward()

        lr_t = learning_rate * (1 - step / num_steps)
        for i, p in enumerate(params):
            m[i] = beta1 * m[i] + (1 - beta1) * p.grad
            v[i] = beta2 * v[i] + (1 - beta2) * p.grad ** 2
            m_hat = m[i] / (1 - beta1 ** (step + 1))
            v_hat = v[i] / (1 - beta2 ** (step + 1))
            p.data -= lr_t * m_hat / (v_hat ** 0.5 + eps_adam)
            p.grad = 0

        if (step + 1) % report_every == 0 or step == 0:
            elapsed = time.time() - t0
            print(f"step {step+1:5d} / {num_steps} | loss {loss.data:.4f} | {elapsed:6.1f}s")

    # 保存: 重みと語彙をJSONに書き出す(次回 --load で訓練なしに使える)
    if args.save:
        ckpt = {
            "n_layer": n_layer, "n_embd": n_embd, "block_size": block_size,
            "uchars": uchars,
            "state_dict": {k: [[p.data for p in row] for row in mat] for k, mat in state_dict.items()},
        }
        with open(args.save, "w", encoding="utf-8") as f:
            json.dump(ckpt, f)
        print(f"saved model: {args.save}")

    # 生成: 温度ごとにサンプルを出力
    for temperature in args.temperatures:
        print(f"\n--- temperature {temperature} ---")
        for sample_idx in range(args.num_samples):
            keys, values = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]
            token_id = BOS
            sample = []
            for pos_id in range(block_size):
                logits = gpt(token_id, pos_id, keys, values)
                probs = softmax([l / temperature for l in logits])
                token_id = random.choices(range(vocab_size), weights=[p.data for p in probs])[0]
                if token_id == BOS:
                    break
                sample.append(uchars[token_id])
            print(f"sample {sample_idx+1:2d}: {''.join(sample)}")

    # 対話: 学習した「双子」に文の出だしを与え、続きを書かせる
    # (本物の対話モデルではない。文字レベルの「次の1文字予測」で続きを作るだけ)
    if args.chat:
        temperature = args.temperatures[0]
        print(f"\n--- あなたの双子と話す / chat with your twin (temperature {temperature}) ---")
        print("文の出だしを入力すると、双子が「君の口調」で続きを書きます。")
        print("Type the start of a line; your twin finishes it in your voice.")
        print("空行か Ctrl-C で終了 / empty line or Ctrl-C to quit.\n")
        while True:
            try:
                seed = input("you  > ")
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if seed.strip() == "":
                break
            keys, values = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]
            seed_ids = [stoi[ch] for ch in seed if ch in stoi]
            logits, pos_id = None, 0
            for tok in [BOS] + seed_ids:   # BOS と入力文字を順に食わせて文脈を作る
                if pos_id >= block_size:
                    break
                logits = gpt(tok, pos_id, keys, values)
                pos_id += 1
            twin = []
            while logits is not None and pos_id < block_size:
                probs = softmax([l / temperature for l in logits])
                token_id = random.choices(range(vocab_size), weights=[p.data for p in probs])[0]
                if token_id == BOS:
                    break
                twin.append(uchars[token_id])
                logits = gpt(token_id, pos_id, keys, values)
                pos_id += 1
            print(f"twin > {seed}{''.join(twin)}\n")


if __name__ == "__main__":
    main()
