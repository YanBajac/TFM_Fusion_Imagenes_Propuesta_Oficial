# -*- coding: utf-8 -*-
"""Demo offline (HOG, referencial) de detectabilidad por MODALIDAD de entrada,
incluyendo el método óptimo multiescala. NO toca detection_metrics.csv."""
import sys, glob, time
from pathlib import Path
import numpy as np, cv2, pandas as pd
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/"data"/"raw"; FUS=ROOT/"experiments"/"results"/"fused_images"
OUT=ROOT/"experiments"/"results"/"metrics_reports"/"detection_demo_modalidades.csv"
MOD={"VIS":RAW/"VIS","IR":RAW/"IR","Promedio":FUS/"Promedio",
     "PiramideLaplace":FUS/"PiramideLaplace","TopHat_disk_L5 (anterior)":FUS/"TopHat_disk_L5",
     "Optimo_Multiescala (propuesta)":FUS/"Optimo_Multiescala"}
hog=cv2.HOGDescriptor(); hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
def det(path):
    im=cv2.imread(str(path),cv2.IMREAD_GRAYSCALE)
    if im is None: return None
    im=cv2.resize(im,None,fx=1.6,fy=1.6)
    rgb=cv2.cvtColor(im,cv2.COLOR_GRAY2BGR)
    r,w=hog.detectMultiScale(rgb,winStride=(8,8),padding=(8,8),scale=1.05,hitThreshold=-0.3)
    return len(r),(float(np.mean(w)) if len(w) else 0.0)
rows=[]
for name,d in MOD.items():
    ds=sorted([p for p in Path(d).iterdir() if p.suffix.lower() in ('.png','.jpg','.jpeg','.bmp')])[:20]
    for p in ds:
        c=det(p)
        if c: rows.append({"modalidad":name,"image":p.stem,"n_det":c[0],"conf":c[1] if c[0] else 0,"has":int(c[0]>0)})
df=pd.DataFrame(rows); df.to_csv(OUT,index=False)
ag=df.groupby("modalidad").agg(det_total=("n_det","sum"),imgs_con_det=("has","sum"),
    conf=("conf",lambda s:round(s[s>0].mean(),3) if (s>0).any() else 0)).reindex(list(MOD))
print(ag.to_string()); print("\nGuardado:",OUT.name)
