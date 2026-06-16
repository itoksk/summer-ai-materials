#!/usr/bin/env python3
"""Generate the Nano Banana (Gemini Image API) Colab notebook.

A Stable-Diffusion-style image studio that runs on the Gemini image API
instead of a local diffusion model -- so it needs NO GPU, just an API key.

Models (verified against ai.google.dev, 2026-06):
  - gemini-3.1-flash-image   = Nano Banana (flash; cheaper/faster)
  - gemini-3-pro-image-preview = Nano Banana Pro (up to 4K, "thinking")
"""
import json, os

OUT = "/Users/keisuke/git/summer-ai/materials/notebooks/nanobanana_colab.ipynb"


def md(s):
    return {"cell_type": "markdown", "metadata": {}, "source": s}


def code(s):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": s}


cells = [
    md('''# Nano Banana スタジオ — APIで動く Stable Diffusion 風お絵かき / Image Studio

Stable Diffusion のような「プロンプト → 画像」のお絵かきを、**GPUなし**で動かします。
裏側は Google の **Nano Banana(Gemini 画像API)**。モデルのダウンロードも、重い計算もなし。**APIキー1つ**だけで動きます。

**今日やること / Today**
1. プロンプトを打って画像を作る(SD と同じノリ)
2. つまみ(モデル・縦横比・解像度・枚数)をいじる
3. ボタン付きの「ミニWebUI」で連続生成
4. 参考画像を入れて **img2img / 写真の編集**(背景替え・色替え・合成)

**準備 / Setup**
- ランタイムは **CPUのままでOK**(GPU不要。APIが画像を作ります)
- 必要なのは **Gemini APIキー**。[Google AI Studio](https://aistudio.google.com/apikey) で無料で作れます
- 上から順に、セルを **1つずつ** 実行してください

> Nano Banana Pro は**有料API**です。生成のたびに少額の料金がかかります(特に Pro / 4K)。授業では安い **flash** を基本にしましょう。'''),

    md('''## つくる前のルール / Rules before you create

AIお絵かきには責任がついてきます。次の4つは守ること。

- **実在する人の顔・名前を使わない**(肖像権 / portrait right)
- **既存のキャラクターをそのまま作らない**(著作権 / copyright)
- **ディープフェイクを作らない。AIの作品を人間が描いたと偽らない**
- 共有するときは「**Nano Banana (Gemini) で生成**」とクレジットし、ライセンスを確認する

> 生成画像には Google の電子透かし **SynthID** が自動で埋め込まれます(AI生成だと後から判別できる仕組み)。'''),

    md('''## SD のつまみ vs Nano Banana のつまみ / Dials compared

Stable Diffusion で慣れた人へ。考え方が少し変わります。

| Stable Diffusion | Nano Banana (Gemini) |
|---|---|
| steps / CFG scale / seed | **なし**(自然文の指示でコントロール) |
| negative prompt(専用欄) | プロンプトに「**避けて / Avoid:** …」と書く |
| width / height(px) | **aspect ratio**(比率)+ **image size**(1K/2K/4K) |
| img2img / inpaint(マスク) | **参考画像 + ことばの指示**(マスク不要) |

ポイント: Nano Banana は「**考える**」モデル。タグの羅列より、**一文の指示**(誰が・どこで・どんな光で・どんな画風)がよく効きます。'''),

    md('''## Step 1 — ライブラリを入れる / Install'''),
    code('!pip -q install -U google-genai pillow ipywidgets'),

    md('''## Step 2 — APIキーを入れて接続 / Connect with your API key

おすすめは Colab の **シークレット機能**(左の鍵アイコン 🔑)。
`GEMINI_API_KEY` という名前でキーを保存しておくと、下のセルが自動で読み込みます。
保存していなければ、その場で入力できます(入力欄には表示されません)。'''),
    code('''import os, getpass
from google import genai

API_KEY = None
try:
    from google.colab import userdata          # Colab のシークレットから取得
    API_KEY = userdata.get("GEMINI_API_KEY")
except Exception:
    pass
if not API_KEY:
    API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    API_KEY = getpass.getpass("Gemini API key を貼り付けてEnter▶ (https://aistudio.google.com/apikey): ")

client = genai.Client(api_key=API_KEY)
print("接続OK / connected")'''),

    md('''## Step 3 — エンジンを読み込む / Load the engine

この1セルが心臓部です。`generate(...)` を呼ぶと画像が作られ、`generated_images/` に保存されます。
**中身は読まなくてもOK**。次のセルからすぐ使えます。'''),
    code('''# ===== Nano Banana engine =====
import io, time, pathlib
from PIL import Image
from IPython.display import display
from google.genai import types

OUTDIR = pathlib.Path("generated_images"); OUTDIR.mkdir(exist_ok=True)
_N = 0   # 連番(ファイル名の重複防止)

# モデル(2026年6月時点の最新世代。左がWebUIに出る表示名)
MODELS = {
    "Nano Banana (flash)": "gemini-3.1-flash-image",      # 速い・安い。普段はこれ
    "Nano Banana Pro":     "gemini-3-pro-image-preview",  # 高画質・4K・文字も得意。少し高い
}

def _resolve(model):
    if model in MODELS: return MODELS[model]
    return model                                          # 生のモデルIDもOK

def _images(resp):
    out = []
    parts = getattr(resp, "parts", None)
    if not parts and getattr(resp, "candidates", None):
        parts = resp.candidates[0].content.parts
    for p in (parts or []):
        data = getattr(getattr(p, "inline_data", None), "data", None)
        if data:
            out.append(Image.open(io.BytesIO(data)))
    return out

def _save(img):
    global _N; _N += 1
    path = OUTDIR / f"{time.strftime('%Y%m%d_%H%M%S')}_{_N:03d}.png"
    img.save(path)
    return path

def _config(aspect, resolution, rich=True):
    if rich:   # Gemini 3 画像モデルの正式なサイズ指定
        return types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(aspect_ratio=aspect, image_size=resolution),
        )
    return types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"])

def generate(prompt, avoid="", model="Nano Banana (flash)",
             aspect="1:1", resolution="2K", count=1, refs=None, show=True):
    # refs に画像(PIL もしくはパス)のリストを渡すと img2img / 編集になる
    mid = _resolve(model)
    text = prompt if not avoid else f"{prompt}\\n\\n避けて / Avoid: {avoid}"
    base = []
    for r in (refs or []):
        base.append(r if isinstance(r, Image.Image) else Image.open(r))
    base.append(text)

    results = []
    for i in range(count):
        try:
            resp = client.models.generate_content(model=mid, contents=base, config=_config(aspect, resolution))
        except Exception as e:
            # 古いSDK等で image_config 非対応のとき → 比率をことばで伝えてフォールバック
            hint = base[:-1] + [f"{text}\\n\\n(Aspect ratio: {aspect}, Resolution: {resolution})"]
            resp = client.models.generate_content(model=mid, contents=hint, config=_config(aspect, resolution, rich=False))
        imgs = _images(resp)
        if not imgs:
            print("画像が返りませんでした / no image. 理由:", getattr(resp, "text", None))
        for img in imgs:
            path = _save(img)
            results.append(img)
            if show:
                print(f"{path}  ({img.width}x{img.height})")
                display(img)
    return results

print("ready -> generate('a cozy ramen shop on a rainy night, neon signs, watercolor style')")'''),

    md('''## Step 4 — クイック生成(SD風フォーム)/ Quick form

右側のフォームに打ち込んで、このセルを実行(▶)するだけ。Stable Diffusion のフォームと同じ感覚です。'''),
    code('''#@title 画像を生成 / Generate  { display-mode: "form" }
prompt = "a cozy ramen shop on a rainy night, neon signs, watercolor style" #@param {type:"string"}
avoid  = "low quality, blurry, text, watermark" #@param {type:"string"}
model  = "Nano Banana (flash)" #@param ["Nano Banana (flash)", "Nano Banana Pro"]
aspect = "1:1" #@param ["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3", "21:9"]
resolution = "2K" #@param ["1K", "2K", "4K"]
count = 1 #@param {type:"slider", min:1, max:4, step:1}

generate(prompt, avoid, model, aspect, resolution, count)'''),

    md('''## Step 5 — ミニWebUI(ボタンで連続生成)/ Mini WebUI

つまみとボタンが並んだパネル。**Generate** を押すたびに画像が増えます。
打ち直して何度も押して、つまみの効き目を体で覚えましょう。'''),
    code('''import ipywidgets as W
from IPython.display import display, clear_output

w_prompt = W.Textarea(value="a stoic robot barista with glowing blue eyes brewing coffee, futuristic cafe on Mars, cinematic, 3D animation style",
                      description="Prompt", layout=W.Layout(width="99%", height="92px"),
                      style={"description_width": "90px"})
w_avoid  = W.Text(value="low quality, blurry, watermark", description="避ける/Avoid",
                  layout=W.Layout(width="99%"), style={"description_width": "90px"})
w_model  = W.Dropdown(options=list(MODELS.keys()), description="Model", style={"description_width": "90px"})
w_aspect = W.Dropdown(options=["1:1","16:9","9:16","4:3","3:4","3:2","2:3","21:9"], value="1:1",
                      description="比率/Aspect", style={"description_width": "90px"})
w_res    = W.Dropdown(options=["1K","2K","4K"], value="2K", description="解像度/Res", style={"description_width": "90px"})
w_count  = W.IntSlider(value=1, min=1, max=4, description="枚数/Count", style={"description_width": "90px"})
btn      = W.Button(description="Generate", button_style="primary", icon="image")
out      = W.Output()

def _go(_):
    with out:
        clear_output()
        print("生成中… / generating… (数秒〜数十秒)")
        generate(w_prompt.value, w_avoid.value, w_model.value, w_aspect.value, w_res.value, w_count.value)

btn.on_click(_go)
display(W.VBox([w_prompt, w_avoid,
               W.HBox([w_model, w_aspect]),
               W.HBox([w_res, w_count]),
               btn, out]))'''),

    md('''## Step 6 — img2img / 写真を編集する / Edit an image

Nano Banana の得意技。**参考画像 + ことばの指示**で、マスクなしに編集できます。
- 背景替え:「change the background to a sunset beach」
- 色替え:「make the car red」
- 合成・スタイル:「draw this person in a watercolor style」
- 復元・着色:「colorize this old black and white photo」

下のセルを実行して画像をアップロード → 指示を打って再実行。'''),
    code('''from google.colab import files
from PIL import Image

up = files.upload()                 # 編集したい画像を選ぶ(1枚以上)
ref_paths = list(up.keys())
print("uploaded:", ref_paths)

instruction = "change the background to a calm sunset beach, keep the subject exactly the same"  #@param {type:"string"}
edit_model  = "Nano Banana (flash)"  #@param ["Nano Banana (flash)", "Nano Banana Pro"]

refs = [Image.open(p) for p in ref_paths]
generate(instruction, model=edit_model, aspect="1:1", resolution="2K", refs=refs)'''),

    md('''## まとめてダウンロード / Download everything

作った画像は `generated_images/` に入っています。zip にして手元へ。'''),
    code('''import shutil
from google.colab import files
shutil.make_archive("nanobanana_images", "zip", "generated_images")
files.download("nanobanana_images.zip")'''),

    md('''## うまく作るコツ / Prompting tips

Nano Banana は「考える」モデル。**Creative Director になったつもり**で一文で指示すると化けます。

- **タグの羅列をやめる**: `dog, park, 4k, realistic` ✗ → `A golden retriever puppy running through a sunlit park at golden hour, shallow depth of field` ◯
- **入れる要素**: 被写体 / 構図(寄り・引き・ローアングル)/ 動き / 場所 / 画風 / 光
- **文字を入れる**: `place the headline "URBAN EXPLORER" at the top in bold white sans-serif` のように引用符で指定
- **作り直さず「編集」**: 80%できていたら新規生成せず「change the lighting to sunset」のように直す方が速い
- **文脈を渡す**: 「a sandwich **for a high-end gourmet cookbook**」のように用途を言うと、プロっぽい仕上がりを自分で推論してくれる

### お題チャレンジ / Try these
1. **同じプロンプトで flash と Pro を比較** — 何が違う?(細部・文字・質感)
2. **比率を変える** — 1:1 → 16:9 → 9:16 で構図はどう変わる?
3. **インフォグラフィック** — 「retro 1950s-style infographic about ramen, legible labels」で文字入り画像
4. **編集の連鎖** — 1枚作って、背景→色→画風と3回だけ「編集」で育てる

> 注意 / Limitations: 小さな文字や細部、スペルは完璧でないことがあります。図やインフォグラフィックの**事実は必ず自分で確認**を。'''),
]

nb = {
    "nbformat": 4,
    "nbformat_minor": 0,
    "metadata": {
        "colab": {"provenance": [], "name": "Nano Banana Studio (Summer AI)"},
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"},
    },
    "cells": cells,
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(nb, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("wrote", OUT)
