# -*- coding: utf-8 -*-
"""PSO por imagen: las 25 configuraciones del Cuadro 1 sobre CADA par VIS/IR del TNO.

Reproduce la presentacion de los anexos del trabajo de referencia (Ortega y Espinoza,
2025): para cada imagen se ejecutan las 25 combinaciones de particulas e iteraciones
(n en {2,4,6,8,10} x T en {10,20,30,40,50}), cada una optimizando (r, m) con la aptitud
F_o = SSIM_avg + E_n + PSNR_n sobre el espacio de busqueda publicado r en [1,25],
m en [0,30; 2,00]. Por cada configuracion se reporta el optimo hallado y las metricas
de la imagen fusionada en ese optimo.

Optimizacion de costo: para una imagen y un radio dados, las respuestas morfologicas
(WTH/BTH combinadas y su maximo entre fuentes) NO dependen de m, de modo que se
precalculan una sola vez por radio; cada evaluacion de aptitud queda reducida a la
reconstruccion y las metricas.

Salida: experiments/results/metrics_reports/pso_por_imagen.csv
        (una fila por imagen x configuracion: 20 x 25 = 500 filas)
Uso:    .venv\Scripts\python.exe -X utf8 experiments/pso_por_imagen.py [--probe] [--procesos N]
"""
import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np

from src.datasets import list_pairs, load_pair
from src.fusion.optimal_top_hat import combined_top_hat
from src.metrics.evaluators import (entropy, std_dev, spatial_frequency,
                                    ssim_fusion, psnr_fusion)

ROOT = Path(__file__).resolve().parents[1]
SALIDA = ROOT / "experiments" / "results" / "metrics_reports" / "pso_por_imagen.csv"

PARTICULAS = [2, 4, 6, 8, 10]
ITERACIONES = [10, 20, 30, 40, 50]
R_LO, R_HI = 1, 25            # rango de radio del trabajo de referencia
M_LO, M_HI = 0.30, 2.00       # rango de peso publicado (se puede cambiar con --m-min)
W_MAX, W_MIN, C1, C2 = 0.9, 0.4, 1.5, 1.5


def precalcular(vis, ir):
    """Devuelve (base, {r: (wth_max, bth_max)}) para todos los radios enteros del rango."""
    base = 0.5 * (vis.astype(np.float32) + ir.astype(np.float32))
    ramas = {}
    for r in range(R_LO, R_HI + 1):
        wv, bv = combined_top_hat(vis, r, "sum")
        wi, bi = combined_top_hat(ir, r, "sum")
        ramas[r] = (np.maximum(wv, wi), np.maximum(bv, bi))
    return base, ramas


def fusionar(base, ramas, r, m):
    w, b = ramas[int(r)]
    return np.clip(base + m * w - m * b, 0.0, 1.0).astype(np.float32)


def aptitud(vis, ir, base, ramas, r, m, cache):
    """F_o = SSIM_avg + E/8 + PSNR/100 (definiciones oficiales del proyecto)."""
    clave = (int(r), round(float(m), 4))
    if clave in cache:
        return cache[clave]
    f = fusionar(base, ramas, clave[0], clave[1])
    fo = ssim_fusion(f, vis, ir) + entropy(f) / 8.0 + psnr_fusion(f, vis, ir) / 100.0
    cache[clave] = fo
    return fo


def pso(vis, ir, base, ramas, n, tmax, semilla, cache, m_lo=M_LO):
    """PSO estandar de 2 variables; devuelve (r*, m*, F_o*)."""
    rng = np.random.default_rng(semilla)
    lo = np.array([R_LO, m_lo], dtype=np.float64)
    hi = np.array([R_HI, M_HI], dtype=np.float64)
    x = lo + rng.random((n, 2)) * (hi - lo)
    v = np.zeros((n, 2))
    pbest = x.copy()
    pfit = np.array([aptitud(vis, ir, base, ramas, xi[0], xi[1], cache) for xi in x])
    g = int(np.argmax(pfit))
    gbest, gfit = pbest[g].copy(), float(pfit[g])
    for t in range(tmax):
        w = W_MAX - (W_MAX - W_MIN) * t / max(1, tmax - 1)
        r1, r2 = rng.random((n, 2)), rng.random((n, 2))
        v = w * v + C1 * r1 * (pbest - x) + C2 * r2 * (gbest - x)
        x = np.clip(x + v, lo, hi)
        fit = np.array([aptitud(vis, ir, base, ramas, xi[0], xi[1], cache) for xi in x])
        mejora = fit > pfit
        pbest[mejora], pfit[mejora] = x[mejora], fit[mejora]
        g = int(np.argmax(pfit))
        if float(pfit[g]) > gfit:
            gbest, gfit = pbest[g].copy(), float(pfit[g])
    return int(round(gbest[0])), float(gbest[1]), gfit


def procesar_imagen(args):
    """Ejecuta las 25 configuraciones sobre una imagen. Devuelve la lista de filas."""
    idx, par, m_lo = args
    vis, ir = load_pair(*par)
    nombre = Path(par[0]).stem
    t0 = time.time()
    base, ramas = precalcular(vis, ir)
    cache = {}
    filas = []
    for n in PARTICULAS:
        for tmax in ITERACIONES:
            r, m, fo = pso(vis, ir, base, ramas, n, tmax,
                           semilla=1000 * idx + 10 * n + tmax, cache=cache, m_lo=m_lo)
            f = fusionar(base, ramas, r, m)
            filas.append(dict(
                imagen=nombre, particulas=n, iteraciones=tmax, r=r, m=round(m, 4),
                SSIM_avg=round(ssim_fusion(f, vis, ir), 6),
                E=round(entropy(f), 6),
                SF=round(spatial_frequency(f), 6),
                SD=round(std_dev(f), 6),
                PSNR=round(psnr_fusion(f, vis, ir), 6),
                FO=round(fo, 6)))
    print(f"  [{idx + 1:2d}/20] {nombre[:44]:44s} {time.time() - t0:6.1f}s "
          f"| evaluaciones unicas: {len(cache)}", flush=True)
    return filas


def main():
    global M_LO, SALIDA
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true", help="solo la primera imagen, para medir")
    ap.add_argument("--procesos", type=int, default=max(1, (os.cpu_count() or 4) - 2))
    ap.add_argument("--m-min", type=float, default=M_LO,
                    help="limite inferior del peso (0.30 = rango publicado)")
    ap.add_argument("--salida", default=None, help="nombre del CSV de salida")
    a = ap.parse_args()
    if a.m_min != M_LO:
        M_LO = a.m_min
        print(f"rango de m ampliado: [{M_LO}; {M_HI}]", flush=True)
    if a.salida:
        SALIDA = SALIDA.parent / a.salida

    pares = list_pairs()
    _t = [(k, p, M_LO) for k, p in enumerate(pares)]
    tareas = _t[:1] if a.probe else _t
    print(f"{len(tareas)} imagen(es) x {len(PARTICULAS) * len(ITERACIONES)} configuraciones "
          f"| procesos: {1 if a.probe else a.procesos}", flush=True)

    t0 = time.time()
    if a.probe or a.procesos <= 1:
        res = [procesar_imagen(t) for t in tareas]
    else:
        import multiprocessing as mp
        with mp.Pool(a.procesos) as pool:
            res = pool.map(procesar_imagen, tareas)
    filas = [x for grupo in res for x in grupo]

    import pandas as pd
    df = pd.DataFrame(filas)
    if a.probe:
        print(df.to_string(index=False))
        print(f"\nprobe: {time.time() - t0:.1f}s para 1 imagen -> "
              f"estimado {len(pares) * (time.time() - t0) / 60:.1f} min secuencial")
        return
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SALIDA, index=False)
    print(f"\nLISTO en {(time.time() - t0) / 60:.1f} min -> {SALIDA} ({len(df)} filas)")
    mejores = df.loc[df.groupby("imagen")["FO"].idxmax()]
    print("\nMejor configuracion por imagen:")
    print(mejores[["imagen", "particulas", "iteraciones", "r", "m", "FO"]].to_string(index=False))


if __name__ == "__main__":
    main()
