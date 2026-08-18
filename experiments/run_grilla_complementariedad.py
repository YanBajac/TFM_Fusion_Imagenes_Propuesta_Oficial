# -*- coding: utf-8 -*-
"""Busca el punto de operacion (r, m) del operador propuesto que MAXIMIZA LA COMPLEMENTARIEDAD.

LA PREGUNTA. El punto adoptado —r = 25, m = 0,30— se eligio sobre las nueve metricas de calidad de
imagen, que premian la actividad espacial. La tarea aplicativa es otra: que la imagen fusionada permita
detectar los objetos que solo se ven en una de las dos modalidades. Y en esa tarea el operador queda
sexto de siete. La hipotesis es que el punto esta mal elegido, no el operador: un peso mas bajo deberia
conservar los objetos de bajo contraste del canal visible —las lamparas— que el realce fuerte borra.

QUE SE MIDE, con el mismo criterio que run_complementariedad_objetos.py:
  (a) de los objetos que ve UNA SOLA modalidad, cuantos conserva la fusion;
  (b) de las escenas que tienen al menos un objeto exclusivo de CADA modalidad, en cuantas la fusion
      recupera los dos lados. Es la condicion tal como la enuncio el director.

NO SE REENTRENA NADA. El detector de M3FD ya esta entrenado sobre las dos modalidades; esto es
inferencia sobre imagenes re-fusionadas, que es exactamente el protocolo del experimento.

DOS COSAS QUE HACEN QUE ESTO SEA COMPARABLE, y sin ellas la grilla mediria otra cosa:

  1. EL IDA Y VUELTA JPEG. prepare_m3fd.py guarda las fusionadas como .jpg, que es con perdida. Si aca
     se le pasara al modelo el arreglo en memoria, veria una imagen mas limpia que la del experimento
     publicado y los numeros no serian comparables. Se codifica y decodifica JPEG en memoria para que
     vea exactamente lo mismo.
  2. EL PUNTO DE CONTROL. La grilla incluye (25; 0,30), el punto publicado, y se ABORTA si no reproduce
     lo que ya midio run_complementariedad_objetos.py. Es la unica forma de saber que el arnes mide lo
     mismo antes de creerle a los puntos nuevos.

LA FACTORIZACION DEL PESO es lo que hace esto barato. En fuse_optimal, m aparece solo en la ultima
linea: fused = base + m·wth_max − m·bth_max. Asi que la morfologia —los diez cierres y aperturas del
banco, que son el costo real— se calcula UNA VEZ POR RADIO y todos los pesos de ese radio salen de una
resta. Sin esto, 18 puntos serian 54 minutos; con esto, unos diez.

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/run_grilla_complementariedad.py
      [--radios 5,15,25] [--pesos 0.05,0.10,0.15,0.20,0.30,0.50] [--conf 0.25] [--iou 0.5]
"""
import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

import cv2
import numpy as np
import pandas as pd

import run_complementariedad_escenas as base
from run_complementariedad_objetos import detectados
from src.fusion.optimal_top_hat import combined_top_hat

SALIDA = ROOT / "experiments" / "results" / "metrics_reports"
def rutas(pref):
    """La salida de la grilla y la referencia por objeto de ESTA particion."""
    suf = "" if pref == "m3fd_comp" else f"_{pref}"
    return (SALIDA / f"grilla_complementariedad{suf}.csv",
            SALIDA / f"complementariedad_objetos{suf}.csv",
            SALIDA / f"grilla_complementariedad_detalle{suf}.csv")
PROP = "Propuesta_Novedosa"


def clave_escena(s):
    """El nombre de escena normalizado, para que las claves de los dos lados coincidan.

    Los stems del dataset son «00063» pero complementariedad_por_escena.csv los guarda como numero y
    pandas los relee como el entero 63. Sin normalizar, las claves de la grilla («00063|People|0») no
    encuentran nada en la referencia («63|People|0») y el control da 0 objetos recuperados de 447. Lo
    cazo el punto de control, que para eso esta.
    """
    t = str(s)
    return str(int(t)) if t.isdigit() else t


def gris01(ruta):
    """Lee en gris y devuelve SIEMPRE un arreglo 2D en [0, 1].

    Hace falta el squeeze porque ULTRALYTICS PARCHEA cv2.imread: su version envuelve el resultado con
    `im[..., None]` cuando la imagen decodificada es 2D, de modo que despues de `from ultralytics import
    YOLO` una lectura en escala de grises devuelve (H, W, 1) y no (H, W). combined_top_hat entonces
    revienta con «operands could not be broadcast together with shapes (768,1024,1) (768,1024)», porque
    cv2.morphologyEx si devuelve 2D. Aislado —sin importar ultralytics— el mismo codigo funciona, que es
    lo que vuelve al defecto dificil de ubicar.
    """
    im = cv2.imread(str(ruta), cv2.IMREAD_GRAYSCALE)
    if im is None:
        return None
    if im.ndim == 3:
        im = im[..., 0]
    return im.astype(np.float32) / 255


def jpeg_ida_y_vuelta(img01):
    """La imagen tal como la veria el modelo si se hubiera guardado a disco como .jpg.

    Dos detalles y los dos son necesarios para que la grilla sea comparable con el experimento
    publicado. El primero es el ida y vuelta JPEG, porque prepare_m3fd.py guarda con perdida y un
    arreglo en memoria seria una imagen mas limpia que la que se midio. El segundo es decodificar en
    COLOR: el archivo que se guarda es gris de un canal, pero cuando ultralytics lo lee de disco lo
    decodifica a BGR replicando el canal, y la primera convolucion del modelo espera tres. Pasarle un
    solo canal falla con «expected input[1, 1, 480, 640] to have 3 channels». Decodificando en color se
    reproduce exactamente lo que el modelo veria leyendo el .jpg del disco.
    """
    u8 = (np.clip(img01, 0, 1) * 255).astype(np.uint8)
    ok, buf = cv2.imencode(".jpg", u8)
    assert ok, "no se pudo codificar a JPEG"
    return cv2.imdecode(buf, cv2.IMREAD_COLOR)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--radios", default="5,15,25")
    ap.add_argument("--pesos", default="0.05,0.10,0.15,0.20,0.30,0.50")
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--iou", type=float, default=0.5)
    ap.add_argument("--prefijo", default="m3fd_comp", choices=["m3fd_comp", "m3fd_test"])
    ap.add_argument("--guardar-objetos", action="store_true",
                    help="ademas del resumen, guarda el detalle por objeto de cada punto de la "
                         "grilla. Hace falta para las pruebas pareadas: comparar dos puntos por sus "
                         "totales no dice si la diferencia es consistente objeto por objeto.")
    a = ap.parse_args()
    GRILLA_CSV, OBJ_REF, DET_CSV = rutas(a.prefijo)
    base.PREF = a.prefijo
    radios = [int(x) for x in a.radios.split(",")]
    pesos = [float(x) for x in a.pesos.split(",")]
    if (25, 0.30) not in [(r, m) for r in radios for m in pesos]:
        print("AVISO: la grilla no incluye el punto publicado (25; 0,30); no habra control")

    from ultralytics import YOLO
    modelo = YOLO(str(base.hallar_pesos()))

    # Los stems y las etiquetas salen del dataset preparado, pero LA FUSION SE HACE DESDE LAS
    # ORIGINALES. prepare_m3fd.py fusiona los PNG sin perdida de data/M3FD_Detection y guarda el
    # resultado como .jpg; fusionar esos .jpg ya comprimidos daria una entrada distinta de la que se
    # midio. Con las copias comprimidas el punto de control daba 4 escenas donde la referencia tiene
    # 6: chico, pero suficiente para que la grilla no fuera comparable.
    dSel = ROOT / "datasets" / f"{a.prefijo}_VIS" / "images" / "val"
    dV = ROOT / "data" / "M3FD_Detection" / "Vis"
    dI = ROOT / "data" / "M3FD_Detection" / "Ir"
    stems = sorted(p.stem for p in dSel.glob("*.jpg"))

    # el GT y las escenas que entran, con el mismo filtro que el analisis por objeto
    escenas = []
    for s in stems:
        im = cv2.imread(str(dSel / f"{s}.jpg"), cv2.IMREAD_GRAYSCALE)
        if im is None:
            continue
        alto, ancho = im.shape[:2]
        gt = base.leer_gt(s, ancho, alto)
        if gt.get(base.PEOPLE) and gt.get(base.LAMP):
            escenas.append((s, gt))
    print(f"escenas con ambas clases: {len(escenas)}")

    # la referencia por objeto: que ve cada modalidad. Se lee del CSV ya validado en lugar de
    # recalcularse, para que la grilla se compare contra exactamente la misma particion de objetos.
    ref = pd.read_csv(OBJ_REF)
    ref["clave"] = (ref.escena.map(clave_escena) + "|" + ref.clase + "|"
                    + ref.objeto.astype(str))
    solo_vis = set(ref.loc[(ref.VIS == 1) & (ref.IR == 0), "clave"])
    solo_ir = set(ref.loc[(ref.IR == 1) & (ref.VIS == 0), "clave"])
    unica = solo_vis | solo_ir
    print(f"objetos que ve UNA SOLA modalidad: {len(unica)} "
          f"({len(solo_vis)} solo VIS, {len(solo_ir)} solo IR)")
    # las escenas donde la condicion literal es posible
    esc_apta = sorted({k.split("|")[0] for k in solo_vis} & {k.split("|")[0] for k in solo_ir})
    print(f"escenas con al menos un objeto exclusivo de cada modalidad: {len(esc_apta)}\n")

    filas = []
    det_todo = {}
    t00 = time.time()
    for r in radios:
        t0 = time.time()
        # por escena: una pasada de morfologia, y todos los pesos de ese radio salen de una resta
        det = {m: {} for m in pesos}     # peso -> clave de objeto -> detectado
        for k, (s, gt) in enumerate(escenas):
            v = gris01(dV / f"{s}.png")
            i = gris01(dI / f"{s}.png")
            if v is None or i is None:
                continue
            if v.shape != i.shape:
                i = cv2.resize(i, (v.shape[1], v.shape[0]))
            wv, bv = combined_top_hat(v, r, "sum")
            wi, bi = combined_top_hat(i, r, "sum")
            wmax, bmax = np.maximum(wv, wi), np.maximum(bv, bi)
            b0 = 0.5 * (v + i)
            for m in pesos:
                fus = np.clip(b0 + m * wmax - m * bmax, 0.0, 1.0)
                pr = modelo.predict(jpeg_ida_y_vuelta(fus), conf=a.conf, verbose=False)[0]
                pred = {base.PEOPLE: [], base.LAMP: []}
                bb = pr.boxes
                if bb is not None and len(bb):
                    xy = bb.xyxy.cpu().numpy()
                    cl = bb.cls.cpu().numpy().astype(int)
                    for caja, c in zip(xy, cl):
                        if c in pred:
                            pred[c].append(tuple(caja))
                for c in (base.PEOPLE, base.LAMP):
                    for j, ok in enumerate(detectados(gt[c], pred[c], a.iou)):
                        det[m][f"{clave_escena(s)}|{base.NAMES[c]}|{j}"] = int(ok)
            if (k + 1) % 60 == 0:
                print(f"  r = {r}: {k + 1}/{len(escenas)} escenas "
                      f"({time.time() - t0:.0f} s)", flush=True)

        for m in pesos:
            det_todo[(r, m)] = dict(det[m])
            dd = det[m]
            rec = sum(dd.get(k, 0) for k in unica)
            rv = sum(dd.get(k, 0) for k in solo_vis)
            ri = sum(dd.get(k, 0) for k in solo_ir)
            resuelve = 0
            for s in esc_apta:
                sv = [k for k in solo_vis if k.split("|")[0] == s]
                si = [k for k in solo_ir if k.split("|")[0] == s]
                if all(dd.get(k, 0) for k in sv) and all(dd.get(k, 0) for k in si):
                    resuelve += 1
            filas.append({
                "r": r, "m": m,
                "objetos_unica_modalidad": len(unica), "recupera": rec,
                "pct_objetos": round(100 * rec / len(unica), 1),
                "recupera_solo_VIS": rv, "de_solo_VIS": len(solo_vis),
                "recupera_solo_IR": ri, "de_solo_IR": len(solo_ir),
                "escenas_aptas": len(esc_apta), "resuelve_escenas": resuelve,
                "pct_escenas": round(100 * resuelve / len(esc_apta), 1) if esc_apta else 0.0,
            })
        print(f"  r = {r} listo en {time.time() - t0:.0f} s")

    d = pd.DataFrame(filas)
    d.to_csv(GRILLA_CSV, index=False)
    if a.guardar_objetos:
        largo = [{"r": r, "m": m, "clave": k, "detectado": v}
                 for (r, m), dd in det_todo.items() for k, v in dd.items()]
        pd.DataFrame(largo).to_csv(DET_CSV, index=False)
        print(f"    detalle por objeto -> {DET_CSV.name} ({len(largo)} filas)")

    # ------------------------------------------------------------------ el control
    ctrl = d[(d.r == 25) & (np.isclose(d.m, 0.30))]
    if len(ctrl):
        esperado_obj = int(ref.loc[ref.clave.isin(unica), PROP].sum())
        esperado_esc = 0
        for s in esc_apta:
            sv = ref[(ref.clave.isin(solo_vis)) & (ref.escena.map(clave_escena) == s)]
            si = ref[(ref.clave.isin(solo_ir)) & (ref.escena.map(clave_escena) == s)]
            if sv[PROP].all() and si[PROP].all():
                esperado_esc += 1
        obt_obj = int(ctrl.recupera.iloc[0])
        obt_esc = int(ctrl.resuelve_escenas.iloc[0])
        print(f"\n--- CONTROL en (25; 0,30), el punto publicado")
        print(f"    objetos recuperados: {obt_obj} · esperado {esperado_obj}")
        print(f"    escenas resueltas:   {obt_esc} · esperado {esperado_esc}")
        if abs(obt_obj - esperado_obj) > 2 or obt_esc != esperado_esc:
            raise SystemExit(
                "ABORTA: el punto de control NO reproduce la medicion publicada, asi que la grilla "
                "esta midiendo otra cosa. Revisar el ida y vuelta JPEG y el filtro de escenas.")
        print("    reproduce: la grilla mide lo mismo")

    print(f"\n--- la grilla, ordenada por la condicion literal (escenas resueltas)")
    print(d.sort_values(["resuelve_escenas", "recupera"], ascending=False)[
        ["r", "m", "resuelve_escenas", "escenas_aptas", "pct_escenas",
         "recupera", "pct_objetos", "recupera_solo_VIS", "recupera_solo_IR"]].to_string(index=False))
    print(f"\n  -> {GRILLA_CSV.name} · {time.time() - t00:.0f} s en total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
