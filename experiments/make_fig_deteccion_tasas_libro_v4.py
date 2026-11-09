# -*- coding: utf-8 -*-
"""Figura fig:deteccion_tasas del libro (cap4, deteccion de objetos): la tasa equilibrada de
cada entrada fusionada y la diferencia entre la propuesta y el Top-Hat clasico.

POR QUE ESTA FIGURA. La Tabla tab:v2_tasas da la tasa equilibrada de cada entrada como un promedio de tres
semillas, y la Tabla tab:deteccion_tophat da la diferencia con el Top-Hat clasico como un numero con su
intervalo. Ninguna de las dos deja ver cuanto cambia el resultado de una semilla a otra. Esta figura lo
muestra, y deja ver a simple vista que la ventaja de la propuesta sobre el Top-Hat clasico es pequena y que
cambia de signo segun el par de semillas.

QUE MUESTRA. Dos paneles, uno al lado del otro.
  (a) Tasa equilibrada de las ocho entradas fusionadas de la tabla (las siete fusiones y el promedio simple),
      de mayor a menor media, de arriba abajo. Un punto por semilla (tres por entrada) y una linea vertical
      corta en la media de las tres, que es el valor de la tabla. La propuesta en azul, el Top-Hat clasico en
      gris oscuro, las demas en gris claro.
  (b) Diferencia de tasa equilibrada, propuesta menos Top-Hat clasico, en puntos porcentuales: arriba, las
      nueve diferencias entre pares de semillas (cada semilla de la propuesta contra cada semilla del Top-Hat
      clasico); abajo, la estimacion principal, 3.0 puntos, con su intervalo de confianza del 95 %, de 0.0 a
      6.0. Una linea vertical en cero: a la derecha, la propuesta acierta mas; a la izquierda, menos.
Los dos paneles usan la misma escala horizontal: un punto porcentual mide lo mismo en los dos, para que la
diferencia del panel (b) se pueda comparar a ojo con la distancia entre las entradas del panel (a).

DE DONDE SALEN LAS CIFRAS (experiments/results/metrics_reports/, umbral principal «fppi»):
  - Medias de la tasa equilibrada: m3fd_v2_tasas_precisas.csv (o m3fd_v2_tasas.csv si no existe), la misma
    fuente que la tabla tab:v2_tasas en tools/generar_tablas_libro.py.
  - Diferencias entre pares de semillas: m3fd_v2_pares_semillas.csv.
  - Estimacion principal e intervalo: m3fd_v2_contrastes_precisos.csv (o m3fd_v2_contrastes.csv).
  - La tasa de cada semilla no esta guardada en ningun CSV; se recupera de los dos primeros, sin aproximar
    nada salvo el redondeo a cuatro decimales de los pares. En analizar_v2.py la tasa equilibrada es lineal en
    los aciertos, asi que el par (i, j) frente al metodo O vale d(i, j) = P_i - O_j, donde P_i es la tasa de
    la semilla i de la propuesta y O_j la de la semilla j del otro metodo. Promediando sobre j sale
    P_i = media_j d(i, j) + media(O), y promediando sobre i sale O_j = media(P) - media_i d(i, j). La tasa de
    cada semilla de la propuesta se obtiene asi frente a los siete metodos y se promedian las siete. El script
    comprueba que las siete coinciden, que las tres semillas promedian el valor de la tabla y que con ellas se
    reconstruyen los 63 pares del CSV, todo dentro del error del redondeo (1e-4 en proporcion, 0.01 puntos).

Tamano de letra: el lienzo mide el ancho de texto (6.30 pulgadas), el ancho con que el LaTeX lo incluye
(width=\\textwidth), asi que la letra se imprime al tamano con que se dibuja: 10 pt los rotulos de los ejes y
9.5 pt los numeros, los nombres de las entradas y los textos de los paneles. Estilo: el comun de las figuras
del libro (experiments/estilo_figuras_libro.py).

Salida: docs/libro_v4/figuras/fig_deteccion_tasas.png (300 ppp)

Uso (desde la raiz del repo):  .venv\\Scripts\\python.exe -X utf8 experiments/make_fig_deteccion_tasas_libro_v4.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator

from estilo_figuras_libro import (ANCHO_TEXTO_PULG, AZUL, GRIS, GRIS_OSCURO, NEGRO, NOMBRES, PROPUESTA,
                                  REPORTES, TAM_MARCAS, TAM_TEXTO, aplicar_estilo, guardar)

FRACCION = 1.0                       # el LaTeX la incluye con width=\textwidth
ANCHO = FRACCION * ANCHO_TEXTO_PULG  # 6.30 pulgadas
ALTO = 3.0
PUNTO = "fppi"                       # umbral principal: igual falsos positivos por imagen
CLASICO = "TopHat_Clasico"

# Rangos de los ejes, en puntos porcentuales. Los dos paneles comparten la escala (pulgadas por punto).
RANGO_A = (45.0, 70.0)
RANGO_B = (-5.0, 10.0)
DESPLAZA = {0: -0.2, 1: 0.0, 2: 0.2}  # separacion vertical de los puntos de cada semilla, en filas
TOL = 2e-4                            # error de redondeo admisible, en proporcion


def csv_preciso(base, preciso):
    """La version sin redondear (tasas_precisas_v2.py) si existe; si no, la oficial. Como en las tablas."""
    return REPORTES / preciso if (REPORTES / preciso).exists() else REPORTES / f"{base}.csv"


def cargar():
    t = pd.read_csv(csv_preciso("m3fd_v2_tasas", "m3fd_v2_tasas_precisas.csv"))
    medias = t[t["punto"] == PUNTO].set_index("entrada")["equilibrada"].astype(float)
    p = pd.read_csv(REPORTES / "m3fd_v2_pares_semillas.csv")
    pares = p[p["punto"] == PUNTO]
    c = pd.read_csv(csv_preciso("m3fd_v2_contrastes", "m3fd_v2_contrastes_precisos.csv"))
    contraste = c[(c["punto"] == PUNTO) & (c["contra"] == CLASICO)].iloc[0]
    otros = sorted(pares["contra"].unique())
    assert set(otros) | {PROPUESTA} == set(medias.index), "los pares y las tasas no tienen las mismas entradas"
    assert len(medias) == 8, "la tabla tab:v2_tasas tiene ocho entradas fusionadas"
    return medias, pares, contraste, otros


def tasas_por_semilla(medias, pares, otros):
    """La tasa equilibrada de cada semilla de cada entrada, a partir de las medias y de los pares.

    d(i, j) = P_i - O_j  =>  P_i = media_j d(i, j) + media(O)  y  O_j = media(P) - media_i d(i, j).
    """
    por_semilla, estim_prop = {}, []
    for o in otros:
        q = pares[pares["contra"] == o].pivot(index="semilla_propuesta", columns="semilla_otro",
                                              values="diferencia").astype(float)
        assert q.shape == (3, 3) and not q.isna().any().any(), f"faltan pares de semillas frente a {o}"
        estim_prop.append(q.mean(axis=1) + medias[o])
        por_semilla[o] = medias[PROPUESTA] - q.mean(axis=0)
    e = pd.concat(estim_prop, axis=1)
    dispersion = float((e.max(axis=1) - e.min(axis=1)).max())
    assert dispersion < TOL, f"las siete estimaciones de la propuesta no coinciden ({dispersion:.1e})"
    por_semilla[PROPUESTA] = e.mean(axis=1)
    # controles: las tres semillas promedian el valor de la tabla y reconstruyen los pares del CSV
    for k, v in por_semilla.items():
        assert len(v) == 3, f"{k} no tiene tres semillas"
        assert abs(float(v.mean()) - medias[k]) < TOL, f"las semillas de {k} no promedian su tasa de la tabla"
    for _, f in pares.iterrows():
        rec = por_semilla[PROPUESTA][f["semilla_propuesta"]] - por_semilla[f["contra"]][f["semilla_otro"]]
        assert abs(rec - f["diferencia"]) < TOL, f"no se reconstruye el par {tuple(f)}"
    return {k: v.sort_index() for k, v in por_semilla.items()}, dispersion


def estilo_entrada(k):
    """(relleno, borde, color de la media) de cada entrada."""
    if k == PROPUESTA:
        return AZUL, AZUL, AZUL
    if k == CLASICO:
        return GRIS_OSCURO, GRIS_OSCURO, NEGRO
    return GRIS, GRIS_OSCURO, GRIS_OSCURO


def dibujar(medias, por_semilla, pares_th, contraste):
    orden = medias.sort_values(ascending=False).index.tolist()     # el orden de la tabla tab:v2_tasas
    fig = plt.figure(figsize=(ANCHO, ALTO))
    ax_a = fig.add_axes([0.25, 0.2, 0.4, 0.7])
    ax_b = fig.add_axes([0.7, 0.2, 0.25, 0.7])

    # ---------------------------------------------------------------- (a) tasa de cada entrada
    for fila, k in enumerate(orden, start=1):
        relleno, borde, color_media = estilo_entrada(k)
        v = 100 * por_semilla[k]
        ax_a.plot(v.values, [fila + DESPLAZA[int(s)] for s in v.index], "o", ms=4.6, mfc=relleno, mec=borde,
                  mew=0.6, zorder=3, clip_on=False)
        ax_a.plot([100 * medias[k]] * 2, [fila - 0.36, fila + 0.36], color=color_media, lw=1.6, zorder=4,
                  solid_capstyle="butt")
    ax_a.set_yticks(range(1, len(orden) + 1), [NOMBRES[k] for k in orden], fontsize=TAM_MARCAS)
    ax_a.set_ylim(len(orden) + 0.6, 0.4)
    ax_a.set_xlim(*RANGO_A)
    ax_a.xaxis.set_major_locator(MultipleLocator(5))
    ax_a.xaxis.grid(True)
    ax_a.tick_params(axis="y", length=0)
    ax_a.set_xlabel("Tasa equilibrada (%)")
    clave = [Line2D([], [], ls="none", marker="o", ms=4.6, mfc=GRIS, mec=GRIS_OSCURO, mew=0.6,
                    label="Una semilla"),
             Line2D([], [], ls="none", marker="|", ms=9, mew=1.6, color=GRIS_OSCURO,
                    label="Media de las tres")]
    ax_a.legend(handles=clave, loc="upper left", fontsize=TAM_MARCAS, handletextpad=0.3,
                borderpad=0.4, labelspacing=0.35, borderaxespad=0.4)

    # ---------------------------------------------------------------- (b) propuesta menos Top-Hat clasico
    y_pares, y_estim = 2.7, 6.4
    v = 100 * pares_th["diferencia"].to_numpy(float)
    y = y_pares + np.array([DESPLAZA[int(s)] for s in pares_th["semilla_propuesta"]])
    ax_b.axvline(0, color=NEGRO, lw=0.8, zorder=2)
    ax_b.plot(v, y, "o", ms=4.6, mfc=GRIS, mec=GRIS_OSCURO, mew=0.6, zorder=3)
    est, lo, hi = (100 * float(contraste[c]) for c in ("diferencia", "ic_lo", "ic_hi"))
    ax_b.plot([lo, hi], [y_estim] * 2, color=NEGRO, lw=1.2, zorder=3, solid_capstyle="butt")
    for x in (lo, hi):
        ax_b.plot([x, x], [y_estim - 0.22, y_estim + 0.22], color=NEGRO, lw=1.2, zorder=3)
    ax_b.plot([est], [y_estim], "o", ms=5.6, mfc=NEGRO, mec=NEGRO, zorder=4)
    # Los textos del panel, a la derecha del cero y alineados a la izquierda: en una sola linea no caben
    # sin cruzar la linea del cero.
    x_txt = 0.6
    ax_b.text(x_txt, y_pares - 0.55, "Nueve pares\nde semillas", fontsize=TAM_MARCAS, ha="left",
              va="bottom", linespacing=1.1)
    ax_b.text(x_txt, y_estim - 0.55, "Estimación\ne IC 95 %", fontsize=TAM_MARCAS, ha="left",
              va="bottom", linespacing=1.1)
    ax_b.text(x_txt, y_estim + 0.5, f"{est:.1f} [{lo:.1f}, {hi:.1f}]", fontsize=TAM_MARCAS,
              ha="left", va="top")
    ax_b.set_ylim(len(orden) + 0.6, 0.4)
    ax_b.set_yticks([])
    ax_b.set_xlim(*RANGO_B)
    ax_b.xaxis.set_major_locator(MultipleLocator(5))
    # sin cuadricula: la unica referencia de este panel es el cero, y la linea del 5 cruzaba los textos
    ax_b.set_xlabel("Propuesta menos Top-Hat clásico\n(puntos porcentuales)")

    # ---------------------------------------------------------------- disposicion, con la misma escala
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    dpi = fig.dpi
    caja_a = ax_a.get_tightbbox(r)
    pos_a = ax_a.get_position()
    rotulos = pos_a.x0 * ANCHO - caja_a.x0 / dpi                  # lo que ocupan los nombres a la izquierda
    caja_b = ax_b.get_tightbbox(r)
    pos_b = ax_b.get_position()
    sobra_b = caja_b.x1 / dpi - pos_b.x1 * ANCHO                   # lo que asoma a la derecha del panel (b)
    abajo = max(pos_a.y0 * ALTO - caja_a.y0 / dpi, pos_b.y0 * ALTO - caja_b.y0 / dpi)
    margen, hueco, arriba = 0.03, 0.30, 0.24
    x0 = margen + rotulos
    util = ANCHO - x0 - hueco - sobra_b - margen
    escala = util / ((RANGO_A[1] - RANGO_A[0]) + (RANGO_B[1] - RANGO_B[0]))   # pulgadas por punto
    w_a, w_b = escala * (RANGO_A[1] - RANGO_A[0]), escala * (RANGO_B[1] - RANGO_B[0])
    y0 = margen + abajo
    alto = ALTO - y0 - arriba
    ax_a.set_position([x0 / ANCHO, y0 / ALTO, w_a / ANCHO, alto / ALTO])
    ax_b.set_position([(x0 + w_a + hueco) / ANCHO, y0 / ALTO, w_b / ANCHO, alto / ALTO])
    for ax, letra in ((ax_a, "(a)"), (ax_b, "(b)")):
        ax.text(0.0, 1.0 + 0.06 / alto, letra, transform=ax.transAxes, fontsize=TAM_TEXTO, ha="left",
                va="bottom")
    # las dos escalas, comprobadas sobre la posicion final
    ia = ax_a.get_position().width * ANCHO / (RANGO_A[1] - RANGO_A[0])
    ib = ax_b.get_position().width * ANCHO / (RANGO_B[1] - RANGO_B[0])
    assert abs(ia - ib) < 1e-9, "los paneles no tienen la misma escala"
    return fig, orden, escala


def main():
    medias, pares, contraste, otros = cargar()
    por_semilla, dispersion = tasas_por_semilla(medias, pares, otros)
    pares_th = pares[pares["contra"] == CLASICO].sort_values(["semilla_otro", "semilla_propuesta"])
    assert len(pares_th) == 9, "no son nueve pares de semillas frente al Top-Hat clasico"
    # lo que dice el texto del libro: 3.0 puntos, de 0.0 a 6.0, y pares de -3.1 a 7.8
    assert f"{100 * contraste['diferencia']:.1f}" == "3.0"
    assert abs(contraste["pares_min"] - pares_th["diferencia"].min()) < TOL
    assert abs(contraste["pares_max"] - pares_th["diferencia"].max()) < TOL

    aplicar_estilo()
    fig, orden, escala = dibujar(medias, por_semilla, pares_th, contraste)
    guardar(fig, "fig_deteccion_tasas", ancho_libro=FRACCION)
    plt.close(fig)

    # las cifras de la figura, para el texto
    print(f"\n    escala comun: {escala:.4f} pulgadas por punto porcentual")
    print(f"    tasa de cada semilla recuperada con error menor que {dispersion * 100:.4f} puntos")
    print("    (a) tasa equilibrada, %: media (tabla) y semillas 0, 1, 2")
    for k in orden:
        s = ", ".join(f"{100 * x:.2f}" for x in por_semilla[k].values)
        print(f"      {NOMBRES[k]:20s} {100 * medias[k]:6.2f}   [{s}]")
    print("    (b) propuesta menos Top-Hat clasico, puntos (semilla propuesta, semilla Top-Hat):")
    for _, f in pares_th.iterrows():
        print(f"      ({int(f['semilla_propuesta'])}, {int(f['semilla_otro'])})  {100 * f['diferencia']:+.2f}")
    neg = int((pares_th["diferencia"] < 0).sum())
    print(f"      {neg} de 9 pares negativos; semillas del Top-Hat con pares negativos: "
          f"{sorted(pares_th.loc[pares_th['diferencia'] < 0, 'semilla_otro'].unique().tolist())}")
    print(f"      estimacion {100 * contraste['diferencia']:.2f}  IC [{100 * contraste['ic_lo']:.2f}, "
          f"{100 * contraste['ic_hi']:.2f}]")


if __name__ == "__main__":
    main()
