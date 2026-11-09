# -*- coding: utf-8 -*-
"""Figura fig:ajuste_pso del libro (cap4, seccion del ajuste de los parametros).

QUE MUESTRA. Dos paneles sobre el ajuste del radio r y del peso m de la propuesta.
  (a) La aptitud en funcion del peso m, para r = 1 (gris, linea punteada) y r = 25 (azul, linea
      continua, el radio adoptado), leida de la grilla de cinco mil combinaciones (25 radios x 200
      pesos, de 0.01 a 2.00 cada 0.01). El rango de busqueda del enjambre, de 0.30 a 2.00, va
      sombreado en gris claro, y una linea discontinua marca m = 0.30. Se rotulan las tres cifras que
      da el libro: 1.7350 (r = 1) y 1.7057 (r = 25) en m = 0.30, y el maximo de la grilla, 1.7715, en
      r = 25 y m = 0.07, fuera del rango.
  (b) En que radio terminaron las 25 corridas del enjambre (las 25 configuraciones de particulas por
      iteraciones): 16 en r = 1, 1 en r = 14 y 8 en r = 25, la de r = 25 en azul. Las 25 terminaron
      con m = 0.30.

DE DONDE SALEN LAS CIFRAS (nada se escribe a mano; el script lee y comprueba):
  - experiments/results/metrics_reports/optimo_exacto_fo.csv: la grilla (columnas r, m, Fo). La escribe
    experiments/optimo_exacto_fo.py con la misma aptitud del enjambre (la de la Ecuacion de la aptitud
    del cap3, promediada sobre las tres escenas del ajuste).
  - experiments/results/metrics_reports/pso_grid_search_fo_propuesta.csv: las 25 corridas (columnas
    r_opt, m_opt, Fo_opt). La aptitud con que termino cada corrida coincide con la de la grilla en
    (r_opt, 0.30), y el script lo comprueba.

ESTILO: el comun de las figuras del libro (experiments/estilo_figuras_libro.py). El lienzo mide el
ancho de texto (6.30 pulgadas), que es el ancho con que el LaTeX la incluye (width=\\textwidth), asi
que la letra se imprime al tamano con que se dibuja: 10 pt los rotulos, 9.5 pt los numeros de los ejes.
Sin titulo dentro de la imagen. Si se cambia algo de lo dibujado, hay que revisar el \\caption y la
\\nota de fig:ajuste_pso en docs/libro_v4/caps/cap4_resultados.tex.

Salida: docs/libro_v4/figuras/fig_ajuste_pso.png (300 ppp)

Uso (desde la raiz del repo):  .venv\\Scripts\\python.exe -X utf8 experiments/make_fig_ajuste_pso_libro_v4.py
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

from estilo_figuras_libro import (ANCHO_TEXTO_PULG, AZUL, GRIS, GRIS_OSCURO, NEGRO, REPORTES,
                                  TAM_TEXTO, aplicar_estilo, guardar)

FRACCION = 1.0                       # el LaTeX la incluye con width=\textwidth
ANCHO = FRACCION * ANCHO_TEXTO_PULG  # 6.30 pulgadas
ALTO = 2.85

PISO, TECHO = 0.30, 2.00             # rango de busqueda del peso en el enjambre (cap3)
R_ADOPTADO, R_OTRO = 25, 1
Y_MIN, Y_MAX = 1.17, 1.92           # eje de la aptitud en el panel (a); arriba queda lugar para un rotulo
SOMBRA = "#e7e7e7"                  # gris claro del rango de busqueda (algo mas oscuro que GRIS_CLARO,
                                     # que en papel casi no se ve)
# Las cifras que da el libro (cap4, seccion del ajuste). El script comprueba que la figura las repita.
LIBRO = {"r1_piso": 1.7350, "r25_piso": 1.7057, "max": 1.7715, "max_r": 25, "max_m": 0.07,
         "corridas": {1: 16, 25: 8, 14: 1}}


def cargar():
    grilla = pd.read_csv(REPORTES / "optimo_exacto_fo.csv")
    corridas = pd.read_csv(REPORTES / "pso_grid_search_fo_propuesta.csv")

    # la grilla: 25 radios x 200 pesos, de 0.01 a 2.00
    assert len(grilla) == 5000, f"la grilla tiene {len(grilla)} filas, no 5000"
    assert sorted(grilla["r"].unique()) == list(range(1, 26)), "la grilla no tiene los radios 1 a 25"
    assert (grilla.groupby("r").size() == 200).all(), "algun radio no tiene 200 pesos"

    curva = {r: grilla[grilla["r"] == r].sort_values("m") for r in (R_OTRO, R_ADOPTADO)}

    def en(r, m):
        fila = curva[r][np.isclose(curva[r]["m"], m)]
        assert len(fila) == 1, f"no hay un unico punto r = {r}, m = {m} en la grilla"
        return float(fila["Fo"].iloc[0])

    cifras = {"r1_piso": en(R_OTRO, PISO), "r25_piso": en(R_ADOPTADO, PISO)}
    imax = grilla["Fo"].idxmax()
    cifras.update(max=float(grilla.loc[imax, "Fo"]), max_r=int(grilla.loc[imax, "r"]),
                  max_m=float(grilla.loc[imax, "m"]))

    # las cifras de la figura son las del libro (a cuatro decimales)
    for k in ("r1_piso", "r25_piso", "max"):
        assert round(cifras[k], 4) == LIBRO[k], f"{k}: la grilla da {cifras[k]:.4f}, el libro {LIBRO[k]}"
    assert cifras["max_r"] == LIBRO["max_r"] and np.isclose(cifras["max_m"], LIBRO["max_m"]), \
        "el maximo de la grilla no esta en r = 25, m = 0.07"

    # dentro del rango de busqueda la aptitud baja con m en los dos radios: el maximo queda en el piso
    for r in (R_OTRO, R_ADOPTADO):
        dentro = curva[r][curva[r]["m"] >= PISO - 1e-9]["Fo"].to_numpy()
        assert (np.diff(dentro) < 0).all(), f"con r = {r} la aptitud no baja en todo el rango"
    # y en el piso r = 1 supera a r = 25
    assert cifras["r1_piso"] > cifras["r25_piso"]

    # las 25 corridas: todas en m = 0.30; el reparto en el radio, recalculado
    assert len(corridas) == 25, f"hay {len(corridas)} corridas, no 25"
    assert np.allclose(corridas["m_opt"], PISO), "no todas las corridas terminaron en m = 0.30"
    reparto = corridas["r_opt"].value_counts().to_dict()
    assert reparto == LIBRO["corridas"], f"el reparto en el radio es {reparto}, no el del libro"
    # la aptitud final de cada corrida es la de la grilla en (r_opt, 0.30)
    for r in reparto:
        fo_grilla = float(grilla[(grilla["r"] == r) & np.isclose(grilla["m"], PISO)]["Fo"].iloc[0])
        fo_pso = corridas.loc[corridas["r_opt"] == r, "Fo_opt"].to_numpy()
        assert np.allclose(fo_pso, round(fo_grilla, 4), atol=5e-5), f"r = {r}: grilla y enjambre difieren"
        cifras[f"apt_r{r}"] = fo_grilla
    return curva, cifras, reparto


def panel_aptitud(ax, curva, cifras):
    ax.axvspan(PISO, TECHO, color=SOMBRA, lw=0, zorder=0)
    # la marca en m = 0.30 sube del eje hasta el punto de r = 1, para no cruzar los rotulos de arriba
    ax.plot([PISO, PISO], [Y_MIN, cifras["r1_piso"]], color=GRIS_OSCURO, lw=0.8, ls=(0, (4, 2.5)),
            zorder=1)

    c1, c25 = curva[R_OTRO], curva[R_ADOPTADO]
    # r = 1 punteada, para que se distinga de r = 25 tambien impresa en gris; discontinua no, porque esa
    # es la marca de m = 0.30
    ax.plot(c1["m"], c1["Fo"], color=GRIS_OSCURO, lw=1.3, ls=":", zorder=3, label=f"$r = {R_OTRO}$")
    ax.plot(c25["m"], c25["Fo"], color=AZUL, lw=1.6, zorder=4, label=f"$r = {R_ADOPTADO}$ (adoptado)")

    # los tres puntos que cita el libro
    kw = dict(marker="o", ms=4.2, mec="white", mew=0.6, ls="none", zorder=5)
    ax.plot([PISO], [cifras["r1_piso"]], mfc=GRIS_OSCURO, **kw)
    ax.plot([PISO], [cifras["r25_piso"]], mfc=AZUL, **kw)
    ax.plot([cifras["max_m"]], [cifras["max"]], mfc=AZUL, **kw)

    ax.annotate(f"{cifras['r1_piso']:.4f}", (PISO, cifras["r1_piso"]), xytext=(5, 3),
                textcoords="offset points", ha="left", va="bottom", fontsize=TAM_TEXTO, color=NEGRO)
    ax.annotate(f"{cifras['r25_piso']:.4f}", (PISO, cifras["r25_piso"]), xytext=(-5, -3),
                textcoords="offset points", ha="right", va="top", fontsize=TAM_TEXTO, color=NEGRO)
    ax.annotate(f"Máximo de la grilla: {cifras['max']:.4f}\n($r = {cifras['max_r']}$, "
                f"$m = {cifras['max_m']:.2f}$)", (cifras["max_m"], cifras["max"]), xytext=(6, 6),
                textcoords="offset points", ha="left", va="bottom", fontsize=TAM_TEXTO, color=NEGRO,
                linespacing=1.15)

    ax.text(0.5 * (PISO + TECHO), 1.205, "Rango de búsqueda del enjambre", ha="center", va="bottom",
            fontsize=TAM_TEXTO, color=GRIS_OSCURO)

    ax.set_xlim(0, 2.05)
    ax.set_ylim(Y_MIN, Y_MAX)
    ax.xaxis.set_major_locator(FixedLocator([0, 0.30, 0.50, 1.00, 1.50, 2.00]))
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    ax.yaxis.set_major_locator(FixedLocator(np.arange(1.2, 1.81, 0.1)))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    ax.set_xlabel("Peso $m$")
    ax.set_ylabel("Aptitud")
    ax.legend(loc="upper right", handlelength=1.8, borderpad=0.4, labelspacing=0.3)


def panel_corridas(ax, reparto):
    radios = sorted(reparto)
    alturas = [reparto[r] for r in radios]
    colores = [AZUL if r == R_ADOPTADO else GRIS for r in radios]
    ax.bar(radios, alturas, width=2.4, color=colores, edgecolor=GRIS_OSCURO, linewidth=0.6, zorder=2)
    for r, h in zip(radios, alturas):
        ax.text(r, h + 0.35, f"{h}", ha="center", va="bottom", fontsize=TAM_TEXTO)
    ax.text(13.5, 13.0, f"Las {sum(alturas)} corridas\nterminaron con\n$m = {PISO:.2f}$", ha="center",
            va="center", fontsize=TAM_TEXTO, color=NEGRO, linespacing=1.2)

    ax.set_xlim(-1.5, 27.5)
    ax.set_ylim(0, 18.5)
    ax.xaxis.set_major_locator(FixedLocator(radios))
    ax.yaxis.set_major_locator(FixedLocator([0, 4, 8, 12, 16]))
    ax.set_xlabel("Radio $r$ final")
    ax.set_ylabel("Número de corridas")


def main():
    curva, cifras, reparto = cargar()

    aplicar_estilo()
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(ANCHO, ALTO), layout="constrained",
                                   gridspec_kw={"width_ratios": [2.15, 1]})
    panel_aptitud(axa, curva, cifras)
    panel_corridas(axb, reparto)
    for ax, letra in ((axa, "(a)"), (axb, "(b)")):
        ax.text(0.0, 1.03, letra, transform=ax.transAxes, ha="left", va="bottom", fontsize=TAM_TEXTO)
    fig.get_layout_engine().set(w_pad=0.02, h_pad=0.02, wspace=0.06)
    guardar(fig, "fig_ajuste_pso", ancho_libro=FRACCION)
    plt.close(fig)

    print("\n    cifras de la figura (optimo_exacto_fo.csv y pso_grid_search_fo_propuesta.csv):")
    print(f"      aptitud en m = 0.30: r = 1 -> {cifras['r1_piso']:.4f}; r = 25 -> {cifras['r25_piso']:.4f}")
    print(f"      maximo de la grilla: {cifras['max']:.4f} en r = {cifras['max_r']}, m = {cifras['max_m']:.2f}")
    print(f"      corridas por radio final: {dict(sorted(reparto.items()))}; todas con m = 0.30")
    for r in sorted(reparto):
        print(f"      aptitud final de las corridas en r = {r}: {cifras[f'apt_r{r}']:.4f}")


if __name__ == "__main__":
    main()
