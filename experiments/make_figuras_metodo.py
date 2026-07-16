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

# ---------------- fig_flujo_propuesta: flujograma de la Propuesta Novedosa ----------------
from matplotlib.patches import FancyArrowPatch, Rectangle

BORDE = "#3a3a3a"
ACENTO = "#8b1a1a"
RELLENO = "#f5f5f5"

def caja(ax, cx, cy, w, h, texto, borde=BORDE, lw=0.9, fill="white",
         bold=False, dashed=False, fs=9.3):
    r = Rectangle((cx - w / 2, cy - h / 2), w, h, facecolor=fill, edgecolor=borde,
                  linewidth=lw, linestyle="--" if dashed else "-", zorder=2)
    ax.add_patch(r)
    ax.text(cx, cy, texto, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", color="#1a1a1a", zorder=3)

def flecha(ax, x0, y0, x1, y1, dashed=False):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                 mutation_scale=11, linewidth=1.0, color="#4d4d4d",
                 linestyle="--" if dashed else "-", zorder=1))

fig = plt.figure(figsize=(7.7, 9.97))
ax = fig.add_axes([0.005, 0.005, 0.99, 0.99])
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

for cx, lab in ((26, "Imagen VIS"), (74, "Imagen IR")):
    caja(ax, cx, 96, 30, 5.0, lab, bold=True, fill=RELLENO)
    caja(ax, cx, 87, 44, 7.0, "Banco de 5 SE (radio $r$):\ndisco + 4 líneas (0°/45°/90°/135°)")
    caja(ax, cx, 76, 44, 7.0, "WTH/BTH de líneas → promedio (ec. 7)\nWTH/BTH del disco (ec. 8)")
    caja(ax, cx, 65, 44, 7.0, "Suma de ramas (ec. 9):\n$W_{opt}=WTH_{lin}+WTH_{disco}$ · ídem $B_{opt}$",
         borde=ACENTO, lw=1.3)
    flecha(ax, cx, 93.4, cx, 90.6)
    flecha(ax, cx, 83.4, cx, 79.6)
    flecha(ax, cx, 72.4, cx, 68.6)

caja(ax, 50, 53, 82, 7.5, "Combinación entre fuentes — máximo por píxel (ec. 10)\n"
     "$W_F=\\max(W_{opt}^{VIS},\\;W_{opt}^{IR})$ ;  $B_F=\\max(B_{opt}^{VIS},\\;B_{opt}^{IR})$")
flecha(ax, 26, 61.4, 42, 57.0)
flecha(ax, 74, 61.4, 58, 57.0)

caja(ax, 50, 42.5, 52, 5.5, "Imagen base  $I_{base}=(VIS+IR)/2$")
flecha(ax, 50, 49.1, 50, 45.4)

caja(ax, 50, 31.5, 62, 8.0, "Reconstrucción ponderada (ec. 11)\n"
     "$F = I_{base} + m\cdot W_F - m\cdot B_F$", borde=ACENTO, lw=1.3,
     fill=RELLENO, bold=True)
flecha(ax, 50, 39.7, 50, 35.7)

caja(ax, 50, 19.5, 64, 5.5, "PSO ajusta $(r, m)$: barrido 5×5 → $r=25$;  $m=0{,}0703$",
     dashed=True, fs=9.2)
flecha(ax, 50, 27.4, 50, 22.4, dashed=True)

caja(ax, 50, 8.5, 34, 5.5, "Imagen fusionada $F$", bold=True, fill=RELLENO)
flecha(ax, 50, 16.6, 50, 11.4)

fig.savefig(os.path.join(OUT, "fig_flujo_propuesta.png"), dpi=170,
            facecolor="white")
plt.close(fig)
print("ok fig_flujo_propuesta.png")

# ---------------- fig_pso_diagrama: PSO sobre el espacio (r, m) ----------------
rr = np.linspace(1, 25, 240)
mm = np.linspace(0.05, 1.20, 240)
RR, MM = np.meshgrid(rr, mm)
Z = 1.9843 - 0.55 * ((25 - RR) / 24) ** 2 - 0.75 * ((MM - 0.0703) / 1.13) ** 2

fig, ax = plt.subplots(figsize=(8.3, 5.0))
cf = ax.contourf(RR, MM, Z, levels=14, cmap="Greys", alpha=0.45)
ax.contour(RR, MM, Z, levels=14, colors="#999999", linewidths=0.4)

px = np.array([3.0, 5.5, 8.0, 10.5, 13.0, 15.5, 18.0, 20.0, 22.0, 6.5])
py = np.array([1.00, 0.62, 0.88, 0.38, 0.72, 0.25, 0.55, 0.90, 0.33, 0.18])
for x, y in zip(px, py):
    dx, dy = (25 - x) * 0.22, (0.0703 - y) * 0.22
    ax.annotate("", xy=(x + dx, y + dy), xytext=(x, y),
                arrowprops=dict(arrowstyle="->", lw=0.9, color="#4d4d4d"))
ax.plot(px, py, "o", ms=5, color="#1a1a1a", label="Partículas (iteración $t$)")
ax.plot(6.5, 0.18, "o", ms=8, color="#1f5c2e")
ax.text(6.9, 0.115, "pbest (mejor propia)", fontsize=9, color="#1f5c2e")
ax.plot(25, 0.0703, "*", ms=17, color="#8b1a1a", zorder=5, clip_on=False)
ax.text(24.4, 0.155, "gbest = óptimo global\n($r=25$;  $m=0{,}0703$)", fontsize=9.5,
        color="#8b1a1a", fontweight="bold", ha="right")
ax.set_xlim(1, 25); ax.set_ylim(0.05, 1.20)
ax.set_xlabel("$r$  —  radio del elemento estructurante")
ax.set_ylabel("$m$  —  peso de contraste")
ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
ax.grid(False)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig_pso_diagrama.png"), dpi=170, facecolor="white")
plt.close(fig)
print("ok fig_pso_diagrama.png")
