# -*- coding: utf-8 -*-
"""Los dos montajes cualitativos del libro: las dos fuentes y los siete metodos.

Muestran solo lo que el libro compara: la imagen visible, la imagen infrarroja y los siete metodos
del banco de calidad, con los mismos parametros que en las tablas.

No llevan titulo: el nombre de la escena va en el epigrafe del LaTeX, no el nombre crudo del archivo.

Estilo: el comun de las figuras del libro (experiments/estilo_figuras_libro.py). Rotulos en Times New
Roman, los nombres de los metodos como en las tablas, y la propuesta con rotulo y marco en azul #4472c4,
el unico color de las figuras; el resto de los marcos, en gris oscuro y finos.

Tamano: el lienzo mide 6.3 pulgadas de ancho, el de la caja de texto del libro (160 mm), y el LaTeX lo
incluye con width=\\textwidth, asi que los rotulos se imprimen a 10 pt. Se guarda a 300 ppp: cada
panel mide unos 2 pulgadas, unos 615 pixeles, casi el tamano original de las imagenes del TNO (620 y
768 de ancho), sin perder detalle.

Salida: docs/libro_v4/figuras/montaje_kaptein.png y montaje_humo.png

Uso (desde la raiz del repo):  .venv\\Scripts\\python.exe -X utf8 experiments/make_montajes_libro_v4.py
"""
import os
import sys
from pathlib import Path

# La raiz del repo se puede pasar como argumento; si no, es la carpeta padre de la del script.
RAIZ = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
os.chdir(RAIZ)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, ".")
from src.datasets import list_pairs, load_pair
from src.fusion import (fuse_optimal, laplacian_pyramid_fusion, ratio_pyramid_fusion,
                        dwt_fusion, dtcwt_fusion, curvelet_fusion, tophat_classic_fusion)
from estilo_figuras_libro import (ANCHO_TEXTO_PULG, AZUL, GRIS_OSCURO, NEGRO, NOMBRES, TAM_TEXTO,
                                  aplicar_estilo, guardar)

ESCENAS = {"Triclobs_Kaptein_1123": "montaje_kaptein",
           "Athena_soldier_behind_smoke_3_meting012-1700": "montaje_humo"}
# (rotulo, funcion de fusion, es la propuesta). Los nombres de los metodos salen de NOMBRES, que son
# los de las tablas; «curvelet_fusion» es la DWT (db4). El orden de los metodos es el de la lista de
# comparativos del cap3 (sec:operador) y de fig_metodologia: las dos piramides, las dos DWT juntas, la
# DTCWT, el Top-Hat clasico y, al final, la propuesta.
PANELES = [
    ("Imagen visible", None, False),
    ("Imagen infrarroja", None, False),
    (NOMBRES["PiramideLaplace"], lambda v, i: laplacian_pyramid_fusion(v, i, levels=4), False),
    (NOMBRES["RatioPiramide"], lambda v, i: ratio_pyramid_fusion(v, i, levels=4), False),
    (NOMBRES["DWT"], lambda v, i: dwt_fusion(v, i, levels=3), False),
    (NOMBRES["Curvelet"], lambda v, i: curvelet_fusion(v, i, levels=3), False),
    (NOMBRES["DTCWT"], lambda v, i: dtcwt_fusion(v, i, levels=4), False),
    (NOMBRES["TopHat_Clasico"] + " ($r = 5$, $m = 1$)",
     lambda v, i: tophat_classic_fusion(v, i, r=5, m=1.0), False),
    (NOMBRES["Propuesta_Novedosa"] + " ($r = 25$, $m = 0.30$)",
     lambda v, i: fuse_optimal(v, i, r=25, m=0.30, mode="sum"), True),
]

# disposicion, en pulgadas
MARGEN = 0.02
HUECO_H = 0.06                      # entre columnas
HUECO_V = 0.05                      # entre el pie de un panel y el rotulo del siguiente
ALTO_ROTULO = 0.21                  # franja del rotulo, sobre cada panel
LW_MARCO = 0.5
LW_PROPUESTA = 1.6


def montaje(vis, ir, nombre):
    alto, ancho = vis.shape
    panel_w = (ANCHO_TEXTO_PULG - 2 * MARGEN - 2 * HUECO_H) / 3
    panel_h = panel_w * alto / ancho
    alto_fig = 2 * MARGEN + 3 * (ALTO_ROTULO + panel_h) + 2 * HUECO_V
    fig = plt.figure(figsize=(ANCHO_TEXTO_PULG, alto_fig))
    for k, (rotulo, fn, prop) in enumerate(PANELES):
        fila, col = divmod(k, 3)
        x0 = MARGEN + col * (panel_w + HUECO_H)
        y0 = alto_fig - MARGEN - ALTO_ROTULO - panel_h - fila * (ALTO_ROTULO + panel_h + HUECO_V)
        ax = fig.add_axes([x0 / ANCHO_TEXTO_PULG, y0 / alto_fig,
                           panel_w / ANCHO_TEXTO_PULG, panel_h / alto_fig])
        img = vis if k == 0 else ir if k == 1 else fn(vis, ir)
        ax.imshow(np.clip(img, 0, 1), cmap="gray", vmin=0, vmax=1, aspect="auto")
        ax.set_title(rotulo, fontsize=TAM_TEXTO, pad=3, color=AZUL if prop else NEGRO)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_edgecolor(AZUL if prop else GRIS_OSCURO)
            sp.set_linewidth(LW_PROPUESTA if prop else LW_MARCO)
    guardar(fig, nombre, ancho_libro=1.0)
    plt.close(fig)


def main():
    aplicar_estilo()
    pares = {os.path.splitext(os.path.basename(str(vp)))[0]: (vp, ip) for vp, ip in list_pairs()}
    for stem, nombre in ESCENAS.items():
        assert stem in pares, f"la escena {stem} no esta en el corpus"
        vis, ir = load_pair(*pares[stem])
        print(f"  {nombre}: {stem}, {vis.shape[1]} x {vis.shape[0]} pixeles")
        montaje(vis, ir, nombre)


if __name__ == "__main__":
    main()
