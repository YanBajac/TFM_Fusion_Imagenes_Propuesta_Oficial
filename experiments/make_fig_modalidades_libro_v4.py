# -*- coding: utf-8 -*-
"""Figura fig:modalidades, la de apertura del capitulo 1 del libro: que aporta cada camara y que
reune la fusion.

QUE MUESTRA. Tres paneles de una misma escena del TNO, uno al lado del otro: la imagen visible, la
imagen infrarroja y la imagen fusionada por la propuesta con la configuracion adoptada (radio r = 25,
peso m = 0.30). La escena es Triclobs_Kaptein_1123, un peaton al anochecer frente a la entrada de un
edificio: en la imagen visible se ven la textura de los arbustos, los adoquines y la puerta, pero la
persona apenas se distingue; en la infrarroja la persona resalta en blanco por su calor y el fondo
pierde textura; en la fusion estan las dos cosas. Es la lectura que el capitulo 1 necesita a la
primera, sin saber todavia nada del metodo.

La misma escena vuelve en el montaje cualitativo de la seccion 4.3 (montaje_kaptein.png), con los
siete metodos; aca solo van las dos fuentes y la propuesta.

DE DONDE SALE CADA COSA.
  - El par: src.datasets.list_pairs(), el corpus vigente de 20 pares (sin el par corrupto
    Athena_heather_IR_hei_vis_g). Se comprueba que la escena este en el corpus.
  - r y m: se leen de experiments/results/metrics_reports/all_metrics.config.json, la configuracion
    con la que se calcularon las metricas de calidad (all_metrics.csv), y se comprueba que sean los
    adoptados (r = 25, m = 0.30, modo «sum»: disco mas el promedio de los cuatro segmentos).
  - La fusion: src.fusion.fuse_optimal con esos r y m. Se compara con la imagen ya guardada en
    experiments/results/fused_images/Propuesta_Novedosa/ y se informa la diferencia maxima (la del
    disco esta truncada a 8 bits, asi que puede diferir en un nivel de gris, 1/255).

ESTILO: el comun de las figuras del libro (experiments/estilo_figuras_libro.py), igual que los
montajes: rotulo arriba de cada panel en Times New Roman a 10 pt, marcos finos en gris oscuro y el de
la propuesta en azul #4472c4, sin titulo dentro de la imagen y sin el nombre del archivo de la escena.
El lienzo mide el ancho de la caja de texto (160 mm = 6.30 pulgadas) y el LaTeX la incluye con
width=\\textwidth, asi los rotulos se imprimen a 10 pt.

Salida: docs/libro_v4/figuras/fig_modalidades.png (300 ppp)

Uso (desde la raiz del repo):  .venv\\Scripts\\python.exe -X utf8 experiments/make_fig_modalidades_libro_v4.py
"""
import json
import os
import sys
from pathlib import Path

# La raiz del repo se puede pasar como argumento; si no, es la carpeta padre de la del script.
RAIZ = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
os.chdir(RAIZ)
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(RAIZ))

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.datasets import list_pairs, load_pair
from src.fusion import fuse_optimal
from estilo_figuras_libro import (ANCHO_TEXTO_PULG, AZUL, GRIS_OSCURO, NEGRO, REPORTES, TAM_TEXTO,
                                  aplicar_estilo, guardar)

ESCENA = "Triclobs_Kaptein_1123"
NOMBRE = "fig_modalidades"
CONFIG = REPORTES / "all_metrics.config.json"
FUSION_EN_DISCO = RAIZ / "experiments" / "results" / "fused_images" / "Propuesta_Novedosa"

ROTULOS = ("Imagen visible", "Imagen infrarroja", "Imagen fusionada (propuesta)")

# disposicion, en pulgadas
MARGEN = 0.02
HUECO_H = 0.08                      # entre paneles
ALTO_ROTULO = 0.22                  # franja del rotulo, sobre cada panel
LW_MARCO = 0.5
LW_PROPUESTA = 1.6                  # el mismo marco azul que en los montajes de la seccion 4.3


def parametros_propuesta():
    """r, m y modo de la propuesta, tal como se usaron para las metricas de calidad."""
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))["config"]["Propuesta_Novedosa"]
    r, m, modo = int(cfg["r"]), float(cfg["m"]), cfg["mode"]
    assert (r, m, modo) == (25, 0.30, "sum"), f"configuracion inesperada en {CONFIG.name}: {cfg}"
    return r, m, modo


def main():
    aplicar_estilo()
    r, m, modo = parametros_propuesta()
    pares = {Path(vp).stem: (vp, ip) for vp, ip in list_pairs()}
    assert len(pares) == 20, f"el corpus deberia tener 20 pares y tiene {len(pares)}"
    assert ESCENA in pares, f"la escena {ESCENA} no esta en el corpus"
    vis, ir = load_pair(*pares[ESCENA])
    fus = fuse_optimal(vis, ir, r=r, m=m, mode=modo)
    print(f"  escena {ESCENA}: {vis.shape[1]} x {vis.shape[0]} pixeles; propuesta r = {r}, m = {m:.2f}")

    guardada = FUSION_EN_DISCO / f"{ESCENA}.png"
    if guardada.exists():
        en_disco = cv2.imread(str(guardada), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255.0
        print(f"  diferencia maxima con la fusion guardada en disco: {np.abs(fus - en_disco).max():.4f}"
              f" (1/255 = {1 / 255:.4f})")

    alto, ancho = vis.shape
    panel_w = (ANCHO_TEXTO_PULG - 2 * MARGEN - 2 * HUECO_H) / 3
    panel_h = panel_w * alto / ancho
    alto_fig = 2 * MARGEN + ALTO_ROTULO + panel_h
    fig = plt.figure(figsize=(ANCHO_TEXTO_PULG, alto_fig))
    for k, (rotulo, img) in enumerate(zip(ROTULOS, (vis, ir, fus))):
        prop = k == 2
        x0 = MARGEN + k * (panel_w + HUECO_H)
        y0 = MARGEN
        ax = fig.add_axes([x0 / ANCHO_TEXTO_PULG, y0 / alto_fig,
                           panel_w / ANCHO_TEXTO_PULG, panel_h / alto_fig])
        ax.imshow(np.clip(img, 0, 1), cmap="gray", vmin=0, vmax=1, aspect="auto")
        ax.set_title(rotulo, fontsize=TAM_TEXTO, pad=3, color=AZUL if prop else NEGRO)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_edgecolor(AZUL if prop else GRIS_OSCURO)
            sp.set_linewidth(LW_PROPUESTA if prop else LW_MARCO)
    guardar(fig, NOMBRE, ancho_libro=1.0)
    plt.close(fig)


if __name__ == "__main__":
    main()
