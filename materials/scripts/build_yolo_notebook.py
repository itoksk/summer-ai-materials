import json, os
OUT = "/Users/keisuke/git/summer-ai/materials/notebooks/yolo_world_colab.ipynb"
def md(s): return {"cell_type":"markdown","metadata":{},"source":s}
def code(s): return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":s}
cells = [
 md('''# YOLO World — ことばで何でも見つける物体検出 / Detect anything by describing it

YOLO World は **ゼロショット物体検出**。従来のYOLOは80個の決まったクラスしか検出できなかったが、YOLO Worldは**英語の言葉でクラスを指定するだけ**で、再学習なしに新しい物体を検出できる。

**準備**: メニュー「ランタイム → ランタイムのタイプを変更」で **T4 GPU** を選ぶと速い(無料枠でOK。CPUでも動く)。上から順にセルを実行。'''),
 md('''## Step 1 — ライブラリを入れる / Install'''),
 code('!pip -q install ultralytics'),
 md('''## Step 2 — モデルを読み込む / Load the YOLO World model'''),
 code('from ultralytics import YOLO\nmodel = YOLO("yolov8s-world.pt")  # downloads once\nprint("ready")'),
 md('''## Step 3 — 探したいものを「言葉」で指定 / Set classes in words

ここがYOLO Worldの肝。検出したいものを英語のリストで渡すだけ。学習は不要。'''),
 code('model.set_classes(["person", "red car", "sleeping cat", "laptop", "person wearing glasses"])'),
 md('''## Step 4 — 画像をアップロードして検出 / Upload an image and detect'''),
 code('''from google.colab import files
up = files.upload()                 # pick a photo (a street scene works well)
img_path = list(up.keys())[0]

results = model.predict(img_path, conf=0.3, save=True)   # conf = confidence threshold (0-1)
for r in results:
    for b in r.boxes:
        print(model.names[int(b.cls)], round(float(b.conf), 2))'''),
 md('''## Step 5 — 結果を表示 / Show the result'''),
 code('''import glob
from IPython.display import Image, display
out = sorted(glob.glob("runs/detect/predict*/*"))[-1]
display(Image(filename=out))'''),
 md('''## 実験 / Experiments

- **conf を変える**: 0.1〜0.9 で検出数と精度のバランスを見る
- **言葉を凝らす**: "person" → "red car" → "person with blue hat reading a book"。AIはどこまで理解できる?
- **苦手を探す**: 重なった物体、遠くの物体、鏡の中。どこで失敗する?

## 考えよう / Discuss
もし街中のカメラが全部YOLO Worldになったら? **安全 / プライバシー / 規制 / バランス** の4つの視点で話そう。「言葉で何でも探せる」力には責任がともなう。'''),
]
nb = {"nbformat":4,"nbformat_minor":0,"metadata":{"colab":{"provenance":[],"name":"YOLO World (Summer AI)"},"kernelspec":{"name":"python3","display_name":"Python 3"},"language_info":{"name":"python"}},"cells":cells}
json.dump(nb, open(OUT,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("wrote", OUT)
