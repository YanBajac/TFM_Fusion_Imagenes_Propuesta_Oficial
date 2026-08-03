# -*- coding: utf-8 -*-
"""run_ablacion_banco.py — aisla el aporte del banco de cinco elementos estructurantes.

POR QUE HACE FALTA. El trabajo compara la propuesta contra el Top-Hat clasico y atribuye la
diferencia al banco de disco + cuatro lineas. Pero los dos operadores NO comparten
hiperparametros: el clasico usa r = 5 y m = 1, y la propuesta r = 25 y m = 0,30. Esa
comparacion mezcla el cambio de operador con el cambio de (r, m), de modo que no aisla nada.

Esta ablacion fija (r, m) y varia UNICAMENTE la forma de combinar las respuestas:

  disco    solo la respuesta del disco B_r                    (el operador clasico, mismo r y m)
  lineas   solo el promedio de las cuatro lineas orientadas
  suma     disco + promedio de lineas        <- la propuesta
  promedio media de disco y promedio de lineas
  maximo   maximo por pixel entre ambos
  base     sin operador: la imagen (VIS+IR)/2  (control negativo)

Todas comparten la reconstruccion F = I_base + m*max(WTH) - m*max(BTH) y se evaluan con las
17 metricas del proyecto sobre el corpus completo, con Wilcoxon-Holm de la propuesta contra
cada brazo.

Salidas (experiments/results/metrics_reports/):
  ablacion_banco.csv           una fila por brazo x imagen
  ablacion_banco_resumen.csv   medias por brazo, rango intra-bloque y contrastes
Uso:
  .venv\Scripts\python.exe -X utf8 experiments/run_ablacion_banco.py [--r 25] [--m 0.30]
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.datasets import list_pairs, load_pair
from src.fusion.optimal_top_hat import combined_top_hat
from src.metrics import evaluate_all
from src.metrics.evaluators import METRIC_DIRECTION

SALIDA = ROOT / "experiments" / "results" / "metrics_reports"
BRAZOS = ["base", "disco", "lineas", "suma", "promedio", "maximo"]
MODO = {"disco": "disco", "lineas": "lineas", "suma": "sum",
        "promedio": "avg", "maximo": "max"}
PROPUESTA = "suma"


def fusionar(vis, ir, brazo, r, m):
    base = 0.5 * (vis.astype(np.float32) + ir.astype(np.float32))
    if brazo == "base":
        return np.clip(base, 0.0, 1.0).astype(np.float32)
    wv, bv = combined_top_hat(vis, r, MODO[brazo])
    wi, bi = combined_top_hat(ir, r, MODO[brazo])
    f = base + m * np.maximum(wv, wi) - m * np.maximum(bv, bi)
    return np.clip(f, 0.0, 1.0).astype(np.float32)


def holm(ps):
    idx = np.argsort(ps)
    out = np.empty(len(ps))
    prev = 0.0
    for k, i in enumerate(idx):
        v = min(1.0, (len(ps) - k) * ps[i])
        prev = max(prev, v)
        out[i] = prev
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--r", type=int, default=25)
    ap.add_argument("--m", type=float, default=0.30)
    a = ap.parse_args()

    pares = list_pairs()
    print(f"ablacion con (r, m) fijos = ({a.r}, {a.m:.2f}) sobre {len(pares)} pares")
    print(f"brazos: {', '.join(BRAZOS)}\n")

    t0 = time.time()
    filas = []
    for k, (vp, ip) in enumerate(pares, 1):
        vis, ir = load_pair(vp, ip)
        for brazo in BRAZOS:
            f = fusionar(vis, ir, brazo, a.r, a.m)
            filas.append({"brazo": brazo, "imagen": vp.stem, **evaluate_all(f, vis, ir)})
        print(f"  [{k:2d}/{len(pares)}] {vp.stem[:44]:44s} ({time.time() - t0:5.1f}s)", flush=True)

    df = pd.DataFrame(filas)
    SALIDA.mkdir(parents=True, exist_ok=True)
    df.to_csv(SALIDA / "ablacion_banco.csv", index=False)

    METS = [c for c in df.columns if c in METRIC_DIRECTION]
    medias = df.groupby("brazo")[METS].mean()

    # rango intra-bloque promediado, igual criterio que el ranking del benchmark
    rangos = {}
    for m_ in METS:
        piv = df.pivot(index="imagen", columns="brazo", values=m_)
        asc = (METRIC_DIRECTION[m_] == "min")
        rangos[m_] = piv.rank(axis=1, ascending=asc, method="average").mean(axis=0)
    rk = pd.DataFrame(rangos)
    NUEVE = [c for c in ["EN", "SD", "FE", "MG", "MI_vis", "MI_ir", "SF", "SSIM", "PSNR"] if c in METS]

    res = medias.copy()
    res["rango_17"] = rk[METS].mean(axis=1).round(3)
    res["rango_9"] = rk[NUEVE].mean(axis=1).round(3)
    res["rango_9_sin_FE"] = rk[[c for c in NUEVE if c != "FE"]].mean(axis=1).round(3)

    # Wilcoxon-Holm de la propuesta contra cada brazo, por metrica
    contrastes = []
    otros = [b for b in BRAZOS if b != PROPUESTA]
    for m_ in METS:
        piv = df.pivot(index="imagen", columns="brazo", values=m_)
        ps, difs = [], []
        for b in otros:
            d = piv[PROPUESTA].values - piv[b].values
            difs.append(float(np.mean(d)))
            ps.append(1.0 if np.allclose(d, 0) else stats.wilcoxon(piv[PROPUESTA], piv[b]).pvalue)
        pc = holm(np.array(ps))
        for b, dd, p0, p1 in zip(otros, difs, ps, pc):
            mejor = (dd > 0) if METRIC_DIRECTION[m_] == "max" else (dd < 0)
            contrastes.append({"metrica": m_, "brazo": b, "dif_propuesta_menos_brazo": round(dd, 6),
                               "p": p0, "p_holm": p1, "sig": bool(p1 < 0.05),
                               "propuesta_mejor": bool(mejor)})
    cdf = pd.DataFrame(contrastes)
    res.round(4).to_csv(SALIDA / "ablacion_banco_resumen.csv")
    cdf.to_csv(SALIDA / "ablacion_banco_contrastes.csv", index=False)

    print(f"\nLISTO en {(time.time() - t0) / 60:.1f} min\n")
    print("=== RANGO INTRA-BLOQUE POR BRAZO (menor = mejor) ===")
    print(res[["rango_17", "rango_9", "rango_9_sin_FE"]].sort_values("rango_9").to_string())
    print("\n=== LA PROPUESTA (suma) CONTRA CADA BRAZO, con Holm ===")
    for b in otros:
        s = cdf[cdf.brazo == b]
        g = int((s.sig & s.propuesta_mejor).sum())
        p = int((s.sig & ~s.propuesta_mejor).sum())
        print(f"  vs {b:9s}  mejor en {g:2d}/{len(METS)}   peor en {p:2d}/{len(METS)}   "
              f"sin diferencia en {len(s) - g - p:2d}")
    print("\n=== EL PUNTO CENTRAL: banco completo (suma) vs disco unico, mismos (r, m) ===")
    s = cdf[cdf.brazo == "disco"]
    for _, x in s.iterrows():
        marca = "propuesta mejor" if (x.sig and x.propuesta_mejor) else (
            "disco mejor" if x.sig else "sin diferencia")
        print(f"  {x.metrica:8s} dif {x.dif_propuesta_menos_brazo:+10.5f}  "
              f"p_holm {x.p_holm:.4f}  {marca}")


if __name__ == "__main__":
    main()
