# -*- coding: utf-8 -*-
"""Comprueba que el corpus de imagenes en data/raw sea el del manifiesto.

POR QUE EXISTE. Las imagenes del TNO no se versionan: pesan y tienen su propia licencia, asi que
data/raw esta en .gitignore y lo unico que viaja en el repo es data/raw/MANIFIESTO_CORPUS.csv, con
el md5 y la ruta de origen exacta de cada archivo. Eso hace el corpus reconstruible... pero hasta
ahora ningun script lo leia, de modo que quien clonaba el repo no tenia forma de saber si habia
armado bien data/raw hasta que un experimento fallaba raro.

Y no es hipotetico: en este proyecto UN PAR VINO CORRUPTO. El canal visible de
Athena_heather_IR_hei_vis era una copia byte a byte del infrarrojo, con lo que cualquier metrica de
fidelidad daba 1 y el PSNR se iba al infinito. Se detecto comparando md5 entre canales. Este script
hace esa comprobacion sola, en un segundo, antes de que nadie corra nada.

QUE COMPRUEBA
  1. que existan los archivos que el manifiesto declara, en data/raw/VIS y data/raw/IR;
  2. que el md5 de cada uno coincida;
  3. que no haya archivos de mas que el manifiesto no declare;
  4. que ningun par tenga el VIS identico al IR (el defecto que ya aparecio una vez);
  5. que list_pairs() devuelva exactamente los pares no excluidos.

Codigo de salida 0 si el corpus esta completo y sano, 1 si no. Sirve como puerta antes de correr
los experimentos.

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/verificar_corpus.py
"""
import hashlib
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))

import pandas as pd

MANIF = RAIZ / 'data' / 'raw' / 'MANIFIESTO_CORPUS.csv'
CRUDO = RAIZ / 'data' / 'raw'
fallos = []


def ok(cond, msg):
    print(f'  {"OK   " if cond else "FALLA"} {msg}')
    if not cond:
        fallos.append(msg)
    return bool(cond)


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


def main():
    if not MANIF.exists():
        print(f'no esta {MANIF.relative_to(RAIZ)}: el repo esta incompleto')
        return 1
    m = pd.read_csv(MANIF)
    print(f'manifiesto: {len(m)} archivos declarados, '
          f'{m.par.nunique()} pares, {int((m.excluido == "si").sum() / 2)} excluido(s)\n')

    print('--- 1. los archivos declarados estan, y con el md5 correcto')
    faltan, distinto = [], []
    for r in m.itertuples():
        p = CRUDO / r.modalidad / r.archivo
        if not p.exists():
            faltan.append(f'{r.modalidad}/{r.archivo}')
        elif md5(p) != r.md5:
            distinto.append(f'{r.modalidad}/{r.archivo}')
    if faltan:
        print(f'        faltan {len(faltan)} de {len(m)}. Primeros: {faltan[:4]}')
        print('        Para armar el corpus, ver la seccion 5 del README: cada fila del manifiesto')
        print('        trae en «origen_tno» la ruta exacta dentro del TNO original.')
    ok(not faltan, f'estan los {len(m)} archivos del manifiesto')
    ok(not distinto, 'todos los md5 coinciden' + (f' — difieren {distinto[:4]}' if distinto else ''))

    print('\n--- 2. no hay archivos de mas')
    declar = {(r.modalidad, r.archivo) for r in m.itertuples()}
    en_disco = {(d, p.name) for d in ('VIS', 'IR') if (CRUDO / d).is_dir()
                for p in (CRUDO / d).iterdir() if p.is_file()}
    sobran = sorted(f'{d}/{n}' for d, n in en_disco - declar)
    ok(not sobran, 'ningun archivo sin declarar en el manifiesto'
                   + (f' — sobran {sobran[:4]}' if sobran else ''))

    print('\n--- 3. ningun par tiene el visible identico al infrarrojo')
    # El defecto que ya aparecio: si los dos canales son el mismo archivo, toda metrica de fidelidad
    # da su valor perfecto y el par infla los promedios sin que nada mas lo delate.
    iguales = []
    for par, g in m.groupby('par'):
        h = {r.modalidad: r.md5 for r in g.itertuples()}
        if h.get('VIS') and h.get('VIS') == h.get('IR'):
            iguales.append((par, str(g.excluido.iloc[0])))
    no_excl = [p for p, e in iguales if e != 'si']
    if iguales:
        print(f'        pares con los dos canales identicos: {[p for p, _ in iguales]}')
        print(f'        (declarados como excluidos en el manifiesto: '
              f'{[p for p, e in iguales if e == "si"]})')
    ok(not no_excl, 'ningun par NO excluido tiene los dos canales iguales'
                    + (f' — {no_excl}' if no_excl else ''))

    print('\n--- 4. list_pairs() devuelve el corpus efectivo')
    try:
        from src.datasets import list_pairs
        vivos = {Path(str(v)).stem for v, _i in list_pairs()}
        esperados = {r.par for r in m.itertuples() if r.excluido != 'si'}
        ok(vivos == esperados,
           f'list_pairs() devuelve los {len(esperados)} pares no excluidos'
           + (f' — faltan {sorted(esperados - vivos)[:3]}, '
              f'sobran {sorted(vivos - esperados)[:3]}' if vivos != esperados else ''))
    except ImportError as e:
        ok(False, f'no se pudo importar list_pairs ({e}): correr pip install -r requirements.txt')
    except Exception as e:
        ok(False, f'list_pairs() fallo: {type(e).__name__}: {e}')

    print(f'\n=== {len(fallos)} fallos ===')
    for f in fallos:
        print(f'  FALLA {f}')
    if not fallos:
        print('  el corpus esta completo y sano: se puede correr todo lo demas')
    return 1 if fallos else 0


if __name__ == '__main__':
    sys.exit(main())
