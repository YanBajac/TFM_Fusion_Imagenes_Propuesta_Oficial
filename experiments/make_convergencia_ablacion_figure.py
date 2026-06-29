# -*- coding: utf-8 -*-
import json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans'})
NAVY='#1f3b57'; ACC='#c0392b'; GRN='#2e7d32'; GRY='#5b6b7b'
st=json.load(open('experiments/results/pso/pso_multiscale_state.json'))
it=[h['it'] for h in st['history']]; F=[h['F'] for h in st['history']]
abl=json.load(open('experiments/results/metrics_reports/ablation_multiescala.json'))
ns=[1,2,4,6,8]
qa=[abl['Monoescala (n=1)'][0],abl['n=2'][0],abl['n=4'][0],abl['Disco + 4 lineas — propuesta (n=6)'][0],abl['n=8'][0]]
sc=[abl['Monoescala (n=1)'][2],abl['n=2'][2],abl['n=4'][2],abl['Disco + 4 lineas — propuesta (n=6)'][2],abl['n=8'][2]]

fig,(a1,a2)=plt.subplots(1,2,figsize=(13,4.6)); fig.patch.set_facecolor('white')
# --- A: convergencia PSO ---
a1.plot(it,F,'-o',color=NAVY,lw=2.4,ms=7,mfc=ACC,mec=ACC)
a1.axvline(6,color=GRN,ls='--',lw=1.4)
a1.annotate('convergencia estable (iter. 6)\nn = 6,  r ≈ 2,89,  m = 0,10',
            xy=(6,F[5]),xytext=(6.3,F[0]+0.004),fontsize=10,color=GRN,
            arrowprops=dict(arrowstyle='->',color=GRN))
a1.set_xlabel('Iteración',fontsize=11); a1.set_ylabel('Aptitud  F = SSIM+Qabf+0,5·SCD−Nabf',fontsize=10)
a1.set_title('Convergencia del PSO (30 partículas)',color=NAVY,fontsize=12.5,fontweight='bold')
a1.grid(alpha=.25); 
for s in ['top','right']: a1.spines[s].set_visible(False)
# --- B: sensibilidad a n ---
a2.plot(ns,qa,'-o',color=ACC,lw=2.2,ms=7,label='Qabf (↑)')
a2.set_xlabel('Número de escalas  n',fontsize=11)
a2.set_ylabel('Qabf',color=ACC,fontsize=11); a2.tick_params(axis='y',labelcolor=ACC)
a2b=a2.twinx(); a2b.plot(ns,sc,'-s',color=NAVY,lw=2.2,ms=7,label='SCD (↑)')
a2b.set_ylabel('SCD',color=NAVY,fontsize=11); a2b.tick_params(axis='y',labelcolor=NAVY)
a2.axvline(6,color=GRN,ls='--',lw=1.4); a2.text(6.05,min(qa),'  n* = 6',color=GRN,fontsize=10,fontweight='bold')
a2.set_title('Sensibilidad al número de escalas',color=NAVY,fontsize=12.5,fontweight='bold')
a2.set_xticks(ns); a2.grid(alpha=.25)
for s in ['top']: a2.spines[s].set_visible(False); a2b.spines[s].set_visible(False)
fig.suptitle('Optimización y ablación del método óptimo multiescala  (5 escenas representativas)',
             color=NAVY,fontsize=13.5,fontweight='bold',y=1.02)
fig.tight_layout()
fig.savefig('docs/figures/fig_pso_convergencia_ablacion.png',dpi=170,facecolor='white',bbox_inches='tight')
print('FIG OK')
