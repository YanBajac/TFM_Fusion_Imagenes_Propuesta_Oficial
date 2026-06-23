# -*- coding: utf-8 -*-
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch
plt.rcParams.update({'font.family':'DejaVu Sans'})
NAVY='#1f3b57'; INK='#1a1a1a'; GRAY='#555555'; BORD='#8a98a6'; LB='#c2ccd6'

fig,ax=plt.subplots(figsize=(8.2,11.7)); ax.set_xlim(0,800); ax.set_ylim(0,1140)
ax.invert_yaxis(); ax.axis('off'); fig.patch.set_facecolor('white')

def box(x,y,w,h,accent=False,dashed=False):
    ec=NAVY if accent else BORD; lw=2.0 if accent else 1.4
    ls=(0,(5,4)) if dashed else 'solid'
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=2,rounding_size=10',
        fc='white',ec=ec,lw=lw,ls=ls,mutation_aspect=1))
def oval(x,y,w,h):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=2,rounding_size=26',fc='white',ec=NAVY,lw=2.0))
def diamond(cx,cy,hw,hh):
    ax.add_patch(Polygon([(cx,cy-hh),(cx+hw,cy),(cx,cy+hh),(cx-hw,cy)],closed=True,fc='white',ec=BORD,lw=1.6))
def T(cx,cy,s,size=12,color=INK,bold=False,italic=False,ha='center'):
    ax.text(cx,cy,s,ha=ha,va='center',fontsize=size,color=color,
            fontweight='bold' if bold else 'normal',fontstyle='italic' if italic else 'normal')
def arr(x1,y1,x2,y2):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=13,color=BORD,lw=1.7))
def loop(points,label=None,lpos=None,rot=0):
    for a,b in zip(points[:-2],points[1:-1]):
        ax.plot([a[0],b[0]],[a[1],b[1]],color=NAVY,lw=1.6,ls=(0,(5,4)))
    p,q=points[-2],points[-1]
    ax.add_patch(FancyArrowPatch(p,q,arrowstyle='-|>',mutation_scale=13,color=NAVY,lw=1.6,ls=(0,(5,4))))
    if label: T(lpos[0],lpos[1],label,11,NAVY,bold=True); 
def YN(x,y,s): T(x,y,s,12,GRAY,bold=True)

# INICIO
oval(230,20,340,52); T(400,40,'INICIO',13,NAVY,bold=True); T(400,60,'VIS, IR (gris, [0,1])  ·  parámetros n, r, m',10.5,GRAY,italic=True)
arr(400,72,400,100)
# loop fuentes
box(210,100,380,44,accent=True,dashed=True); T(400,123,'Para cada fuente S ∈ {VIS, IR}',12.5,NAVY,bold=True)
arr(400,144,400,172)
box(330,172,140,38); T(400,191,'i ← 1',12.5,INK,bold=True)
arr(400,210,400,240)
# cuerpo escala
box(150,240,500,52); T(400,260,'Escala i:  rᵢ = redondear(r · i)',12.5,INK,bold=True); T(400,280,'construir 5 SE: disco + líneas 0°, 45°, 90°, 135°',10.5,GRAY,italic=True)
arr(400,292,400,320)
box(150,320,500,54); T(400,341,'WTHᵢ = máxᵦ ( S − apertura(S, b) )',11,INK,italic=True); T(400,361,'BTHᵢ = máxᵦ ( cierre(S, b) − S )',11,INK,italic=True)
arr(400,374,400,416)
# decisión i<n
diamond(400,456,105,40); T(400,458,'¿ i < n ?',12.5,INK,bold=True)
YN(515,448,'sí'); YN(414,518,'no')
loop([(505,456),(735,456),(735,266),(654,266)],'i ← i + 1',(700,250))
arr(400,496,400,524)
# cascada
box(150,524,500,54); T(400,544,'Diferencias en cascada',12.5,INK,bold=True); T(400,565,'WTHS₂ = WTH₂ − WTH₁ ;  WTHSᵢ = WTHᵢ − WTHSᵢ₋₂',10.5,INK,italic=True)
arr(400,578,400,606)
# agregación
box(150,606,500,54); T(400,626,'Agregar por máximo entre escalas',12.5,INK,bold=True); T(400,647,'WTH_M[S],  WTHS_M[S],  BTH_M[S],  BTHS_M[S]',10.5,INK,italic=True)
arr(400,660,400,702)
# decisión fuentes
diamond(400,744,125,42); T(400,744,'¿VIS e IR listas?',12,INK,bold=True)
YN(410,812,'sí'); YN(258,734,'no')
loop([(275,744),(70,744),(70,122),(208,122)])
ax.text(58,470,'siguiente fuente',rotation=90,ha='center',va='center',fontsize=11,color=NAVY,fontweight='bold')
arr(400,786,400,816)
# combinar
box(150,816,500,54); T(400,836,'Combinar fuentes (máximo por píxel)',12.5,INK,bold=True); T(400,857,'WTH_M = máx(VIS, IR)  ·  ídem WTHS_M, BTH_M, BTHS_M',10.5,INK,italic=True)
arr(400,870,400,898)
# base
box(285,898,230,42); T(400,922,'I_base = (VIS + IR) / 2',11,INK,italic=True)
arr(400,940,400,968)
# fusión
box(130,968,540,54,accent=True); T(400,997,'F = recortar( I_base + m·(WTH_M+WTHS_M) − m·(BTH_M+BTHS_M), 0, 1 )',10.8,NAVY,italic=True,bold=True)
arr(400,1022,400,1052)
# fin
oval(270,1052,260,50); T(400,1080,'Imagen fusionada  F',12.5,NAVY,bold=True)

# limpiar el placeholder vacío de rotación
fig.tight_layout(pad=0.4)
fig.savefig('docs/figures/fig_flujograma_multiescala.png',dpi=200,facecolor='white',bbox_inches='tight')
print('FLUJOGRAMA OK')
