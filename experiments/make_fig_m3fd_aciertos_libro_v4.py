# -*- coding: utf-8 -*-
"""Figura fig:m3fd_aciertos del libro: dos cuadros de la prueba de M3FD en los que una fusion encuentra
un objeto que el detector de una de las camaras pierde (capitulo 4, seccion sec:deteccion del libro).

QUE MUESTRA. Dos escenas, una por fila. Cada fila tiene cuatro paneles con el mismo recorte del cuadro:
  Imagen visible     con las detecciones del detector de la visible (semilla 3), en negro;
  Imagen infrarroja  con las del detector de la infrarroja (semilla 3), en negro;
  Top-Hat clasico    la fusion (r = 5, m = 1) con las de su detector (semilla 0), en gris oscuro;
  Propuesta          la fusion (r = 25, m = 0.30) con las de su detector (semilla 0), en azul #4472c4.
Es la primera semilla de cada entrada, con los pesos del final del entrenamiento (last.pt, los que
evaluo evaluar_v2.py) y su umbral calibrado. Se dibujan las detecciones de personas y luces, recuadros
finos con linea continua para personas y discontinua para luces y un borde blanco fino debajo, como en
fig_m3fd_ejemplo, aunque aqui continuo tambien bajo los guiones de las luces, para que el gris oscuro
del Top-Hat clasico se vea sobre el cielo gris del cuadro de dia. Un triangulo blanco con borde negro, en el mismo lugar de los cuatro paneles (encima
del objeto y de las detecciones que lo encuentran), senala el objeto de una sola camara de la escena;
su caja marcada en M3FD no se dibuja, para que no se confunda con una deteccion.
  Arriba: un objeto de solo la infrarroja: la mayoria de los detectores de la infrarroja lo encuentra
          y la de los de la visible no.
  Abajo:  un objeto de solo la visible, al reves.
Las dos escenas ilustran el mecanismo, que una fusion puede encontrar un objeto que una de las camaras
pierde. No dicen con que frecuencia pasa ni que la propuesta lo haga mejor: se eligen entre los objetos
que la propuesta encuentra (ver abajo), y la diferencia con el Top-Hat clasico se mide en el conjunto.

COMO SE ELIGEN LOS CUADROS (regla fija en el codigo; no interviene lo que hizo el Top-Hat clasico):
  1. Cuadros de la prueba final: m3fd_v2_prueba.csv con entra = True (1067 cuadros, 11 grupos).
  2. Objetos de una sola camara, con la regla de analizar_v2.py: la mayoria de los tres detectores de la
     visible (semillas 3, 4 y 5) lo encuentra y la de los de la infrarroja no, o al reves; cada detector
     con su umbral calibrado (umbral_fppi de m3fd_v2_umbrales.csv), IoU >= 0.5 con el emparejamiento de
     analizar_v2.emparejar. Son 211 de solo la visible y 622 de solo la infrarroja.
  3. Candidatos: los que encuentra el detector de la propuesta con la semilla 0 y su umbral (0.25),
     fuera del grupo del cuadro 00437 (grupo 1), que ya muestra fig_m3fd_ejemplo.
  4. Escena de arriba: el candidato de solo la infrarroja de mayor area (la de su caja marcada).
     Escena de abajo: el candidato de solo la visible de mayor area entre los de otro grupo que el de
     arriba. Los empates se resuelven por id del cuadro y por orden de la caja en la etiqueta.
  Asi las tres escenas de la seccion quedan en tres grupos distintos, y el grupo es la unidad de
  analisis: los cuadros de un grupo son tramos de video vecinos. La exclusion es por grupo y no solo
  por cuadro porque, con la de cuadro, la escena de abajo caia en el 03972, del mismo grupo que la de
  arriba y a 53 cuadros de ella: una multitud de 12 personas en una escalera, de noche, donde la
  persona elegida se ve con claridad en la infrarroja y quedo como de solo la visible porque dos de los
  tres detectores de la infrarroja fallaron en la multitud. El script lo vuelve a calcular e informa.
  Resultado: arriba el cuadro 04025 (val, grupo 10), una persona; abajo el 02200 (val, grupo 7), una
  luz (semaforo). En los dos, el detector del Top-Hat clasico (semilla 0) tambien encuentra el objeto,
  y se muestra tal cual.

RECORTE (el mismo en las cuatro columnas de una fila): la ventana mas chica con la proporcion de la
imagen (4:3) que contiene la caja marcada del objeto, agrandada K_RECORTE = 4 veces alrededor de su
centro, limitada al tamano de la imagen y corrida lo necesario para quedar dentro de ella. En la
escena de arriba la persona es grande y la ventana es el cuadro entero.

DE DONDE SALE CADA COSA (nada se dibuja de memoria):
  - Las cajas: experiments/results/metrics_reports/m3fd_v2_predicciones.csv, las predicciones crudas
    (confianza >= 0.05) que guardo evaluar_v2.py y que uso analizar_v2.py. Se dibujan las de confianza
    igual o mayor que el umbral del detector. Con --verificar, se vuelve a correr cada uno de los cuatro
    detectores (last.pt, imgsz 640, en el procesador) sobre los dos cuadros y se comprueba que da las
    mismas cajas.
  - Los umbrales: m3fd_v2_umbrales.csv, columna umbral_fppi.
  - Las cajas marcadas (verdad de terreno), los objetos de una sola camara y si cada detector encuentra
    cada objeto: las etiquetas de datasets/m3fd2_VIS/labels y las funciones de analizar_v2.py (leer_gt,
    indexar, detecciones, que usa emparejar), que se importa y no se corre.
  - Las imagenes: datasets/m3fd2_<entrada>/images/<parte>/<id>.jpg, las mismas que vio cada detector. Se
    comprueba que coinciden, salvo la compresion JPEG, con las fuentes de data/M3FD_Detection y con la
    fusion recalculada desde src/ (propuesta: fuse_optimal r = 25, m = 0.30, modo "sum"; Top-Hat
    clasico: tophat_classic_fusion r = 5).
  - El brillo medio de la visible de cada cuadro se informa por pantalla como referencia de dia o noche;
    no interviene en la eleccion.
  El script informa ademas las cifras que el texto puede citar: que objeto marcado encuentra cada
  detector en cada cuadro y con que semillas, la confianza de la mejor caja cruda de la primera semilla
  sobre cada objeto (aunque quede bajo el umbral), las detecciones que caen en el recorte, y cuantos
  objetos de una sola camara encuentran la propuesta y el Top-Hat clasico con la semilla 0, los dos y
  al menos uno de ellos.

ESTILO: el comun de las figuras del libro (experiments/estilo_figuras_libro.py) y el de fig_m3fd_ejemplo:
rotulo arriba de cada panel a 10 pt, marco fino gris oscuro y el de la propuesta en azul, y una linea
sobre cada fila con el cuadro y el objeto. La leyenda va abajo, en dos renglones. El lienzo mide el
ancho de la caja de texto (160 mm = 6.30 pulgadas); el LaTeX la incluye con width=\\textwidth.

Salida: docs/libro_v4/figuras/fig_m3fd_aciertos.png (300 ppp)

Uso (desde la raiz del repo):
    .venv\\Scripts\\python.exe -X utf8 experiments/make_fig_m3fd_aciertos_libro_v4.py [--verificar]
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
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

import analizar_v2 as A          # solo sus funciones (leer_gt, indexar, detecciones); su main() no se corre
from estilo_figuras_libro import (ANCHO_TEXTO_PULG, AZUL, GRIS_OSCURO, NEGRO, NOMBRES, REPORTES,
                                  TAM_LEYENDA, TAM_TEXTO, aplicar_estilo, guardar)

NOMBRE = "fig_m3fd_aciertos"
DATOS = RAIZ / "datasets"
M3FD = RAIZ / "data" / "M3FD_Detection"
PESOS = RAIZ / "runs" / "m3fd_v2"
VIS, IR, TH, PROP = "VIS", "IR", "TopHat_Clasico", "Propuesta_Novedosa"
ENTRADAS = (VIS, IR, TH, PROP)
SEMILLAS = {VIS: (3, 4, 5), IR: (3, 4, 5), TH: (0, 1, 2), PROP: (0, 1, 2)}
PRIMERA = {VIS: 3, IR: 3, TH: 0, PROP: 0}       # la semilla que se dibuja de cada entrada
CUADRO_EJEMPLO = "00437"                       # el de fig_m3fd_ejemplo: se excluye su grupo
ESPERADOS = ("04025", "02200")                 # lo que dio la regla al fijarla (paso de candidatos)
K_RECORTE = 4.0                                # la ventana mide 4 veces la caja del objeto
CAMARA_TXT = {"visible": "la visible", "infrarroja": "la infrarroja"}
CLASE_TXT = {"People": "persona", "Lamp": "luz"}

# disposicion, en pulgadas
MARGEN = 0.02
HUECO_H = 0.06                      # entre columnas
HUECO_V = 0.10                      # entre el pie de la fila de arriba y la linea de la de abajo
ALTO_LINEA = 0.22                   # linea de la escena, sobre cada fila
ALTO_ROTULO = 0.20                  # franja del rotulo, sobre cada panel
ALTO_LEYENDA = 0.50                 # dos renglones de leyenda, debajo de la grilla
LW_MARCO = 0.5
LW_PROPUESTA = 1.6                  # el marco azul de la propuesta, como en los montajes
LW_CAJA = 1.2                       # recuadros de las detecciones
LW_BORDE_BLANCO = 1.7               # borde blanco por debajo de cada recuadro (visible de noche)
GUIONES = (0, (3.5, 2.0))           # linea discontinua de las luces
TAM_MARCA = 7.0                     # lado del triangulo que senala el objeto, en puntos
SEP_MARCA = 0.05                    # separacion entre el triangulo y la caja del objeto, en pulgadas


# ---------------------------------------------------------------- datos
def cargar_predicciones():
    pred = pd.read_csv(REPORTES / "m3fd_v2_predicciones.csv").drop_duplicates()
    pred["imagen"] = pred.imagen.map(lambda x: f"{int(x):05d}")
    umb = pd.read_csv(REPORTES / "m3fd_v2_umbrales.csv")
    umbral = {(e, int(s)): float(t) for e, s, t in zip(umb.entrada, umb.semilla, umb.umbral_fppi)}
    return pred, umbral


def objetos_una_camara(pred, umbral):
    """Pasos 1 y 2 del docstring, y que objeto encuentra cada detector de las cuatro entradas."""
    prueba = pd.read_csv(REPORTES / "m3fd_v2_prueba.csv")
    prueba = prueba[prueba.entra]
    parte_de = {f"{int(i):05d}": p for i, p in zip(prueba.id, prueba.parte)}
    grupo_de = {f"{int(i):05d}": int(g) for i, g in zip(prueba.id, prueba.grupo)}
    gt = A.leer_gt(["test", "val"], set(parte_de))
    det = A.indexar(pred[pred.entrada.isin(ENTRADAS)], ["test", "val"])
    claves, M = None, {}
    for e, ss in SEMILLAS.items():
        for s in ss:
            d = A.detecciones(det.get((e, s), {}), gt, umbral[(e, s)])
            claves = claves or sorted(d)
            assert sorted(d) == claves
            M[(e, s)] = np.array([d[c] for c in claves], dtype=bool)
    mayoria = {e: np.mean([M[(e, s)] for s in SEMILLAS[e]], axis=0) > 0.5 for e in (VIS, IR)}
    solo = {"visible": mayoria[VIS] & ~mayoria[IR], "infrarroja": mayoria[IR] & ~mayoria[VIS]}
    print(f"  prueba: {len(gt)} cuadros en {len(set(grupo_de.values()))} grupos, {len(claves)} objetos "
          f"marcados (personas y luces); solo de la visible {solo['visible'].sum()}, solo de la "
          f"infrarroja {solo['infrarroja'].sum()}, de las dos {(mayoria[VIS] & mayoria[IR]).sum()}")
    assert (solo["visible"].sum(), solo["infrarroja"].sum()) == (211, 622), "no coincide con el libro"
    filas = []
    for k, c in enumerate(claves):
        im, clase, j = c.split("|")
        cam = ("visible" if solo["visible"][k] else "infrarroja" if solo["infrarroja"][k] else None)
        if cam is None:
            continue
        x1, y1, x2, y2 = gt[im][clase][int(j)]
        filas.append({"k": k, "id": im, "parte": parte_de[im], "grupo": grupo_de[im], "clase": clase,
                      "j": int(j), "camara": cam, "area": (x2 - x1) * (y2 - y1),
                      "propuesta": bool(M[(PROP, PRIMERA[PROP])][k])})
    return pd.DataFrame(filas), claves, M, solo, mayoria, gt, grupo_de


def elegir(obj, grupo_de):
    """Pasos 3 y 4 del docstring. Devuelve las dos filas elegidas (arriba, abajo)."""
    excl = grupo_de[CUADRO_EJEMPLO]
    orden = ["area", "id", "j"]
    cand = obj[obj.propuesta & (obj.grupo != excl)].sort_values(orden, ascending=[False, True, True])
    ci, cv = cand[cand.camara == "infrarroja"], cand[cand.camara == "visible"]
    arriba = ci.iloc[0]
    abajo = cv[cv.grupo != arriba.grupo].iloc[0]
    print(f"  candidatos (encontrados por la propuesta, semilla 0, fuera del grupo {excl} del cuadro "
          f"{CUADRO_EJEMPLO}): {len(ci)} de solo la infrarroja y {len(cv)} de solo la visible; de estos, "
          f"{int((cv.grupo != arriba.grupo).sum())} fuera del grupo {arriba.grupo}")
    solo_cuadro = cv[cv.id != arriba.id].iloc[0]
    print(f"  con la exclusion solo por cuadro, abajo habria quedado el {solo_cuadro.id} "
          f"(grupo {solo_cuadro.grupo}, a {abs(int(solo_cuadro.id) - int(arriba.id))} cuadros del de arriba)")
    assert (arriba.id, abajo.id) == ESPERADOS, f"la regla dio {arriba.id} y {abajo.id}"
    return arriba, abajo


def leer_imagen(entrada, parte, im):
    ruta = DATOS / f"m3fd2_{entrada}" / "images" / parte / f"{im}.jpg"
    g = cv2.imread(str(ruta), cv2.IMREAD_GRAYSCALE)
    assert g is not None, f"no se pudo leer {ruta}"
    return g


def comprobar_imagenes(im, imagenes):
    """Las imagenes del conjunto tienen que ser las fuentes y la fusion de src/, salvo el JPEG."""
    from src.fusion.optimal_top_hat import fuse_optimal
    from src.fusion.comparatives import tophat_classic_fusion
    v = cv2.imread(str(M3FD / "Vis" / f"{im}.png"), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
    r = cv2.imread(str(M3FD / "Ir" / f"{im}.png"), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
    calc = {VIS: v, IR: r, TH: tophat_classic_fusion(v, r, r=5),
            PROP: fuse_optimal(v, r, 25, 0.30, mode="sum")}
    for e, f in calc.items():
        f8 = (np.clip(f, 0, 1) * 255).astype(np.uint8).astype(int)
        dif = np.abs(f8 - imagenes[e].astype(int))
        print(f"    {e}: diferencia con la recalculada, media {dif.mean():.2f} y percentil 99 "
              f"{np.percentile(dif, 99):.0f} niveles de gris")
        assert dif.mean() < 2.0, f"la imagen de {e} no coincide con la de src"


def cajas_detectadas(pred, umbral, entrada, im):
    s = PRIMERA[entrada]
    d = pred[(pred.entrada == entrada) & (pred.semilla == s) & (pred.imagen == im)]
    d = d[d.conf >= umbral[(entrada, s)]]
    return [(c, (x1, y1, x2, y2), cf) for c, x1, y1, x2, y2, cf in
            zip(d.clase, d.x1, d.y1, d.x2, d.y2, d.conf)]


def conf_cruda(pred, entrada, im, clase, caja):
    """Confianza mas alta entre las predicciones crudas de la primera semilla que se superponen con la
    caja marcada (IoU >= 0.5), aunque queden bajo el umbral. Solo informativa."""
    s = PRIMERA[entrada]
    d = pred[(pred.entrada == entrada) & (pred.semilla == s) & (pred.imagen == im) & (pred.clase == clase)]
    cf = [c for c, x1, y1, x2, y2 in zip(d.conf, d.x1, d.y1, d.x2, d.y2)
          if A.iou(caja, (x1, y1, x2, y2)) >= A.IOU]
    return f"{max(cf):.3f}" if cf else "ninguna"


def recorte(caja, alto, ancho):
    """Ventana (x0, y0, w, h) de proporcion ancho:alto, K_RECORTE veces la caja, dentro de la imagen."""
    x1, y1, x2, y2 = caja
    prop = ancho / alto
    h = min(K_RECORTE * max(y2 - y1, (x2 - x1) / prop), alto)
    w = h * prop
    x0 = min(max((x1 + x2) / 2 - w / 2, 0.0), ancho - w)
    y0 = min(max((y1 + y2) / 2 - h / 2, 0.0), alto - h)
    return x0, y0, w, h


def dentro(caja, ventana):
    """'entera', 'en parte' o 'fuera' de la ventana."""
    x0, y0, w, h = ventana
    x1, y1, x2, y2 = caja
    if x1 >= x0 and y1 >= y0 and x2 <= x0 + w and y2 <= y0 + h:
        return "entera"
    if x2 <= x0 or y2 <= y0 or x1 >= x0 + w or y1 >= y0 + h:
        return "fuera"
    return "en parte"


def informar(fila, claves, M, solo, mayoria, gt, imagenes, ventana, pred, umbral):
    """Lo que el texto y la nota pueden citar de una escena."""
    im = fila.id
    caja = gt[im][fila.clase][fila.j]
    k = fila.k
    print(f"\n  CUADRO {im} ({fila.parte}, grupo {fila.grupo}); brillo medio de la visible "
          f"{imagenes[VIS].mean():.1f} y de la infrarroja {imagenes[IR].mean():.1f}")
    print(f"    objeto senalado: {fila.clase} {fila.j}, solo de {CAMARA_TXT[fila.camara]}, caja "
          f"({caja[0]:.0f}, {caja[1]:.0f}, {caja[2]:.0f}, {caja[3]:.0f}), "
          f"{caja[2] - caja[0]:.0f} x {caja[3] - caja[1]:.0f} px, area {fila.area:.0f} px2")
    print("    primera semilla: " + ", ".join(
        f"{e} s{PRIMERA[e]} {'lo encuentra' if M[(e, PRIMERA[e])][k] else 'no'}" for e in ENTRADAS))
    print("    semillas que lo encuentran: " + ", ".join(
        f"{e} {sum(int(M[(e, s)][k]) for s in SEMILLAS[e])} de {len(SEMILLAS[e])}" for e in ENTRADAS))
    x0, y0, w, h = ventana
    print(f"    recorte: x {x0:.0f} a {x0 + w:.0f}, y {y0:.0f} a {y0 + h:.0f} ({w:.0f} x {h:.0f} px de "
          f"{imagenes[VIS].shape[1]} x {imagenes[VIS].shape[0]})")
    print("    objetos marcados del cuadro: si lo encuentra la primera semilla de cada entrada, y entre "
          "corchetes las semillas que lo encuentran:")
    for kk, c in enumerate(claves):
        i2, clase, j = c.split("|")
        if i2 != im:
            continue
        b = gt[im][clase][int(j)]
        tipo = ("solo visible" if solo["visible"][kk] else "solo infrarroja" if solo["infrarroja"][kk]
                else "las dos" if mayoria[VIS][kk] and mayoria[IR][kk] else "ninguna")
        print(f"      {clase:6s} {j}  ({b[0]:.0f}, {b[1]:.0f}, {b[2]:.0f}, {b[3]:.0f})  {tipo:15s} "
              f"{dentro(b, ventana):8s} " +
              " ".join(f"{e}={'si' if M[(e, PRIMERA[e])][kk] else 'no'}"
                       f"[{','.join(str(s) for s in SEMILLAS[e] if M[(e, s)][kk]) or '-'}]"
                       for e in ENTRADAS))
        print("        confianza de la mejor caja cruda (>= 0.05, misma clase, IoU >= 0.5) de la primera "
              "semilla: " + ", ".join(f"{e} {conf_cruda(pred, e, im, clase, b)}" for e in ENTRADAS))
    print("    detecciones sobre el umbral (y cuantas caen en el recorte, enteras o en parte):")
    for e in ENTRADAS:
        cajas = cajas_detectadas(pred, umbral, e, im)
        partes = []
        for cl in A.CLASES:
            cc = [b for c, b, _ in cajas if c == cl]
            n_rec = sum(dentro(b, ventana) != "fuera" for b in cc)
            partes.append(f"{len(cc)} {cl} ({n_rec} en el recorte)")
        print(f"      {e} s{PRIMERA[e]} (umbral {umbral[(e, PRIMERA[e])]:.2f}): " + ", ".join(partes))
        for c, b, cf in cajas:
            print(f"        {c:6s} ({b[0]:.0f}, {b[1]:.0f}, {b[2]:.0f}, {b[3]:.0f}) conf {cf:.3f}  "
                  f"{dentro(b, ventana)}")


def cifras_nota(M, solo):
    """Cuantos objetos de una sola camara encuentran las dos fusiones con la semilla 0, cada una, las dos
    y al menos una."""
    print("\n  objetos de una sola camara que encuentra cada fusion (semilla 0, umbral principal):")
    for cam in ("visible", "infrarroja"):
        m = solo[cam]
        p, t = M[(PROP, 0)][m], M[(TH, 0)][m]
        print(f"    solo de {CAMARA_TXT[cam]} ({m.sum()}): propuesta {p.sum()}, Top-Hat clasico {t.sum()}; "
              f"los dos {(p & t).sum()}, solo la propuesta {(p & ~t).sum()}, solo el Top-Hat clasico "
              f"{(~p & t).sum()}, al menos una {(p | t).sum()}")


def verificar_detector(pred, cuadros):
    """Vuelve a correr cada detector sobre los cuadros y compara con el CSV."""
    from ultralytics import YOLO        # se importa al final: cambia cv2.imread
    for e in ENTRADAS:
        s = PRIMERA[e]
        modelo = YOLO(str(PESOS / f"{e}_s{s}" / "weights" / "last.pt"))
        for im, parte in cuadros:
            ruta = DATOS / f"m3fd2_{e}" / "images" / parte / f"{im}.jpg"
            r = modelo.predict(str(ruta), conf=0.05, imgsz=640, verbose=False, device="cpu")[0]
            nuevas = sorted((A.CLASES[0] if int(c) == 0 else A.CLASES[1],
                             tuple(round(float(x), 1) for x in caja), round(float(cf), 4))
                            for caja, c, cf in zip(r.boxes.xyxy.cpu().numpy(), r.boxes.cls.cpu().numpy(),
                                                   r.boxes.conf.cpu().numpy()) if int(c) in (0, 4))
            d = pred[(pred.entrada == e) & (pred.semilla == s) & (pred.imagen == im)]
            csv = sorted((c, (x1, y1, x2, y2), cf) for c, x1, y1, x2, y2, cf in
                         zip(d.clase, d.x1, d.y1, d.x2, d.y2, d.conf))
            iguales = len(nuevas) == len(csv) and all(
                a[0] == b[0] and np.allclose(a[1], b[1], atol=0.11) and abs(a[2] - b[2]) < 1e-3
                for a, b in zip(nuevas, csv))
            print(f"  verificacion {e} s{s}, cuadro {im}: {len(nuevas)} cajas ahora, {len(csv)} en el "
                  f"CSV -> {'iguales' if iguales else 'DISTINTAS'}")
            assert iguales, f"el detector {e} s{s} no reproduce las cajas del CSV en {im}"


# ---------------------------------------------------------------- dibujo
def recuadro(ax, caja, color, clase):
    """Recuadro de una deteccion sobre un borde blanco continuo, tambien bajo los guiones de las luces:
    asi el gris oscuro del Top-Hat clasico se ve sobre el cielo gris del cuadro de dia."""
    x1, y1, x2, y2 = caja
    ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, edgecolor="white",
                           linewidth=LW_BORDE_BLANCO, linestyle="-", joinstyle="miter"))
    ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, edgecolor=color, linewidth=LW_CAJA,
                           linestyle="-" if clase == "People" else GUIONES, joinstyle="miter"))


def extension_vertical(caja, pred, umbral, im):
    """Tope y pie del objeto y de las detecciones que lo encuentran (IoU >= 0.5), en cualquiera de los
    cuatro paneles: el triangulo va por fuera de todas, en el mismo lugar de los cuatro."""
    ys = [(caja[1], caja[3])]
    for e in ENTRADAS:
        ys += [(b[1], b[3]) for _, b, _ in cajas_detectadas(pred, umbral, e, im) if A.iou(caja, b) >= A.IOU]
    return min(y for y, _ in ys), max(y for _, y in ys)


def marca(ax, caja, tope, pie, ventana, panel_h):
    """Triangulo que senala el objeto: encima de el, o debajo si no hay lugar arriba."""
    x0, y0, w, h = ventana
    px = h / panel_h                                    # pixeles de la imagen por pulgada del panel
    lado, sep = TAM_MARCA / 72 * px, SEP_MARCA * px
    if tope - y0 >= sep + lado:
        y, forma = tope - sep - lado / 2, "v"
    else:
        y, forma = pie + sep + lado / 2, "^"
    ax.plot([(caja[0] + caja[2]) / 2], [y], marker=forma, markersize=TAM_MARCA, markerfacecolor="white",
            markeredgecolor=NEGRO, markeredgewidth=0.8, linestyle="none", zorder=5)


def panel(fig, alto_fig, x0, y0, panel_w, panel_h, img, ventana, rotulo, prop=False):
    ax = fig.add_axes([x0 / ANCHO_TEXTO_PULG, y0 / alto_fig,
                       panel_w / ANCHO_TEXTO_PULG, panel_h / alto_fig])
    ax.imshow(img, cmap="gray", vmin=0, vmax=255, aspect="auto", interpolation="lanczos")
    vx, vy, vw, vh = ventana
    ax.set_xlim(vx - 0.5, vx + vw - 0.5)
    ax.set_ylim(vy + vh - 0.5, vy - 0.5)
    ax.set_title(rotulo, fontsize=TAM_TEXTO, pad=3, color=AZUL if prop else NEGRO)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_edgecolor(AZUL if prop else GRIS_OSCURO)
        sp.set_linewidth(LW_PROPUESTA if prop else LW_MARCO)
    return ax


def renglon(fig, ax, y, items):
    """Un renglon de leyenda centrado. items: (tipo, color, estilo, texto); tipo 'linea', 'caja' o
    'marca'."""
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
        elif tipo == "caja":
            ax.add_patch(Rectangle((x + 0.04, y - 0.055), ANCHO_MUESTRA - 0.08, 0.11, fill=False,
                                   edgecolor=color, linewidth=LW_CAJA + 0.3))
        else:
            ax.add_line(Line2D([x + ANCHO_MUESTRA / 2], [y], marker="v", markersize=TAM_MARCA,
                               markerfacecolor="white", markeredgecolor=color, markeredgewidth=0.8,
                               linestyle="none"))
        t.set_x(x + ANCHO_MUESTRA + ESP_TEXTO)
        x += ANCHO_MUESTRA + ESP_TEXTO + w + ESP_ITEM


def dibujar(escenas, pred, umbral):
    """escenas: lista de (fila elegida, caja del objeto, imagenes, ventana)."""
    alto, ancho = escenas[0][2][VIS].shape
    panel_w = (ANCHO_TEXTO_PULG - 2 * MARGEN - 3 * HUECO_H) / 4
    panel_h = panel_w * alto / ancho
    alto_fila = ALTO_LINEA + ALTO_ROTULO + panel_h
    alto_fig = 2 * MARGEN + len(escenas) * alto_fila + (len(escenas) - 1) * HUECO_V + ALTO_LEYENDA
    fig = plt.figure(figsize=(ANCHO_TEXTO_PULG, alto_fig))
    columnas = ((VIS, NEGRO, "Imagen visible"), (IR, NEGRO, "Imagen infrarroja"),
                (TH, GRIS_OSCURO, NOMBRES[TH]), (PROP, AZUL, NOMBRES[PROP]))
    for r, (fila, caja, imagenes, ventana) in enumerate(escenas):
        tope = alto_fig - MARGEN - r * (alto_fila + HUECO_V)
        fig.text(MARGEN / ANCHO_TEXTO_PULG, (tope - ALTO_LINEA / 2) / alto_fig,
                 f"Cuadro {int(fila.id)}: {CLASE_TXT[fila.clase]} vista solo por "
                 f"{CAMARA_TXT[fila.camara]}", fontsize=TAM_TEXTO, ha="left", va="center")
        y0 = tope - alto_fila
        arriba_obj, abajo_obj = extension_vertical(caja, pred, umbral, fila.id)
        for col, (e, color, rotulo) in enumerate(columnas):
            x0 = MARGEN + col * (panel_w + HUECO_H)
            ax = panel(fig, alto_fig, x0, y0, panel_w, panel_h, imagenes[e], ventana, rotulo,
                       prop=(e == PROP))
            for clase, b, _ in cajas_detectadas(pred, umbral, e, fila.id):
                recuadro(ax, b, color, clase)
            marca(ax, caja, arriba_obj, abajo_obj, ventana, panel_h)

    # leyenda: dos renglones debajo de la grilla, en un eje sin marco medido en pulgadas
    axl = fig.add_axes([0, MARGEN / alto_fig, 1, ALTO_LEYENDA / alto_fig])
    axl.set_xlim(0, ANCHO_TEXTO_PULG)
    axl.set_ylim(0, ALTO_LEYENDA)
    axl.axis("off")
    renglon(fig, axl, ALTO_LEYENDA - 0.17, [
        ("linea", NEGRO, "-", "Persona"),
        ("linea", NEGRO, GUIONES, "Luz"),
        ("marca", NEGRO, None, "Objeto de una sola c\u00e1mara")])
    renglon(fig, axl, ALTO_LEYENDA - 0.39, [
        ("caja", NEGRO, "-", "Detecci\u00f3n en la fuente"),
        ("caja", GRIS_OSCURO, "-", "Detecci\u00f3n del Top-Hat cl\u00e1sico"),
        ("caja", AZUL, "-", "Detecci\u00f3n de la propuesta")])
    guardar(fig, NOMBRE, ancho_libro=1.0, recortar=False)
    plt.close(fig)


def main():
    aplicar_estilo()
    pred, umbral = cargar_predicciones()
    obj, claves, M, solo, mayoria, gt, grupo_de = objetos_una_camara(pred, umbral)
    arriba, abajo = elegir(obj, grupo_de)
    escenas = []
    for fila in (arriba, abajo):
        imagenes = {e: leer_imagen(e, fila.parte, fila.id) for e in ENTRADAS}
        print(f"\n  imagenes del cuadro {fila.id}:")
        comprobar_imagenes(fila.id, imagenes)
        caja = gt[fila.id][fila.clase][fila.j]
        ventana = recorte(caja, *imagenes[VIS].shape)
        informar(fila, claves, M, solo, mayoria, gt, imagenes, ventana, pred, umbral)
        escenas.append((fila, caja, imagenes, ventana))
    cifras_nota(M, solo)
    print()
    dibujar(escenas, pred, umbral)
    if "--verificar" in sys.argv[1:]:
        verificar_detector(pred, [(f.id, f.parte) for f in (arriba, abajo)])


if __name__ == "__main__":
    main()
