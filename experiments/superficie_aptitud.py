# -*- coding: utf-8 -*-
"""superficie_aptitud.py — superficie REAL de la aptitud F_o sobre el espacio (r, m).

La figura del PSO del libro dibujaba una superficie SINTETICA con la forma
    Z = 1,7354 - 0,30*((25-r)/24)^2 - 0,45*((m-0,30)/1,70)^2
cuyo maximo esta en (r = 25, m = 0,30). Eso contradice el resultado del propio barrido: la
aptitud publicada F_o = SSIM_avg + E/8 + PSNR/100 prefiere r = 1, y r = 25 se adopta por
decision de diseno sobre las metricas de evaluacion. Una figura que ilustra un optimo donde
no esta invierte la lectura del capitulo.

Este script calcula la superficie de verdad, sobre las MISMAS escenas que usa el barrido
(list_pairs()[::7]) y con las metricas oficiales del proyecto.

Optimizacion: para una imagen y un radio dados, las respuestas morfologicas no dependen de m,
de modo que se precalculan una vez por radio y cada evaluacion queda reducida a la
reconstruccion y las metricas.

Salida: experiments/results/metrics_reports/superficie_aptitud_fo.csv  (r, m, Fo)
Uso:    .venv\Scripts\python.exe -X utf8 experiments/superficie_aptitud.py [--paso-m 0.10] [--radios 1,3,5,...]
"""
import argparse
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.datasets import list_pairs, load_pair
from src.fusion.optimal_top_hat import combined_top_hat
from src.metrics.evaluators import entropy, ssim_fusion, psnr_fusion

SALIDA = ROOT / "experiments" / "results" / "metrics_reports" / "superficie_aptitud_fo.csv"


def aptitud(f, vis, ir):
    """F_o = SSIM_avg + E/8 + PSNR/100, con las definiciones oficiales del proyecto."""
    return ssim_fusion(f, vis, ir) + entropy(f) / 8.0 + psnr_fusion(f, vis, ir) / 100.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paso-m", type=float, default=0.10)
    ap.add_argument("--m-lo", type=float, default=0.30)
    ap.add_argument("--m-hi", type=float, default=2.00)
    ap.add_argument("--radios", default="",
                    help="lista separada por comas; por defecto 1..25 de a 2 mas el 25")
    a = ap.parse_args()

    radios = ([int(x) for x in a.radios.split(",")] if a.radios
              else sorted(set(list(range(1, 26, 2)) + [25])))
    ms = np.round(np.arange(a.m_lo, a.m_hi + 1e-9, a.paso_m), 4)

    pares = list_pairs()[::7]
    print(f"escenas: {', '.join(p[0].stem for p in pares)}")
    print(f"{len(radios)} radios x {len(ms)} valores de m x {len(pares)} escenas "
          f"= {len(radios) * len(ms) * len(pares)} evaluaciones")

    t0 = time.time()
    filas = []
    for r in radios:
        # precalculo por radio: las respuestas morfologicas no dependen de m
        pre = []
        for vp, ip in pares:
            vis, ir = load_pair(vp, ip)
            base = 0.5 * (vis.astype(np.float32) + ir.astype(np.float32))
            wv, bv = combined_top_hat(vis, r, "sum")
            wi, bi = combined_top_hat(ir, r, "sum")
            pre.append((vis, ir, base, np.maximum(wv, wi), np.maximum(bv, bi)))
        for m in ms:
            vals = []
            for vis, ir, base, w, b in pre:
                f = np.clip(base + m * w - m * b, 0.0, 1.0).astype(np.float32)
                vals.append(aptitud(f, vis, ir))
            filas.append(dict(r=r, m=float(m), Fo=float(np.mean(vals))))
        print(f"  r = {r:2d} listo  ({time.time() - t0:5.1f}s)", flush=True)

    df = pd.DataFrame(filas)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SALIDA, index=False)
    mejor = df.loc[df.Fo.idxmax()]
    print(f"\nLISTO en {(time.time() - t0) / 60:.1f} min -> {SALIDA} ({len(df)} filas)")
    print(f"maximo de la superficie: r = {int(mejor.r)}, m = {mejor.m:.2f}, F_o = {mejor.Fo:.4f}")
    en25 = df[df.r == 25]
    if len(en25):
        b = en25.loc[en25.Fo.idxmax()]
        print(f"mejor en r = 25:        m = {b.m:.2f}, F_o = {b.Fo:.4f} "
              f"(deficit {mejor.Fo - b.Fo:+.4f})")
    print("\nF_o por radio en m = 0,30 (el peso que adopta el trabajo):")
    for _, x in df[np.isclose(df.m, 0.30)].sort_values("r").iterrows():
        print(f"  r = {int(x.r):2d}  F_o = {x.Fo:.4f}")


if __name__ == "__main__":
    main()
