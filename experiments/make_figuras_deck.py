# -*- coding: utf-8 -*-
"""Graficos embebidos en el deck de defensa, generados desde los CSV.

Los tres graficos venian incrustados en el pptx sin generador, de modo que
quedaron con las cifras de una corrida anterior. Este script los reproduce a
partir de experiments/results/metrics_reports/ para que no vuelva a pasar.

Salidas (docs/figures/):
  fig_deck_llvip_map.png     barras de mAP@0,5 por modalidad (LLVIP)
  fig_deck_m3fd_clases.png   barras agrupadas AP People / AP Lamp (M3FD)
  fig_deck_pso_barrido.png   matriz de aptitud F_o del barrido n x T

Uso: python experiments/make_figuras_deck.py
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
GRANATE_CLARO = "#e79a9a"
OSCURO = "#404040"
GRIS = "#a6a6a6"
DPI = 150

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif", "Times New Roman"],
    "axes.grid": True,
    "grid.color": "#dddddd",
    "grid.linewidth": 0.7,
    "axes.axisbelow": True,
})

# etiquetas cortas usadas en el deck
CORTO = {
    "VIS": "VIS\n(solo)", "IR": "IR\n(solo)", "PiramideLaplace": "LP",
    "RatioPiramide": "RP", "DWT": "DWT", "DTCWT": "DTCWT", "Curvelet": "CVT",
    "TopHat_Clasico": "TH\nclásico", "Propuesta_Novedosa": "Propuesta",
}
ORDEN = ["VIS", "IR", "PiramideLaplace", "RatioPiramide", "DWT", "DTCWT",
         "Curvelet", "TopHat_Clasico", "Propuesta_Novedosa"]


def coma(v, nd=3):
    return f"{v:.{nd}f}".replace(".", ",")


def color_de(clave):
    if clave == "Propuesta_Novedosa":
        return GRANATE
    return OSCURO if clave in ("VIS", "IR") else GRIS


# --------------------------------------------------------------- 1. LLVIP
def llvip():
    d = pd.read_csv(REP / "detection_llvip_map.csv").set_index("method")
    faltan = [k for k in ORDEN if k not in d.index]
    assert not faltan, f"faltan entradas en el CSV de LLVIP: {faltan}"
    v = [float(d.loc[k, "mAP50"]) for k in ORDEN]

    fig, ax = plt.subplots(figsize=(1535 / DPI, 682 / DPI), dpi=DPI)
    barras = ax.bar(range(len(ORDEN)), v,
                    color=[color_de(k) for k in ORDEN], width=0.62)
    for b, val in zip(barras, v):
        ax.text(b.get_x() + b.get_width() / 2, val + 0.004, coma(val),
                ha="center", va="bottom", fontsize=11)
    lo = min(0.75, np.floor(min(v) * 20) / 20)
    ax.set_ylim(lo, 1.0)
    ax.set_xticks(range(len(ORDEN)))
    ax.set_xticklabels([CORTO[k] for k in ORDEN], fontsize=11)
    ax.set_ylabel("mAP@0,5", fontsize=12)
    ax.set_title("Detección de peatones en LLVIP — YOLOv8n reentrenado por modalidad",
                 fontsize=13)
    ax.set_axisbelow(True)
    ax.xaxis.grid(False)
    fig.tight_layout()
    out = FIG / "fig_deck_llvip_map.png"
    fig.savefig(out, dpi=DPI)
    plt.close(fig)
    print(f"Guardado: {out}  (IR {coma(d.loc['IR','mAP50'])}, "
          f"propuesta {coma(d.loc['Propuesta_Novedosa','mAP50'])})")


# ---------------------------------------------------------------- 2. M3FD
def m3fd():
    d = pd.read_csv(REP / "detection_m3fd_map.csv").set_index("method")
    faltan = [k for k in ORDEN if k not in d.index]
    assert not faltan, f"faltan entradas en el CSV de M3FD: {faltan}"
    pe = [float(d.loc[k, "AP50_People"]) for k in ORDEN]
    la = [float(d.loc[k, "AP50_Lamp"]) for k in ORDEN]
    # el maximo de cada clase se declara en la leyenda: verificarlo, no suponerlo
    max_pe = ORDEN[int(np.argmax(pe))]
    max_la = ORDEN[int(np.argmax(la))]

    x = np.arange(len(ORDEN))
    an = 0.36
    fig, ax = plt.subplots(figsize=(1519 / DPI, 661 / DPI), dpi=DPI)
    c_pe = [GRANATE if k == "Propuesta_Novedosa" else OSCURO for k in ORDEN]
    c_la = [GRANATE_CLARO if k == "Propuesta_Novedosa" else GRIS for k in ORDEN]
    def llano(clave):
        return CORTO[clave].replace("\n(solo)", "").replace("\n", " ")

    ax.bar(x - an / 2, pe, an, color=c_pe,
           label=f"AP@0,5 People — máx.: {llano(max_pe)}")
    ax.bar(x + an / 2, la, an, color=c_la,
           label=f"AP@0,5 Lamp — máx.: {llano(max_la)}")
    ax.set_xticks(x)
    ax.set_xticklabels([CORTO[k].replace("\n(solo)", "").replace("\n", " ")
                        for k in ORDEN], fontsize=11)
    ax.set_ylabel("AP@0,5", fontsize=12)
    ax.set_ylim(0, max(max(pe), max(la)) * 1.22)
    ax.set_title("M3FD — clases complementarias con un detector único VIS+IR",
                 fontsize=13)
    ax.legend(fontsize=10, framealpha=1.0)
    ax.xaxis.grid(False)
    fig.tight_layout()
    out = FIG / "fig_deck_m3fd_clases.png"
    fig.savefig(out, dpi=DPI)
    plt.close(fig)
    print(f"Guardado: {out}  (People máx. {max_pe}, Lamp máx. {max_la})")


# ----------------------------------------------------------------- 3. PSO
def pso():
    d = pd.read_csv(REP / "pso_grid_search_fo_propuesta.csv")
    assert set(d.m_opt.unique()) == {0.30}, \
        f"el barrido no es el del rango restringido: {sorted(d.m_opt.unique())}"
    piv = d.pivot(index="n", columns="Tmax", values="Fo_opt")
    ns = list(piv.index)
    ts = list(piv.columns)
    mejor = float(piv.values.max())

    fig, ax = plt.subplots(figsize=(961 / DPI, 618 / DPI), dpi=DPI)
    for i, nn in enumerate(ns):
        for j, tt in enumerate(ts):
            val = float(piv.loc[nn, tt])
            es_max = abs(val - mejor) < 1e-9
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                       facecolor="#d9d9d9" if es_max else "#f7f7f7",
                                       edgecolor="white", linewidth=1.5))
            ax.text(j, i, coma(val, 4), ha="center", va="center",
                    fontsize=11, color=GRANATE if es_max else "#202020",
                    fontweight="bold" if es_max else "normal")
    ax.set_xlim(-0.5, len(ts) - 0.5)
    ax.set_ylim(len(ns) - 0.5, -0.5)
    ax.set_xticks(range(len(ts)))
    ax.set_xticklabels([f"T={t}" for t in ts], fontsize=11)
    ax.set_yticks(range(len(ns)))
    ax.set_yticklabels([f"n={n}" for n in ns], fontsize=11)
    ax.set_title("Barrido PSO (rango publicado): todas convergen a m* = 0,30",
                 fontsize=13)
    ax.grid(False)
    for lado in ax.spines.values():
        lado.set_visible(False)
    ax.tick_params(length=0)
    fig.tight_layout()
    out = FIG / "fig_deck_pso_barrido.png"
    fig.savefig(out, dpi=DPI)
    plt.close(fig)
    r1 = d.loc[d.r_opt == 1, "Fo_opt"].max()
    r25 = d.loc[d.r_opt == 25, "Fo_opt"].max()
    print(f"Guardado: {out}  (mejor {coma(mejor,4)}; r=1 -> {coma(r1,4)}, "
          f"r=25 -> {coma(r25,4)}; r=1 en {(d.r_opt==1).sum()}/25 celdas)")


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    llvip()
    m3fd()
    pso()
