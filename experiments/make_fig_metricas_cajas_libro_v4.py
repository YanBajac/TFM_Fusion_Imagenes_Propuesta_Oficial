# -*- coding: utf-8 -*-
"""Figura fig:metricas_cajas del libro (cap4, resultados cuantitativos): las seis metricas de calidad
por metodo, como diagramas de caja sobre los veinte pares del TNO.

POR QUE ESTA FIGURA. La Tabla de medias (tab:medias_seis) da un solo numero por metodo y metrica, y no
deja ver cuanto cambia ese valor de un par a otro. Esta figura muestra esa variacion: en cada panel, una
caja por metodo con los veinte valores del corpus.

QUE MUESTRA. Seis paneles en dos filas: arriba las tres metricas de actividad (entropia, desviacion
estandar, gradiente medio), abajo las tres de fidelidad (informacion mutua, similitud estructural,
relacion senal-ruido de pico, en dB), el mismo orden de la tabla. En cada panel, los siete metodos de
arriba abajo en el orden del ranking de seis metricas (ranking_seis_metricas.csv), igual en todos los
paneles. La caja va de la cuarta parte a las tres cuartas partes de los veinte valores (primer y tercer
cuartil), la linea vertical dentro es la mediana, el rombo blanco es la media (el valor de la tabla) y los
bigotes llegan al minimo y al maximo de los veinte pares. La propuesta en azul, los demas en gris.

LAS METRICAS se toman tal cual de all_metrics.csv, con la misma definicion que usa
run_stats_seis_metricas.py: la informacion mutua es, POR PAR, el promedio de la informacion mutua con la
imagen visible y con la infrarroja. El script comprueba que las medias de la figura coinciden con
descriptive_means_seis.csv y que la linea de cada caja es la mediana de los veinte valores.

Tamano de letra: el lienzo mide el ancho de texto (6.30 pulgadas), el ancho con que el LaTeX lo incluye
(width=\\textwidth), asi que la letra se imprime al tamano con que se dibuja: 10 pt los nombres de las
metricas y 9.5 pt los numeros y los nombres de los metodos. Estilo: el comun de las figuras del libro
(experiments/estilo_figuras_libro.py).

Salida: docs/libro_v4/figuras/fig_metricas_cajas.png (300 ppp)

Uso (desde la raiz del repo):  .venv\\Scripts\\python.exe -X utf8 experiments/make_fig_metricas_cajas_libro_v4.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FixedLocator, FormatStrFormatter

from estilo_figuras_libro import (ANCHO_TEXTO_PULG, GRIS_OSCURO, NEGRO, NOMBRES, REPORTES, TAM_MARCAS,
                                  TAM_TEXTO, aplicar_estilo, color_metodo, guardar)

FRACCION = 1.0                       # el LaTeX la incluye con width=\textwidth
ANCHO = FRACCION * ANCHO_TEXTO_PULG  # 6.30 pulgadas
ALTO = 4.3

# Las seis, en el orden de la tabla: tres de actividad arriba, tres de fidelidad abajo.
# Todas son "mayor es mejor". Para cada una: nombre del panel, marcas del eje y formato de los numeros
# (con el mismo numero de decimales en todo el eje: 0.10 y no 0.1). Las marcas se fijan a mano para que
# ninguna caiga en el borde derecho del panel, donde el numero se juntaria con el del panel vecino.
METRICAS = [
    ("EN", "Entropía (EN)", [5.5, 6.0, 6.5, 7.0], "%.1f"),
    ("SD", "Desviación estándar (SD)", [0.05, 0.10, 0.15, 0.20], "%.2f"),
    ("MG", "Gradiente medio (MG)", [0.02, 0.04, 0.06, 0.08], "%.2f"),
    ("MI", "Información mutua (MI)", [0.5, 1.0, 1.5], "%.1f"),
    ("SSIM", "Similitud estructural (SSIM)", [0.5, 0.6, 0.7, 0.8], "%.1f"),
    ("PSNR", "Relación señal-ruido\nde pico (PSNR), en dB", [10, 15, 20], "%d"),
]


def cargar():
    """all_metrics.csv con la MI unificada por par, como en run_stats_seis_metricas.con_mi_unificada."""
    df = pd.read_csv(REPORTES / "all_metrics.csv")
    df["MI"] = (df["MI_vis"] + df["MI_ir"]) / 2.0
    orden = pd.read_csv(REPORTES / "ranking_seis_metricas.csv", index_col=0).index.tolist()
    assert set(orden) == set(df["method"].unique()), "el ranking y all_metrics no tienen los mismos metodos"
    n = df.groupby("method").size()
    assert (n == 20).all() and df["image"].nunique() == 20, "no son 20 pares por metodo"
    return df, orden


def comprobar_medias(df):
    """Las medias de la figura son las de descriptive_means_seis.csv (redondeadas a cuatro decimales)."""
    ref = pd.read_csv(REPORTES / "descriptive_means_seis.csv").set_index("method")
    medias = df.groupby("method")[[m for m, *_ in METRICAS]].mean()
    for m, *_ in METRICAS:
        for k in ref.index:
            assert abs(round(float(medias.loc[k, m]), 4) - float(ref.loc[k, m])) < 1e-9, \
                f"la media de {m} en {k} no coincide con descriptive_means_seis.csv"
    return medias


def main():
    df, orden = cargar()
    medias = comprobar_medias(df)

    aplicar_estilo()
    fig, axes = plt.subplots(2, 3, figsize=(ANCHO, ALTO), sharey=True, layout="constrained")
    pos = np.arange(1, len(orden) + 1)
    medianas = {}

    for ax, (m, titulo, marcas, formato) in zip(axes.ravel(), METRICAS):
        datos = [df.loc[df["method"] == k, m].to_numpy() for k in orden]
        cajas = ax.boxplot(
            datos, positions=pos, orientation="horizontal", widths=0.62, whis=(0, 100),
            patch_artist=True, showfliers=False, showmeans=True,
            boxprops={"edgecolor": GRIS_OSCURO, "linewidth": 0.6},
            whiskerprops={"color": GRIS_OSCURO, "linewidth": 0.7},
            capprops={"color": GRIS_OSCURO, "linewidth": 0.7},
            medianprops={"color": NEGRO, "linewidth": 1.3},
            meanprops={"marker": "D", "markersize": 3.2, "markerfacecolor": "white",
                       "markeredgecolor": NEGRO, "markeredgewidth": 0.6},
        )
        for caja, k in zip(cajas["boxes"], orden):
            caja.set_facecolor(color_metodo(k))
        # lo dibujado es lo calculado: la linea de cada caja es la mediana, el rombo la media
        for caja, linea, rombo, k, v in zip(cajas["boxes"], cajas["medians"], cajas["means"], orden, datos):
            borde = caja.get_path().vertices[:, 0]
            assert np.isclose(borde.min(), np.percentile(v, 25)) and \
                np.isclose(borde.max(), np.percentile(v, 75)), f"cuartiles de {m} en {k}"
            assert np.allclose(linea.get_xdata(), np.median(v)), f"mediana de {m} en {k}"
            assert np.isclose(rombo.get_xdata()[0], medias.loc[k, m]), f"media de {m} en {k}"
            medianas[(m, k)] = float(np.median(v))

        ax.set_title(titulo, fontsize=TAM_TEXTO)
        lo, hi = ax.get_xlim()
        assert all(lo < t < hi for t in marcas), f"una marca de {m} cae fuera del panel"
        ax.xaxis.set_major_locator(FixedLocator(marcas))
        ax.xaxis.set_major_formatter(FormatStrFormatter(formato))
        ax.xaxis.grid(True)
        ax.tick_params(axis="y", length=0)

    axes[0, 0].set_yticks(pos, [NOMBRES[k] for k in orden], fontsize=TAM_MARCAS)
    axes[0, 0].set_ylim(len(orden) + 0.55, 0.45)        # la propuesta arriba, como en el ranking
    fig.get_layout_engine().set(w_pad=0.03, h_pad=0.04, wspace=0.04, hspace=0.08)
    guardar(fig, "fig_metricas_cajas", ancho_libro=FRACCION)
    plt.close(fig)

    # las cifras de la figura, para el texto
    print("\n    orden (ranking de seis metricas): " + ", ".join(NOMBRES[k] for k in orden))
    for m, *_ in METRICAS:
        nd = 2 if m == "PSNR" else 4
        print(f"    {m}:")
        for k in orden:
            v = df.loc[df["method"] == k, m]
            print(f"      {NOMBRES[k]:20s} media {medias.loc[k, m]:.{nd}f}  mediana {medianas[(m, k)]:.{nd}f}"
                  f"  Q1 {v.quantile(.25):.{nd}f}  Q3 {v.quantile(.75):.{nd}f}"
                  f"  min {v.min():.{nd}f}  max {v.max():.{nd}f}")


if __name__ == "__main__":
    main()
