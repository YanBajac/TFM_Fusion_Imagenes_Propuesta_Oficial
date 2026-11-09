# -*- coding: utf-8 -*-
"""Figuras del libro, generadas desde los CSV del criterio de SEIS metricas.

Salidas, en docs/libro_v4/figuras/ para que viajen con el proyecto de LaTeX:
  fig_ranking_seis.png        rango promedio de las seis metricas, 7 metodos
  fig_metricas_seis.png       las seis metricas, media por metodo, un panel cada una

El libro solo usa fig_ranking_seis (cap4, fig:ranking_seis). Esa figura tiene la letra a su tamano real:
el lienzo mide 6.3 x 3.8 pulgadas, el ancho de la caja de texto del libro (160 mm), porque el LaTeX la
incluye con width=\\textwidth; asi los rotulos de 10 pt se imprimen a 10 pt. Va a 300 ppp, con el estilo
comun de las figuras del libro (experiments/estilo_figuras_libro.py): Times New Roman, la propuesta en
azul #4472c4 y el resto en gris, y los nombres de los metodos tomados de las tablas.

Sin argumentos solo rehace fig_ranking_seis, la que usa el libro; fig_metricas_seis se pide por
nombre y no esta ajustada al tamano de la pagina. Usa la paleta comun (la propuesta en azul).

Uso: .venv\\Scripts\\python.exe -X utf8 experiments/make_figuras_libro_v4.py [ranking_seis] [metricas_seis]
"""
import os
import sys
from pathlib import Path

os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, ".")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from estilo_figuras_libro import (ANCHO_TEXTO_PULG, GRIS_OSCURO, NOMBRES, TAM_TEXTO,
                                  aplicar_estilo, color_metodo, guardar)

REP = Path("experiments/results/metrics_reports")
FIG = Path("docs/libro_v4/figuras")
FIG.mkdir(parents=True, exist_ok=True)

DPI = 150                           # fig_metricas_seis, que el libro no usa
ANCHO_RANKING, ALTO_RANKING = ANCHO_TEXTO_PULG, 3.8
TAM_RANKING = TAM_TEXTO             # rotulos de los metodos, valores, marcas y nombre del eje

aplicar_estilo()

# Los mismos nombres que las tablas (tools/generar_tablas_libro.py, leidos por estilo_figuras_libro):
# el libro no define siglas para los metodos, y «Curvelet» es en realidad una DWT con base db4.
CORTO = NOMBRES
SEIS = ["EN", "SD", "MG", "MI", "SSIM", "PSNR"]
NOMBRE = {"EN": "Entropía", "SD": "Desviación estándar", "MG": "Gradiente medio",
          "MI": "Información mutua", "SSIM": "Similitud estructural",
          "PSNR": "Relación señal-ruido de pico"}


def num(v, nd=3):
    """Numero con punto decimal, como el texto y las tablas del libro."""
    return f"{v:.{nd}f}"


def color(k):
    return color_metodo(k)          # azul la propuesta, gris el resto


# ------------------------------------------- rango promedio de las seis metricas
def ranking_seis():
    tabla = pd.read_csv(REP / "ranking_seis_metricas.csv", index_col=0)
    # el rango de las seis es el promedio de los seis rangos por metrica: se lo recalcula
    recalc = tabla[SEIS].mean(axis=1).round(3)
    assert (recalc - tabla["rango_6"]).abs().max() < 1e-9, "rango_6 no es el promedio de las seis"
    rk = tabla["rango_6"].sort_values()
    primero = rk.index[0]
    assert primero == "Propuesta_Novedosa", \
        f"el primer puesto es {primero}; revisar el texto antes de publicar la figura"

    fig, ax = plt.subplots(figsize=(ANCHO_RANKING, ALTO_RANKING), layout="constrained")
    y = np.arange(len(rk))[::-1]
    ax.barh(y, rk.values, color=[color_metodo(k) for k in rk.index],
            edgecolor=GRIS_OSCURO, linewidth=0.6, height=0.66)
    for yy, v, k in zip(y, rk.values, rk.index):
        ax.text(v + 0.05, yy, num(v, 3), va="center", fontsize=TAM_RANKING,
                fontweight="bold" if k == "Propuesta_Novedosa" else "normal")
    ax.set_yticks(y)
    ax.set_yticklabels([CORTO[k] for k in rk.index], fontsize=TAM_RANKING)
    ax.tick_params(axis="x", labelsize=TAM_RANKING)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, max(rk.values) * 1.16)
    ax.set_xlabel("Rango promedio sobre las seis métricas (1 = mejor)", fontsize=TAM_RANKING)
    ax.xaxis.grid(True)
    out = guardar(fig, "fig_ranking_seis", ancho_libro=1.0)
    plt.close(fig)
    for k, v in rk.items():
        print(f"    {CORTO[k]:<22} {num(v)}  (recalculado {num(recalc[k])})")


# ------------------------------------------- las seis metricas, media por metodo
def metricas_seis():
    dm = pd.read_csv(REP / "descriptive_means_seis.csv").set_index("method")
    orden = pd.read_csv(REP / "ranking_seis_metricas.csv", index_col=0).index.tolist()

    fig, axes = plt.subplots(2, 3, figsize=(2000 / DPI, 1100 / DPI), dpi=DPI)
    for ax, m in zip(axes.ravel(), SEIS):
        v = [float(dm.loc[k, m]) for k in orden]
        ax.bar(range(len(orden)), v, color=[color(k) for k in orden],
               edgecolor="#555555", width=0.66)
        nd = 4 if max(v) < 1 else (2 if max(v) > 10 else 3)
        for i, val in enumerate(v):
            ax.text(i, val + max(v) * 0.02, num(val, nd), ha="center", va="bottom", fontsize=8)
        lider = orden[int(np.argmax(v))]
        ax.set_title(f"{NOMBRE[m]} ({m}), mayor es mejor\nmáximo: {CORTO[lider]}", fontsize=10)
        ax.set_ylim(0, max(v) * 1.22)
        ax.set_xticks(range(len(orden)))
        ax.set_xticklabels([CORTO[k] for k in orden], rotation=30, ha="right", fontsize=8)
        ax.xaxis.grid(False)
    fig.tight_layout()
    out = FIG / "fig_metricas_seis.png"
    fig.savefig(out, dpi=DPI, facecolor="white")
    plt.close(fig)
    peor = min(orden, key=lambda k: float(dm.loc[k, "SSIM"]))
    print(f"  {out}  (SSIM mas bajo: {CORTO[peor]} {num(dm.loc[peor, 'SSIM'], 4)})")


if __name__ == "__main__":
    FIGURAS = {"ranking_seis": ranking_seis, "metricas_seis": metricas_seis}
    pedidas = sys.argv[1:] or ["ranking_seis"]     # sin argumentos, solo la que usa el libro
    for nombre in pedidas:
        if nombre not in FIGURAS:
            raise SystemExit(f"figura desconocida: {nombre}; opciones: {', '.join(FIGURAS)}")
        FIGURAS[nombre]()
