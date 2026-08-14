"""Verificacion final del libro contra los CSV y contra si mismo."""
import hashlib
import re
import sys
import zipfile
from pathlib import Path

import fitz
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
BASE = RAIZ / 'docs'
REP = RAIZ / 'experiments' / 'results' / 'metrics_reports'
doc = fitz.open(str(BASE / 'Tesis_Borrador_V3.pdf'))
paginas = [p.get_text() for p in doc]
# Se COLAPSAN los espacios y saltos antes de comparar. Diecisiete chequeos de este archivo buscan
# frases literales en el texto, y la extraccion de PDF corta las lineas donde cae el renglon: basta
# que una edicion reflowe un parrafo para que la frase se parta y el chequeo informe un defecto que
# no existe. Paso: al nombrar las seis metricas de la Tabla 7 en lugar de llamarlas «clave», el
# salto de linea cayo entre «global» y «(3,39)» y el control del primer puesto fallo con el libro
# correcto. Nada de este archivo depende de los saltos dentro de txt —el indice se lee de
# paginas[i].splitlines(), aparte—, asi que normalizar aca no debilita ningun otro control.
txt = re.sub(r'\s+', ' ', '\n'.join(paginas))
fallos = []


def ok(cond, msg):
    print(f'  {"OK  " if cond else "FALLA"} {msg}')
    if not cond:
        fallos.append(msg)


print(f'=== documento: {doc.page_count} paginas, {len(txt)} caracteres ===\n')

# ---- 1. cifras obsoletas eliminadas ---------------------------------------
print('--- 1. cifras y textos obsoletos')
OBSOLETOS = ['3,67', '3,44', '6,9888', '1,1045', '0,1477', '17,3435', '0,6677',
             '1,7354', '1,7039', '0,913', '0,957', '22,8554', '6,9334', '0,1387',
             '0,5781', '17,2546', '0,808', '36 configuraciones', '[0,05; 1,20]',
             '0,05–1,20', 'contenido de bordes', 'entropía de bordes',
             '90 contrastes', 'segundo lugar del ranking',
             'ciego a las luces', 'presenta el patrón espejo',
             # «desactiva el banco» salio de esta lista: el libro ahora dice, con razon,
             # que r = 1 NO desactiva el banco, y aca la busqueda es de subcadena y no
             # mira la negacion. El bloque 4 de verificar_entregables.py si la mira, y
             # cubre los cuatro documentos.
             'penaliza los artefactos',
             # --- retirados el 4 de agosto: los tres hallazgos «falso» y los dos
             # pasajes que seguian con la numeracion vieja de tres hipotesis
             '0,739',                              # el SSIM de DTCWT es 0,7249
             'fidelidad estructural y limpieza',   # la propuesta tiene el peor SSIM
             'variante WTH+BTH directa',           # esa variante no existe
             'H3 no se sostiene',                  # §5.8.2 dice «Se sostiene H3»
             'quedan sostenidas H1 y H2',          # H2 se contrasta en §5.8, no en §5.6
             'sostenidas las hipótesis H1 y H2',   # corresponde H1 y H6
             'pso_grid_state.json',                # el estado de la Fo publicada es otro
             'pso_grid_search.csv',                # esa tabla es de la aptitud F_apt
             'pso_grid_search.py']                 # el script es pso_grid_search_fo.py
for v in OBSOLETOS:
    # los numeros se buscan con frontera para no confundir 3,44 con 3,444
    patron = (re.escape(v) + r'(?!\d)') if re.fullmatch(r'[\d,]+', v) else re.escape(v)
    n = len(re.findall(patron, txt))
    ok(n == 0, f'ausente {v!r} (hay {n})')

# ---- 2. medias del benchmark contra descriptive_means.csv ------------------
print('\n--- 2. medias del benchmark (Tablas 4, 5 y 10)')
dm = pd.read_csv(REP / 'descriptive_means.csv').set_index('method')
M9 = ['EN', 'SD', 'FE', 'MG', 'MI_vis', 'MI_ir', 'SF', 'SSIM', 'PSNR']
falt = []
for met in dm.index:
    for m in M9:
        s = f'{dm.loc[met, m]:.4f}'.replace('.', ',')
        if s not in txt:
            falt.append(f'{met}/{m}={s}')
ok(not falt, f'las {len(dm)*9} medias aparecen en el PDF'
             + (f' — faltan {falt[:6]}' if falt else ''))

# ---- 3. rangos contra ranking_methods.csv ---------------------------------
print('\n--- 3. rangos del benchmark (Tabla 7)')
rk = pd.read_csv(REP / 'ranking_methods.csv', index_col=0)
falt = [f'{i}={v:.2f}' for i, v in rk['avg_rank'].items()
        if f'{v:.2f}'.replace('.', ',') not in txt]
ok(not falt, f'los {len(rk)} rangos globales aparecen' +
             (f' — faltan {falt}' if falt else ''))
prim = rk['avg_rank'].idxmin()
ok(prim == 'Propuesta_Novedosa',
   f'la propuesta encabeza el ranking ({prim}, {rk["avg_rank"].min():.3f})')
ok('encabeza el ranking global (3,39)' in txt,
   'la prosa declara el primer lugar de la propuesta')
ok('primer lugar del ranking agregado' in txt or
   'encabeza el ranking agregado' in txt,
   'las conclusiones declaran el primer lugar')

# ---- 4. deteccion --------------------------------------------------------
print('\n--- 4. deteccion (Tablas 8 y 9)')
m3 = pd.read_csv(REP / 'detection_m3fd_map.csv').set_index('method')
# LLVIP se compara contra la MEDIA DE LAS CINCO SEMILLAS, que es lo que el libro publica desde que
# el estudio de repeticiones existe. Antes se comparaba contra detection_llvip_map.csv, la corrida de
# una sola semilla, y al pasar la Tabla 8 a medias este chequeo empezo a reclamar seis cifras que el
# libro ya no imprime —ni debe—: aquel 0,906 de la propuesta era el mas bajo de sus cinco valores.
_sem = REP / 'semillas_llvip_resumen.csv'
if _sem.exists():
    ll = pd.read_csv(_sem, index_col=0).rename(columns={'mAP50_media': 'mAP50'})
    _fuente_ll = f'media de {int(pd.read_csv(REP / "detection_llvip_semillas.csv").semilla.nunique())} semillas'
else:
    ll = pd.read_csv(REP / 'detection_llvip_map.csv').set_index('method')
    _fuente_ll = 'corrida de una semilla'
print(f'    (mAP de LLVIP contra la {_fuente_ll})')
falt = [f'LLVIP {i}={v:.3f}' for i, v in ll['mAP50'].items()
        if f'{v:.3f}'.replace('.', ',') not in txt]
falt += [f'M3FD {i}={v:.3f}' for i, v in m3['mAP50'].items()
         if f'{v:.3f}'.replace('.', ',') not in txt]
ok(not falt, 'los mAP de LLVIP y M3FD aparecen' + (f' — faltan {falt}' if falt else ''))

# ---- 5. seccion 5.8 y sus tablas ------------------------------------------
print('\n--- 5. seccion 5.8 y tablas nuevas')
for s in ['5.8 Auditoría del protocolo de evaluación',
          '5.8.1 Sensibilidad del orden de mérito',
          '5.8.2 Control negativo con degradaciones conocidas',
          '5.8.3 Aporte del banco con hiperparámetros igualados',
          '5.8.4 Robustez frente al ajuste simétrico',
          '5.8.5 Alcance de la optimización y contraste con la tarea',
          'Tabla 12. Control negativo', 'Tabla 13. Ablación del banco',
          'Tabla 14. Rango medio por escenario']:
    ok(txt.count(s) >= 1, f'presente: {s[:58]}')
cn = pd.read_csv(REP / 'control_negativo_ranking.csv')
falt = [f'{r.brazo}={r.rango_9:.3f}' for _, r in cn.iterrows()
        if f'{r.rango_9:.3f}'.replace('.', ',') not in txt]
ok(not falt, f'los {len(cn)} rangos del control negativo aparecen' +
             (f' — faltan {falt}' if falt else ''))

# ---- 6. hipotesis y objetivos ---------------------------------------------
print('\n--- 6. reencuadre')
ok('siete hipótesis de trabajo' in txt, 'declara siete hipotesis')
for h in ['H1:', 'H2:', 'H3:', 'H4:', 'H5:', 'H6:', 'H7:']:
    ok(h in txt, f'enuncia {h}')
ok('Diseñar, implementar y caracterizar un operador' in txt,
   'objetivo general reencuadrado')
ok('ese promedio se suma a la respuesta del disco' in txt,
   'OE1 corrige la combinacion (suma, no maximo)')
ok('Décimo,' in txt, 'las limitaciones llegan al decimo punto')
# El numero de escenas se LEE del CSV que lo calcula, no se escribe aca. Antes este chequeo exigia el
# literal «trece escenas distintas» y con eso bloqueaba una cifra que ningun script producia: agrupar
# los veinte nombres a ojo da 13 o 14 segun como se cuenten las dos tomas de soldier_in_trench, de modo
# que el control estaba fijando una afirmacion sin respaldo. run_escenas_distintas.py fija el criterio
# —la estructura de carpetas del TNO— y lo verifica; si el corpus cambia, ese script falla primero y
# este chequeo pide la palabra nueva.
_PALABRA = {11: 'once', 12: 'doce', 13: 'trece', 14: 'catorce', 15: 'quince', 16: 'dieciséis'}
_esc = REP / 'escenas_distintas.csv'
if _esc.exists():
    _n = int(pd.read_csv(_esc).escena.nunique())
    _pal = _PALABRA.get(_n, str(_n))
    ok(f'{_pal} escenas distintas' in txt,
       f'declara las {_pal} ({_n}) escenas que calcula run_escenas_distintas.py')
else:
    ok(False, 'falta escenas_distintas.csv: correr experiments/run_escenas_distintas.py')
ok('aproximación mediante wavelet 2D' in txt, 'declara la aproximacion del CVT')

# ---- 7. ecuaciones -------------------------------------------------------
print('\n--- 7. ecuaciones')
ok('[0,30; 2,00]' in txt or '0.30' in txt, 'rango de m corregido en el texto')
ok('Δx' in txt and 'Δy' in txt, 'la ecuacion (18) tiene radicando')

# ---- 8. indice coherente con el PDF --------------------------------------
# El indice es texto fijo, no un campo de Word: cualquier insercion lo desfasa en
# silencio. Este chequeo miraba solo las seis entradas de 5.8, y por eso paso
# inadvertido que un parrafo mas largo en §5.3 empujara §5.4 de la 49 a la 50.
# Ahora se comprueban las 79, uniendo los titulos que el indice parte en dos lineas.
print('\n--- 8. indice')
llanas = [re.sub(r'\s+', ' ', p).strip() for p in paginas]
GUIA = re.compile(r'\.{3,}\s*\d{1,3}\s*$', re.M)
espaginas = [i for i, p in enumerate(paginas) if len(GUIA.findall(p)) >= 3]
ok(bool(espaginas), f'el indice ocupa las paginas {[i + 1 for i in espaginas]}')

entradas = []
for i in espaginas:
    resto = ''
    for linea in paginas[i].splitlines():
        linea = linea.strip()
        if not linea:
            continue
        m = re.match(r'^(.*?)\.{2,}\s*(\d{1,3})$', linea)
        if m:
            titulo = re.sub(r'\s+', ' ', f'{resto} {m.group(1)}').strip()
            # la cabecera de la propia pagina del indice no es una entrada
            titulo = re.sub(r'^CONTENIDO\s*', '', titulo).strip(' .')
            entradas.append((titulo, int(m.group(2))))
            resto = ''
        else:
            resto = f'{resto} {linea}'.strip()
ok(len(entradas) >= 70, f'el indice lista {len(entradas)} entradas')

cuerpo = [(i, t) for i, t in enumerate(llanas) if i not in espaginas]
desfasadas = []
for titulo, pag in entradas:
    fis = next((i for i, t in cuerpo if titulo and titulo in t), None)
    if fis is None or fis + 1 != pag:
        desfasadas.append(f'«{titulo[:46]}» dice {pag}, real '
                          f'{fis + 1 if fis is not None else "no hallado"}')
ok(not desfasadas, f'las {len(entradas)} entradas apuntan a su pagina real'
                   + (f' — {desfasadas[:6]}' if desfasadas else ''))

# ---- 9. figuras embebidas identicas a las del repositorio -----------------
# Las cuatro figuras de datos del libro vivian solo dentro del docx y quedaron
# con cifras de corridas anteriores: la del ranking llego a mostrar la piramide
# de Laplace primera, contradiciendo el texto. Este chequeo compara byte a byte.
print('\n--- 9. figuras embebidas')
EMBEBIDAS = {
    'word/media/image8.png': 'fig_libro_boxplots.png',        # Figura 7
    'word/media/image9.png': 'fig_libro_ranking.png',         # Figura 8
    'word/media/image13.png': 'fig_libro_propuesta_vs.png',   # Figura 10
    'word/media/image14.png': 'fig_libro_pso.png',            # Figura 11
    'word/media/image16.png': 'fig_m3fd_detecciones.png',     # Figura 9
}
docx = BASE / 'Tesis_Borrador_V3.docx'
if not docx.exists():
    ok(False, f'no encuentro {docx.name} para revisar las figuras')
else:
    with zipfile.ZipFile(docx) as z:
        nombres = set(z.namelist())
        for interno, fig in EMBEBIDAS.items():
            ruta = RAIZ / 'docs' / 'figures' / fig
            if interno not in nombres:
                ok(False, f'{interno} no esta en el docx')
            elif not ruta.exists():
                ok(False, f'falta docs/figures/{fig}')
            else:
                h1 = hashlib.md5(z.read(interno)).hexdigest()
                h2 = hashlib.md5(ruta.read_bytes()).hexdigest()
                ok(h1 == h2, f'{interno} == docs/figures/{fig}')

# ---- el RESUMEN y el SUMMARY tienen que decir lo mismo -------------------
# POR QUE. El libro lleva su resumen dos veces, en español y en ingles, y son dos textos separados que
# hay que editar los dos. Cuando LLVIP paso a cinco semillas se corrigio el español —«la propuesta
# alcanza 0,9283 y queda 3.a de siete»— y el ingles quedo con las cifras de la corrida unica: «the
# proposal falls at the lower end of the fusion band (0.906)». El libro se contradecia entre su resumen
# y su abstract, y el abstract se contradecia consigo mismo, porque ya declaraba las cinco semillas y
# despues daba el valor de una. Nada lo detectaba: los dos parrafos son texto libre y ningun chequeo los
# comparaba entre si.
# COMO. Se extraen los mAP de los dos parrafos —el español con coma, el ingles con punto— y se exige
# que sean el MISMO conjunto y que cada uno sea una media del estudio de semillas. Compararlos entre si
# no alcanzaria: los dos podrian estar viejos a la vez.
print('\n=== el resumen y el abstract dan las mismas cifras de LLVIP ===')
_sem_res = REP / 'semillas_llvip_resumen.csv' if 'REP' in dir() else None
_p_sem = BASE.parent / 'experiments' / 'results' / 'metrics_reports' / 'semillas_llvip_resumen.csv'
if _p_sem.exists():
    import pandas as _pd
    _sm = _pd.read_csv(_p_sem, index_col=0)
    _validos = set()
    for _c in ('mAP50_media', 'mAP50_95_media'):
        for _v in _sm[_c]:
            _validos |= {f'{_v:.3f}', f'{_v:.4f}'}
    _desv = {f'{_v:.4f}' for _v in _sm.mAP50_desv} | {f'{_sm.mAP50_desv.median():.4f}'}

    from docx import Document as _Doc
    _d = _Doc(str(BASE / 'Tesis_Borrador_V3.docx'))
    _res = next((p.text for p in _d.paragraphs if p.text.strip().startswith('El presente trabajo')
                 or 'reentrenamiento de un detector' in p.text), '')
    _sum = next((p.text for p in _d.paragraphs if 'retraining a detector' in p.text), '')
    ok(bool(_res) and bool(_sum), 'se encontraron el resumen y el abstract')

    def _maps(t, sep):
        """Los mAP del pasaje de LLVIP: entre «LLVIP» y «M3FD», que es donde estan."""
        _i, _j = t.find('LLVIP'), t.find('M3FD')
        _frag = t[_i:_j] if 0 <= _i < _j else t
        return {x.replace(sep, '.') for x in re.findall(r'0[' + re.escape(sep) + r']\d{3,4}', _frag)}

    _m_es, _m_en = _maps(_res, ','), _maps(_sum, '.')
    ok(_m_es == _m_en,
       f'los {len(_m_es)} mAP del resumen son los mismos del abstract'
       + (f' — solo en español {sorted(_m_es - _m_en)} · solo en ingles {sorted(_m_en - _m_es)}'
          if _m_es != _m_en else ''))
    _viejos = sorted((_m_es | _m_en) - _validos - _desv)
    ok(not _viejos, 'y todos son medias vigentes del estudio de semillas'
                    + (f' — RETIRADOS: {_viejos}' if _viejos else ''))
else:
    print('  AVISO no esta semillas_llvip_resumen.csv: resumen y abstract sin comparar')

# ---- resumen -------------------------------------------------------------
print(f'\n=== {len(fallos)} fallos ===')
for f in fallos:
    print(f'   {f}')
sys.exit(1 if fallos else 0)
