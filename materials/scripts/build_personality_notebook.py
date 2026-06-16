#!/usr/bin/env python3
"""Generate the Day 3 personality-matching Colab notebook.

Adapted for the summer course (bilingual EN/JA, no API keys) from the
noda-ai-stu lesson `personality_analysis.ipynb`: interactive radar quiz,
colour-coded compatibility checker, heatmap + top-5 dashboard, K-means +
PCA team scatter, and diversity/harmony team scoring. Run:

    python3 materials/scripts/build_personality_notebook.py
"""
import json
import os

ROOT = "/Users/keisuke/git/summer-ai"
OUT = os.path.join(ROOT, "materials", "notebooks")
os.makedirs(OUT, exist_ok=True)


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


cells = []

cells.append(md('''# Matching Lab — Let the Math Find Your Twin / マッチングラボ — 数学に双子を探させる

This afternoon your class survey becomes **data**. Each person is a row of 1–5 answers — a vector — and we measure how alike any two people are with **cosine similarity**, exactly the math from this morning.

クラスのアンケートが **データ** になります。1人は 1〜5 の答えの並び(ベクトル)。午前に学んだ **コサイン類似度** で、2人がどれだけ似ているかを測ります。

**What you will do / やること**
1. Upload your class CSV / クラスの CSV をアップロード
2. Check one similarity by hand / 1組だけ手計算で確かめる
3. Radar profile of one person / 1人のレーダープロフィール
4. Compatibility checker (colour-coded) / 相性チェッカー(色分け)
5. Heatmap + "most similar" top-5 / ヒートマップと「似ている人トップ5」
6. K-means suggests teams / K-means がチームを提案
7. Score each team's balance / 各チームのバランスを採点

> Run the cells **one at a time, in order**. Before each one, PREDICT what will appear — that is how you stay the scientist, not the spectator. / セルは **1つずつ順番に**。実行の前に「何が出るか」を予想しよう。

> No API keys, no GPU. Everything runs in this notebook. / APIキー不要・GPU不要。すべてこのノートの中で動きます。'''))

# ---------------------------------------------------------------- setup
cells.append(md('''## 1. Setup / 準備

Installs a Japanese font for matplotlib so question labels in either language render cleanly. / 日本語フォントを入れて、どちらの言語のラベルもきれいに表示します。'''))

cells.append(code('''# @title Run setup / 準備を実行
!pip install -q japanize-matplotlib seaborn scikit-learn ipywidgets

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output

try:
    import japanize_matplotlib  # noqa: F401  (registers a JP-capable font)
except Exception:
    pass

print("Ready / 準備完了")'''))

# ---------------------------------------------------------------- upload
cells.append(md('''## 2. Upload your class CSV / クラスの CSV をアップロード

Export your Google Form responses (Responses tab → ⋮ → Download responses (.csv)) and upload the file here. The code auto-detects the columns, so **any number of questions works**.

Google フォームの回答を CSV で書き出して(「回答」タブ → ⋮ → 回答をダウンロード(.csv))、ここにアップロード。列は自動認識するので **質問は何問でもOK**。'''))

cells.append(code('''# @title Upload + auto-detect columns / アップロードと列の自動認識
from google.colab import files

print("Choose your class_survey.csv ... / class_survey.csv を選んでね ...")
uploaded = files.upload()

csv_files = [f for f in uploaded.keys() if f.endswith(".csv")]
if not csv_files:
    raise SystemExit("No .csv found — run this cell again. / CSVが見つかりません。もう一度実行してね。")

data = pd.read_csv(csv_files[0])

# Find the nickname column by NAME (works in English or Japanese, any order),
# and keep only the numeric 1-5 answer columns. The form just needs ONE
# short-answer "Nickname" question plus the 1-5 questions.
def looks_like_timestamp(name):
    n = str(name).lower()
    return ("time" in n) or ("タイム" in str(name)) or ("時刻" in str(name)) or ("日時" in str(name))

def looks_like_nickname(name):
    n = str(name).lower()
    keys = ["nick", "name", "handle", "ニック", "なまえ", "名前", "氏名", "ハンドル"]
    return any(k in n for k in keys)

cols = [c for c in data.columns if not looks_like_timestamp(c)]
name_cols = [c for c in cols if looks_like_nickname(c)]
if name_cols:
    nickname_col = name_cols[0]
else:
    nickname_col = cols[0]
    print("NOTE / 注意: no 'Nickname' question found — using:", nickname_col)
    print("Add a short-answer 'Nickname' question to your form for clean labels.")
    print("フォームに記述式の『Nickname / ニックネーム』質問を1つ入れると、ラベルがきれいになります。")

# Answer columns = every non-timestamp, non-name column whose values are all numeric (the 1-5 scales).
question_cols = [c for c in cols
                 if c != nickname_col and pd.to_numeric(data[c], errors="coerce").notna().all()]

nicknames = data[nickname_col].astype(str).values
student_vectors = data[question_cols].astype(float).values

print(f"People / 人数: {len(nicknames)}")
print(f"Questions / 質問数: {len(question_cols)}")
print(f"Name column / 名前の列: {nickname_col}")
print("First rows / 先頭:")
display(data[[nickname_col] + list(question_cols[:4])].head())'''))

# ---------------------------------------------------------------- cosine + by hand
cells.append(md('''## 3. Cosine similarity — and a by-hand check / コサイン類似度と手計算チェック

We build an N×N table of how alike every pair is. Then we re-compute ONE pair by hand to prove the library is doing exactly the morning's formula. / 全ペアの似ている度の表を作り、1組だけ手計算で確かめます。'''))

cells.append(code('''# @title Build the similarity table / 類似度の表を作る
sim = cosine_similarity(student_vectors)
sim_df = pd.DataFrame(sim, index=nicknames, columns=nicknames)
print("Similarity table (first 5x5) / 類似度の表(最初の5x5):")
display(sim_df.iloc[:5, :5].round(3))'''))

cells.append(code('''# @title Prove it by hand for the first pair / 最初の1組を手計算で確かめる
if len(nicknames) >= 2:
    a, b = student_vectors[0], student_vectors[1]
    dot = float(np.dot(a, b))
    len_a = float(np.linalg.norm(a))
    len_b = float(np.linalg.norm(b))
    by_hand = dot / (len_a * len_b)
    by_lib = float(sim_df.iloc[0, 1])
    print(f"{nicknames[0]} x {nicknames[1]}")
    print(f"  dot (a . b)      = {dot:.4f}")
    print(f"  |a|, |b|         = {len_a:.4f}, {len_b:.4f}")
    print(f"  by hand          = {by_hand:.6f}")
    print(f"  by scikit-learn  = {by_lib:.6f}")
    print("  match? / 一致?    =", "YES" if np.isclose(by_hand, by_lib) else "NO")'''))

# ---------------------------------------------------------------- radar quiz
cells.append(md('''## 4. Radar profile / レーダープロフィール

Pick a classmate and see their answers as a shape. Two people with a similar shape will have a high cosine similarity. / クラスメイトを選ぶと、その人の答えが「形」になります。形が似ている2人は類似度が高い。'''))

cells.append(code('''# @title Launch the radar / レーダーを起動
def launch_personality_quiz():
    selector = widgets.Dropdown(options=list(nicknames), description="Person", layout=widgets.Layout(width="320px"))
    show_btn = widgets.Button(description="Show radar / 表示", button_style="success", layout=widgets.Layout(width="200px", height="40px"))
    out = widgets.Output()

    def show_radar(_=None):
        with out:
            clear_output()
            name = selector.value
            row = data[data[nickname_col].astype(str) == str(name)]
            if row.empty:
                print("Not found / 見つかりません:", name)
                return
            values = row[question_cols].astype(float).values.flatten().tolist()
            labels = [str(c)[:14] for c in question_cols]
            angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
            angles += angles[:1]
            plot_vals = values + [values[0]]
            fig, ax = plt.subplots(figsize=(8, 7), subplot_kw=dict(polar=True))
            ax.plot(angles, plot_vals, color="#7C3AED", linewidth=2)
            ax.fill(angles, plot_vals, alpha=0.25, color="#7C3AED")
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels, fontsize=9)
            ax.set_ylim(0, 5)
            ax.set_title(f"{name} — personality profile / 性格プロフィール", fontsize=15, pad=20)
            plt.tight_layout()
            plt.show()
            hi = int(np.argmax(values))
            lo = int(np.argmin(values))
            display(HTML(
                f"<div style='background:#f3f0ff;padding:16px;border-radius:10px;margin-top:8px;'>"
                f"<b>Average / 平均:</b> {np.mean(values):.2f} / 5.0 &nbsp;&nbsp;"
                f"<b>Highest / 最高:</b> {question_cols[hi]} ({values[hi]:.0f}) &nbsp;&nbsp;"
                f"<b>Lowest / 最低:</b> {question_cols[lo]} ({values[lo]:.0f})</div>"))

    show_btn.on_click(show_radar)
    display(widgets.HTML("<p>Pick a person, then press the button. / 人を選んでボタンを押そう。</p>"))
    display(selector, show_btn, out)

launch_personality_quiz()'''))

# ---------------------------------------------------------------- compatibility
cells.append(md('''## 5. Compatibility checker / 相性チェッカー

Pick two people. The score is their cosine similarity, colour-coded. Check at least three pairs and predict each score first. / 2人を選ぶと、コサイン類似度が色付きで出ます。3組以上、先に予想してから試そう。

| Score / スコア | Colour | Meaning / 意味 |
|---|---|---|
| ≥ 0.90 | green / 緑 | very alike / とても似ている |
| ≥ 0.70 | blue / 青 | alike / 似ている |
| ≥ 0.50 | orange / 橙 | so-so / まあまあ |
| < 0.50 | red / 赤 | quite different / かなり違う |'''))

cells.append(code('''# @title Launch the checker / チェッカーを起動
def launch_compatibility_checker():
    p1 = widgets.Dropdown(options=list(nicknames), description="Person 1", layout=widgets.Layout(width="240px"))
    p2 = widgets.Dropdown(options=list(nicknames), description="Person 2", layout=widgets.Layout(width="240px"))
    btn = widgets.Button(description="Check / 相性をみる", button_style="primary", layout=widgets.Layout(width="200px", height="40px"))
    out = widgets.Output()
    hist_out = widgets.Output()
    history = []

    def check(_=None):
        with out:
            clear_output()
            n1, n2 = p1.value, p2.value
            if n1 == n2:
                display(HTML("<p style='color:#ef4444;'>Pick two different people. / 別々の人を選んでね。</p>"))
                return
            score = float(sim_df.loc[n1, n2])
            if score >= 0.90:
                color, msg = "#10b981", "very alike / とても似ている"
            elif score >= 0.70:
                color, msg = "#3b82f6", "alike / 似ている"
            elif score >= 0.50:
                color, msg = "#f59e0b", "so-so / まあまあ"
            else:
                color, msg = "#ef4444", "quite different / かなり違う"
            display(HTML(
                f"<div style='background:{color};padding:22px;border-radius:12px;color:white;text-align:center;'>"
                f"<h3 style='margin:0;'>{n1} x {n2}</h3>"
                f"<p style='font-size:34px;margin:8px 0;'>{score:.3f}</p>"
                f"<p style='font-size:18px;margin:0;'>{msg}</p></div>"
                f"<div style='background:#f8fafc;padding:14px;border-radius:10px;margin-top:8px;'>"
                f"A big difference is not bad — it is a chance to <b>complement</b> each other. / "
                f"違いが大きいのは悪いことではなく、<b>補い合える</b>チャンス。</div>"))
            history.append((n1, n2, score))
        with hist_out:
            clear_output()
            if history:
                items = "".join(f"<li>{x} x {y}: {s:.3f}</li>" for x, y, s in history[-5:])
                display(HTML(f"<h4>Recent checks / 最近の記録</h4><ul>{items}</ul>"))

    btn.on_click(check)
    display(widgets.HTML("<p>Pick two people and check. / 2人選んでチェック。</p>"))
    display(widgets.HBox([p1, p2]), btn, out, hist_out)

launch_compatibility_checker()'''))

# ---------------------------------------------------------------- dashboard
cells.append(md('''## 6. Whole-class dashboard / クラス全体ダッシュボード

The heatmap shows every pair at once (darker = more alike). "Find similar people" ranks the top-5 for whoever you choose. / ヒートマップは全ペアを一度に表示(濃いほど似ている)。「似ている人を探す」で、選んだ人のトップ5が出ます。'''))

cells.append(code('''# @title Launch the dashboard / ダッシュボードを起動
def launch_visualization_dashboard():
    base = widgets.Dropdown(options=list(nicknames), description="Person", layout=widgets.Layout(width="280px"))
    heat_btn = widgets.Button(description="Heatmap / ヒートマップ", button_style="info", layout=widgets.Layout(width="200px", height="40px"))
    top_btn = widgets.Button(description="Find similar / 似ている人", button_style="success", layout=widgets.Layout(width="200px", height="40px"))
    out = widgets.Output()

    def show_heatmap(_):
        with out:
            clear_output()
            size = max(8, min(16, len(nicknames) * 0.6))
            plt.figure(figsize=(size, size * 0.85))
            annot = len(nicknames) <= 16
            sns.heatmap(sim_df, cmap="YlOrRd", vmin=0, vmax=1, annot=annot, fmt=".2f", annot_kws={"size": 8})
            plt.title("Cosine similarity heatmap / コサイン類似度ヒートマップ", fontsize=14)
            plt.tight_layout()
            plt.show()

    def show_top(_):
        with out:
            clear_output()
            b = base.value
            ranked = sim_df.loc[b].drop(b).sort_values(ascending=False).head(5)
            rows = "".join(
                f"<tr><td style='padding:8px;'>{i}</td><td style='padding:8px;'>{n}</td>"
                f"<td style='padding:8px;'><b>{s:.3f}</b></td></tr>"
                for i, (n, s) in enumerate(ranked.items(), 1))
            display(HTML(
                f"<div style='background:#eef2ff;padding:18px;border-radius:12px;'>"
                f"<h3 style='margin-top:0;'>Most similar to {b} / {b} と似ている人</h3>"
                f"<table style='width:100%;border-collapse:collapse;'>"
                f"<thead style='background:#c7d2fe;'><tr><th style='padding:8px;text-align:left;'>#</th>"
                f"<th style='padding:8px;text-align:left;'>Name / 名前</th>"
                f"<th style='padding:8px;text-align:left;'>Score</th></tr></thead>"
                f"<tbody>{rows}</tbody></table></div>"))

    heat_btn.on_click(show_heatmap)
    top_btn.on_click(show_top)
    display(widgets.HTML("<p>See the whole class, or find one person's closest matches. / 全体を見る、または1人の近い相手を探す。</p>"))
    display(base, widgets.HBox([heat_btn, top_btn]), out)

launch_visualization_dashboard()'''))

# ---------------------------------------------------------------- kmeans
cells.append(md('''## 7. K-means suggests teams / K-means がチームを提案

Nobody labels anyone. K-means drops a few centers, pulls each person to the nearest one, moves the centers, and repeats until they settle — then PCA flattens the answers to 2D so we can see the islands. Change `n_teams` and re-run. / 誰もラベルを付けません。K-means が中心を置き、近い人を集め、中心を動かし、落ち着くまで繰り返す。PCA で2次元にして島を見ます。`n_teams` を変えて再実行しよう。'''))

cells.append(code('''# @title Cluster + 2D map / クラスタリングと2次元マップ
n_teams = 4  # @param {type:"slider", min:2, max:6, step:1}

km = KMeans(n_clusters=n_teams, random_state=42, n_init=10)
labels = km.fit_predict(student_vectors)
coords = PCA(n_components=2).fit_transform(student_vectors)

plt.figure(figsize=(11, 8))
palette = plt.cm.Set2(np.linspace(0, 1, n_teams))
for t in range(n_teams):
    m = labels == t
    plt.scatter(coords[m, 0], coords[m, 1], color=[palette[t]], s=120, alpha=0.75, label=f"Team {t + 1}")
    for x, y, name in zip(coords[m, 0], coords[m, 1], nicknames[m]):
        plt.annotate(str(name), (x, y), xytext=(5, 5), textcoords="offset points", fontsize=9)
plt.xlabel("PCA axis 1 / 第1主成分")
plt.ylabel("PCA axis 2 / 第2主成分")
plt.title("Suggested teams (K-means, shown in 2D) / 提案されたチーム", fontsize=14)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()'''))

cells.append(md('''## 8. How many teams? The elbow / チームは何個? エルボー

Run K-means for k = 1..6 and plot how tightly people sit inside their team. The spread always shrinks, but where the line suddenly bends — the elbow — is the honest number of teams. / k=1〜6 で回し、まとまり具合をグラフに。急に曲がる「ひじ」が、ちょうどいいチーム数。'''))

cells.append(code('''# @title Elbow plot / エルボーのグラフ
ks = range(1, min(7, len(nicknames)))
inertias = [KMeans(n_clusters=k, random_state=42, n_init=10).fit(student_vectors).inertia_ for k in ks]
plt.figure(figsize=(8, 5))
plt.plot(list(ks), inertias, "o-", color="#7C3AED", linewidth=2)
plt.xlabel("number of teams (k) / チーム数")
plt.ylabel("spread inside teams / チーム内のばらつき")
plt.title("Elbow method / エルボー法")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
print("Look for the bend. / 折れ曲がる点を探そう。")'''))

# ---------------------------------------------------------------- team balance
cells.append(md('''## 9. Score each team's balance / チームのバランスを採点

For each suggested team we compute two scores: **diversity** (1 − average similarity inside the team; higher = more varied views) and **harmony** (the lowest similarity in the team; higher = nobody clashes hard). A good team is not just "all alike". / 各チームに2つのスコア: **多様性**(チーム内平均類似度を1から引いた値。高いほど多彩)と **協調性**(チーム内の最小類似度。高いほど相性の悪いペアがいない)。良いチーム=似た人だけ、ではない。'''))

cells.append(code('''# @title Diversity + harmony per team / 多様性と協調性
def team_scores(idx):
    if len(idx) < 2:
        return float("nan"), float("nan")
    pairs = [sim[i, j] for i, j in combinations(idx, 2)]
    return 1 - float(np.mean(pairs)), float(np.min(pairs))

for t in range(n_teams):
    idx = np.where(labels == t)[0]
    members = ", ".join(map(str, nicknames[idx]))
    div, harm = team_scores(idx)
    print(f"Team {t + 1} ({len(idx)}): {members}")
    if not np.isnan(div):
        print(f"   diversity / 多様性 = {div:.3f}   harmony / 協調性 = {harm:.3f}")
    print()'''))

# ---------------------------------------------------------------- reflect
cells.append(md('''## 10. Break the seal / 封を開ける

Unfold your morning sticky note. Did the math put your guessed twin in your cluster, or near you on the heatmap? Tally the whole class: how often did **gut** match **math**? / 朝の付箋を開こう。予想した双子は、同じチーム/ヒートマップで近かった? クラスで集計: **直感**と**数学**が一致した回数は?

**Remember / 忘れずに**
- A cluster is **not** a verdict on you. It reflects a handful of answers on one afternoon. / クラスタは君への判定ではない。今日の少しの答えを映すだけ。
- Being an outlier means you bring a rare angle — that is individuality, not an error. / 外れ値は珍しい視点を持つ証。エラーではなく個性。
- Teams here are a **hint** for later, not a final decision. / ここでのチームは後のための**ヒント**で、確定ではない。'''))

write_nb("personality_match_colab.ipynb", cells, "Personality Match Lab")
