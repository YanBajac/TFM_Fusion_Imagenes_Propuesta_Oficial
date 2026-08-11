# -*- coding: utf-8 -*-
"""Correlaciona el orden de CALIDAD de las siete fusiones con su UTILIDAD en deteccion.

POR QUE EXISTE. El deck de defensa proyecta, en la lamina del contraste de hipotesis, un
«rho = +0,214 (p = 0,645)» como evidencia de que el orden de calidad no predice el mAP. Ese numero
NO LO CALCULABA NINGUN SCRIPT del repositorio: vivia solamente en documentos de texto —el plan del
deck y dos documentos archivados—, y uno de ellos lo declara como pendiente de versionar
(«E5 ... pendientes de versionar como scripts»). Una cifra sin generador es una cifra que nadie
puede rehacer: si cambian el corpus, las metricas o el entrenamiento del detector, sigue impresa
igual. Ya paso en este proyecto con tres figuras que rotulaban un peso que la tesis no adopta.

Este script es ese generador. Recalcula la correlacion desde los mismos CSV que alimentan el resto
del informe, para que la cifra del deck se pueda cotejar y rehacer.

QUE CALCULA. Para cada combinacion de
  - conjunto de metricas de calidad: las nueve reportadas, las nueve sin FE (que es EN reescalada,
    de modo que no es una dimension independiente) y las diecisiete que el evaluador calcula;
  - medida de deteccion: mAP@0,5 y mAP@0,5:0,95, en LLVIP y en M3FD,
la correlacion de Spearman y la de Kendall entre el rango medio de calidad de las siete fusiones y
su medida de deteccion.

COMO SE LEE EL SIGNO. En rango medio, MENOR ES MEJOR calidad; en mAP, MAYOR ES MEJOR deteccion. Si
la calidad predijera la utilidad, la correlacion seria NEGATIVA. Un rho positivo apunta en la
direccion contraria a la esperada. El script deja el signo esperado escrito en el CSV para que no
haya que recordarlo al leerlo.

QUE NO HACE. No compara contra VIS ni IR solos: la correlacion es sobre el orden de las FUSIONES,
que es lo que la hipotesis afirma. El contraste contra la mejor modalidad individual es otro, y lo
hace el conteo por escena de McNemar.

Salida: experiments/results/metrics_reports/correlacion_calidad_deteccion.csv
Uso:    .venv\\Scripts\\python.exe -X utf8 experiments/run_correlacion_calidad_deteccion.py
"""
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))

import pandas as pd
from scipy.stats import spearmanr, kendalltau

# Se importa con el mismo alias que usa el generador del informe (linea 1512), para que las dos
# rutas de calculo lean literalmente el mismo diccionario de direcciones.
from src.metrics.evaluators import METRIC_DIRECTION as DIRECTION_TODAS

MR = RAIZ / 'experiments' / 'results' / 'metrics_reports'
SALIDA = MR / 'correlacion_calidad_deteccion.csv'

PROP = 'Propuesta_Novedosa'
# Las nueve que el informe reporta, en el orden en que las publica.
NUEVE = ['EN', 'SD', 'FE', 'MG', 'MI_vis', 'MI_ir', 'SF', 'SSIM', 'PSNR']
# FE es la entropia reescalada por una constante por escena: da rangos identicos a EN y el mismo
# chi2 de Friedman, asi que no agrega una dimension. Se ofrece el conjunto sin ella.
SIN_FE = [m for m in NUEVE if m != 'FE']


def rango_medio(allm, metricas):
    """Rango medio de cada metodo: se rankea DENTRO de cada imagen y despues se promedia.

    Es el mismo procedimiento que usa el informe (ranking_methods.csv y el _rk17 del generador):
    rankear intra-imagen y no sobre las medias, para que una escena de escala distinta no domine.
    La direccion de cada metrica sale de src/metrics/evaluators.py, no de una lista a mano.
    """
    por_metrica = {}
    for m in metricas:
        piv = allm.pivot(index='image', columns='method', values=m)
        # ascending=True cuando menor es mejor: asi el rango 1 es siempre el mejor valor
        por_metrica[m] = piv.rank(axis=1, ascending=(DIRECTION_TODAS[m] == 'min'),
                                  method='average').mean(axis=0)
    return pd.DataFrame(por_metrica).mean(axis=1)


def main():
    allm = pd.read_csv(MR / 'all_metrics.csv')
    diecisiete = [c for c in allm.columns if c in DIRECTION_TODAS]
    print(f'corpus: {allm.image.nunique()} imagenes · {allm.method.nunique()} entradas')
    print(f'metricas disponibles con direccion declarada: {len(diecisiete)} '
          f'{sorted(diecisiete)}\n')

    CONJUNTOS = {
        'nueve': NUEVE,
        'nueve_sin_FE': SIN_FE,
        'diecisiete': diecisiete,
    }
    rangos = {}
    for nombre, mets in CONJUNTOS.items():
        faltan = [m for m in mets if m not in allm.columns]
        if faltan:
            raise SystemExit(f'ABORTA: al conjunto «{nombre}» le faltan columnas: {faltan}')
        rangos[nombre] = rango_medio(allm, mets)
        orden = rangos[nombre].sort_values()
        pos = list(orden.index).index(PROP) + 1
        print(f'--- rango medio con {nombre} ({len(mets)} metricas)')
        print('    ' + ' · '.join(f'{k} {v:.3f}' for k, v in orden.items()))
        print(f'    la propuesta queda {pos}.a de {len(orden)} con '
              f'{orden[PROP]:.3f}; lidera {orden.index[0]} con {orden.iloc[0]:.3f}\n')

    DET = {}
    for etiq, arch in (('LLVIP', 'detection_llvip_map.csv'), ('M3FD', 'detection_m3fd_map.csv')):
        d = pd.read_csv(MR / arch).set_index('method')
        DET[etiq] = d
        print(f'--- deteccion en {etiq}: {len(d)} entradas')

    filas = []
    for cj, rg in rangos.items():
        # solo las FUSIONES: la hipotesis habla del orden entre metodos de fusion
        fusiones = [m for m in rg.index if m not in ('VIS', 'IR')]
        for etiq, d in DET.items():
            for medida in ('mAP50', 'mAP50_95'):
                comunes = [m for m in fusiones if m in d.index]
                if len(comunes) < 3:
                    continue
                x = [float(rg[m]) for m in comunes]          # rango de calidad: menor es mejor
                y = [float(d.loc[m, medida]) for m in comunes]  # mAP: mayor es mejor
                rho, p_rho = spearmanr(x, y)
                tau, p_tau = kendalltau(x, y)
                filas.append({
                    'conjunto_metricas': cj,
                    'n_metricas': len(CONJUNTOS[cj]),
                    'dataset': etiq,
                    'medida_deteccion': medida,
                    'n_fusiones': len(comunes),
                    'spearman_rho': round(float(rho), 4),
                    'spearman_p': round(float(p_rho), 4),
                    'kendall_tau': round(float(tau), 4),
                    'kendall_p': round(float(p_tau), 4),
                    'signo_esperado': 'negativo',
                    'signo_observado': 'negativo' if rho < 0 else 'positivo',
                    'apunta_como_se_esperaba': bool(rho < 0),
                    'significativo_05': bool(p_rho < 0.05),
                })

    res = pd.DataFrame(filas)
    # Multiplicidad: son doce contrastes sobre los mismos siete metodos, asi que un p nominal de
    # 0,05 no es 0,05. Bonferroni es conservador y aca alcanza para lo unico que hay que decidir:
    # si algun hallazgo sobrevive a haber mirado doce veces.
    res['p_bonferroni'] = (res.spearman_p * len(res)).clip(upper=1.0).round(4)
    res['sobrevive_multiplicidad'] = res.p_bonferroni < 0.05
    print('\n' + '=' * 78)
    print(res.to_string(index=False))

    # ---------------------------------------------------------------- controles
    fallos = []

    def ok(cond, msg):
        print(f'  {"OK   " if cond else "FALLA"} {msg}')
        if not cond:
            fallos.append(msg)

    print('\n--- controles')
    # 1. El control que importa es sobre LAS NUEVE METRICAS REPORTADAS, que son las que sostienen
    #    la hipotesis: si ahi no hay asociacion, el orden de calidad publicado no predice utilidad.
    #    La primera version de este control exigia que NINGUNA de las doce fuera significativa, y
    #    era una suposicion mia, no un hecho: con las diecisiete metricas sobre M3FD el mAP@0,5:0,95
    #    SI correlaciona, fuerte y en la direccion esperada. Ese hallazgo no se tapa, se reporta.
    _n9 = res[res.conjunto_metricas == 'nueve']
    ok(not _n9.significativo_05.any(),
       f'con las nueve metricas reportadas, ninguno de los {len(_n9)} contrastes es significativo'
       + ('' if not _n9.significativo_05.any()
          else f' — {_n9[_n9.significativo_05][["dataset", "medida_deteccion"]].to_dict("records")}'))
    # 2. y ningun hallazgo de los doce sobrevive a la correccion por multiplicidad, de modo que
    #    nada de esto se puede presentar como una asociacion establecida
    ok(not res.sobrevive_multiplicidad.any(),
       f'ninguno de los {len(res)} contrastes sobrevive a Bonferroni'
       + ('' if not res.sobrevive_multiplicidad.any()
          else f' — {res[res.sobrevive_multiplicidad].to_dict("records")}'))
    # 3. lo que si hay que dejar dicho, porque es un hallazgo y no un control
    _nom = res[res.significativo_05]
    if len(_nom):
        print(f'\n  HALLAZGO, no fallo: {len(_nom)} de {len(res)} contrastes alcanzan '
              f'significancia NOMINAL, todos con el conjunto ampliado:')
        for _r in _nom.itertuples():
            print(f'    {_r.conjunto_metricas} · {_r.dataset} · {_r.medida_deteccion}: '
                  f'rho = {_r.spearman_rho:+.4f}, p = {_r.spearman_p:.4f} '
                  f'(Bonferroni {_r.p_bonferroni:.4f}), signo {_r.signo_observado}')
        print('    Lectura: la bateria de nueve no predice la utilidad y la ampliada apunta a que\n'
              '    si, en la direccion esperada. Va en la misma linea que el control negativo, donde\n'
              '    el brazo de ruido es 3.o de 14 con nueve metricas y ultimo con diecisiete. Con\n'
              '    siete metodos y doce contrastes no alcanza para afirmarlo: es una pista, no un\n'
              '    resultado, y hay que decirlo asi.\n')
    # 2. el rango medio con las nueve tiene que coincidir con el CSV ya publicado
    rk = pd.read_csv(MR / 'ranking_methods.csv').rename(columns={'Unnamed: 0': 'metodo'})
    pub = rk.set_index('metodo')['avg_rank']
    mio = rangos['nueve'].round(3)
    dif = {k: (float(pub[k]), float(mio[k])) for k in pub.index
           if abs(float(pub[k]) - float(mio[k])) > 0.0015}
    ok(not dif, 'el rango medio recalculado con las nueve coincide con ranking_methods.csv'
                + (f' — difiere en {dif}' if dif else ''))
    # 3. y sin FE tambien, que es la otra columna publicada
    pub2 = rk.set_index('metodo')['avg_rank_sin_FE']
    mio2 = rangos['nueve_sin_FE'].round(3)
    dif2 = {k: (float(pub2[k]), float(mio2[k])) for k in pub2.index
            if abs(float(pub2[k]) - float(mio2[k])) > 0.0015}
    ok(not dif2, 'el rango sin FE coincide con avg_rank_sin_FE'
                 + (f' — difiere en {dif2}' if dif2 else ''))
    # 4. Spearman sobre rangos es invariante al signo de la escala: si se invierte el rango
    #    (de menor-es-mejor a mayor-es-mejor), rho tiene que cambiar de signo y nada mas
    _r = rangos['nueve']
    _f = [m for m in _r.index if m not in ('VIS', 'IR')]
    _x = [float(_r[m]) for m in _f]
    _y = [float(DET['LLVIP'].loc[m, 'mAP50']) for m in _f]
    _a, _ = spearmanr(_x, _y)
    _b, _ = spearmanr([-v for v in _x], _y)
    ok(abs(_a + _b) < 1e-12, 'invertir la escala del rango invierte rho y nada mas')

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(SALIDA, index=False)
    print(f'\nescrito: {SALIDA.relative_to(RAIZ)}  ({len(res)} filas)')
    print(f'\n=== {len(fallos)} fallos ===')
    return 1 if fallos else 0


if __name__ == '__main__':
    sys.exit(main())
