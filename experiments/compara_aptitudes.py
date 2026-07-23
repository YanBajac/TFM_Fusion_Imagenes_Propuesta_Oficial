# -*- coding: utf-8 -*-
"""Comparacion en paralelo de las dos funciones de aptitud sobre el MISMO operador
(Top-Hat de una escala con suma de ramas), cada una con su optimo de PSO:

  - F_o  (Ortega y Espinoza, publicada, rango publicado m in [0.3,2.0]) -> r=1,  m=0.30
  - F_apt (propuesta, orientada a fusion)                               -> r=25, m=0.0703

Produce:
  1) docs/figures/comparacion_aptitudes.png  (cualitativo: 3 escenas x VIS/IR/F_o/F_apt)
  2) metrics_reports/comparacion_aptitudes.csv (cuantitativo: 12 metricas, ambos optimos)
  3) metrics_reports/comparacion_aptitudes_wilcoxon.csv (Wilcoxon pareado F_apt vs F_o, 20 pares)

Uso:  python experiments/compara_aptitudes.py
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, ".")
from src.datasets import list_pairs, load_pair
from src.fusion import fuse_optimal
from src.metrics import evaluate_all, METRIC_DIRECTION
from scipy.stats import wilcoxon
import pandas as pd

FO = dict(r=1, m=0.30, tag="F_o (r=1, m=0,30)")        # publicada, rango publicado
FAPT = dict(r=25, m=0.0703, tag="F_apt (r=25, m=0,070)")  # propuesta
MR = "experiments/results/metrics_reports"
COLS = ["EN", "SD", "FE", "MG", "MI_vis", "MI_ir", "SF", "Qabf", "Nabf", "SSIM", "SCD", "VIF"]

# ----------------------------------------------------------- 1. cuantitativo (20 pares)
pares = list(list_pairs())
filas_fo, filas_fapt = [], []
for k, (vp, ip) in enumerate(pares, 1):
    v, i = load_pair(vp, ip)
    m_fo = evaluate_all(fuse_optimal(v, i, FO["r"], FO["m"], mode="sum"), v, i)
    m_ap = evaluate_all(fuse_optimal(v, i, FAPT["r"], FAPT["m"], mode="sum"), v, i)
    m_fo["image"] = m_ap["image"] = k
    filas_fo.append(m_fo); filas_fapt.append(m_ap)
    print(f"par {k:02d}/20 ok", flush=True)

df_fo = pd.DataFrame(filas_fo); df_ap = pd.DataFrame(filas_fapt)
comp = pd.DataFrame({"metrica": COLS,
                     "F_o (r=1, m=0,30)": [df_fo[c].mean() for c in COLS],
                     "F_apt (r=25, m=0,070)": [df_ap[c].mean() for c in COLS]})
comp["direccion"] = [("mayor" if METRIC_DIRECTION.get(c, "max") == "max" else "menor") + " mejor" for c in COLS]
comp.round(4).to_csv(os.path.join(MR, "comparacion_aptitudes.csv"), index=False)

# Wilcoxon pareado F_apt vs F_o sobre los 20 pares
w_rows = []
for c in COLS:
    a, b = df_ap[c].to_numpy(), df_fo[c].to_numpy()
    try:
        stat, p = wilcoxon(a, b)
    except ValueError:
        stat, p = float("nan"), 1.0
    mejor_ap = (a.mean() > b.mean()) if METRIC_DIRECTION.get(c, "max") == "max" else (a.mean() < b.mean())
    w_rows.append(dict(metrica=c, media_Fapt=round(a.mean(), 4), media_Fo=round(b.mean(), 4),
                       p_value=round(float(p), 4), Fapt_mejor=bool(mejor_ap),
                       significativo=bool(p < 0.05)))
wdf = pd.DataFrame(w_rows)
wdf.to_csv(os.path.join(MR, "comparacion_aptitudes_wilcoxon.csv"), index=False)
print("\n=== medias (20 pares) ===")
print(comp.round(3).to_string(index=False))
n_sig = int((wdf["significativo"] & wdf["Fapt_mejor"]).sum())
print(f"\nWilcoxon: F_apt mejor y significativo en {n_sig}/12 metricas")

# ----------------------------------------------------------- 2. cualitativo (3 escenas)
IDX = [1, 7, 16]  # escenas representativas
GRANATE = "#c00000"
plt.rcParams.update({"font.family": "serif"})
fig, axes = plt.subplots(len(IDX), 4, figsize=(13.0, 3.15 * len(IDX)),
                         gridspec_kw={"hspace": 0.14, "wspace": 0.04})
COLTIT = ["VIS", "IR", f"Propuesta · {FO['tag']}", f"Propuesta · {FAPT['tag']}"]
for fila, idx in enumerate(IDX):
    vp, ip = pares[idx]
    v, i = load_pair(vp, ip)
    stem = os.path.splitext(os.path.basename(str(vp)))[0]
    imgs = [v, i,
            fuse_optimal(v, i, FO["r"], FO["m"], mode="sum"),
            fuse_optimal(v, i, FAPT["r"], FAPT["m"], mode="sum")]
    for col, (img, tit) in enumerate(zip(imgs, COLTIT)):
        ax = axes[fila, col] if len(IDX) > 1 else axes[col]
        ax.imshow(np.clip(img, 0, 1), cmap="gray", vmin=0, vmax=1)
        es_ap = col == 3
        if fila == 0:
            ax.set_title(tit, fontsize=10.5, color=(GRANATE if es_ap else "black"),
                         fontweight=("bold" if es_ap else "normal"))
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_edgecolor(GRANATE if es_ap else "#555555")
            sp.set_linewidth(2.0 if es_ap else 0.6)
    (axes[fila, 0] if len(IDX) > 1 else axes[0]).set_ylabel(f"Escena {stem[:16]}", fontsize=9)
fig.suptitle("Efecto de la aptitud sobre el mismo operador — F_apt: más limpia y estructural; "
             "F_o: más actividad de alta frecuencia",
             fontsize=11.5, y=0.995)
fig.tight_layout(rect=[0, 0, 1, 0.97])
out = "docs/figures/comparacion_aptitudes.png"
fig.savefig(out, dpi=160, bbox_inches="tight", facecolor="white")
print("Guardado:", out, "y comparacion_aptitudes.csv / _wilcoxon.csv")
