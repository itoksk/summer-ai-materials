#!/usr/bin/env python3
"""ヒアリングGemの出力を microgpt 用の input.txt に変換するスクリプト。

Gem(materials/gems/hearing-gem.md)が出力したコーパス(1行=1文)を受け取り、
microgpt.py がそのまま学習できる形に整える:

  - コードブロック記号・番号・引用符などの飾りを除去
  - Unicode 正規化(NFC)と空白の整理
  - 個人情報らしき行(URL / メール / 電話番号)を除外して警告
  - 長すぎる行を切り詰め(文字レベルGPTは短い行ほど速く学べる)
  - 重複行を除去
  - 行数が少なすぎる場合は --augment でシャッフル反復して水増し
    (microgpt は学習中にデータを自動で周回するので必須ではない)

使い方:
  python3 gem_to_corpus.py my_corpus.txt
  python3 gem_to_corpus.py my_corpus.txt -o input.txt --max-chars 40 --augment

依存ライブラリなし(Python 3.8+ の標準ライブラリのみ)。
"""

import argparse
import random
import re
import statistics
import sys
import unicodedata

# 個人情報・ノイズの検出パターン(該当行はコーパスから外して警告する)
RE_URL = re.compile(r"https?://|www\.")
RE_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
RE_PHONE = re.compile(r"\d{2,4}[-\s]?\d{2,4}[-\s]?\d{3,4}")
# 行頭の飾り: 番号("1. " "12) ")、箇条書き記号、引用記号
RE_DECOR = re.compile(r"^\s*(?:\d{1,3}[.)]\s*|[-*>・]\s*)")


def clean_line(line: str) -> str:
    line = unicodedata.normalize("NFC", line)
    line = RE_DECOR.sub("", line)
    line = line.strip().strip('"“”「」').strip()
    line = re.sub(r"\s+", " ", line)
    return line


def truncate(line: str, max_chars: int) -> str:
    if len(line) <= max_chars:
        return line
    cut = line[:max_chars]
    # なるべく単語・文節の切れ目(空白か句読点)で切る
    for i in range(len(cut) - 1, max(0, max_chars - 12), -1):
        if cut[i] in " 、。!?！？,.":
            return cut[: i + 1].rstrip()
    return cut


def extract_lines(text: str) -> list[str]:
    """フェンス付きコードブロックがあればその中身を、なければ全文を行リストにする。"""
    blocks = re.findall(r"```[\w-]*\n(.*?)```", text, flags=re.DOTALL)
    body = "\n".join(blocks) if blocks else text
    return body.splitlines()


def main() -> int:
    ap = argparse.ArgumentParser(description="Gem corpus -> microgpt input.txt")
    ap.add_argument("source", help="Gemの出力を保存したテキストファイル(例: my_corpus.txt)")
    ap.add_argument("-o", "--output", default="input.txt", help="出力先(既定: input.txt)")
    ap.add_argument("--max-chars", type=int, default=40, help="1行の最大文字数(既定: 40)")
    ap.add_argument("--min-chars", type=int, default=4, help="これより短い行は捨てる(既定: 4)")
    ap.add_argument("--min-lines", type=int, default=150, help="--augment 時の目標行数(既定: 150)")
    ap.add_argument("--augment", action="store_true", help="行数が足りない場合シャッフル反復で水増しする")
    ap.add_argument("--seed", type=int, default=42, help="--augment 用の乱数シード")
    args = ap.parse_args()

    try:
        text = open(args.source, encoding="utf-8").read()
    except OSError as e:
        print(f"error: {args.source} を読めません: {e}", file=sys.stderr)
        return 1

    kept: list[str] = []
    dropped_pii = 0
    seen = set()
    for raw in extract_lines(text):
        line = clean_line(raw)
        if len(line) < args.min_chars:
            continue
        if RE_URL.search(line) or RE_EMAIL.search(line) or RE_PHONE.search(line):
            dropped_pii += 1
            continue
        line = truncate(line, args.max_chars)
        if line in seen:
            continue
        seen.add(line)
        kept.append(line)

    if not kept:
        print("error: 使える行が1行もありません。Gemの出力を確認してください。", file=sys.stderr)
        return 1

    corpus = list(kept)
    if args.augment and len(corpus) < args.min_lines:
        rng = random.Random(args.seed)
        while len(corpus) < args.min_lines:
            batch = list(kept)
            rng.shuffle(batch)
            corpus.extend(batch)
        corpus = corpus[: max(args.min_lines, len(kept))]

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(corpus) + "\n")

    lengths = [len(l) for l in kept]
    vocab = sorted(set("".join(kept)))
    print(f"wrote {args.output}: {len(corpus)} lines ({len(kept)} unique)")
    print(f"  line length  min {min(lengths)} / median {int(statistics.median(lengths))} / max {max(lengths)}")
    print(f"  vocab size   {len(vocab) + 1} (unique chars + BOS)")
    if dropped_pii:
        print(f"  note: URL・メール・電話番号らしき {dropped_pii} 行を除外しました")
    if len(kept) < 80:
        print("  warning: 行数が少なめです。Gemにもう少しインタビューに答えてから再出力させると良くなります")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
