# -*- coding: utf-8 -*-
"""Verifica el libro en LaTeX: citas, referencias cruzadas y archivos.

POR QUE. Un documento sin chequeo se separa de los datos. Este script revisa lo que mas se rompe al
editar el libro.

QUE REVISA; del 1 al 4, si algo falla, termina con codigo 1:
  1. cada \\cite del texto tiene su entrada en referencias.bib;
  2. cada \\ref apunta a una \\label que existe;
  3. cada \\include nombra un archivo que existe;
  4. cada \\includegraphics apunta a una imagen que existe.

No compila el documento: para eso hace falta una distribucion de LaTeX. Esto revisa lo que se puede
revisar sin compilar, que es casi todo lo que se rompe en la practica.

Uso:  .venv\\Scripts\\python.exe -X utf8 tools/verificar_libro_v4.py
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
LIBRO = RAIZ / 'docs' / 'libro_v4'
BIB = LIBRO / 'referencias.bib'

fallos, avisos = [], []


def ok(cond, msg):
    print(f'  {"OK   " if cond else "FALLA"} {msg}')
    if not cond:
        fallos.append(msg)


def texto_de(p):
    return p.read_text(encoding='utf-8', errors='replace')


def sin_comentarios(t):
    return re.sub(r'(?<!\\)%.*', '', t)


def main():
    if not LIBRO.exists():
        print(f'  no existe {LIBRO.relative_to(RAIZ)}')
        return 1
    texs = sorted(LIBRO.rglob('*.tex'))
    print(f'=== libro_v4: {len(texs)} archivos .tex\n')

    todo = {p: sin_comentarios(texto_de(p)) for p in texs}
    junto = '\n'.join(todo.values())

    # ---------------------------------------------------------------- 1. citas
    claves = set(re.findall(r'@\w+\s*\{\s*([^,\s]+)\s*,', texto_de(BIB))) if BIB.exists() else set()
    citas = set()
    for m in re.finditer(r'\\[a-zA-Z]*cite[a-zA-Z]*\s*(?:\[[^\]]*\])*\s*\{([^}]*)\}', junto):
        citas |= {c.strip() for c in m.group(1).split(',') if c.strip()}
    huerfanas = sorted(citas - claves)
    ok(not huerfanas, f'las {len(citas)} citas del texto tienen entrada en referencias.bib'
                      + (f' — SIN ENTRADA: {huerfanas}' if huerfanas else ''))
    sin_citar = sorted(claves - citas)
    if sin_citar:
        print(f'  --    {len(sin_citar)} entradas del .bib todavia sin citar: {sin_citar[:8]}')
        avisos.append(f'{len(sin_citar)} referencias sin citar')

    # ---------------------------------------------------------------- 2. referencias cruzadas
    labels = set(re.findall(r'\\label\{([^}]+)\}', junto))
    refs = set(re.findall(r'\\(?:page)?ref\{([^}]+)\}', junto))
    rotas = sorted(refs - labels)
    ok(not rotas, f'las {len(refs)} referencias cruzadas apuntan a una etiqueta que existe'
                  + (f' — ROTAS: {rotas}' if rotas else ''))

    # ---------------------------------------------------------------- 3. includes
    faltan = []
    for m in re.finditer(r'\\(?:include|input)\{([^}]+)\}', junto):
        rel = m.group(1)
        if not (LIBRO / (rel + '.tex')).exists() and not (LIBRO / rel).exists():
            faltan.append(rel)
    ok(not faltan, 'cada \\include nombra un archivo que existe'
                   + (f' — FALTAN: {faltan}' if faltan else ''))

    # ---------------------------------------------------------------- 4. imagenes
    img_faltan = []
    for m in re.finditer(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', junto):
        rel = m.group(1)
        if not any((LIBRO / (rel + ext)).exists() or (LIBRO / rel).exists()
                   for ext in ('', '.png', '.pdf', '.jpg')):
            img_faltan.append(rel)
    ok(not img_faltan, 'cada figura apunta a un archivo que existe'
                       + (f' — FALTAN: {img_faltan}' if img_faltan else ''))

    print(f'\n=== {len(fallos)} fallos · {len(avisos)} avisos ===')
    for f in fallos:
        print(f'  FALLA {f}')
    for a in avisos:
        print(f'  AVISO {a}')
    return 1 if fallos else 0


if __name__ == '__main__':
    sys.exit(main())
