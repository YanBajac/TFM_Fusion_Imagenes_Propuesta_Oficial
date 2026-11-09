# -*- coding: utf-8 -*-
"""Figura fig:morfologia del libro (cap2): operaciones morfologicas y transformada Top-Hat en 1-D.

COMO. Usa las mismas operaciones de src/fusion: cv2.erode, cv2.dilate y cv2.morphologyEx con un
elemento plano, y los vecinos que caen fuera de la senal se ignoran, como dice la Seccion 2.3.

QUE MUESTRA. Una senal sintetica, como los niveles de gris a lo largo de una fila, con un fondo plano
y cuatro rasgos separados: un monte angosto, un monte ancho, un valle angosto y un valle ancho. Los
angostos son mas estrechos que el elemento y los anchos, mas amplios, de modo que la Top-Hat recoge
entero el rasgo angosto y solo la punta del ancho. Seis paneles: la senal con una barra del ancho del
elemento, la erosion, la dilatacion, la apertura, el cierre y las dos Top-Hat (la blanca hacia arriba
y la negra, con el signo cambiado, hacia abajo). Sin titulo general. Si se cambia algo de esto, hay
que revisar el \\caption de fig:morfologia en docs/libro_v4/caps/cap2_marco.tex.

El elemento es el segmento horizontal de src.fusion.optimal_top_hat.linear_se(r, 0). Sobre una sola
fila, el disco de radio r da el mismo resultado, y el script lo comprueba.

Tamano de letra: el lienzo mide 0.9 del ancho de texto (5.67 pulgadas), el ancho con que el LaTeX lo
incluye (width=0.9\\textwidth), asi que la letra se imprime al tamano con que se dibuja: 10 pt los
nombres de los paneles, los rotulos y los ejes. Estilo: el comun de las figuras del libro
(experiments/estilo_figuras_libro.py), en negro y grises, sin color, porque el azul queda reservado
para la propuesta en las demas figuras.

Salida: docs/libro_v4/figuras/fig_morfologia_tophat.png (300 ppp)

Uso (desde la raiz del repo):  .venv\\Scripts\\python.exe -X utf8 experiments/make_fig_morfologia_libro_v4.py
"""
import os
import sys
from pathlib import Path

# La raiz del repo se puede pasar como argumento; si no, es la carpeta padre de la del script.
RAIZ = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
os.chdir(RAIZ)
sys.path.insert(0, ".")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.fusion.optimal_top_hat import _close, _open, disk_se, linear_se
from estilo_figuras_libro import (ANCHO_TEXTO_PULG, GRIS, GRIS_OSCURO, NEGRO, TAM_TEXTO,
                                  aplicar_estilo, guardar)

FRACCION = 0.9                      # el LaTeX la incluye con width=0.9\textwidth
ANCHO = FRACCION * ANCHO_TEXTO_PULG # 5.67 pulgadas
ALTO = 3.45
GRIS_WTH = GRIS_OSCURO              # la Top-Hat blanca
GRIS_BTH = GRIS                     # la Top-Hat negra, mas clara, para distinguirlas sin color
GRIS_F = GRIS                       # la senal original, repetida de fondo
TAM_ROTULO = TAM_TEXTO              # rotulos dentro de los paneles y de los ejes
OSCURO = GRIS_OSCURO
LW_SENAL = 1.3
LW_FONDO = 1.1

N = 760      # muestras de la senal
R = 25       # radio del elemento: el segmento tiene 2R + 1 = 51 muestras


# centros de los cuatro rasgos (muestra), escala y altura; los angostos miden menos que el elemento.
# Entre dos montes (o dos valles) vecinos queda un valle (o un monte) de fondo; se los separa lo
# bastante para que ese hueco sea mas ancho que el elemento y las Top-Hat no lo recojan.
RASGOS = {"monte angosto": (80, 7.0, 0.30), "monte ancho": (270, 45.0, 0.16),
          "valle angosto": (420, 7.0, -0.28), "valle ancho": (610, 45.0, -0.16)}


def senal():
    """Fondo plano y cuatro rasgos separados, para que las Top-Hat solo respondan a los rasgos."""
    x = np.arange(N, dtype=np.float64)
    f = np.full(N, 0.50)
    for centro, escala, alto in RASGOS.values():
        f += alto * np.exp(-((x - centro) / escala) ** 2)
    return x, f.astype(np.float32)


def operaciones(f):
    """Erosion, dilatacion, apertura y cierre de la senal f con el elemento plano de src/fusion."""
    fila = f[None, :]
    se = linear_se(R, 0)
    assert int(se.sum()) == 2 * R + 1 and se[R].all(), "el elemento no es un segmento de 2R + 1"
    ero = cv2.erode(fila, se)
    dil = cv2.dilate(fila, se)
    ape = _open(fila, se)
    cie = _close(fila, se)
    # la apertura y el cierre de src/fusion son las composiciones de eq:apertura-cierre (cap2)
    assert np.allclose(ape, cv2.dilate(ero, se)), "la apertura no es la dilatacion de la erosion"
    assert np.allclose(cie, cv2.erode(dil, se)), "el cierre no es la erosion de la dilatacion"
    # sobre una sola fila, el disco del banco da lo mismo que el segmento horizontal
    assert np.allclose(ape, _open(fila, disk_se(R))) and np.allclose(cie, _close(fila, disk_se(R)))
    # los vecinos de fuera se ignoran: en el primer punto la erosion es el minimo de las R + 1 muestras
    assert np.isclose(ero[0, 0], f[:R + 1].min()) and np.isclose(dil[0, 0], f[:R + 1].max())
    return ero[0], dil[0], ape[0], cie[0]


def main():
    x, f = senal()
    ero, dil, ape, cie = operaciones(f)
    wth = f - ape
    bth = cie - f
    assert wth.min() >= -1e-6 and bth.min() >= -1e-6, "una Top-Hat dio negativa"

    aplicar_estilo()
    fig, axes = plt.subplots(2, 3, figsize=(ANCHO, ALTO), sharex=True, layout="constrained")
    ax = axes.ravel()
    lim = (f.min() - 0.06, f.max() + 0.05)

    ax[0].plot(x, f, color=NEGRO, linewidth=LW_SENAL)
    ax[0].set_title("Señal original, $f$", fontsize=TAM_ROTULO)
    # barra del ancho del elemento, arriba a la derecha, donde la senal no llega
    yb = lim[1] - 0.05
    x1 = N - 30
    ax[0].plot([x1 - 2 * R, x1], [yb, yb], color=NEGRO, linewidth=1.8, solid_capstyle="butt")
    # el rotulo va en dos lineas: en una sola tapaba el monte angosto
    ax[0].text(x1 - 2 * R - 14, yb - 0.03, "Ancho del\nelemento $b$", ha="right", va="center",
               multialignment="right", linespacing=1.1, fontsize=TAM_ROTULO, color=NEGRO)

    paneles = [
        (ax[1], ero, r"Erosión, $\varepsilon(f,b)$"),
        (ax[2], dil, r"Dilatación, $\delta(f,b)$"),
        (ax[3], ape, r"Apertura, $\gamma(f,b)$"),
        (ax[4], cie, r"Cierre, $\varphi(f,b)$"),
    ]
    for a, g, titulo in paneles:
        a.plot(x, f, color=GRIS_F, linewidth=LW_FONDO)
        a.plot(x, g, color=NEGRO, linewidth=LW_SENAL)
        a.set_title(titulo, fontsize=TAM_ROTULO)
    for a in ax[:5]:
        a.set_ylim(*lim)

    a = ax[5]
    a.axhline(0, color=OSCURO, linewidth=0.6)
    a.fill_between(x, 0, wth, color=GRIS_WTH, linewidth=0)
    a.fill_between(x, 0, -bth, color=GRIS_BTH, linewidth=0)
    a.set_title("Top-Hat blanca y negra", fontsize=TAM_ROTULO)
    alto = max(wth.max(), bth.max()) * 1.15
    a.set_ylim(-alto, alto)
    xw = RASGOS["monte angosto"][0] + 18
    xb = RASGOS["valle angosto"][0] + 18
    a.text(xw, wth.max() * 0.80, r"$\mathrm{WTH}$", fontsize=TAM_ROTULO, color=NEGRO, va="center")
    a.text(xb, -bth.max() * 0.80, r"$-\mathrm{BTH}$", fontsize=TAM_ROTULO, color=OSCURO, va="center")

    for a in ax:
        a.set_xticks([])
        a.set_yticks([])
        a.set_xlim(0, N - 1)
        for sp in a.spines.values():
            sp.set_edgecolor(OSCURO)
            sp.set_linewidth(0.6)
    fig.supxlabel("Posición a lo largo de la fila", fontsize=TAM_ROTULO)
    fig.supylabel("Nivel de gris", fontsize=TAM_ROTULO)
    # disposicion «constrained»: con tight_layout el rotulo vertical pisaba los paneles de la izquierda
    fig.get_layout_engine().set(w_pad=0.03, h_pad=0.03, wspace=0.03, hspace=0.06)
    guardar(fig, "fig_morfologia_tophat", ancho_libro=FRACCION)
    plt.close(fig)

    # lo que el texto de la Seccion 2.3 dice que se ve, comprobado sobre los datos de la figura
    print(f"    elemento: {2 * R + 1} muestras; senal: {N} muestras")
    fuera = np.ones(N, bool)
    for nombre, (centro, escala, alto) in RASGOS.items():
        media = 3 * escala if escala < R else 2.2 * escala
        cerca = slice(max(0, int(centro - media)), int(centro + media) + 1)
        fuera[cerca] = False
        th = wth if alto > 0 else bth
        otra = bth if alto > 0 else wth
        print(f"    {nombre}: altura {abs(alto):.2f}; {'WTH' if alto > 0 else 'BTH'} maxima "
              f"{th[cerca].max():.3f}; la otra Top-Hat, {otra[cerca].max():.4f}")
    print(f"    WTH y BTH maximas lejos de los rasgos: {wth[fuera].max():.4f} y {bth[fuera].max():.4f}")
    assert wth[fuera].max() < 0.01 and bth[fuera].max() < 0.01, "las Top-Hat no son casi nulas en el fondo"


if __name__ == "__main__":
    main()
