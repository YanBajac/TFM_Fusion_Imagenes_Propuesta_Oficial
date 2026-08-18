# -*- coding: utf-8 -*-
"""Saca de los entregables editables los rastros del entorno de trabajo.

DOS RASTROS, en lugares que no se ven al leer el documento y que por eso sobrevivieron:

  1. EL LIBRO tenia cinco comentarios de Word cuyo autor era el nombre de la herramienta, tres de ellos
     anclados en el texto. No aparecen en el PDF —LibreOffice no imprime los comentarios— pero se ven en
     el panel de revision en cuanto alguien abre el .docx, que es lo primero que hace quien lo recibe.
     Se retiran el archivo de comentarios, sus relaciones, su declaracion de tipo de contenido y las
     marcas que los anclan en el cuerpo.

  2. EL DECK tenia el TEXTO ALTERNATIVO de cinco imagenes con la ruta completa del directorio temporal,
     que lleva el nombre de la herramienta en el camino. Se ve en el campo de texto alternativo de
     PowerPoint y en cualquier lector de accesibilidad. Se reemplaza por el titulo de la lamina, que es
     una descripcion util y no una ruta.

EL CONTENIDO DE LOS DOCUMENTOS NO SE TOCA. El script comprueba, antes y despues, que la cantidad de
parrafos y el texto del libro y las laminas del deck sean identicos: lo unico que cambia es lo que no se
lee.

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/limpiar_rastros_entregables.py
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
LIBRO = DOCS / 'Tesis_Borrador_V3.docx'
DECK = DOCS / 'Tesis_Defensa_Presentacion.pptx'
RESP = ROOT / 'experiments' / 'results' / 'respaldos'
PAT = re.compile(r'claude|anthropic|chatgpt|openai|copilot|gemini', re.I)

# las partes de comentarios de un .docx, con las que las acompañan
PARTES_COM = ('word/comments.xml', 'word/commentsExtended.xml', 'word/commentsIds.xml',
              'word/commentsExtensible.xml', 'word/people.xml')


def texto_docx(p):
    from docx import Document
    d = Document(str(p))
    return [x.text for x in d.paragraphs], len(d.tables)


def texto_pptx(p):
    from pptx import Presentation
    pr = Presentation(str(p))
    return ['\n'.join(sh.text_frame.text for sh in s.shapes if sh.has_text_frame)
            for s in pr.slides]


def reescribir(origen, cambios, quitar=()):
    """Reescribe el zip aplicando `cambios` (nombre -> funcion sobre el texto) y quitando `quitar`."""
    tmp = origen.with_suffix(origen.suffix + '.limpio')
    with zipfile.ZipFile(origen) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            if it.filename in quitar:
                continue
            datos = zin.read(it.filename)
            if it.filename in cambios:
                datos = cambios[it.filename](datos.decode('utf-8')).encode('utf-8')
            zout.writestr(it, datos)
    return tmp


def limpiar_libro():
    if not LIBRO.exists():
        return ['no esta el libro']
    antes_p, antes_t = texto_docx(LIBRO)
    with zipfile.ZipFile(LIBRO) as z:
        presentes = [n for n in PARTES_COM if n in z.namelist()]
        n_com = len(re.findall(r'<w:comment ', z.read('word/comments.xml').decode('utf-8'))) \
            if 'word/comments.xml' in z.namelist() else 0
    if not presentes:
        return ['el libro no tiene comentarios']

    def sin_anclas(t):
        # las marcas que anclan cada comentario en el cuerpo. El <w:r> que lleva la referencia se retira
        # entero: dejar el run vacio no rompe nada, pero deja basura en el XML.
        t = re.sub(r'<w:commentRangeStart[^/]*/>', '', t)
        t = re.sub(r'<w:commentRangeEnd[^/]*/>', '', t)
        t = re.sub(r'<w:r>(?:(?!</w:r>).)*?<w:commentReference[^/]*/>.*?</w:r>', '', t, flags=re.S)
        t = re.sub(r'<w:commentReference[^/]*/>', '', t)
        return t

    def sin_rels(t):
        for n in presentes:
            hoja = n.split('/')[-1]
            t = re.sub(rf'<Relationship[^>]*Target="{hoja}"[^>]*/>', '', t)
        return t

    def sin_tipos(t):
        for n in presentes:
            t = re.sub(rf'<Override PartName="/{re.escape(n)}"[^>]*/>', '', t)
        return t

    tmp = reescribir(LIBRO, {'word/document.xml': sin_anclas,
                             'word/_rels/document.xml.rels': sin_rels,
                             '[Content_Types].xml': sin_tipos}, quitar=presentes)
    RESP.mkdir(parents=True, exist_ok=True)
    shutil.copy2(LIBRO, RESP / (LIBRO.name + '.con_comentarios'))
    tmp.replace(LIBRO)
    desp_p, desp_t = texto_docx(LIBRO)
    if desp_p != antes_p or desp_t != antes_t:
        return [f'EL CONTENIDO CAMBIO: {len(antes_p)} parrafos y {antes_t} tablas antes, '
                f'{len(desp_p)} y {desp_t} despues']
    return [f'libro: {n_com} comentarios retirados de {len(presentes)} partes; '
            f'{len(desp_p)} parrafos y {desp_t} tablas intactos']


def limpiar_deck():
    if not DECK.exists():
        return ['no esta el deck']
    antes = texto_pptx(DECK)
    from pptx import Presentation
    pr = Presentation(str(DECK))
    titulos = {}
    for i, s in enumerate(pr.slides, 1):
        t = next((sh.text_frame.text.strip() for sh in s.shapes
                  if sh.has_text_frame and sh.text_frame.text.strip()), '')
        titulos[f'ppt/slides/slide{i}.xml'] = re.sub(r'\s+', ' ', t)[:110]

    cambios, tocadas = {}, []
    with zipfile.ZipFile(DECK) as z:
        for nm in z.namelist():
            if not nm.startswith('ppt/slides/slide') or not nm.endswith('.xml'):
                continue
            t = z.read(nm).decode('utf-8')
            if not PAT.search(t):
                continue
            tocadas.append(nm)
            desc = (titulos.get(nm) or 'Figura de la presentación').replace('"', '')

            def rep(m, desc=desc):
                # solo el atributo descr, y solo si lleva un rastro: el resto del XML no se toca
                return m.group(0) if not PAT.search(m.group(1)) else f'descr="{desc}"'

            cambios[nm] = lambda s, rep=rep: re.sub(r'descr="([^"]*)"', rep, s)
    if not cambios:
        return ['el deck no tiene rastros en el texto alternativo']
    tmp = reescribir(DECK, cambios)
    RESP.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DECK, RESP / (DECK.name + '.con_rutas'))
    tmp.replace(DECK)
    desp = texto_pptx(DECK)
    if desp != antes:
        return [f'EL CONTENIDO CAMBIO: {len(antes)} laminas antes, {len(desp)} despues']
    return [f'deck: texto alternativo reemplazado en {len(tocadas)} laminas '
            f'({", ".join(n.split("/")[-1] for n in tocadas)}); {len(desp)} laminas intactas']


def main():
    msgs = limpiar_libro() + limpiar_deck()
    for m in msgs:
        print(f'    {m}')
    # control final: ninguna parte de ningun entregable editable menciona la herramienta
    quedan = []
    for p in (LIBRO, DECK):
        if not p.exists():
            continue
        with zipfile.ZipFile(p) as z:
            for nm in z.namelist():
                if nm.endswith(('.xml', '.rels')) and PAT.search(
                        z.read(nm).decode('utf-8', errors='replace')):
                    quedan.append(f'{p.name}/{nm}')
    print(f'\n  control: {len(quedan)} partes con rastros' + (f' — {quedan}' if quedan else ' (limpio)'))
    return 1 if quedan or any('CAMBIO' in m for m in msgs) else 0


if __name__ == '__main__':
    sys.exit(main())
