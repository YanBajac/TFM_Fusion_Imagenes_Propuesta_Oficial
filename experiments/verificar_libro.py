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
txt = '\n'.join(paginas)
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
             '90 contrastes', 'desactiva el banco', 'segundo lugar del ranking',
             'ciego a las luces', 'presenta el patrón espejo',
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
ll = pd.read_csv(REP / 'detection_llvip_map.csv').set_index('method')
m3 = pd.read_csv(REP / 'detection_m3fd_map.csv').set_index('method')
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
ok('trece escenas distintas' in txt, 'declara las trece escenas del corpus')
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

# ---- resumen -------------------------------------------------------------
print(f'\n=== {len(fallos)} fallos ===')
for f in fallos:
    print(f'   {f}')
sys.exit(1 if fallos else 0)
