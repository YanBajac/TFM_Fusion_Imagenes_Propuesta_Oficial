# -*- coding: utf-8 -*-
"""Montajes cualitativos (20 escenas TNO): VIS, IR, comparativos y la propuesta (r=12, m=0.127).

Calcula las fusiones directamente con src/fusion (no depende de imagenes pre-fusionadas).
Uso (desde la raiz del repo):  python experiments/make_montajes_cualitativos.py
"""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, ".")
from src.datasets import list_pairs, load_pair
from src.fusion.comparatives import average_fusion, laplacian_pyramid_fusion, curvelet_fusion
from src.fusion.prop_top_hat import TopHatFusion
from src.fusion.novel_fusion import fuse_novel
from src.fusion.optimal_top_hat import fuse_optimal

OUT = "docs/figures/cualitativas/"
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.family": "serif"})

CELLS = [
    ("VIS", None),
    ("IR", None),
    ("Promedio", lambda v, i: average_fusion(v, i)),
    ("Pirámide Laplace", lambda v, i: laplacian_pyramid_fusion(v, i, levels=4)),
    ("Curvelet", lambda v, i: curvelet_fusion(v, i, levels=3)),
    ("Torre Top-Hat disco L5 (anterior)", lambda v, i: TopHatFusion("disk", levels=5).fuse(v, i)),
    ("Variante multiescala (descartada)", lambda v, i: fuse_novel(v, i, n=8, m=0.12)),
    ("Propuesta (r=12, m=0,127)", lambda v, i: fuse_optimal(v, i, r=12, m=0.1274, mode="max")),
]

for idx, (vp, ip) in enumerate(list_pairs(), 1):
    vis, ir = load_pair(vp, ip)
    stem = os.path.splitext(os.path.basename(str(vp)))[0]
    fig, axes = plt.subplots(2, 4, figsize=(13, 6.0))
    fig.patch.set_facecolor("white")
    for k, (lab, fn) in enumerate(CELLS):
        ax = axes.ravel()[k]
        img = vis if lab == "VIS" else ir if lab == "IR" else fn(vis, ir)
        ax.imshow(np.clip(img, 0, 1), cmap="gray", vmin=0, vmax=1)
        es_prop = lab.startswith("Propuesta")
        ax.set_title(lab, fontsize=9.5, pad=3, color="#c00000" if es_prop else "black",
                     fontweight="bold" if es_prop else "normal")
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_edgecolor("#c00000" if es_prop else "#555555")
            sp.set_linewidth(2.2 if es_prop else 0.6)
    fig.suptitle(f"Escena {idx}: {stem.replace('_', ' ')[:60]}", fontsize=12, y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.965])
    fig.savefig(os.path.join(OUT, f"montaje_{idx:02d}.png"), dpi=105, facecolor="white")
    plt.close(fig)
    print(f"montaje {idx:02d} ok", flush=True)
print("listo:", OUT)
