# materials/ — 5日間コースの配布素材

カリキュラム全体の設計は `docs/curriculum-5days.md`、日別の進行は `docs/lesson-flow/day1.md`〜`day5.md` を参照。

## gems/ — Gemini Gem のシステムプロンプト

| ファイル | 用途 | 使う日 |
|---|---|---|
| `lyrics-gem.md` | Suno用の作詞サポートGem(タイトル/スタイル/歌詞の3点セットを出力) | Day 1 |
| `hearing-gem.md` | 「自分データGPT」用インタビュアー(microgpt学習コーパスを出力) | Day 2 |
| `kabeuchi-gem.md` | ハッカソン企画の壁打ちメンター(企画シート出力。7つの黄金律・審査ルーブリック付き) | Day 4–5 |
| `twin-gem.md` | 「話せるAI双子」テンプレート(自分のコーパスを貼って双子を作る。逆チューリング・クラスGPT・タイムカプセルの起点) | Day 2, 5 |

いずれも「システムプロンプト」のコードブロックをGemのInstructionsに貼って登録し、共有リンクを生徒に配る。

## notebooks/ — Google Colab ノートブック

| ファイル | 用途 | 使う日 | ランタイム |
|---|---|---|---|
| `microgpt_colab.ipynb` | 200行GPTの訓練・温度実験・データセットメニュー・自分データGPT | Day 2 | CPU |
| `tetris_hand_colab.ipynb` | tetris-hand(手で操作するテトリス)をColabで起動・改造 | Day 3 | CPU |
| `yolo_world_colab.ipynb` | YOLO World ゼロショット物体検出(`set_classes` で任意クラスを指定・conf閾値) | Day 3 | **GPU (T4)** |
| `titanic_colab.ipynb` | Titanic生存予測(決定木・過学習実験)— 予備モジュール | Day 3 | CPU |
| `image_gen_advanced.ipynb` | Stable Diffusionを直接動かす — 上級予備モジュール | Day 1 | **GPU (T4)** |

## scripts/

| ファイル | 用途 |
|---|---|
| `gem_to_corpus.py` | ヒアリングGemの出力 → microgpt用 `input.txt` 変換(PII除外・整形・水増し) |
| `microgpt_lab.py` | microgpt.py の実験版(データ・ステップ数・温度をCLIで変更可) |

どちらも依存ライブラリなし(Python標準ライブラリのみ)。ノートブックにも同じものが埋め込み済みなので、単体配布は任意。

## data/ — microgpt 学習用コーパス(データセット・メニュー)

| ファイル | 中身 | 行数 | 語彙 |
|---|---|---|---|
| `input_abc.txt` | フォーク民謡(ABC記譜法、Nottingham Music Database) | 1,017 | 40 |
| `input_chess.txt` | チェスの序盤棋譜(Lichess) | 1,340 | 27 |
| `input_haiku.txt` | 俳句・ひらがな化済み(青空文庫のパブリックドメイン句集) | 2,800 | 80 |

出典・ライセンス・前処理の詳細は `data/README.md`。**注意**: コーパス本体に出典コメントを書き込まない(1行=1学習データのため)。
