# -*- coding: utf-8 -*-
"""Tría los hallazgos de la reverificación en tres montones, sin criterio humano.

Motivo: la reverificación devolvió 106 hallazgos y aplicarlos a ciegas no es opción
—los agentes ya erraron cifras en esta misma sesión—, pero leerlos de a uno tampoco
escala. Este script hace la parte mecánica:

  YA_APLICADO   el texto que el hallazgo señala ya no está en el documento.
  PENDIENTE     el texto sigue ahí y las cifras del reemplazo se confirman en los CSV.
  A_LEER        no se pudo decidir por máquina: exige leer el documento.

No corrige nada. Su salida es la lista de trabajo, ordenada por gravedad.

Uso:   .venv\Scripts\python.exe -X utf8 experiments/triar_hallazgos.py [--gravedad falso] [--doc libro]
Salida: docs/fuentes/triage.json y un resumen por consola.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

import fitz
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
REP = RAIZ / 'experiments' / 'results' / 'metrics_reports'
DOCS = RAIZ / 'docs'
HALL = DOCS / 'fuentes' / 'reverificacion_hallazgos.json'


def plano(s):
    return re.sub(r'\s+', ' ', s or '')


def sin_tildes(s):
    s = unicodedata.normalize('NFKD', s or '')
    return ''.join(c for c in s if not unicodedata.combining(c))


# ------------------------------------------------------------- documentos
def texto_pdf(p):
    with fitz.open(str(p)) as d:
        return plano('\n'.join(pg.get_text() for pg in d))


DOCUMENTOS = {}
for clave, ruta in (('libro', DOCS / 'Tesis_Borrador_V3.pdf'),
                    ('deck', DOCS / 'Tesis_Defensa_Presentacion.pdf'),
                    ('avances', DOCS / 'Avances_Tesis.pdf')):
    if ruta.exists():
        DOCUMENTOS[clave] = texto_pdf(ruta)
if (RAIZ / 'README.md').exists():
    DOCUMENTOS['readme'] = plano((RAIZ / 'README.md').read_text(encoding='utf-8'))
# el codigo, para los hallazgos de la dimension «codigo»
CODIGO = plano('\n'.join(
    p.read_text(encoding='utf-8', errors='ignore')
    for p in list((RAIZ / 'src').rglob('*.py')) + list((RAIZ / 'experiments').glob('*.py'))))


def doc_de(donde):
    """Adivina a que documento apunta el campo «donde» del hallazgo."""
    d = sin_tildes(donde).lower()
    if 'readme' in d:
        return 'readme'
    if 'presentacion' in d or 'lamina' in d or 'deck' in d:
        return 'deck'
    if 'avances' in d:
        return 'avances'
    if 'borrador' in d or 'libro' in d or re.search(r'§|seccion|apendice|tabla|p\.\s*\d', d):
        return 'libro'
    return None


# ------------------------------------------------- universo de cifras de los CSV
CIFRAS = set()
for csv in REP.glob('*.csv'):
    try:
        d = pd.read_csv(csv)
    except Exception:                                              # noqa: BLE001
        continue
    for col in d.select_dtypes('number').columns:
        for v in d[col].dropna().unique():
            for nd in (2, 3, 4):
                CIFRAS.add(f'{float(v):.{nd}f}')
                CIFRAS.add(f'{float(v):.{nd}f}'.replace('.', ','))
            if float(v) == int(float(v)):
                CIFRAS.add(str(int(float(v))))


def numeros(s):
    """Cifras con dos o mas decimales que aparecen en el texto."""
    return set(re.findall(r'\d+[.,]\d{2,4}', s or ''))


def fragmentos(dice):
    """TODOS los fragmentos citados del hallazgo, no solo el mas largo.

    Un hallazgo suele citar dos o tres pasajes («§5.3: «...» y §6.1: «...»»). Tomar
    solo uno hacia que un pasaje ya corregido pareciera pendiente porque otro
    sobrevivia, o al revez. Se evaluan todos y el veredicto sale de la combinacion.
    """
    m = re.findall(r'[«"]([^»"]{25,200})[»"]', dice or '')
    cands = m or ([dice] if dice else [])
    out = []
    for c in cands:
        c = plano(c).strip(' .;:…')
        # los fragmentos con elipsis no se pueden buscar literales: se parte en trozos
        for trozo in re.split(r'\s*[…]+\s*|\s*\.\.\.\s*', c):
            trozo = trozo.strip(' .;:')
            if len(trozo) >= 25:
                out.append(trozo)
    return out


ap = argparse.ArgumentParser()
ap.add_argument('--gravedad')
ap.add_argument('--doc')
a = ap.parse_args()

hall = json.loads(HALL.read_text(encoding='utf-8'))
salida = []
for i, h in enumerate(hall, 1):
    dim = h.get('dimension', '?')
    doc = doc_de(h.get('donde', '')) or ('codigo' if dim == 'codigo' else None)
    texto = CODIGO if doc == 'codigo' else DOCUMENTOS.get(doc)
    frs = fragmentos(h.get('dice', ''))
    reg = {'n': i, 'dimension': dim, 'gravedad': h.get('gravedad'),
           'doc': doc, 'donde': h.get('donde', '')[:110],
           'dice': plano(h.get('dice', ''))[:180],
           'corresponde': plano(h.get('corresponde', ''))[:180]}
    if texto is None or not frs:
        reg['estado'] = 'A_LEER'
        reg['motivo'] = 'no se pudo ubicar el documento o la cita'
        salida.append(reg)
        continue
    viven = [f for f in frs if f in texto]
    reg['fragmentos'] = len(frs)
    reg['fragmentos_vivos'] = len(viven)
    if not viven:
        reg['estado'] = 'YA_APLICADO'
        reg['motivo'] = f'ninguno de los {len(frs)} pasajes citados sigue en el documento'
    elif len(viven) < len(frs):
        reg['estado'] = 'A_LEER'
        reg['motivo'] = (f'{len(viven)} de {len(frs)} pasajes siguen presentes: el '
                         'hallazgo esta a medio aplicar')
        reg['vivos'] = [f[:90] for f in viven]
    else:
        prop = numeros(h.get('corresponde', '')) | numeros(h.get('reemplazo', ''))
        confirm = {x for x in prop if x in CIFRAS or x.replace(',', '.') in CIFRAS}
        if prop and confirm:
            reg['estado'] = 'PENDIENTE'
            reg['motivo'] = (f'los {len(frs)} pasajes siguen presentes y {len(confirm)} '
                             f'de {len(prop)} cifras del reemplazo estan en los CSV')
            reg['cifras_confirmadas'] = sorted(confirm)[:6]
        else:
            reg['estado'] = 'A_LEER'
            reg['motivo'] = ('los pasajes siguen presentes pero el reemplazo no trae '
                             'cifras verificables: es de redaccion o de encuadre')
    salida.append(reg)

if a.gravedad:
    salida = [r for r in salida if r['gravedad'] == a.gravedad]
if a.doc:
    salida = [r for r in salida if r['doc'] == a.doc]

(DOCS / 'fuentes' / 'triage.json').write_text(
    json.dumps(salida, ensure_ascii=False, indent=1), encoding='utf-8')

from collections import Counter
print(f'{len(salida)} hallazgos triados\n')
print('=== por estado ===')
for k, v in Counter(r['estado'] for r in salida).most_common():
    print(f'  {k:12} {v}')
print('\n=== PENDIENTE, por documento y gravedad ===')
pend = [r for r in salida if r['estado'] == 'PENDIENTE']
for k, v in Counter((r['doc'], r['gravedad']) for r in pend).most_common():
    print(f'  {str(k):34} {v}')
print('\n=== A_LEER, por documento ===')
for k, v in Counter(r['doc'] for r in salida if r['estado'] == 'A_LEER').most_common():
    print(f'  {str(k):12} {v}')
ORD = {'falso': 0, 'incoherente': 1, 'desactualizado': 2, 'sobreafirmado': 3, 'menor': 4}
print(f'\n=== los {min(12, len(pend))} PENDIENTE mas graves ===')
for r in sorted(pend, key=lambda x: ORD.get(x['gravedad'], 9))[:12]:
    print(f"\n[{r['n']}] {r['gravedad']} · {r['doc']} · {r['donde'][:78]}")
    print(f"    dice: {r['dice'][:120]}")
    print(f"    debe: {r['corresponde'][:120]}")
    print(f"    cifras confirmadas: {r.get('cifras_confirmadas')}")
print(f'\ndetalle completo en docs/fuentes/triage.json')
