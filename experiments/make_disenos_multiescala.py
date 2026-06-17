# -*- coding: utf-8 -*-
import sys; sys.path.insert(0,'.')
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import pandas as pd
from src.datasets import list_pairs, load_pair
from src.fusion.optimal_top_hat import _wth_bth_5se, _multiscale_components, fuse_optimal_multiscale

plt.rcParams.update({'font.family':'DejaVu Sans'})
NAVY='#1f3b57'; ACC='#c0392b'; GRN='#2e7d32'; BG='#f4f7fa'; GRY='#5b6b7b'
OUT='docs/figures/disenos/'
def nrm(x):
    x=x.astype(float); mn,mx=x.min(),x.max()
    return (x-mn)/(mx-mn+1e-9)
def stretch(x,p=99.0,g=0.5):
    x=x.astype(float); hi=np.percentile(x,p)
    return np.clip(x/(hi+1e-9),0,1)**g

pairs=list_pairs()
vis,ir=load_pair(*pairs[6])           # Athena: dos hombres frente a una casa
R=2.89; N=6
fused=fuse_optimal_multiscale(vis,ir,n=N,base_radius=R,m=0.10)
scales=[1,3,6]
wth_sc=[]; bth_sc=[]
for i in scales:
    r=max(1,int(round(R*i)))
    wv,bv=_wth_bth_5se(vis,r); wi,bi=_wth_bth_5se(ir,r)
    wth_sc.append(np.maximum(wv,wi)); bth_sc.append(np.maximum(bv,bi))
wv,bv,wsv,bsv=_multiscale_components(vis,N,R)
wi,bi,wsi,bsi=_multiscale_components(ir,N,R)
WTH_M=np.maximum(wv,wi); BTH_M=np.maximum(bv,bi)

dm=pd.read_csv('experiments/results/metrics_reports/descriptive_means.csv').set_index('method')
def row(m): return dm.loc[m]
opt=row('Optimo_Multiescala'); lap=row('PiramideLaplace'); ant=row('TopHat_disk_L5')

def img(ax,a,title,cmap='gray',tc=NAVY,fs=12):
    ax.imshow(a,cmap=cmap); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_edgecolor('#c2ccd6'); s.set_linewidth(1.2)
    if title: ax.set_title(title,color=tc,fontsize=fs,fontweight='bold',pad=4)

# =================== FIGURA A: GRAPHICAL ABSTRACT ===================
fig=plt.figure(figsize=(14,5.4)); fig.patch.set_facecolor('white')
bg=fig.add_axes([0,0,1,1]); bg.axis('off'); bg.set_xlim(0,1); bg.set_ylim(0,1)
def box(x,y,w,h,fc,ec,lw=1.6):
    bg.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.004,rounding_size=0.02',fc=fc,ec=ec,lw=lw,zorder=0))
def arr(x1,x2,y,col=GRY):
    bg.add_patch(FancyArrowPatch((x1,y),(x2,y),arrowstyle='-|>',mutation_scale=22,color=col,lw=2.4,zorder=5))
fig.text(0.5,0.95,'Fusión VIS/IR por morfología multiescala óptima — esquema general del método',
         ha='center',color=NAVY,fontsize=15,fontweight='bold')
# entradas
av=fig.add_axes([0.025,0.55,0.12,0.30]); img(av,vis,'VIS',fs=11)
ai=fig.add_axes([0.025,0.18,0.12,0.30]); img(ai,ir,'IR',fs=11)
bg.text(0.085,0.10,'Entradas',ha='center',color=GRY,fontsize=11,fontweight='bold')
arr(0.155,0.205,0.51)
# bloque método
box(0.21,0.13,0.30,0.74,'#eaf0f6',NAVY,1.8)
bg.text(0.36,0.81,'Método óptimo multiescala',ha='center',color=NAVY,fontsize=12.5,fontweight='bold')
bg.text(0.36,0.76,'banco de 5 SE (disco + 4 líneas) · cascada de n escalas',ha='center',color=GRY,fontsize=9.5)
for k,(xx,i) in enumerate(zip([0.235,0.318,0.401],scales)):
    axk=fig.add_axes([xx,0.34,0.083,0.30]); img(axk,stretch(wth_sc[k]),f'escala r·{i}',cmap='magma',tc=ACC,fs=10)
bg.text(0.36,0.20,'PSO: n = 6,  r ≈ 2,89,  m = 0,10',ha='center',color=GRN,fontsize=10.5,fontweight='bold')
arr(0.515,0.565,0.5)
# fusión
af=fig.add_axes([0.575,0.27,0.17,0.46]); img(af,fused,'Imagen fusionada',tc=ACC,fs=12)
arr(0.75,0.80,0.5)
# métricas
axm=fig.add_axes([0.82,0.27,0.16,0.42])
mets=['Qabf','SCD','SSIM','VIF']
xo=np.arange(len(mets)); wdt=0.38
axm.bar(xo-wdt/2,[opt[m] for m in mets],wdt,color=ACC,label='Multiescala')
axm.bar(xo+wdt/2,[lap[m] for m in mets],wdt,color=GRY,label='Laplace')
axm.set_xticks(xo); axm.set_xticklabels(mets,fontsize=9); axm.tick_params(labelsize=8)
axm.set_title('Evaluación · 12 métricas',color=NAVY,fontsize=11,fontweight='bold')
axm.legend(fontsize=8,loc='upper right',framealpha=.9)
for sp in ['top','right']: axm.spines[sp].set_visible(False)
bg.text(0.90,0.20,'+ detección (YOLO)',ha='center',color=GRY,fontsize=9.5,style='italic')
fig.savefig(OUT+'A_graphical_abstract.png',dpi=170,facecolor='white'); plt.close(fig)

# =================== FIGURA B: PIPELINE CON IMÁGENES REALES ===================
fig=plt.figure(figsize=(14,6.2)); fig.patch.set_facecolor('white')
bg=fig.add_axes([0,0,1,1]); bg.axis('off'); bg.set_xlim(0,1); bg.set_ylim(0,1)
fig.text(0.5,0.95,'Descomposición Top-Hat multiescala sobre un par real y regla de fusión',
         ha='center',color=NAVY,fontsize=15,fontweight='bold')
def arrB(x1,y1,x2,y2,col=ACC):
    bg.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=20,color=col,lw=2.2,zorder=5))
cols_x=[0.06,0.205,0.35]; rW=0.135
for k,(xx,i) in enumerate(zip(cols_x,scales)):
    r=max(1,int(round(R*i)))
    a1=fig.add_axes([xx,0.55,rW,0.30]); img(a1,stretch(wth_sc[k]),f'r·{i}  (r={r})',cmap='magma',tc=NAVY,fs=11)
    a2=fig.add_axes([xx,0.16,rW,0.30]); img(a2,stretch(bth_sc[k]),'',cmap='magma')
bg.text(0.035,0.70,'WTH',ha='center',va='center',color=NAVY,fontsize=12,fontweight='bold',rotation=90)
bg.text(0.035,0.31,'BTH',ha='center',va='center',color='#7a4a2b',fontsize=12,fontweight='bold',rotation=90)
bg.text(0.235,0.07,'escalas crecientes  rᵢ = r·i   (i = 1 … n)',ha='center',color=GRY,fontsize=10.5)
# agregado
arrB(0.50,0.70,0.545,0.70); arrB(0.50,0.31,0.545,0.31)
ag1=fig.add_axes([0.55,0.55,rW,0.30]); img(ag1,stretch(WTH_M),'WTH_M  (máx)',cmap='magma',tc=ACC,fs=11)
ag2=fig.add_axes([0.55,0.16,rW,0.30]); img(ag2,stretch(BTH_M),'BTH_M  (máx)',cmap='magma',tc=ACC,fs=11)
# fusión
arrB(0.695,0.70,0.74,0.51); arrB(0.695,0.31,0.74,0.49)
afu=fig.add_axes([0.745,0.27,0.235,0.45]); img(afu,fused,'Imagen fusionada',tc=ACC,fs=13)
bg.text(0.862,0.20,'F = I_base + m·(WTH_M+WTHS_M) − m·(BTH_M+BTHS_M)',ha='center',color=GRN,fontsize=9,fontweight='bold')
fig.savefig(OUT+'B_pipeline_real.png',dpi=170,facecolor='white'); plt.close(fig)

# =================== FIGURA C: ESQUEMÁTICO VECTORIAL ===================
fig,ax=plt.subplots(figsize=(14,4.8)); ax.set_xlim(0,14); ax.set_ylim(0,4.8); ax.axis('off')
fig.patch.set_facecolor('white')
def cbox(x,y,w,h,txt,fc,ec,fs=10.5,tc='#16242f',bold=True):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.05,rounding_size=0.14',fc=fc,ec=ec,lw=1.8))
    ax.text(x+w/2,y+h/2,txt,ha='center',va='center',fontsize=fs,color=tc,fontweight='bold' if bold else 'normal')
def ca(x1,x2,y=3.0,col=GRY):
    ax.add_patch(FancyArrowPatch((x1,y),(x2,y),arrowstyle='-|>',mutation_scale=18,color=col,lw=2.0))
ax.text(7,4.5,'Pipeline del método óptimo multiescala (esquema)',ha='center',color=NAVY,fontsize=15,fontweight='bold')
cbox(0.2,2.4,1.5,1.2,'VIS\n+\nIR','#eef3f8',NAVY,10)
cbox(2.1,2.35,2.3,1.3,'Banco de 5 SE\ndisco + 4 líneas\n(máx por píxel)','#d6e4f0',NAVY,9.5)
cbox(4.8,2.35,2.3,1.3,'Cascada de\nn escalas\nWTHSᵢ, BTHSᵢ','#d6e4f0',NAVY,9.5)
cbox(7.5,2.35,2.3,1.3,'Agregación máx\nWTH_M, WTHS_M\nBTH_M, BTHS_M','#fbe9e7',ACC,9.5)
cbox(10.2,2.35,2.4,1.3,'Fusión ponderada\nF = I_base\n+ m·WTH − m·BTH','#e8f5e9',GRN,9.5)
cbox(12.85,2.55,1.0,0.9,'F','#16242f','#16242f',13,tc='white')
for x1,x2 in [(1.7,2.1),(4.4,4.8),(7.1,7.5),(9.8,10.2),(12.6,12.85)]: ca(x1,x2)
# lazo PSO
ax.add_patch(FancyBboxPatch((2.1,0.5),10.5,0.95,boxstyle='round,pad=0.05,rounding_size=0.12',fc='#fff7e6',ec='#b8860b',lw=1.6))
ax.text(7.35,0.97,'PSO ajusta (n, r, m)  maximizando  F = SSIM + Qabf + 0,5·SCD − Nabf   →   n=6, r≈2,89, m=0,10',
        ha='center',va='center',fontsize=10.5,color='#7a5b00',fontweight='bold')
for xx in [3.25,5.95,8.65,11.4]:
    ax.add_patch(FancyArrowPatch((xx,2.35),(xx,1.45),arrowstyle='-|>',mutation_scale=12,color='#b8860b',lw=1.3,linestyle=(0,(4,2))))
fig.savefig(OUT+'C_esquema_vectorial.png',dpi=170,facecolor='white'); plt.close(fig)
print('DISENOS OK')
