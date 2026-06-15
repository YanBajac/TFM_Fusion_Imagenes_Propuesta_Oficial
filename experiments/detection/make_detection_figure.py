# -*- coding: utf-8 -*-
"""Figura de la evaluación de detección con YOLO (a partir de detection_summary.csv)."""
from pathlib import Path
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
MDIR = ROOT/"experiments"/"results"/"metrics_reports"
FIG = ROOT/"docs"/"figures"
s = pd.read_csv(MDIR/"detection_summary.csv").set_index("method")

def grp(name):
    if name=="VIS": return "VIS"
    if name=="IR": return "IR"
    if name in ("Promedio","PiramideLaplace","Curvelet"): return "Baselines"
    return "Fusión +BTH" if "BTH" in name else "Fusión WTH"
s["grupo"]=[grp(m) for m in s.index]
order=["VIS","IR","Baselines","Fusión WTH","Fusión +BTH"]
g=s.groupby("grupo")[["person_total","vehiculo_total"]].sum().reindex(order)

fig,ax=plt.subplots(1,2,figsize=(14,5.4))
x=np.arange(len(order)); w=0.38
ax[0].bar(x-w/2, g["person_total"], w, label="Personas", color="#c0392b")
ax[0].bar(x+w/2, g["vehiculo_total"], w, label="Vehículos", color="#2980b9")
ax[0].set_xticks(x); ax[0].set_xticklabels(order, rotation=15)
ax[0].set_ylabel("Detecciones (total, 20 imágenes)")
ax[0].set_title("Detecciones de YOLO por modalidad: personas vs vehículos", weight="bold")
ax[0].legend()
for i,v in enumerate(g["person_total"]): ax[0].text(i-w/2,v+0.2,int(v),ha="center",fontsize=9)
for i,v in enumerate(g["vehiculo_total"]): ax[0].text(i+w/2,v+0.2,int(v),ha="center",fontsize=9)

ss=s.sort_values("det_total")
colors=[("#e67e22" if "BTH" in m else "#27ae60") if m.startswith("TopHat") else
        ("#2980b9" if m=="PiramideLaplace" else "#95a5a6") for m in ss.index]
ax[1].barh(ss.index, ss["det_total"], color=colors)
ax[1].set_xlabel("Detecciones totales")
ax[1].set_title("Detecciones totales por método (YOLOv8n, inferencia)", weight="bold")
for i,v in enumerate(ss["det_total"]): ax[1].text(v+0.1,i,int(v),va="center",fontsize=8)
fig.tight_layout()
fig.savefig(FIG/"fig_deteccion_yolo.png", dpi=150)
print("Figura:", FIG/"fig_deteccion_yolo.png")
print(g.to_string())
