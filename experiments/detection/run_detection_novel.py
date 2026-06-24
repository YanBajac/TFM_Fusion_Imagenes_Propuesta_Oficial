# -*- coding: utf-8 -*-
"""
run_detection_novel.py
----------------------
Evaluación de DETECTABILIDAD (orientada a tarea) incluyendo la PROPUESTA NOVEDOSA.
Fusiona al vuelo (en memoria) desde los pares VIS/IR del TNO — no necesita imágenes
guardadas — y corre un detector sobre cada modalidad.

Detectores (correr en PC/Colab con el venv e instalaciones correspondientes):
  --detector yolo   : Ultralytics YOLO (pip install ultralytics). Clases COCO.
  --detector rfdetr : RF-DETR de Roboflow (pip install "rfdetr"). Clases COCO.
  --detector hog    : HOG-SVM de personas (OpenCV, offline; SOLO referencial, no concluyente).

Uso (en tu PC):
  python experiments/detection/run_detection_novel.py --detector yolo   --weights yolov8n.pt
  python experiments/detection/run_detection_novel.py --detector rfdetr

Salida: experiments/results/metrics_reports/detection_novel_<detector>.csv  (+ resumen por método)
"""
import argparse, time, sys
from pathlib import Path
import numpy as np, cv2, pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from src.datasets import list_pairs, load_pair
from src.fusion.novel_fusion import fuse_novel
from src.fusion.optimal_top_hat import fuse_optimal_multiscale
from src.fusion.comparatives import average_fusion, laplacian_pyramid_fusion, curvelet_fusion
from src.fusion.prop_top_hat import TopHatFusion

MR = ROOT / "experiments" / "results" / "metrics_reports"
VEHICLE = {"car","truck","bus","motorcycle","bicycle"}

# Modalidades fusionadas al vuelo (VIS/IR se tratan aparte)
FUSERS = {
    "Promedio":            lambda v,i: average_fusion(v,i),
    "PiramideLaplace":     lambda v,i: laplacian_pyramid_fusion(v,i,levels=4),
    "Curvelet":            lambda v,i: curvelet_fusion(v,i,levels=3),
    "TopHat_disk_L5":      lambda v,i: TopHatFusion("disk",levels=5).fuse(v,i),
    "Optimo_Multiescala":  lambda v,i: fuse_optimal_multiscale(v,i,6,2.89,0.10),
    "Propuesta_Novedosa":  lambda v,i: fuse_novel(v,i,8,0.120),   # n=8, m=0.12 (PSO)
}

def to_bgr(img01):
    g=(np.clip(img01,0,1)*255).astype(np.uint8)
    return cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)

class HOG:
    name="HOG-SVM (personas, OpenCV) — REFERENCIAL"
    def __init__(self):
        self.h=cv2.HOGDescriptor(); self.h.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    def __call__(self,bgr):
        rects,w=self.h.detectMultiScale(bgr,winStride=(8,8),padding=(8,8),scale=1.05)
        confs=[float(x) for x in (w.ravel().tolist() if hasattr(w,'ravel') else list(w))]
        return ["person"]*len(rects), confs

class YOLOv:
    def __init__(self,weights="yolov8n.pt",conf=0.25):
        from ultralytics import YOLO
        self.m=YOLO(weights); self.conf=conf; self.names=self.m.names; self.name=f"YOLO ({weights})"
    def __call__(self,bgr):
        r=self.m(bgr,conf=self.conf,verbose=False)[0]
        if r.boxes is None: return [],[]
        labels=[self.names[int(c)] for c in r.boxes.cls.tolist()]
        confs=[float(x) for x in r.boxes.conf.tolist()]
        return labels,confs

class RFDETRv:
    def __init__(self,threshold=0.40):
        from rfdetr import RFDETRBase
        try:
            from rfdetr.util.coco_classes import COCO_CLASSES
            self.names = COCO_CLASSES
        except Exception:
            self.names = None     # se mapeará por id si no está disponible
        self.m=RFDETRBase(); self.thr=threshold; self.name="RF-DETR (base, COCO)"
    def __call__(self,bgr):
        rgb = bgr[:,:,::-1]                       # BGR -> RGB
        det = self.m.predict(rgb, threshold=self.thr)
        ids = list(det.class_id) if det.class_id is not None else []
        confs = [float(x) for x in det.confidence] if det.confidence is not None else []
        def nm(c):
            c=int(c)
            if isinstance(self.names,dict): return self.names.get(c,str(c))
            if isinstance(self.names,(list,tuple)) and c < len(self.names): return self.names[c]
            return str(c)
        return [nm(c) for c in ids], confs

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--detector",choices=["hog","yolo","rfdetr"],default="hog")
    ap.add_argument("--weights",default="yolov8n.pt"); ap.add_argument("--limit",type=int,default=0)
    a=ap.parse_args()
    det = {"hog":HOG,"yolo":lambda:YOLOv(a.weights),"rfdetr":RFDETRv}[a.detector]()
    print("Detector:",det.name)
    pairs=list_pairs()
    if a.limit: pairs=pairs[:a.limit]
    rows=[]
    for vp,ip in pairs:
        v,i=load_pair(vp,ip); stem=Path(vp).stem
        mods={"VIS":v,"IR":i}
        for name,fn in FUSERS.items(): mods[name]=fn(v,i)
        for name,img in mods.items():
            t=time.time(); labels,confs=det(to_bgr(img)); ms=(time.time()-t)*1000
            rows.append({"method":name,"image":stem,"n_det":len(labels),
                "n_person":sum(1 for l in labels if l=="person"),
                "n_vehicle":sum(1 for l in labels if l in VEHICLE),
                "conf_mean":float(np.mean(confs)) if confs else 0.0,
                "has_det":int(len(labels)>0),"ms":ms})
    df=pd.DataFrame(rows); MR.mkdir(parents=True,exist_ok=True)
    out=MR/f"detection_novel_{a.detector}.csv"; df.to_csv(out,index=False,float_format="%.4f")
    agg=df.groupby("method").agg(det_total=("n_det","sum"),det_x_img=("n_det","mean"),
        person_total=("n_person","sum"),vehiculo_total=("n_vehicle","sum"),
        imgs_con_det=("has_det","sum"),conf_mean=("conf_mean",lambda s:s[s>0].mean() if (s>0).any() else 0),
        ms_mean=("ms","mean")).round(3)
    agg["FPS"]=(1000/agg["ms_mean"]).round(1)
    order=["VIS","IR","Promedio","PiramideLaplace","Curvelet","TopHat_disk_L5","Optimo_Multiescala","Propuesta_Novedosa"]
    agg=agg.reindex([m for m in order if m in agg.index])
    print(agg.to_string()); print("\nGuardado:",out)

if __name__=="__main__": main()
