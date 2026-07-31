# -*- coding: utf-8 -*-
"""run_ajuste_comparativos.py — da a los comparativos el mismo paso de ajuste que a la propuesta.

POR QUE HACE FALTA. El radio de la propuesta (r = 25) se eligio mirando las nueve metricas de
evaluacion, mientras los seis metodos comparativos corrieron con su parametro por defecto. Esa
asimetria es la objecion mas dificil de responder en la defensa: si el ajuste explica parte de
la ventaja, hay que saberlo y declararlo.

Este experimento barre el parametro principal de cada comparativo y selecciona su mejor
configuracion con EL MISMO CRITERIO con que se eligio r = 25: el promedio de rangos
intra-bloque sobre las nueve metricas, calculado entre las configuraciones del propio metodo.
Despues rearma el benchmark con cada metodo en su mejor configuracion y recalcula el ranking.

Se reportan cuatro escenarios:
  A. todos por defecto (lo publicado hoy)
  B. comparativos ajustados, propuesta fija en (r = 25, m = 0,30)
  C. B mas la propuesta tambien ajustada en r por el mismo criterio (simetria completa)
  D. igual que B pero rankeando con las 17 metricas

Salidas (experiments/results/metrics_reports/):
  ajuste_comparativos.csv           una fila por (metodo, configuracion, imagen)
  ajuste_comparativos_mejores.csv   mejor configuracion de cada metodo y su rango interno
  ajuste_comparativos_ranking.csv   el ranking en los cuatro escenarios
Uso:
  python experiments/run_ajuste_comparativos.py
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.datasets import list_pairs, load_pair
from src.fusion import (laplacian_pyramid_fusion, ratio_pyramid_fusion, dwt_fusion,
                        dtcwt_fusion, curvelet_fusion, tophat_classic_fusion, fuse_optimal)
from src.metrics import evaluate_all
from src.metrics.evaluators import METRIC_DIRECTION

SALIDA = ROOT / "experiments" / "results" / "metrics_reports"
NUEVE = ["EN", "SD", "FE", "MG", "MI_vis", "MI_ir", "SF", "SSIM", "PSNR"]
PROP = "Propuesta_Novedosa"

# Parametro principal de cada metodo y los valores a barrer. El por defecto va marcado.
BARRIDO = {
    "PiramideLaplace":  ("levels", [1, 2, 3, 4, 5, 6], 4),
    "RatioPiramide":    ("levels", [1, 2, 3, 4, 5, 6], 4),
    "DWT":              ("levels", [1, 2, 3, 4, 5], 3),
    "DTCWT":            ("levels", [1, 2, 3, 4, 5, 6], 4),
    "Curvelet":         ("levels", [1, 2, 3, 4, 5], 3),
    "TopHat_Clasico":   ("r", [1, 3, 5, 7, 9, 11, 15, 19, 21, 23, 25], 5),
    PROP:               ("r", [1, 3, 5, 7, 9, 11, 15, 19, 21, 23, 25], 25),
}
FUSOR = {
    "PiramideLaplace":  lambda v, i, p: laplacian_pyramid_fusion(v, i, levels=p),
    "RatioPiramide":    lambda v, i, p: ratio_pyramid_fusion(v, i, levels=p),
    "DWT":              lambda v, i, p: dwt_fusion(v, i, levels=p),
    "DTCWT":            lambda v, i, p: dtcwt_fusion(v, i, levels=p),
    "Curvelet":         lambda v, i, p: curvelet_fusion(v, i, levels=p),
    "TopHat_Clasico":   lambda v, i, p: tophat_classic_fusion(v, i, r=p),
    PROP:               lambda v, i, p: fuse_optimal(v, i, r=p, m=0.30, mode="sum"),
}


def rango_medio(df, mets, col_metodo="clave"):
    """Promedio de rangos intra-bloque (imagen) sobre las metricas dadas."""
    out = {}
    for m in mets:
        piv = df.pivot(index="imagen", columns=col_metodo, values=m)
        asc = (METRIC_DIRECTION[m] == "min")
        out[m] = piv.rank(axis=1, ascending=asc, method="average").mean(axis=0)
    return pd.DataFrame(out).mean(axis=1)


def main():
    pares = list_pairs()
    total = sum(len(v[1]) for v in BARRIDO.values())
    print(f"{total} configuraciones x {len(pares)} pares = {total * len(pares)} fusiones")
    t0 = time.time()
    filas = []
    for metodo, (nombre_par, valores, _def) in BARRIDO.items():
        for p in valores:
            for vp, ip in pares:
                vis, ir = load_pair(vp, ip)
                try:
                    f = FUSOR[metodo](vis, ir, p)
                except Exception as exc:
                    print(f"  [SKIP] {metodo} {nombre_par}={p} / {vp.stem}: {exc}")
                    break
                filas.append({"metodo": metodo, "parametro": nombre_par, "valor": p,
                              "clave": f"{metodo}|{p}", "imagen": vp.stem,
                              **evaluate_all(f, vis, ir)})
            print(f"  {metodo:20s} {nombre_par}={p:<3} listo ({time.time() - t0:6.1f}s)",
                  flush=True)
    df = pd.DataFrame(filas)
    SALIDA.mkdir(parents=True, exist_ok=True)
    df.to_csv(SALIDA / "ajuste_comparativos.csv", index=False)
    METS = [c for c in df.columns if c in METRIC_DIRECTION]

    # ---- mejor configuracion de cada metodo, con el criterio de las nueve metricas ----
    mejores = {}
    detalle = []
    for metodo in BARRIDO:
        sub = df[df.metodo == metodo]
        if sub.empty:
            continue
        rk = rango_medio(sub, NUEVE)          # rango DENTRO de las configs del propio metodo
        best = rk.idxmin()
        mejores[metodo] = int(best.split("|")[1])
        for k, v in rk.sort_values().items():
            detalle.append({"metodo": metodo, "valor": int(k.split("|")[1]),
                            "rango_interno_9": round(float(v), 3),
                            "elegida": k == best,
                            "por_defecto": int(k.split("|")[1]) == BARRIDO[metodo][2]})
    pd.DataFrame(detalle).to_csv(SALIDA / "ajuste_comparativos_mejores.csv", index=False)
    print("\n=== mejor configuracion de cada metodo (criterio: nueve metricas) ===")
    for m, v in mejores.items():
        print(f"  {m:20s} {BARRIDO[m][0]} = {v:2d}   (por defecto {BARRIDO[m][2]})")

    # ---- escenarios de ranking ----
    def arma(sel, mets):
        trozos = [df[(df.metodo == m) & (df.valor == v)].assign(clave=m) for m, v in sel.items()]
        return rango_medio(pd.concat(trozos), mets, "clave").sort_values()

    por_defecto = {m: BARRIDO[m][2] for m in BARRIDO}
    ajustados = dict(mejores)
    ajustados_prop_fija = dict(mejores); ajustados_prop_fija[PROP] = 25

    esc = {
        "A_todos_por_defecto":        arma(por_defecto, NUEVE),
        "B_comparativos_ajustados":   arma(ajustados_prop_fija, NUEVE),
        "C_todos_ajustados":          arma(ajustados, NUEVE),
        "D_comparativos_ajustados_17": arma(ajustados_prop_fija, METS),
    }
    rdf = pd.DataFrame(esc).round(3)
    rdf.to_csv(SALIDA / "ajuste_comparativos_ranking.csv")
    print(f"\nLISTO en {(time.time() - t0) / 60:.1f} min")
    print("\n=== RANKING EN LOS CUATRO ESCENARIOS (menor = mejor) ===")
    print(rdf.to_string())
    print()
    for k, s in esc.items():
        pos = list(s.index).index(PROP) + 1 if PROP in s.index else -1
        print(f"  {k:28s} propuesta {pos}.o de {len(s)}  ({s.get(PROP, float('nan')):.3f})"
              f"   lider: {s.index[0]} {s.iloc[0]:.3f}")


if __name__ == "__main__":
    main()
