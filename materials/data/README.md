# Character-level training corpora for microgpt.py

Three corpora for the course's pure-Python GPT (`microgpt.py`). Format: **one document per
line**, UTF-8, Unix newlines, no blank lines, no header/metadata lines, deduplicated.
Retrieval date for all sources: **2026-06-13**.

| File | Lines | Bytes | Char length min/med/max | Unique chars (vocab) |
|---|---|---|---|---|
| `input_haiku.txt` | 2,800 | 149,455 | 8 / 17 / 32 | 80 |
| `input_chess.txt` | 1,340 | 63,240 | 21 / 46 / 48 | 27 |
| `input_abc.txt` | 1,017 | 60,165 | 34 / 60 / 64 | 40 |

---

## 1. input_haiku.txt — Japanese haiku (hiragana)

**Source:** Aozora Bunko (青空文庫), seven public-domain haiku collections
(all flagged 作品著作権フラグ「なし」 in the official Aozora index
`list_person_all_extended_utf8.csv`):

| Collection | Author (died) | Text file URL |
|---|---|---|
| 尾崎放哉選句集 | 尾崎放哉 (1926) | https://www.aozora.gr.jp/cards/000195/files/974_txt_317.zip |
| 川端茅舎句集 | 川端茅舎 (1941) | https://www.aozora.gr.jp/cards/000369/files/55239_ruby_65169.zip |
| 不器男句集 | 芝不器男 (1930) | https://www.aozora.gr.jp/cards/000594/files/55240_ruby_66943.zip |
| 草木塔 | 種田山頭火 (1940) | https://www.aozora.gr.jp/cards/000146/files/749_ruby_298.zip |
| 鳴雪句集 | 内藤鳴雪 (1926) | https://www.aozora.gr.jp/cards/000684/files/55833_txt_63814.zip |
| 普羅句集 | 前田普羅 (1954) | https://www.aozora.gr.jp/cards/001719/files/55258_ruby_64312.zip |
| 松本たかし句集 | 松本たかし (1956) | https://www.aozora.gr.jp/cards/001720/files/55259_ruby_66667.zip |

**License:** Public domain in Japan (all authors died before 1968; Japanese copyright term
for these works has expired). Aozora Bunko asks that redistributed files follow its
handling guidelines (https://www.aozora.gr.jp/guide/kijyunn.html); this corpus is a
derived excerpt, with source attribution given here.

**Preprocessing:**
- Decoded Shift_JIS (cp932) → UTF-8; CRLF → LF.
- Stripped Aozora header (everything up to the second `----` rule line) and footer
  (from `底本：` onward).
- Removed ruby annotations `《...》`, ruby start markers `｜`, editorial notes `［＃...］`,
  and gaiji placeholders `※`.
- For "season-word label + full-width space + haiku" lines (鳴雪句集 layout), kept the
  last full-width-space-separated segment.
- Kept only haiku-like lines: 8–25 Japanese characters, no ASCII, no `。` (filters prose),
  plus removal of a few non-haiku headings (e.g. 青空文庫版まえがき).
- **Kanji → hiragana conversion with pykakasi 2.x** (to keep the char-level vocab small),
  then katakana → hiragana folding, and expansion of iteration marks
  (`ゝゞヽヾ`, `／＼`, `／″＼`) into explicit kana.
- Final strict charset filter (hiragana + `ー、・「」？！…` only), NFC normalization,
  length filter 8–35 chars, dedup, capped at 2,800 lines (file-size guideline).

**Caveats:**
- pykakasi produces modern dictionary readings; some readings differ from the poetic ones
  (e.g. 蛙 → かえる rather than かわず), so the 5-7-5 on-count is not exact for every line.
- Source texts use historical kana (旧仮名遣い), which mixes with pykakasi's modern
  readings (e.g. つて / って alternations).
- 山頭火 and 放哉 are free-verse (自由律) haiku, so line lengths vary beyond strict 5-7-5.

**Samples:**
```
きれたこのいとかかりけりうめのえだ
みずうつてしずかないえやなつやなぎ
きのかんよりつりどこみゆるあおばかな
```

---

## 2. input_chess.txt — chess opening move sequences

**Source:** Lichess public games-export API, 400 most recent blitz/rapid/classical games
per account from five strong, active accounts (retrieved one request at a time with
pauses, per API politeness rules):

```
https://lichess.org/api/games/user/{user}?max=400&perfType=blitz,rapid,classical&moves=true&tags=false
```

for `{user}` in: `DrNykterstein`, `penguingim1`, `nihalsarin2004`, `Zhigalko_Sergei`,
`RebeccaHarris` (1,997 games total).

**License:** Lichess game data is released under **Creative Commons CC0** (see
https://database.lichess.org/ — "released under the Creative Commons CC0 license");
chess moves themselves are facts and not copyrightable.

**Preprocessing:**
- Split PGN stream into per-game movetext blocks (export already had no tag headers).
- Removed `{...}` comments, `$n` NAGs, and result tokens (`1-0`, `0-1`, `1/2-1/2`, `*`).
- Kept the opening moves of each game up to ≤ 48 characters, cutting only at a token
  boundary and stripping any dangling move number (lines never end with e.g. `7.`).
- Dropped lines under 20 chars (instantly aborted games); deduplicated across all five
  players (1,997 games → 1,340 unique opening lines).

**Samples:**
```
1. e4 Nf6 2. e5 Nd5 3. Nc3 Nxc3 4. dxc3 d6
1. d4 Nf6 2. c4 g6 3. Nc3 Bg7 4. e3 d6 5. e4 O-O
1. c4 g6 2. Nc3 Bg7 3. g3 c5 4. Bg2 Nc6 5. e4 d6
```

---

## 3. input_abc.txt — ABC notation folk melodies (Nottingham Music Database)

**Source:** Nottingham Music Database (~1,030 British/Irish folk tunes collected by Eric
Foxley, ABC conversion via abc.sourceforge.net/NMD), using the cleaned mirror:

- Repo: https://github.com/jukedeck/nottingham-dataset (directory `ABC_cleaned/`)
- Files: `ashover.abc, hpps.abc, jigs.abc, morris.abc, playford.abc, reelsa-c.abc,
  reelsd-g.abc, reelsh-l.abc, reelsm-q.abc, reelsr-t.abc, reelsu-z.abc, slip.abc,
  waltzes.abc, xmas.abc` fetched from
  `https://raw.githubusercontent.com/jukedeck/nottingham-dataset/master/ABC_cleaned/<file>`

**License:** **GPL-3.0** (repository license of jukedeck/nottingham-dataset). The tunes
are traditional; this dataset is the standard ABC corpus used in ML research.

**Why not thesession.org?** The originally planned source
(https://github.com/adactio/TheSession-data) was downloaded and inspected first, but its
`LICENSE.md` **explicitly prohibits AI use, including training AI models**, so it was
discarded and replaced by the Nottingham Music Database.

**Preprocessing:**
- Split each `.abc` file into tunes at `X:` blocks; took the first `K:` (key) and `M:`
  (meter) header of each tune.
- Body = music lines after the first `K:` (header/field lines `T: S: P: Y: ...` and
  `%` comments skipped), joined into a single line.
- Removed `"..."` chord symbols, `!...!` decorations, `y` spacers, backslashes;
  collapsed whitespace.
- Prefixed each line with compact `K:<key> M:<meter> `, then truncated to ≤ 64 chars at
  the last bar `|` boundary.
- Dropped lines < 24 chars or containing characters outside the ABC core charset;
  deduplicated (1,034 tunes → 1,017 lines).

**Samples:**
```
K:G M:3/4 e|:d2B|A3/2B/2c|B2G|A2e|d2B|A3/2B/2c| B=F| G2e:||
K:D M:2/2 A2|:a3/2b/2a3/2g/2 f2(3def|g3/2a/2g3/2f/2 e2A2|
K:A M:2/4 |:A c/4B/4A/4G/4|A/2c/2 e/2a/2|g/2b/2 e/2d/2|c/2AB/2|
```

---

# Day 3 — heatstroke.csv (regression dataset)

A separate dataset (not a microgpt corpus): daily **heat-illness emergency transports**
joined with daily **temperature**, for the Day 3 regression notebook
(`materials/notebooks/heatstroke_colab.ipynb`). One row per **prefecture × day**, summer
months (May–Sep), **2018–2024**, for 7 climate-diverse prefectures (Hokkaido, Tokyo, Aichi,
Osaka, **Hyogo/Kobe — the course location**, Fukuoka, Okinawa). **7,280 rows.** Retrieval
date: **2026-06-16**. Rebuild with `materials/scripts/build_heatstroke_data.py`.

**Columns:** `date, year, month, weekday, pref_code, pref_en, pref_ja, tmax_c, tmean_c,
humidity_pct, transported, elderly, severe` — target = `transported` (people taken to
hospital for heat illness that day in that prefecture).

**Sources & license:**
- **Transports (the prediction target): 総務省消防庁「熱中症による救急搬送状況」**
  (Fire and Disaster Management Agency), per-year Excel files, daily × prefecture, 2008–2025:
  https://www.fdma.go.jp/disaster/heatstroke/post4.html — Japanese government public statistics
  (政府標準利用規約 / CC-BY-compatible; attribution given here).
- **Temperature & humidity (features): Open-Meteo Historical Weather API** (ERA5 reanalysis),
  daily `temperature_2m_max / temperature_2m_mean / relative_humidity_2m_mean` at each
  prefecture capital's coordinates: https://open-meteo.com/ — data under CC-BY 4.0.
- Alert-threshold context (not used as a column): 環境省 熱中症予防情報サイト 暑さ指数(WBGT)
  https://www.wbgt.env.go.jp/

**Caveats (taught explicitly in the notebook):**
- Temperature is the **capital city's** value used as a proxy for the whole (large) prefecture.
- `transported` counts scale with **prefecture population** (Tokyo ≫ Okinawa); for a fair
  cross-prefecture comparison, normalise per 100k residents.
- The heat→transport relation is strongly **non-linear** (it explodes above ~30 °C), so a
  straight-line fit under-predicts the hottest days — this is the lesson of the notebook.

**Samples:**
```
date,year,month,weekday,pref_code,pref_en,pref_ja,tmax_c,tmean_c,humidity_pct,transported,elderly,severe
2018-07-23,2018,7,Mon,13,Tokyo,東京都,39.1,32.4,55,406,236,34
2024-07-29,2024,7,Mon,13,Tokyo,東京都,38.2,32.4,56,281,178,28
```
