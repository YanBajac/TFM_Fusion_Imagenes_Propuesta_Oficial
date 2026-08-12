# -*- coding: utf-8 -*-
"""Aplica al propio benchmark la primera recomendacion del trabajo: agregar una metrica de artefactos.

POR QUE EXISTE. El segundo aporte de la tesis recomienda que un protocolo de evaluacion de fusion
incluya al menos una metrica de direccion inversa que penalice artefactos. El trabajo aplica esa
recomendacion AL CONTROL NEGATIVO —la Tabla 7 bis del libro trae la columna «Con 9 + Nabf» para las
catorce entradas degradadas— pero NO al benchmark de los siete metodos, que se sigue ordenando solo
con las nueve. Queda una distancia entre lo que el trabajo recomienda y lo que el trabajo hace con su
propio resultado, y es justo la clase de cosa que un tribunal pregunta.

Este script cierra esa distancia sin tocar el criterio primario. El orden con las NUEVE se conserva
como es: es la replica del trabajo de referencia y es lo que hace comparable el resultado. Lo que se
agrega es una agregacion mas, declarada, con Nabf sumada a las nueve, para poder decir que pasa con la
propuesta cuando se le aplica su propia recomendacion.

Nabf es «menor es mejor» —cuenta artefactos introducidos por la fusion— y es la unica metrica de
direccion inversa entre las diecisiete que el evaluador calcula. La direccion no se fija a mano: sale
de src/metrics/evaluators.py, igual que en el resto del proyecto.

Salida: experiments/results/metrics_reports/ranking_mas_nabf.csv
Uso:    .venv\\Scripts\\python.exe -X utf8 experiments/run_ranking_mas_nabf.py
"""
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))

import pandas as pd

from src.metrics.evaluators import METRIC_DIRECTION as DIR

MR = RAIZ / 'experiments' / 'results' / 'metrics_reports'
SALIDA = MR / 'ranking_mas_nabf.csv'
PROP = 'Propuesta_Novedosa'
NUEVE = ['EN', 'SD', 'FE', 'MG', 'MI_vis', 'MI_ir', 'SF', 'SSIM', 'PSNR']
fallos = []


def ok(cond, msg):
    print(f'  {"OK   " if cond else "FALLA"} {msg}')
    if not cond:
        fallos.append(msg)


def rango_medio(allm, metricas):
    """Rango medio por metodo: se rankea DENTRO de cada imagen y se promedia entre imagenes.

    Es el procedimiento del informe y del libro —el complemento habitual de Friedman—, no rankear
    los promedios, que ignora la variabilidad entre escenas.
    """
    por_metrica = {}
    for m in metricas:
        piv = allm.pivot(index='image', columns='method', values=m)
        por_metrica[m] = piv.rank(axis=1, ascending=(DIR[m] == 'min'),
                                 method='average').mean(axis=0)
    return pd.DataFrame(por_metrica).mean(axis=1)


def main():
    allm = pd.read_csv(MR / 'all_metrics.csv')
    ok('Nabf' in allm.columns, 'all_metrics.csv trae la columna Nabf')
    ok(DIR.get('Nabf') == 'min', f'Nabf esta declarada «menor es mejor» (dice {DIR.get("Nabf")!r})')
    inversas = [m for m, d in DIR.items() if d == 'min' and m in allm.columns]
    ok(inversas == ['Nabf'], f'Nabf es la unica metrica de direccion inversa del estudio '
                             f'(las inversas son {inversas})')

    r9 = rango_medio(allm, NUEVE)
    r10 = rango_medio(allm, NUEVE + ['Nabf'])
    med_nabf = allm.groupby('method')['Nabf'].mean()

    res = pd.DataFrame({
        'rango_9': r9.round(3),
        'rango_9_mas_Nabf': r10.round(3),
        'Nabf_medio': med_nabf.round(4),
    })
    res['puesto_9'] = res.rango_9.rank(method='min').astype(int)
    res['puesto_9_mas_Nabf'] = res.rango_9_mas_Nabf.rank(method='min').astype(int)
    res['cambio_de_puesto'] = res.puesto_9_mas_Nabf - res.puesto_9
    res = res.sort_values('rango_9')

    print('\n--- el benchmark de siete, con las nueve y con las nueve mas Nabf')
    print(res.to_string())

    p9 = int(res.loc[PROP, 'puesto_9'])
    p10 = int(res.loc[PROP, 'puesto_9_mas_Nabf'])
    lider10 = res.rango_9_mas_Nabf.idxmin()
    print(f'\n  la propuesta pasa del puesto {p9} al {p10} de {len(res)}')
    print(f'  con Nabf lidera {lider10} ({res.loc[lider10, "rango_9_mas_Nabf"]:.3f})')
    print(f'  Nabf medio: propuesta {res.loc[PROP, "Nabf_medio"]:.4f} · '
          f'mejor {med_nabf.idxmin()} {med_nabf.min():.4f} · '
          f'peor {med_nabf.idxmax()} {med_nabf.max():.4f}')

    print('\n--- controles')
    # 1. el rango con las nueve tiene que coincidir con el que ya publica el proyecto
    pub = (pd.read_csv(MR / 'ranking_methods.csv')
           .rename(columns={'Unnamed: 0': 'metodo'}).set_index('metodo')['avg_rank'])
    dif = {k: (float(pub[k]), float(res.loc[k, 'rango_9']))
           for k in pub.index if abs(float(pub[k]) - float(res.loc[k, 'rango_9'])) > 0.0015}
    ok(not dif, 'el rango con las nueve reproduce ranking_methods.csv'
                + (f' — difiere en {dif}' if dif else ''))
    # 2. agregar una metrica de siete metodos no puede mover ningun rango medio mas de 0,5
    salto = res[(res.rango_9_mas_Nabf - res.rango_9).abs() > 0.5]
    ok(salto.empty, 'ningun rango medio se mueve mas de 0,5 al sumar una decima metrica'
                    + ('' if salto.empty else f' — {salto.index.tolist()}'))
    # 3. y el orden de Nabf tiene que ser el que ya publica la ablacion para los dos brazos comunes
    abl = pd.read_csv(MR / 'ablacion_banco_resumen.csv').set_index('brazo')
    ok(abs(float(abl.loc['suma', 'Nabf']) - float(res.loc[PROP, 'Nabf_medio'])) < 0.0005,
       f'el Nabf de la propuesta coincide con el brazo «suma» de la ablacion '
       f'({abl.loc["suma", "Nabf"]:.4f})')

    res.to_csv(SALIDA)
    print(f'\nescrito: {SALIDA.relative_to(RAIZ)}')
    print(f'\n=== {len(fallos)} fallos ===')
    return 1 if fallos else 0


if __name__ == '__main__':
    sys.exit(main())
