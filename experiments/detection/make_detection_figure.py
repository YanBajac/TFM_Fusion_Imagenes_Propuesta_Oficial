# -*- coding: utf-8 -*-
"""Figura de detectabilidad por inferencia (YOLOv8n) — Parte B (aplicación)."""
from pathlib import Path
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
MDIR=Path("experiments/results/metrics_reports"); FIG=Path("docs/figures")
s=pd.read_csv(MDIR/"detection_summary.csv").set_index("method")

def grp(m):
    if m=="VIS": return "VIS"
    if m=="IR": return "IR"
    if m in ("Promedio","PiramideLaplace","Curvelet"): return "Baselines"
    if m=="Optimo_Multiescala": return "Óptimo Multiescala"
    return "Fusión +BTH" if "BTH" in m else "Fusión Top-Hat"
s["g"]=[grp(m) for m in s.index]
order=["VIS","IR","Baselines","Fusión Top-Hat","Fusión +BTH","Óptimo Multiescala"]
g=s.groupby("g")[["person_total","vehiculo_total"]].sum().reindex(order)

fig,ax=plt.subplots(1,2,figsize=(15,5.6))
x=np.arange(len(order)); w=0.38
ax[0].bar(x-w/2,g["person_total"],w,label="Personas",color="#c0392b")
ax[0].bar(x+w/2,g["vehiculo_total"],w,label="Vehículos",color="#2980b9")
ax[0].set_xticks(x); ax[0].set_xticklabels(order,rotation=18,fontsize=9)
ax[0].set_ylabel("Detecciones (total, 20 imágenes)"); ax[0].legend()
ax[0].set_title("YOLO por modalidad: personas vs vehículos",weight="bold")
for i,v in enumerate(g["person_total"]): ax[0].text(i-w/2,v+0.15,int(v),ha="center",fontsize=8)
for i,v in enumerate(g["vehiculo_total"]): ax[0].text(i+w/2,v+0.15,int(v),ha="center",fontsize=8)
ss=s.sort_values("det_total")
cols=["#c0392b" if m=="Optimo_Multiescala" else ("#2980b9" if m in ("VIS","IR") else "#9aa6b2") for m in ss.index]
ax[1].barh(ss.index,ss["det_total"],color=cols)
ax[1].set_xlabel("Detecciones totales"); ax[1].set_title("Detecciones por método (YOLOv8n inferencia)",weight="bold")
ax[1].tick_params(axis="y",labelsize=7)
for i,v in enumerate(ss["det_total"]): ax[1].text(v+0.1,i,int(v),va="center",fontsize=7)
fig.suptitle("Evaluación orientada a tarea — detectabilidad con YOLOv8n preentrenado (inferencia, sin etiquetas)",fontsize=12.5,weight="bold")
fig.tight_layout(rect=[0,0,1,0.96]); fig.savefig(FIG/"fig_deteccion_yolo.png",dpi=150)
print(g.to_string()); print("ok fig_deteccion_yolo.png")
