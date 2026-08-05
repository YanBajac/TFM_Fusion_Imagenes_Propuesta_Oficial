# -*- coding: utf-8 -*-
"""El optimo exacto de la aptitud, por enumeracion, y cuanto de el encuentra el PSO.

Motivo: la pregunta «¿mejorarian m y r con mas corridas?» no se contesta con mas corridas.
La aptitud es determinista y el radio es ENTERO —el codigo hace int(round(clip(x, 1, 25)))—,
de modo que el espacio tiene 25 valores en una dimension y un continuo suave en la otra.
Se puede enumerar: 25 radios x un barrido fino de m da el maximo global sin azar, en una
fraccion del costo de mil corridas de PSO, y ademas permite medir cuantas corridas del
estudio de estabilidad lo encontraron.

Usa el mismo fitness cacheado por radio de pso_repeticiones.py, verificado bit a bit contra
fuse_optimal, de modo que los valores son comparables con los del barrido publicado.

Salida: experiments/results/metrics_reports/optimo_exacto_fo.csv (una fila por (r, m))
        y un resumen por consola.
Uso:    .venv\\Scripts\\python.exe -X utf8 experiments/optimo_exacto_fo.py [--paso 0.005]
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, '.')
import numpy as np
import pandas as pd

import experiments.pso_grid_search_fo as G
from experiments.pso_repeticiones import escenas, hacer_fitness

RAIZ = Path(__file__).resolve().parent.parent
MR = RAIZ / 'experiments' / 'results' / 'metrics_reports'
SALIDA = MR / 'optimo_exacto_fo.csv'
PISO_PUB, TECHO_PUB = 0.30, 2.00        # el rango publicado por Ortega y Espinoza


def coma(v, nd=4):
    return f'{v:.{nd}f}'.replace('.', ',')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--paso', type=float, default=0.005, help='paso del barrido en m')
    ap.add_argument('--m-lo', type=float, default=0.01)
    ap.add_argument('--m-hi', type=float, default=2.00)
    ap.add_argument('--operator', default='propuesta')
    a = ap.parse_args()

    # el fitness recorta a G.LO/G.HI: hay que abrirlo para poder barrer por debajo de 0,30
    G.LO = np.array([1.0, min(a.m_lo, PISO_PUB)])
    G.HI = np.array([25.0, max(a.m_hi, TECHO_PUB)])
    ESC = escenas()
    fitness, _ = hacer_fitness(a.operator, ESC)

    pesos = np.round(np.arange(a.m_lo, a.m_hi + 1e-9, a.paso), 6)
    radios = list(range(1, 26))
    total = len(radios) * len(pesos)
    print(f'enumerando {len(radios)} radios x {len(pesos)} pesos = {total:,} evaluaciones')
    print(f'escenas: {", ".join(c["nombre"] for c in ESC)}')

    filas, t0 = [], time.time()
    for k, r in enumerate(radios, 1):
        for m in pesos:
            filas.append({'r': r, 'm': float(m), 'Fo': fitness(np.array([float(r), float(m)]))})
        hecho = k * len(pesos)
        print(f'  r = {r:2d}  ({hecho:,}/{total:,}, {time.time() - t0:.0f} s)', flush=True)

    d = pd.DataFrame(filas)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(SALIDA, index=False)

    glob = d.loc[d.Fo.idxmax()]
    pub = d[(d.m >= PISO_PUB - 1e-9) & (d.m <= TECHO_PUB + 1e-9)]
    mpub = pub.loc[pub.Fo.idxmax()]
    print()
    print(f'=== optimo GLOBAL (m libre en [{a.m_lo}, {a.m_hi}]) ===')
    print(f'  r = {int(glob.r)} · m = {coma(glob.m)} · Fo = {coma(glob.Fo)}')
    print(f'=== optimo DENTRO del rango publicado [0,30; 2,00] ===')
    print(f'  r = {int(mpub.r)} · m = {coma(mpub.m)} · Fo = {coma(mpub.Fo)}')
    print(f'  el rango publicado cuesta {coma(glob.Fo - mpub.Fo)} de aptitud')

    print(f'\n=== el mejor m por radio, dentro del rango publicado ===')
    mejor_r = pub.loc[pub.groupby('r').Fo.idxmax()].sort_values('Fo', ascending=False)
    print(mejor_r.head(6).to_string(index=False))
    print(f'  ... y el peor radio: r = {int(mejor_r.iloc[-1].r)} con Fo = {coma(mejor_r.iloc[-1].Fo)}')
    print(f'  en los {len(mejor_r)} radios el mejor m es siempre el piso: '
          f'{bool((mejor_r.m <= PISO_PUB + 1e-9).all())}')

    # cuanto de esto encontro el PSO
    rep = MR / f'pso_repeticiones_{a.operator}.csv'
    if rep.exists():
        p = pd.read_csv(rep)
        hallado = (p.Fo_opt - mpub.Fo).abs() < 5e-4
        print(f'\n=== que encontro el PSO en {len(p)} corridas ===')
        print(f'  el optimo del rango publicado ({coma(mpub.Fo)}): {int(hallado.sum())} de '
              f'{len(p)} corridas ({100 * hallado.mean():.1f} %)')
        print(f'  su mejor valor: {coma(p.Fo_opt.max())} · su peor: {coma(p.Fo_opt.min())}')
        mejor_que = (p.Fo_opt > mpub.Fo + 5e-4).sum()
        print(f'  corridas que SUPERAN el optimo enumerado: {int(mejor_que)}')
        print('  -> mas corridas no pueden mejorarlo: el maximo ya esta alcanzado'
              if mejor_que == 0 else
              '  -> ATENCION: hay corridas por encima del optimo enumerado; revisar el barrido')
    print(f'\n-> {SALIDA.relative_to(RAIZ)}  ({time.time() - t0:.0f} s)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
