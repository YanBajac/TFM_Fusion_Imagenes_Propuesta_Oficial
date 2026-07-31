# -*- coding: utf-8 -*-
"""run_complementariedad_escenas.py — mide el OBJETIVO DECLARADO de la tesis.

El objetivo del trabajo es que la imagen fusionada permita detectar objetos que NO se
detectan en el visible ni en el infrarrojo por separado. El mAP promediado sobre el
conjunto de prueba no mide eso: mide precision de deteccion promedio. Lo que corresponde
al enunciado es un CONTEO POR ESCENA.

Para cada escena de la particion de prueba de M3FD que contenga anotaciones de las dos
clases de visibilidad opuesta (People, dominante en IR; Lamp, dominante en VIS) y para
cada entrada del detector (VIS, IR y cada metodo de fusion) se determina:

  recupera_People : detecta al menos un verdadero positivo de People
  recupera_Lamp   : detecta al menos un verdadero positivo de Lamp
  recupera_ambas  : las dos anteriores a la vez  -> "ambas clases en una sola imagen"

Un verdadero positivo exige emparejar una caja anotada de esa clase con IoU >= UMBRAL_IOU
y confianza >= CONF; no basta con que el detector dibuje una caja de la clase en
cualquier parte de la imagen.

De ahi se derivan las tres cifras que contrastan la hipotesis:

  A. En cuantas escenas recupera ambas clases cada entrada (fusion vs VIS vs IR).
  B. ESCENAS CRITICAS: aquellas donde NI el VIS NI el IR recuperan ambas clases por
     separado. Son las escenas que la hipotesis reclama para la fusion. Se reporta en
     cuantas de ellas la fusion si lo logra.
  C. Cobertura por clase: escenas donde una modalidad falla en una clase y la fusion la
     recupera, y escenas donde la fusion PIERDE una clase que la modalidad si detectaba
     (el costo, que hay que reportar junto con el beneficio).

Salidas (en experiments/results/metrics_reports/):
  complementariedad_por_escena.csv   una fila por escena x entrada
  complementariedad_resumen.csv      una fila por entrada con los agregados
  complementariedad_criticas.csv     detalle de las escenas criticas

Uso:
  python experiments/run_complementariedad_escenas.py [--conf 0.25] [--iou 0.5]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

NAMES = ["People", "Car", "Bus", "Motorcycle", "Lamp", "Truck"]
PEOPLE, LAMP = NAMES.index("People"), NAMES.index("Lamp")
ENTRADAS = ["VIS", "IR", "PiramideLaplace", "RatioPiramide", "DWT", "DTCWT",
            "Curvelet", "TopHat_Clasico", "Propuesta_Novedosa"]
SALIDA = ROOT / "experiments" / "results" / "metrics_reports"


def hallar_pesos():
    c = sorted(ROOT.glob("runs/**/mixto/weights/best.pt"), key=lambda p: p.stat().st_mtime)
    c = [p for p in c if p.parent.parent.name == "mixto"]
    assert c, "no encuentro best.pt del modelo mixto; corre antes el pipeline de M3FD"
    return c[-1]


def leer_gt(stem, ancho, alto):
    """Devuelve {clase: [ (x1,y1,x2,y2), ... ]} desde la etiqueta YOLO compartida."""
    lb = ROOT / "datasets" / "m3fd_test_VIS" / "labels" / "val" / f"{stem}.txt"
    cajas = {}
    if not lb.exists():
        return cajas
    for ln in lb.read_text(encoding="utf-8").strip().splitlines():
        p = ln.split()
        if len(p) < 5:
            continue
        cl = int(p[0])
        cx, cy, w, h = (float(x) for x in p[1:5])
        x1, y1 = (cx - w / 2) * ancho, (cy - h / 2) * alto
        x2, y2 = (cx + w / 2) * ancho, (cy + h / 2) * alto
        cajas.setdefault(cl, []).append((x1, y1, x2, y2))
    return cajas


def iou(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    ua = (ax2 - ax1) * (ay2 - ay1) + (bx2 - bx1) * (by2 - by1) - inter
    return inter / ua if ua > 0 else 0.0


def verdaderos_positivos(pred, gt, umbral):
    """Cuenta cajas anotadas emparejadas con alguna prediccion (emparejado codicioso)."""
    if not gt or not pred:
        return 0
    libres = list(pred)
    n = 0
    for g in gt:
        mejor, k = 0.0, -1
        for i, p in enumerate(libres):
            v = iou(g, p)
            if v > mejor:
                mejor, k = v, i
        if mejor >= umbral:
            n += 1
            libres.pop(k)
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--iou", type=float, default=0.5)
    a = ap.parse_args()

    from ultralytics import YOLO
    pesos = hallar_pesos()
    print("pesos:", pesos)
    modelo = YOLO(str(pesos))

    base = ROOT / "datasets" / "m3fd_test_VIS" / "images" / "val"
    stems = sorted(p.stem for p in base.glob("*.jpg"))
    print(f"escenas en la particion de prueba: {len(stems)}")

    filas = []
    for k, s in enumerate(stems):
        # las etiquetas son compartidas entre entradas, asi que el GT se lee una vez
        img0 = ROOT / "datasets" / "m3fd_test_VIS" / "images" / "val" / f"{s}.jpg"
        import cv2
        im = cv2.imread(str(img0), cv2.IMREAD_GRAYSCALE)
        if im is None:
            continue
        alto, ancho = im.shape[:2]
        gt = leer_gt(s, ancho, alto)
        # solo interesan las escenas donde CONVIVEN las dos clases complementarias
        if not (gt.get(PEOPLE) and gt.get(LAMP)):
            continue
        for e in ENTRADAS:
            ruta = ROOT / "datasets" / f"m3fd_test_{e}" / "images" / "val" / f"{s}.jpg"
            if not ruta.exists():
                continue
            r = modelo.predict(str(ruta), conf=a.conf, verbose=False)[0]
            pred = {PEOPLE: [], LAMP: []}
            b = r.boxes
            if b is not None and len(b):
                xy = b.xyxy.cpu().numpy()
                cl = b.cls.cpu().numpy().astype(int)
                for caja, c in zip(xy, cl):
                    if c in pred:
                        pred[c].append(tuple(caja))
            tp_p = verdaderos_positivos(pred[PEOPLE], gt[PEOPLE], a.iou)
            tp_l = verdaderos_positivos(pred[LAMP], gt[LAMP], a.iou)
            filas.append(dict(
                escena=s, entrada=e,
                gt_People=len(gt[PEOPLE]), gt_Lamp=len(gt[LAMP]),
                tp_People=tp_p, tp_Lamp=tp_l,
                recupera_People=int(tp_p >= 1), recupera_Lamp=int(tp_l >= 1),
                recupera_ambas=int(tp_p >= 1 and tp_l >= 1)))
        if (k + 1) % 50 == 0:
            print(f"  {k+1}/{len(stems)} escenas revisadas...", flush=True)

    df = pd.DataFrame(filas)
    assert len(df), "ninguna escena tiene anotaciones de ambas clases"
    SALIDA.mkdir(parents=True, exist_ok=True)
    df.to_csv(SALIDA / "complementariedad_por_escena.csv", index=False)
    escenas = sorted(df.escena.unique())
    n = len(escenas)
    print(f"\nescenas con ambas clases anotadas: {n}")

    piv = df.pivot(index="escena", columns="entrada", values="recupera_ambas")
    pP = df.pivot(index="escena", columns="entrada", values="recupera_People")
    pL = df.pivot(index="escena", columns="entrada", values="recupera_Lamp")

    # B. escenas criticas: ni el VIS ni el IR recuperan ambas clases por separado
    criticas = piv.index[(piv["VIS"] == 0) & (piv["IR"] == 0)]
    print(f"escenas CRITICAS (ni VIS ni IR recuperan ambas): {len(criticas)} de {n}")

    res = []
    for e in [x for x in ENTRADAS if x in piv.columns]:
        fila = dict(
            entrada=e,
            escenas=n,
            recupera_ambas=int(piv[e].sum()),
            pct_ambas=round(100.0 * piv[e].mean(), 1),
            recupera_People=int(pP[e].sum()),
            recupera_Lamp=int(pL[e].sum()),
            criticas=len(criticas),
            resuelve_criticas=int(piv.loc[criticas, e].sum()) if len(criticas) else 0)
        if e not in ("VIS", "IR"):
            # C. beneficio y costo respecto de cada modalidad, escena por escena
            fila["gana_vs_VIS"] = int(((piv[e] == 1) & (piv["VIS"] == 0)).sum())
            fila["pierde_vs_VIS"] = int(((piv[e] == 0) & (piv["VIS"] == 1)).sum())
            fila["gana_vs_IR"] = int(((piv[e] == 1) & (piv["IR"] == 0)).sum())
            fila["pierde_vs_IR"] = int(((piv[e] == 0) & (piv["IR"] == 1)).sum())
        res.append(fila)
    rdf = pd.DataFrame(res)
    rdf.to_csv(SALIDA / "complementariedad_resumen.csv", index=False)

    if len(criticas):
        piv.loc[criticas].to_csv(SALIDA / "complementariedad_criticas.csv")

    cols = ["entrada", "recupera_ambas", "pct_ambas", "recupera_People", "recupera_Lamp",
            "resuelve_criticas", "gana_vs_VIS", "pierde_vs_VIS", "gana_vs_IR", "pierde_vs_IR"]
    print("\n===== RECUPERACION DE AMBAS CLASES POR ESCENA =====")
    print(rdf[[c for c in cols if c in rdf.columns]].to_string(index=False))
    print(f"\nUmbrales: conf >= {a.conf}, IoU >= {a.iou}")
    print("Guardado en", SALIDA)


if __name__ == "__main__":
    main()
