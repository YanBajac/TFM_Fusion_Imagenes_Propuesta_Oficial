# -*- coding: utf-8 -*-
"""Corre la metodologia de Ortega y Espinoza (2025) EN SU PUNTO DE OPERACION sobre los 20 pares.

POR QUE FALTABA. El benchmark tiene un brazo llamado «TopHat_Clasico», y es facil creer que ese brazo
es la metodologia de referencia. No lo es: es tophat_classic_fusion(r=5, m=1), el Top-Hat clasico
GENERICO. La metodologia de la referencia usa el mismo operador de disco unico pero en un punto de
operacion distinto, el que su propio PSO elige. Resultado: la tesis se compara con un clasico generico
y con ese mismo operador puesto en los hiperparametros de la propuesta (control_tophat_igual_peso.csv),
pero NUNCA con el punto de operacion de la metodologia que toma como referencia. Es la primera cosa que
una mesa va a preguntar.

CUAL ES SU PUNTO DE OPERACION. Sale de sus 125 corridas publicadas —5 escenas x 25 configuraciones de
enjambre—, que estan en referencia_pso_ortega_espinoza.csv. No se escribe a mano: se lee del CSV.
  - el radio: la moda y la mediana de las 125 son r = 25, y el argmax de SU aptitud da r = 25 en cuatro
    de sus cinco escenas (24 en la restante). El radio no esta en discusion.
  - el peso: la mediana de las 125 es m = 0,695, que es la cifra que el libro ya cita al caracterizar su
    metodo. La mediana de los cinco optimos por escena es 0,622. Se corre el punto principal con la
    mediana de las 125 y el otro como SENSIBILIDAD, para que la conclusion no dependa de como se agrega.

QUE NO HACE ESTE SCRIPT. No toca all_metrics.csv ni el benchmark de siete metodos. El benchmark de siete
es lo que replica el protocolo de la referencia, y meterle un octavo brazo recalcularia todos los rangos
medios, el Friedman, los Wilcoxon con Holm, el control negativo de catorce entradas, la ablacion y los
dos experimentos de deteccion —incluidas las 45 corridas de LLVIP—. Esto escribe su propio CSV y su
propio ranking, declarados aparte, que es como el trabajo ya trata el ranking con Nabf, el control a
peso igualado y el ajuste simetrico.

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/run_metodologia_referencia.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.datasets import list_pairs, load_pair
from src.fusion import tophat_classic_fusion
from src.metrics import evaluate_all
# El diccionario se llama METRIC_DIRECTION en el modulo; el generador del informe lo
# importa con el mismo alias, asi que la direccion de cada metrica es UNA sola fuente.
from src.metrics.evaluators import METRIC_DIRECTION as DIRECTION_TODAS

MR = ROOT / 'experiments' / 'results' / 'metrics_reports'
REF_CSV = MR / 'referencia_pso_ortega_espinoza.csv'
SALIDA = MR / 'metodologia_referencia.csv'
RANKING = MR / 'metodologia_referencia_ranking.csv'
PROP_KEY = 'Propuesta_Novedosa'
NUEVE = ['EN', 'SD', 'FE', 'MG', 'MI_vis', 'MI_ir', 'SF', 'SSIM', 'PSNR']


def punto_de_operacion():
    """El (r, m) de la referencia, leido de sus 125 corridas publicadas."""
    d = pd.read_csv(REF_CSV)
    r_moda = int(d.r.mode().iloc[0])
    m_med = float(d.m.median())
    mejores = d.loc[d.groupby('escena').Fo.idxmax()]
    m_med_opt = float(mejores.m.median())
    return {
        'r': r_moda,
        'm_principal': m_med,
        'm_sensibilidad': m_med_opt,
        'n_corridas': len(d),
        'n_escenas': int(d.escena.nunique()),
        'r_en_optimos': f"{int((mejores.r == r_moda).sum())} de {len(mejores)}",
    }


def correr(pares, r, m, clave):
    filas = []
    for vis_p, ir_p in pares:
        vis, ir = load_pair(vis_p, ir_p)
        fus = tophat_classic_fusion(vis, ir, r=r, m=m)
        met = evaluate_all(fus, vis, ir)
        filas.append({'method': clave, 'image': Path(str(vis_p)).stem, **met})
    return pd.DataFrame(filas)


def rangos(df, mets):
    """Rango medio intra-par, con la misma convencion que run_stats_analysis.py."""
    out = {}
    for m in mets:
        piv = df.pivot(index='image', columns='method', values=m)
        out[m] = piv.rank(axis=1, ascending=(DIRECTION_TODAS.get(m) == 'min'),
                          method='average').mean(axis=0)
    return pd.DataFrame(out).mean(axis=1).sort_values()


def main():
    op = punto_de_operacion()
    print(f'--- punto de operacion de la referencia, de sus {op["n_corridas"]} corridas '
          f'({op["n_escenas"]} escenas)')
    print(f'    r = {op["r"]}  (moda y mediana; es el argmax de su aptitud en {op["r_en_optimos"]} '
          f'de sus escenas)')
    print(f'    m = {op["m_principal"]:.3f}  (mediana de las {op["n_corridas"]})')
    print(f'    sensibilidad: m = {op["m_sensibilidad"]:.3f}  (mediana de sus cinco optimos por escena)')

    pares = list_pairs()
    if not pares:
        print('  no se encontraron pares VIS/IR')
        return 1
    print(f'\n--- corriendo sobre {len(pares)} pares')

    CLAVE = 'Referencia_OyE'
    CLAVE_S = 'Referencia_OyE_m0622'
    d1 = correr(pares, op['r'], op['m_principal'], CLAVE)
    print(f'    {CLAVE}: {len(d1)} filas')
    d2 = correr(pares, op['r'], op['m_sensibilidad'], CLAVE_S)
    print(f'    {CLAVE_S}: {len(d2)} filas')
    todo = pd.concat([d1, d2], ignore_index=True)
    todo.insert(2, 'r', op['r'])
    todo.insert(3, 'm', [op['m_principal']] * len(d1) + [op['m_sensibilidad']] * len(d2))
    todo.to_csv(SALIDA, index=False)
    print(f'\n    -> {SALIDA.relative_to(ROOT)}')

    # El ranking de OCHO: los siete del benchmark mas la referencia en su punto de operacion. Va en su
    # propio archivo: el de siete no se toca, porque es el que replica el protocolo de la referencia.
    allm = pd.read_csv(MR / 'all_metrics.csv')
    comunes = [c for c in allm.columns if c not in ('method', 'image')]
    ocho = pd.concat([allm, d1[['method', 'image'] + comunes]], ignore_index=True)
    r9 = rangos(ocho, NUEVE)
    diecisiete = [c for c in comunes if c in DIRECTION_TODAS]
    r17 = rangos(ocho, diecisiete)
    rk = pd.DataFrame({'rango_9': r9, 'rango_17': r17}).sort_values('rango_9')
    rk['puesto_9'] = range(1, len(rk) + 1)
    rk = rk.sort_values('rango_17')
    rk['puesto_17'] = range(1, len(rk) + 1)
    rk.sort_values('rango_9').rename_axis('method').to_csv(RANKING)
    print(f'    -> {RANKING.relative_to(ROOT)}')

    print(f'\n--- ranking de ocho entradas (nueve metricas; menor es mejor)')
    print(rk.sort_values('rango_9')[['rango_9', 'puesto_9', 'rango_17', 'puesto_17']]
          .to_string(float_format=lambda v: f'{v:.3f}'))

    # ------------------------------------------------------------------ sensibilidad y prueba pareada
    # El resultado con las nueve metricas invierte el primer puesto del benchmark, asi que NO alcanza
    # con reportarlo: hay que decir de que depende. Dos controles.
    #
    # (1) SENSIBILIDAD AL PESO. Si el orden se da vuelta con el otro criterio de agregacion del peso de
    #     la referencia —la mediana de sus cinco optimos por escena en lugar de la de sus 125 corridas—,
    #     entonces el primer puesto lo decide una eleccion del analista y hay que decirlo asi.
    ocho_s = pd.concat([allm, d2[['method', 'image'] + comunes]], ignore_index=True)
    r9s = rangos(ocho_s, NUEVE)
    print(f'\n--- sensibilidad: el mismo ranking con su peso agregado por el otro criterio '
          f'(m = {op["m_sensibilidad"]:.3f})')
    print(r9s.rename('rango_9').to_frame().assign(puesto=range(1, len(r9s) + 1))
          .to_string(float_format=lambda v: f'{v:.3f}'))

    # (2) PRUEBA PAREADA sobre los 20 pares. Un rango medio es un promedio de posiciones, y una
    #     diferencia de 0,07 puede ser ruido de agregacion. Lo que decide es en cuantos pares gana cada
    #     una y si esa asimetria sobrevive a un Wilcoxon. Se compara el rango PROMEDIO POR PAR, que es
    #     la unidad que el ranking agrega.
    from scipy.stats import wilcoxon
    print('\n--- la propuesta contra la referencia, par por par')
    filas_par = []
    for etiqueta, dref in (('m = %.3f' % op['m_principal'], d1),
                           ('m = %.3f' % op['m_sensibilidad'], d2)):
        base = pd.concat([allm, dref[['method', 'image'] + comunes]], ignore_index=True)
        por_par = {}
        for met in NUEVE:
            piv = base.pivot(index='image', columns='method', values=met)
            por_par[met] = piv.rank(axis=1, ascending=(DIRECTION_TODAS.get(met) == 'min'),
                                    method='average')
        prop = sum(por_par[m][PROP_KEY] for m in NUEVE) / len(NUEVE)
        ref = sum(por_par[m][dref.method.iloc[0]] for m in NUEVE) / len(NUEVE)
        gana = int((prop < ref).sum())      # menor rango es mejor
        pierde = int((prop > ref).sum())
        try:
            W, p = wilcoxon(prop, ref)
            sp = f'W = {W:.1f}, p = {p:.4f}'
        except Exception as e:                                        # pragma: no cover
            sp = f'sin prueba ({type(e).__name__})'
        print(f'    referencia con {etiqueta}: la propuesta gana en {gana} de {len(prop)} pares, '
              f'pierde en {pierde} · {sp}')
        print(f'      rango medio: propuesta {prop.mean():.3f} · referencia {ref.mean():.3f} '
              f'(diferencia {ref.mean() - prop.mean():+.3f})')
        # Nabf, la unica metrica del evaluador que penaliza artefactos, par por par y en la direccion
        # correcta: MENOR es mejor. Es la que explica por que el orden se da vuelta con las diecisiete.
        pn = pd.concat([allm, dref[['method', 'image'] + comunes]],
                       ignore_index=True).pivot(index='image', columns='method', values='Nabf')
        nabf_gana = int((pn[PROP_KEY] < pn[dref.method.iloc[0]]).sum())
        filas_par.append({
            'referencia': dref.method.iloc[0], 'r': op['r'],
            'm': op['m_principal'] if dref is d1 else op['m_sensibilidad'],
            'pares': len(prop), 'gana_propuesta': gana, 'pierde_propuesta': pierde,
            'empata': len(prop) - gana - pierde,
            'rango9_propuesta': round(float(prop.mean()), 4),
            'rango9_referencia': round(float(ref.mean()), 4),
            'W': float(W), 'p': float(p),
            'nabf_propuesta': round(float(pn[PROP_KEY].mean()), 4),
            'nabf_referencia': round(float(pn[dref.method.iloc[0]].mean()), 4),
            'nabf_gana_propuesta': nabf_gana,
        })
        print(f'      Nabf (menos artefactos es mejor): la propuesta gana en {nabf_gana} de '
              f'{len(pn)} pares · {pn[PROP_KEY].mean():.4f} contra '
              f'{pn[dref.method.iloc[0]].mean():.4f}')
    PAREADO = MR / 'metodologia_referencia_pareado.csv'
    pd.DataFrame(filas_par).to_csv(PAREADO, index=False)
    print(f'\n    -> {PAREADO.relative_to(ROOT)}')
    print('\n--- medias de las nueve, la referencia contra los dos Top-Hat del benchmark')
    comp = pd.concat([
        allm[allm.method.isin(['TopHat_Clasico', 'Propuesta_Novedosa'])],
        d1, d2], ignore_index=True)
    print(comp.groupby('method')[NUEVE].mean().to_string(float_format=lambda v: f'{v:.4f}'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
