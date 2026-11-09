# -*- coding: utf-8 -*-
"""Figura fig:m3fd_ejemplo del libro: un cuadro de la prueba de M3FD con las detecciones del Top-Hat
clasico y de la propuesta (Seccion 3.5 del libro).

QUE MUESTRA. Cuatro paneles de un mismo cuadro, en una grilla de dos por dos:
  arriba   la imagen visible y la imagen infrarroja, en escala de grises, como las recibe el detector.
           En cada una, un recuadro negro marca el objeto que solo encuentran los detectores de esa
           imagen (objeto de una sola camara);
  abajo    la fusion del Top-Hat clasico (r = 5, m = 1) y la de la propuesta (r = 25, m = 0.30), cada una
           con las detecciones de personas y luces de su propio detector: la semilla 0, los pesos del
           final del entrenamiento (last.pt, los que evaluo evaluar_v2.py) y su umbral calibrado.
Recuadros finos: gris oscuro en el Top-Hat clasico, azul #4472c4 en la propuesta, negro en las imagenes
originales; linea continua para personas y discontinua para luces. Un borde blanco fino debajo de cada
recuadro lo hace visible sobre el fondo oscuro de la escena nocturna.

COMO SE ELIGE EL CUADRO (sin mirar las detecciones de las fusiones):
  1. Cuadros de la prueba final: m3fd_v2_prueba.csv con entra = True (1067 cuadros).
  2. Objetos de una sola camara, con la regla de analizar_v2.py: la mayoria de los tres detectores de la
     visible (semillas 3, 4 y 5) lo encuentra y la de los de la infrarroja no, o al reves; cada detector
     con su umbral calibrado (umbral_fppi de m3fd_v2_umbrales.csv), IoU >= 0.5.
  3. Candidatos: los cuadros con al menos un objeto de una sola camara de cada camara (son 49) y con
     personas y luces marcadas, las dos clases del analisis.
  4. Se toma el de mayor area mediana de sus objetos de una sola camara, para que se vean en la pagina.
El resultado es el cuadro 00437 (de noche). En el, el detector del Top-Hat clasico encuentra uno de los
dos objetos de una sola camara (el semaforo) y el de la propuesta ninguno; se muestra igual, porque el
cuadro no se eligio por el resultado.

DE DONDE SALE CADA COSA (nada se dibuja de memoria):
  - Las cajas: experiments/results/metrics_reports/m3fd_v2_predicciones.csv, las predicciones crudas
    (confianza >= 0.05) que guardo evaluar_v2.py y que uso analizar_v2.py. Se dibujan las de confianza
    igual o mayor que el umbral del detector. Con --verificar, se vuelve a correr el detector (last.pt,
    imgsz 640, procesador) sobre el cuadro y se comprueba que da las mismas cajas.
  - Los umbrales: m3fd_v2_umbrales.csv, columna umbral_fppi (0.26 el Top-Hat clasico y 0.25 la
    propuesta, semilla 0).
  - Las cajas marcadas (verdad de terreno) y los objetos de una sola camara: las etiquetas de
    datasets/m3fd2_VIS/labels, leidas con las funciones de analizar_v2.py (que se importa, no se corre).
  - Las imagenes: datasets/m3fd2_<entrada>/images/<parte>/<id>.jpg, las mismas que vio cada detector. Se
    comprueba que coinciden, salvo la compresion JPEG, con la fusion recalculada desde src/ a partir de
    data/M3FD_Detection (propuesta: fuse_optimal r = 25, m = 0.30, modo «sum»; Top-Hat clasico:
    tophat_classic_fusion r = 5).

ESTILO: el comun de las figuras del libro (experiments/estilo_figuras_libro.py), como los montajes de la
seccion de calidad: rotulo arriba de cada panel a 10 pt, marco fino gris oscuro y el de la propuesta en
azul. El lienzo mide el ancho de la caja de texto (160 mm = 6.30 pulgadas); el LaTeX la incluye con
width=\\textwidth.

Salida: docs/libro_v4/figuras/fig_m3fd_ejemplo.png (300 ppp)

Uso (desde la raiz del repo):
    .venv\\Scripts\\python.exe -X utf8 experiments/make_fig_m3fd_ejemplo_libro_v4.py [--verificar]
"""
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
os.chdir(RAIZ)
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(RAIZ / "experiments" / "detection_m3fd"))
sys.path.insert(0, str(RAIZ))

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

import analizar_v2 as A          # solo sus funciones (leer_gt, indexar, detecciones); su main() no se corre
from estilo_figuras_libro import (ANCHO_TEXTO_PULG, AZUL, GRIS_OSCURO, NEGRO, NOMBRES, REPORTES,
                                  TAM_LEYENDA, TAM_TEXTO, aplicar_estilo, guardar)

NOMBRE = "fig_m3fd_ejemplo"
DATOS = RAIZ / "datasets"
M3FD = RAIZ / "data" / "M3FD_Detection"
PESOS = RAIZ / "runs" / "m3fd_v2"
VIS, IR, TH, PROP = "VIS", "IR", "TopHat_Clasico", "Propuesta_Novedosa"
SEMILLAS_REF = {VIS: (3, 4, 5), IR: (3, 4, 5)}
SEMILLA = 0                         # la de las fusiones que se dibuja

# disposicion, en pulgadas
MARGEN = 0.02
HUECO_H = 0.08                      # entre columnas
HUECO_V = 0.06                      # entre el pie de la fila de arriba y los rotulos de la de abajo
ALTO_ROTULO = 0.21                  # franja del rotulo, sobre cada panel
ALTO_LEYENDA = 0.50                 # dos renglones de leyenda, debajo de la grilla
LW_MARCO = 0.5
LW_PROPUESTA = 1.6                  # el marco azul de la propuesta, como en los montajes
LW_CAJA = 1.2                       # recuadros de los objetos
LW_BORDE_BLANCO = 1.7               # borde blanco por debajo de cada recuadro (visible de noche)
GUIONES = (0, (3.5, 2.0))           # linea discontinua de las luces


# ---------------------------------------------------------------- datos
def cargar_predicciones():
    pred = pd.read_csv(REPORTES / "m3fd_v2_predicciones.csv").drop_duplicates()
    pred["imagen"] = pred.imagen.map(lambda x: f"{int(x):05d}")
    umb = pd.read_csv(REPORTES / "m3fd_v2_umbrales.csv")
    umbral = {(e, int(s)): float(t) for e, s, t in zip(umb.entrada, umb.semilla, umb.umbral_fppi)}
    return pred, umbral


def elegir_cuadro(pred, umbral):
    """Aplica el criterio del docstring. Devuelve (id, parte, gt, solo_visible, solo_infrarroja)."""
    prueba = pd.read_csv(REPORTES / "m3fd_v2_prueba.csv")
    prueba = prueba[prueba.entra]
    parte_de = {f"{int(i):05d}": p for i, p in zip(prueba.id, prueba.parte)}
    gt = A.leer_gt(["test", "val"], set(parte_de))
    det = A.indexar(pred[pred.entrada.isin([VIS, IR])], ["test", "val"])
    claves, M = None, {}
    for e, semillas in SEMILLAS_REF.items():
        for s in semillas:
            d = A.detecciones(det[(e, s)], gt, umbral[(e, s)])
            claves = claves or sorted(d)
            M[(e, s)] = np.array([d[c] for c in claves])
    mayoria = {e: np.mean([M[(e, s)] for s in ss], axis=0) > 0.5 for e, ss in SEMILLAS_REF.items()}
    solo_v, solo_i = mayoria[VIS] & ~mayoria[IR], mayoria[IR] & ~mayoria[VIS]
    print(f"  prueba: {len(gt)} cuadros; objetos solo de la visible {solo_v.sum()}, solo de la "
          f"infrarroja {solo_i.sum()}, de las dos {(mayoria[VIS] & mayoria[IR]).sum()}")
    img = np.array([c.split("|")[0] for c in claves])
    cand = []
    for im in sorted(set(img[solo_v]) & set(img[solo_i])):
        if not (gt[im]["People"] and gt[im]["Lamp"]):
            continue
        areas = []
        for c in np.array(claves)[(img == im) & (solo_v | solo_i)]:
            _, clase, j = c.split("|")
            x1, y1, x2, y2 = gt[im][clase][int(j)]
            areas.append((x2 - x1) * (y2 - y1))
        cand.append((float(np.median(areas)), im))
    n_ambas = len(set(img[solo_v]) & set(img[solo_i]))
    print(f"  cuadros con objetos de una sola camara de las dos camaras: {n_ambas}; con personas y "
          f"luces marcadas: {len(cand)}")
    area, im = max(cand)
    print(f"  elegido: {im} ({parte_de[im]}), area mediana de sus objetos de una sola camara "
          f"{area:.0f} px2")
    sel = img == im
    marca = lambda m: {(c.split("|")[1], int(c.split("|")[2])) for c in np.array(claves)[sel & m]}
    return im, parte_de[im], gt[im], marca(solo_v), marca(solo_i)


def leer_imagen(entrada, parte, im):
    ruta = DATOS / f"m3fd2_{entrada}" / "images" / parte / f"{im}.jpg"
    g = cv2.imread(str(ruta), cv2.IMREAD_GRAYSCALE)
    assert g is not None, f"no se pudo leer {ruta}"
    return g


def comprobar_fusiones(im, imagenes):
    """Las imagenes del conjunto tienen que ser la fusion de src/, salvo la compresion JPEG."""
    from src.fusion.optimal_top_hat import fuse_optimal
    from src.fusion.comparatives import tophat_classic_fusion
    v = cv2.imread(str(M3FD / "Vis" / f"{im}.png"), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
    r = cv2.imread(str(M3FD / "Ir" / f"{im}.png"), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
    calc = {VIS: v, IR: r, TH: tophat_classic_fusion(v, r, r=5),
            PROP: fuse_optimal(v, r, 25, 0.30, mode="sum")}
    for e, f in calc.items():
        f8 = (np.clip(f, 0, 1) * 255).astype(np.uint8).astype(int)
        dif = np.abs(f8 - imagenes[e].astype(int))
        print(f"  {e}: diferencia con la recalculada desde src, media {dif.mean():.2f} y percentil 99 "
              f"{np.percentile(dif, 99):.0f} niveles de gris (compresion JPEG)")
        assert dif.mean() < 2.0, f"la imagen de {e} no coincide con la fusion de src"


def cajas_detectadas(pred, umbral, entrada, im):
    d = pred[(pred.entrada == entrada) & (pred.semilla == SEMILLA) & (pred.imagen == im)]
    d = d[d.conf >= umbral[(entrada, SEMILLA)]]
    return [(c, (x1, y1, x2, y2), cf) for c, x1, y1, x2, y2, cf in
            zip(d.clase, d.x1, d.y1, d.x2, d.y2, d.conf)]


def informar(im, gt, solo_v, solo_i, pred, umbral):
    """Que objeto marcado encuentra cada fusion (semilla 0), para el texto y la nota."""
    for e in (TH, PROP):
        u = umbral[(e, SEMILLA)]
        d = pred[(pred.entrada == e) & (pred.semilla == SEMILLA) & (pred.imagen == im)]
        det = {c: list(zip(g.conf.values, g[["x1", "y1", "x2", "y2"]].values.tolist()))
               for c, g in d.groupby("clase")}
        enc = A.detecciones({im: det}, {im: gt}, u)
        cajas = cajas_detectadas(pred, umbral, e, im)
        print(f"\n  {NOMBRES[e]} (semilla {SEMILLA}, umbral {u:.2f}): "
              f"{sum(c == 'People' for c, _, _ in cajas)} personas y "
              f"{sum(c == 'Lamp' for c, _, _ in cajas)} luces sobre el umbral")
        for c in A.CLASES:
            for j, caja in enumerate(gt[c]):
                tipo = ("solo visible" if (c, j) in solo_v else
                        "solo infrarroja" if (c, j) in solo_i else "otro")
                print(f"    {c:6s} {j}  {tuple(round(x) for x in caja)}  {tipo:15s}  "
                      f"{'encontrado' if enc[f'{im}|{c}|{j}'] else 'no'}")


def verificar_detector(pred, im, parte):
    """Vuelve a correr cada detector sobre el cuadro y compara con el CSV."""
    from ultralytics import YOLO        # se importa al final: cambia cv2.imread
    for e in (TH, PROP):
        pesos = PESOS / f"{e}_s{SEMILLA}" / "weights" / "last.pt"
        ruta = DATOS / f"m3fd2_{e}" / "images" / parte / f"{im}.jpg"
        r = YOLO(str(pesos)).predict(str(ruta), conf=0.05, imgsz=640, verbose=False, device="cpu")[0]
        nuevas = sorted((A.CLASES[0] if int(c) == 0 else A.CLASES[1],
                         tuple(round(float(x), 1) for x in caja), round(float(cf), 4))
                        for caja, c, cf in zip(r.boxes.xyxy.cpu().numpy(), r.boxes.cls.cpu().numpy(),
                                               r.boxes.conf.cpu().numpy()) if int(c) in (0, 4))
        d = pred[(pred.entrada == e) & (pred.semilla == SEMILLA) & (pred.imagen == im)]
        csv = sorted((c, (x1, y1, x2, y2), cf) for c, x1, y1, x2, y2, cf in
                     zip(d.clase, d.x1, d.y1, d.x2, d.y2, d.conf))
        iguales = len(nuevas) == len(csv) and all(
            a[0] == b[0] and np.allclose(a[1], b[1], atol=0.11) and abs(a[2] - b[2]) < 1e-3
            for a, b in zip(nuevas, csv))
        print(f"  verificacion {e}: {len(nuevas)} cajas ahora, {len(csv)} en el CSV -> "
              f"{'iguales' if iguales else 'DISTINTAS'}")
        assert iguales, f"el detector {e} no reproduce las cajas del CSV"


# ---------------------------------------------------------------- dibujo
def recuadro(ax, caja, color, clase):
    x1, y1, x2, y2 = caja
    ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, edgecolor=color, linewidth=LW_CAJA,
                           linestyle="-" if clase == "People" else GUIONES, joinstyle="miter",
                           path_effects=[pe.Stroke(linewidth=LW_BORDE_BLANCO, foreground="white"),
                                         pe.Normal()]))


def panel(fig, alto_fig, fila, col, panel_w, panel_h, img, rotulo, prop=False):
    x0 = MARGEN + col * (panel_w + HUECO_H)
    y0 = alto_fig - MARGEN - ALTO_ROTULO - panel_h - fila * (ALTO_ROTULO + panel_h + HUECO_V)
    ax = fig.add_axes([x0 / ANCHO_TEXTO_PULG, y0 / alto_fig,
                       panel_w / ANCHO_TEXTO_PULG, panel_h / alto_fig])
    ax.imshow(img, cmap="gray", vmin=0, vmax=255, aspect="auto", interpolation="lanczos")
    ax.set_xlim(-0.5, img.shape[1] - 0.5)
    ax.set_ylim(img.shape[0] - 0.5, -0.5)
    ax.set_title(rotulo, fontsize=TAM_TEXTO, pad=3, color=AZUL if prop else NEGRO)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_edgecolor(AZUL if prop else GRIS_OSCURO)
        sp.set_linewidth(LW_PROPUESTA if prop else LW_MARCO)
    return ax


def renglon(fig, ax, y, items):
    """Un renglon de leyenda centrado. items: (tipo, color, estilo, texto); tipo 'linea' o 'caja'."""
    rend = fig.canvas.get_renderer()
    ANCHO_MUESTRA, ESP_TEXTO, ESP_ITEM = 0.30, 0.07, 0.30
    textos = [ax.text(0, y, t, fontsize=TAM_LEYENDA, va="center", ha="left") for *_, t in items]
    anchos = [t.get_window_extent(rend).width / fig.dpi for t in textos]
    total = sum(ANCHO_MUESTRA + ESP_TEXTO + w for w in anchos) + ESP_ITEM * (len(items) - 1)
    x = (ANCHO_TEXTO_PULG - total) / 2
    for (tipo, color, estilo, _), t, w in zip(items, textos, anchos):
        if tipo == "linea":
            ax.add_line(Line2D([x, x + ANCHO_MUESTRA], [y, y], color=color, linewidth=LW_CAJA + 0.3,
                               linestyle=estilo))
        else:
            ax.add_patch(Rectangle((x + 0.04, y - 0.055), ANCHO_MUESTRA - 0.08, 0.11, fill=False,
                                   edgecolor=color, linewidth=LW_CAJA + 0.3))
        t.set_x(x + ANCHO_MUESTRA + ESP_TEXTO)
        x += ANCHO_MUESTRA + ESP_TEXTO + w + ESP_ITEM


def dibujar(im, parte, gt, solo_v, solo_i, imagenes, pred, umbral):
    alto, ancho = imagenes[VIS].shape
    panel_w = (ANCHO_TEXTO_PULG - 2 * MARGEN - HUECO_H) / 2
    panel_h = panel_w * alto / ancho
    alto_grilla = 2 * (ALTO_ROTULO + panel_h) + HUECO_V
    alto_fig = 2 * MARGEN + alto_grilla + ALTO_LEYENDA
    fig = plt.figure(figsize=(ANCHO_TEXTO_PULG, alto_fig))

    ax = panel(fig, alto_fig, 0, 0, panel_w, panel_h, imagenes[VIS], "Imagen visible")
    for clase, j in sorted(solo_v):
        recuadro(ax, gt[clase][j], NEGRO, clase)
    ax = panel(fig, alto_fig, 0, 1, panel_w, panel_h, imagenes[IR], "Imagen infrarroja")
    for clase, j in sorted(solo_i):
        recuadro(ax, gt[clase][j], NEGRO, clase)
    for col, (e, color, rotulo) in enumerate(
            ((TH, GRIS_OSCURO, NOMBRES[TH] + " ($r = 5$, $m = 1$)"),
             (PROP, AZUL, NOMBRES[PROP] + " ($r = 25$, $m = 0.30$)"))):
        ax = panel(fig, alto_fig, 1, col, panel_w, panel_h, imagenes[e], rotulo, prop=(e == PROP))
        for clase, caja, _ in cajas_detectadas(pred, umbral, e, im):
            recuadro(ax, caja, color, clase)

    # leyenda: dos renglones debajo de la grilla, en un eje sin marco medido en pulgadas
    axl = fig.add_axes([0, MARGEN / alto_fig, 1, ALTO_LEYENDA / alto_fig])
    axl.set_xlim(0, ANCHO_TEXTO_PULG)
    axl.set_ylim(0, ALTO_LEYENDA)
    axl.axis("off")
    renglon(fig, axl, ALTO_LEYENDA - 0.17, [
        ("linea", NEGRO, "-", "Persona"),
        ("linea", NEGRO, GUIONES, "Luz")])
    renglon(fig, axl, ALTO_LEYENDA - 0.39, [
        ("caja", NEGRO, "-", "Objeto de una sola cámara"),
        ("caja", GRIS_OSCURO, "-", "Detección del Top-Hat clásico"),
        ("caja", AZUL, "-", "Detección de la propuesta")])
    guardar(fig, NOMBRE, ancho_libro=1.0, recortar=False)
    plt.close(fig)


def main():
    aplicar_estilo()
    pred, umbral = cargar_predicciones()
    im, parte, gt, solo_v, solo_i = elegir_cuadro(pred, umbral)
    imagenes = {e: leer_imagen(e, parte, im) for e in (VIS, IR, TH, PROP)}
    comprobar_fusiones(im, imagenes)
    informar(im, gt, solo_v, solo_i, pred, umbral)
    print(f"\n  umbrales: {NOMBRES[TH]} {umbral[(TH, SEMILLA)]:.2f}, "
          f"{NOMBRES[PROP]} {umbral[(PROP, SEMILLA)]:.2f}")
    dibujar(im, parte, gt, solo_v, solo_i, imagenes, pred, umbral)
    if "--verificar" in sys.argv[1:]:
        verificar_detector(pred, im, parte)


if __name__ == "__main__":
    main()
