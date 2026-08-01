# -*- coding: utf-8 -*-
"""run_saturacion_vs_m.py — cuanto recorta la reconstruccion segun el peso m.

La reconstruccion F = I_base + m*WTH - m*BTH se recorta a [0, 1] antes de evaluarse. Ese
recorte destruye informacion: los pixeles que caen fuera del rango dinamico quedan aplastados
en 0 o en 1. Cuanto mayor es m, mas pixeles se saturan.

La medicion sirve para justificar el peso adoptado con un criterio INDEPENDIENTE de la funcion
de aptitud: m = 0,30 mantiene la saturacion por debajo del 1 %, mientras el peso canonico de la
metodologia clasica (m = 1) satura varias veces mas sobre este operador, porque el banco de
cinco elementos estructurantes inyecta unas 4,2 veces mas energia de detalle que un disco unico.

Salida: experiments/results/metrics_reports/saturacion_vs_m.csv
        (m, pct_saturado_medio, pct_saturado_min, pct_saturado_max, pct_bajo_cero, pct_sobre_uno)
Uso:    python experiments/run_saturacion_vs_m.py [--r 25]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.datasets import list_pairs, load_pair
from src.fusion.optimal_top_hat import combined_top_hat

SALIDA = ROOT / "experiments" / "results" / "metrics_reports" / "saturacion_vs_m.csv"
PESOS = [0.05, 0.10, 0.20, 0.30, 0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 2.00]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--r", type=int, default=25)
    a = ap.parse_args()

    pares = list_pairs()
    print(f"saturacion del recorte con r = {a.r} sobre {len(pares)} pares")

    # Las respuestas morfologicas no dependen de m: se precalculan una vez.
    pre = []
    for vp, ip in pares:
        vis, ir = load_pair(vp, ip)
        base = 0.5 * (vis.astype(np.float32) + ir.astype(np.float32))
        wv, bv = combined_top_hat(vis, a.r, "sum")
        wi, bi = combined_top_hat(ir, a.r, "sum")
        pre.append((base, np.maximum(wv, wi), np.maximum(bv, bi)))

    filas = []
    for m in PESOS:
        pcts, bajo, sobre = [], [], []
        for base, w, b in pre:
            f = base + m * w - m * b
            bajo.append(100.0 * float(np.mean(f < 0.0)))
            sobre.append(100.0 * float(np.mean(f > 1.0)))
            pcts.append(bajo[-1] + sobre[-1])
        filas.append(dict(m=m,
                          pct_saturado_medio=round(float(np.mean(pcts)), 4),
                          pct_saturado_min=round(float(np.min(pcts)), 4),
                          pct_saturado_max=round(float(np.max(pcts)), 4),
                          pct_bajo_cero=round(float(np.mean(bajo)), 4),
                          pct_sobre_uno=round(float(np.mean(sobre)), 4)))
        print(f"  m = {m:4.2f}  saturado {filas[-1]['pct_saturado_medio']:6.2f} %  "
              f"(por debajo de 0: {filas[-1]['pct_bajo_cero']:.2f} %, "
              f"por encima de 1: {filas[-1]['pct_sobre_uno']:.2f} %)", flush=True)

    df = pd.DataFrame(filas)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SALIDA, index=False)
    print(f"\nGuardado: {SALIDA}")
    ref = df[np.isclose(df.m, 0.30)]
    uno = df[np.isclose(df.m, 1.00)]
    if len(ref) and len(uno):
        print(f"m = 0,30 satura {float(ref.pct_saturado_medio.iloc[0]):.2f} % de los pixeles; "
              f"m = 1,00 satura {float(uno.pct_saturado_medio.iloc[0]):.2f} % "
              f"({float(uno.pct_saturado_medio.iloc[0]) / float(ref.pct_saturado_medio.iloc[0]):.1f} veces mas)")


if __name__ == "__main__":
    main()
