# -*- coding: utf-8 -*-
"""Figura fig:metodologia del libro (cap3): diagrama de las etapas del estudio.

POR QUE. El capitulo de metodologia abre con un diagrama de las etapas del estudio. Este cumple ese
papel: figuras/fig_flujo_propuesta.png muestra el operador y no el estudio.

QUE MUESTRA. Las etapas en el orden de docs/libro_v4/caps/cap3_metodologia.tex:
  - Los dos conjuntos, TNO (20 pares de 13 escenas, para la calidad) y M3FD (para la deteccion), con
    el mismo preprocesamiento.
  - El operador propuesto, con el ajuste por enjambre de particulas como rama lateral, unida con una
    flecha doble porque el enjambre evalua el propio algoritmo y le devuelve el radio y el peso: el peso
    quedo en el limite inferior del rango de busqueda, m = 0.30, y se adopto r = 25, uno de los dos
    resultados del enjambre (cap3, sec:ajuste; cap4, sec:res-ajuste).
  - Las imagenes fusionadas con los siete metodos, que alimentan las dos evaluaciones: la de calidad y,
    junto con la visible, la infrarroja y el promedio simple, las diez entradas de los detectores
    (las diez de m3fd_v2_map_resumen.csv).
  - La evaluacion de la deteccion con la tasa equilibrada sobre los objetos que solo ve una camara.
  - Al final, una etapa comun: el examen de la hipotesis del trabajo, en sus dos partes: calidad
    frente a los seis metodos y aplicacion en deteccion frente al Top-Hat clasico.
Las cifras van con punto decimal, como en el resto del libro. Si se cambia algo del capitulo 3 que
figure aqui, hay que regenerar la figura. El script comprueba que cada texto entre en su caja.

Estilo: el comun de las figuras del libro (experiments/estilo_figuras_libro.py): Times New Roman, cajas
rectas con relleno gris claro y borde gris oscuro; la caja del operador propuesto, con borde azul, el
unico color, que en todas las figuras marca la propuesta.

Tamano de letra: el lienzo mide 6.3 pulgadas de ancho, el de la caja de texto del libro (160 mm), y el
LaTeX la incluye con width=\\textwidth, de modo que los cuerpos de letra son los reales: 10 pt en los
nombres de las etapas y 9 pt en el detalle. Se guarda sin recortar, para conservar ese ancho.

Salida: docs/libro_v4/figuras/fig_metodologia.png (300 ppp)

Uso (desde la raiz del repo):  .venv\\Scripts\\python.exe -X utf8 experiments/make_fig_metodologia_libro_v4.py
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
from matplotlib.patches import Rectangle

from estilo_figuras_libro import (ANCHO_TEXTO_PULG, AZUL, GRIS_CLARO, GRIS_OSCURO, NEGRO,
                                  aplicar_estilo, guardar)

BORDE = GRIS_OSCURO
RELLENO = GRIS_CLARO

# Lienzo en pulgadas: 6.3 de ancho, el ancho de la caja de texto del libro (160 mm).
ANCHO = ANCHO_TEXTO_PULG
CAJA_W = 2.85                       # cajas de una columna
ANCHO_PREPRO = 3.9                  # preprocesamiento
ANCHO_COMUN = 5.9                   # imagenes fusionadas y examen de la hipotesis
X_IZQ, X_DER = 1.5, 4.8             # centros de las dos columnas
X_CENTRO = (X_IZQ + X_DER) / 2
HUECO = 0.26                        # distancia vertical entre dos filas de cajas, para la flecha
BORDE_SUP = BORDE_INF = 0.06
MARGEN = 0.08                       # aire minimo entre el texto y el borde de la caja

TAM_TITULO, TAM_DETALLE = 10, 9
D_TITULO = 0.21                     # del centro del nombre al de la primera linea de detalle
D_LINEA = 0.155                     # entre dos lineas de detalle
ALTO_BASE = 0.57                    # alto de una caja con una sola linea de detalle
LW_CAJA = 0.8
LW_PROPUESTA = 1.4                  # el borde azul de la caja de la propuesta, un poco mas grueso
_textos = []                        # (artista, ancho y alto de su caja, centro y), para comprobar


def alto_caja(n_lineas):
    return ALTO_BASE + D_LINEA * (n_lineas - 1)


def caja(ax, x, y, titulo, detalle, ancho=CAJA_W, alto=None, propuesta=False):
    """Caja recta con el nombre de la etapa en negrita y una o mas lineas de detalle debajo."""
    lineas = [detalle] if isinstance(detalle, str) else list(detalle)
    alto = alto or alto_caja(len(lineas))
    ax.add_patch(Rectangle((x - ancho / 2, y - alto / 2), ancho, alto,
                           linewidth=LW_PROPUESTA if propuesta else LW_CAJA,
                           edgecolor=AZUL if propuesta else BORDE, facecolor=RELLENO))
    bloque = D_TITULO + D_LINEA * (len(lineas) - 1)
    y_tit = y + bloque / 2 + 0.01
    t = ax.text(x, y_tit, titulo, ha="center", va="center", fontsize=TAM_TITULO,
                fontweight="bold", color=NEGRO)
    _textos.append((t, ancho, alto, y))
    for i, linea in enumerate(lineas):
        t = ax.text(x, y_tit - D_TITULO - D_LINEA * i, linea, ha="center", va="center",
                    fontsize=TAM_DETALLE, color=NEGRO)
        _textos.append((t, ancho, alto, y))
    return alto


def flecha(ax, x0, y0, x1, y1, discontinua=False, doble=False):
    """Flecha de (x0, y0) a (x1, y1); con doble=True lleva punta en los dos extremos."""
    if discontinua:
        # El trazo discontinuo va aparte y la punta se dibuja llena: con el patron de rayas en
        # arrowprops, las rayas tambien cortaban el contorno de la punta y la deformaban.
        largo = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        xm = x1 - PUNTA * (x1 - x0) / largo
        ym = y1 - PUNTA * (y1 - y0) / largo
        ax.plot([x0, xm], [y0, ym], color=BORDE, lw=0.9, linestyle=(0, (3, 2)),
                dash_capstyle="butt")
        x0, y0 = xm, ym
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="<|-|>" if doble else "-|>", color=BORDE, lw=0.9,
                                mutation_scale=11, shrinkA=0, shrinkB=0))


PUNTA = 0.09                        # tramo final, lleno, de la flecha discontinua (pulgadas)


def comprobar(fig):
    """Falla si algun texto no entra en su caja con el margen pedido, a lo ancho o a lo alto."""
    r = fig.canvas.get_renderer()
    inv = fig.dpi_scale_trans.inverted()
    for t, ancho, alto, y in _textos:
        bb = t.get_window_extent(renderer=r).transformed(inv)
        if bb.width > ancho - 2 * MARGEN:
            raise SystemExit(f"no entra a lo ancho ({bb.width:.2f} in de {ancho:.2f}): {t.get_text()}")
        if bb.y1 > y + alto / 2 - MARGEN / 2 or bb.y0 < y - alto / 2 + MARGEN / 2:
            raise SystemExit(f"no entra a lo alto: {t.get_text()}")


def main():
    aplicar_estilo()
    # contenido de cada fila: (x, nombre, detalle, ancho, es la propuesta)
    filas = [
        [(X_IZQ, "TNO Image Fusion Dataset", ["20 pares de 13 escenas,", "para la calidad de imagen"], CAJA_W, False),
         (X_DER, "M3FD", ["pares con objetos marcados,", "para la detección de objetos"], CAJA_W, False)],
        [(X_CENTRO, "Preprocesamiento", "escala de grises e intensidad entre cero y uno", ANCHO_PREPRO, False)],
        [(X_IZQ, "Algoritmo propuesto", ["banco de cinco elementos de radio $r$",
                                        "y regla de fusión con peso $m$"], CAJA_W, True),
         (X_DER, "Ajuste por enjambre de partículas",
          ["radio $r$ y peso $m$, sobre tres escenas;", "el peso quedó en el límite inferior",
           "del rango de búsqueda, 0.30;", "se adoptó el radio 25, que prioriza el realce"], CAJA_W, False)],
        [(X_CENTRO, "Imágenes fusionadas con siete métodos",
          ["propuesta ($r = 25$, $m = 0.30$), Top-Hat clásico ($r = 5$, $m = 1$) y cinco",
           "multiescala: pirámides de Laplace y de razón, DWT (Haar y db4) y DTCWT"], ANCHO_COMUN, False)],
        [(X_IZQ, "Evaluación de la calidad", ["seis métricas sin referencia", "y pruebas no paramétricas"], CAJA_W, False),
         (X_DER, "Entradas del detector", ["visible, infrarroja, promedio simple", "y las siete fusiones: diez en total"], CAJA_W, False)],
        [(X_DER, "Entrenamiento de detectores", "YOLOv8n, tres semillas por entrada", CAJA_W, False)],
        [(X_DER, "Evaluación de la detección", ["tasa equilibrada sobre los objetos",
                                                 "que solo ve una de las dos cámaras"], CAJA_W, False)],
        [(X_CENTRO, "Examen de la hipótesis",
          ["calidad frente a los seis métodos y",
           "aplicación en detección frente al Top-Hat clásico"], ANCHO_COMUN, False)],
    ]

    def n_lineas(d):
        return 1 if isinstance(d, str) else len(d)
    altos = [max(alto_caja(n_lineas(d)) for _, _, d, _, _ in fila) for fila in filas]
    alto_total = BORDE_SUP + sum(altos) + HUECO * (len(filas) - 1) + BORDE_INF
    centros, y = [], alto_total - BORDE_SUP
    for a in altos:
        centros.append(y - a / 2)
        y -= a + HUECO

    fig = plt.figure(figsize=(ANCHO, alto_total))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, ANCHO)
    ax.set_ylim(0, alto_total)
    ax.axis("off")

    for fila, yc, a in zip(filas, centros, altos):
        for x, nombre, detalle, ancho, prop in fila:
            caja(ax, x, yc, nombre, detalle, ancho=ancho, alto=a, propuesta=prop)

    arriba = [yc + a / 2 for yc, a in zip(centros, altos)]
    abajo = [yc - a / 2 for yc, a in zip(centros, altos)]
    # los dos conjuntos entran al preprocesamiento, y de ahi al operador
    flecha(ax, X_IZQ, abajo[0], X_IZQ, arriba[1])
    flecha(ax, X_DER, abajo[0], X_DER, arriba[1])
    flecha(ax, X_IZQ, abajo[1], X_IZQ, arriba[2])
    # rama lateral, con flecha doble: el enjambre evalua el propio algoritmo y le devuelve el radio y
    # el peso (cap3, sec:ajuste)
    flecha(ax, X_IZQ + CAJA_W / 2, centros[2], X_DER - CAJA_W / 2, centros[2], doble=True)
    # el operador, con los otros seis metodos, da las imagenes fusionadas
    flecha(ax, X_IZQ, abajo[2], X_IZQ, arriba[3])
    # las siete fusiones alimentan las dos evaluaciones
    flecha(ax, X_IZQ, abajo[3], X_IZQ, arriba[4])
    flecha(ax, X_DER, abajo[3], X_DER, arriba[4])
    flecha(ax, X_DER, abajo[4], X_DER, arriba[5])
    flecha(ax, X_DER, abajo[5], X_DER, arriba[6])
    # las dos evaluaciones llegan al examen de la hipotesis
    flecha(ax, X_IZQ, abajo[4], X_IZQ, arriba[7])
    flecha(ax, X_DER, abajo[6], X_DER, arriba[7])

    comprobar(fig)
    guardar(fig, "fig_metodologia", ancho_libro=1.0, recortar=False)
    plt.close(fig)


if __name__ == "__main__":
    main()
