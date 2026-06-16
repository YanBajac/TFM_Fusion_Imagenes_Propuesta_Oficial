# -*- coding: utf-8 -*-
"""Figura comparativa del método óptimo (PSO) en métricas de fidelidad y contraste."""
from pathlib import Path
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT=Path("."); MDIR=ROOT/"experiments/results/metrics_reports"; FIG=ROOT/"docs/figures"
m=pd.read_csv(MDIR/"descriptive_means.csv",index_col=0)
sel=["Promedio","Curvelet","PiramideLaplace","TopHat_disk_L5","TopHat_Optimo"]
lab={"Promedio":"Promedio","Curvelet":"Curvelet","PiramideLaplace":"Laplace",
     "TopHat_disk_L5":"TH disco L5","TopHat_Optimo":"TH Óptimo (PSO)"}
mets=[("SSIM","↑"),("Qabf","↑"),("SCD","↑"),("VIF","↑"),("SD","↑"),("Nabf","↓")]
fig,axes=plt.subplots(2,3,figsize=(14,7.5))
for ax,(mt,dirn) in zip(axes.ravel(),mets):
    vals=[m.loc[s,mt] for s in sel]
    colors=["#27ae60" if s=="TopHat_Optimo" else "#9aa6b2" for s in sel]
    ax.bar([lab[s] for s in sel],vals,color=colors)
    ax.set_title(f"{mt}  ({'mayor=mejor' if dirn=='↑' else 'menor=mejor'})",weight="bold",fontsize=12)
    ax.tick_params(axis="x",rotation=20,labelsize=9)
    for i,v in enumerate(vals): ax.text(i,v,f"{v:.3f}",ha="center",va="bottom",fontsize=8)
fig.suptitle("Método óptimo (disco+lineales, PSO r=1·m=0,30) frente a referentes — medias sobre 20 pares",
             fontsize=13,weight="bold")
fig.tight_layout(rect=[0,0,1,0.96])
fig.savefig(FIG/"fig_metodo_optimo.png",dpi=150); print("ok",FIG/"fig_metodo_optimo.png")
