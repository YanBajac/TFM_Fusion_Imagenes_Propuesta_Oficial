# -*- coding: utf-8 -*-
"""
run_detection_eval.py
---------------------
Evaluación orientada a tarea (detección) de los métodos de fusión.
Corre un detector sobre VIS, IR y las imágenes fusionadas de cada método, y
calcula métricas de DETECTABILIDAD (sin etiquetas) y de PRODUCCIÓN.

Detectores soportados:
  --detector yolo  : Ultralytics YOLO (requiere torch; GPU/CPU). Clases COCO.
  --detector hog   : HOG-SVM de personas integrado en OpenCV (offline, sin pesos).

Salida: experiments/results/metrics_reports/detection_metrics.csv
        (una fila por imagen y método)

Uso:
  python experiments/detection/run_detection_eval.py --detector hog
  python experiments/detection/run_detection_eval.py --detector yolo --weights yolov8n.pt
"""
import argparse, time
from pathlib import Path
import numpy as np
import cv2
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
FUSED = ROOT / "experiments" / "results" / "fused_images"
RAW = ROOT / "data" / "raw"
OUT = ROOT / "experiments" / "results" / "metrics_reports" / "detection_metrics.csv"

# Conjuntos a evaluar: fuentes + métodos de fusión
METHOD_DIRS = {"VIS": RAW / "VIS", "IR": RAW / "IR"}
if FUSED.exists():
    for d in sorted(FUSED.iterdir()):
        # solo los métodos inter-comparados (no las 36 configs del benchmark)
        if d.is_dir() and d.name in {
            "Promedio","PiramideLaplace","Curvelet",
            "TopHat_disk_L3","TopHat_square_L3","TopHat_cross_L3","TopHat_disk_L5",
            "TopHat_disk_L3_BTH","TopHat_square_L3_BTH","TopHat_cross_L3_BTH","TopHat_disk_L5_BTH",
            "TopHat_Optimo","Optimo_Multiescala"}:
            METHOD_DIRS[d.name] = d

VEHICLE = {"car","truck","bus","motorcycle","bicycle"}

def list_imgs(d):
    ex = (".png",".jpg",".jpeg",".bmp",".tif",".tiff")
    return sorted([p for p in Path(d).iterdir() if p.suffix.lower() in ex])

# ---------------- detectores ----------------
class HOGDetector:
    name = "HOG-SVM (personas, OpenCV, offline)"
    def __init__(self, upscale=1.6, hit=-0.3):
        self.h = cv2.HOGDescriptor()
        self.h.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.upscale = upscale; self.hit = hit
    def __call__(self, path):
        im = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if im is None: return [], [], []
        if self.upscale != 1.0:
            im = cv2.resize(im, None, fx=self.upscale, fy=self.upscale)
        rgb = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
        rects, w = self.h.detectMultiScale(rgb, winStride=(8,8), padding=(8,8),
                                           scale=1.05, hitThreshold=self.hit)
        confs = [float(x) for x in w] if len(w) else []
        labels = ["person"] * len(rects)
        return labels, confs, rects

class YOLODetector:
    def __init__(self, weights="yolov8n.pt", conf=0.25):
        from ultralytics import YOLO
        self.model = YOLO(weights); self.conf = conf
        self.name = f"YOLO ({weights})"
        self.names = self.model.names
    def __call__(self, path):
        r = self.model(str(path), conf=self.conf, verbose=False)[0]
        labels = [self.names[int(c)] for c in r.boxes.cls.tolist()] if r.boxes is not None else []
        confs = [float(x) for x in r.boxes.conf.tolist()] if r.boxes is not None else []
        return labels, confs, None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--detector", choices=["hog","yolo"], default="hog")
    ap.add_argument("--weights", default="yolov8n.pt")
    args = ap.parse_args()
    det = HOGDetector() if args.detector=="hog" else YOLODetector(args.weights)
    print(f"Detector: {getattr(det,'name',args.detector)}")
    rows=[]
    for method, d in METHOD_DIRS.items():
        if not Path(d).exists(): continue
        for p in list_imgs(d):
            t=time.time()
            labels, confs, _ = det(p)
            ms=(time.time()-t)*1000
            n=len(labels)
            persons=sum(1 for l in labels if l=="person")
            vehicles=sum(1 for l in labels if l in VEHICLE)
            rows.append({
                "method": method, "image": Path(p).stem,
                "n_det": n, "n_person": persons, "n_vehicle": vehicles,
                "conf_mean": float(np.mean(confs)) if confs else 0.0,
                "conf_max": float(np.max(confs)) if confs else 0.0,
                "has_det": int(n>0), "ms": ms,
            })
        print(f"  {method:24s} listo ({len(list_imgs(d))} imgs)")
    df=pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, float_format="%.4f")
    print(f"\nGuardado: {OUT}  ({len(df)} filas)")
    # resumen
    agg=df.groupby("method").agg(
        det_total=("n_det","sum"), det_x_img=("n_det","mean"),
        person_total=("n_person","sum"), imgs_con_det=("has_det","sum"),
        conf_mean=("conf_mean", lambda s: s[s>0].mean() if (s>0).any() else 0),
        ms_mean=("ms","mean")).round(3)
    agg["FPS"]=(1000/agg["ms_mean"]).round(1)
    print(agg.to_string())

if __name__=="__main__":
    main()
