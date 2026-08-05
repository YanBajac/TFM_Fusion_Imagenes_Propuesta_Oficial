# -*- coding: utf-8 -*-
"""Diagrama de la arquitectura del detector, extraido del checkpoint entrenado.

Pedido del orientador: graficar la arquitectura. El diagrama NO se dibuja de memoria ni se
copia de la documentacion de la biblioteca: se lee el grafo del modelo entrenado de este
trabajo —los 23 modulos del Sequential con sus indices de origen, canales, nucleos y pasos— y
se dibuja eso. Si el modelo cambiara, el diagrama cambia con el.

La resolucion de cada nivel se deduce de los pasos acumulados desde la entrada, de modo que
las etiquetas 80x80, 40x40 y 20x20 no son un supuesto sino el producto de los Conv con
paso 2 que el grafo declara.

Salida: docs/figures/fig_arquitectura_yolo.png
        experiments/results/metrics_reports/arquitectura_yolo.json (el grafo leido)
Uso:    .venv\\Scripts\\python.exe -X utf8 experiments/make_figura_arquitectura_yolo.py
"""
import json
import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')
RAIZ = Path(__file__).resolve().parent.parent
os.chdir(RAIZ)
sys.path.insert(0, '.')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

SALIDA = Path('docs/figures/fig_arquitectura_yolo.png')
JSON_OUT = Path('experiments/results/metrics_reports/arquitectura_yolo.json')
GRIS, GRIS_C, AZUL, GRANATE = '#f2f2f2', '#d9d9d9', '#4472c4', '#c00000'
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman']})


def leer_grafo(pesos):
    from ultralytics import YOLO
    m = YOLO(pesos)
    capas, res = [], None
    imgsz = 640
    actual = imgsz
    for i, l in enumerate(m.model.model):
        t = type(l).__name__
        d = {'i': i, 'tipo': t, 'from': getattr(l, 'f', -1)}
        if hasattr(l, 'conv'):                       # Conv simple
            d['cin'], d['cout'] = l.conv.in_channels, l.conv.out_channels
            d['k'], d['s'] = l.conv.kernel_size[0], l.conv.stride[0]
            if d['s'] == 2:
                actual //= 2
        elif hasattr(l, 'cv1') and hasattr(l, 'cv2'):  # C2f, SPPF
            d['cin'] = l.cv1.conv.in_channels
            d['cout'] = l.cv2.conv.out_channels
            d['s'] = 1
        elif t == 'Upsample':
            actual *= 2
            d['s'] = 1
        d['res'] = actual
        if t == 'Detect':
            d['clases'] = len(m.model.names)
        capas.append(d)
    return capas, {
        'parametros': int(sum(p.numel() for p in m.model.parameters())),
        'clases': list(m.model.names.values()), 'imgsz': imgsz,
        'checkpoint': os.path.relpath(pesos, RAIZ).replace('\\', '/')}


def caja(ax, x, y, w, h, txt, sub='', fill=GRIS, borde='#555555', lw=0.9, fs=7.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.008,rounding_size=0.02',
                                facecolor=fill, edgecolor=borde, linewidth=lw, zorder=3))
    ax.text(x + w / 2, y + h * (0.62 if sub else 0.5), txt, ha='center', va='center',
            fontsize=fs, zorder=4)
    if sub:
        ax.text(x + w / 2, y + h * 0.26, sub, ha='center', va='center', fontsize=fs - 1.3,
                color='#444444', zorder=4)


def flecha(ax, p0, p1, color='#555555', lw=0.9, estilo='-', rad=0.0):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle='-|>', mutation_scale=8,
                                 color=color, linewidth=lw, linestyle=estilo,
                                 connectionstyle=f'arc3,rad={rad}', zorder=2,
                                 shrinkA=1, shrinkB=1))


def main():
    cands = sorted(Path('.').glob('runs/**/mixto/weights/best.pt'),
                   key=lambda p: p.stat().st_mtime)
    if not cands:
        print('no hay best.pt del mixto')
        return 1
    capas, meta = leer_grafo(str(cands[-1]))
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps({'meta': meta, 'capas': capas}, indent=1), encoding='utf-8')

    col = [c for c in capas if c['i'] <= 9]
    cue = [c for c in capas if 10 <= c['i'] <= 21]
    det = capas[-1]
    por = {c['i']: c for c in capas}

    fig, ax = plt.subplots(figsize=(12.6, 5.6))
    ax.set_xlim(0, 100); ax.set_ylim(0, 62); ax.axis('off')
    W, H = 8.2, 6.4
    xs_col = [3 + k * 9.6 for k in range(len(col))]
    Y_COL, Y_TD, Y_BU, Y_HEAD = 47, 32, 17, 4

    # ------------------------------------------------------------------ columna
    ax.text(1, Y_COL + H + 3.4, 'Columna (backbone) — extrae los rasgos', fontsize=9,
            fontweight='bold')
    caja(ax, 0.4, Y_COL + 1.2, 2.2, H - 2.4, 'VIS+IR', f'{meta["imgsz"]}²', fill='white')
    ant = (2.6, Y_COL + H / 2)
    for x, c in zip(xs_col, col):
        et = c['tipo'] if c['tipo'] != 'Conv' else f"Conv s{c['s']}"
        sub = (f"{c.get('cin','')}→{c.get('cout','')} · {c['res']}²"
               if 'cout' in c else f"{c['res']}²")
        es_tap = c['i'] in (4, 6, 9)
        caja(ax, x, Y_COL, W, H, f"{c['i']}. {et}", sub,
             fill=GRIS_C if es_tap else GRIS, lw=1.5 if es_tap else 0.9)
        flecha(ax, ant, (x, Y_COL + H / 2))
        ant = (x + W, Y_COL + H / 2)

    # ---------------------------------------------------- cuello: las dos bandas en orden
    # Se dibujan de izquierda a derecha en el orden del grafo: intentar reflejar el sentido
    # «descendente» con el trazado hacia la izquierda superponia las cajas y hacia falta leer
    # dos direcciones distintas en la misma figura.
    ax.text(1, Y_TD + H + 2.6, 'Cuello (neck) — pirámide de rasgos: camino descendente',
            fontsize=9, fontweight='bold')
    ax.text(1, Y_BU + H + 2.6, 'Cuello (neck) — camino ascendente', fontsize=9,
            fontweight='bold')
    pos = {}
    RANURAS = [3 + k * 16 for k in range(6)]

    def banda(indices, y):
        ant = None
        for idx, x in zip(indices, RANURAS):
            c = por[idx]
            if c['tipo'] == 'Concat':
                et, sub = f'{idx}. Concat', f"con la capa {c['from'][1]}"
            elif c['tipo'] == 'Upsample':
                et, sub = f'{idx}. Upsample', f"×2 · {c['res']}²"
            else:
                et = f"{idx}. {c['tipo']}" + (f" s{c['s']}" if c['tipo'] == 'Conv' else '')
                sub = f"{c['cin']}→{c['cout']} · {c['res']}²"
            salida = idx in det['from']
            caja(ax, x, y, W, H, et, sub, fill=GRIS_C if salida else GRIS,
                 lw=1.5 if salida else 0.9)
            pos[idx] = (x, y)
            if ant is not None:
                flecha(ax, (ant + W, y + H / 2), (x, y + H / 2))
            ant = x

    banda([10, 11, 12, 13, 14, 15], Y_TD)
    banda([16, 17, 18, 19, 20, 21], Y_BU)

    # del SPPF al primer Upsample, y del final del descendente al primer Conv del ascendente
    flecha(ax, (xs_col[9] + W / 2, Y_COL), (pos[10][0] + W / 2, Y_TD + H))
    flecha(ax, (pos[15][0] + W / 2, Y_TD), (pos[16][0] + W / 2, Y_BU + H))

    # los atajos entre escalas, que son lo que hace la piramide
    for icc in (11, 14, 17, 20):
        src = por[icc]['from'][1]
        p0 = ((xs_col[src] + W / 2, Y_COL) if src <= 9
              else (pos[src][0] + W / 2, pos[src][1]))
        flecha(ax, p0, (pos[icc][0] + W / 2, pos[icc][1] + H), color=AZUL, estilo='--',
               rad=0.18)

    # ------------------------------------------------------------------ cabezal
    ax.text(1, Y_HEAD + H + 2.6, 'Cabezal (head) — desacoplado y sin cajas ancla',
            fontsize=9, fontweight='bold')
    xs_h = [8, 40, 72]
    for idx, xh in zip(det['from'], xs_h):
        r = por[idx]['res']
        caja(ax, xh, Y_HEAD, 20, H, f'Detect · nivel {r}² (capa {idx})',
             f"clasificación + caja (DFL) · {det['clases']} clases", fill='white',
             borde=GRANATE, lw=1.4)
        flecha(ax, (pos[idx][0] + W / 2, pos[idx][1]), (xh + 10, Y_HEAD + H),
               color=GRANATE, rad=0.12)

    ax.text(99, 1.2, f"{meta['parametros']:,}".replace(',', '.') + ' parámetros · '
            f"medido sobre {meta['checkpoint']}", ha='right', fontsize=6.8, color='#666666')
    ax.plot([0.6, 99.4], [Y_COL - 4.2] * 2, color='#cccccc', lw=0.7)
    ax.plot([0.6, 99.4], [Y_BU - 4.2] * 2, color='#cccccc', lw=0.7)
    ax.text(99, Y_COL + H + 3.4, 'línea continua: flujo secuencial · línea azul punteada: '
            'atajo entre escalas', ha='right', fontsize=6.8, color='#666666')

    fig.tight_layout(pad=0.3)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SALIDA, dpi=180, facecolor='white')
    plt.close(fig)
    print(f'{len(capas)} capas leidas del checkpoint · {meta["parametros"]:,} parametros')
    print(f'-> {SALIDA}')
    print(f'-> {JSON_OUT}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
