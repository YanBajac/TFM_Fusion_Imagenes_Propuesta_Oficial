# -*- coding: utf-8 -*-
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch
plt.rcParams.update({'font.family':'DejaVu Sans'})
NAVY='#1f3b57'; INK='#1a1a1a'; GRAY='#555555'; BORD='#8a98a6'
fig,ax=plt.subplots(figsize=(8.4,11.6)); ax.set_xlim(0,800); ax.set_ylim(0,1160)
ax.invert_yaxis(); ax.axis('off'); fig.patch.set_facecolor('white')
def box(x,y,w,h,accent=False):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=2,rounding_size=10',fc='white',
        ec=(NAVY if accent else BORD),lw=(2.0 if accent else 1.4)))
def oval(x,y,w,h):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=2,rounding_size=26',fc='white',ec=NAVY,lw=2.0))
def dia(cx,cy,hw,hh):
    ax.add_patch(Polygon([(cx,cy-hh),(cx+hw,cy),(cx,cy+hh),(cx-hw,cy)],closed=True,fc='white',ec=BORD,lw=1.6))
def T(cx,cy,s,size=12,color=INK,bold=False,italic=False):
    ax.text(cx,cy,s,ha='center',va='center',fontsize=size,color=color,
            fontweight='bold' if bold else 'normal',fontstyle='italic' if italic else 'normal')
def arr(x1,y1,x2,y2):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=13,color=BORD,lw=1.7))
def loop(pts):
    for a,b in zip(pts[:-2],pts[1:-1]): ax.plot([a[0],b[0]],[a[1],b[1]],color=NAVY,lw=1.6,ls=(0,(5,4)))
    ax.add_patch(FancyArrowPatch(pts[-2],pts[-1],arrowstyle='-|>',mutation_scale=13,color=NAVY,lw=1.6,ls=(0,(5,4))))

oval(230,20,340,52); T(400,40,'INICIO',13,NAVY,bold=True); T(400,60,'VIS, IR (gris, [0,1])  ·  parámetros n, m',10.5,GRAY,italic=True)
arr(400,72,400,100)
box(210,100,380,44,accent=True); T(400,123,'Para cada fuente S ∈ {VIS, IR}',12.5,NAVY,bold=True)
arr(400,144,400,172)
box(330,172,140,38); T(400,191,'i ← 1',12.5,INK,bold=True)
arr(400,210,400,242)
box(150,242,500,54); T(400,262,'Escala i:  dᵢ = 2·i + 1',12.5,INK,bold=True); T(400,282,'construir 5 SE: 1 disco + 4 líneas (0°,45°,90°,135°)',10.5,GRAY,italic=True)
arr(400,296,400,326)
box(150,326,500,56)
T(400,346,'WTHᵢ = máx( (Σθ líneas)/4 ,  disco )',11,INK,italic=True)
T(400,367,'BTHᵢ = máx( (Σθ líneas)/4 ,  disco )',11,INK,italic=True)
arr(400,382,400,420)
dia(400,460,105,40); T(400,462,'¿ i < n ?',12.5,INK,bold=True)
T(515,452,'sí',12,GRAY,bold=True); T(414,524,'no',12,GRAY,bold=True)
loop([(505,460),(735,460),(735,270),(654,270)]); T(700,254,'i ← i + 1',11,NAVY,bold=True)
arr(400,500,400,532)
box(150,532,500,54); T(400,552,'Agregar por máximo entre escalas',12.5,INK,bold=True); T(400,573,'WTH_M = máxᵢ WTHᵢ ;  BTH_M = máxᵢ BTHᵢ',10.5,INK,italic=True)
arr(400,586,400,624)
dia(400,664,125,42); T(400,664,'¿VIS e IR listas?',12,INK,bold=True)
T(410,730,'sí',12,GRAY,bold=True); T(258,654,'no',12,GRAY,bold=True)
loop([(275,664),(70,664),(70,122),(208,122)]); ax.text(58,400,'siguiente fuente',rotation=90,ha='center',va='center',fontsize=11,color=NAVY,fontweight='bold')
arr(400,706,400,738)
box(150,738,500,54); T(400,758,'Combinar fuentes (máximo por píxel)',12.5,INK,bold=True); T(400,779,'WTH_M = máx(VIS, IR) ;  BTH_M = máx(VIS, IR)',10.5,INK,italic=True)
arr(400,792,400,820)
box(285,820,230,42); T(400,844,'I_base = (VIS + IR) / 2',11,INK,italic=True)
arr(400,862,400,890)
box(140,890,520,54,accent=True); T(400,919,'F = recortar( I_base + m·WTH_M − m·BTH_M , 0, 1 )',11.5,NAVY,italic=True,bold=True)
arr(400,944,400,974)
oval(270,974,260,50); T(400,1002,'Imagen fusionada  F',12.5,NAVY,bold=True)
T(400,1062,'PSO ajusta (n, m) maximizando SSIM+Qabf+0,5·SCD−Nabf   →   n = 8,  m = 0,12',10.5,GRAY)
fig.tight_layout(pad=0.4); fig.savefig('docs/figures/fig_flujograma_multiescala.png',dpi=200,facecolor='white',bbox_inches='tight')
print('flujograma OK')
