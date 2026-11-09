# -*- coding: utf-8 -*-
"""Arma el .zip de docs/libro_v4 listo para subir a Overleaf, y revisa lo que suele fallar al compilar.

POR QUE UN SCRIPT. Overleaf compila en su servidor, asi que un error de preambulo se descubre alla y no
aca. Antes de empaquetar, esto revisa las cosas que se pueden comprobar sin compilar: que los paquetes
del preambulo existan en la distribucion que usa Overleaf, que no haya opciones de clase invalidas, que
todos los archivos incluidos esten dentro del zip y que las imagenes referenciadas viajen con el.

Uso:  .venv\\Scripts\\python.exe -X utf8 tools/empaquetar_overleaf.py
"""
import re
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
LIBRO = RAIZ / 'docs' / 'libro_v4'
SALIDA = RAIZ / 'docs' / 'libro_v4_overleaf.zip'

# Paquetes que trae TeX Live completo, que es lo que usa Overleaf. Si se agrega uno que no este aca,
# conviene comprobarlo antes de subir: un paquete faltante frena la compilacion entera.
CONOCIDOS = {
    'inputenc', 'fontenc', 'babel', 'lmodern', 'helvet', 'geometry', 'setspace', 'fancyhdr', 'titlesec',
    'graphicx', 'booktabs', 'caption', 'placeins', 'amsmath', 'amssymb', 'biblatex', 'hyperref',
    'float', 'subcaption', 'multirow', 'longtable', 'array', 'siunitx', 'csquotes', 'microtype',
}

fallos = []


def ok(cond, msg):
    print(f'  {"OK   " if cond else "FALLA"} {msg}')
    if not cond:
        fallos.append(msg)


def main():
    if not LIBRO.exists():
        print('  no existe docs/libro_v4')
        return 1
    main_tex = (LIBRO / 'main.tex').read_text(encoding='utf-8')
    sin_com = re.sub(r'(?<!\\)%.*', '', main_tex)

    # --- clase y opciones
    m = re.search(r'\\documentclass(?:\[([^\]]*)\])?\{(\w+)\}', sin_com)
    clase, opciones = m.group(2), [o.strip() for o in (m.group(1) or '').split(',') if o.strip()]
    VALIDAS = {'10pt', '11pt', '12pt', 'a4paper', 'letterpaper', 'oneside', 'twoside', 'openany',
               'openright', 'draft', 'final', 'landscape', 'titlepage', 'notitlepage', 'fleqn', 'leqno'}
    malas = [o for o in opciones if o not in VALIDAS]
    ok(not malas, f'las opciones de \\documentclass{{{clase}}} son validas: {opciones}'
                  + (f' — DESCONOCIDAS: {malas}' if malas else ''))

    # --- paquetes
    paquetes = []
    for m in re.finditer(r'\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}', sin_com):
        paquetes += [p.strip() for p in m.group(1).split(',')]
    raros = [p for p in paquetes if p not in CONOCIDOS]
    ok(not raros, f'los {len(paquetes)} paquetes del preambulo son de TeX Live'
                  + (f' — COMPROBAR: {raros}' if raros else ''))

    # --- biblatex necesita biber
    usa_biblatex = 'biblatex' in paquetes
    if usa_biblatex:
        backend = re.search(r'\\usepackage\[[^\]]*backend\s*=\s*(\w+)', sin_com)
        ok(bool(backend) and backend.group(1) == 'biber',
           'biblatex declara backend=biber (en Overleaf hay que elegir Biber en Menu > Bibliography)')
        ok((LIBRO / 'referencias.bib').exists(), 'referencias.bib esta presente')

    # --- archivos incluidos
    faltan = []
    for m in re.finditer(r'\\(?:include|input)\{([^}]+)\}', sin_com):
        rel = m.group(1)
        if not (LIBRO / (rel + '.tex')).exists():
            faltan.append(rel)
    ok(not faltan, 'todos los archivos incluidos existen' + (f' — FALTAN: {faltan}' if faltan else ''))

    # --- imagenes de todos los .tex
    todos = '\n'.join(re.sub(r'(?<!\\)%.*', '', p.read_text(encoding='utf-8', errors='replace'))
                      for p in LIBRO.rglob('*.tex'))
    img_faltan = []
    for m in re.finditer(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', todos):
        rel = m.group(1)
        if not any((LIBRO / (rel + e)).exists() for e in ('', '.png', '.pdf', '.jpg', '.jpeg')):
            img_faltan.append(rel)
    ok(not img_faltan, 'todas las figuras referenciadas estan en la carpeta'
                       + (f' — FALTAN: {img_faltan}' if img_faltan else ''))

    if fallos:
        print(f'\n  {len(fallos)} problemas: no se empaqueta hasta resolverlos')
        return 1

    # --- empaquetar
    # Solo viajan las imagenes que algun \includegraphics usa: las demas de figuras/ quedan en el disco
    # pero no ensucian el proyecto de Overleaf.
    usadas = set()
    for m in re.finditer(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', todos):
        rel = m.group(1)
        for e in ('', '.png', '.pdf', '.jpg', '.jpeg'):
            if (LIBRO / (rel + e)).exists():
                usadas.add((LIBRO / (rel + e)).resolve())
    if SALIDA.exists():
        SALIDA.unlink()
    n = 0
    fuera = []
    with zipfile.ZipFile(SALIDA, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(LIBRO.rglob('*')):
            if not p.is_file():
                continue
            suf = p.suffix.lower()
            if suf in ('.png', '.pdf', '.jpg', '.jpeg') and p.resolve() not in usadas:
                fuera.append(p.relative_to(LIBRO).as_posix())
                continue
            if suf in ('.tex', '.bib', '.png', '.pdf', '.jpg', '.jpeg', '.cls', '.sty'):
                z.write(p, p.relative_to(LIBRO).as_posix())
                n += 1
    if fuera:
        print(f'\n  Imagenes que el libro no usa, fuera del zip: {", ".join(fuera)}')
    print(f'\n  {n} archivos · {SALIDA.stat().st_size / 1024:.0f} KB')
    print(f'  -> {SALIDA.relative_to(RAIZ)}')
    print('\n  En Overleaf: New Project > Upload Project > elegir este zip.')
    print('  Despues, Menu > Compiler: pdfLaTeX · Menu > Bibliography: Biber.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
