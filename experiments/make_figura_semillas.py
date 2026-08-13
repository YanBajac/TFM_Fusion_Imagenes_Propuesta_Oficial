# -*- coding: utf-8 -*-
"""La figura del estudio de semillas: cuanto se mueve cada entrada frente a cuanto las separa.

POR QUE ESTA FIGURA. El resultado del estudio no es un orden, es una comparacion de dos magnitudes:
la dispersion de una misma entrada al cambiar la semilla contra la distancia entre entradas distintas.
Eso en una tabla se lee mal y en un grafico se ve de un golpe, que es justo lo que hace falta cuando
la conclusion es «esto no se distingue».

COMO SE LEE. Cada entrada es una fila. El punto es la media de las cinco semillas, la barra une el
minimo y el maximo, y los puntos chicos son las cinco corridas. Cuando las barras de dos entradas se
superponen, la diferencia entre ellas no se distingue del ruido del entrenamiento.

Estilo sobrio a proposito, en grises, sin colores decorativos y sin cuadricula de fondo: es una figura
de tesis, no de presentacion comercial. La propuesta se marca en negro y el resto en gris, que es la
unica jerarquia que la figura necesita.

Salida: docs/figures/fig_semillas_llvip.png
Uso:    .venv\\Scripts\\python.exe -X utf8 experiments/make_figura_semillas.py
"""
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
os.chdir(RAIZ)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

MR = RAIZ / 'experiments' / 'results' / 'metrics_reports'
SALIDA = RAIZ / 'docs' / 'figures' / 'fig_semillas_llvip.png'
PROP = 'Propuesta_Novedosa'
ROTULO = {
    'VIS': 'Visible solo', 'IR': 'Infrarrojo solo',
    'PiramideLaplace': 'Pirámide de Laplace', 'RatioPiramide': 'Ratio Pyramid',
    'DWT': 'Wavelet discreta', 'DTCWT': 'DTCWT', 'Curvelet': 'CVT (wavelet db4)',
    'TopHat_Clasico': 'Top-Hat clásico', PROP: 'Propuesta',
}
fallos = []


def ok(cond, msg):
    print(f'  {"OK   " if cond else "FALLA"} {msg}')
    if not cond:
        fallos.append(msg)


def main():
    d = pd.read_csv(MR / 'detection_llvip_semillas.csv')
    piv = d.pivot(index='semilla', columns='method', values='mAP50')
    ok(piv.notna().all().all(), f'las {piv.size} celdas (semilla × entrada) estan completas')
    n_sem = piv.shape[0]
    orden = piv.mean().sort_values()                       # de menor a mayor, para leer de abajo
    desv_mediano = float(piv.std().median())

    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    for i, m in enumerate(orden.index):
        vals = piv[m].dropna().values
        es_prop = (m == PROP)
        color = '#1a1a1a' if es_prop else '#8c8c8c'
        ax.plot([vals.min(), vals.max()], [i, i], color=color,
                linewidth=1.1 if es_prop else 0.9, solid_capstyle='butt', zorder=2)
        ax.scatter(vals, [i] * len(vals), s=13, facecolor='white',
                   edgecolor=color, linewidth=0.8, zorder=3)
        ax.scatter([vals.mean()], [i], s=46, color=color, zorder=4)

    ax.set_yticks(range(len(orden)))
    ax.set_yticklabels([ROTULO.get(m, m) + ('  ←' if m == PROP else '')
                        for m in orden.index], fontsize=9)
    for et, m in zip(ax.get_yticklabels(), orden.index):
        if m == PROP:
            et.set_fontweight('bold')
    ax.set_xlabel(f'mAP@0,5 en LLVIP · punto: media de {n_sem} semillas · barra: mínimo a máximo',
                  fontsize=9)
    ax.tick_params(axis='x', labelsize=9)
    # Marcas cada 0,05 fijadas a mano. Con el localizador automatico caian en 0,775, 0,825, 0,875...
    # y el formateador de dos decimales las rotulaba 0,78 · 0,82 · 0,88, que se leen como una escala
    # despareja aunque no lo sea. Se vio en el render.
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.05))
    ax.xaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(0.01))
    ax.xaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _p: f'{v:.2f}'.replace('.', ',')))
    for lado in ('top', 'right', 'left'):
        ax.spines[lado].set_visible(False)
    ax.spines['bottom'].set_linewidth(0.8)
    ax.set_axisbelow(True)
    ax.grid(axis='x', color='#e6e6e6', linewidth=0.6)

    # la vara: el desvio tipico dentro de una entrada, dibujado a escala junto al eje
    x0 = float(piv.min().min()) - 0.004
    ax.annotate('', xy=(x0, -0.75), xytext=(x0 + desv_mediano, -0.75),
                arrowprops=dict(arrowstyle='|-|,widthA=0.35,widthB=0.35',
                                color='#1a1a1a', linewidth=0.8))
    ax.text(x0 + desv_mediano / 2, -1.15,
            f'desvío típico de una misma entrada: {desv_mediano:.4f}'.replace('.', ','),
            ha='center', va='top', fontsize=8, color='#1a1a1a')
    ax.set_ylim(-1.9, len(orden) - 0.4)
    fig.tight_layout()
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SALIDA, dpi=200, facecolor='white')
    plt.close(fig)

    print(f'\n  escrita {SALIDA.relative_to(RAIZ)} '
          f'({SALIDA.stat().st_size / 1000:.0f} kB)')
    print('\n--- controles')
    ok(SALIDA.exists() and SALIDA.stat().st_size > 20000, 'la figura pesa lo de una figura de verdad')
    # el orden dibujado tiene que ser el del CSV, no uno inventado
    ok(list(orden.index) == list(piv.mean().sort_values().index),
       'las filas estan en el orden de las medias calculadas del CSV')
    # y la propuesta tiene que quedar 3.a de las siete fusiones contando de arriba
    FUS = [m for m in orden.index if m not in ('VIS', 'IR')]
    pos = list(reversed(FUS)).index(PROP) + 1
    ok(pos == 3, f'la propuesta queda {pos}.a de las siete fusiones, como dice el analisis')
    print(f'\n=== {len(fallos)} fallos ===')
    return 1 if fallos else 0


if __name__ == '__main__':
    sys.exit(main())
