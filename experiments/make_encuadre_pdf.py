# -*- coding: utf-8 -*-
"""Arma el PDF de la propuesta de encuadre a partir de docs/PROPUESTA_ENCUADRE.md.

POR QUE EXISTE. La pagina 3 del informe de avances le dice al director que la redaccion propuesta «va
aparte, en un documento breve». Ese documento existia solo como markdown dentro del repositorio, o sea
que la promesa no se podia cumplir: hay que poder adjuntarlo.

DE DONDE SALE EL CONTENIDO. Del markdown, y de ningun otro lugar. Este script no escribe prosa: convierte.
Si hay que cambiar una frase se cambia en el .md y se vuelve a correr, para que no existan dos versiones
que se separen —el mismo criterio con que el informe lee las referencias del libro y la secuencia de
reproduccion del README—.

LA TIPOGRAFIA ES LA DEL INFORME, extraida de su propio HTML: los dos documentos llegan juntos al director
y tienen que verse como el mismo trabajo.

LA PAGINACION ES DECLARATIVA, y es un guardrail y no una comodidad. Cada seccion del markdown tiene que
estar asignada a una pagina en PAGINAS; si aparece una seccion nueva y nadie la asigno, el script ABORTA
en lugar de dejarla afuera. Y despues de imprimir se exige que el PDF tenga tantas paginas como se
declararon: si una derrama, se entera acá y no el lector.

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/make_encuadre_pdf.py
"""
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import fitz

RAIZ = Path(__file__).resolve().parents[1]
MD = RAIZ / 'docs' / 'PROPUESTA_ENCUADRE.md'
HTML_INFORME = RAIZ / 'docs' / '_local' / 'Avances_Tesis.html'
HTML_OUT = RAIZ / 'docs' / '_local' / 'Propuesta_Encuadre.html'
PDF_OUT = RAIZ / 'docs' / 'Propuesta_Encuadre.pdf'

# que seccion va en que pagina. La clave es el titulo tal como esta en el markdown; 'INTRO' es lo que
# viene antes del primer «##».
PAGINAS = [
    ['INTRO',
     'El problema, en cuatro frases',
     'Qué demuestra hoy la evidencia, mitad por mitad',
     'La propuesta: un objetivo, dos mitades, y la auditoría como explicación'],
    ['Redacción propuesta para el encuadre del aporte',
     'Y la conclusión que cierra la segunda mitad'],
    ['Lo que hay que decidirle, concretamente',
     'Lo que este documento no resuelve'],
]

EDGE = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
if not os.path.exists(EDGE):
    EDGE = r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'


# --------------------------------------------------------------------------- markdown -> html
def enlinea(t):
    """El formato de una linea: negrita, cursiva, codigo. Nada mas: el documento no usa otra cosa."""
    t = (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
    t = re.sub(r'`([^`]+)`', r'<span class="mono">\1</span>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<![*\w])\*([^*]+)\*(?![*\w])', r'<i>\1</i>', t)
    return t


def secciones(texto):
    """[(titulo, nivel, [bloques])], donde cada bloque es ('p'|'cita'|'ol', [lineas])."""
    out, actual = [], ('INTRO', 0, [])
    lineas = texto.splitlines()
    i = 0
    while i < len(lineas):
        ln = lineas[i]
        m = re.match(r'^(#{1,4})\s+(.*)$', ln)
        if m:
            if m.group(1) == '#':                       # el titulo del documento va con la intro
                actual[2].append(('h1', [m.group(2).strip()]))
                i += 1
                continue
            out.append(actual)
            actual = (m.group(2).strip(), len(m.group(1)), [])
            i += 1
            continue
        if ln.startswith('> '):
            cita = []
            while i < len(lineas) and (lineas[i].startswith('>')):
                t = lineas[i][1:].strip()
                if not t:
                    cita.append('')                     # parrafo nuevo dentro de la cita
                else:
                    cita.append(t)
                i += 1
            actual[2].append(('cita', cita))
            continue
        m = re.match(r'^(\d+)\.\s+(.*)$', ln)
        if m:
            items = []
            while i < len(lineas):
                m2 = re.match(r'^(\d+)\.\s+(.*)$', lineas[i])
                if m2:
                    items.append(m2.group(2).strip())
                    i += 1
                elif lineas[i].startswith('   ') and items:
                    items[-1] += ' ' + lineas[i].strip()
                    i += 1
                else:
                    break
            actual[2].append(('ol', items))
            continue
        if ln.strip():
            par = []
            while i < len(lineas) and lineas[i].strip() and not lineas[i].startswith(('#', '>')) \
                    and not re.match(r'^\d+\.\s', lineas[i]):
                par.append(lineas[i].strip())
                i += 1
            actual[2].append(('p', [' '.join(par)]))
            continue
        i += 1
    out.append(actual)
    return out


def html_de(sec):
    titulo, nivel, bloques = sec
    h = []
    if titulo != 'INTRO':
        h.append(f'<h{min(nivel, 3)}>{enlinea(titulo)}</h{min(nivel, 3)}>')
    for tipo, cuerpo in bloques:
        if tipo == 'h1':
            h.append(f'<h2 class="titulodoc">{enlinea(cuerpo[0])}</h2>')
        elif tipo == 'p':
            h.append(f'<p>{enlinea(cuerpo[0])}</p>')
        elif tipo == 'cita':
            partes, buf = [], []
            for ln in cuerpo:
                if ln:
                    buf.append(ln)
                elif buf:
                    partes.append(' '.join(buf))
                    buf = []
            if buf:
                partes.append(' '.join(buf))
            h.append('<div class="cita">'
                     + ''.join(f'<p>{enlinea(x)}</p>' for x in partes) + '</div>')
        elif tipo == 'ol':
            h.append('<ol>' + ''.join(f'<li>{enlinea(x)}</li>' for x in cuerpo) + '</ol>')
    return '\n'.join(h)


def main():
    if not MD.exists():
        print(f'  no esta {MD.relative_to(RAIZ)}')
        return 1
    secs = {s[0]: s for s in secciones(MD.read_text(encoding='utf-8'))}

    # GUARDRAIL: toda seccion del markdown tiene que estar asignada a una pagina, y toda pagina tiene
    # que nombrar secciones que existan. Sin esto, agregar una seccion al .md la dejaria afuera del PDF
    # sin que nada avise.
    declaradas = [t for pg in PAGINAS for t in pg]
    sin_asignar = [t for t in secs if t not in declaradas]
    inexistentes = [t for t in declaradas if t not in secs]
    if sin_asignar or inexistentes:
        print(f'  ABORTA: secciones del markdown sin pagina asignada: {sin_asignar}')
        print(f'          paginas que nombran secciones inexistentes: {inexistentes}')
        return 1
    if len(declaradas) != len(set(declaradas)):
        print('  ABORTA: una seccion esta asignada a dos paginas')
        return 1

    css = re.search(r'<style.*?</style>', HTML_INFORME.read_text(encoding='utf-8'), re.S).group(0)
    extra = """<style>
      .titulodoc { font-size: 13pt; text-align: center; margin: 0 0 6mm 0; }
      .cita { margin: 2mm 0 3mm 6mm; padding-left: 4mm; border-left: 1pt solid #999; }
      .cita p { font-size: 10.5pt; }
      .mono { font-family: "Consolas", "Courier New", monospace; font-size: 9.5pt; }
      ol { margin: 1mm 0 3mm 0; padding-left: 8mm; }
      li { margin-bottom: 2mm; }
    </style>"""

    cuerpo = []
    for n, pg in enumerate(PAGINAS, 1):
        cuerpo.append('<div class="page">'
                      + '\n'.join(html_de(secs[t]) for t in pg)
                      + f'<div class="pie">{n}</div></div>')
    HTML_OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML_OUT.write_text('<!doctype html><html><head><meta charset="utf-8">'
                        + css + extra + '</head><body>' + '\n'.join(cuerpo) + '</body></html>',
                        encoding='utf-8', newline='\n')

    if not os.path.exists(EDGE):
        print('  no se encontro Edge: quedo el HTML sin imprimir')
        return 1
    tmp = str(PDF_OUT) + '.edge.tmp'
    if os.path.exists(tmp):
        os.remove(tmp)
    subprocess.run([EDGE, '--headless', '--disable-gpu', f'--print-to-pdf={tmp}',
                    '--no-pdf-header-footer', str(HTML_OUT)], capture_output=True, timeout=300)
    # la misma espera que el informe: no alcanza con que el tamaño se repita, el documento tiene que
    # ABRIR y dar la misma cantidad de paginas en dos lecturas seguidas
    ant, ant_pg, estable = -1, -1, 0
    for _ in range(75):
        tam = os.path.getsize(tmp) if os.path.exists(tmp) else -1
        try:
            with fitz.open(tmp) as d:
                pg = d.page_count
        except Exception:
            pg = -1
        estable = estable + 1 if (tam == ant and pg == ant_pg and pg > 0) else 0
        if estable >= 2:
            break
        ant, ant_pg = tam, pg
        time.sleep(0.4)
    os.replace(tmp, PDF_OUT)

    # ---------------------------------------------------------------- controles sobre el PDF cerrado
    with fitz.open(str(PDF_OUT)) as d:
        n_pag = d.page_count
        texto = '\n'.join(d[i].get_text() for i in range(n_pag))
    plano = re.sub(r'\s+', ' ', texto)
    fallos = []
    if n_pag != len(PAGINAS):
        fallos.append(f'se declararon {len(PAGINAS)} paginas y el PDF tiene {n_pag}: alguna derramo')
    for t in secs:
        if t != 'INTRO' and re.sub(r'\s+', ' ', re.sub(r'\*\*|`', '', t)) not in plano:
            fallos.append(f'el titulo «{t}» no aparece en el PDF')
    # las citas son la razon de ser del documento: se comprueba que ninguna se haya perdido
    citas = [b for s in secs.values() for tipo, b in s[2] if tipo == 'cita']
    for c in citas:
        primera = next((x for x in c if x), '')
        clave = re.sub(r'\*\*|`', '', primera)[:40]
        if clave and re.sub(r'\s+', ' ', clave) not in plano:
            fallos.append(f'falta una cita: «{clave}…»')
    # El vocabulario de rastros no se repite aca: vive en limpiar_rastros_entregables, que es el modulo
    # que existe para eso. Tenerlo en dos lugares hace que uno de los dos se quede viejo, y ademas
    # obligaba a declarar este archivo en la lista de excepciones del bloque 29 del verificador.
    from limpiar_rastros_entregables import PAT, RUTA
    sucio = PAT.search(plano) or RUTA.search(plano)
    if sucio:
        fallos.append(f'el PDF lleva un rastro: «{plano[max(0, sucio.start() - 30):sucio.end() + 30]}»')

    print(f'  {PDF_OUT.relative_to(RAIZ)}: {n_pag} paginas · {len(plano.split())} palabras · '
          f'{len(secs) - 1} secciones · {len(citas)} citas')
    for i in range(n_pag):
        with fitz.open(str(PDF_OUT)) as d:
            print(f'     pag. {i + 1}: {len(d[i].get_text().split()):>3} palabras')
    if fallos:
        for f in fallos:
            print(f'  FALLA {f}')
        return 1
    print('  controles: paginacion, titulos, citas y rastros — todo en orden')
    return 0


if __name__ == '__main__':
    sys.exit(main())
