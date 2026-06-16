# -*- coding: utf-8 -*-
"""
run_all_applications.py — Experimentos aplicativos de detección en UN SOLO script.
Compara 4 modalidades de entrada (VIS, IR, Anterior_TopHat, Optimo_Multiescala) en 3 modelos:
  YOLO (Ultralytics) · RF-DETR (Roboflow) · Keras (clasificación MobileNetV2)
Sin Roboflow ni anotación manual: las etiquetas se autogeneran (pseudo-etiquetas) con un YOLO
preentrenado (o HOG como respaldo offline). Las cajas valen para las 4 modalidades (imágenes
registradas). Cada modelo se salta solo si su librería no está instalada.

USO:
  python experiments/detection/run_all_applications.py --models yolo,rfdetr,keras --epochs 30 --device 0
  python experiments/detection/run_all_applications.py --models yolo --epochs 10 --device cpu
Salida: experiments/results/metrics_reports/application_results.csv
"""
import argparse, sys, json, shutil, time
from pathlib import Path
import numpy as np, cv2

ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from src.datasets import list_pairs, load_pair
from src.fusion import TopHatFusion
from src.fusion.optimal_top_hat import OptimalMultiscaleFusion

WORK = ROOT / "experiments" / "results" / "applications"
OUTCSV = ROOT / "experiments" / "results" / "metrics_reports" / "application_results.csv"
COCO_KEEP = {0: "person", 1: "bicycle", 2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
CLASSES = ["person", "bicycle", "car", "motorcycle", "bus", "truck"]
REMAP = {0: 0, 1: 1, 2: 2, 3: 3, 5: 4, 7: 5}

MODALITIES = {
    "VIS": lambda v, i: v,
    "IR": lambda v, i: i,
    "Anterior_TopHat": lambda v, i: TopHatFusion("disk", 5).fuse(v, i),
    "Optimo_Multiescala": lambda v, i: OptimalMultiscaleFusion(n=6, base_radius=2.89, m=0.10).fuse(v, i),
}

def to_u8(arr): return (np.clip(arr, 0, 1) * 255).astype("uint8")

# ---------------- 1) PSEUDO-ETIQUETAS ----------------
def pseudo_labels(pairs, labeler, conf=0.25):
    """Devuelve dict stem -> (H, W, [ (cls, xc,yc,w,h normalizado) ])."""
    labels = {}
    if labeler == "yolo":
        from ultralytics import YOLO
        det = YOLO("yolov8n.pt")
        for vp, ip in pairs:
            v, _ = load_pair(vp, ip); H, W = v.shape
            r = det(to_u8(v), conf=conf, verbose=False)[0]
            boxes = []
            if r.boxes is not None:
                for c, xywhn in zip(r.boxes.cls.tolist(), r.boxes.xywhn.tolist()):
                    c = int(c)
                    if c in REMAP: boxes.append((REMAP[c], *xywhn))
            labels[vp.stem] = (H, W, boxes)
    else:  # HOG (offline, solo personas) — respaldo para validar el pipeline sin torch
        hog = cv2.HOGDescriptor(); hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        for vp, ip in pairs:
            v, _ = load_pair(vp, ip); H, W = v.shape
            rects, _ = hog.detectMultiScale(cv2.cvtColor(to_u8(v), cv2.COLOR_GRAY2BGR),
                                            winStride=(8, 8), padding=(8, 8), scale=1.05, hitThreshold=-0.3)
            boxes = [(0, (x + w/2)/W, (y + h/2)/H, w/W, h/H) for (x, y, w, h) in rects]
            labels[vp.stem] = (H, W, boxes)
    return labels

# ---------------- 2) CONSTRUIR DATASETS POR MODALIDAD ----------------
def build_datasets(pairs, labels, val_frac=0.3, test_frac=0.0, seed=0):
    rng = np.random.default_rng(seed); idx = np.arange(len(pairs)); rng.shuffle(idx)
    nval = max(1, int(len(pairs) * val_frac)); ntest = int(len(pairs) * test_frac)
    test_ids = set(idx[:ntest]); val_ids = set(idx[ntest:ntest + nval])
    def split_of(k): return "test" if k in test_ids else ("valid" if k in val_ids else "train")
    if WORK.exists(): shutil.rmtree(WORK)
    coco = {m: {sp: {"images": [], "annotations": [], "categories":
                     [{"id": i, "name": c} for i, c in enumerate(CLASSES)]} for sp in ("train", "valid", "test")}
            for m in MODALITIES}
    img_id = {m: 0 for m in MODALITIES}; ann_id = {m: 0 for m in MODALITIES}
    cls_label = {m: {} for m in MODALITIES}  # imagen -> 1 si hay persona
    for k, (vp, ip) in enumerate(pairs):
        v, i = load_pair(vp, ip)
        if i.shape != v.shape: i = cv2.resize(i, (v.shape[1], v.shape[0]))
        H, W, boxes = labels[vp.stem]; sp = split_of(k); stem = vp.stem
        for m, fn in MODALITIES.items():
            img = to_u8(fn(v, i)); d = WORK / m
            (d / sp / "images").mkdir(parents=True, exist_ok=True)
            (d / sp / "labels").mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(d / sp / "images" / f"{stem}.png"), img)
            # YOLO labels
            with open(d / sp / "labels" / f"{stem}.txt", "w") as f:
                for (c, xc, yc, bw, bh) in boxes: f.write(f"{c} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")
            # COCO
            iid = img_id[m]; coco[m][sp]["images"].append({"id": iid, "file_name": f"{stem}.png", "width": W, "height": H})
            for (c, xc, yc, bw, bh) in boxes:
                x, y, ww, hh = (xc - bw/2)*W, (yc - bh/2)*H, bw*W, bh*H
                coco[m][sp]["annotations"].append({"id": ann_id[m], "image_id": iid, "category_id": c,
                                                   "bbox": [x, y, ww, hh], "area": ww*hh, "iscrowd": 0})
                ann_id[m] += 1
            img_id[m] += 1
            cls_label[m][f"{sp}/{stem}.png"] = int(any(c == 0 for (c, *_) in boxes))
    # data.yaml (YOLO) y _annotations.coco.json (RF-DETR)
    import yaml
    for m in MODALITIES:
        d = WORK / m
        yaml.safe_dump({"path": str(d), "train": "train/images", "val": "valid/images",
                        "test": "test/images" if ntest else "valid/images",
                        "names": {i: c for i, c in enumerate(CLASSES)}}, open(d / "data.yaml", "w"))
        for sp in ("train", "valid", "test"):
            if coco[m][sp]["images"]:
                json.dump(coco[m][sp], open(d / sp / "_annotations.coco.json", "w"))
    return cls_label

# ---------------- 3) MODELOS ----------------
def run_yolo(epochs, device, imgsz=640):
    from ultralytics import YOLO; rows = []
    for m in MODALITIES:
        dy = str(WORK / m / "data.yaml")
        model = YOLO("yolov8n.pt")
        model.train(data=dy, epochs=epochs, imgsz=imgsz, device=device, seed=0,
                    project=str(WORK / "runs_yolo"), name=m, exist_ok=True, verbose=False)
        r = model.val(data=dy, device=device)
        P, R = float(r.box.mp), float(r.box.mr)
        rows.append({"modelo": "YOLO", "modalidad": m, "mAP50": round(float(r.box.map50), 4),
                     "mAP50_95": round(float(r.box.map), 4), "precision": round(P, 4),
                     "recall": round(R, 4), "F1": round(2*P*R/(P+R+1e-9), 4)})
    return rows

def run_rfdetr(epochs, device):
    from rfdetr import RFDETRBase
    import supervision as sv
    rows = []
    for m in MODALITIES:
        d = WORK / m
        try:
            model = RFDETRBase()
            model.train(dataset_dir=str(d), epochs=epochs, batch_size=4, lr=1e-4, output_dir=str(WORK/f"rfdetr_{m}"))
            # mAP en valid con supervision
            ds = sv.DetectionDataset.from_coco(str(d/"valid"), str(d/"valid"/"_annotations.coco.json"))
            targets, preds = [], []
            for path, _, ann in ds:
                img = cv2.imread(path); det = model.predict(img, threshold=0.3)
                targets.append(ann); preds.append(det)
            mapr = sv.MeanAveragePrecision().update(preds, targets).compute()
            rows.append({"modelo": "RF-DETR", "modalidad": m, "mAP50": round(float(mapr.map50), 4),
                         "mAP50_95": round(float(mapr.map50_95), 4), "precision": None, "recall": None, "F1": None})
        except Exception as e:
            rows.append({"modelo": "RF-DETR", "modalidad": m, "error": str(e)[:120]})
    return rows

def run_keras(cls_label, epochs):
    import tensorflow as tf
    from sklearn.metrics import precision_recall_fscore_support, accuracy_score
    rows = []
    for m in MODALITIES:
        d = WORK / m
        # armar carpetas por clase (0/1) para train y valid
        for sp in ("train", "valid"):
            for c in ("0", "1"): (d/"kr"/sp/c).mkdir(parents=True, exist_ok=True)
            for img in (d/sp/"images").glob("*.png"):
                lab = cls_label[m].get(f"{sp}/{img.name}", 0)
                shutil.copy(img, d/"kr"/sp/str(lab)/img.name)
        IMG = 224
        tr = tf.keras.utils.image_dataset_from_directory(str(d/"kr"/"train"), image_size=(IMG, IMG), batch_size=8)
        va = tf.keras.utils.image_dataset_from_directory(str(d/"kr"/"valid"), image_size=(IMG, IMG), batch_size=8, shuffle=False)
        norm = tf.keras.layers.Rescaling(1./255)
        base = tf.keras.applications.MobileNetV2(input_shape=(IMG, IMG, 3), include_top=False, weights="imagenet"); base.trainable = False
        model = tf.keras.Sequential([norm, base, tf.keras.layers.GlobalAveragePooling2D(),
                                     tf.keras.layers.Dropout(0.2), tf.keras.layers.Dense(2, activation="softmax")])
        model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
        model.fit(tr, validation_data=va, epochs=epochs, verbose=0)
        y_true = np.concatenate([y for _, y in va]); y_pred = model.predict(va, verbose=0).argmax(1)
        P, R, F1, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", zero_division=0)
        rows.append({"modelo": "Keras", "modalidad": m, "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
                     "precision": round(float(P), 4), "recall": round(float(R), 4), "F1": round(float(F1), 4)})
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="yolo,rfdetr,keras")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--device", default="0")
    ap.add_argument("--labeler", choices=["yolo", "hog"], default="yolo")
    ap.add_argument("--val_frac", type=float, default=0.3)
    args = ap.parse_args()
    pairs = list_pairs()
    if not pairs: print("No hay pares en data/raw/. Abortando."); return
    print(f"{len(pairs)} pares. Generando pseudo-etiquetas ({args.labeler})...")
    labels = pseudo_labels(pairs, args.labeler)
    print("Construyendo datasets de las 4 modalidades...")
    cls_label = build_datasets(pairs, labels, val_frac=args.val_frac)
    want = [x.strip() for x in args.models.split(",") if x.strip()]
    import pandas as pd; rows = []
    for name, fn in [("yolo", lambda: run_yolo(args.epochs, args.device)),
                     ("rfdetr", lambda: run_rfdetr(args.epochs, args.device)),
                     ("keras", lambda: run_keras(cls_label, args.epochs))]:
        if name not in want: continue
        print(f"\n===== {name.upper()} =====")
        try:
            rows += fn()
        except ImportError as e:
            print(f"  [SKIP] {name}: librería no instalada ({e}).")
        except Exception as e:
            print(f"  [ERROR] {name}: {e}")
    if rows:
        df = pd.DataFrame(rows); OUTCSV.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(OUTCSV, index=False); print("\n==== RESULTADOS ===="); print(df.to_string(index=False))
        print(f"\nGuardado: {OUTCSV}")
    else:
        print("Sin resultados (¿faltan librerías? instalá: pip install ultralytics rfdetr supervision tensorflow scikit-learn).")

if __name__ == "__main__":
    main()
