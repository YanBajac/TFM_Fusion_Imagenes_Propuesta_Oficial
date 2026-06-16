# -*- coding: utf-8 -*-
from pathlib import Path
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
MDIR=Path("experiments/results/metrics_reports"); FIG=Path("docs/figures")
m=pd.read_csv(MDIR/"descriptive_means.csv",index_col=0)
sel=["Promedio","Curvelet","PiramideLaplace","TopHat_disk_L5","TopHat_Optimo","Optimo_Multiescala"]
lab={"Promedio":"Promedio","Curvelet":"Curvelet","PiramideLaplace":"Laplace",
     "TopHat_disk_L5":"Torre TH L5\n(anterior)","TopHat_Optimo":"Óptimo 1 escala",
     "Optimo_Multiescala":"Óptimo\nMultiescala"}
mets=[("Qabf","↑"),("SCD","↑"),("SSIM","↑"),("Nabf","↓"),("VIF","↑"),("SD","↑")]
fig,axes=plt.subplots(2,3,figsize=(14,7.5))
for ax,(mt,dr) in zip(axes.ravel(),mets):
    vals=[m.loc[s,mt] for s in sel]
    cols=["#c0392b" if s=="Optimo_Multiescala" else "#9aa6b2" for s in sel]
    ax.bar(range(len(sel)),vals,color=cols)
    ax.set_xticks(range(len(sel))); ax.set_xticklabels([lab[s] for s in sel],fontsize=8.5,rotation=15)
    ax.set_title(f"{mt}  ({'mayor=mejor' if dr=='↑' else 'menor=mejor'})",weight="bold",fontsize=12)
    for i,v in enumerate(vals): ax.text(i,v,f"{v:.3f}",ha="center",va="bottom",fontsize=8)
fig.suptitle("Método óptimo MULTIESCALA (PSO: n=6, r≈2,9, m=0,10) vs método anterior y baselines — medias sobre 20 pares",
             fontsize=12.5,weight="bold")
fig.tight_layout(rect=[0,0,1,0.96]); fig.savefig(FIG/"fig_metodo_optimo_multiescala.png",dpi=150)
print("ok")
