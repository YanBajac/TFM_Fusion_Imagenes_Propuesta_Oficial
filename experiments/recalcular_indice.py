# -*- coding: utf-8 -*-
"""Recalcula los números de página del índice del libro contra el PDF compilado.

Motivo: el índice del docx es TEXTO FIJO, no un campo de Word, de modo que cualquier
párrafo que cambie de largo mueve un salto de página y lo desfasa en silencio. Ya pasó
cuatro veces en el proyecto. Corregirlo a mano es mecánico y se olvida; esto lo hace.

Cómo: cada entrada del índice es un párrafo de la forma «Título<TAB>NN». Para cada una se
busca la primera página del cuerpo —excluidas las del propio índice— cuyo texto contenga
el título, y se reescribe el número si no coincide.

El orden correcto de trabajo es: editar el docx, compilar el PDF, correr este script,
volver a compilar el PDF y correr verificar_libro.py. Hacen falta las dos compilaciones
porque la primera revela la paginación real y la segunda incorpora el índice corregido;
cambiar «63» por «64» no altera el flujo del texto, así que dos pasadas alcanzan siempre.

Uso:   .venv\\Scripts\\python.exe -X utf8 experiments/recalcular_indice.py [--simular]
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

import docx
import fitz

RAIZ = Path(__file__).resolve().parent.parent
DOCX = RAIZ / 'docs' / 'Tesis_Borrador_V3.docx'
PDF = RAIZ / 'docs' / 'Tesis_Borrador_V3.pdf'
ENTRADA = re.compile(r'^(.*?)\t(\d{1,3})$')
GUIA = re.compile(r'\.{3,}\s*\d{1,3}\s*$', re.M)


def plano(s):
    return re.sub(r'\s+', ' ', s).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--simular', action='store_true', help='informa sin escribir')
    args = ap.parse_args()

    if not PDF.exists():
        print(f'falta {PDF.name}: compilar el PDF antes de recalcular')
        return 1

    with fitz.open(str(PDF)) as doc:
        paginas = [pg.get_text() for pg in doc]
    # las páginas del propio índice no cuentan como cuerpo
    del_indice = {i for i, t in enumerate(paginas) if len(GUIA.findall(t)) >= 3}
    cuerpo = [(i, plano(t)) for i, t in enumerate(paginas) if i not in del_indice]
    print(f'{len(paginas)} páginas · índice en {[i + 1 for i in sorted(del_indice)]}')

    libro = docx.Document(str(DOCX))
    corregidas, sin_hallar, iguales = [], [], 0
    for i, p in enumerate(libro.paragraphs):
        m = ENTRADA.match(p.text)
        if not m or len(p.runs) < 1:
            continue
        titulo, dice = plano(m.group(1)), int(m.group(2))
        real = next((k for k, t in cuerpo if titulo and titulo in t), None)
        if real is None:
            sin_hallar.append(titulo)
            continue
        real += 1
        if real == dice:
            iguales += 1
            continue
        # el número vive al final del texto del párrafo; se reescribe el run que lo contiene
        for r in reversed(p.runs):
            if r.text.rstrip().endswith(str(dice)):
                r.text = r.text.rstrip()[:-len(str(dice))] + str(real)
                break
        else:
            sin_hallar.append(f'{titulo} (no se pudo ubicar el número en los runs)')
            continue
        corregidas.append((titulo, dice, real))

    for titulo, dice, real in corregidas:
        print(f'  {titulo[:58]:60s} {dice:3d} -> {real:3d}')
    for titulo in sin_hallar:
        print(f'  SIN HALLAR  {titulo[:70]}')

    if corregidas and not args.simular:
        shutil.copy2(DOCX, DOCX.with_suffix('.docx.bak_indice'))
        libro.save(str(DOCX))
        print(f'\n{len(corregidas)} entradas corregidas · {iguales} ya estaban bien')
        print('AHORA: recompilar el PDF y correr verificar_libro.py')
    elif corregidas:
        print(f'\n{len(corregidas)} entradas a corregir (simulación, no se escribió)')
    else:
        print(f'\nel índice ya está al día: las {iguales} entradas apuntan a su página real')
    return 1 if sin_hallar else 0


if __name__ == '__main__':
    sys.exit(main())
