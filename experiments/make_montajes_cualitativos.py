# -*- coding: utf-8 -*-
"""Montajes cualitativos (20 escenas TNO): VIS, IR, los 6 comparativos y la propuesta.

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
from src.fusion import (fuse_optimal, laplacian_pyramid_fusion, ratio_pyramid_fusion,
                        dwt_fusion, dtcwt_fusion, curvelet_fusion, tophat_classic_fusion)

# Hiperparametros de la propuesta (PSO, operador con suma de ramas)
PROP_R, PROP_M = 25, 0.0703

OUT = "docs/figures/cualitativas/"
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.family": "serif"})

CELLS = [
    ("VIS", None),
    ("IR", None),
    ("Pirámide Laplace (LP)", lambda v, i: laplacian_pyramid_fusion(v, i, levels=4)),
    ("Ratio Pyramid (RP)", lambda v, i: ratio_pyramid_fusion(v, i, levels=4)),
    ("DWT", lambda v, i: dwt_fusion(v, i, levels=3)),
    ("DTCWT", lambda v, i: dtcwt_fusion(v, i, levels=4)),
    ("Curvelet (CVT)", lambda v, i: curvelet_fusion(v, i, levels=3)),
    ("Top-Hat clásico", lambda v, i: tophat_classic_fusion(v, i, r=5)),
    (f"Propuesta (r={PROP_R}, m={PROP_M:.3f})".replace(".", ","),
     lambda v, i: fuse_optimal(v, i, r=PROP_R, m=PROP_M, mode="sum")),
]

for idx, (vp, ip) in enumerate(list_pairs(), 1):
    vis, ir = load_pair(vp, ip)
    stem = os.path.splitext(os.path.basename(str(vp)))[0]
    fig, axes = plt.subplots(3, 3, figsize=(11.5, 8.2))
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
    fig.suptitle(f"Escena {idx}: {stem.replace('_', ' ')[:60]}", fontsize=12, y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(os.path.join(OUT, f"montaje_{idx:02d}.png"), dpi=105, facecolor="white")
    plt.close(fig)
    print(f"montaje {idx:02d} ok", flush=True)
print("listo:", OUT)
