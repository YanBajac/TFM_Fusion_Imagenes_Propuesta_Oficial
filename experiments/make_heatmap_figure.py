# -*- coding: utf-8 -*-
"""Heatmap legible del benchmark exhaustivo (36 configs) por métrica."""
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(".")
df=pd.read_csv(ROOT/"experiments/results/metrics_reports/benchmark_top_hat.csv")
FIG=ROOT/"docs/figures/fig_heatmap_tophat.png"

SE=["disk","square","cross"]; SE_es={"disk":"disco","square":"cuadrado","cross":"cruz"}
L=[2,3,4,5]; R=[2,3,5]
metrics=["EN","SD","FE","MG","MI_vis","MI_ir"]
g=df.groupby(["Structuring_Element","Levels","Base_Radius"])[metrics].mean().reset_index()

# filas = (SE,L) 12; columnas = R 3
rows=[(se,l) for se in SE for l in L]
row_labels=[f"{SE_es[se]} · L{l}" for se,l in rows]

plt.rcParams["font.family"]="DejaVu Sans"
fig,axes=plt.subplots(2,3,figsize=(15,10))
for ax,m in zip(axes.ravel(), metrics):
    M=np.zeros((12,3))
    for i,(se,l) in enumerate(rows):
        for j,r in enumerate(R):
            M[i,j]=g[(g.Structuring_Element==se)&(g.Levels==l)&(g.Base_Radius==r)][m].values[0]
    im=ax.imshow(M, cmap="viridis", aspect="auto")
    ax.set_title(m, fontsize=14, weight="bold", pad=8)
    ax.set_xticks(range(3)); ax.set_xticklabels([f"r={r}" for r in R], fontsize=10)
    ax.set_yticks(range(12)); ax.set_yticklabels(row_labels, fontsize=9)
    # anotaciones legibles
    vmin,vmax=M.min(),M.max()
    for i in range(12):
        for j in range(3):
            v=M[i,j]
            txt=f"{v:.3f}" if m not in ("MG",) else f"{v:.4f}"
            ax.text(j,i,txt,ha="center",va="center",fontsize=8.5,
                    color="white" if (v-vmin)/(vmax-vmin+1e-9)<0.55 else "black")
    cb=fig.colorbar(im,ax=ax,fraction=0.046,pad=0.04); cb.ax.tick_params(labelsize=8)
    # separadores entre grupos de SE (cada 4 filas)
    for k in (3.5,7.5): ax.axhline(k,color="white",lw=2)
fig.suptitle("Benchmark exhaustivo de la Torre Top-Hat — promedio por configuración (SE × nivel × radio)",
             fontsize=15, weight="bold")
fig.tight_layout(rect=[0,0,1,0.97])
fig.savefig(FIG, dpi=160, bbox_inches="tight")
print("Heatmap regenerado:", FIG)
from PIL import Image; print("size", Image.open(FIG).size)
