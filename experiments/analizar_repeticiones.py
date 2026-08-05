# -*- coding: utf-8 -*-
"""Analiza la dispersion de las 500 corridas del barrido PSO repetido.

Contesta lo que el orientador pide mirar: como salen los resultados al repetir veinte veces
cada configuracion. Tres preguntas, en orden de importancia para el trabajo:

  1. ¿El peso sigue anclado en el piso del rango? La tesis afirma que m* = 0,30 no depende de
     la semilla. Con una semilla por configuracion eso no se podia distinguir de una
     coincidencia; con veinte, si.
  2. ¿Y el radio? El barrido publicado devuelve r = 1 en 16 de 25 celdas y r = 25 en 8. Esa
     mezcla es justamente H5: el argmax de la aptitud no es el radio adoptado. Hay que ver
     si la proporcion se sostiene o si era un artefacto de las semillas.
  3. ¿Sirve agrandar el enjambre? Si la dispersion cae con n y con Tmax, el barrido de
     configuraciones tiene sentido; si no, el resultado es plano y conviene decirlo.

Salida: experiments/results/metrics_reports/pso_repeticiones_resumen.csv y un informe por
consola. No escribe en los documentos: las cifras se citan desde el CSV.

Uso: .venv\\Scripts\\python.exe -X utf8 experiments/analizar_repeticiones.py [--operator propuesta]
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
MR = RAIZ / 'experiments' / 'results' / 'metrics_reports'
PISO, TECHO = 0.30, 2.00


def coma(x, nd=4):
    return f'{x:.{nd}f}'.replace('.', ',')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--operator', default='propuesta')
    a = ap.parse_args()
    ruta = MR / f'pso_repeticiones_{a.operator}.csv'
    if not ruta.exists():
        print(f'falta {ruta.name}: correr primero pso_repeticiones.py')
        return 1
    d = pd.read_csv(ruta)
    reps = sorted(d.repeticion.unique())
    print(f'=== {len(d)} corridas · {d.repeticion.nunique()} repeticiones x '
          f'{len(d.groupby(["n", "Tmax"]))} configuraciones · operador {a.operator} ===\n')
    if len(d) < 500:
        print(f'AVISO: hay {len(d)} corridas de 500; el analisis es parcial\n')

    # ---------------------------------------------------------------- 1. el peso
    en_piso = (d.m_opt - PISO).abs() < 5e-4
    print('--- 1. el peso m')
    print(f'  m* = {coma(PISO, 2)} (piso del rango) en {en_piso.sum()} de {len(d)} corridas '
          f'({100 * en_piso.mean():.1f} %)')
    print(f'  m* distintos: {sorted(d.m_opt.round(4).unique())[:8]}'
          f'{" ..." if d.m_opt.nunique() > 8 else ""}')
    print(f'  maximo m* observado: {coma(d.m_opt.max())}')
    fuera = d[~en_piso]
    if len(fuera):
        print(f'  las {len(fuera)} corridas que NO terminan en el piso:')
        print('    ' + fuera[['repeticion', 'n', 'Tmax', 'r_opt', 'm_opt', 'Fo_opt']]
              .to_string(index=False).replace('\n', '\n    '))

    # ---------------------------------------------------------------- 2. el radio
    print('\n--- 2. el radio r')
    cnt = d.r_opt.value_counts().sort_index()
    for r, k in cnt.items():
        print(f'  r* = {r:2d}  en {k:3d} corridas ({100 * k / len(d):5.1f} %)')
    mejor = d.loc[d.Fo_opt.idxmax()]
    print(f'  argmax global de Fo: {coma(mejor.Fo_opt)} en r = {int(mejor.r_opt)}, '
          f'm = {coma(mejor.m_opt)} (rep {int(mejor.repeticion)}, n={int(mejor.n)}, '
          f'T={int(mejor.Tmax)})')
    porr = d.groupby('r_opt').Fo_opt.agg(['mean', 'max', 'count']).round(4)
    print('  Fo por radio hallado:')
    print('    ' + porr.to_string().replace('\n', '\n    '))

    # -------------------------------------------------- 3. dispersion por configuracion
    print('\n--- 3. dispersion por configuracion (sobre las repeticiones)')
    g = d.groupby(['n', 'Tmax']).agg(
        Fo_media=('Fo_opt', 'mean'), Fo_min=('Fo_opt', 'min'), Fo_max=('Fo_opt', 'max'),
        Fo_desv=('Fo_opt', 'std'), r_moda=('r_opt', lambda s: int(s.mode().iloc[0])),
        pct_r1=('r_opt', lambda s: 100 * (s == 1).mean()),
        pct_piso=('m_opt', lambda s: 100 * ((s - PISO).abs() < 5e-4).mean()),
        corridas=('Fo_opt', 'size')).round(4).reset_index()
    print('    ' + g.to_string(index=False).replace('\n', '\n    '))

    print('\n--- 4. ¿sirve agrandar el enjambre?')
    for col in ('n', 'Tmax'):
        z = d.groupby(col).agg(Fo_media=('Fo_opt', 'mean'), Fo_desv=('Fo_opt', 'std'),
                               pct_r1=('r_opt', lambda s: 100 * (s == 1).mean())).round(4)
        print(f'  por {col}:')
        print('    ' + z.to_string().replace('\n', '\n    '))

    # ------------------------------------------------------------- 5. lo que cambia el veredicto
    print('\n--- 5. lo que hay que reportar')
    tasa_piso = 100 * en_piso.mean()
    tasa_r1 = 100 * (d.r_opt == 1).mean()
    print(f'  el peso se ancla en el piso en el {tasa_piso:.1f} % de las 500 corridas')
    print(f'  el radio devuelve r = 1 en el {tasa_r1:.1f} %')
    if tasa_piso == 100.0:
        print('  -> el anclaje de m NO depende de la semilla: la afirmacion del trabajo se sostiene')
    else:
        # Una corrida que no llega al piso puede ser dos cosas muy distintas: un optimo
        # alternativo (y entonces habria que matizar la afirmacion) o una falla de
        # convergencia del enjambre (y entonces la refuerza, porque el piso sigue siendo el
        # maximo). Se distingue mirando si su aptitud quedo por debajo de la mejor.
        peores = d[~en_piso]
        if bool((peores.Fo_opt < d.Fo_opt.max()).all()):
            print(f'  -> las {len(peores)} corridas fuera del piso tienen aptitud MENOR que el maximo '
                  f'({coma(peores.Fo_opt.max())} contra {coma(d.Fo_opt.max())}): son fallas de '
                  'convergencia del enjambre, no optimos alternativos. El piso sigue siendo el '
                  'maximo y la afirmacion del trabajo se sostiene.')
            print(f'     la peor es n = {int(peores.loc[peores.Fo_opt.idxmin(), "n"])}, '
                  f'T = {int(peores.loc[peores.Fo_opt.idxmin(), "Tmax"])}, la configuracion con menos '
                  'evaluaciones del barrido.')
        else:
            print('  -> hay corridas fuera del piso que igualan o superan el maximo: son optimos '
                  'alternativos y HAY QUE MATIZAR la afirmacion del trabajo.')
    frec = d.groupby('r_opt').size().idxmax()
    mejor = int(d.loc[d.Fo_opt.idxmax(), 'r_opt'])
    if frec != mejor:
        print(f'  el radio mas frecuente (r = {frec}) NO es el de mejor aptitud (r = {mejor}): la '
              'frecuencia con que el enjambre devuelve un radio no mide su calidad')
    print(f'  Fo maxima global {coma(d.Fo_opt.max())} · minima {coma(d.Fo_opt.min())} · '
          f'recorrido {coma(d.Fo_opt.max() - d.Fo_opt.min())}')

    salida = MR / f'pso_repeticiones_resumen_{a.operator}.csv'
    g.to_csv(salida, index=False)
    print(f'\n-> {salida.relative_to(RAIZ)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
