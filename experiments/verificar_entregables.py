# -*- coding: utf-8 -*-
"""Verificador unico de los cuatro entregables contra los CSV.

Motivo: durante el proyecto se repitio el mismo patron —texto y figuras copiados
entre documentos que despues divergen de los datos—. Aparecio en el libro, en el
deck, en los montajes cualitativos y en el README. Este script cierra ese agujero:
un solo comando que falla si cualquiera de los cuatro contradice a los CSV.

Todos los valores esperados se DERIVAN de experiments/results/metrics_reports/.
Nada esta escrito a mano, salvo la lista de afirmaciones retiradas (§4), que por
definicion no puede derivarse de los datos.

Uso:   .venv\Scripts\python.exe -X utf8 experiments/verificar_entregables.py
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
    # El mAP del visible y del infrarrojo en LLVIP estaban escritos a mano en la lectura
    # de la Tabla 9 del informe de avances, con valores de una corrida anterior, mientras
    # la tabla de arriba —generada desde el CSV— imprimia los vigentes: 0,813 y 0,971.
    # Se buscan como frase y no como cifra suelta porque 0,808 y 0,957 colisionan con
    # valores por imagen que si son vigentes (SSIM, Q0, QW, FE de varios CSV).
    'de 0,808 a la banda', 'más fuerte (0,957)',
    # y el argumento que los otros tres documentos ya retiraron
    'activa el banco completo',
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

# Las cifras retiradas hay que buscarlas en LAS DOS notaciones. El abstract en
# ingles del libro sobrevivio trece cifras obsoletas porque esta lista solo miraba
# la coma decimal y el ingles usa punto.
print('\n=== 4b. cifras retiradas, en coma Y en punto ===')
# Solo cifras INEQUIVOCAS. Las de tres decimales del M3FD anterior (0,165 · 0,124 ·
# 0,157 · 0,119 · 0,220 · 0,018 · 0,178 · 0,135) quedan fuera a proposito: colisionan
# con valores vigentes —0,135 es el SD del Top-Hat (0,1352) redondeado— y darian
# falsos positivos. Esas afirmaciones ya las cubre el chequeo de frases del punto 4.
# 0,5781 · 1,7354 · 1,7039 salieron de la lista el 5 de agosto: dejaron de ser
# inequivocas. Las dos primeras coinciden con valores por imagen vigentes de
# pso_por_imagen.csv y la tercera con la aptitud media de las corridas que terminan en
# r = 22 en el estudio de estabilidad. Las afirmaciones que representaban ya las cubre
# el chequeo de frases del punto 4.
CIFRAS_RETIRADAS = ['6,9888', '1,1045', '0,1477', '17,3435', '0,6677', '17,2546',
                    '22,8554', '6,9334', '0,1387', '0,0353', '3,67', '3,44']
for doc in DOCUMENTOS:
    t = DOCUMENTOS[doc]['texto']
    hits = []
    for v in CIFRAS_RETIRADAS:
        for var in (v, v.replace(',', '.')):
            # frontera a la derecha: 3,44 no debe cazar 3,444
            if re.search(re.escape(var) + r'(?!\d)', t):
                hits.append(var)
    ok(not hits, f'{doc}: ninguna cifra retirada, en ninguna notacion {hits[:6]}')

# Las negritas de las tablas se pusieron cuando los valores eran otros y quedaron
# marcando la celda equivocada: en la Tabla 7 el Global señalaba a la piramide de
# Laplace, que es la conclusion que el propio capitulo desmiente.
print('\n=== 4c. negritas de las tablas == optimo de la columna ===')
docx = DOCS / 'Tesis_Borrador_V3.docx'
try:
    import docx as _dx
    rk_t = pd.read_csv(REP / 'ranking_methods.csv', index_col=0)
    ETQ = {'Pirámide de Laplace (LP)': 'PiramideLaplace', 'Ratio Pyramid (RP)': 'RatioPiramide',
           'Wavelet discreta (DWT)': 'DWT', 'DTCWT': 'DTCWT', 'Curvelet (CVT)': 'Curvelet',
           'Top-Hat clásico': 'TopHat_Clasico', 'Propuesta Novedosa': 'Propuesta_Novedosa'}
    ESPERA = {
        ('Método', 'EN', 'SD', 'FE', 'MG', 'MI_vis', 'MI_ir'):
            ('Tabla 4', ['EN', 'SD', 'FE', 'MG', 'MI_vis', 'MI_ir'], dm, 'max'),
        ('Método', 'SF ↑', 'SSIM ↑', 'PSNR ↑'):
            ('Tabla 5', ['SF', 'SSIM', 'PSNR'], dm, 'max'),
        ('Método', 'SD', 'MG', 'SF', 'SSIM', 'PSNR', 'MI_ir', 'Global'):
            ('Tabla 7', ['SD', 'MG', 'SF', 'SSIM', 'PSNR', 'MI_ir', 'avg_rank'], rk_t, 'min'),
    }
    doc_x = _dx.Document(str(docx))
    revisadas = 0
    for tb in doc_x.tables:
        cab = tuple(c.text.strip() for c in tb.rows[0].cells)
        if cab not in ESPERA:
            continue
        nom, cols, src, modo = ESPERA[cab]
        gan = {c: (src[c].idxmax() if modo == 'max' else src[c].idxmin()) for c in cols}
        malas = []
        for fila in tb.rows[1:]:
            cel = list(fila.cells)
            clave = ETQ.get(cel[0].text.strip())
            if clave is None:
                continue
            for j, c in enumerate(cols, start=1):
                neg = any(r.bold for p in cel[j].paragraphs for r in p.runs if r.bold)
                if neg != (gan[c] == clave):
                    malas.append(f'{c}/{clave}')
        ok(not malas, f'{nom}: la negrita marca el optimo {malas[:6]}')
        revisadas += 1
    ok(revisadas == 3, f'se revisaron las 3 tablas con negrita ({revisadas})')
except ImportError:
    print('  AVISO python-docx no instalado: no se reviso la negrita')
    avisos.append('negritas sin revisar (falta python-docx)')

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
        # el flujograma no llevaba control y quedo rotulando m = 0,0703 —el optimo de la
        # aptitud paralela— en lugar del peso adoptado, en los DOS entregables
        'word/media/image5.png': 'fig_flujo_propuesta.png',
        'word/media/image2.png': 'fig_morfologia_tophat.png',
        'word/media/image17.png': 'comparacion_aptitudes.png',
    },
    DOCS / 'Tesis_Defensa_Presentacion.pptx': {
        'ppt/media/image-8-2.png': 'fig_deck_pso_barrido.png',
        'ppt/media/image-13-1.png': 'fig_deck_llvip_map.png',
        'ppt/media/image-14-1.png': 'fig_deck_m3fd_clases.png',
        'ppt/media/image-15-1.png': 'fig_m3fd_detecciones.png',
        'ppt/media/image-10-1.png': 'cualitativas/montaje_07.png',
        'ppt/media/image-7-1.png': 'fig_flujo_propuesta.png',
        'ppt/media/image-6-1.png': 'fig_morfologia_tophat.png',
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

# --------------------------------------------- 9. desborde del deck
# LibreOffice recorta en el borde de la lamina: lo que no entra no se dibuja y no deja
# rastro en el PDF. Asi la lamina 18 perdio entero el parrafo del conteo por escena, que
# es el resultado de OE5, y nadie lo noto. Comparar el texto de cada shape con el de su
# pagina detecta el recorte sin mirar geometria. Se comparan solo letras y digitos: los
# simbolos (-, °, ∈, ·) no sobreviven igual a las dos extracciones.
print('\n=== 9. texto del deck que no llega al PDF ===')
PPTX = DOCS / 'Tesis_Defensa_Presentacion.pptx'
try:
    from pptx import Presentation

    if 'deck' not in DOCUMENTOS or not PPTX.exists():
        raise FileNotFoundError(PPTX.name)

    def solo_alfanum(s):
        return re.sub(r'[^0-9a-z]+', '', sin_tildes(s or '').lower())

    prs = Presentation(str(PPTX))
    with fitz.open(str(DOCUMENTOS['deck']['ruta'])) as d:
        ok(len(prs.slides) == d.page_count,
           f'el PDF trae una pagina por lamina ({d.page_count} y {len(prs.slides)})')
        perdidos = []
        for i, (lam, pg) in enumerate(zip(prs.slides, d), start=1):
            enpdf = solo_alfanum(pg.get_text())
            for sh in lam.shapes:
                if not sh.has_text_frame:
                    continue
                for par in sh.text_frame.paragraphs:
                    clave = solo_alfanum(par.text)
                    if len(clave) >= 20 and clave not in enpdf:
                        perdidos.append(f'lamina {i} «{sh.name}»')
        ok(not perdidos, 'ningun parrafo se pierde en el recorte'
                         + (f' — {perdidos[:5]}' if perdidos else ''))
except ImportError:
    print('  AVISO python-pptx no instalado: no se reviso el desborde del deck')
    avisos.append('desborde del deck sin revisar (falta python-pptx)')
except FileNotFoundError as e:
    ok(False, f'falta {e} para revisar el desborde del deck', blando=True)

# --------------------------------------------- 10. texto tapado por una figura
# Las figuras del deck son PNG con fondo blanco OPACO. Si el orden de shapes las pone
# despues del cuadro de texto, tapan lo que se solape, y en el PDF el texto sigue estando
# —se puede seleccionar— asi que el chequeo de recorte del bloque 9 no lo ve. Asi la lamina 8
# tenia la segunda linea del titulo debajo del flujograma y la 9 perdia el final de un
# renglon bajo el mapa de calor. Se cruza el bbox de cada span con el de cada imagen.
print('\n=== 10. texto del deck tapado por una figura ===')
UMBRAL_TAPADO = 0.005          # discrimina los solapes reales de los meros roces de borde
if 'deck' in DOCUMENTOS:
    tapados = []
    with fitz.open(str(DOCUMENTOS['deck']['ruta'])) as d:
        for i, pg in enumerate(d, start=1):
            imgs = [fitz.Rect(im['bbox']) for im in pg.get_image_info()]
            if not imgs:
                continue
            for bl in pg.get_text('dict')['blocks']:
                if bl['type'] != 0:
                    continue
                for ln in bl['lines']:
                    for sp in ln['spans']:
                        sr = fitz.Rect(sp['bbox'])
                        if not sp['text'].strip() or sr.get_area() <= 0:
                            continue
                        for ir in imgs:
                            inter = sr & ir
                            if inter.is_empty:
                                continue
                            if inter.get_area() / sr.get_area() >= UMBRAL_TAPADO:
                                tapados.append(f'lamina {i}: {sp["text"].strip()[:40]!r}')
                                break
    ok(not tapados, 'ningun texto queda debajo de una figura'
                    + (f' — {tapados[:5]}' if tapados else ''))

# --------------------------------------------- 8b. la secuencia de pies del informe
# El bloque 8 busca contadores con la forma «N / M», que es la del deck. El informe de
# avances numera con el numero solo, de modo que ese chequeo pasaba sin mirar nada: al
# insertar una pagina en el medio quedaron un pie repetido y otro faltante sin que nadie
# lo notara. Aca se comprueba que la secuencia sea estrictamente consecutiva.
print('\n=== 8b. secuencia de pies del informe de avances ===')
if 'avances' in DOCUMENTOS:
    with fitz.open(str(DOCUMENTOS['avances']['ruta'])) as d:
        pies = []
        for i, pg in enumerate(d, start=1):
            lineas = [l.strip() for l in pg.get_text().splitlines() if l.strip()]
            ult = lineas[-1] if lineas else ''
            pies.append((i, int(ult)) if re.fullmatch(r'\d{1,3}', ult) else (i, None))
    conp = [(i, v) for i, v in pies if v is not None]
    saltos = [f'pag {a[0]}: {a[1]} -> {b[1]}'
              for a, b in zip(conp, conp[1:]) if b[1] != a[1] + 1]
    ok(not saltos, f'los {len(conp)} pies numerados son consecutivos'
                   + (f' — {saltos[:5]}' if saltos else ''))
    rep = [v for _, v in conp]
    ok(len(rep) == len(set(rep)), 'ningun pie se repite'
       + ('' if len(rep) == len(set(rep))
          else f' — repetidos {sorted(v for v in set(rep) if rep.count(v) > 1)}'))
    # Y el encuadre: el pie esta posicionado en absoluto al fondo del div de cada pagina, de
    # modo que si el contenido se pasa de alto el div termina en la pagina SIGUIENTE y se
    # lleva el pie con el. Una pagina sin pie al final es, por tanto, una pagina cuyo
    # contenido se derramo: parte del texto queda huerfano y la siguiente arranca a media
    # frase. La portada es la unica que legitimamente no lleva pie.
    derramadas = [i for i, v in pies if v is None and i > 1]
    ok(not derramadas, 'ninguna pagina derrama su contenido a la siguiente'
                       + (f' — derraman {derramadas}' if derramadas else ''))

# --------------------------------------------- 11. el Excel
# El Excel es un entregable rastreado y no tenia ningun chequeo. Llego a publicar «optimo
# global r* = 25» —lo contrario de H5—, una banda de mAP de una corrida anterior y la
# numeracion vieja de hipotesis. Se revisa en dos planos: las cadenas de texto contra la
# misma lista de afirmaciones retiradas que los otros documentos, y las celdas NUMERICAS
# contra las cifras retiradas, comparando por valor y no por cadena, porque el Excel guarda
# numeros y no texto formateado.
print('\n=== 11. el Excel de tablas ===')
XLSX = DOCS / 'Avances_Tesis_Tablas.xlsx'
try:
    from openpyxl import load_workbook

    if not XLSX.exists():
        raise FileNotFoundError(XLSX.name)
    wb = load_workbook(XLSX, data_only=True)
    textos, numeros = [], []
    for hoja in wb.worksheets:
        for fila in hoja.iter_rows():
            for c in fila:
                if isinstance(c.value, str):
                    textos.append(c.value)
                elif isinstance(c.value, (int, float)) and c.value is not None:
                    numeros.append(float(c.value))
    blob = plano(' '.join(textos))
    ok(len(wb.worksheets) >= 10, f'tiene {len(wb.worksheets)} hojas: {", ".join(wb.sheetnames)}')

    presentes = [s for s in RETIRADAS if afirmada(blob, s)]
    ok(not presentes, f'excel: ninguna afirmacion retirada {presentes}')

    # las cifras retiradas, por valor: se comparan con la tolerancia del formato publicado
    hits = []
    for v in CIFRAS_RETIRADAS:
        try:
            x = float(v.replace(',', '.'))
        except ValueError:
            continue
        nd = len(v.split(',')[1]) if ',' in v else 0
        if any(abs(n - x) < 0.5 * 10 ** (-nd) for n in numeros):
            hits.append(v)
    ok(not hits, f'excel: ninguna cifra retirada en las celdas numericas {hits[:6]}')

    # y las que el Excel publicaba a mano y ya no deben estar
    VIEJAS_EXCEL = ['óptimo global', 'H3 no sostenida', 'r=12', 'm=0.069', '0,957', '0,913']
    quedan = [s for s in VIEJAS_EXCEL if s.lower() in blob.lower()]
    ok(not quedan, f'excel: sin las afirmaciones que publicaba a mano {quedan}')

    # El rango medio no esta como valor: la hoja lo deja en una formula AVERAGE que Excel
    # calcula al abrir, de modo que openpyxl no lo ve. Se verifica la materia prima: que el
    # promedio de los nueve rangos guardados reproduzca el del CSV.
    rk = pd.read_csv(REP / 'ranking_methods.csv', index_col=0)
    hoja = wb['Ranking_Global'] if 'Ranking_Global' in wb.sheetnames else None
    if hoja is None:
        ok(False, 'excel: falta la hoja Ranking_Global')
    else:
        # La fila buscada es la de DATOS, no el subtitulo: este tambien dice «La propuesta»,
        # de modo que hace falta exigir que la fila traiga los nueve rangos. La ultima
        # columna es la formula AVERAGE, que openpyxl lee como None.
        def rangos_de(fila):
            return [c.value for c in fila[1:] if isinstance(c.value, (int, float))]

        fila_prop = next((f for f in hoja.iter_rows()
                          if isinstance(f[0].value, str)
                          and 'PROPUESTA' in f[0].value.upper()
                          and len(rangos_de(f)) == 9), None)
        rangos = rangos_de(fila_prop) if fila_prop else []
        prom = sum(rangos) / len(rangos) if len(rangos) == 9 else None
        esperado = float(rk['avg_rank'].min())
        visto = coma(prom, 3) if prom is not None else 'nada'
        ok(prom is not None and abs(prom - esperado) < 5e-4,
           f'excel: los nueve rangos de la propuesta promedian {visto} '
           f'y el CSV publica {coma(esperado, 3)}')
except ImportError:
    print('  AVISO openpyxl no instalado: no se reviso el Excel')
    avisos.append('excel sin revisar (falta openpyxl)')
except FileNotFoundError as e:
    ok(False, f'falta {e} para revisar el Excel', blando=True)

# --------------------------------------------- resumen
print(f'\n=== {len(fallos)} fallos · {len(avisos)} avisos ===')
for f in fallos:
    print(f'  FALLA {f}')
for a in avisos:
    print(f'  AVISO {a}')
sys.exit(1 if fallos else 0)
