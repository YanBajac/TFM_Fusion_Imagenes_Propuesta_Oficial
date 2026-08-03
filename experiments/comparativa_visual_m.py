# -*- coding: utf-8 -*-
"""Control visual del peso de contraste: la propuesta con distintos m sobre la misma escena.

Complementa el barrido cuantitativo (barrido_metricas_vs_m.py). Las metricas clasicas de
actividad mejoran al aumentar m, pero un realce excesivo satura y genera halos; esta figura
permite juzgar visualmente hasta donde el aumento de m sigue produciendo una fusion util.

Salida: docs/figures/fig_comparativa_m.png
Uso: .venv\Scripts\python.exe -X utf8 experiments/comparativa_visual_m.py
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.datasets import list_pairs, load_pair
from src.fusion.optimal_top_hat import fuse_optimal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIG = os.path.join(ROOT, "docs", "figures")
R = 25
M_VER = [0.0703, 0.30, 0.50, 1.00, 2.00]
ESCENAS = [0, 7, 14]   # tres escenas representativas (mismas del barrido)

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 9,
})


def main():
    os.makedirs(FIG, exist_ok=True)
    pares = list_pairs()
    filas = [load_pair(*pares[k]) for k in ESCENAS]

    ncols = 2 + len(M_VER)
    fig, axes = plt.subplots(len(filas), ncols, figsize=(2.05 * ncols, 1.85 * len(filas)))
    titulos = ["VIS", "IR"] + [f"$m$ = {m:.4f}".replace(".", ",").rstrip("0").rstrip(",")
                               if m < 0.1 else f"$m$ = {m:.2f}".replace(".", ",")
                               for m in M_VER]

    for fila, (v, i) in enumerate(filas):
        imgs = [v, i] + [fuse_optimal(v, i, R, m, mode="sum") for m in M_VER]
        # fraccion de pixeles saturados en la fusion (indicador de realce excesivo)
        sat = [None, None] + [float(np.mean((f >= 0.999) | (f <= 0.001))) for f in imgs[2:]]
        for col in range(ncols):
            ax = axes[fila, col] if len(filas) > 1 else axes[col]
            ax.imshow(np.clip(imgs[col], 0, 1), cmap="gray", vmin=0, vmax=1)
            ax.set_xticks([]); ax.set_yticks([])
            for s in ax.spines.values():
                s.set_color("#8b1a1a" if col == 2 else "#bfbfbf")
                s.set_linewidth(1.4 if col == 2 else 0.6)
            if fila == 0:
                ax.set_title(titulos[col], fontsize=10,
                             color=("#8b1a1a" if col == 2 else "black"))
            if sat[col] is not None and sat[col] > 0.005:
                ax.set_xlabel(f"saturado {sat[col] * 100:.1f}%".replace(".", ","),
                              fontsize=7.5, color="#8b1a1a", labelpad=1.5)

    fig.suptitle("Propuesta (r = 25) con distintos pesos de contraste $m$ — "
                 "en rojo la configuración óptima de $F_o$", fontsize=11, y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.975], h_pad=0.5, w_pad=0.3)
    salida = os.path.join(FIG, "fig_comparativa_m.png")
    fig.savefig(salida, dpi=170, facecolor="white")
    plt.close(fig)
    print("ok", salida)


if __name__ == "__main__":
    main()
