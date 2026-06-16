#!/usr/bin/env python3
"""Generate the 4 Colab notebooks for summer-ai materials/notebooks/."""
import json
import os

ROOT = "/Users/keisuke/git/summer-ai"
OUT = os.path.join(ROOT, "materials", "notebooks")
os.makedirs(OUT, exist_ok=True)

MICROGPT_SRC = open(os.path.join(ROOT, "microgpt-lab", "microgpt.py"), encoding="utf-8").read()
LAB_SRC = open(os.path.join(ROOT, "materials", "scripts", "microgpt_lab.py"), encoding="utf-8").read()
CORPUS_SRC = open(os.path.join(ROOT, "materials", "scripts", "gem_to_corpus.py"), encoding="utf-8").read()


def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source}


def code(source):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": source}


def write_nb(filename, cells, title):
    nb = {
        "nbformat": 4,
        "nbformat_minor": 0,
        "metadata": {
            "colab": {"provenance": [], "name": title},
            "kernelspec": {"name": "python3", "display_name": "Python 3"},
            "language_info": {"name": "python"},
        },
        "cells": cells,
    }
    path = os.path.join(OUT, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print("wrote", path)


# ---------------------------------------------------------------- microgpt
cells = []
cells.append(md('''# microgpt ラボ — 200行で GPT を育てる / The 200-line GPT Lab

ChatGPT の「超ミニ版」を、たった **200行の Python** で動かします。ライブラリなし。かくしごとなし。全部このノートの中で見えます。

**今日やること / Today**
1. ポケモンの名前 1000 体で AI を訓練する
2. 温度(temperature)のつまみで遊ぶ
3. 民謡・チェス・俳句 — データを変えて「別の専門家」を育てる
4. 自分のデータで「自分GPT」を作る

**準備 / Setup**: ランタイムは **CPU のままでOK**(GPU は使いません)。上のメニューから「ランタイム → すべてのセルを実行」はせず、**1つずつ順番に**実行してください。

> やさしい日本語メモ: 「訓練(くんれん)」= AI にデータをたくさん見せて、まねできるように育てること。'''))
cells.append(md('''## Step 1 — microgpt.py をこの Colab に置く / Get microgpt.py

下のセルを実行すると、`microgpt.py` がこの Colab に保存されます。これが **全部** です。この 200 行の外に魔法はありません。

(作者: Andrej Karpathy。コースサイトの Day 2 ページにコードの読み方ガイドがあります)'''))
cells.append(code("%%writefile microgpt.py\n" + MICROGPT_SRC))
cells.append(md('''## Step 2 — ポケモンの名前 1000 体で訓練する / Train on Pokémon names

学習データ `input.txt` は「1行に1つの名前」が並んだだけのファイルです。AI がやるのは **「次の1文字を当てる」** ゲームだけ。それを何百回もくり返すと、名前の「らしさ」を覚えます。'''))
cells.append(code('''# ポケモンの名前データをダウンロードして input.txt にする
import urllib.request
url = "https://raw.githubusercontent.com/itoksk/summer-ai-materials/main/materials/data/pokemon.txt"
urllib.request.urlretrieve(url, "input.txt")
lines = open("input.txt").read().splitlines()
print(f"{len(lines)} 行 / lines")
print("\\n".join(lines[:10]))'''))
cells.append(md('''実行中の見方 / How to read the output:
- `loss` = まちがい度。**下がっていけば学んでいる**証拠
- 終わると「図鑑にいない新ポケモン」の名前が 20 個出ます

(数分かかります。loss が動くのをながめるのも勉強のうち)'''))
cells.append(code("!python3 microgpt.py"))
cells.append(md('''### 観察タイム / Observe

- どの名前が「ありそう」? 声に出して読んでみよう
- 本物の図鑑にある名前がそのまま出た? それは「創作」ではなく「丸暗記」かも
- となりの人と「ベスト新ポケモン」を1体ずつ選ぼう'''))
cells.append(md('''## Step 3 — 実験室: つまみをいじる / The experiment lab

ここからは `microgpt_lab.py` を使います。**アルゴリズムは Step 1 と同じ**で、実験用のつまみ(データ・ステップ数・温度など)を外から変えられるようにしただけのものです。'''))
cells.append(code("%%writefile microgpt_lab.py\n" + LAB_SRC))
cells.append(md('''### 実験A — 温度(temperature)で遊ぶ / Play with temperature

生成のときの「冒険度」のつまみです。
- **低い(0.1)** = 安全運転。いちばん確率の高い文字ばかり選ぶ
- **高い(2.0)** = 大冒険。確率の低い文字もどんどん選ぶ

ChatGPT にも同じつまみがあります。1回の訓練で、4つの温度のサンプルをまとめて出します。'''))
cells.append(code("!python3 microgpt_lab.py --input input.txt --steps 600 --temperatures 0.1 0.5 1.0 2.0 --num-samples 5"))
cells.append(md('''**問い / Questions**
- 温度 0.1 の名前、おたがい似すぎていない?
- 温度 2.0 では何が起きている?
- 「ちょうどいい創造性」は何度くらい? それは作るものによって変わる?'''))
cells.append(md('''## Step 4 — データセット・メニュー / Dataset menu

同じ 200 行のコードが、**データを変えるだけで別の専門家**になります。3つのデータから1つ選んでください(全部やってもOK)。

| メニュー | データ | 見どころ |
|---|---|---|
| A | フォーク民謡(ABC記譜法) | AI が作曲する。楽譜は音にして聞ける |
| B | チェスの棋譜 | ルールを教えていないのに「合法っぽい手」を指す |
| C | 俳句(ひらがな) | 5-7-5 を守れるか、指を折って数えよう |

**データの入れ方**: 下のセルを実行すると、3つのデータセットが自動でダウンロードされます(アップロード不要)。

**自分で操る**: メニューを試したあと、下の「**自分で操る — 対話する**」セルでモデルと対話できます(コマンド末尾の `--chat`)。ただしモデルは意味を理解せず、打った**出だしの続き**を書くだけです。'''))
cells.append(code('''# データセットを GitHub から自動ダウンロード / Auto-download the datasets
import urllib.request
BASE = "https://raw.githubusercontent.com/itoksk/summer-ai-materials/main/materials/data/"
for name in ["input_abc.txt", "input_chess.txt", "input_haiku.txt"]:
    urllib.request.urlretrieve(BASE + name, name)
    n = sum(1 for _ in open(name, encoding="utf-8"))
    print(f"{name}: {n} 行 / lines  ダウンロード完了 / done")'''))
cells.append(md('''### メニューA — AI が作曲する / ABC folk tunes

データはフォーク民謡(Nottingham Music Database)の楽譜を ABC 記譜法という文字の形式にしたものです。下のセルを実行すると、AI がメロディーを生成します。'''))
cells.append(code("!python3 microgpt_lab.py --input input_abc.txt --steps 400 --block-size 48 --temperatures 0.7 --num-samples 5"))
cells.append(md('''**音にして聞く / Hear it**
1. 気に入ったサンプル(`K:` や `|` が入った行)をコピー
2. [editor.drawthedots.com](https://editor.drawthedots.com) を開く
3. 次のテンプレートの最後の行に貼り付けると、再生ボタンで聞けます:

```
X:1
T:AI Tune
M:6/8
L:1/8
K:Gmaj
(ここに生成されたメロディーを貼る)
```

変な音になったら、それも「発見」。別のサンプルでもう一度。'''))
cells.append(md('''### メニューB — チェスを「見て」覚える / Chess openings

データは「1. e4 c5 2. Nf3 ...」のような対局の出だしです。AI にチェスのルールは**一切教えていません**。'''))
cells.append(code("!python3 microgpt_lab.py --input input_chess.txt --steps 500 --block-size 40 --temperatures 0.5 --num-samples 5"))
cells.append(md('''**検証 / Verify**: 生成された棋譜を [lichess.org/analysis](https://lichess.org/analysis) に貼って、**何手目まで合法か**数えてみよう。

ルールを教えていないのに、なぜ合法手っぽくなる? — 「次の文字を当てる」だけで、世界の決まりごとがしみ込んでいく。これが大きな LLM で起きていることの縮図です。'''))
cells.append(md('''### メニューC — 俳句 5-7-5 / Haiku

データはひらがなの俳句です(漢字だと文字の種類が多すぎて、この小さな AI には大変なので)。'''))
cells.append(code("!python3 microgpt_lab.py --input input_haiku.txt --steps 500 --block-size 24 --temperatures 0.8 --num-samples 8"))
cells.append(md('''**数えてみよう / Count**: 生成された句を、指を折って 5-7-5 で数えてみよう。
- 何句が 5-7-5 になった?
- ChatGPT も実は「数える」のが苦手です(strawberry に r は何個? 問題)。理由はトークンの仕組みにあります — コースサイトのトークナイザーのページとつながる話'''))
cells.append(md('''### 自分で操る — 対話する / Drive it yourself (chat)

サンプルを眺めるだけでなく、自分で**ハンドルを握れます**。下のセルを実行すると、訓練のあと「`you >`」の入力欄が出ます。**出だし**を打つと、モデルがその続きを書きます。

たいせつ: モデルは**意味を理解していません**。俳句モデルに「桜」と打っても、桜を**お題にした句を作る**のではなく、桜の後に続きそうな文字を並べるだけです。チェスは序盤の数手、俳句は上の句、音楽は数音を打ってみましょう。**空行**で終了。

(お題で本当に一句詠ませたいときは、指示を理解する大きいモデル=Gem の出番です — これが「スケール」の差。)'''))
cells.append(code("# 音楽と話す / chat with the music model\n!python3 microgpt_lab.py --input input_abc.txt --steps 400 --block-size 48 --chat"))
cells.append(code("# チェスと話す / chat with the chess model\n!python3 microgpt_lab.py --input input_chess.txt --steps 500 --block-size 40 --chat"))
cells.append(code("# 俳句と話す / chat with the haiku model\n!python3 microgpt_lab.py --input input_haiku.txt --steps 500 --block-size 24 --chat"))
cells.append(md('''### Show & Tell

チームで共有しよう:
- **ベストの1つ**(いちばん「らしい」生成)
- **最大の失敗作**(失敗はネタとして最高。なぜ失敗したか考えるのが本番)'''))
cells.append(md('''## Step 5 — 自分データGPT / My-Data GPT

最後は **自分のことば** で訓練します。

1. 先生から共有された **ヒアリングGem** を開いてチャットする(インタビューに答える)
2. 最低 5 問は答えてから「コーパスを作って / make my corpus」と頼む
3. 出てきたコードブロックの中身を `my_corpus.txt` という名前で保存
4. このColabにアップロード(左のフォルダにドラッグ)

**たいせつ**: 本名・住所・学校名・連絡先はコーパスに入れない。保存する前に自分で読み直そう。これが「学習データ」になります。'''))
cells.append(code("%%writefile gem_to_corpus.py\n" + CORPUS_SRC))
cells.append(code('''# Gemの出力 my_corpus.txt を、訓練用の input_me.txt に変換する
!python3 gem_to_corpus.py my_corpus.txt -o input_me.txt --augment'''))
cells.append(code("!python3 microgpt_lab.py --input input_me.txt --steps 600 --block-size 40 --temperatures 0.8 --num-samples 10"))
cells.append(md('''### 双子と話す / Chat with your twin

下のセルを実行すると、訓練のあと **入力欄** が出ます。**文の出だし**(例:「わたしは」「いつも」)を打つと、双子が君の口調で **続き** を書きます。

たいせつ: これは本物のチャットボットではありません。**次の1文字を予測しているだけ**なので、返ってくるのは質問への「答え」ではなく、君が打った文の『続き』です。これが今日の学びそのもの — 中身は理解していないのに、口調だけは君っぽい。**空行**を入れると終了します。'''))
cells.append(code("!python3 microgpt_lab.py --input input_me.txt --steps 600 --block-size 40 --temperatures 0.8 --num-samples 3 --chat"))
cells.append(md('''### 品評会 / Show & Tell

- 「**一番自分っぽい一言**」と「**一番ハズした一言**」を1つずつ発表
- 問い: なぜ 150 行のデータでは「自分」を完全に学べないのだろう? ChatGPT は何兆文字で訓練されている? — **データの量と質がAIのすべてを決める**'''))
cells.append(md('''## ふりかえり / Reflection

- 「次の1文字を当てる」だけのゲームから、何が生まれた?
- データを変えると AI はどう変わった? 温度を変えると?
- 自分GPTは「自分」だった? どこが違った?

**もっとやりたい人へ / Challenges**
- `--steps 2000` にすると? (時間とひきかえに賢くなる?)
- `--n-embd 32` で脳を大きくすると?
- 2つのデータファイルを混ぜて訓練したら?
- 自分のパソコンで本物のローカルLLM(Ollama)を動かす — コースサイトの Day 2 ページへ'''))
write_nb("microgpt_colab.ipynb", cells, "microgpt Lab (Summer AI)")

# ---------------------------------------------------------------- tetris
cells = []
cells.append(md('''# tetris-hand を Colab で動かす / Hand-controlled Tetris on Colab

カメラに映した **手の動き** でテトリスを操作します(Google の MediaPipe Hands という手認識AIを使ったゲームです)。

- リポジトリ: [github.com/itoksk/tetris-hand](https://github.com/itoksk/tetris-hand)
- **GitHub Codespaces でも動きます**(リポジトリの README の手順どおり)。このノートは **Colab だけで動かす**ためのものです
- カメラの映像は **自分のブラウザの中だけ** で処理されます(Colab のサーバーには送られません)

**しくみ**: ゲーム本体はブラウザで動く JavaScript。Colab は「ビルド(組み立て)」と「配信」だけを担当します。'''))
cells.append(md('''## Step 1 — ゲームのコードを取ってくる / Clone'''))
cells.append(code("!git clone https://github.com/itoksk/tetris-hand.git\n%cd /content/tetris-hand\n!ls"))
cells.append(md('''## Step 2 — Node.js を入れる / Install Node.js

このゲームのビルドに Node.js という道具が必要です(数分かかります)。'''))
cells.append(code('''!curl -fsSL https://deb.nodesource.com/setup_22.x 2>/dev/null | bash - >/dev/null 2>&1
!apt-get install -y nodejs >/dev/null 2>&1
!node -v && npm -v'''))
cells.append(md('''## Step 3 — 部品を集めて組み立てる / Install & build'''))
cells.append(code("%cd /content/tetris-hand\n!npm install\n!npm run build"))
cells.append(md('''## Step 4 — ゲームを配信して遊ぶ / Serve & play

下のセルを実行すると URL が出ます。**クリックして開き、カメラを「許可」**してください。

**遊び方 / How to play**
- 手を左右にかたむける = ブロックを左右に動かす
- 人差し指を立てる = 回転
- 手を下にさげる = 高速落下'''))
cells.append(code('''import subprocess
server = subprocess.Popen(["python3", "-m", "http.server", "8000", "--directory", "dist"])
from google.colab.output import eval_js
url = eval_js("google.colab.kernel.proxyPort(8000)")
print("ゲームのURL(クリックして開く):", url)'''))
cells.append(md('''## Step 5 — 改造タイム / Hack it

ジェスチャー(手の形の判定)は自分で変えられます。

1. 左のフォルダで `tetris-hand/src/hand/tracker.js` を開く(ダブルクリックで編集できる)
2. リポジトリ内の `GESTURE_CUSTOMIZATION_GUIDE.md` を読みながら、判定のしきい値や新しいジェスチャーを変えてみる
3. 下のセルで **再ビルド** して、ゲームのタブをリロード

課題リスト(初級→上級)は `PROGRAMMING_EXERCISES.md` にあります。'''))
cells.append(code('!npm run build && echo "再ビルド完了 — ゲームのタブをリロードしてね / rebuilt, reload the game tab"'))
cells.append(md('''## うまくいかないとき / Troubleshooting

| 症状 | 対処 |
|---|---|
| URL を開いても真っ白 | Step 3〜4 のセルをもう一度実行 |
| カメラ許可のポップアップが出ない | ブラウザのアドレスバー横のカメラアイコンから許可 |
| 手を認識しない | 明るい場所で、カメラから 50cm〜1m。手のひらをカメラに向ける |
| `npm install` が失敗 | メニュー「ランタイム → ランタイムを再起動」して最初から |
| しばらく放置したら URL が死んだ | Colab のセッション切れ。Step 4 を再実行 |

**ビルドがどうしても失敗するとき**(開発サーバーで直接動かす別ルート):'''))
cells.append(code('''# 代替ルート: ビルドせず開発サーバーをプロキシで公開する
import subprocess, time
dev = subprocess.Popen(["npx", "vite", "--port", "8000", "--host", "0.0.0.0"], cwd="/content/tetris-hand")
time.sleep(8)
from google.colab.output import eval_js
print("ゲームのURL:", eval_js("google.colab.kernel.proxyPort(8000)"))'''))
cells.append(md('''## ふりかえり / Reflection

- 「手の認識」はどこで動いていた? (ヒント: Colab? 自分のブラウザ?)
- MediaPipe は何を出力している? (`tracker.js` の中に 21 個の点 = ランドマークが出てくる)
- このしくみで、テトリス以外に何が作れる? — Day 4 のハッカソンのネタ帳へ'''))
write_nb("tetris_hand_colab.ipynb", cells, "tetris-hand on Colab (Summer AI)")

# ---------------------------------------------------------------- titanic
cells = []
cells.append(md('''# Titanic で機械学習に入門する / ML with the Titanic dataset

**Day 3 の予備モジュール**です。Kaggle(世界最大のデータ分析コンペサイト)で一番有名なデータ「タイタニック号の乗客名簿」を使って、**過去のデータから未来を予測する** 機械学習を体験します。

- 配布ワークシート「Titanic データ分析ワークシート」と一緒に使います
- 1912年の実際の事故のデータです。数字の1つ1つが実在の人だったことを忘れずに'''))
cells.append(md('''## Step 1 — データを読み込む / Load the data'''))
cells.append(code('''import pandas as pd

url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
try:
    df = pd.read_csv(url)
except Exception:
    print("ダウンロードできない場合: 先生から titanic.csv をもらって左のフォルダにアップロードしてください")
    df = pd.read_csv("titanic.csv")
print(df.shape)
df.head()'''))
cells.append(md('''## Step 2 — まず自分の目でデータを見る / Look at the data yourself first

いきなり機械に予測させない。まず**自分の目で**データを見て、生死を分けていそうな「とくちょう」を探そう。

- `Survived`: 1 = 生存, 0 = 死亡 / `Pclass`: 等級(1=富裕 … 3=庶民) / `Sex` / `Age` / `Fare`(運賃)

Before letting a machine predict anything, look at the data with your own eyes. Which columns seem to separate who survived?'''))
cells.append(code('''print("全体の生存率 / overall:", round(df["Survived"].mean(), 3))
print("\\n性別ごと / by Sex")
print(df.groupby("Sex")["Survived"].mean().round(3))
print("\\n等級ごと / by Pclass")
print(df.groupby("Pclass")["Survived"].mean().round(3))

# 年齢を子ども/10代/大人に分けて見る / bin Age into child / teen / adult
df["AgeGroup"] = pd.cut(df["Age"], [0, 12, 18, 200], labels=["child(0-12)", "teen(13-18)", "adult(19+)"])
print("\\n年齢グループごと / by Age group")
print(df.groupby("AgeGroup", observed=True)["Survived"].mean().round(3))'''))
cells.append(code('''import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(13, 4))
df.groupby("Sex")["Survived"].mean().plot.bar(ax=axes[0], title="by Sex")
df.groupby("Pclass")["Survived"].mean().plot.bar(ax=axes[1], title="by Pclass")
df.groupby("AgeGroup", observed=True)["Survived"].mean().plot.bar(ax=axes[2], title="by Age group")
for ax in axes:
    ax.set_ylim(0, 1)
    ax.set_ylabel("survival rate")
plt.tight_layout()
plt.show()'''))
cells.append(md('''**観察 / Observe**: どの差が一番大きい? 「女性と子どもを先に救命ボートへ」という当時の行動が、110年後のデータから読み取れる。 / Which gap is biggest? You can read 1912 behaviour straight out of the numbers.'''))
cells.append(md('''## Step 3 — 予測する前に、予想を書こう / Predict BEFORE you train

機械に答えを出させる前に、**自分の予想**を決める。これが一番の学び。

1. 生死を一番わける「とくちょう」は? **Sex / Pclass / Age / Fare** を重要そうな順に並べる。
2. なぜそう思う? 1行で書く。

Write your ranking down NOW. In a moment the tree will reveal which feature it actually relied on most — then you can check whether your intuition matched the data. **No peeking at Step 4 first!**'''))
cells.append(md('''## Step 4 — 決定木で予測する / Train a decision tree

**決定木(けっていぎ)** は「質問を繰り返して答えにたどりつく」モデル(20の質問ゲームと同じ)。

(先生向けメモ: 文部科学省「情報Ⅱ」教員研修用教材 第3章 学習15 の R での演習を Python に移したもの)'''))
cells.append(code('''from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree

data = df[["Pclass", "Sex", "Age", "Fare", "Survived"]].copy()
data["Sex"] = (data["Sex"] == "female").astype(int)  # female=1, male=0
data["Age"] = data["Age"].fillna(data["Age"].median())

X = data[["Pclass", "Sex", "Age", "Fare"]]
y = data["Survived"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

tree = DecisionTreeClassifier(max_depth=3, random_state=42)
tree.fit(X_train, y_train)
print("訓練データの正解率 / train accuracy:", round(tree.score(X_train, y_train), 3))
print("テストデータの正解率 / test accuracy:", round(tree.score(X_test, y_test), 3))'''))
cells.append(code('''plt.figure(figsize=(14, 7))
plot_tree(tree, feature_names=["Pclass", "Sex(female=1)", "Age", "Fare"],
          class_names=["died", "survived"], filled=True, fontsize=9)
plt.show()

print("特徴量の重要度 / feature importance — did it match YOUR ranking from Step 3?")
for name, imp in sorted(zip(X.columns, tree.feature_importances_), key=lambda t: -t[1]):
    print(f"  {name:6} {round(imp, 3)}")'''))
cells.append(md('''**木の読み方 / Read the tree**: 一番上の質問は何? → モデルが「生死を分けた最大の要因」と判断したもの。**あなたの予想(Step 3)と合っていた? / Did the top split match the ranking you wrote?**'''))
cells.append(md('''## Step 5 — 実験: 木を深くしすぎると? / Overfitting experiment

`max_depth` を変えて、訓練の正解率とテストの正解率がどうなるか見てみよう。'''))
cells.append(code('''for depth in [1, 2, 3, 5, 10, None]:
    t = DecisionTreeClassifier(max_depth=depth, random_state=42).fit(X_train, y_train)
    print(f"max_depth={str(depth):>4} | train {t.score(X_train, y_train):.3f} | test {t.score(X_test, y_test):.3f}")'''))
cells.append(md('''**問い / Questions**
- 木を深くすると、訓練の正解率はどうなる? テストは?
- 訓練だけ上がってテストが下がる現象を **過学習(丸暗記)** と呼びます。microgpt のラボで見た「図鑑の名前をそのまま言う」のと同じ現象です

## ふりかえり / Reflection

- データから「人の行動」が見えた瞬間はどこ?
- この予測モデルを現実で使うとしたら、どんな危険がある? (バイアスのページとつながる話)
- **Kaggle** に登録すると(13歳以上)、世界中の人と同じ課題に挑戦できます: [kaggle.com/c/titanic](https://www.kaggle.com/c/titanic)'''))
write_nb("titanic_colab.ipynb", cells, "Titanic ML (Summer AI)")

# ---------------------------------------------------------------- heatstroke (regression)
HEAT_CSV = "https://raw.githubusercontent.com/itoksk/summer-ai-materials/main/materials/data/heatstroke.csv"
cells = []
cells.append(md('''# 暑さから「今日 何人 倒れるか」を予測する / Predict heat-illness from the heat

**Day 3 — 回帰(regression)の実習**です。Titanic は「助かる / 助からない」の **Yes/No(=分類)** でした。今度は **数そのものを当てる(=回帰)**。

**予測するもの**: その日・その都道府県で **熱中症で救急搬送された人数**。

**データの出所 / provenance**(作り物は一つもない):
- 搬送人数 = **総務省消防庁「熱中症による救急搬送状況」**(日別・都道府県別の政府公式記録)
- 気温・湿度 = **Open-Meteo 歴史アーカイブ**(ERA5 再解析 / 各国気象機関ベース)
- 期間 = 2018〜2024年の夏(5〜9月)、7都道府県(北海道・東京・愛知・大阪・**兵庫=神戸**・福岡・沖縄)

We predict a NUMBER (how many people are taken to hospital for heat illness on a given day), using real government records. This is regression — the counterpart to the Titanic yes/no.'''))

cells.append(md('''## Step 1 — データを読み込む / Load the data'''))
cells.append(code('''import pandas as pd

url = "%s"
df = pd.read_csv(url)
print(df.shape)          # (行数, 列数)
df.head()''' % HEAT_CSV))

cells.append(md('''## Step 2 — まず自分の目で見る / Look first

機械に予測させる前に、**自分の目で**「暑さ」と「搬送人数」の関係を見る。

- `tmax_c`: その日の最高気温 / `transported`: 搬送人数(これを予測する) / `pref_en`: 都道府県 / `severe`: 重症+死亡'''))
cells.append(code('''# 最高気温を3度ごとに区切って、平均の搬送人数を見る / mean transports per 3°C bin
df["tmax_bin"] = (df["tmax_c"] // 3 * 3).astype(int)
print(df.groupby("tmax_bin")["transported"].mean().round(1))'''))
cells.append(code('''import matplotlib.pyplot as plt

plt.figure(figsize=(8, 5))
plt.scatter(df["tmax_c"], df["transported"], s=6, alpha=0.15)
plt.xlabel("daily max temperature (°C)")
plt.ylabel("people transported (per prefecture/day)")
plt.title("Heat vs heat-illness transports")
plt.show()'''))
cells.append(md('''**観察 / Observe**: 直線? それとも**曲がっている**? 30°Cを超えたあたりから急に跳ね上がる(=非線形)。これが今日のカギ。 / Straight line, or does it bend upward past ~30°C?'''))

cells.append(md('''## Step 3 — 予測する前に予想を書く / Predict BEFORE you train

機械に答えさせる前に、**自分の予想**を決める。

1. 最高気温が **35°C** の日、ある県で何人くらい運ばれると思う? 数を1つ書く。
2. 気温の他に、搬送人数を左右しそうな要素は? (都道府県/月/湿度…) 1つ挙げる。

Write a number for "how many at 35°C" now. The model will reveal the real answer in a moment — no peeking.'''))

cells.append(md('''## Step 4 — 「見たことのない夏」を当てる / Train on the past, predict an unseen summer

ズルを防ぐため、**年で分ける**。2018〜2023年で学習し、**2024年(モデルが一度も見ていない夏)** を当てさせる。これが「テストデータで予測する」ということ。'''))
cells.append(code('''from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

train = df[df["year"] < 2024]
test  = df[df["year"] == 2024]
print("train rows:", len(train), " / test rows (2024):", len(test))

# まずは一番単純に: 最高気温 だけ で直線を引く / simplest: a straight line from tmax only
lin = LinearRegression().fit(train[["tmax_c"]], train["transported"])
pred = lin.predict(test[["tmax_c"]])
print("直線モデルの平均誤差 / linear MAE:", round(mean_absolute_error(test["transported"], pred), 2), "人")
at35 = pd.DataFrame({"tmax_c": [35]})
print("35°Cの予測 / prediction at 35°C:", round(float(lin.predict(at35)[0]), 1), "人  <- Step3の予想と比べる")'''))
cells.append(md('''**問い**: 直線は、暑い日(35°C超)の急増をうまく当てられた? たぶん**過小評価**したはず。関係が曲がっているのに、直線で引いたから。 / A straight line under-predicts the hottest days, because the real curve bends.'''))

cells.append(md('''## Step 5 — もっと良いモデル + 他の手がかり / A better model with more clues

曲がりに強い **ランダムフォレスト**(たくさんの決定木の多数決)に、気温だけでなく **都道府県・月・湿度** も渡す。'''))
cells.append(code('''from sklearn.ensemble import RandomForestRegressor

feat = ["tmax_c", "tmean_c", "humidity_pct", "month"]
Xtr = pd.get_dummies(train[feat + ["pref_en"]], columns=["pref_en"])
Xte = pd.get_dummies(test[feat + ["pref_en"]], columns=["pref_en"]).reindex(columns=Xtr.columns, fill_value=0)

rf = RandomForestRegressor(n_estimators=200, random_state=42).fit(Xtr, train["transported"])
pred_rf = rf.predict(Xte)
print("森モデルの平均誤差 / RandomForest MAE:", round(mean_absolute_error(test["transported"], pred_rf), 2), "人")
print("(直線モデルより小さくなった? = 当たるようになった)")'''))

cells.append(md('''## Step 6 — 答え合わせ: 実在の1日を予測する / Answer-check on a real day

2024年の **一番暑かった東京の日** を、モデルに予測させて、**実際の搬送人数**と比べる。'''))
cells.append(code('''test = test.copy()
test["pred"] = pred_rf.round(0)

# 2024年・東京で最高気温が一番高かった日 / hottest Tokyo day of 2024
tokyo = test[test["pref_en"] == "Tokyo"].sort_values("tmax_c", ascending=False)
print(tokyo[["date", "tmax_c", "transported", "pred"]].head(5).to_string(index=False))
print("\\n予測(pred) と 実際(transported) は近い? どれくらいズレた? / How close was the model?")'''))
cells.append(code('''# どの手がかりを重視した? / which clues mattered most?
imp = sorted(zip(Xtr.columns, rf.feature_importances_), key=lambda t: -t[1])
print("特徴量の重要度 top8 / feature importance:")
for name, v in imp[:8]:
    print(f"  {name:18} {round(v, 3)}")
print("\\nStep3で挙げた要素は入っていた? / did your guessed factor show up?")'''))

cells.append(md('''## Step 7 — しきい値とアラート / The threshold and the alert

搬送人数は 30°C を超えると急増する。だから日本では **暑さ指数(WBGT)** が一定を超えると **熱中症警戒アラート**(環境省・気象庁)が出る。モデルが見つけた「曲がり角」は、国が人を守るために使っている線とほぼ同じ場所にある。

The model's "elbow" near 30°C is essentially the same line Japan uses to issue heat-illness alerts.'''))

cells.append(md('''## ふりかえり / Reflection & limits

- このモデルは **都道府県庁所在地の気温** を県全体の代表として使っている。県は広い。Titanic と同じ警告: **モデルは「測ったもの」しか知らない**。
- 人口の多い県ほど搬送人数は多い。気温だけでなく **人口** も効いている — 公平に比べるなら「人口10万人あたり」にすべき?
- 夏は年々暑くなっている(気候変動)。学習した過去より暑い未来では、モデルの予測は当たる? 外れる?
- **チャレンジ**: (1) 「人口あたり」に直して県を公平に比べる (2) 自分の住む県を追加する(消防庁データは47都道府県すべてにある) (3) 「明日 アラートを出すべきか(Yes/No)」の**分類**に作り変える

**データ出典 / Sources**
- 総務省消防庁「熱中症による救急搬送状況」 https://www.fdma.go.jp/disaster/heatstroke/
- Open-Meteo Historical Weather API (ERA5) https://open-meteo.com/
- 環境省 熱中症予防情報サイト(暑さ指数WBGT) https://www.wbgt.env.go.jp/'''))
write_nb("heatstroke_colab.ipynb", cells, "Heatstroke Prediction (Summer AI)")

# ---------------------------------------------------------------- image gen
# Colab links for the two language versions (used to cross-link the notebooks)
JA_COLAB = "https://colab.research.google.com/github/itoksk/summer-ai-materials/blob/main/materials/notebooks/image_gen_advanced.ipynb"
EN_COLAB = "https://colab.research.google.com/github/itoksk/summer-ai-materials/blob/main/materials/notebooks/image_gen_advanced_en.ipynb"

# ===== Japanese version =====
cells = []
cells.append(md(f'''# 画像生成のしくみをのぞく / Open-source image generation (Day 1 実習)

> **English version / 英語版はこちら**: [Open in Colab]({EN_COLAB})

Day 1 の画像コンテストで使った Gemini は「完成品のサービス」。ここでは **オープンなモデル(Stable Diffusion)を自分の手で動かして**、中のつまみを直接さわります。

このノートは公開リポジトリ **github.com/itoksk/summer-ai-materials** の `materials/notebooks/` にあり、「Open in Colab」で GitHub から複製されました。

**準備 / Setup**
1. メニュー「ファイル → ドライブにコピーを保存」(編集と画像が自分のドライブに残ります)
2. メニュー「ランタイム → ランタイムのタイプを変更」で **T4 GPU** を選ぶ(無料枠でOK)
3. セルを上から順に実行。**つまみは各セル上の「フォーム」で変えられます**(コードは「Show code」で見られます)

**約束 / Rules**
- 実在の人物・友だち・有名人の名前や顔は生成しない(肖像権)
- 実在のキャラクター(アニメ・ゲーム)をそのまま出さない — 著作権ワークで考えたとおり
- AI生成を人作と偽る・なりすまし・ディープフェイクは作らない(犯罪になりえます)
- 作った画像には「created with Stable Diffusion」と添え、公開・商用の前にライセンスを確認する
- モデルのライセンスは CreativeML OpenRAIL-M / OpenRAIL++ 系(禁止用途が定められています)

(この教材は学校の授業「AI画像処理と著作権」のノートブックをもとにしています)'''))
cells.append(md('''## Step 1 — 道具を入れる / Install'''))
cells.append(code('''# diffusers などを最新化(高画質モデル Animagine の長文プロンプト対応に新しめの diffusers が必要)
!pip -q install --upgrade diffusers transformers accelerate safetensors'''))
cells.append(md('''## Step 2 — モデルを選んで読み込む / Pick a model and load it

何十億枚の画像で訓練済みのモデル(数GB)をダウンロードします。数分かかります。

**モデルは下のフォームの `MODEL` で選びます。** 2つの段があります:

| 段 | `MODEL` の値 | 特徴 |
|---|---|---|
| 基本(SD1.5) | `anime` / `base` / `photo` | **速い**・**安全フィルタON**・つまみが教科書どおり。まずはここから |
| 高画質(SDXL) | `anime-xl` / `photo-xl` | **きれいだが重い**・内蔵フィルタなし・書き方が少し違う |

**書き方(プロンプト)の違いに注意**
- `anime-xl`(Animagine XL 4.0) … 自然な文より **Danbooru風のタグ**で書くモデル。末尾の品質タグは自動で付きます。
- それ以外 … いつもの自然な英文でOK。
- → モデルを選ぶと、**そのモデルのおすすめプロンプト/設定が下に表示**されます(Step 3 のフォームにコピペ)。

**安全フィルタの話(ふりかえりの実例)**
- 基本段(SD1.5)は **NSFWフィルタを入れた状態**で読み込みます。引っかかると画像が**真っ黒**で返ります = バグではなくフィルタが働いた合図。
- 高画質段(SDXL)には、この内蔵フィルタが**付きません**。
- 「同じオープンモデルでも、サービス(Gemini)はなぜフィルタを足すのか?」— 最後のふりかえりで確認します。

**重さ / VRAM** — SDXLは1枚が重い。無料T4で `Out of memory` が出たら → 基本段に戻すか、下の `steps` を下げる。'''))
cells.append(code('''#@title ① モデルを選んで読み込む / Pick a model & load  { display-mode: "form" }
#@markdown 基本(速い・フィルタON): **anime / base / photo**　｜　高画質(SDXL・重い・フィルタなし): **anime-xl / photo-xl**
MODEL = "anime"  #@param ["anime", "base", "photo", "anime-xl", "photo-xl"]
#@markdown 変えたら左の ▶ を押して読み込み直す。

import torch
from diffusers import (
    StableDiffusionPipeline, StableDiffusionXLPipeline,
    DPMSolverMultistepScheduler, AutoencoderKL,
)

# GPUが無いと to("cuda") で止まるので最初に確認(なければ ランタイム→ランタイムのタイプを変更→T4 GPU)
if not torch.cuda.is_available():
    raise RuntimeError(
        "GPUが見つかりません。Colab上部メニュー[ランタイム]→[ランタイムのタイプを変更]"
        "→ハードウェアアクセラレータで【T4 GPU】を選び、保存してから、もう一度実行してください。")

# --- モデル表(リポジトリ名と、各モデルのおすすめ設定) ---
ANIME_XL_NEG = ("lowres, bad anatomy, bad hands, text, error, missing finger, "
                "extra digits, fewer digits, cropped, worst quality, low quality, "
                "low score, bad score, average score, signature, watermark, username, blurry")
PHOTO_XL_NEG = ("worst quality, low quality, illustration, 3d, 2d, painting, cartoon, "
                "sketch, deformed iris, deformed pupils, bad anatomy, extra fingers, "
                "fused fingers, blurry, text, watermark")
SD15_PHOTO_NEG = ("cartoon, anime, sketch, drawing, 3d, render, worst quality, low quality, "
                  "bad anatomy, extra fingers, mutated hands, blurry, text, watermark")

MODELS = {
    # ---- 基本段: SD1.5(速い・フィルタON・自然文OK) ----
    "anime": {"arch": "sd15", "repo": "stablediffusionapi/anything-v5",
              "prompt": "a cozy ramen shop on a rainy night, neon signs, watercolor style",
              "neg": "low quality, blurry, text, watermark", "suffix": "",
              "steps": 25, "cfg": 7.0, "w": 512, "h": 512},
    "base":  {"arch": "sd15", "repo": "stable-diffusion-v1-5/stable-diffusion-v1-5",
              "prompt": "a cozy ramen shop on a rainy night, neon signs, watercolor style",
              "neg": "low quality, blurry, text, watermark", "suffix": "",
              "steps": 25, "cfg": 7.0, "w": 512, "h": 512},
    "photo": {"arch": "sd15", "repo": "SG161222/Realistic_Vision_V5.1_noVAE", "vae": "mse",
              "prompt": "a cozy ramen shop on a rainy night, neon signs, photo, 35mm",
              "neg": SD15_PHOTO_NEG, "suffix": "",
              "steps": 25, "cfg": 7.0, "w": 512, "h": 512},
    # ---- 高画質段: SDXL(きれい・重い・内蔵フィルタなし) ----
    "anime-xl": {"arch": "sdxl", "repo": "cagliostrolab/animagine-xl-4.0", "lpw": True,
                 "prompt": "no humans, ramen shop interior, neon signs, rainy night, "
                           "window reflection, steam, warm lighting, detailed background",
                 "neg": ANIME_XL_NEG,
                 "suffix": ", masterpiece, high score, great score, absurdres",
                 "steps": 28, "cfg": 5.5, "w": 1024, "h": 1024},
    "photo-xl": {"arch": "sdxl", "repo": "SG161222/RealVisXL_V5.0",
                 "prompt": "a cozy ramen shop on a rainy night, neon signs reflecting on wet "
                           "pavement, cinematic lighting, photorealistic, 35mm",
                 "neg": PHOTO_XL_NEG, "suffix": "",
                 "steps": 30, "cfg": 5.0, "w": 1024, "h": 1024},
}

cfg = MODELS[MODEL]
print("loading:", MODEL, "->", cfg["repo"])

if cfg["arch"] == "sd15":
    # SD1.5: NSFW安全フィルタを必ず付けて読み込む(学校で使うため)
    from transformers import CLIPImageProcessor
    from diffusers.pipelines.stable_diffusion.safety_checker import StableDiffusionSafetyChecker
    checker = StableDiffusionSafetyChecker.from_pretrained(
        "CompVis/stable-diffusion-safety-checker", torch_dtype=torch.float16)
    extractor = CLIPImageProcessor.from_pretrained("CompVis/stable-diffusion-safety-checker")
    kw = dict(torch_dtype=torch.float16, safety_checker=checker, feature_extractor=extractor)
    if cfg.get("vae") == "mse":   # *_noVAE モデルは VAE を足さないと色がくすむ
        kw["vae"] = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-mse",
                                                  torch_dtype=torch.float16)
    pipe = StableDiffusionPipeline.from_pretrained(cfg["repo"], **kw)
else:
    # SDXL: 高画質。内蔵フィルタは付かない(Step 2 の説明を参照)
    kw = dict(torch_dtype=torch.float16, use_safetensors=True, add_watermarker=False)
    if cfg.get("lpw"):            # 長文・タグ・強調プロンプトに強いパイプライン
        kw["custom_pipeline"] = "lpw_stable_diffusion_xl"
    pipe = StableDiffusionXLPipeline.from_pretrained(cfg["repo"], **kw)

# スケジューラ(ノイズの消し方)。Karras 版にすると質感が安定します
pipe.scheduler = DPMSolverMultistepScheduler.from_config(
    pipe.scheduler.config, use_karras_sigmas=True, algorithm_type="dpmsolver++")
pipe = pipe.to("cuda")

HAS_FILTER = (cfg["arch"] == "sd15")
print("ready:", cfg["repo"], "| 安全フィルタ:", "ON" if HAS_FILTER else "なし(SDXL)")
print()
print("--- このモデルのおすすめ(Step 3 のフォームにコピペ) ---")
print("prompt   :", cfg["prompt"])
print("negative :", cfg["neg"])
print(f"steps={cfg['steps']}  guidance={cfg['cfg']}  size={cfg['w']}x{cfg['h']}")
if cfg["suffix"]:
    print("品質タグ", repr(cfg["suffix"]), "は自動で末尾に付きます")'''))
cells.append(md('''## Step 3 — 生成する / Generate

つまみの意味:
- `prompt`: 何を描くか(**英語**で。Gemini に翻訳してもらってOK)
- `negative_prompt`: 入れたくないもの
- `seed`: サイコロの目。**同じ seed + 同じ言葉 = 同じ絵**
- `guidance`: 言葉にどれだけ従うか(基本7前後 / SDXLは5前後が定番)
- `steps`: ノイズから絵にする回数(25〜28前後)

下のフォームで変えて ▶ を押すだけ。**選んだモデルのおすすめ**は Step 2 の出力に出ています(コピペ可)。'''))
cells.append(code('''#@title ② 生成する / Generate  { display-mode: "form" }
#@markdown 英語で(Geminiに訳してOK)。同じ seed + 同じ言葉 = 同じ絵。SDXL(anime-xl/photo-xl)は guidance 5 前後がきれい。
prompt = "a cozy ramen shop on a rainy night, neon signs, watercolor style"  #@param {type:"string"}
negative_prompt = "low quality, blurry, text, watermark"  #@param {type:"string"}
seed = 42  #@param {type:"integer"}
steps = 25  #@param {type:"slider", min:10, max:40, step:1}
guidance = 7.0  #@param {type:"slider", min:1, max:15, step:0.5}

full_prompt = prompt + cfg["suffix"]          # 品質タグ(モデルごと)を自動付与
generator = torch.Generator("cuda").manual_seed(seed)
image = pipe(full_prompt, negative_prompt=negative_prompt,
             num_inference_steps=steps, guidance_scale=guidance,
             width=cfg["w"], height=cfg["h"], generator=generator).images[0]
# 画像が真っ黒なら → 安全フィルタが働いた合図(SD1.5のみ)。言葉を変えて再挑戦
image'''))
cells.append(md('''## Step 4 — 実験 / Experiments

1. **seed を固定して言葉だけ変える** — `watercolor style` を `pixel art` にすると?
2. **言葉を固定して seed だけ変える** — 同じ注文でも違う絵になる
3. `guidance` を 2 と 15 にしてみる — 従いすぎると絵はどうなる?

(Day 1 コンテストの「言葉で絵を支配する」感覚を、今度はつまみのレベルで)

※ この実験が成り立つのは、つまみが素直に効く**基本段**と**標準SDXL**だから。4〜6ステップで一気に描く「高速版(Lightning/Turbo)」だと guidance が効かず、この実験は壊れます。'''))
cells.append(code('''#@title ③ 実験: つまみを変えてもう1枚 / Experiment  { display-mode: "form" }
#@markdown seed を固定して言葉だけ変える / 言葉を固定して seed を変える / guidance を 2 と 15 で比べる
prompt = "a cozy ramen shop on a rainy night, neon signs, pixel art"  #@param {type:"string"}
seed = 42  #@param {type:"integer"}
steps = 25  #@param {type:"slider", min:10, max:40, step:1}
guidance = 7.0  #@param {type:"slider", min:1, max:15, step:0.5}

full_prompt = prompt + cfg["suffix"]
generator = torch.Generator("cuda").manual_seed(seed)
pipe(full_prompt, negative_prompt=cfg["neg"],
     num_inference_steps=steps, guidance_scale=guidance,
     width=cfg["w"], height=cfg["h"], generator=generator).images[0]'''))
cells.append(md('''## ふりかえり / Reflection

- このモデルは「誰の絵」で訓練された? 描いた人は同意した? — 著作権ワークの問いを、今日は**自分が生成する側**として考え直す
- Gemini のようなサービスと、自分で動かすオープンモデルの違いは? (安全フィルター、責任、自由度)
  - 今日は **基本段=フィルタON / 高画質段(SDXL)=フィルタなし** を実際に切り替えた。サービスがフィルタを足すのはなぜ?
- 生成した絵は「あなたの作品」? AI の作品? 訓練データの作者の作品?'''))
write_nb("image_gen_advanced.ipynb", cells, "Image Generation Advanced (Summer AI)")

# ===== English version =====
cells = []
cells.append(md(f'''# Open-source image generation (Day 1 lab)

> **日本語版 / Japanese version**: [Open in Colab]({JA_COLAB})

The Gemini you used in the Day 1 image contest is a "finished service." Here you'll **run an open model (Stable Diffusion) with your own hands** and turn the dials directly.

This notebook lives in the public repo **github.com/itoksk/summer-ai-materials** under `materials/notebooks/`, opened from GitHub via "Open in Colab."

**Setup**
1. Menu "File -> Save a copy in Drive" (keeps your edits and images in your own Drive)
2. Menu "Runtime -> Change runtime type" -> pick **T4 GPU** (the free tier is fine)
3. Run the cells top to bottom. **Change the dials in the form on top of each cell** (open the code with "Show code").

**Rules**
- No real people's faces or names — not yourself, friends, or celebrities (portrait rights)
- No existing characters (anime / games) as-is — as you discussed in the copyright work
- No passing AI work off as human-made, no impersonation, no deepfakes (these can be crimes)
- Credit your images as "created with Stable Diffusion"; check the licence before sharing or commercial use
- Model licences are the CreativeML OpenRAIL-M / OpenRAIL++ family (they define prohibited uses)

(Based on the school class "AI image processing & copyright")'''))
cells.append(md('''## Step 1 — Install'''))
cells.append(code('''# Upgrade diffusers etc. (the high-quality Animagine model needs a recent diffusers for long prompts)
!pip -q install --upgrade diffusers transformers accelerate safetensors'''))
cells.append(md('''## Step 2 — Pick a model and load it

This downloads a model (a few GB) trained on billions of images. It takes a few minutes.

**Pick the model with `MODEL` in the form below.** There are two tiers:

| Tier | `MODEL` value | Notes |
|---|---|---|
| Basic (SD1.5) | `anime` / `base` / `photo` | **Fast** · **safety filter ON** · textbook dials. Start here. |
| High quality (SDXL) | `anime-xl` / `photo-xl` | **Prettier but heavy** · no built-in filter · prompts written a bit differently |

**Mind the prompt style**
- `anime-xl` (Animagine XL 4.0) … write **Danbooru-style tags** rather than natural sentences. The quality tags at the end are added for you.
- Everything else … plain natural English is fine.
- → When you pick a model, **its recommended prompt/settings are printed below** (copy them into the Step 3 form).

**About the safety filter (a real example for the reflection)**
- The basic tier (SD1.5) loads **with the NSFW filter on**. If you trip it, the image comes back **pure black** = not a bug, but the filter doing its job.
- The high-quality tier (SDXL) has **no** built-in filter.
- "If it's the same open model, why does a service (Gemini) add a filter?" — you'll feel this difference with your own hands in the final reflection.

**Weight / VRAM** — SDXL is heavy per image. If a free T4 gives `Out of memory`, go back to the basic tier or lower `steps` below.'''))
cells.append(code('''#@title ① Pick a model & load  { display-mode: "form" }
#@markdown Basic (fast, filter ON): **anime / base / photo**　|　High quality (SDXL, heavy, no filter): **anime-xl / photo-xl**
MODEL = "anime"  #@param ["anime", "base", "photo", "anime-xl", "photo-xl"]
#@markdown Change it, then press the ▶ on the left to reload.

import torch
from diffusers import (
    StableDiffusionPipeline, StableDiffusionXLPipeline,
    DPMSolverMultistepScheduler, AutoencoderKL,
)

# Check for a GPU first (otherwise to("cuda") fails): Runtime -> Change runtime type -> T4 GPU
if not torch.cuda.is_available():
    raise RuntimeError(
        "No GPU found. In the Colab menu open [Runtime] -> [Change runtime type], "
        "pick the T4 GPU accelerator, save, then run this cell again.")

# --- model table (repo name + recommended settings for each model) ---
ANIME_XL_NEG = ("lowres, bad anatomy, bad hands, text, error, missing finger, "
                "extra digits, fewer digits, cropped, worst quality, low quality, "
                "low score, bad score, average score, signature, watermark, username, blurry")
PHOTO_XL_NEG = ("worst quality, low quality, illustration, 3d, 2d, painting, cartoon, "
                "sketch, deformed iris, deformed pupils, bad anatomy, extra fingers, "
                "fused fingers, blurry, text, watermark")
SD15_PHOTO_NEG = ("cartoon, anime, sketch, drawing, 3d, render, worst quality, low quality, "
                  "bad anatomy, extra fingers, mutated hands, blurry, text, watermark")

MODELS = {
    # ---- Basic tier: SD1.5 (fast, filter ON, natural sentences OK) ----
    "anime": {"arch": "sd15", "repo": "stablediffusionapi/anything-v5",
              "prompt": "a cozy ramen shop on a rainy night, neon signs, watercolor style",
              "neg": "low quality, blurry, text, watermark", "suffix": "",
              "steps": 25, "cfg": 7.0, "w": 512, "h": 512},
    "base":  {"arch": "sd15", "repo": "stable-diffusion-v1-5/stable-diffusion-v1-5",
              "prompt": "a cozy ramen shop on a rainy night, neon signs, watercolor style",
              "neg": "low quality, blurry, text, watermark", "suffix": "",
              "steps": 25, "cfg": 7.0, "w": 512, "h": 512},
    "photo": {"arch": "sd15", "repo": "SG161222/Realistic_Vision_V5.1_noVAE", "vae": "mse",
              "prompt": "a cozy ramen shop on a rainy night, neon signs, photo, 35mm",
              "neg": SD15_PHOTO_NEG, "suffix": "",
              "steps": 25, "cfg": 7.0, "w": 512, "h": 512},
    # ---- High-quality tier: SDXL (pretty, heavy, no built-in filter) ----
    "anime-xl": {"arch": "sdxl", "repo": "cagliostrolab/animagine-xl-4.0", "lpw": True,
                 "prompt": "no humans, ramen shop interior, neon signs, rainy night, "
                           "window reflection, steam, warm lighting, detailed background",
                 "neg": ANIME_XL_NEG,
                 "suffix": ", masterpiece, high score, great score, absurdres",
                 "steps": 28, "cfg": 5.5, "w": 1024, "h": 1024},
    "photo-xl": {"arch": "sdxl", "repo": "SG161222/RealVisXL_V5.0",
                 "prompt": "a cozy ramen shop on a rainy night, neon signs reflecting on wet "
                           "pavement, cinematic lighting, photorealistic, 35mm",
                 "neg": PHOTO_XL_NEG, "suffix": "",
                 "steps": 30, "cfg": 5.0, "w": 1024, "h": 1024},
}

cfg = MODELS[MODEL]
print("loading:", MODEL, "->", cfg["repo"])

if cfg["arch"] == "sd15":
    # SD1.5: always load with the NSFW safety filter on (this runs in school)
    from transformers import CLIPImageProcessor
    from diffusers.pipelines.stable_diffusion.safety_checker import StableDiffusionSafetyChecker
    checker = StableDiffusionSafetyChecker.from_pretrained(
        "CompVis/stable-diffusion-safety-checker", torch_dtype=torch.float16)
    extractor = CLIPImageProcessor.from_pretrained("CompVis/stable-diffusion-safety-checker")
    kw = dict(torch_dtype=torch.float16, safety_checker=checker, feature_extractor=extractor)
    if cfg.get("vae") == "mse":   # *_noVAE models need a VAE added or colors look dull
        kw["vae"] = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-mse",
                                                  torch_dtype=torch.float16)
    pipe = StableDiffusionPipeline.from_pretrained(cfg["repo"], **kw)
else:
    # SDXL: high quality. No built-in filter (see the Step 2 notes)
    kw = dict(torch_dtype=torch.float16, use_safetensors=True, add_watermarker=False)
    if cfg.get("lpw"):            # pipeline that handles long / tag / weighted prompts
        kw["custom_pipeline"] = "lpw_stable_diffusion_xl"
    pipe = StableDiffusionXLPipeline.from_pretrained(cfg["repo"], **kw)

# scheduler (how the noise is removed). The Karras variant keeps texture stable
pipe.scheduler = DPMSolverMultistepScheduler.from_config(
    pipe.scheduler.config, use_karras_sigmas=True, algorithm_type="dpmsolver++")
pipe = pipe.to("cuda")

HAS_FILTER = (cfg["arch"] == "sd15")
print("ready:", cfg["repo"], "| safety filter:", "ON" if HAS_FILTER else "none (SDXL)")
print()
print("--- recommended for this model (copy into the Step 3 form) ---")
print("prompt   :", cfg["prompt"])
print("negative :", cfg["neg"])
print(f"steps={cfg['steps']}  guidance={cfg['cfg']}  size={cfg['w']}x{cfg['h']}")
if cfg["suffix"]:
    print("quality tags", repr(cfg["suffix"]), "are appended automatically")'''))
cells.append(md('''## Step 3 — Generate

What the dials mean:
- `prompt`: what to draw (**in English**; ask Gemini to translate if you like)
- `negative_prompt`: what to keep OUT
- `seed`: the dice. **same seed + same words = same image**
- `guidance`: how hard to obey the words (about 7 for basic / about 5 for SDXL)
- `steps`: passes from noise to image (about 25–28)

Just change the form below and press ▶. **The recommended values for your model** are printed in the Step 2 output (copy them).'''))
cells.append(code('''#@title ② Generate  { display-mode: "form" }
#@markdown In English (ask Gemini to translate). Same seed + same words = same image. For SDXL (anime-xl/photo-xl), guidance around 5 looks best.
prompt = "a cozy ramen shop on a rainy night, neon signs, watercolor style"  #@param {type:"string"}
negative_prompt = "low quality, blurry, text, watermark"  #@param {type:"string"}
seed = 42  #@param {type:"integer"}
steps = 25  #@param {type:"slider", min:10, max:40, step:1}
guidance = 7.0  #@param {type:"slider", min:1, max:15, step:0.5}

full_prompt = prompt + cfg["suffix"]          # quality tags (per model) are appended for you
generator = torch.Generator("cuda").manual_seed(seed)
image = pipe(full_prompt, negative_prompt=negative_prompt,
             num_inference_steps=steps, guidance_scale=guidance,
             width=cfg["w"], height=cfg["h"], generator=generator).images[0]
# A pure-black image = the safety filter fired (SD1.5 only). Change the words and retry
image'''))
cells.append(md('''## Step 4 — Experiments

1. **Fix the seed, change only the words** — turn `watercolor style` into `pixel art`?
2. **Fix the words, change only the seed** — same order, a different picture
3. Try `guidance` at 2 and 15 — what happens when it obeys too hard?

(The "control a picture with words" feeling from the Day 1 contest — now at the level of the dials.)

Note: this experiment works because the dials respond cleanly on the **basic tier** and **standard SDXL**. "Fast" models (Lightning/Turbo) that draw in 4–6 steps ignore guidance and break this experiment.'''))
cells.append(code('''#@title ③ Experiment: one more image with different dials  { display-mode: "form" }
#@markdown Fix the seed and change only the words / fix the words and change only the seed / compare guidance at 2 and 15
prompt = "a cozy ramen shop on a rainy night, neon signs, pixel art"  #@param {type:"string"}
seed = 42  #@param {type:"integer"}
steps = 25  #@param {type:"slider", min:10, max:40, step:1}
guidance = 7.0  #@param {type:"slider", min:1, max:15, step:0.5}

full_prompt = prompt + cfg["suffix"]
generator = torch.Generator("cuda").manual_seed(seed)
pipe(full_prompt, negative_prompt=cfg["neg"],
     num_inference_steps=steps, guidance_scale=guidance,
     width=cfg["w"], height=cfg["h"], generator=generator).images[0]'''))
cells.append(md('''## Reflection

- Whose pictures was this model trained on? Did they agree? — revisit the copyright question, today as the one **doing the generating**.
- How is a service like Gemini different from an open model you run yourself? (safety filter, responsibility, freedom)
  - Today you actually switched between **basic = filter ON / high-quality (SDXL) = no filter**. Why does a service add a filter?
- Is the picture you made "your work"? The AI's? The training-data artists'?'''))
write_nb("image_gen_advanced_en.ipynb", cells, "Image Generation Advanced — English (Summer AI)")

# ---------------------------------------------------------------- survivor machine
cells = []
cells.append(md('''# Survivor Machine — サイトの木は本物か? / Is the website tree real?

サイトの **Survivor Machine** で「自分は助かるか?」を遊んだあと、このノートで確かめます。

- サイトの木に埋め込んだ生存確率は、**本物の Titanic データから出した実際の割合**であることを確認する
- 本物の決定木(深さ3)を sklearn で学習し、**特徴量重要度**を出す → 「運命を変える最小の一手」がなぜ性別だったか分かる
- (任意) GAS で集めたクラスの予想を読み込み、**人間 vs モデル**を比べる

このノートは公開リポジトリ **github.com/itoksk/summer-ai-materials** の `materials/notebooks/` にあります。'''))

cells.append(md('''## Step 1 — 本物のデータを読む / Load the real data'''))
cells.append(code('''import pandas as pd

url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
try:
    df = pd.read_csv(url)
except Exception:
    print("ダウンロードできない場合: 先生から titanic.csv をもらって左の folder にアップロードしてください")
    df = pd.read_csv("titanic.csv")
print("乗客:", len(df), "人  全体の生存率:", round(df["Survived"].mean(), 3))
df.head()'''))

cells.append(md('''## Step 2 — サイトの数字 vs 実データ / Website numbers vs real data

サイトのウィジェットは、これらの確率を木に埋め込んでいます。本当にデータと一致する?'''))
cells.append(code('''g = df.dropna(subset=["Age"]).copy()

def rate(mask):
    sub = g[mask]
    return (len(sub), round(sub["Survived"].mean(), 2)) if len(sub) else (0, None)

print("                 サイトの値   実データ (人数, 生存率)")
print("女性 1等          0.97        ", rate((g.Sex=="female") & (g.Pclass==1)))
print("女性 2等          0.92        ", rate((g.Sex=="female") & (g.Pclass==2)))
print("女性 3等          0.50        ", rate((g.Sex=="female") & (g.Pclass==3)))
print("男児(<=6) 1-2等   0.83        ", rate((g.Sex=="male") & (g.Age<=6) & (g.Pclass<=2)))
print("男児(<=6) 3等     0.36        ", rate((g.Sex=="male") & (g.Age<=6) & (g.Pclass==3)))
print("男性(>6) 1等      0.36        ", rate((g.Sex=="male") & (g.Age>6) & (g.Pclass==1)))
print("男性(>6) 2-3等    0.13        ", rate((g.Sex=="male") & (g.Age>6) & (g.Pclass>=2)))'''))
cells.append(md('''**観察 / Observe**: サイトの数字は作り物ではなく、110年前の実データの割合そのもの。だから「自分の判定」も本物だった。'''))

cells.append(md('''## Step 3 — 本物の決定木と特徴量重要度 / The real tree + feature importance'''))
cells.append(code('''from sklearn.tree import DecisionTreeClassifier, plot_tree
import matplotlib.pyplot as plt

d = df.dropna(subset=["Age"]).copy()
d["Sex_male"] = (d["Sex"] == "male").astype(int)
X = d[["Sex_male", "Pclass", "Age"]]
y = d["Survived"]
clf = DecisionTreeClassifier(max_depth=3, random_state=0).fit(X, y)

plt.figure(figsize=(14, 7))
plot_tree(clf, feature_names=["Sex(male=1)", "Pclass", "Age"],
          class_names=["died", "survived"], filled=True, rounded=True)
plt.show()

print("特徴量重要度 / feature importance:")
for name, imp in zip(X.columns, clf.feature_importances_):
    print(" ", name, round(imp, 3))'''))
cells.append(md('''**つながり / Connect**: 一番大きい重要度は **Sex**。だからウィジェットで「運命を変える最小の一手」が(多くの場合)性別だった。木はそれを誰にも教わらず、データだけから決めた。'''))

cells.append(md('''## Step 4 — モデルが測っていないもの / What the model never measured

ウィジェットの「勇気・泳げる・運がいい」をいくらONにしても判定は動かなかった。理由はここにある —
**データにそんな列が無い**。モデルは列にあるものしか知らない。'''))
cells.append(code('''print("データにある列 / columns the model could ever see:")
print(list(df.columns))
print()
print("'勇気' 'やさしさ' 'あきらめない心' のような列は、どこにも無い。")'''))

cells.append(md('''## Step 5 (任意) — 人間 vs モデル / Class guesses vs the model

GAS のスプレッドシートを「ファイル → ダウンロード → カンマ区切り(.csv)」で `responses.csv` にして、
左の folder アイコンからアップロードしてから実行(無ければ自動でスキップ)。'''))
cells.append(code('''try:
    cls = pd.read_csv("responses.csv")

    def model_predict(sex, pclass, age):
        if sex == "female":
            p = 0.97 if pclass == 1 else (0.92 if pclass == 2 else 0.5)
        elif age <= 6:
            p = 0.36 if pclass == 3 else 0.83
        else:
            p = 0.36 if pclass == 1 else 0.13
        return "survive" if p >= 0.5 else "dies"

    cls["model"] = cls.apply(
        lambda r: model_predict(r["sex"], int(r["pclass"]), float(r["age"])), axis=1)
    agree = (cls["guess"] == cls["model"]).mean()
    print("クラス人数:", len(cls))
    print("モデルが survive と判定:", int((cls["model"] == "survive").sum()))
    print("みんなが survive と予想:", int((cls["guess"] == "survive").sum()))
    print("人間とモデルの一致率:", round(agree * 100), "%")
except FileNotFoundError:
    print("responses.csv が無いのでスキップ。サイトのウィジェットだけでも体験は完結します。")'''))

cells.append(md('''## 問い / Questions
- サイトの数字と実データはどれくらい一致した? ずれた所は、なぜ?
- 特徴量重要度で Sex が一番大きいのはなぜ? それは「世界の真実」か「1912年の救命ボートの真実」か?
- 人間の予想とモデル、どちらがよく当たった? モデルが見落としている人間的なものは何?'''))
write_nb("survivor_machine_colab.ipynb", cells, "Survivor Machine (Summer AI)")

print("done")
