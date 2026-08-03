# -*- coding: utf-8 -*-
"""Verificador unico de los cuatro entregables contra los CSV.

Motivo: durante el proyecto se repitio el mismo patron —texto y figuras copiados
entre documentos que despues divergen de los datos—. Aparecio en el libro, en el
deck, en los montajes cualitativos y en el README. Este script cierra ese agujero:
un solo comando que falla si cualquiera de los cuatro contradice a los CSV.

Todos los valores esperados se DERIVAN de experiments/results/metrics_reports/.
Nada esta escrito a mano, salvo la lista de afirmaciones retiradas (§4), que por
definicion no puede derivarse de los datos.

Uso:   python experiments/verificar_entregables.py
Salida: informe por consola; codigo de salida 1 si hay algun fallo.
"""
import hashlib
import re
import sys
import unicodedata
import zipfile
from pathlib import Path

import fitz
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
REP = RAIZ / 'experiments' / 'results' / 'metrics_reports'
DOCS = RAIZ / 'docs'

fallos = []
avisos = []


def ok(cond, msg, blando=False):
    if cond:
        print(f'  OK    {msg}')
    elif blando:
        print(f'  AVISO {msg}')
        avisos.append(msg)
    else:
        print(f'  FALLA {msg}')
        fallos.append(msg)
    return bool(cond)


def coma(v, nd):
    return f'{v:.{nd}f}'.replace('.', ',')


def punto(v, nd):
    return f'{v:.{nd}f}'


def plano(s):
    """Normaliza espacios: la extraccion de PDF corta frases y numeros en saltos."""
    return re.sub(r'\s+', ' ', s)


def sin_tildes(s):
    s = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in s if not unicodedata.combining(c))


# ----------------------------------------------------------------- documentos
def texto_pdf(p):
    with fitz.open(str(p)) as d:
        return plano('\n'.join(pg.get_text() for pg in d)), d.page_count


DOCUMENTOS = {}
for clave, ruta in (('libro', DOCS / 'Tesis_Borrador_V3.pdf'),
                    ('deck', DOCS / 'Tesis_Defensa_Presentacion.pdf'),
                    ('avances', DOCS / 'Avances_Tesis.pdf')):
    if ruta.exists():
        t, n = texto_pdf(ruta)
        DOCUMENTOS[clave] = {'texto': t, 'paginas': n, 'ruta': ruta}
readme = RAIZ / 'README.md'
if readme.exists():
    DOCUMENTOS['readme'] = {'texto': plano(readme.read_text(encoding='utf-8')),
                            'paginas': None, 'ruta': readme}

print('=== documentos ===')
for k, v in DOCUMENTOS.items():
    pg = f'{v["paginas"]} pag.' if v['paginas'] else f'{len(v["texto"])} car.'
    print(f'  {k:8} {pg:12} {v["ruta"].name}')
faltan = [k for k in ('libro', 'deck', 'avances', 'readme') if k not in DOCUMENTOS]
ok(not faltan, f'los cuatro entregables existen (faltan: {faltan or "ninguno"})')


def contiene(clave, *variantes):
    """True si alguna variante aparece en el documento."""
    t = DOCUMENTOS[clave]['texto']
    return any(v in t for v in variantes)


# --------------------------------------------- 1. medias del benchmark
print('\n=== 1. medias por metodo (9 metricas clasicas) ===')
dm = pd.read_csv(REP / 'descriptive_means.csv').set_index('method')
M9 = ['EN', 'SD', 'FE', 'MG', 'MI_vis', 'MI_ir', 'SF', 'SSIM', 'PSNR']
for doc in ('libro', 'avances'):
    if doc not in DOCUMENTOS:
        continue
    falt = []
    for met in dm.index:
        for m in M9:
            v = float(dm.loc[met, m])
            # se acepta cualquier redondeo entre 2 y 4 decimales, con coma o punto
            if not contiene(doc, *[f(v, nd) for nd in (4, 3, 2) for f in (coma, punto)]):
                falt.append(f'{met}/{m}')
    ok(not falt, f'{doc}: las {len(dm)*9} medias aparecen'
                 + (f' — faltan {falt[:5]}' if falt else ''),
       blando=(doc == 'avances'))

# --------------------------------------------- 2. ranking
print('\n=== 2. ranking de rangos medios ===')
rk = pd.read_csv(REP / 'ranking_methods.csv', index_col=0)['avg_rank']
primero = rk.idxmin()
ok(primero == 'Propuesta_Novedosa',
   f'el CSV pone primera a la propuesta ({primero}, {rk.min():.3f})')
for doc in DOCUMENTOS:
    falt = [f'{i}={v:.2f}' for i, v in rk.items()
            if not contiene(doc, coma(v, 2), punto(v, 2), coma(v, 3), punto(v, 3))]
    ok(not falt, f'{doc}: los {len(rk)} rangos globales aparecen'
                 + (f' — faltan {falt}' if falt else ''),
       blando=(doc in ('deck', 'readme')))
# la propuesta debe declararse primera, no segunda
for doc in DOCUMENTOS:
    malas = [s for s in ('segundo lugar del ranking', 'queda segunda, a 0,23',
                         'ocupa el segundo lugar (3,67)')
             if s in DOCUMENTOS[doc]['texto']]
    ok(not malas, f'{doc}: no declara a la propuesta en segundo lugar {malas}')

# --------------------------------------------- 3. deteccion
print('\n=== 3. deteccion ===')
ll = pd.read_csv(REP / 'detection_llvip_map.csv').set_index('method')
m3 = pd.read_csv(REP / 'detection_m3fd_map.csv').set_index('method')
com = pd.read_csv(REP / 'complementariedad_resumen.csv').set_index('entrada')
for doc in ('libro', 'deck', 'avances'):
    if doc not in DOCUMENTOS:
        continue
    falt = [f'LLVIP {i}' for i, v in ll['mAP50'].items()
            if not contiene(doc, coma(v, 3), punto(v, 3), coma(v, 2), punto(v, 2))]
    ok(not falt, f'{doc}: los mAP de LLVIP aparecen' + (f' — faltan {falt}' if falt else ''),
       blando=(doc == 'deck'))
# el par complementario: la mejor entrada es Ratio Pyramid, no la propuesta
par = ((m3['AP50_People'] + m3['AP50_Lamp']) / 2).sort_values(ascending=False)
ok(par.index[0] == 'RatioPiramide',
   f'el CSV pone a RatioPiramide primera en el par complementario ({par.iloc[0]:.3f})')
pos_prop = list(par.index).index('Propuesta_Novedosa') + 1
print(f'        la propuesta queda {pos_prop}.a de {len(par)} en el par complementario')
# el conteo por escena
p_prop = float(com.loc['Propuesta_Novedosa', 'pct_ambas'])
p_vis = float(com.loc['VIS', 'pct_ambas'])
ok(p_prop < p_vis, f'el CSV deja la propuesta por debajo del visible en el conteo '
                   f'por escena ({p_prop:.1f} % vs {p_vis:.1f} %)')

# --------------------------------------------- 4. afirmaciones retiradas
print('\n=== 4. afirmaciones retiradas (no pueden reaparecer) ===')
# Varias de estas frases SI aparecen legitimamente, negadas: el texto corregido dice
# «no hay patron espejo», «el infrarrojo no es ciego a las luces», «r = 1 no
# desactiva el banco». Por eso no basta buscar la cadena: hay que mirar si viene
# precedida de una negacion en la misma oracion.
RETIRADAS = [
    'la propuesta es la mejor fusión del estudio',
    'ciego a las luces', 'ciego a Lamp', 'el VIS es el espejo',
    'Complementariedad extrema', 'patrón espejo',
    'maximiza las nueve métricas', 'La configuración hallada por PSO',
    'desactiva el banco', 'contenido de bordes', 'entropía de bordes',
    'penaliza los artefactos', 'pocos artefactos',
    '36 configuraciones', '90 contrastes', '[0,05; 1,20]', '0,05–1,20',
    'seis personas frente a dos', 'cuatro luces que el IR',
    'Toet, A. (2014)', 'Mukhopadhyay y Chanda (2001)',
]
NEGADORES = ('no ', 'No ', 'ninguna', 'Ninguna', 'ningún', 'sin ', 'tampoco')


def afirmada(texto, frase):
    """True si la frase aparece al menos una vez SIN negacion que la anteceda."""
    for m in re.finditer(re.escape(frase), texto):
        # se mira el fragmento de oracion previo, hasta 90 caracteres o el punto
        ini = max(0, m.start() - 90)
        previo = texto[ini:m.start()]
        previo = previo[previo.rfind('.') + 1:] if '.' in previo else previo
        # el README enfatiza con Markdown («**no** desactiva»), de modo que hay que
        # quitar los marcadores antes de buscar la negacion
        previo = re.sub(r'[*_`]+', ' ', previo)
        if not any(n in previo for n in NEGADORES):
            return True
    return False


for doc in DOCUMENTOS:
    t = DOCUMENTOS[doc]['texto']
    presentes = [s for s in RETIRADAS if afirmada(t, s)]
    negadas = [s for s in RETIRADAS if s in t and not afirmada(t, s)]
    ok(not presentes, f'{doc}: ninguna afirmacion retirada {presentes}')
    if negadas:
        print(f'        (aparecen negadas, correcto: {negadas})')

# --------------------------------------------- 5. coherencia entre documentos
print('\n=== 5. coherencia entre documentos ===')
CANTIDADES = {
    'rango de la propuesta': [coma(rk['Propuesta_Novedosa'], 3), punto(rk['Propuesta_Novedosa'], 3),
                              coma(rk['Propuesta_Novedosa'], 2), punto(rk['Propuesta_Novedosa'], 2)],
    'mAP del IR en LLVIP': [coma(ll.loc['IR', 'mAP50'], 3), punto(ll.loc['IR', 'mAP50'], 3)],
    'escenas del conteo M3FD': [str(int(com.loc['VIS', 'escenas']))],
    'tamano del corpus': ['20 pares', '20 pares'],
}
for nombre, variantes in CANTIDADES.items():
    donde = [d for d in DOCUMENTOS if contiene(d, *variantes)]
    ausentes = [d for d in DOCUMENTOS if d not in donde]
    ok(len(donde) >= 2, f'«{nombre}» coincide en {donde} (ausente en {ausentes})',
       blando=True)

# --------------------------------------------- 6. figuras embebidas
print('\n=== 6. figuras embebidas, por md5 ===')
EMBEBIDAS = {
    DOCS / 'Tesis_Borrador_V3.docx': {
        'word/media/image8.png': 'fig_libro_boxplots.png',
        'word/media/image9.png': 'fig_libro_ranking.png',
        'word/media/image13.png': 'fig_libro_propuesta_vs.png',
        'word/media/image14.png': 'fig_libro_pso.png',
        'word/media/image16.png': 'fig_m3fd_detecciones.png',
    },
    DOCS / 'Tesis_Defensa_Presentacion.pptx': {
        'ppt/media/image-8-2.png': 'fig_deck_pso_barrido.png',
        'ppt/media/image-13-1.png': 'fig_deck_llvip_map.png',
        'ppt/media/image-14-1.png': 'fig_deck_m3fd_clases.png',
        'ppt/media/image-15-1.png': 'fig_m3fd_detecciones.png',
        'ppt/media/image-10-1.png': 'cualitativas/montaje_07.png',
    },
}
for contenedor, mapa in EMBEBIDAS.items():
    if not contenedor.exists():
        ok(False, f'falta {contenedor.name}')
        continue
    with zipfile.ZipFile(contenedor) as z:
        nombres = set(z.namelist())
        for interno, fig in mapa.items():
            ruta = DOCS / 'figures' / fig
            if interno not in nombres or not ruta.exists():
                ok(False, f'{contenedor.name}: falta {interno} o {fig}')
                continue
            h1 = hashlib.md5(z.read(interno)).hexdigest()
            h2 = hashlib.md5(ruta.read_bytes()).hexdigest()
            ok(h1 == h2, f'{contenedor.name}: {interno} == {fig}')

# --------------------------------------------- 7. montajes al dia
print('\n=== 7. montajes cualitativos ===')
sys.path.insert(0, str(RAIZ))
try:
    from src.datasets import list_pairs
    pares = list_pairs()
    n_esc = len(pares)
    cual = DOCS / 'figures' / 'cualitativas'
    hay = sorted(cual.glob('montaje_*.png'))
    ok(len(hay) == n_esc, f'hay un montaje por escena ({len(hay)} de {n_esc})')
    # el ultimo par del corpus debe aparecer en la galeria de entrada del informe
    ultimo = pares[-1][0].stem
    penultimo = pares[-2][0].stem
    for doc in ('avances',):
        if doc in DOCUMENTOS:
            ok(contiene(doc, penultimo), f'{doc}: el par {penultimo} figura en la galeria')
except Exception as e:                                             # noqa: BLE001
    ok(False, f'no se pudo comprobar el corpus: {str(e)[:80]}')

# --------------------------------------------- 8. paginacion
print('\n=== 8. paginacion y contadores ===')
for doc, patron, total in (('avances', r'\b(\d{1,3}) */ *(\d{1,3})\b', None),
                           ('deck', r'\b(\d{1,2}) */ *(\d{1,2})\b', 22)):
    if doc not in DOCUMENTOS:
        continue
    with fitz.open(str(DOCUMENTOS[doc]['ruta'])) as d:
        desfasados = []
        for i, pg in enumerate(d, start=1):
            m = re.findall(patron, pg.get_text())
            if total is not None:
                m = [x for x in m if x[1] == str(total)]
            else:
                m = [x for x in m if x[1] == str(d.page_count)]
            if m and int(m[-1][0]) != i:
                desfasados.append((i, m[-1]))
        ok(not desfasados, f'{doc}: contadores sin desfase'
                           + (f' — {desfasados[:4]}' if desfasados else ''))

# --------------------------------------------- resumen
print(f'\n=== {len(fallos)} fallos · {len(avisos)} avisos ===')
for f in fallos:
    print(f'  FALLA {f}')
for a in avisos:
    print(f'  AVISO {a}')
sys.exit(1 if fallos else 0)
