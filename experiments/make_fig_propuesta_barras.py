# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
NAVY='#1f3b57'; ACC='#c0392b'; GREY='#9aa7b3'
df=pd.read_csv('experiments/results/metrics_reports/comparativa_con_propuesta.csv').set_index(
    pd.read_csv('experiments/results/metrics_reports/comparativa_con_propuesta.csv').columns[0])
df=pd.read_csv('experiments/results/metrics_reports/comparativa_con_propuesta.csv')
df=df.set_index(df.columns[0])
order=[('Promedio','Promedio'),('PiramideLaplace','Laplace'),('Curvelet','Curvelet'),
('TopHat_disk_L5','Torre L5'),('Optimo_Multiescala','Multiesc. prelim.'),('Propuesta_Novedosa','Propuesta\nNovedosa')]
labels=[o[1] for o in order]; keys=[o[0] for o in order]
metr=[('Qabf','Qabf (mayor=mejor)'),('SCD','SCD (mayor=mejor)'),('SSIM','SSIM (mayor=mejor)'),
('Nabf','Nabf (menor=mejor)'),('VIF','VIF (mayor=mejor)'),('SD','SD (mayor=mejor)')]
fig,axes=plt.subplots(2,3,figsize=(13,7)); axes=axes.ravel(); fig.patch.set_facecolor('white')
for k,(m,title) in enumerate(metr):
    ax=axes[k]; vals=[df.loc[kk,m] for kk in keys]
    colors=[ACC if kk=='Propuesta_Novedosa' else GREY for kk in keys]
    bars=ax.bar(range(len(keys)),vals,color=colors,edgecolor='white')
    ax.set_title(title,fontsize=11,fontweight='bold',color=NAVY)
    ax.set_xticks(range(len(keys))); ax.set_xticklabels(labels,fontsize=7.5,rotation=30,ha='right')
    for b,v in zip(bars,vals): ax.text(b.get_x()+b.get_width()/2,v,f'{v:.3f}',ha='center',va='bottom',fontsize=7.5)
    for s in ['top','right']: ax.spines[s].set_visible(False)
    ax.margins(y=0.18)
fig.suptitle('Propuesta Novedosa (PSO: n=8, m=0,12) frente al método anterior y a los baselines — medias sobre 20 pares',
             fontsize=12.5,fontweight='bold',color=NAVY,y=1.00)
fig.tight_layout(rect=[0,0,1,0.97]); fig.savefig('docs/figures/fig_metodo_optimo_multiescala.png',dpi=160,facecolor='white')
print('barra OK')
