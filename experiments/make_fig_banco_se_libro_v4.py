# -*- coding: utf-8 -*-
"""Figura fig:banco_se del libro (cap3, Seccion 3.2.1): los cinco elementos estructurantes del banco.

QUE MUESTRA. Cinco cuadriculas de (2r+1) x (2r+1) pixeles, con r = 5 para que los pixeles se distingan
(la configuracion adoptada usa r = 25, que daria cuadriculas de 51 x 51). Cada cuadro es un pixel; los
grises forman el elemento. El punto blanco marca el centro, que el libro define como parte del elemento
(Seccion 2.3). Las matrices salen de src.fusion.optimal_top_hat: disk_se(r) para el disco y
linear_se(r, angulo) para los segmentos, y se dibujan con la fila 0 arriba, como una imagen. Por eso el
segmento de 45 grados baja de izquierda a derecha: los angulos se miden en coordenadas de imagen, con
las filas creciendo hacia abajo, que es la convencion que declara el libro en la Seccion 3.2.1.
Con r = 5 el disco es ademas el unico elemento del Top-Hat clasico (src.fusion.comparatives.
tophat_classic_fusion arma el mismo cv2.MORPH_ELLIPSE de 11 x 11). La configuracion adoptada, r = 25 y
m = 0.30, esta en experiments/results/metrics_reports/all_metrics.config.json.

COMPROBACIONES. El script verifica que las matrices del codigo coinciden con las Ecuaciones (eq:disco)
y (eq:segmentos) del libro, para r = 5 y r = 25, y que los segmentos diagonales tienen 2 q_r + 1
pixeles, con q_r = floor(r / sqrt(2) + 1/2). Si alguna falla, se detiene sin escribir la figura.

Tamano de letra: el lienzo mide el ancho de texto (160 mm = 6.30 pulgadas), el ancho con que el LaTeX
la incluye (width=\\textwidth), asi que los rotulos se imprimen a 10 pt.

Salida: docs/libro_v4/figuras/fig_banco_se.png (300 ppp)

Uso (desde la raiz del repo):  .venv\\Scripts\\python.exe -X utf8 experiments/make_fig_banco_se_libro_v4.py
"""
import os
import sys
from pathlib import Path

# La raiz del repo se puede pasar como argumento; si no, es la carpeta padre de la del script.
RAIZ = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
os.chdir(RAIZ)
sys.path.insert(0, ".")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from estilo_figuras_libro import (aplicar_estilo, guardar, ANCHO_TEXTO_PULG, NEGRO, GRIS_OSCURO,
                                  GRIS, TAM_TEXTO)
from src.fusion.optimal_top_hat import disk_se, linear_se, _ANGLES

R_FIGURA = 5          # radio ilustrativo: cuadriculas de 11 x 11
R_ADOPTADO = 25       # configuracion adoptada (solo para la comprobacion y el aviso de consola)


# ---------------------------------------------------------------- comprobaciones contra el libro
def disco_libro(r):
    """Ecuacion (eq:disco): |k| <= r, |j| <= floor(sqrt(r^2 - k^2) + 1/2). Filas k, columnas j."""
    n = 2 * r + 1
    d = np.zeros((n, n), dtype=np.uint8)
    for k in range(-r, r + 1):
        a = int(np.floor(np.sqrt(r * r - k * k) + 0.5))
        d[k + r, r - a:r + a + 1] = 1
    return d


def segmento_libro(r, ang):
    """Ecuacion (eq:segmentos), con las filas creciendo hacia abajo. (j, k) = (columna, fila)."""
    n = 2 * r + 1
    q = int(np.floor(r / np.sqrt(2) + 0.5))
    s = np.zeros((n, n), dtype=np.uint8)
    if ang == 0:
        pts = [(j, 0) for j in range(-r, r + 1)]
    elif ang == 90:
        pts = [(0, k) for k in range(-r, r + 1)]
    elif ang == 45:
        pts = [(j, j) for j in range(-q, q + 1)]
    elif ang == 135:
        pts = [(-j, j) for j in range(-q, q + 1)]
    else:
        raise ValueError(ang)
    for j, k in pts:
        s[k + r, j + r] = 1
    return s, q


def comprobar(r):
    d = disk_se(r)
    assert d.shape == (2 * r + 1, 2 * r + 1), d.shape
    assert np.array_equal(d, disco_libro(r)), f"el disco del codigo no coincide con eq:disco (r={r})"
    cuentas = {"Disco": int(d.sum())}
    for a in _ANGLES:
        s = linear_se(r, a)
        s_libro, q = segmento_libro(r, a)
        assert np.array_equal(s, s_libro), f"el segmento de {a} grados no coincide con eq:segmentos (r={r})"
        esperado = 2 * r + 1 if a in (0, 90) else 2 * q + 1
        assert int(s.sum()) == esperado, (a, int(s.sum()), esperado)
        assert s[r, r] == 1, "el segmento no pasa por el centro"
        cuentas[f"Segmento {a}"] = int(s.sum())
    assert d[r, r] == 1
    return cuentas


for r in (R_FIGURA, R_ADOPTADO):
    c = comprobar(r)
    print(f"  r = {r}: cuadricula {2 * r + 1} x {2 * r + 1}; pixeles por elemento: "
          + ", ".join(f"{k} = {v}" for k, v in c.items()))
print(f"  _ANGLES de src = {_ANGLES}")

# ---------------------------------------------------------------- figura
aplicar_estilo()

elementos = [("Disco", disk_se(R_FIGURA))] + [
    (f"Segmento {a}°", linear_se(R_FIGURA, a)) for a in _ANGLES]
n = 2 * R_FIGURA + 1

# Cinco cuadros iguales a lo ancho de la caja de texto, con los rotulos debajo.
ANCHO = ANCHO_TEXTO_PULG
LADO = 0.98            # lado de cada cuadricula, en pulgadas (unos 2.3 mm por pixel)
MARGEN = 0.01          # para que el trazo del borde no quede recortado
HUECO = (ANCHO - 2 * MARGEN - 5 * LADO) / 4
ALTO_ROTULO = 0.30
ALTO = LADO + ALTO_ROTULO + 2 * MARGEN

fig = plt.figure(figsize=(ANCHO, ALTO))
cmap = ListedColormap(["white", GRIS_OSCURO])

for i, (rotulo, se) in enumerate(elementos):
    x0 = MARGEN + i * (LADO + HUECO)
    ax = fig.add_axes([x0 / ANCHO, (ALTO_ROTULO + MARGEN) / ALTO, LADO / ANCHO, LADO / ALTO])
    # Fila 0 arriba, como en la imagen: pcolormesh con el eje vertical invertido.
    ax.pcolormesh(np.arange(n + 1), np.arange(n + 1), se, cmap=cmap, vmin=0, vmax=1,
                  edgecolors=GRIS, linewidth=0.4, shading="flat")
    ax.set_xlim(0, n)
    ax.set_ylim(n, 0)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for borde in ax.spines.values():
        borde.set_linewidth(0.6)
        borde.set_color(NEGRO)
    # centro del elemento
    ax.plot(R_FIGURA + 0.5, R_FIGURA + 0.5, "o", ms=2.6, mfc="white", mec="white", mew=0)
    ax.text(0.5, -0.07, rotulo, transform=ax.transAxes, ha="center", va="top", fontsize=TAM_TEXTO)

guardar(fig, "fig_banco_se", ancho_libro=1.0)
plt.close(fig)
