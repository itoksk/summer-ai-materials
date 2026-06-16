#!/usr/bin/env python3
"""Generate ENGLISH-ONLY versions of the Day 3 data-science Colab notebooks:
titanic_colab_en, survivor_machine_colab_en, personality_match_colab_en.

These mirror the bilingual notebooks (build_notebooks.py /
build_personality_notebook.py) but with English-only prose for English-medium
students. Run:

    python3 materials/scripts/build_en_notebooks.py
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
    with open(os.path.join(OUT, filename), "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print("wrote", filename)


# ============================================================ Titanic (EN)
cells = []
cells.append(md('''# Machine Learning with the Titanic dataset

Use the most famous dataset on Kaggle — the 1912 Titanic passenger list — to try **predicting the future from past data**.

- Every row was a real person. Keep that in mind.
- Goal today: look at the data yourself, predict which features matter, then train a model and check your intuition.'''))

cells.append(md('''## Step 1 — Load the data'''))
cells.append(code('''import pandas as pd

url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
try:
    df = pd.read_csv(url)
except Exception:
    print("If the download fails, ask your teacher for titanic.csv and upload it to the folder on the left.")
    df = pd.read_csv("titanic.csv")
print(df.shape)
df.head()'''))

cells.append(md('''## Step 2 — Look at the data yourself first

Before letting a machine predict anything, look with your own eyes. Which columns seem to separate who survived?

- `Survived`: 1 = lived, 0 = died | `Pclass`: ticket class (1 = rich ... 3 = poor) | `Sex` | `Age` | `Fare`'''))
cells.append(code('''print("overall survival rate:", round(df["Survived"].mean(), 3))
print("\\nby Sex")
print(df.groupby("Sex")["Survived"].mean().round(3))
print("\\nby Pclass")
print(df.groupby("Pclass")["Survived"].mean().round(3))

# bin Age into child / teen / adult
df["AgeGroup"] = pd.cut(df["Age"], [0, 12, 18, 200], labels=["child(0-12)", "teen(13-18)", "adult(19+)"])
print("\\nby Age group")
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
cells.append(md('''**Observe**: Which gap is biggest? You can read 1912 behaviour ("women and children to the lifeboats first") straight out of the numbers.'''))

cells.append(md('''## Step 3 — Predict BEFORE you train

Before the machine answers, write down **your own** prediction. This is the most important part of the lesson.

1. Which feature separates survivors best? Rank **Sex / Pclass / Age / Fare** from most to least important.
2. Why? Write one line.

Write your ranking down NOW. In a moment the tree will reveal which feature it actually relied on most — then you can check whether your intuition matched the data. **No peeking at Step 4 first!**'''))

cells.append(md('''## Step 4 — Train a decision tree

A **decision tree** reaches an answer by asking a chain of yes/no questions (like 20 Questions).'''))
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
print("train accuracy:", round(tree.score(X_train, y_train), 3))
print("test accuracy: ", round(tree.score(X_test, y_test), 3))'''))
cells.append(code('''plt.figure(figsize=(14, 7))
plot_tree(tree, feature_names=["Pclass", "Sex(female=1)", "Age", "Fare"],
          class_names=["died", "survived"], filled=True, fontsize=9)
plt.show()

print("feature importance - did it match YOUR ranking from Step 3?")
for name, imp in sorted(zip(X.columns, tree.feature_importances_), key=lambda t: -t[1]):
    print(f"  {name:6} {round(imp, 3)}")'''))
cells.append(md('''**Read the tree**: What is the top question? That is the feature the model judged to split survival best. **Did it match the ranking you wrote in Step 3?**'''))

cells.append(md('''## Step 5 — Experiment: what if the tree is too deep? (overfitting)

Change `max_depth` and watch the train vs test accuracy.'''))
cells.append(code('''for depth in [1, 2, 3, 5, 10, None]:
    t = DecisionTreeClassifier(max_depth=depth, random_state=42).fit(X_train, y_train)
    print(f"max_depth={str(depth):>4} | train {t.score(X_train, y_train):.3f} | test {t.score(X_test, y_test):.3f}")'''))
cells.append(md('''**Questions**
- As the tree gets deeper, what happens to train accuracy? To test accuracy?
- When train rises but test falls, that is **overfitting** (memorising instead of learning).

## Reflection
- Where did you "see" human behaviour in the data?
- If this model were used for real decisions, what could go wrong? (connects to the bias page)
- **Kaggle** (13+) lets you try the same challenge as people worldwide: kaggle.com/c/titanic'''))
write_nb("titanic_colab_en.ipynb", cells, "Titanic ML - English (Summer AI)")


# ============================================================ Heatstroke (EN, regression)
HEAT_CSV = "https://raw.githubusercontent.com/itoksk/summer-ai-materials/main/materials/data/heatstroke.csv"
cells = []
cells.append(md('''# Predict heat-illness from the heat

**Day 3 — a regression lab.** Titanic was a **yes/no** question (survived or not) — that is *classification*. This time we predict an actual **number** — that is *regression*.

**What we predict**: how many people are taken to hospital by ambulance for **heat illness** on a given day, in a given prefecture of Japan.

**Where the data comes from** (nothing is invented):
- Transports (the target) = **Japan's Fire and Disaster Management Agency (FDMA / 総務省消防庁)**, official daily × prefecture records.
- Temperature & humidity = **Open-Meteo historical archive** (ERA5 reanalysis).
- 2018–2024 summers (May–Sep), 7 climate-diverse prefectures (Hokkaido, Tokyo, Aichi, Osaka, **Hyogo = Kobe, where this course is held**, Fukuoka, Okinawa).'''))

cells.append(md('''## Step 1 — Load the data'''))
cells.append(code('''import pandas as pd

url = "%s"
df = pd.read_csv(url)
print(df.shape)
df.head()''' % HEAT_CSV))

cells.append(md('''## Step 2 — Look first

Before any model, look at the link between heat and transports with your own eyes.

- `tmax_c`: daily max temperature | `transported`: people transported (the target) | `pref_en`: prefecture | `severe`: severe + fatal cases'''))
cells.append(code('''# mean transports per 3°C temperature bin
df["tmax_bin"] = (df["tmax_c"] // 3 * 3).astype(int)
print(df.groupby("tmax_bin")["transported"].mean().round(1))'''))
cells.append(code('''import matplotlib.pyplot as plt

plt.figure(figsize=(8, 5))
plt.scatter(df["tmax_c"], df["transported"], s=6, alpha=0.15)
plt.xlabel("daily max temperature (°C)")
plt.ylabel("people transported (per prefecture/day)")
plt.title("Heat vs heat-illness transports")
plt.show()'''))
cells.append(md('''**Observe**: Straight line, or does it **bend upward** past ~30°C? That non-linear jump is the key to today.'''))

cells.append(md('''## Step 3 — Predict BEFORE you train

Write your own guess first:

1. On a day when the max temperature hits **35°C**, how many people do you think one prefecture sends to hospital? Write a number.
2. Besides temperature, what else might drive the count (prefecture / month / humidity ...)? Name one.

No peeking — the model reveals the real answer in a moment.'''))

cells.append(md('''## Step 4 — Train on the past, predict an unseen summer

To prevent cheating, split **by year**: train on 2018–2023, then predict **2024 (a summer the model has never seen)**. That is what "predict on the test set" means.'''))
cells.append(code('''from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

train = df[df["year"] < 2024]
test  = df[df["year"] == 2024]
print("train rows:", len(train), " / test rows (2024):", len(test))

# simplest possible model: a straight line from tmax only
lin = LinearRegression().fit(train[["tmax_c"]], train["transported"])
pred = lin.predict(test[["tmax_c"]])
print("linear MAE:", round(mean_absolute_error(test["transported"], pred), 2), "people")
at35 = pd.DataFrame({"tmax_c": [35]})
print("prediction at 35°C:", round(float(lin.predict(at35)[0]), 1), "people  <- compare with your Step 3 guess")'''))
cells.append(md('''**Question**: Did the straight line capture the surge on the hottest days (35°C+)? It probably **under-predicts** them, because the real relationship bends but a line cannot.'''))

cells.append(md('''## Step 5 — A better model with more clues

A **random forest** (many decision trees voting) handles the bend. Give it not only temperature but also **prefecture, month, humidity**.'''))
cells.append(code('''from sklearn.ensemble import RandomForestRegressor

feat = ["tmax_c", "tmean_c", "humidity_pct", "month"]
Xtr = pd.get_dummies(train[feat + ["pref_en"]], columns=["pref_en"])
Xte = pd.get_dummies(test[feat + ["pref_en"]], columns=["pref_en"]).reindex(columns=Xtr.columns, fill_value=0)

rf = RandomForestRegressor(n_estimators=200, random_state=42).fit(Xtr, train["transported"])
pred_rf = rf.predict(Xte)
print("RandomForest MAE:", round(mean_absolute_error(test["transported"], pred_rf), 2), "people")
print("(smaller than the linear MAE? = it predicts better)")'''))

cells.append(md('''## Step 6 — Answer-check on a real day

Take the **hottest Tokyo day of 2024**, let the model predict it, and compare with what **actually** happened.'''))
cells.append(code('''test = test.copy()
test["pred"] = pred_rf.round(0)

tokyo = test[test["pref_en"] == "Tokyo"].sort_values("tmax_c", ascending=False)
print(tokyo[["date", "tmax_c", "transported", "pred"]].head(5).to_string(index=False))
print("\\nHow close was the prediction to reality? By how much was it off?")'''))
cells.append(code('''# which clues mattered most?
imp = sorted(zip(Xtr.columns, rf.feature_importances_), key=lambda t: -t[1])
print("feature importance (top 8):")
for name, v in imp[:8]:
    print(f"  {name:18} {round(v, 3)}")
print("\\nDid the factor you guessed in Step 3 show up?")'''))

cells.append(md('''## Step 7 — The threshold and the alert

Transports explode above ~30°C. That is why Japan issues a **Heat-Illness Alert** (環境省 / JMA) when the **WBGT heat index** crosses a set line. The "elbow" the model found is essentially the same line the country uses to protect people.'''))

cells.append(md('''## Reflection & limits

- The model uses each prefecture **capital city's** temperature as a stand-in for the whole (large) prefecture. Same warning as Titanic: **a model only knows what you measured.**
- Bigger-population prefectures have more transports (Tokyo ≫ Okinawa). To compare fairly, you would normalise **per 100,000 residents**.
- Summers keep getting hotter (climate change). On a future hotter than anything in the training data, will the model's predictions still hold?
- **Challenge**: (1) normalise per capita to compare prefectures fairly (2) add your own prefecture (FDMA has all 47) (3) reshape it into a **classification** task — "should an alert be issued tomorrow, yes/no?"

**Sources**
- FDMA "Heatstroke emergency transport status" https://www.fdma.go.jp/disaster/heatstroke/
- Open-Meteo Historical Weather API (ERA5) https://open-meteo.com/
- Ministry of the Environment heat-index (WBGT) site https://www.wbgt.env.go.jp/'''))
write_nb("heatstroke_colab_en.ipynb", cells, "Heatstroke Prediction - English (Summer AI)")


# ============================================ Survivor Machine (EN)
cells = []
cells.append(md('''# Survivor Machine — is the website's tree real?

On the site you set sex, ticket class and age, and a tree gave you a survival percentage. **Is that number invented, or is it a real calculation?** Let's check it against the actual 1912 data.'''))

cells.append(md('''## Step 1 — Load the real data'''))
cells.append(code('''import pandas as pd

url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
try:
    df = pd.read_csv(url)
except Exception:
    print("If the download fails, ask your teacher for titanic.csv and upload it to the folder on the left.")
    df = pd.read_csv("titanic.csv")
print("passengers:", len(df), " overall survival rate:", round(df["Survived"].mean(), 3))
df.head()'''))

cells.append(md('''## Step 2 — Website numbers vs real data

The website widget has these probabilities baked into its tree. Do they actually match the data? Each one should be the survival RATE of the real passengers in that group (survived / total).'''))
cells.append(code('''g = df.dropna(subset=["Age"]).copy()

def rate(mask):
    sub = g[mask]
    return (len(sub), round(sub["Survived"].mean(), 2)) if len(sub) else (0, None)

print("                    website   real data (count, rate)")
print("female 1st          0.97     ", rate((g.Sex=="female") & (g.Pclass==1)))
print("female 2nd          0.92     ", rate((g.Sex=="female") & (g.Pclass==2)))
print("female 3rd          0.50     ", rate((g.Sex=="female") & (g.Pclass==3)))
print("boy (<=6) 1-2nd     0.83     ", rate((g.Sex=="male") & (g.Age<=6) & (g.Pclass<=2)))
print("boy (<=6) 3rd       0.36     ", rate((g.Sex=="male") & (g.Age<=6) & (g.Pclass==3)))
print("man (>6) 1st        0.36     ", rate((g.Sex=="male") & (g.Age>6) & (g.Pclass==1)))
print("man (>6) 2-3rd      0.13     ", rate((g.Sex=="male") & (g.Age>6) & (g.Pclass>=2)))'''))
cells.append(md('''**Observe**: The website numbers are not made up — they are the real proportions from 110-year-old data. So your own verdict on the site was real too: it was the survival rate of passengers who matched your three answers.'''))

cells.append(md('''## Step 3 — The real tree + feature importance'''))
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

print("feature importance:")
for name, imp in zip(X.columns, clf.feature_importances_):
    print(" ", name, round(imp, 3))'''))
cells.append(md('''**Connect**: The biggest importance is **Sex** — that is why the widget's "cheapest change to flip your fate" was usually changing sex. The tree decided that from data alone, with nobody telling it.'''))

cells.append(md('''## Step 4 — What the model never measured

On the site, toggling "Brave / Can swim / Lucky" never moved the verdict. Here is why — **there is no such column**. The model only knows what is in the columns.'''))
cells.append(code('''print("columns the model could ever see:")
print(list(df.columns))
print()
print("There is no column for 'courage', 'kindness', or 'never gives up'.")'''))
cells.append(md('''## Questions
- How closely did the website numbers match the real data? Where they differ, why?
- Why is Sex the most important feature — is that a truth about the world, or a truth about who reached the 1912 lifeboats?
- What human things does the model miss entirely?'''))
write_nb("survivor_machine_colab_en.ipynb", cells, "Survivor Machine - English (Summer AI)")


# ============================================ Personality Match (EN)
cells = []
cells.append(md('''# Matching Lab — Let the Math Find Your Twin

Your class survey becomes **data**. Each person is a row of 1-5 answers (a vector), and we measure how alike any two people are with **cosine similarity** — the same math from this morning.

**What you will do**
1. Upload your class CSV
2. Check one similarity by hand
3. Radar profile of one person
4. Compatibility checker (colour-coded)
5. Heatmap + "most similar" top-5
6. K-means suggests teams
7. Score each team's balance

> Run the cells one at a time, in order. Before each one, PREDICT what will appear. No API keys, no GPU.'''))

cells.append(md('''## 1. Setup'''))
cells.append(code('''!pip install -q seaborn scikit-learn ipywidgets

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
print("Ready")'''))

cells.append(md('''## 2. Upload your class CSV

Export your Google Form responses (Responses tab -> three-dot menu -> Download responses (.csv)) and upload here. Columns are auto-detected, so any number of questions works. Your form just needs a short-answer **Nickname** question plus the 1-5 questions.'''))
cells.append(code('''from google.colab import files

print("Choose your class_survey.csv ...")
uploaded = files.upload()

csv_files = [f for f in uploaded.keys() if f.endswith(".csv")]
if not csv_files:
    raise SystemExit("No .csv found - run this cell again.")

data = pd.read_csv(csv_files[0])

def looks_like_timestamp(name):
    n = str(name).lower()
    return ("time" in n) or ("date" in n)

def looks_like_nickname(name):
    n = str(name).lower()
    return any(k in n for k in ["nick", "name", "handle"])

cols = [c for c in data.columns if not looks_like_timestamp(c)]
name_cols = [c for c in cols if looks_like_nickname(c)]
if name_cols:
    nickname_col = name_cols[0]
else:
    nickname_col = cols[0]
    print("NOTE: no 'Nickname' question found - using:", nickname_col)
    print("Add a short-answer 'Nickname' question to your form for clean labels.")

question_cols = [c for c in cols
                 if c != nickname_col and pd.to_numeric(data[c], errors="coerce").notna().all()]

nicknames = data[nickname_col].astype(str).values
student_vectors = data[question_cols].astype(float).values

print(f"People: {len(nicknames)}")
print(f"Questions: {len(question_cols)}")
print(f"Name column: {nickname_col}")
display(data[[nickname_col] + list(question_cols[:4])].head())'''))

cells.append(md('''## 3. Cosine similarity — and a by-hand check

Build an N x N table of how alike every pair is, then re-compute ONE pair by hand to prove the library uses the morning's exact formula.'''))
cells.append(code('''sim = cosine_similarity(student_vectors)
sim_df = pd.DataFrame(sim, index=nicknames, columns=nicknames)
display(sim_df.iloc[:5, :5].round(3))'''))
cells.append(code('''if len(nicknames) >= 2:
    a, b = student_vectors[0], student_vectors[1]
    dot = float(np.dot(a, b))
    len_a, len_b = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    by_hand = dot / (len_a * len_b)
    by_lib = float(sim_df.iloc[0, 1])
    print(f"{nicknames[0]} x {nicknames[1]}")
    print(f"  dot (a . b)     = {dot:.4f}")
    print(f"  |a|, |b|        = {len_a:.4f}, {len_b:.4f}")
    print(f"  by hand         = {by_hand:.6f}")
    print(f"  by scikit-learn = {by_lib:.6f}")
    print("  match? =", "YES" if np.isclose(by_hand, by_lib) else "NO")'''))

cells.append(md('''## 4. Radar profile

Pick a classmate and see their answers as a shape. Two people with a similar shape have a high cosine similarity.'''))
cells.append(code('''def launch_personality_quiz():
    selector = widgets.Dropdown(options=list(nicknames), description="Person", layout=widgets.Layout(width="320px"))
    show_btn = widgets.Button(description="Show radar", button_style="success", layout=widgets.Layout(width="180px", height="40px"))
    out = widgets.Output()

    def show_radar(_=None):
        with out:
            clear_output()
            name = selector.value
            row = data[data[nickname_col].astype(str) == str(name)]
            if row.empty:
                print("Not found:", name)
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
            ax.set_title(f"{name} - personality profile", fontsize=15, pad=20)
            plt.tight_layout()
            plt.show()
            hi, lo = int(np.argmax(values)), int(np.argmin(values))
            display(HTML(
                f"<div style='background:#f3f0ff;padding:16px;border-radius:10px;'>"
                f"<b>Average:</b> {np.mean(values):.2f}/5.0 &nbsp; "
                f"<b>Highest:</b> {question_cols[hi]} ({values[hi]:.0f}) &nbsp; "
                f"<b>Lowest:</b> {question_cols[lo]} ({values[lo]:.0f})</div>"))

    show_btn.on_click(show_radar)
    display(widgets.HTML("<p>Pick a person, then press the button.</p>"))
    display(selector, show_btn, out)

launch_personality_quiz()'''))

cells.append(md('''## 5. Compatibility checker

Pick two people. The score is their cosine similarity, colour-coded: green >= 0.90 (very alike), blue >= 0.70 (alike), orange >= 0.50 (so-so), red < 0.50 (quite different). Check at least three pairs, predicting each first.'''))
cells.append(code('''def launch_compatibility_checker():
    p1 = widgets.Dropdown(options=list(nicknames), description="Person 1", layout=widgets.Layout(width="240px"))
    p2 = widgets.Dropdown(options=list(nicknames), description="Person 2", layout=widgets.Layout(width="240px"))
    btn = widgets.Button(description="Check", button_style="primary", layout=widgets.Layout(width="160px", height="40px"))
    out = widgets.Output()

    def check(_=None):
        with out:
            clear_output()
            n1, n2 = p1.value, p2.value
            if n1 == n2:
                display(HTML("<p style='color:#ef4444;'>Pick two different people.</p>"))
                return
            score = float(sim_df.loc[n1, n2])
            if score >= 0.90:
                color, msg = "#10b981", "very alike"
            elif score >= 0.70:
                color, msg = "#3b82f6", "alike"
            elif score >= 0.50:
                color, msg = "#f59e0b", "so-so"
            else:
                color, msg = "#ef4444", "quite different"
            display(HTML(
                f"<div style='background:{color};padding:22px;border-radius:12px;color:white;text-align:center;'>"
                f"<h3 style='margin:0;'>{n1} x {n2}</h3>"
                f"<p style='font-size:34px;margin:8px 0;'>{score:.3f}</p>"
                f"<p style='font-size:18px;margin:0;'>{msg}</p></div>"
                f"<div style='background:#f8fafc;padding:12px;border-radius:10px;margin-top:8px;'>"
                f"A big difference is not bad - it is a chance to complement each other.</div>"))

    btn.on_click(check)
    display(widgets.HTML("<p>Pick two people and check.</p>"))
    display(widgets.HBox([p1, p2]), btn, out)

launch_compatibility_checker()'''))

cells.append(md('''## 6. Whole-class dashboard

The heatmap shows every pair at once (darker = more alike). "Find similar" ranks the top-5 for whoever you choose.'''))
cells.append(code('''def launch_visualization_dashboard():
    base = widgets.Dropdown(options=list(nicknames), description="Person", layout=widgets.Layout(width="260px"))
    heat_btn = widgets.Button(description="Heatmap", button_style="info", layout=widgets.Layout(width="160px", height="40px"))
    top_btn = widgets.Button(description="Find similar", button_style="success", layout=widgets.Layout(width="160px", height="40px"))
    out = widgets.Output()

    def show_heatmap(_):
        with out:
            clear_output()
            size = max(8, min(16, len(nicknames) * 0.6))
            plt.figure(figsize=(size, size * 0.85))
            sns.heatmap(sim_df, cmap="YlOrRd", vmin=0, vmax=1, annot=len(nicknames) <= 16, fmt=".2f", annot_kws={"size": 8})
            plt.title("Cosine similarity heatmap", fontsize=14)
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
                f"<h3 style='margin-top:0;'>Most similar to {b}</h3>"
                f"<table style='width:100%;border-collapse:collapse;'>"
                f"<thead style='background:#c7d2fe;'><tr><th style='padding:8px;text-align:left;'>#</th>"
                f"<th style='padding:8px;text-align:left;'>Name</th>"
                f"<th style='padding:8px;text-align:left;'>Score</th></tr></thead>"
                f"<tbody>{rows}</tbody></table></div>"))

    heat_btn.on_click(show_heatmap)
    top_btn.on_click(show_top)
    display(widgets.HTML("<p>See the whole class, or find one person's closest matches.</p>"))
    display(base, widgets.HBox([heat_btn, top_btn]), out)

launch_visualization_dashboard()'''))

cells.append(md('''## 7. K-means suggests teams

Nobody labels anyone. K-means drops a few centers, pulls each person to the nearest, moves the centers, and repeats until they settle. PCA flattens the answers to 2D so we can see the islands. Change `n_teams` and re-run.'''))
cells.append(code('''n_teams = 4  # @param {type:"slider", min:2, max:6, step:1}

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
plt.xlabel("PCA axis 1")
plt.ylabel("PCA axis 2")
plt.title("Suggested teams (K-means, shown in 2D)", fontsize=14)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()'''))

cells.append(md('''## 8. How many teams? The elbow

Run K-means for k = 1..6 and plot how tightly people sit inside their team. The spread always shrinks, but where the line suddenly bends — the elbow — is the honest number of teams.'''))
cells.append(code('''ks = range(1, min(7, len(nicknames)))
inertias = [KMeans(n_clusters=k, random_state=42, n_init=10).fit(student_vectors).inertia_ for k in ks]
plt.figure(figsize=(8, 5))
plt.plot(list(ks), inertias, "o-", color="#7C3AED", linewidth=2)
plt.xlabel("number of teams (k)")
plt.ylabel("spread inside teams")
plt.title("Elbow method")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
print("Look for the bend.")'''))

cells.append(md('''## 9. Score each team's balance

Two scores per team: **diversity** (1 - average similarity inside the team; higher = more varied views) and **harmony** (the lowest similarity in the team; higher = nobody clashes hard). A good team is not just "all alike".'''))
cells.append(code('''def team_scores(idx):
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
        print(f"   diversity = {div:.3f}   harmony = {harm:.3f}")
    print()'''))

cells.append(md('''## 10. Break the seal

Unfold your morning sticky note. Did the math put your guessed twin in your cluster, or near you on the heatmap? Tally the whole class: how often did **gut** match **math**?

- A cluster is **not** a verdict on you — it reflects a few answers on one afternoon.
- Being an outlier means you bring a rare angle: individuality, not an error.
- Teams here are a **hint** for later, not a final decision.'''))
write_nb("personality_match_colab_en.ipynb", cells, "Personality Match Lab - English (Summer AI)")

print("done")
