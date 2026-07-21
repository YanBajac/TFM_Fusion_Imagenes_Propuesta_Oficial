# -*- coding: utf-8 -*-
"""Evalua sobre los 20 pares TNO los optimos hallados por el PSO con la aptitud
F_o = SSIM_avg + E_n + PSNR_n del libro FPUNA (experimento solicitado por el
director): Propuesta_Fo (r=1, m=0.3, suma de ramas) y Clasico_Fo (r=25, m=0.3,
disco unico), y los compara con los metodos del benchmark ya calculados.

Salida: experiments/results/metrics_reports/fo_ablacion_per_image.csv
        experiments/results/metrics_reports/fo_ablacion_comparativa.csv
Uso:    python experiments/eval_fo_optima.py
"""
import sys
sys.path.insert(0, '.')
import pandas as pd
from src.datasets import list_pairs, load_pair
from src.fusion.optimal_top_hat import fuse_optimal
from src.fusion.comparatives import tophat_classic_fusion
from src.metrics import evaluate_all

MR = 'experiments/results/metrics_reports/'
VARIANTES = {
    'Propuesta_Fo(r=1,m=0.30)': lambda v, i: fuse_optimal(v, i, r=1, m=0.30, mode='sum'),
    'Clasico_Fo(r=25,m=0.30)': lambda v, i: tophat_classic_fusion(v, i, r=25, m=0.30),
}

filas = []
for k, (vp, ip) in enumerate(list_pairs(), 1):
    vis, ir = load_pair(vp, ip)
    for nombre, fn in VARIANTES.items():
        met = evaluate_all(fn(vis, ir), vis, ir)
        met.update(method=nombre, image=k)
        filas.append(met)
    print(f'par {k:02d}/20 ok', flush=True)

df = pd.DataFrame(filas)
df.to_csv(MR + 'fo_ablacion_per_image.csv', index=False)

COLS = ['EN', 'SD', 'FE', 'MG', 'MI_vis', 'MI_ir', 'SF', 'Qabf', 'Nabf', 'SSIM', 'SCD', 'VIF']
medias_fo = df.groupby('method')[COLS].mean()
ref = pd.read_csv(MR + 'descriptive_means.csv').set_index('method')
comp = pd.concat([
    ref.loc[['Propuesta_Novedosa'], COLS].rename(
        index={'Propuesta_Novedosa': 'Propuesta_Fapt(r=25,m=0.07)'}),
    medias_fo,
    ref.loc[['TopHat_Clasico'], COLS].rename(
        index={'TopHat_Clasico': 'Clasico_manual(r=5,m=1)'}),
])
comp.round(4).to_csv(MR + 'fo_ablacion_comparativa.csv')
print()
print(comp.round(3).to_string())
print('\nGuardado:', MR + 'fo_ablacion_comparativa.csv')
