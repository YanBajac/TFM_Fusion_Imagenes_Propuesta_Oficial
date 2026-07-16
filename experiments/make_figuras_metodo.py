# -*- coding: utf-8 -*-
"""Figuras del metodo para informes y presentacion (operador con SUMA de ramas).
Genera docs/figures/fig_cinco_se.png (banco de SE + combinacion por suma) y
docs/figures/ejemplo_modalidades.png (VIS | IR | Top-Hat clasico | Propuesta).
Uso: python experiments/make_figuras_metodo.py (desde la raiz del repo)."""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, ".")
from src.datasets import list_pairs, load_pair
from src.fusion import fuse_optimal, tophat_classic_fusion
from src.fusion.optimal_top_hat import disk_se, linear_se

PROP_R, PROP_M = 25, 0.0703
OUT = "docs/figures"
plt.rcParams.update({"font.family": "serif", "font.size": 10})

# ---------------- fig_cinco_se: banco de SE combinados por SUMA ----------------
R_VIS = 5  # radio ilustrativo (los SE reales usan r = 25)
ses = [("Disco $B_r$", disk_se(R_VIS))] + [
    (f"Línea {a}°", linear_se(R_VIS, a)) for a in (0, 45, 90, 135)]
suma = disk_se(R_VIS).astype(float) + sum(linear_se(R_VIS, a).astype(float)
                                          for a in (0, 45, 90, 135)) / 4.0

fig, axes = plt.subplots(1, 6, figsize=(11.6, 2.55))
for ax, (lab, se) in zip(axes[:5], ses):
    ax.imshow(se, cmap="Blues", vmin=0, vmax=1.4)
    ax.set_title(lab, fontsize=10)
    ax.set_xticks([]); ax.set_yticks([])
axes[4].annotate("", xy=(1.42, 0.5), xytext=(1.08, 0.5), xycoords="axes fraction",
                 arrowprops=dict(arrowstyle="->", lw=1.6, color="#8b1a1a"))
axes[4].text(1.25, 0.62, "suma", transform=axes[4].transAxes, ha="center",
             fontsize=10, color="#8b1a1a", fontweight="bold")
axes[5].imshow(suma, cmap="Reds", vmin=0, vmax=suma.max())
axes[5].set_title("Respuesta combinada", fontsize=10, color="#8b1a1a", fontweight="bold")
axes[5].set_xticks([]); axes[5].set_yticks([])
fig.suptitle("Banco de 5 elementos estructurantes (disco + 4 líneas) — respuestas lineales "
             "promediadas y sumadas a la del disco", fontsize=11, y=1.02)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig_cinco_se.png"), dpi=160, bbox_inches="tight",
            facecolor="white")
plt.close(fig)
print("ok fig_cinco_se.png")

# ---------------- ejemplo_modalidades: VIS | IR | clasico | propuesta ----------------
pares = list(list_pairs())
vp, ip = pares[6]  # escena 7: Athena, dos hombres frente a la casa
vis, ir = load_pair(vp, ip)
paneles = [
    ("VIS", vis),
    ("IR", ir),
    ("Top-Hat clásico (r=5, m=1)", tophat_classic_fusion(vis, ir, r=5)),
    (f"Propuesta (r={PROP_R}, m={PROP_M:.3f})".replace(".", ","),
     fuse_optimal(vis, ir, r=PROP_R, m=PROP_M, mode="sum")),
]
fig, axes = plt.subplots(1, 4, figsize=(13.6, 3.05))
stem = os.path.splitext(os.path.basename(str(vp)))[0]
for ax, (lab, img) in zip(axes, paneles):
    es_prop = lab.startswith("Propuesta")
    ax.imshow(np.clip(img, 0, 1), cmap="gray", vmin=0, vmax=1)
    ax.set_title(lab, fontsize=10.5, color="#c00000" if es_prop else "black",
                 fontweight="bold" if es_prop else "normal")
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_edgecolor("#c00000" if es_prop else "#555555")
        sp.set_linewidth(2.0 if es_prop else 0.6)
fig.suptitle(f"Escena: {stem.replace('_', ' ')}", fontsize=10, y=0.99, color="#555555")
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(OUT, "ejemplo_modalidades.png"), dpi=160, bbox_inches="tight",
            facecolor="white")
plt.close(fig)
print("ok ejemplo_modalidades.png")
