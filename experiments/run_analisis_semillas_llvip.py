# -*- coding: utf-8 -*-
"""Que diferencias de mAP sobreviven a la semilla, y cuales no.

LA PREGUNTA. El trabajo entrena un detector por entrada con UNA sola semilla, y sus siete fusiones se
apilan en centesimas: la menor distancia entre dos consecutivas es 0,0001. Con una corrida por entrada
no hay forma de separar el orden entre ellas del ruido de inicializacion, y el informe lo declara. Con
cinco semillas si se puede responder, y la respuesta es lo que hay que reportar: no «cual gana», sino
CUALES DIFERENCIAS SON DISTINGUIBLES.

COMO SE COMPARA. Las cinco semillas son las mismas para las nueve entradas, asi que las comparaciones
van PAREADAS POR SEMILLA: cada semilla es un bloque y lo que se compara dentro del bloque son las nueve
entradas entrenadas con esa misma inicializacion. Eso quita del medio la variacion entre semillas, que
es comun a todas las entradas, y es el mismo razonamiento por el que el resto del trabajo rankea dentro
de cada par de imagenes en lugar de promediar y despues rankear.

QUE SE REPORTA
  1. media, desvio y recorrido de cada entrada sobre las semillas: cuanto se mueve una misma entrada
     solo por cambiar la inicializacion. Es la vara con la que hay que leer cualquier diferencia.
  2. Friedman sobre los bloques de semilla: hay alguna diferencia entre las nueve entradas?
  3. todas las comparaciones pareadas contra el infrarrojo solo y contra el visible solo, que son las
     dos afirmaciones que el trabajo hace, con Wilcoxon de rangos con signo y correccion de Holm.
  4. las comparaciones entre las siete FUSIONES: cuantas son distinguibles. Con cinco bloques el
     Wilcoxon pareado tiene un p minimo alcanzable de 1/16 = 0,0625, de modo que NINGUNA comparacion
     individual puede dar significativa al 5 % ni en el mejor caso. Eso no es un defecto del analisis:
     es la resolucion que dan cinco semillas, y hay que decirlo asi en lugar de presentar un orden.
  5. cuantas diferencias observadas son menores que el desvio dentro de la propia entrada, que es la
     forma practica de decir «esto no se distingue».

Salida: experiments/results/metrics_reports/semillas_llvip_resumen.csv
        experiments/results/metrics_reports/semillas_llvip_pareadas.csv
Uso:    .venv\\Scripts\\python.exe -X utf8 experiments/run_analisis_semillas_llvip.py
"""
import itertools
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
os.chdir(RAIZ)

import pandas as pd
from scipy.stats import friedmanchisquare, wilcoxon

MR = RAIZ / 'experiments' / 'results' / 'metrics_reports'
ENTRADA = MR / 'detection_llvip_semillas.csv'
RES_OUT = MR / 'semillas_llvip_resumen.csv'
PAR_OUT = MR / 'semillas_llvip_pareadas.csv'
FUSIONES = ['PiramideLaplace', 'RatioPiramide', 'DWT', 'DTCWT', 'Curvelet',
            'TopHat_Clasico', 'Propuesta_Novedosa']
fallos = []


def ok(cond, msg):
    print(f'  {"OK   " if cond else "FALLA"} {msg}')
    if not cond:
        fallos.append(msg)


def holm(pares):
    """Correccion de Holm. Devuelve {clave: p_ajustado}."""
    orden = sorted(pares.items(), key=lambda kv: kv[1])
    n, out, corrido = len(orden), {}, 0.0
    for i, (k, p) in enumerate(orden):
        corrido = max(corrido, min(1.0, p * (n - i)))
        out[k] = corrido
    return out


def main():
    if not ENTRADA.exists():
        print(f'todavia no existe {ENTRADA.name}: correr primero '
              f'experiments/detection_llvip/run_semillas_llvip.py')
        return 1
    d = pd.read_csv(ENTRADA)
    piv = d.pivot(index='semilla', columns='method', values='mAP50')
    piv95 = d.pivot(index='semilla', columns='method', values='mAP50_95')
    print(f'--- {len(d)} corridas · {piv.shape[0]} semillas × {piv.shape[1]} entradas')
    completas = [c for c in piv.columns if piv[c].notna().all()]
    if len(completas) < piv.shape[1]:
        print(f'    AVISO: incompletas {sorted(set(piv.columns) - set(completas))}; '
              f'se analizan las {len(completas)} completas')
    piv, piv95 = piv[completas], piv95[completas]
    n_sem = piv.shape[0]

    # ---------------------------------------------------------------- 1. cuanto se mueve cada entrada
    res = pd.DataFrame({
        'n_semillas': piv.notna().sum(),
        'mAP50_media': piv.mean().round(4), 'mAP50_desv': piv.std().round(4),
        'mAP50_min': piv.min().round(4), 'mAP50_max': piv.max().round(4),
        'mAP50_recorrido': (piv.max() - piv.min()).round(4),
        'mAP50_95_media': piv95.mean().round(4), 'mAP50_95_desv': piv95.std().round(4),
    }).sort_values('mAP50_media', ascending=False)
    print('\n--- 1. cuanto se mueve una misma entrada al cambiar solo la semilla')
    print(res.to_string())
    desv_tipica = float(res.mAP50_desv.median())
    print(f'\n    desvio mediano dentro de una entrada: {desv_tipica:.4f} de mAP50')
    print(f'    recorrido mediano: {float(res.mAP50_recorrido.median()):.4f}')

    # ---------------------------------------------------------------- 2. Friedman por bloques
    print('\n--- 2. Friedman con las semillas como bloques')
    if n_sem >= 3 and len(completas) >= 3:
        chi2, p = friedmanchisquare(*[piv[c].values for c in completas])
        print(f'    chi2 = {chi2:.4f} · p = {p:.6f} · '
              f'{"hay diferencias entre las entradas" if p < 0.05 else "no se detectan diferencias"}')
    else:
        chi2 = p = float('nan')
        print('    hacen falta al menos tres semillas y tres entradas')

    # ---------------------------------------------------------------- 3 y 4. pareadas
    print('\n--- 3. las dos afirmaciones del trabajo, pareadas por semilla')
    filas, brutos = [], {}
    for a, b in itertools.combinations(completas, 2):
        dif = piv[a] - piv[b]
        try:
            _w, pw = wilcoxon(piv[a], piv[b])
        except ValueError:
            pw = 1.0
        clave = f'{a} vs {b}'
        brutos[clave] = float(pw)
        filas.append({'a': a, 'b': b, 'media_a': round(float(piv[a].mean()), 4),
                      'media_b': round(float(piv[b].mean()), 4),
                      'dif_media': round(float(dif.mean()), 4),
                      'gana_a_en': int((dif > 0).sum()), 'de': int(dif.notna().sum()),
                      'p_wilcoxon': round(float(pw), 4)})
    aj = holm(brutos)
    par = pd.DataFrame(filas)
    par['p_holm'] = [round(aj[f'{r.a} vs {r.b}'], 4) for r in par.itertuples()]
    par['sig_holm'] = par.p_holm < 0.05
    par['mayor_que_el_ruido'] = par.dif_media.abs() > desv_tipica

    for mod in ('IR', 'VIS'):
        if mod not in completas:
            continue
        sub = par[(par.a == mod) | (par.b == mod)].copy()
        sub['contra'] = sub.apply(lambda r: r.b if r.a == mod else r.a, axis=1)
        sub['dif_a_favor_de_' + mod] = sub.apply(
            lambda r: r.dif_media if r.a == mod else -r.dif_media, axis=1)
        print(f'\n    {mod} solo, contra cada fusion:')
        print(sub[['contra', f'dif_a_favor_de_{mod}', 'p_wilcoxon', 'p_holm',
                   'mayor_que_el_ruido']].to_string(index=False))

    print('\n--- 4. entre las siete fusiones: cuantas diferencias son distinguibles')
    fus = par[par.a.isin(FUSIONES) & par.b.isin(FUSIONES)]
    p_min = 2 ** -(n_sem - 1) if n_sem >= 2 else 1.0
    print(f'    {len(fus)} comparaciones · con {n_sem} bloques el p minimo alcanzable por el '
          f'Wilcoxon pareado es {p_min:.4f}')
    print(f'    significativas tras Holm: {int(fus.sig_holm.sum())}')
    print(f'    con diferencia mayor que el desvio dentro de la entrada '
          f'({desv_tipica:.4f}): {int(fus.mayor_que_el_ruido.sum())} de {len(fus)}')
    if int(fus.mayor_que_el_ruido.sum()):
        print(fus[fus.mayor_que_el_ruido][['a', 'b', 'dif_media', 'gana_a_en', 'de']]
              .to_string(index=False))

    # ---------------------------------------------------------------- controles
    print('\n--- controles')
    ok(piv.notna().all().all(), 'no falta ninguna celda (semilla × entrada) entre las completas')
    if 'VIS' in completas:
        peor_fus = min((c for c in completas if c in FUSIONES), key=lambda c: piv[c].mean())
        brecha = float(piv[peor_fus].mean() - piv['VIS'].mean())
        ok(brecha > 0, f'toda fusion supera al visible solo en media: la mas floja es {peor_fus} '
                       f'y le saca {brecha:+.4f}')
    if 'IR' in completas:
        mejor_fus = max((c for c in completas if c in FUSIONES), key=lambda c: piv[c].mean())
        d_ir = float(piv['IR'].mean() - piv[mejor_fus].mean())
        ok(d_ir > 0, f'el infrarrojo solo sigue por encima de la mejor fusion ({mejor_fus}) '
                     f'por {d_ir:+.4f}')
    ok(desv_tipica > 0, f'el desvio dentro de una entrada no es cero ({desv_tipica:.4f}): '
                        f'si lo fuera, las corridas no serian independientes')

    res.to_csv(RES_OUT)
    par.to_csv(PAR_OUT, index=False)
    print(f'\nescritos: {RES_OUT.name} y {PAR_OUT.name}')
    print(f'\n=== {len(fallos)} fallos ===')
    return 1 if fallos else 0


if __name__ == '__main__':
    sys.exit(main())
