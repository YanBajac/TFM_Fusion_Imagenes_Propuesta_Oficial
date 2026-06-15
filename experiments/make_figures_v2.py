"""Genera figuras actualizadas: boxplots de metricas de calidad, ranking
global con 12 metricas, y efecto del Black Top-Hat."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
MDIR = ROOT / "experiments" / "results" / "metrics_reports"
FIG = ROOT / "docs" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", context="notebook")

df = pd.read_csv(MDIR / "all_metrics.csv")
rank = pd.read_csv(MDIR / "ranking_methods.csv", index_col=0)

# Etiquetas cortas
short = {
    "Promedio": "Promedio", "PiramideLaplace": "Laplace", "Curvelet": "Curvelet",
    "TopHat_disk_L3": "TH disk L3", "TopHat_square_L3": "TH square L3",
    "TopHat_cross_L3": "TH cross L3", "TopHat_disk_L5": "TH disk L5",
    "TopHat_disk_L3_BTH": "TH disk L3 +BTH", "TopHat_square_L3_BTH": "TH square L3 +BTH",
    "TopHat_cross_L3_BTH": "TH cross L3 +BTH", "TopHat_disk_L5_BTH": "TH disk L5 +BTH",
}

# --- Fig 1: boxplots de las metricas estandar de calidad de fusion ----------
subset = ["Promedio", "Curvelet", "PiramideLaplace", "TopHat_disk_L5", "TopHat_disk_L5_BTH"]
dsub = df[df.method.isin(subset)].copy()
dsub["m"] = dsub.method.map(short)
order = [short[s] for s in subset]
qual = ["Qabf", "Nabf", "SSIM", "SCD", "VIF", "SF"]
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for ax, met in zip(axes.ravel(), qual):
    sns.boxplot(data=dsub, x="m", y=met, order=order, ax=ax,
                palette="Set2", width=0.6)
    arrow = "menor=mejor" if met == "Nabf" else "mayor=mejor"
    ax.set_title(f"{met}  ({arrow})", fontsize=12, weight="bold")
    ax.set_xlabel(""); ax.set_ylabel("")
    ax.tick_params(axis="x", rotation=25, labelsize=9)
fig.suptitle("Metricas estandar de calidad de fusion por metodo (n = 20 pares)",
             fontsize=14, weight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.97])
fig.savefig(FIG / "fig_boxplot_metricas_calidad.png", dpi=150)
plt.close(fig)

# --- Fig 2: ranking global con 12 metricas ----------------------------------
rk = rank["avg_rank"].sort_values(ascending=True)
labels = [short.get(i, i) for i in rk.index]
colors = ["#c0392b" if "BTH" in i else ("#2c3e50" if i.startswith("TopHat") else "#7f8c8d")
          for i in rk.index]
colors = []
for i in rk.index:
    if i == "PiramideLaplace": colors.append("#2980b9")
    elif "BTH" in i: colors.append("#e67e22")
    elif i.startswith("TopHat"): colors.append("#27ae60")
    else: colors.append("#95a5a6")
fig, ax = plt.subplots(figsize=(9, 6))
ax.barh(labels[::-1], rk.values[::-1], color=colors[::-1])
for y, v in enumerate(rk.values[::-1]):
    ax.text(v + 0.05, y, f"{v:.2f}", va="center", fontsize=9)
ax.set_xlabel("Ranking promedio sobre 12 metricas (menor = mejor)")
ax.set_title("Ranking global por metodo (12 metricas, direccion corregida)",
             weight="bold")
fig.tight_layout()
fig.savefig(FIG / "fig_ranking_global_12metricas.png", dpi=150)
plt.close(fig)

# --- Fig 3: efecto del Black Top-Hat (WTH vs WTH+BTH, pares disk) ------------
pairs = [("TopHat_disk_L3", "TopHat_disk_L3_BTH"),
         ("TopHat_disk_L5", "TopHat_disk_L5_BTH")]
mets = ["EN", "SD", "SF", "MG", "Qabf", "Nabf", "SSIM", "VIF", "MI_vis"]
means = df.groupby("method")[mets].mean()
fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
for ax, (wth, bth) in zip(axes, pairs):
    # cambio relativo (%) de BTH respecto a WTH
    rel = (means.loc[bth] - means.loc[wth]) / means.loc[wth].abs() * 100
    cols = ["#27ae60" if (v >= 0) != (m == "Nabf") else "#c0392b"
            for m, v in rel.items()]
    # interpretacion: verde = mejora; rojo = empeora (Nabf invertido)
    cols = []
    for m, v in rel.items():
        better = (v < 0) if m == "Nabf" else (v > 0)
        cols.append("#27ae60" if better else "#c0392b")
    ax.bar(mets, rel.values, color=cols)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_title(f"Efecto de +BTH sobre {short[wth]}", weight="bold")
    ax.set_ylabel("Cambio relativo (%)")
    ax.tick_params(axis="x", rotation=35, labelsize=9)
fig.suptitle("Impacto de agregar Black Top-Hat: gana contraste/actividad (EN,SD,SF,MG) "
             "pero degrada calidad (Qabf,SSIM,VIF,MI) y dispara artefactos (Nabf)",
             fontsize=11, weight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(FIG / "fig_efecto_black_top_hat.png", dpi=150)
plt.close(fig)

print("Figuras generadas:")
for f in ["fig_boxplot_metricas_calidad.png", "fig_ranking_global_12metricas.png",
          "fig_efecto_black_top_hat.png"]:
    print("  ", FIG / f)
