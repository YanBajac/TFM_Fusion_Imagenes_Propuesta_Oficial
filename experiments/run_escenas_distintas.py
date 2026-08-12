# -*- coding: utf-8 -*-
"""Cuenta cuantas ESCENAS FISICAS distintas hay en los 20 pares, con el criterio escrito y verificable.

POR QUE EXISTE. El libro afirma que los 20 pares corresponden a «trece escenas distintas», y un
chequeo de verificar_libro.py exige esa frase. Pero NINGUN script del repositorio calculaba el numero:
vivia como afirmacion en la prosa y como literal en un chequeo, que es la peor combinacion posible
—un control que bloquea una cifra que nadie puede rehacer—. Agrupando los nombres a ojo salen 13 o 14
segun como se cuenten las dos tomas de soldier_in_trench, de modo que hacia falta fijar el criterio.

EL CRITERIO, sobre la ruta de origen del TNO que el manifiesto guarda en «origen_tno». No se agrupa
por el nombre del par, que es una construccion de este proyecto, sino por la estructura de carpetas
del dataset original, que es la que declara que es una escena:

  1. Si la carpeta es «X/view_N», la escena es X, y X queda marcada como CARPETA CON VISTAS. El TNO
     usa subcarpetas «view_N» para varias vistas de una misma escena: APC_1 tiene tres, APC_3 tiene
     tres. Una carpeta con vistas es una escena por si misma y no se agrupa con nadie mas.
  2. Las demas carpetas son HOJAS: contienen las imagenes directamente. Dos o mas hojas hermanas
     cuyos nombres solo difieran en un sufijo «_N» final son tomas de la misma escena y colapsan en
     el nombre comun. Asi soldier_behind_smoke_1/2/3 son una escena y soldier_in_trench_1/2 son otra.
  3. La distincion del punto 1 es la que salva a APC_4, y es un hecho del dataset, no una excepcion
     escrita a mano: su sufijo _4 es parte del nombre del vehiculo, no un numero de toma. APC_4 es
     una hoja, y sus unicas candidatas a hermanas —APC_1 y APC_3— NO son hojas, porque contienen
     vistas. La primera version de este script no distinguia hojas de carpetas con vistas y colapso
     APC_1, APC_3 y APC_4 en una sola «escena APC», dando 11 en lugar de 13.

QUE SE HACE CON EL RESULTADO. El numero se comprueba contra el 13 que publica el libro. Si algun dia
cambia el corpus y deja de ser 13, este script falla y hay que corregir la prosa: la cifra deja de
poder envejecer en silencio.

Salida: experiments/results/metrics_reports/escenas_distintas.csv
Uso:    .venv\\Scripts\\python.exe -X utf8 experiments/run_escenas_distintas.py
"""
import os
import re
import sys
from collections import defaultdict
from pathlib import Path, PurePosixPath

RAIZ = Path(__file__).resolve().parent.parent
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))

import pandas as pd

from src.datasets import list_pairs

MANIF = RAIZ / 'data' / 'raw' / 'MANIFIESTO_CORPUS.csv'
SALIDA = RAIZ / 'experiments' / 'results' / 'metrics_reports' / 'escenas_distintas.csv'
ESPERADAS = 13                      # lo que publica el libro
fallos = []


def ok(cond, msg):
    print(f'  {"OK   " if cond else "FALLA"} {msg}')
    if not cond:
        fallos.append(msg)


def main():
    m = pd.read_csv(MANIF)
    vivos = {Path(str(v)).stem for v, _i in list_pairs()}
    filas = m[(m.modalidad == 'VIS') & (m.par.isin(vivos))]
    ok(len(filas) == len(vivos), f'{len(filas)} filas VIS para los {len(vivos)} pares vivos')

    carpeta = {r.par: str(PurePosixPath(r.origen_tno).parent) for r in filas.itertuples()}

    # regla 1: «X/view_N» -> X, y X queda marcada como carpeta CON VISTAS
    con_vistas = {re.sub(r'/view_\d+$', '', c) for c in carpeta.values()
                  if re.search(r'/view_\d+$', c)}
    nivel1 = {p: re.sub(r'/view_\d+$', '', c) for p, c in carpeta.items()}
    print(f'  carpetas con subcarpetas «view_N»: {sorted(con_vistas)}')

    # regla 2: solo entre HOJAS —las que no tienen vistas— se agrupan las hermanas que difieren en
    # un sufijo «_N» final. Una carpeta con vistas ya es una escena y no entra en este reparto.
    candidatas = defaultdict(set)                 # (padre, stem sin _N) -> {hojas hermanas}
    for c in set(nivel1.values()):
        if c in con_vistas:
            continue
        pp = PurePosixPath(c)
        stem = re.sub(r'_\d+$', '', pp.name)
        if stem != pp.name:                       # la hoja termina en _N
            candidatas[(str(pp.parent), stem)].add(c)
    colapsa = {}
    for (padre, stem), hermanas in candidatas.items():
        if len(hermanas) >= 2:                    # hace falta hermandad real entre hojas
            for h in hermanas:
                colapsa[h] = f'{padre}/{stem}'
        else:
            print(f'  «{sorted(hermanas)[0]}» termina en _N pero no tiene hoja hermana: '
                  f'queda sola')
    escena = {p: colapsa.get(c, c) for p, c in nivel1.items()}

    grupos = defaultdict(list)
    for p, e in escena.items():
        grupos[e].append(p)

    print(f'\n--- {len(grupos)} escenas distintas en {len(vivos)} pares')
    for e in sorted(grupos, key=lambda x: (-len(grupos[x]), x)):
        pares = sorted(grupos[e])
        print(f'  {len(pares)}  {e}')
        if len(pares) > 1:
            for p in pares:
                print(f'         {p}   (carpeta {carpeta[p]})')

    print('\n--- por que APC_4 no colapsa con APC_1 ni APC_3')
    for p in sorted(vivos):
        if 'APC' in p:
            print(f'  {p:32} carpeta {carpeta[p]:28} -> escena {escena[p]}')

    print('\n--- controles')
    ok(len(grupos) == ESPERADAS,
       f'las escenas distintas son {ESPERADAS}, como publica el libro (dan {len(grupos)})')
    ok(sum(len(v) for v in grupos.values()) == len(vivos),
       'cada par cae en exactamente una escena')
    apc = {escena[p] for p in vivos if p.startswith('Athena_APC_4')}
    otros_apc = {escena[p] for p in vivos if 'APC_1' in p or 'APC_3' in p}
    ok(apc.isdisjoint(otros_apc), f'APC_4 queda en su propia escena ({apc}) y no se mezcla con '
                                  f'APC_1 ni APC_3 ({otros_apc})')
    series = {e: len(v) for e, v in grupos.items() if len(v) > 1}
    ok(max(series.values()) == 3,
       f'la serie mas larga tiene tres tomas (las series son {series})')

    res = pd.DataFrame([{'par': p, 'carpeta_tno': carpeta[p], 'escena': escena[p],
                         'pares_en_la_escena': len(grupos[escena[p]])}
                        for p in sorted(vivos)])
    res.to_csv(SALIDA, index=False)
    print(f'\nescrito: {SALIDA.relative_to(RAIZ)}  ({len(res)} pares, {len(grupos)} escenas)')
    print(f'\n=== {len(fallos)} fallos ===')
    return 1 if fallos else 0


if __name__ == '__main__':
    sys.exit(main())
