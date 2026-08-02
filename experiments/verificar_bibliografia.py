# -*- coding: utf-8 -*-
"""Verificador de la bibliografia, 2.a version.

La 1.a version emparejaba solo por titulo y engancho resenas de libros y trabajos
ajenos. Esta exige ademas coincidencia de APELLIDOS, y cuando no la consigue
declara "no verificada" en lugar de adivinar.

Salida: fuentes/v2.json  +  informe por consola.
"""
import json
import re
import subprocess
import time
import unicodedata
import urllib.parse
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / 'docs' / 'fuentes'
CORREO = 'yan_bajac@softshop.com.py'
UA = f'verificacion-bibliografia-tesis/2.0 (mailto:{CORREO})'

# obras que Crossref no indexa como registro propio (libros de editorial)
LIBROS = {8, 21, 24}
# obras sin DOI por naturaleza
SIN_DOI = {18}


def get(url, intentos=3):
    for i in range(intentos):
        try:
            p = subprocess.run(
                ['curl', '-sSL', '--max-time', '45', '-H', f'User-Agent: {UA}',
                 '-H', 'Accept: application/json', url],
                capture_output=True, text=True, encoding='utf-8', timeout=60)
            if p.returncode != 0:
                raise RuntimeError((p.stderr or 'curl fallo')[:120])
            return json.loads(p.stdout)
        except Exception as e:                                    # noqa: BLE001
            if i == intentos - 1:
                return {'__error__': str(e)[:140]}
            time.sleep(2 * (i + 1))


def sin_tildes(s):
    s = unicodedata.normalize('NFKD', s or '')
    return ''.join(c for c in s if not unicodedata.combining(c))


def norm(s):
    return re.sub(r'[^a-z0-9 ]', ' ', sin_tildes(s).lower()).strip()


def pal(s):
    return {w for w in norm(s).split() if len(w) > 2}


def parse(cita):
    m = re.match(r'^(.*?)\((\d{4})\)\.\s*(.*)$', cita, re.S)
    if not m:
        return None, None, None, cita
    aut, anio, cola = m.group(1).strip().rstrip('.,'), m.group(2), m.group(3)
    mt = re.match(r'^(.*?)\.\s+(?=[A-ZÁÉÍÓÚÑ]|En\b|http)', cola, re.S)
    tit = (mt.group(1) if mt else cola).strip()
    return aut, anio, tit, cola[len(tit):].lstrip('. ').strip()


def apellidos(aut):
    """Apellidos de una lista APA: 'Bai, X., Zhou, F., y Xue, B.' -> [bai, zhou, xue]."""
    aut = re.sub(r'\s+y\s+', ', ', aut or '')
    trozos = [t.strip().rstrip('.') for t in aut.split(',')]
    out = []
    for t in trozos:
        if not t:
            continue
        # descartar bloques de iniciales tipo 'X' / 'A. A' / 'P. N'
        if re.fullmatch(r'(?:[A-Z]\.?\s*)+', t):
            continue
        out.append(norm(t))
    return [x for x in out if x]


def buscar(tit, anio, aps):
    """Busca en Crossref exigiendo titulo parecido Y un apellido en comun."""
    q = urllib.parse.quote(tit[:200])
    d = get(f'https://api.crossref.org/works?query.bibliographic={q}&rows=8')
    if not d or '__error__' in d:
        return None, (d or {}).get('__error__', 'sin respuesta'), 0, 0
    obj = pal(tit)
    mejor = None
    for it in d.get('message', {}).get('items', []):
        t = (it.get('title') or [''])[0]
        c = pal(t)
        if not c:
            continue
        jac = len(obj & c) / max(1, len(obj | c))
        fam = [norm(a.get('family', '')) for a in it.get('author', [])]
        comun = sum(1 for a in aps if any(a and (a in f or f in a) for f in fam))
        puntaje = jac + 0.5 * min(comun, 2) / 2
        if mejor is None or puntaje > mejor[0]:
            mejor = (puntaje, it, jac, comun)
    if mejor is None:
        return None, 'sin resultados', 0, 0
    _, it, jac, comun = mejor
    if jac < 0.6:
        return None, f'titulo no coincide (jaccard {jac:.2f})', jac, comun
    if aps and comun == 0:
        return None, f'ningun apellido en comun (jaccard titulo {jac:.2f})', jac, comun
    return it, None, jac, comun


def anio_de(it):
    for c in ('published-print', 'published-online', 'issued'):
        p = it.get(c, {}).get('date-parts', [[None]])
        if p and p[0] and p[0][0]:
            return str(p[0][0])
    return None


def oa(doi):
    if not doi:
        return {}
    d = get(f'https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}?mailto={CORREO}')
    if not d or '__error__' in d:
        return {}
    b = d.get('best_oa_location') or {}
    return {'es_oa': bool(d.get('open_access', {}).get('is_oa')),
            'estado': d.get('open_access', {}).get('oa_status'),
            'pdf': b.get('pdf_url'), 'landing': b.get('landing_page_url'),
            'licencia': b.get('license')}


refs = json.loads((BASE / 'entradas.json').read_text(encoding='utf-8'))
out = []
for i, r in enumerate(refs, 1):
    cita = r['cita']
    aut, anio, tit, resto = parse(cita)
    aps = apellidos(aut)
    reg = {'n': i, 'cita': cita, 'anio': anio, 'titulo': tit, 'apellidos': aps}
    if i in LIBROS or i in SIN_DOI:
        reg['estado'] = 'no aplica (libro o sin DOI): verificar por catalogo'
        print(f'{i:2}. APARTE   {tit[:56]}')
        out.append(reg)
        continue
    it, err, jac, comun = buscar(tit, anio, aps)
    if it is None:
        reg.update({'estado': 'no verificada', 'motivo': err})
        print(f'{i:2}. NO VERIF {tit[:52]}  [{err}]')
        out.append(reg)
        time.sleep(0.3)
        continue
    doi = it.get('DOI')
    cr_anio, cr_pg, cr_vol = anio_de(it), it.get('page'), it.get('volume')
    fam = [a.get('family', '') for a in it.get('author', [])]
    reg.update({'estado': 'verificada', 'doi': doi, 'jaccard': round(jac, 2),
                'apellidos_en_comun': comun,
                'cr_titulo': (it.get('title') or [''])[0], 'cr_anio': cr_anio,
                'cr_revista': (it.get('container-title') or [''])[0],
                'cr_vol': cr_vol, 'cr_num': it.get('issue'), 'cr_pag': cr_pg,
                'cr_autores': fam, 'cr_tipo': it.get('type')})
    d = []
    if cr_anio and cr_anio != anio:
        d.append(f'anio: tesis {anio} / fuente {cr_anio}')
    if len(aps) != len(fam):
        d.append(f'autores: tesis {len(aps)} / fuente {len(fam)} ({", ".join(fam)})')
    solo_dig = re.sub(r'[^\d]', '', resto)
    if cr_vol and not re.search(rf'\b{re.escape(cr_vol)}\b', resto):
        d.append(f'volumen: fuente {cr_vol} no figura')
    if cr_pg:
        pr = re.split(r'[-–]', cr_pg)
        if pr and pr[0].isdigit() and pr[0] not in solo_dig:
            d.append(f'paginas: fuente {cr_pg}')
    reg['defectos'] = d
    reg['oa'] = oa(doi)
    ac = reg['oa'].get('pdf') and 'PDF-OA' or (reg['oa'].get('es_oa') and 'OA' or 'cerrado')
    print(f'{i:2}. {"OK     " if not d else "DEFECTO"} {doi:32} [{ac:7}] {tit[:38]}')
    for x in d:
        print(f'          - {x}')
    out.append(reg)
    time.sleep(0.3)

(BASE / 'v2.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
ok = [r for r in out if r.get('estado') == 'verificada' and not r.get('defectos')]
df = [r for r in out if r.get('defectos')]
nv = [r for r in out if r.get('estado') == 'no verificada']
ap = [r for r in out if str(r.get('estado', '')).startswith('no aplica')]
pdf = [r for r in out if (r.get('oa') or {}).get('pdf')]
print(f'\n=== {len(ok)} correctas · {len(df)} con defectos · {len(nv)} no verificadas · '
      f'{len(ap)} a verificar aparte · {len(pdf)} con PDF abierto ===')
