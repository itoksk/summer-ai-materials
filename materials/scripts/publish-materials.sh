#!/usr/bin/env bash
# Publish the course materials to a DEDICATED PUBLIC GitHub repo so the
# planning docs in the main summer-ai repo can stay private.
#
# The site (microgpt-lab/src/lib/resources.ts) points at:
#   itoksk/summer-ai-materials   (a repo whose root contains a `materials/` folder)
#
# Run this as the itoksk GitHub account:
#   gh auth switch --user itoksk        # if needed
#   bash materials/scripts/publish-materials.sh
#
# Re-running it updates the public repo with your latest materials/.
set -euo pipefail

OWNER="itoksk"
REPO="summer-ai-materials"
BRANCH="main"

# Resolve the project's materials/ folder (this script lives in materials/scripts/).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MATERIALS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Materials source: $MATERIALS_DIR"
command -v gh >/dev/null || { echo "ERROR: gh CLI not found"; exit 1; }
echo "Active GitHub account:"; gh auth status 2>&1 | grep -i "account" | head -1 || true

# Keep the published microgpt.py in sync with its canonical source so the copy never drifts.
# Canonical lives at <repo>/microgpt-lab/microgpt.py (build_notebooks.py reads the same file).
CANON_MICROGPT="$MATERIALS_DIR/../microgpt-lab/microgpt.py"
if [ -f "$CANON_MICROGPT" ]; then
  cp "$CANON_MICROGPT" "$MATERIALS_DIR/scripts/microgpt.py"
  echo "Synced materials/scripts/microgpt.py from microgpt-lab/microgpt.py"
else
  echo "WARNING: canonical microgpt.py not found at $CANON_MICROGPT — publishing the existing copy"
fi

# Stage a clean copy with the materials/ folder at the repo root.
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/materials"
# Copy everything except OS cruft.
( cd "$MATERIALS_DIR" && find . -name '.DS_Store' -prune -o -type f -print | while read -r f; do
    mkdir -p "$TMP/materials/$(dirname "$f")"
    cp "$f" "$TMP/materials/$f"
  done )

cat > "$TMP/README.md" <<EOF
# summer-ai-materials

Public code distribution for the **AI from Scratch** 5-day course site.
Notebooks, datasets, scripts and Gem prompts live under \`materials/\`.

- Colab notebooks open via \`colab.research.google.com/github/$OWNER/$REPO/blob/$BRANCH/materials/notebooks/<name>.ipynb\`
- Datasets are fetched from \`raw.githubusercontent.com/$OWNER/$REPO/$BRANCH/materials/data/<name>.txt\`

Source of truth: the (private) summer-ai repo. Re-publish with materials/scripts/publish-materials.sh.
EOF

# Troubleshooting section — literal markdown (quoted heredoc, no shell expansion).
cat >> "$TMP/README.md" <<'EOF'

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
EOF

cd "$TMP"
git init -q -b "$BRANCH"
git add .
git commit -q -m "Publish course materials (notebooks, datasets, scripts, gem prompts)"

if gh repo view "$OWNER/$REPO" >/dev/null 2>&1; then
  echo "Repo exists — pushing update to $OWNER/$REPO"
  git remote add origin "https://github.com/$OWNER/$REPO.git"
  git push -f origin "$BRANCH"
else
  echo "Creating public repo $OWNER/$REPO and pushing"
  gh repo create "$OWNER/$REPO" --public --source=. --remote=origin --push \
    --description "Course materials (notebooks, datasets, gem prompts) for the AI from Scratch site"
fi

echo
echo "Done. Verify a dataset is reachable (should print 200):"
echo "  curl -s -o /dev/null -w '%{http_code}\\n' https://raw.githubusercontent.com/$OWNER/$REPO/$BRANCH/materials/data/input_abc.txt"
