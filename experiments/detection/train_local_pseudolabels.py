# -*- coding: utf-8 -*-
"""
train_local_pseudolabels.py
---------------------------
Entrenamiento LOCAL de YOLO (Ultralytics) para comparar modalidades de fusión
SIN anotación manual. Procedimiento:

1) Un YOLO preentrenado (COCO) genera *pseudo-etiquetas* de personas/vehículos
   sobre las imágenes VIS (la modalidad con más textura).
2) Esas mismas cajas se reutilizan para VIS, IR y las fusiones (imágenes
   registradas: las cajas son válidas para todas las versiones).
3) Se entrena un YOLO por modalidad con idénticos hiperparámetros y se reportan
   mAP@0.5, mAP@0.5:0.95, Precision, Recall y F1.

Caveat metodológico: el "ground truth" son pseudo-etiquetas (lo que el modelo
preentrenado ve en VIS). Por eso la lectura es RELATIVA entre modalidades, no un
mAP absoluto. Para mAP absoluto usá un dataset etiquetado por humanos (Roboflow/M3FD).

Uso (en tu PC):
    pip install ultralytics
    python experiments/detection/train_local_pseudolabels.py --epochs 30 --device cpu
"""
import argparse, sys
from pathlib import Path
import numpy as np, cv2, yaml, pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.datasets import list_pairs, load_pair
from src.fusion import TopHatFusion
from src.fusion.optimal_top_hat import OptimalMultiscaleFusion

OUT = ROOT / "experiments" / "results" / "detection_train"
COCO_KEEP = {0: "person", 1: "bicycle", 2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
CLASSES = ["person", "bicycle", "car", "motorcycle", "bus", "truck"]
REMAP = {0:0, 1:1, 2:2, 3:3, 5:4, 7:5}

MODALITIES = {
    "VIS": lambda v, i: v,
    "IR": lambda v, i: i,
    "Anterior_TopHat": lambda v, i: TopHatFusion("disk", 5).fuse(v, i),
    "Optimo_Multiescala": lambda v, i: OptimalMultiscaleFusion(n=6, base_radius=2.89, m=0.10).fuse(v, i),
}

def to_u8_bgr(arr):
    return cv2.cvtColor((np.clip(arr,0,1)*255).astype("uint8"), cv2.COLOR_GRAY2BGR)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--device", default="cpu")          # 'cpu' o '0' (GPU)
    ap.add_argument("--val_frac", type=float, default=0.3)
    ap.add_argument("--pseudo_conf", type=float, default=0.25)
    args = ap.parse_args()
    from ultralytics import YOLO

    pairs = list_pairs()
    if not pairs:
        print("No hay pares VIS/IR en data/raw/. Abortando."); return
    print(f"{len(pairs)} pares. Generando pseudo-etiquetas con YOLO preentrenado...")

    pl = YOLO("yolov8n.pt")
    rng = np.random.default_rng(0)
    idx = np.arange(len(pairs)); rng.shuffle(idx)
    n_val = max(1, int(len(pairs)*args.val_frac))
    val_ids = set(idx[:n_val].tolist())

    # 1) pseudo-labels sobre VIS + 2) construir datasets por modalidad
    for name, fn in MODALITIES.items():
        for split in ("train","val"):
            (OUT/name/split/"images").mkdir(parents=True, exist_ok=True)
            (OUT/name/split/"labels").mkdir(parents=True, exist_ok=True)

    for k,(vp,ip) in enumerate(pairs):
        vis, ir = load_pair(vp, ip)
        if ir.shape != vis.shape:
            ir = cv2.resize(ir,(vis.shape[1],vis.shape[0]))
        split = "val" if k in val_ids else "train"
        # pseudo-etiquetas desde VIS
        res = pl(to_u8_bgr(vis), conf=args.pseudo_conf, verbose=False)[0]
        H,W = vis.shape
        lines=[]
        if res.boxes is not None:
            for c,xywhn in zip(res.boxes.cls.tolist(), res.boxes.xywhn.tolist()):
                c=int(c)
                if c in REMAP:
                    x,y,w,h = xywhn
                    lines.append(f"{REMAP[c]} {x:.6f} {y:.6f} {w:.6f} {h:.6f}")
        stem=vp.stem
        for name, fn in MODALITIES.items():
            img = fn(vis, ir)
            cv2.imwrite(str(OUT/name/split/"images"/f"{stem}.png"),
                        (np.clip(img,0,1)*255).astype("uint8"))
            (OUT/name/split/"labels"/f"{stem}.txt").write_text("\n".join(lines))

    # 3) entrenar y evaluar por modalidad
    rows=[]
    for name in MODALITIES:
        dyaml = OUT/name/"data.yaml"
        yaml.safe_dump({"path":str(OUT/name),"train":"train/images","val":"val/images",
                        "names":{i:c for i,c in enumerate(CLASSES)}}, open(dyaml,"w"))
        print(f"\n=== Entrenando modalidad: {name} ===")
        model = YOLO("yolov8n.pt")
        model.train(data=str(dyaml), epochs=args.epochs, imgsz=args.imgsz,
                    device=args.device, seed=0, project=str(OUT/"runs"),
                    name=name, exist_ok=True, verbose=False, plots=True)
        m = model.val(data=str(dyaml), device=args.device)
        P,R = float(m.box.mp), float(m.box.mr)
        rows.append({"modalidad":name, "mAP50":round(float(m.box.map50),4),
                     "mAP50_95":round(float(m.box.map),4),
                     "precision":round(P,4),"recall":round(R,4),
                     "F1":round(2*P*R/(P+R+1e-9),4)})
    df=pd.DataFrame(rows)
    csv=ROOT/"experiments"/"results"/"metrics_reports"/"detection_training_metrics.csv"
    df.to_csv(csv, index=False)
    print("\n==== RESULTADOS (pseudo-etiquetas, lectura relativa) ====")
    print(df.to_string(index=False))
    print(f"\nGuardado: {csv}")
    print("Curvas de pérdida por modalidad en:", OUT/"runs")

if __name__=="__main__":
    main()
