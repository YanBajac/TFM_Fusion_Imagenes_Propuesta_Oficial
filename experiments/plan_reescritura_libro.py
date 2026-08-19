# -*- coding: utf-8 -*-
"""Arma la lista de trabajo para reescribir el libro a mano, parrafo por parrafo.

POR QUE. El libro se va a reescribir manualmente y hay dos cosas distintas que arreglar, que hasta ahora
vivian en lugares separados y sin cruzarse:

  1. LO QUE DICE MAL. Estan en docs/AUDITORIA_LIBRO.md: 54 afirmaciones confirmadas contra los CSV, 11 de
     gravedad alta. Sus titulos nombran el parrafo, asi que se pueden ubicar.
  2. COMO ESTA ESCRITO. Un barrido de estilometria midio lo que un detector o un lector atento usan de
     verdad: oraciones demasiado largas y demasiado parejas, densidad de rayas, series ordinales
     anunciadas. Eso hasta ahora eran totales del libro entero, que no dicen que parrafo tocar.

Este script mide el docx parrafo por parrafo y cruza las dos cosas, para que la reescritura sea una lista
ordenada y no 75 paginas a ciegas.

DE DONDE SALEN LAS CIFRAS. Del propio .docx, con python-docx, y de la auditoria. Ninguna se escribe a
mano. El detalle completo queda en un CSV y el plan cita ese CSV.

CONTROLES. Los totales se cruzan contra la medicion independiente del barrido, y se exige lo que no
depende de como se corte el texto en oraciones: las 130 rayas, los 26 arranques ordinales, la oracion mas
larga del libro —147 palabras, y las dos mediciones encuentran LA MISMA, que es la señal mas fuerte de
que miran el mismo texto— y las 127 oraciones de mas de 40 palabras. El conteo total de oraciones no se
exige: los dos cortadores segmentan distinto —este da 458 y el barrido 400— y eso es politica, no error;
se imprime al lado para que la diferencia quede a la vista. Y avisa si la auditoria nombra un parrafo que
no existe.

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/plan_reescritura_libro.py
"""
import csv
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
LIBRO = RAIZ / 'docs' / 'Tesis_Borrador_V3.docx'
AUD = RAIZ / 'docs' / 'AUDITORIA_LIBRO.md'
CSV_OUT = RAIZ / 'experiments' / 'results' / 'metrics_reports' / 'estilo_por_parrafo.csv'
MD_OUT = RAIZ / 'docs' / 'PLAN_REESCRITURA_LIBRO.md'

# LO QUE MIDIO EL BARRIDO, para cruzar contra una medicion independiente.
# QUE SE COMPARA Y QUE NO, que es la parte que importa. Se exigen las cantidades que no dependen de como
# se corte el texto en oraciones: las rayas, los arranques ordinales, la oracion mas larga del libro
# —un punto de referencia agudo: si las dos mediciones encuentran la misma, estan mirando el mismo
# texto— y cuantas pasan de 40 palabras.
# El CONTEO TOTAL de oraciones NO se exige, y no por comodidad: los dos cortadores segmentan distinto
# —este encuentra 458 y el barrido 400 sobre practicamente las mismas palabras— y eso es una diferencia
# de politica, no un error. Se imprime al lado para que la diferencia quede a la vista, y el plan usa las
# cifras de este script, que son las del CSV que publica.
REFERENCIA = {'rayas': (130, 3), 'ordinales': (26, 3), 'oracion_mas_larga': (147, 0),
              'oraciones_largas': (127, 10)}
SOLO_INFORMATIVO = {'oraciones': 400, 'media_oracion': 33.8}
LARGA = 40                      # una oracion de mas de 40 palabras es la que hay que partir
ORDINALES = ('Primero', 'Segundo', 'Tercero', 'Cuarto', 'Quinto', 'Sexto', 'Séptimo', 'Octavo',
             'Noveno', 'Décimo', 'Finalmente')


def plano(t):
    return ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')


def oraciones(t):
    """Corta en oraciones.

    Las protecciones salieron de mirar donde cortaba mal, no de una corazonada. Lo que hay que saber, y
    esta medido: con ellas y sin ellas este cortador da las mismas 458 oraciones sobre el cuerpo, porque
    los casos que protegen —«et al.» sobre todo— ya venian resueltos por el resto de la expresion o son
    pocos. Se dejan igual porque son correctas y porque el proximo texto puede no ser tan benigno; lo que
    NO hay que hacer es atribuirles una mejora que no produjeron.
    El barrido, con su propio cortador, conto 400 sobre practicamente las mismas palabras: los dos
    coinciden en la oracion mas larga (147) y en las que pasan de 40 (121 contra 127), y difieren en
    cuantas oraciones cortas reconocen. Eso es politica de segmentacion.
      · abreviaturas y «et al.»;
      · ordinales femeninos, que en este libro son puestos de ranking: «1.ª de 7»;
      · el numero que abre un item de lista, «1. Primero...», que no es fin de oracion;
      · iniciales de nombre, «J. C. Mello».
    """
    t = re.sub(r'^\s*\d+\.\s', '', t)                                  # el rotulo del item de lista
    t = re.sub(r'\b(Fig|Tab|Ec|Dr|Lic|Ing|Sr|Sra|aprox|vs|cf|ed|cap|art|num)\.', r'\1<PUNTO>', t)
    t = re.sub(r'\bp\. ej\.', 'p<PUNTO> ej<PUNTO>', t)
    t = re.sub(r'\bet al\.', 'et al<PUNTO>', t)
    t = re.sub(r'(\d)\.(ª|º)', r'\1<PUNTO>\2', t)
    t = re.sub(r'\b([A-ZÁÉÍÓÚÑ])\.(?=\s)', r'\1<PUNTO>', t)            # iniciales de nombre
    partes = re.split(r'(?<=[.!?])\s+(?=[«"(¿¡A-ZÁÉÍÓÚÑ0-9])', t)
    return [x.replace('<PUNTO>', '.').strip() for x in partes if x.strip()]


def cuerpo(ps):
    """El rango del cuerpo: de INTRODUCCION a REFERENCIAS, los dos como titulo."""
    ini = fin = None
    for i, p in enumerate(ps):
        t = plano(p.text.strip()).upper()
        if p.style.name.startswith('Heading'):
            if ini is None and t == 'INTRODUCCION':
                ini = i
            elif ini is not None and 'REFERENCIAS' in t:
                fin = i
                break
    if ini is None or fin is None:
        raise SystemExit(f'ABORTA: no se pudo delimitar el cuerpo (INTRODUCCION={ini}, '
                         f'REFERENCIAS={fin})')
    return ini, fin


VEREDICTOS = ('CONTRADICE', 'SIN FUENTE', 'INCOHERENCIA', 'IMPRECISION', 'NO VERIFICABLE')


def veredicto(titulo):
    """El tipo de falla, que la auditoria escribe al final del titulo despues de una raya."""
    t = plano(titulo).upper()
    for v in VEREDICTOS:
        if v in t:
            return v
    return 'revisar'


def ubicacion(titulo):
    """La seccion, tabla o apendice que el titulo nombra, sin el numero de parrafo."""
    m = re.search(r'§\s*[\d.]+', titulo)
    if m:
        return m.group(0).replace(' ', '')
    m = re.search(r'(Tabla|Cuadro)\s+\d+', titulo)
    if m:
        return m.group(0)
    m = re.search(r'ap[eé]ndice\s+([A-E])', titulo, re.I)
    if m:
        return f'apéndice {m.group(1).upper()}'
    m = re.search(r'(conclusi[oó]n(?:\s+espec[ií]fica)?|recomendaci[oó]n|limitaci[oó]n|'
                  r'hip[oó]tesis|RESUMEN|SUMMARY)\s*(\w+)?', titulo, re.I)
    if m:
        return re.sub(r'\s+', ' ', m.group(0)).strip()
    return '—'


def hallazgos_auditoria():
    """{n_parrafo: [(gravedad, titulo)]} leido de los titulos de la auditoria."""
    if not AUD.exists():
        return {}, {}
    grav, out, titulos = None, {}, {}
    for ln in AUD.read_text(encoding='utf-8').splitlines():
        m = re.match(r'^##\s+(.*)$', ln)
        if m:
            t = plano(m.group(1)).lower()
            grav = ('alta' if 'alta' in t else 'media' if 'media' in t else
                    'baja' if 'baja' in t else 'refutada' if 'refutad' in t else None)
            continue
        m = re.match(r'^###\s+(.*)$', ln)
        if m and grav in ('alta', 'media', 'baja'):
            titulo = m.group(1).strip()
            nums = [int(x) for x in re.findall(r'[Pp]arrafos?\s+(\d+)(?:\s+y\s+(\d+))?', plano(titulo))
                    for x in ([x] if isinstance(x, str) else x) if x]
            nums = [int(x) for x in re.findall(r'\d+', ' '.join(
                re.findall(r'[Pp]arrafos?\s+((?:\d+)(?:\s+y\s+\d+)?)', plano(titulo))))]
            for n in nums:
                out.setdefault(n, []).append((grav, titulo))
            titulos.setdefault(grav, []).append((titulo, nums))
    return out, titulos


def main():
    from docx import Document
    if not LIBRO.exists():
        print(f'  no esta {LIBRO.name}')
        return 1
    ps = Document(str(LIBRO)).paragraphs
    ini, fin = cuerpo(ps)
    por_parrafo, aud, _tit = [], *hallazgos_auditoria()

    # SE RECORRE EL DOCUMENTO ENTERO Y NO SOLO EL CUERPO. La auditoria tiene hallazgos en los apendices
    # (parrafos 484 a 519) y en el RESUMEN y el SUMMARY (83 y 86), que estan fuera del rango del cuerpo:
    # la primera version los dejaba afuera y avisaba «nombra parrafos que no estan». La zona queda en una
    # columna, y las cifras de estilo se totalizan SOLO sobre el cuerpo, que es lo que el barrido midio.
    for i, p in enumerate(ps):
        t = p.text.strip()
        if not t or p.style.name.startswith('Heading'):
            continue
        zona = 'cuerpo' if ini <= i < fin else ('frente' if i < ini else 'apendice')
        if zona != 'cuerpo' and i not in aud:
            continue                     # del frente y los apendices, solo lo que tiene hallazgo
        ors = oraciones(t)
        largos = [len(o.split()) for o in ors]
        fila = {
            'parrafo': i,
            'zona': zona,
            'estilo': p.style.name,
            'palabras': len(t.split()),
            'oraciones': len(ors),
            'oracion_mas_larga': max(largos) if largos else 0,
            'oraciones_largas': sum(1 for x in largos if x > LARGA),
            'rayas': t.count('—'),
            'punto_y_coma': t.count(';'),
            'arranque_ordinal': sum(1 for o in ors if o.split(',')[0].strip(' «"') in ORDINALES),
            'hallazgos': ' + '.join(f'{g}: {ti}' for g, ti in aud.get(i, [])),
            # el titulo crudo de la auditoria no sirve en una tabla: se parte a mitad de palabra. Se
            # separa en QUE falla (el veredicto, que va despues de la raya) y DONDE (la seccion o tabla)
            'veredictos': ' · '.join(sorted({veredicto(ti) for _g, ti in aud.get(i, [])})),
            'ubicaciones': ' · '.join(sorted({ubicacion(ti) for _g, ti in aud.get(i, [])}
                                             - {'—'}) or ['—']),
            'n_hallazgos': len(aud.get(i, [])),
            'gravedad_max': ('alta' if any(g == 'alta' for g, _ in aud.get(i, [])) else
                             'media' if any(g == 'media' for g, _ in aud.get(i, [])) else
                             'baja' if aud.get(i) else ''),
            'inicio': re.sub(r'\s+', ' ', t)[:90],
        }
        por_parrafo.append(fila)

    # ------------------------------------------------------------- controles
    cpo = [f for f in por_parrafo if f['zona'] == 'cuerpo']
    tot = {
        'rayas': sum(f['rayas'] for f in cpo),
        'ordinales': sum(f['arranque_ordinal'] for f in cpo),
        'oraciones': sum(f['oraciones'] for f in cpo),
        'oracion_mas_larga': max((f['oracion_mas_larga'] for f in cpo), default=0),
        'oraciones_largas': sum(f['oraciones_largas'] for f in cpo),
    }
    tot['media_oracion'] = round(sum(f['palabras'] for f in cpo) / max(tot['oraciones'], 1), 1)
    print(f'  cuerpo: parrafos {ini}-{fin}, {len(cpo)} con texto, '
          f'{sum(f["palabras"] for f in cpo)} palabras · fuera del cuerpo, '
          f'{len(por_parrafo) - len(cpo)} parrafos con hallazgo')
    desvios = []
    for k, (v, tol) in REFERENCIA.items():
        mio, dif = tot[k], abs(tot[k] - v) / max(v, 1) * 100
        marca = 'ok' if dif <= tol else 'DIFIERE'
        print(f'     {k:<18} barrido {v:<7} este script {mio:<7} {marca} '
              f'({dif:.1f} % · tolerancia {tol} %)')
        if dif > tol:
            desvios.append(k)
    for k, v in SOLO_INFORMATIVO.items():
        print(f'     {k:<18} barrido {v:<7} este script {tot[k]:<7} (no se exige: los dos '
              f'cortadores segmentan distinto)')

    fuera = [n for n in aud if not any(f['parrafo'] == n for f in por_parrafo)]
    if fuera:
        print(f'  AVISO la auditoria nombra parrafos que no existen o estan vacios: {fuera}')

    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(por_parrafo[0]))
        w.writeheader()
        w.writerows(por_parrafo)
    print(f'  -> {CSV_OUT.relative_to(RAIZ)} ({len(por_parrafo)} filas)')

    # ------------------------------------------------------------- el plan
    con_hallazgo = [f for f in por_parrafo if f['gravedad_max']]
    orden = {'alta': 0, 'media': 1, 'baja': 2, '': 3}
    con_hallazgo.sort(key=lambda f: (orden[f['gravedad_max']], -f['oraciones_largas'], f['parrafo']))
    # carga de estilo: lo que un detector mide. Se ordena por rayas y oraciones largas juntas.
    carga = sorted((f for f in cpo if f['rayas'] >= 2 or f['oraciones_largas'] >= 2),
                   key=lambda f: (-(f['rayas'] + 2 * f['oraciones_largas']), f['parrafo']))
    resumenes = [f for f in por_parrafo if f['palabras'] > 300]

    L = []
    L.append('# Plan de reescritura del libro, párrafo por párrafo')
    L.append('')
    L.append('Lo produce `experiments/plan_reescritura_libro.py` desde el propio `.docx` y desde')
    L.append('`AUDITORIA_LIBRO.md`. El detalle completo de las mediciones está en')
    L.append(f'`{CSV_OUT.relative_to(RAIZ).as_posix()}`, una fila por párrafo del cuerpo.')
    L.append('')
    L.append('**Dos cosas distintas que arreglar, y conviene no mezclarlas.** Lo que el libro *dice* mal')
    L.append('—las afirmaciones que no coinciden con los datos— y *cómo* está escrito. La primera es')
    L.append('corrección; la segunda es reescritura. Un párrafo que aparece en las dos listas conviene')
    L.append('reescribirlo entero de una sola vez.')
    L.append('')
    L.append(f'## 1. Lo que dice mal: {len(con_hallazgo)} párrafos con hallazgo confirmado')
    L.append('')
    L.append('Ordenados por gravedad. La columna «carga» dice si además hay que reescribir el estilo:')
    L.append('rayas y oraciones de más de 40 palabras.')
    L.append('')
    L.append('| Párrafo | Zona | Gravedad | Qué falla | Dónde | Carga de estilo |')
    L.append('|---:|:---|:---|:---|:---|:---|')
    for f in con_hallazgo:
        c = (f'{f["rayas"]} rayas, {f["oraciones_largas"]} '
             + ('larga' if f['oraciones_largas'] == 1 else 'largas')
             if (f['rayas'] or f['oraciones_largas']) else '—')
        L.append(f'| {f["parrafo"]} | {f["zona"]} | {f["gravedad_max"]} | {f["veredictos"]} | '
                 f'{f["ubicaciones"]} | {c} |')
    L.append('')
    L.append(f'El detalle de cada uno —qué dice el libro, qué dicen los datos y de qué CSV salen— está en')
    L.append('`AUDITORIA_LIBRO.md`, en la sección de su gravedad.')
    L.append('')
    L.append(f'## 2. Cómo está escrito: {len(carga)} párrafos con carga de estilo')
    L.append('')
    L.append('Estas tres cosas son las que mide un detector, y son las tres que se arreglan sin discutir')
    L.append('el contenido:')
    L.append('')
    L.append(f'- **Rayas (—).** El cuerpo tiene {tot["rayas"]} en total. Son incisos: se convierten en')
    L.append('  paréntesis, en comas o en oración aparte. No hay ninguna suelta, así que siempre vienen')
    L.append('  de a pares y se sacan de a pares.')
    L.append(f'- **Oraciones largas.** La media del cuerpo es de '
                 f'{str(tot["media_oracion"]).replace(".", ",")} palabras. Las de más')
    L.append(f'  de {LARGA} se parten, y el punto y coma marca dónde: no hay que reordenar palabras.')
    L.append(f'- **Series ordinales anunciadas.** {tot["ordinales"]} arranques «Primero/Segundo/…». Alcanza con')
    L.append('  variar el andamio en algunos, sacando el número anunciado al principio del párrafo.')
    L.append('')
    L.append('| Párrafo | Palabras | Oración más larga | Largas | Rayas | `;` | Ordinal | Arranca |')
    L.append('|---:|---:|---:|---:|---:|---:|:---:|:---|')
    for f in carga[:60]:
        L.append(f'| {f["parrafo"]} | {f["palabras"]} | {f["oracion_mas_larga"]} | '
                 f'{f["oraciones_largas"]} | {f["rayas"]} | {f["punto_y_coma"]} | '
                 f'{"sí" if f["arranque_ordinal"] else ""} | {f["inicio"][:60]}… |')
    if len(carga) > 60:
        L.append('')
        L.append(f'*(La tabla muestra los 60 de mayor carga de {len(carga)}. El resto está en el CSV.)*')
    L.append('')
    L.append('## 3. RESUMEN y SUMMARY: el caso más barato y el más visible')
    L.append('')
    for f in resumenes:
        L.append(f'- **Párrafo {f["parrafo"]}**: {f["palabras"]} palabras en un solo párrafo, '
                 f'{f["oraciones"]} oraciones, la más larga de {f["oracion_mas_larga"]}, '
                 f'{f["rayas"]} rayas y {f["punto_y_coma"]} puntos y coma.')
    L.append('')
    L.append('Es lo primero que lee un examinador y es donde la longitud de oración es más alta de todo')
    L.append('el libro. Se parte en tres o cuatro párrafos cortando en los puntos y coma que ya tiene.')
    L.append('')
    L.append('## 4. Para saber cuándo terminaste')
    L.append('')
    L.append('| Qué | Ahora | Objetivo razonable |')
    L.append('|:---|---:|:---|')
    L.append(f'| Media de palabras por oración | {str(tot["media_oracion"]).replace(".", ",")} | 20 a 24 |')
    L.append(f'| Oraciones de más de {LARGA} palabras | {tot["oraciones_largas"]} | menos de la mitad |')
    L.append(f'| Rayas (—) en el cuerpo | {tot["rayas"]} | menos de 40 |')
    L.append(f'| Arranques ordinales | {tot["ordinales"]} | menos de 10 |')
    L.append('')
    L.append('Volver a correr este script después de cada tanda de reescritura recalcula la tabla.')
    L.append('')
    MD_OUT.write_text('\n'.join(L), encoding='utf-8', newline='\n')
    print(f'  -> {MD_OUT.relative_to(RAIZ)} ({len(L)} lineas)')
    print(f'     {len(con_hallazgo)} parrafos con hallazgo · {len(carga)} con carga de estilo · '
          f'{len(resumenes)} monoparrafo')
    return 1 if desvios else 0


if __name__ == '__main__':
    sys.exit(main())
