# -*- coding: utf-8 -*-
"""Genera el esquema de la Torre Top-Hat incluyendo la rama Black Top-Hat (BTH)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

FIG = "docs/figures/fig_esquema_torre_tophat.png"

fig, ax = plt.subplots(figsize=(12.2, 6.6))
ax.set_xlim(0, 122); ax.set_ylim(0, 66); ax.axis("off")

C_VIS="#F6D99B"; C_IR="#F1A8A8"; C_WTH="#BBD2EC"; C_BTH="#C9B6E0"
C_FUS="#BFE3C0"; C_OUT="#F6EFC0"; EDGE="#3a3a3a"

def box(x,y,w,h,text,fc,fs=8.5,dashed=False,ec=EDGE,bold=False):
    style="round,pad=0.02,rounding_size=2"
    p=FancyBboxPatch((x,y),w,h,boxstyle=style,fc=fc,ec=ec,lw=1.3,
                     linestyle="--" if dashed else "-")
    ax.add_patch(p)
    ax.text(x+w/2,y+h/2,text,ha="center",va="center",fontsize=fs,
            weight="bold" if bold else "normal")

def arrow(x1,y1,x2,y2,dashed=False,color=EDGE):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",
        mutation_scale=12,lw=1.2,color=color,
        linestyle="--" if dashed else "-"))

ax.text(61,63,"Esquema de la Torre Top-Hat propuesta (modos WTH y WTH+BTH)",
        ha="center",fontsize=12.5,weight="bold")

# Fuentes
box(2,46,12,7,"VIS\nf_vis",C_VIS,bold=True)
box(2,12,12,7,"IR\nf_ir",C_IR,bold=True)

# Niveles
radii=["r=2","r=4","r=6"]
wx=[20,38,56]
# WTH VIS (arriba) y WTH IR
for i,x in enumerate(wx):
    box(x,52,14,7,f"WTH$_{i+1}$ (VIS)\n{radii[i]}",C_WTH)
    box(x,19,14,7,f"WTH$_{i+1}$ (IR)\n{radii[i]}",C_WTH)
# BTH VIS y BTH IR (ramas opcionales, borde discontinuo)
for i,x in enumerate(wx):
    box(x,42,14,7,f"BTH$_{i+1}$ (VIS)\n{radii[i]}",C_BTH,dashed=True)
    box(x,9,14,7,f"BTH$_{i+1}$ (IR)\n{radii[i]}",C_BTH,dashed=True)

# flechas desde fuentes a primeros niveles
arrow(14,51,20,55.5)          # VIS->WTH1
arrow(14,48,20,45.5,dashed=True)  # VIS->BTH1
arrow(14,16,20,22.5)          # IR->WTH1
arrow(14,14,20,12.5,dashed=True)  # IR->BTH1
# encadenado entre niveles (solo indicativo)
for a,b in zip(wx[:-1],wx[1:]):
    arrow(a+14,55.5,b,55.5)
    arrow(a+14,45.5,b,45.5,dashed=True)
    arrow(a+14,22.5,b,22.5)
    arrow(a+14,12.5,b,12.5,dashed=True)

# Bloque de fusion
box(80,33,20,12,"Fusión por capa:\nmáx. actividad (WTH y BTH)\n+ promedio (base)",C_FUS,fs=8.2,bold=False)
# flechas de cada rama al bloque
arrow(70,55.5,80,43)
arrow(70,45.5,80,40,dashed=True)
arrow(70,22.5,80,38)
arrow(70,12.5,80,35,dashed=True)

# Reconstruccion
box(78,20,24,7,"F = base + Σ WTH$_k$ − Σ BTH$_k$",C_OUT,fs=9.5,bold=True)
arrow(90,33,90,27)
# Salida
box(82,7,16,7,"Imagen\nFusionada",C_OUT,bold=True)
arrow(90,20,90,14)

# Leyenda
ax.text(2,3.0,"Línea continua: rama White Top-Hat (modo por defecto).  "
              "Línea discontinua: rama Black Top-Hat (modo WTH+BTH, opcional) — se resta en la reconstrucción.",
        fontsize=8.0, style="italic", color="#444")

plt.tight_layout()
fig.savefig(FIG, dpi=170, bbox_inches="tight")
print("Esquema regenerado:", FIG)
