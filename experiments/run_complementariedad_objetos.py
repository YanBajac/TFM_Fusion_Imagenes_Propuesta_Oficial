# -*- coding: utf-8 -*-
"""Mide la condicion de complementariedad OBJETO POR OBJETO, y no por clase.

LA CONDICION QUE SE QUIERE MEDIR, en las palabras del director del trabajo: si el objeto A se detecta
solo en el visible y el objeto B solo en el infrarrojo, entonces A y B tienen que detectarse los dos en
la imagen fusionada. El modelo se entrena una vez con las dos modalidades y sus etiquetas, y despues
solo se INFIERE sobre las fusionadas.

POR QUE HACE FALTA ESTE SCRIPT Y NO ALCANZA run_complementariedad_escenas.py. Ese mide POR CLASE:
«recupera People» significa al menos un verdadero positivo de esa clase en la escena. Con ese grano, la
condicion estricta —cada modalidad aportando justo lo que a la otra le falta— se cumple en apenas 5 de
las 232 escenas, y con n = 5 no se puede concluir nada. El grano correcto es el OBJETO: la condicion
habla de «el objeto A» y «el objeto B», no de las clases. Contando objeto por objeto la muestra pasa de
5 escenas a cientos de objetos.

QUE CALCULA. Para cada objeto anotado, si lo detecta (IoU >= umbral) cada una de las nueve entradas.
De ahi salen dos medidas, y las dos importan:

  (a) POR OBJETO — la capacidad de fondo. De los objetos que detecta EXACTAMENTE UNA de las dos
      modalidades, cuantos conserva la fusion. Es lo que tiene que pasar para que la condicion sea
      posible: la fusion no puede perder lo que una fuente sola si veia.

  (b) POR ESCENA, la condicion literal. En las escenas que tienen al menos un objeto que solo ve el
      visible Y al menos uno que solo ve el infrarrojo, la fusion detecta los dos? Es la condicion tal
      como esta enunciada, con muestra utilizable porque ahora se arma con objetos y no con clases.

El emparejado, la lectura del GT y la busqueda de los pesos se IMPORTAN de
run_complementariedad_escenas.py, para que no haya dos implementaciones del mismo criterio.

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/run_complementariedad_objetos.py [--conf 0.25] [--iou 0.5]
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

import pandas as pd

import run_complementariedad_escenas as base

SALIDA = ROOT / "experiments" / "results" / "metrics_reports"


def salidas(pref):
    """Los tres CSV de esta particion.

    La particion por defecto —m3fd_comp, las escenas con ambas clases— conserva los nombres sin sufijo
    porque son los que ya estan versionados y citados. Cualquier otra particion escribe con sufijo, para
    que validar sobre m3fd_test no pise la medicion de m3fd_comp: los dos resultados tienen que convivir,
    porque uno es donde se ELIGIO el punto y el otro donde se VALIDA.
    """
    suf = "" if pref == "m3fd_comp" else f"_{pref}"
    return (SALIDA / f"complementariedad_objetos{suf}.csv",
            SALIDA / f"complementariedad_objetos_resumen{suf}.csv",
            SALIDA / f"complementariedad_objetos_escenas{suf}.csv")


def detectados(gt_cajas, pred_cajas, umbral):
    """Para cada caja del GT, si quedo emparejada con alguna prediccion.

    Es el mismo criterio que verdaderos_positivos() de run_complementariedad_escenas.py —mayor IoU
    primero, sin reutilizar predicciones— pero devolviendo el detalle por objeto en lugar del conteo.
    Se replica aca en vez de importarse porque esa funcion devuelve un entero y perdio el detalle.
    """
    libres = list(pred_cajas)
    out = []
    for g in gt_cajas:
        mejor, k = 0.0, -1
        for i, p in enumerate(libres):
            v = base.iou(g, p)
            if v > mejor:
                mejor, k = v, i
        if mejor >= umbral and k >= 0:
            out.append(True)
            libres.pop(k)
        else:
            out.append(False)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--iou", type=float, default=0.5)
    ap.add_argument("--prefijo", default="m3fd_comp", choices=["m3fd_comp", "m3fd_test"])
    a = ap.parse_args()
    base.PREF = a.prefijo
    OBJ_CSV, RES_CSV, ESC_CSV = salidas(a.prefijo)

    import cv2
    from ultralytics import YOLO
    pesos = base.hallar_pesos()
    print(f"pesos: {pesos}")
    modelo = YOLO(str(pesos))

    dir_val = ROOT / "datasets" / f"{base.PREF}_VIS" / "images" / "val"
    stems = sorted(p.stem for p in dir_val.glob("*.jpg"))
    print(f"conjunto {base.PREF}_<ENTRADA> · {len(stems)} escenas en la particion")

    filas = []
    for k, s in enumerate(stems):
        img0 = dir_val / f"{s}.jpg"
        im = cv2.imread(str(img0), cv2.IMREAD_GRAYSCALE)
        if im is None:
            continue
        alto, ancho = im.shape[:2]
        gt = base.leer_gt(s, ancho, alto)
        # se conservan las escenas donde CONVIVEN las dos clases complementarias, igual que el
        # analisis por clase, para que las dos medidas hablen del mismo conjunto
        if not (gt.get(base.PEOPLE) and gt.get(base.LAMP)):
            continue
        por_entrada = {}
        for e in base.ENTRADAS:
            ruta = ROOT / "datasets" / f"{base.PREF}_{e}" / "images" / "val" / f"{s}.jpg"
            if not ruta.exists():
                continue
            r = modelo.predict(str(ruta), conf=a.conf, verbose=False)[0]
            pred = {base.PEOPLE: [], base.LAMP: []}
            b = r.boxes
            if b is not None and len(b):
                xy = b.xyxy.cpu().numpy()
                cl = b.cls.cpu().numpy().astype(int)
                for caja, c in zip(xy, cl):
                    if c in pred:
                        pred[c].append(tuple(caja))
            por_entrada[e] = {c: detectados(gt[c], pred[c], a.iou)
                              for c in (base.PEOPLE, base.LAMP) if c in gt}
        if len(por_entrada) < len(base.ENTRADAS):
            continue
        for c in (base.PEOPLE, base.LAMP):
            for j in range(len(gt.get(c, []))):
                fila = {"escena": s, "clase": base.NAMES[c], "objeto": j}
                for e in base.ENTRADAS:
                    fila[e] = int(por_entrada[e][c][j])
                filas.append(fila)
        if (k + 1) % 50 == 0:
            print(f"  {k + 1}/{len(stems)} escenas...", flush=True)

    d = pd.DataFrame(filas)
    assert len(d), "no se registro ningun objeto"
    d.to_csv(OBJ_CSV, index=False)
    print(f"\n{len(d)} objetos anotados en {d.escena.nunique()} escenas -> {OBJ_CSV.name}")

    FUS = [e for e in base.ENTRADAS if e not in ("VIS", "IR")]

    # ---------------------------------------------------------------- (a) por objeto
    solo_vis = (d.VIS == 1) & (d.IR == 0)
    solo_ir = (d.IR == 1) & (d.VIS == 0)
    ambas = (d.VIS == 1) & (d.IR == 1)
    ninguna = (d.VIS == 0) & (d.IR == 0)
    print(f"\n--- los {len(d)} objetos, segun que modalidad los ve")
    print(f"    solo el visible ....... {int(solo_vis.sum()):>5}")
    print(f"    solo el infrarrojo .... {int(solo_ir.sum()):>5}")
    print(f"    las dos ............... {int(ambas.sum()):>5}")
    print(f"    ninguna ............... {int(ninguna.sum()):>5}   (ninguna fusion puede recuperarlos)")

    unica = solo_vis | solo_ir
    res = []
    for e in FUS:
        res.append({
            "entrada": e,
            "objetos_de_una_sola_modalidad": int(unica.sum()),
            "recupera": int(d.loc[unica, e].sum()),
            "pct": round(100 * d.loc[unica, e].mean(), 1),
            "recupera_solo_VIS": int(d.loc[solo_vis, e].sum()),
            "de_solo_VIS": int(solo_vis.sum()),
            "recupera_solo_IR": int(d.loc[solo_ir, e].sum()),
            "de_solo_IR": int(solo_ir.sum()),
            "conserva_de_ambas": int(d.loc[ambas, e].sum()),
            "de_ambas": int(ambas.sum()),
        })
    r = pd.DataFrame(res).sort_values("pct", ascending=False)
    r.to_csv(RES_CSV, index=False)
    print(f"\n--- (a) de los {int(unica.sum())} objetos que ve UNA SOLA modalidad, cuantos conserva "
          f"la fusion")
    print(r[["entrada", "recupera", "objetos_de_una_sola_modalidad", "pct",
             "recupera_solo_VIS", "recupera_solo_IR"]].to_string(index=False))

    # ---------------------------------------------------------------- (b) la condicion literal
    # escenas con al menos un objeto exclusivo de cada modalidad: ahi la complementariedad EXISTE y la
    # fusion tiene que recuperar los dos lados.
    g = d.assign(_sv=solo_vis, _si=solo_ir).groupby("escena")
    apta = g.apply(lambda x: bool(x._sv.any() and x._si.any()), include_groups=False)
    escenas = apta.index[apta]
    print(f"\n--- (b) la condicion literal: escenas con al menos un objeto exclusivo de CADA modalidad")
    print(f"    {len(escenas)} de {d.escena.nunique()} escenas cumplen la premisa")
    filas_e = []
    for e in FUS:
        ok = 0
        for s in escenas:
            sub = d[d.escena == s]
            sv = sub[(sub.VIS == 1) & (sub.IR == 0)]
            si = sub[(sub.IR == 1) & (sub.VIS == 0)]
            if sv[e].all() and si[e].all() and len(sv) and len(si):
                ok += 1
        filas_e.append({"entrada": e, "escenas_aptas": len(escenas), "resuelve": ok,
                        "pct": round(100 * ok / len(escenas), 1) if len(escenas) else 0.0})
    re_ = pd.DataFrame(filas_e).sort_values("resuelve", ascending=False)
    re_.to_csv(ESC_CSV, index=False)
    print(re_.to_string(index=False))
    print(f"\n  -> {RES_CSV.name} · {ESC_CSV.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
