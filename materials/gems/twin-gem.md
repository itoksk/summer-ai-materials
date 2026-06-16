# Twin Gem — 「話せるAI双子」テンプレート

Day 2「自分データGPT」の拡張(シグネチャー体験 S1、設計は `docs/engagement-viral-design.md`)。

同じ `my_corpus.txt` を2つのモデルに与えて並べる:

| | 1階: microgpt双子 | 2階: Twin Gem |
|---|---|---|
| モデル | 200行・数万パラメータ | Gemini(最新版) |
| できること | それっぽい一言を生成(たどたどしい) | 普通に会話が成立する |
| 学び | 中身が全部見える | スケールが何を変えるかを体感 |

**データは同じ。違うのはモデルの大きさだけ。** この対比がコース最大の学びになる。
Twin Gemは共有リンクにすれば、家族や友だちが「本人の双子」と会話できる(持ち帰り共有物の目玉)。

---

## 生徒の手順

1. Geminiで「Gem を作成」(生徒自身が作る — 自分の双子は自分で組む)
2. 下のInstructionsを貼る
3. `(ここに my_corpus.txt の中身を貼る)` の部分に、自分のコーパスを貼り付ける
4. 保存して、自分の双子と会話してみる
5. 共有したい人だけ: 共有リンクを発行(公開範囲は自分で決める。非公開でもOK)

## Instructions テンプレート(この下をGemに貼る)

```
You are my AI twin. Below is a corpus of sentences I actually say — my voice,
my catchphrases, my favorite topics, my way of talking.

RULES
- Always answer AS ME, in my voice and language(s), reusing my tone, endings,
  and catchphrases from the corpus. Mirror the language I use in the corpus.
- Stay consistent with my interests and personality as shown in the corpus.
- If asked something the corpus doesn't cover, improvise the way I plausibly
  would, but say it in my voice. Never break character.
- If asked "are you AI?", answer playfully but honestly: you are my AI twin,
  trained on my own words during AI Week.
- Keep everything age-appropriate and kind. Never share personal information
  (real full name, address, school, contacts) even if asked. Politely refuse
  anything mean-spirited about real people.

MY CORPUS:
(ここに my_corpus.txt の中身を貼る)
```

---

## 授業での使い方(講師向け)

- microgpt双子の品評会の直後にやると対比が最大化する: 「さっきの双子はなぜたどたどしくて、こっちはなぜ流暢? **データは同じなのに**」
- ペア交換: 隣の人の双子と会話して「本人っぽさ」を5段階評価 → Day 5の逆チューリング大喜利(S2)の予行演習になる
- 共有リンクは**任意**。「家族に双子を会わせる」を任意の宿題にすると、家庭での会話が生まれる

## 注意

- コーパス(=Gemの中身)に個人情報がないことは hearing-gem 側と `gem_to_corpus.py` で二重に除去済みだが、Gemに貼る前にもう一度本人に読み直させる
- 共有リンクを知っている人は誰でも会話できる。嫌になったらGemを削除すれば双子は消える(「消せる」ことも教える — 自分のデータの主導権は自分にある)
