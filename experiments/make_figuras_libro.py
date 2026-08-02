# -*- coding: utf-8 -*-
"""Figuras de datos del libro (Figuras 7, 8, 10 y 11), generadas desde los CSV.

Estas cuatro figuras estaban incrustadas en el docx sin generador y quedaron con
las cifras de corridas anteriores; la Figura 8 llegaba a contradecir el texto
(mostraba la pirámide de Laplace primera) y la Figura 10 mostraba a la propuesta
con el mejor SSIM cuando hoy tiene el peor. Este script las reproduce desde
experiments/results/metrics_reports/ para que no vuelva a ocurrir.

Salidas (docs/figures/):
  fig_libro_boxplots.png    Figura 7  — cajas de seis metricas por metodo
  fig_libro_ranking.png     Figura 8  — rango medio global por metodo
  fig_libro_propuesta_vs.png Figura 10 — propuesta vs clasico y estado del arte
  fig_libro_pso.png         Figura 11 — aptitud vs m y matriz del barrido

Uso: python experiments/make_figuras_libro.py
"""
import os
import sys
from pathlib import Path

os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, ".")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REP = Path("experiments/results/metrics_reports")
FIG = Path("docs/figures")
GRANATE = "#c00000"
GRIS = "#bfbfbf"
AZUL = "#1f4e79"
DPI = 150

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif", "Times New Roman"],
    "font.size": 11,
    "axes.grid": True,
    "grid.color": "#e6e6e6",
    "grid.linewidth": 0.7,
    "axes.axisbelow": True,
})

CORTO = {"PiramideLaplace": "LP", "RatioPiramide": "RP", "DWT": "DWT",
         "DTCWT": "DTCWT", "Curvelet": "CVT", "TopHat_Clasico": "TH clásico",
         "Propuesta_Novedosa": "Propuesta"}
ORDEN = ["PiramideLaplace", "RatioPiramide", "DWT", "DTCWT", "Curvelet",
         "TopHat_Clasico", "Propuesta_Novedosa"]


def coma(v, nd=3):
    return f"{v:.{nd}f}".replace(".", ",")


# --------------------------------------------- Figura 7: cajas por metrica
def boxplots():
    a = pd.read_csv(REP / "all_metrics.csv")
    M = ["SSIM", "SF", "EN", "SD", "MI_ir", "PSNR"]
    faltan = [m for m in M if m not in a.columns]
    assert not faltan, f"faltan metricas en all_metrics.csv: {faltan}"
    for m in M:
        assert np.isfinite(a[m]).all(), f"{m} tiene valores no finitos"

    fig, axes = plt.subplots(2, 3, figsize=(2250 / DPI, 1200 / DPI), dpi=DPI)
    for ax, m in zip(axes.ravel(), M):
        datos = [a.loc[a.method == k, m].to_numpy() for k in ORDEN]
        bp = ax.boxplot(datos, patch_artist=True, widths=0.62,
                        medianprops=dict(color="black", linewidth=1.6),
                        flierprops=dict(marker="o", markersize=3.5,
                                        markerfacecolor="none",
                                        markeredgecolor="#999999"))
        for caja, k in zip(bp["boxes"], ORDEN):
            caja.set_facecolor(GRANATE if k == "Propuesta_Novedosa" else GRIS)
            caja.set_edgecolor("#555555")
        ax.set_title(f"{m} ↑", fontsize=13)
        ax.set_xticklabels([CORTO[k] for k in ORDEN], rotation=30, ha="right",
                           fontsize=10)
        ax.xaxis.grid(False)
    fig.tight_layout()
    out = FIG / "fig_libro_boxplots.png"
    fig.savefig(out, dpi=DPI, facecolor="white")
    plt.close(fig)
    print(f"Guardado: {out}  (PSNR max {a.PSNR.max():.2f}, SSIM max {a.SSIM.max():.4f})")


# ---------------------------------------------- Figura 8: rango medio global
def ranking():
    rk = pd.read_csv(REP / "ranking_methods.csv", index_col=0)["avg_rank"]
    rk = rk.sort_values()
    primero = rk.index[0]
    assert primero == "Propuesta_Novedosa", \
        f"el primer puesto es {primero}; revisar antes de publicar la figura"

    fig, ax = plt.subplots(figsize=(1350 / DPI, 900 / DPI), dpi=DPI)
    y = np.arange(len(rk))[::-1]
    col = [GRANATE if k == "Propuesta_Novedosa" else GRIS for k in rk.index]
    ax.barh(y, rk.values, color=col, edgecolor="#555555", height=0.66)
    for yy, v, k in zip(y, rk.values, rk.index):
        ax.text(v + 0.06, yy, coma(v, 2), va="center", fontsize=11,
                fontweight="bold" if k == "Propuesta_Novedosa" else "normal")
    ax.set_yticks(y)
    ax.set_yticklabels([CORTO[k] for k in rk.index], fontsize=11)
    ax.set_xlim(0, max(rk.values) * 1.18)
    ax.set_xlabel("Rango promedio sobre las nueve métricas (1 = mejor)", fontsize=12)
    ax.yaxis.grid(False)
    fig.tight_layout()
    out = FIG / "fig_libro_ranking.png"
    fig.savefig(out, dpi=DPI, facecolor="white")
    plt.close(fig)
    print(f"Guardado: {out}  (1.o {CORTO[primero]} {coma(rk.iloc[0],3)}, "
          f"2.o {CORTO[rk.index[1]]} {coma(rk.iloc[1],3)})")


# ------------------------- Figura 10: propuesta vs clasico y estado del arte
def propuesta_vs():
    dm = pd.read_csv(REP / "descriptive_means.csv").set_index("method")
    # las mismas cinco metricas de la Tabla 10, mas SSIM para mostrar donde cede
    M = ["EN", "FE", "SD", "MG", "SF", "SSIM"]
    METODOS = ["Propuesta_Novedosa", "TopHat_Clasico", "PiramideLaplace",
               "RatioPiramide", "DTCWT"]
    ETQ = {"Propuesta_Novedosa": "Propuesta", "TopHat_Clasico": "TH clásico",
           "PiramideLaplace": "LP", "RatioPiramide": "RP", "DTCWT": "DTCWT"}

    fig, axes = plt.subplots(2, 3, figsize=(1254 / DPI * 1.6, 693 / DPI * 1.6),
                             dpi=DPI)
    for ax, m in zip(axes.ravel(), M):
        v = [float(dm.loc[k, m]) for k in METODOS]
        col = [GRANATE if k == "Propuesta_Novedosa" else GRIS for k in METODOS]
        ax.bar(range(len(METODOS)), v, color=col, edgecolor="#555555", width=0.66)
        nd = 4 if max(v) < 1 else (2 if max(v) > 10 else 3)
        for i, val in enumerate(v):
            ax.text(i, val + max(v) * 0.02, coma(val, nd), ha="center",
                    va="bottom", fontsize=9)
        lider = METODOS[int(np.argmax(v))]
        ax.set_title(f"{m} ↑   (máx.: {ETQ[lider]})", fontsize=12)
        ax.set_ylim(0, max(v) * 1.20)
        ax.set_xticks(range(len(METODOS)))
        ax.set_xticklabels([ETQ[k] for k in METODOS], rotation=25, ha="right",
                           fontsize=9)
        ax.xaxis.grid(False)
    fig.tight_layout()
    out = FIG / "fig_libro_propuesta_vs.png"
    fig.savefig(out, dpi=DPI, facecolor="white")
    plt.close(fig)
    peor = min(METODOS, key=lambda k: float(dm.loc[k, "SSIM"]))
    print(f"Guardado: {out}  (SSIM mas bajo de los cinco: {ETQ[peor]} "
          f"{coma(dm.loc[peor,'SSIM'],4)})")


# ---------------------------- Figura 11: aptitud vs m y matriz del barrido
def pso():
    cur = pd.read_csv(REP / "curva_aptitud_vs_m.csv")
    d = pd.read_csv(REP / "pso_grid_search_fo_propuesta.csv")
    assert set(d.m_opt.unique()) == {0.30}, "el barrido no es el del rango restringido"
    piv = d.pivot(index="n", columns="Tmax", values="Fo_opt")
    mejor = float(piv.values.max())
    # coherencia entre la curva y el barrido: F_o(r=25, m=0,30) debe coincidir
    fo_r25 = float(d.loc[d.r_opt == 25, "Fo_opt"].max())
    en_curva = float(cur.loc[np.isclose(cur.m, 0.30), "Fo_propuesta"].iloc[0])
    assert abs(fo_r25 - en_curva) < 5e-4, (
        f"la curva da F_o(m=0,30) = {en_curva:.4f} y el barrido {fo_r25:.4f}: "
        "re-genera curva_aptitud_vs_m.csv antes de dibujar")

    fig, (izq, der) = plt.subplots(1, 2, figsize=(1245 / DPI * 1.7,
                                                  459 / DPI * 1.7), dpi=DPI)
    izq.plot(cur.m, cur.Fo_propuesta, marker="o", ms=4.5, color=AZUL, lw=1.8)
    izq.axvspan(0.30, 2.00, color="#f0f0f0", zorder=0)
    izq.axvline(0.30, color="#555555", ls=":", lw=1.2)
    izq.plot([0.30], [en_curva], marker="o", ms=11, mfc="none",
             mec=GRANATE, mew=2.0)
    izq.annotate(f"m* = 0,30\n(piso del rango publicado)\nF$_o$ = {coma(en_curva,4)}",
                 xy=(0.30, en_curva), xytext=(0.62, en_curva + 0.015),
                 fontsize=9, color=GRANATE,
                 arrowprops=dict(arrowstyle="-", color=GRANATE, lw=1.0))
    izq.text(0.98, 0.97, "rango publicado\n$m \\in [0,30;\\ 2,00]$",
             transform=izq.transAxes, ha="right", va="top", fontsize=9,
             color="#777777")
    izq.set_xlabel("Peso de contraste  $m$", fontsize=11)
    izq.set_ylabel("Aptitud  F$_o$", fontsize=11)
    izq.set_title("Aptitud F$_o$ frente al peso de contraste (r = 25)", fontsize=12)

    ns, ts = list(piv.index), list(piv.columns)
    for i, nn in enumerate(ns):
        for j, tt in enumerate(ts):
            val = float(piv.loc[nn, tt])
            es_max = abs(val - mejor) < 1e-9
            der.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                        facecolor=AZUL if es_max else "#dce6f1",
                                        edgecolor="white", linewidth=1.6))
            der.text(j, i, coma(val, 4), ha="center", va="center", fontsize=9,
                     color="white" if es_max else "#202020",
                     fontweight="bold" if es_max else "normal")
    der.set_xlim(-0.5, len(ts) - 0.5)
    der.set_ylim(len(ns) - 0.5, -0.5)
    der.set_xticks(range(len(ts)))
    der.set_xticklabels([f"T={t}" for t in ts], fontsize=10)
    der.set_yticks(range(len(ns)))
    der.set_yticklabels([f"n={n}" for n in ns], fontsize=10)
    der.set_title("Barrido de 25 configuraciones ($m^*$ = 0,30 en todas)", fontsize=12)
    der.grid(False)
    for lado in der.spines.values():
        lado.set_visible(False)
    der.tick_params(length=0)
    fig.tight_layout()
    out = FIG / "fig_libro_pso.png"
    fig.savefig(out, dpi=DPI, facecolor="white")
    plt.close(fig)
    print(f"Guardado: {out}  (F_o en m=0,30 -> {coma(en_curva,4)}; "
          f"mejor del barrido {coma(mejor,4)})")


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    boxplots()
    ranking()
    propuesta_vs()
    pso()
