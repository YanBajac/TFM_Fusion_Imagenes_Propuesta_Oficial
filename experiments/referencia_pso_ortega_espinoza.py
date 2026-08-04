# -*- coding: utf-8 -*-
"""Extrae a CSV las 125 corridas del PSO del trabajo de referencia.

Motivo: la justificacion del peso m = 0,30 de esta tesis se apoya en un contraste con
Ortega y Espinoza (2025), que usa el MISMO rango publicado y la MISMA funcion de aptitud
pero con un disco unico como elemento estructurante. Ese contraste necesita sus cifras, y
citarlas a mano es el patron que ya costo caro en este proyecto. Este script las lee de
los anexos del PDF de referencia y las deja en un CSV, de modo que toda afirmacion sobre
su barrido sea reproducible y auditable.

Los anexos publican, por cada una de sus cinco escenas, las 25 combinaciones de particulas
e iteraciones con la configuracion optima hallada: (r, m) y las metricas resultantes. La
extraccion se valida con la identidad de la propia aptitud, Fo = SSIM_avg + E_n + PSNR_n,
que en sus tablas ya vienen normalizadas: si el mapeo de columnas estuviera corrido, la
identidad no cerraria en ninguna fila.

Uso:   .venv\\Scripts\\python.exe -X utf8 experiments/referencia_pso_ortega_espinoza.py
Salida: experiments/results/metrics_reports/referencia_pso_ortega_espinoza.csv
"""
import re
import sys
from pathlib import Path

import fitz
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PDF = RAIZ / 'docs' / 'fuentes' / 'Libro___Fusion_de_Imagenes___FPUNA__PSO_2.pdf'
SALIDA = RAIZ / 'experiments' / 'results' / 'metrics_reports' / 'referencia_pso_ortega_espinoza.csv'

COLS = ['particulas', 'iteraciones', 'r', 'm', 'SSIM_avg', 'E_n', 'SF', 'SD', 'PSNR_n', 'Fo']
CABECERA = ('Part. Iter.', 'r', 'm', 'SSIM avg', 'E', 'SF', 'SD', 'PSNR', 'FO')
PARTICULAS = {2, 4, 6, 8, 10}
ITERACIONES = {10, 20, 30, 40, 50}


def escenas_de(doc):
    """Devuelve {escena: pagina} leyendo los rotulos «Anexo N: Resultados para X»."""
    fuera = {}
    for i, pg in enumerate(doc):
        m = re.search(r'Anexo\s+\d+:\s*Resultados para\s+(.+)', pg.get_text())
        if m:
            fuera[m.group(1).strip()] = i
    return fuera


def filas_de(pagina, n_filas=25):
    """Los numeros que siguen a la cabecera, agrupados de a diez.

    Se tokeniza en lugar de leer por lineas porque la extraccion no es uniforme: casi
    todas las celdas salen en su propia linea, pero al menos una fila viene colapsada en
    una sola. Despues de la tabla queda el numero de pagina, de modo que se toman
    exactamente las 25 x 10 primeras cifras y no todo lo que haya.
    """
    texto = pagina.get_text()
    corte = texto.find(CABECERA[-1])
    if corte < 0:
        return []
    numeros = [float(t) for t in re.findall(r'-?\d+(?:\.\d+)?', texto[corte + len(CABECERA[-1]):])]
    esperados = n_filas * len(COLS)
    if len(numeros) < esperados:
        return []
    numeros = numeros[:esperados]
    return [numeros[k:k + len(COLS)] for k in range(0, esperados, len(COLS))]


def main():
    if not PDF.exists():
        print(f'falta {PDF}')
        return 1
    doc = fitz.open(str(PDF))
    paginas = escenas_de(doc)
    if not paginas:
        print('no se hallaron los anexos en el PDF')
        return 1

    marcos = []
    for escena, pag in paginas.items():
        filas = filas_de(doc[pag])
        d = pd.DataFrame(filas, columns=COLS)
        d.insert(0, 'escena', escena)
        marcos.append(d)
        print(f'  {escena:12s} pagina {pag + 1:3d}  {len(d):3d} corridas')
    tabla = pd.concat(marcos, ignore_index=True)
    tabla[['particulas', 'iteraciones', 'r']] = tabla[['particulas', 'iteraciones', 'r']].astype(int)

    # --- validacion: la identidad de la aptitud tiene que cerrar en TODAS las filas
    error = (tabla.Fo - (tabla.SSIM_avg + tabla.E_n + tabla.PSNR_n)).abs()
    assert error.max() < 1e-5, f'el mapeo de columnas no cierra: error maximo {error.max():.2e}'
    # --- y la rejilla de enjambre tiene que estar completa en cada escena
    for escena, g in tabla.groupby('escena'):
        assert len(g) == 25, f'{escena}: {len(g)} corridas, deben ser 25'
        assert set(g.particulas) == PARTICULAS, f'{escena}: particulas {sorted(set(g.particulas))}'
        assert set(g.iteraciones) == ITERACIONES, f'{escena}: iteraciones {sorted(set(g.iteraciones))}'
        assert len(set(zip(g.particulas, g.iteraciones))) == 25, f'{escena}: la rejilla se repite'
    # --- y los dos parametros, dentro del rango que el propio trabajo declara
    assert tabla.r.between(1, 25).all(), 'hay un radio fuera de [1, 25]'
    assert tabla.m.between(0.30, 2.00).all(), 'hay un peso fuera de [0,30; 2,00]'

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(SALIDA, index=False)

    print(f'\n{len(tabla)} corridas · identidad de la aptitud verificada '
          f'(error maximo {error.max():.2e})')
    print(f'\npeso m por escena:')
    for escena, g in tabla.groupby('escena'):
        piso = int((g.m - 0.30).abs().lt(5e-3).sum())
        print(f'  {escena:12s} mediana {g.m.median():.3f}  [{g.m.min():.3f}, {g.m.max():.3f}]'
              f'  en el piso 0,30: {piso:2d} de 25')
    piso = int((tabla.m - 0.30).abs().lt(5e-3).sum())
    print(f'  TOTAL        mediana {tabla.m.median():.3f}  '
          f'[{tabla.m.min():.3f}, {tabla.m.max():.3f}]  en el piso: {piso} de {len(tabla)}')
    print(f'\nradio: r = 25 (la cota superior) en {int((tabla.r == 25).sum())} de {len(tabla)} '
          f'corridas; r = 1 en {int((tabla.r == 1).sum())}')
    print(f'\n-> {SALIDA.relative_to(RAIZ)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
