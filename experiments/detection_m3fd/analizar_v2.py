# -*- coding: utf-8 -*-
"""Analisis de la deteccion de objetos en M3FD (Seccion 3.5 del libro).

Lee las predicciones crudas de evaluar_v2.py y la prueba final de prueba_v2.py, y aplica sin tocar la GPU:

  1. Umbral por detector, calibrado en los cuadros de seguimiento (sobrante): el que da el mismo numero de
     falsos positivos de personas y luces por imagen que el detector de la VISIBLE con umbral 0,25.
  2. Objetos de una sola camara en la prueba: los que la mayoria de las semillas del detector visible
     encuentra y la del infrarrojo no, o al reves.
  3. Puntaje de cada fusion en cada objeto: la fraccion de sus semillas que lo encuentra.
  4. Medida principal: tasa de acierto equilibrada, promedio de la tasa sobre los objetos de solo visible
     y la tasa sobre los de solo infrarroja.
  5. Propuesta menos cada metodo: IC 95 % con varianza robusta por grupos y t con K-1 grados de libertad;
     sensibilidad con las nueve diferencias entre pares de semillas. Las columnas wild_lo y wild_hi guardan
     un bootstrap salvaje por grupos (pesos de Webb) sin estudentizar, que el libro no usa: el del libro,
     estudentizado y con la nula impuesta, lo calcula bootstrap_estudentizado_v2.py.
  6. Sensibilidad con umbral fijo 0,25 y con umbral de maximo F1 por clase. Las columnas cota, desenlace y
     desenlace_wild comparan cada intervalo con una cota fija (-5 puntos frente a los multiescala y 0 frente
     al Top-Hat clasico y al promedio simple); el libro no las usa: solo examina la diferencia con el
     Top-Hat clasico y da las demas como referencia.
  7. Secundarias: condicion por imagen, objetos de ambas camaras y convergencia de la primera ronda
     (ronda 0).

Si alguna entrada tiene menos de tres semillas, se usa el mismo numero de semillas para todas y el
resultado se marca INCOMPLETO (regla de corte).

SALIDAS en experiments/results/metrics_reports/: m3fd_v2_umbrales.csv, m3fd_v2_tasas.csv,
m3fd_v2_contrastes.csv, m3fd_v2_pares_semillas.csv, m3fd_v2_convergencia.csv

ENTRADAS QUE NO SE PUBLICAN: las etiquetas y las imagenes de
datasets/m3fd2_VIS/{labels,images}/{sobrante,val,test} (preparar_v2.py) y, solo para la convergencia,
runs/m3fd_v2/<entrada>_s<semilla>/results.csv (entrenar_v2.py). Sin datasets/ el calculo se detiene; sin
runs/, m3fd_v2_convergencia.csv se reescribe vacio (se recupera con git checkout).

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/detection_m3fd/analizar_v2.py
"""
import sys
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DATOS = ROOT / "datasets"
RUNS = ROOT / "runs" / "m3fd_v2"
MR = ROOT / "experiments" / "results" / "metrics_reports"
PROP = "Propuesta_Novedosa"
MULTI = ["PiramideLaplace", "RatioPiramide", "DWT", "DTCWT", "Curvelet"]
CLASICO = "TopHat_Clasico"
PROMEDIO = "Promedio"
FUSIONES = [PROP, PROMEDIO] + MULTI + [CLASICO]
REFERENCIA = ["VIS", "IR"]
CLASES = ("People", "Lamp")
IOU = 0.5
MARGEN = -0.05
GRILLA = np.round(np.arange(0.05, 0.951, 0.01), 2)
B = 9999
WEBB = np.array([-np.sqrt(1.5), -1.0, -np.sqrt(0.5), np.sqrt(0.5), 1.0, np.sqrt(1.5)])


# ---------------------------------------------------------------- datos
def leer_gt(partes, ids=None):
    import cv2
    out = {}
    carp = DATOS / "m3fd2_VIS"
    for parte in partes:
        for lb in sorted((carp / "labels" / parte).glob("*.txt")):
            if ids is not None and lb.stem not in ids:
                continue
            im = cv2.imread(str(carp / "images" / parte / f"{lb.stem}.jpg"), cv2.IMREAD_GRAYSCALE)
            alto, ancho = im.shape[:2]
            g = {c: [] for c in CLASES}
            for linea in lb.read_text(encoding="utf-8").splitlines():
                c, cx, cy, w, h = linea.split()
                nombre = {"0": "People", "4": "Lamp"}.get(c)
                if nombre:
                    cx, cy = float(cx) * ancho, float(cy) * alto
                    w, h = float(w) * ancho, float(h) * alto
                    g[nombre].append((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
            out[lb.stem] = g
    return out


def iou(a, b):
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / u if u > 0 else 0.0


def emparejar(gt, pred):
    """Emparejamiento: por cada caja marcada, la prediccion libre de mayor IoU."""
    libres, ok = list(pred), []
    for g in gt:
        mejor, k = 0.0, -1
        for j, p in enumerate(libres):
            v = iou(g, p)
            if v > mejor:
                mejor, k = v, j
        if mejor >= IOU and k >= 0:
            ok.append(True)
            libres.pop(k)
        else:
            ok.append(False)
    return ok, len(libres)


def indexar(pred, partes):
    d = {}
    sub = pred[pred.parte.isin(partes)]
    for (e, s, im, c), g in sub.groupby(["entrada", "semilla", "imagen", "clase"]):
        d.setdefault((e, int(s)), {}).setdefault(im, {})[c] = \
            list(zip(g.conf.values, g[["x1", "y1", "x2", "y2"]].values.tolist()))
    return d


def umbral_de(t, c):
    return t[c] if isinstance(t, dict) else t


def fp_por_imagen(det, gt, t):
    fp = 0
    for im, g in gt.items():
        for c in CLASES:
            p = [caja for cf, caja in det.get(im, {}).get(c, []) if cf >= umbral_de(t, c)]
            fp += emparejar(g[c], p)[1]
    return fp / len(gt)


def f1_optimo(det, gt, c):
    mejor = (0.25, -1.0)
    n_gt = sum(len(g[c]) for g in gt.values())
    for t in GRILLA:
        tp = fp = 0
        for im, g in gt.items():
            p = [caja for cf, caja in det.get(im, {}).get(c, []) if cf >= t]
            ok, libres = emparejar(g[c], p)
            tp += sum(ok)
            fp += libres
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / n_gt if n_gt else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        if f1 > mejor[1]:
            mejor = (float(t), f1)
    return mejor[0]


def detecciones(det, gt, t):
    out = {}
    for im, g in gt.items():
        for c in CLASES:
            p = [caja for cf, caja in det.get(im, {}).get(c, []) if cf >= umbral_de(t, c)]
            for j, ok in enumerate(emparejar(g[c], p)[0]):
                out[f"{im}|{c}|{j}"] = int(ok)
    return out


# ---------------------------------------------------------------- inferencia
def diferencia(d, dirs, grupo):
    """Diferencia equilibrada, IC por grupos (t, K-1) y bootstrap salvaje por grupos (Webb)."""
    d, dirs, grupo = np.asarray(d, float), np.asarray(dirs), np.asarray(grupo)
    mV, mI = d[dirs == "V"].mean(), d[dirs == "I"].mean()
    est = 0.5 * mV + 0.5 * mI
    nV, nI = (dirs == "V").sum(), (dirs == "I").sum()
    psi = np.where(dirs == "V", 0.5 * (d - mV) / nV, 0.5 * (d - mI) / nI)
    gs = np.unique(grupo)
    K = len(gs)
    s = np.array([psi[grupo == g].sum() for g in gs])
    se = np.sqrt(K / (K - 1) * (s ** 2).sum())
    tq = stats.t.ppf(0.975, K - 1)
    rng = np.random.default_rng(0)
    w = rng.choice(WEBB, size=(B, K))
    delta = np.sqrt(K / (K - 1)) * (w @ s)
    lo_b = est - np.quantile(delta, 0.975)
    hi_b = est - np.quantile(delta, 0.025)
    return est, est - tq * se, est + tq * se, lo_b, hi_b, K


def desenlace(lo, hi, cota):
    if lo > cota:
        return "sostenida"
    if hi < cota:
        return "refutada"
    return "no concluyente"


# ---------------------------------------------------------------- convergencia
def convergencia(semillas):
    filas, orden30, orden40 = [], {}, {}
    for e in REFERENCIA + FUSIONES:
        s = semillas[e][0]
        f = RUNS / f"{e}_s{s}" / "results.csv"
        if not f.exists():
            continue
        r = pd.read_csv(f)
        r.columns = [c.strip() for c in r.columns]
        col = [c for c in r.columns if "mAP50(B)" in c]
        if not col or r[col[0]].isna().all() or (r[col[0]] == 0).all():
            continue
        m = r[col[0]].values
        pend = np.polyfit(np.arange(5), m[-5:], 1)[0] if len(m) >= 5 else np.nan
        filas.append({"entrada": e, "semilla": s, "mAP50_ep30": round(float(m[29]), 4) if len(m) >= 30 else np.nan,
                      "mAP50_ep40": round(float(m[-1]), 4), "pendiente_ultimas_5": round(float(pend), 5)})
        if len(m) >= 30:
            orden30[e], orden40[e] = m[29], m[-1]
    df = pd.DataFrame(filas)
    cambios = []
    if PROP in orden30:
        for e in orden30:
            if e != PROP and np.sign(orden30[PROP] - orden30[e]) != np.sign(orden40[PROP] - orden40[e]):
                cambios.append(e)
    return df, cambios


# ---------------------------------------------------------------- principal
def main():
    pred = pd.read_csv(MR / "m3fd_v2_predicciones.csv").drop_duplicates()
    pred["imagen"] = pred.imagen.map(lambda x: f"{int(x):05d}")
    prueba = pd.read_csv(MR / "m3fd_v2_prueba.csv")
    prueba = prueba[prueba.entra]
    ids_prueba = {f"{int(i):05d}" for i in prueba.id}
    grupo_de = {f"{int(i):05d}": int(g) for i, g in zip(prueba.id, prueba.grupo)}

    gt_cal = leer_gt(["sobrante"])
    gt_test = leer_gt(["test", "val"], ids_prueba)
    cal, test = indexar(pred, ["sobrante"]), indexar(pred, ["test", "val"])
    dets = sorted(set(cal) & set(test))
    semillas = {}
    for e, s in dets:
        semillas.setdefault(e, []).append(s)
    faltan = [e for e in REFERENCIA + FUSIONES if e not in semillas]
    if faltan:
        print(f"  faltan entradas: {faltan}; no se puede analizar todavia")
        return 1
    n_sem = min(len(v) for v in semillas.values())
    semillas = {e: sorted(v)[:n_sem] for e, v in semillas.items()}      # mismo numero para todas
    dets = [(e, s) for e in semillas for s in semillas[e]]
    incompleto = n_sem < 3
    print(f"  prueba: {len(gt_test)} cuadros; detectores: {len(dets)}; semillas por entrada: {n_sem}"
          + ("  ->  RESULTADO INCOMPLETO" if incompleto else ""))

    # 1. umbrales, calibrados en los cuadros de seguimiento
    objetivo = float(np.mean([fp_por_imagen(cal[("VIS", s)], gt_cal, 0.25) for s in semillas["VIS"]]))
    filas_u, umbral, umbral_f1 = [], {}, {}
    for k in dets:
        curva = [(t, fp_por_imagen(cal[k], gt_cal, t)) for t in GRILLA]
        umbral[k] = min(curva, key=lambda x: (abs(x[1] - objetivo), x[0]))[0]
        umbral_f1[k] = {c: f1_optimo(cal[k], gt_cal, c) for c in CLASES}
        filas_u.append({"entrada": k[0], "semilla": k[1], "umbral_fppi": umbral[k],
                        "fppi_025": round(fp_por_imagen(cal[k], gt_cal, 0.25), 4),
                        "umbral_f1_personas": umbral_f1[k]["People"], "umbral_f1_luces": umbral_f1[k]["Lamp"]})
    pd.DataFrame(filas_u).to_csv(MR / "m3fd_v2_umbrales.csv", index=False)
    print(f"  falsos positivos por imagen del detector visible con 0,25 (objetivo) = {objetivo:.3f}")

    filas_t, filas_c, filas_p = [], [], []
    puntos = {"fppi": lambda k: umbral[k], "0.25": lambda k: 0.25, "f1": lambda k: umbral_f1[k]}
    for punto, u in puntos.items():
        D = {k: detecciones(test[k], gt_test, u(k)) for k in dets}
        claves = sorted(next(iter(D.values())))
        M = {k: np.array([D[k][c] for c in claves]) for k in dets}
        def mayoria(e):
            return np.mean([M[(e, s)] for s in semillas[e]], axis=0) > 0.5
        vis, ir = mayoria("VIS"), mayoria("IR")
        solo_v, solo_i, ambas = vis & ~ir, ir & ~vis, vis & ir
        sel = solo_v | solo_i
        dirs = np.where(solo_v, "V", "I")[sel]
        grp = np.array([grupo_de[c.split("|")[0]] for c in claves])[sel]
        punt = {e: np.mean([M[(e, s)] for s in semillas[e]], axis=0) for e in FUSIONES}
        # condicion por imagen: imagenes con al menos un objeto de cada direccion
        img = np.array([c.split("|")[0] for c in claves])
        imgs_ambas = sorted(set(img[solo_v]) & set(img[solo_i]))
        for e in FUSIONES:
            p = punt[e]
            ambas_img = np.mean([np.mean([M[(e, s)][(img == im) & solo_v].max() *
                                          M[(e, s)][(img == im) & solo_i].max() for im in imgs_ambas])
                                 for s in semillas[e]]) if imgs_ambas else np.nan
            filas_t.append({"punto": punto, "entrada": e,
                            "solo_visible": round(p[solo_v].mean(), 4),
                            "solo_infrarroja": round(p[solo_i].mean(), 4),
                            "equilibrada": round(0.5 * p[solo_v].mean() + 0.5 * p[solo_i].mean(), 4),
                            "de_ambas": round(p[ambas].mean(), 4),
                            "imagenes_con_los_dos": round(float(ambas_img), 4),
                            "n_solo_visible": int(solo_v.sum()), "n_solo_infrarroja": int(solo_i.sum()),
                            "n_ambas": int(ambas.sum()), "n_imagenes_con_los_dos": len(imgs_ambas)})
        for otro in MULTI + [CLASICO, PROMEDIO]:
            d = (punt[PROP] - punt[otro])[sel]
            est, lo, hi, lob, hib, K = diferencia(d, dirs, grp)
            cota = MARGEN if otro in MULTI else 0.0
            pares = []
            for sp, so in product(semillas[PROP], semillas[otro]):
                dd = (M[(PROP, sp)] - M[(otro, so)])[sel].astype(float)
                pares.append(0.5 * dd[dirs == "V"].mean() + 0.5 * dd[dirs == "I"].mean())
                filas_p.append({"punto": punto, "contra": otro, "semilla_propuesta": sp,
                                "semilla_otro": so, "diferencia": round(pares[-1], 4)})
            filas_c.append({"punto": punto, "contra": otro, "diferencia": round(est, 4),
                            "ic_lo": round(lo, 4), "ic_hi": round(hi, 4),
                            "wild_lo": round(lob, 4), "wild_hi": round(hib, 4), "grupos": K,
                            "cota": cota, "desenlace": desenlace(lo, hi, cota),
                            "desenlace_wild": desenlace(lob, hib, cota),
                            "pares_min": round(min(pares), 4), "pares_max": round(max(pares), 4),
                            "robusta_a_la_semilla": bool(min(pares) > 0 or max(pares) < 0)})
    tasas, cont = pd.DataFrame(filas_t), pd.DataFrame(filas_c)
    tasas.to_csv(MR / "m3fd_v2_tasas.csv", index=False)
    cont.to_csv(MR / "m3fd_v2_contrastes.csv", index=False)
    pd.DataFrame(filas_p).to_csv(MR / "m3fd_v2_pares_semillas.csv", index=False)
    conv, cambios = convergencia(semillas)
    conv.to_csv(MR / "m3fd_v2_convergencia.csv", index=False)

    print("\n  === Tasas sobre los objetos de una sola camara (umbral de igual falsos positivos) ===")
    print(tasas[tasas.punto == "fppi"].drop(columns="punto").to_string(index=False))
    print("\n  === Propuesta menos cada metodo, tasa equilibrada, IC 95 % por grupos ===")
    print(cont[cont.punto == "fppi"].drop(columns="punto").to_string(index=False))
    if incompleto:
        print("\n  INCOMPLETO: menos de tres semillas")
    pr = cont[(cont.punto == "fppi") & (cont.contra == PROMEDIO)].iloc[0]
    print(f"  Contraste con el promedio simple: {pr.diferencia:+.4f} [{pr.ic_lo:+.4f}; {pr.ic_hi:+.4f}] "
          f"-> {pr.desenlace}")
    if cambios:
        print(f"  Convergencia: la propuesta cambia de orden entre las epocas 30 y 40 con {cambios}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
