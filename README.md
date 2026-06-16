# summer-ai-materials

Public code distribution for the **AI from Scratch** 5-day course site.
Notebooks, datasets, scripts and Gem prompts live under `materials/`.

- Colab notebooks open via `colab.research.google.com/github/itoksk/summer-ai-materials/blob/main/materials/notebooks/<name>.ipynb`
- Datasets are fetched from `raw.githubusercontent.com/itoksk/summer-ai-materials/main/materials/data/<name>.txt`

Source of truth: the (private) summer-ai repo. Re-publish with materials/scripts/publish-materials.sh.

## Updating your clone / クローンの更新

We sometimes fix scripts after class. To get the latest, update the repo you cloned.

**Easiest — re-clone (delete the old folder first):**
```
git clone https://github.com/itoksk/summer-ai-materials.git
```

**Or update your existing clone to match the latest:**
```
git fetch origin
git reset --hard origin/main
```

`git pull` can fail here with an "unrelated histories" error (each publish is a fresh
snapshot), so use `git reset --hard origin/main` or just re-clone.

日本語: 授業のあとにスクリプトを直すことがあります。クローン済みのフォルダを更新してください。
いちばん簡単なのは、古いフォルダを消して **クローンし直す** こと。既存のフォルダを使うなら
`git fetch origin` → `git reset --hard origin/main`（`git pull` は失敗することがあります）。

## Running microgpt.py / 実行方法

```
cd materials/scripts
python microgpt.py     # Windows
python3 microgpt.py    # macOS / Linux
```

If you still hit one of these, your copy is old — update it (see above):

- **macOS `CERTIFICATE_VERIFY_FAILED`** — Homebrew Python has no CA certificates. The
  script now reads the bundled `materials/data/pokemon.txt`, so no download is needed.
- **Windows `UnicodeDecodeError: 'cp932'`** — files are now read as UTF-8.
- **Windows "Python was not found"** — run `python` (not `python3`).
- **Leftover empty `input.txt`** from an earlier failed run — delete it and re-run:
  `rm input.txt` (macOS) / `del input.txt` (Windows).

注意: 上のエラーが出るならコピーが古いので更新してください。Windows は `python`（`python3` ではない）。
前回の失敗で空の `input.txt` が残っていたら削除して実行し直してください。
