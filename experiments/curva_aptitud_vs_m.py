# -*- coding: utf-8 -*-
"""Curva de aptitud en funcion del peso m (r fijo en 25) para las dos funciones
objetivo: F_apt (tesis) y F_o (libro FPUNA), sobre la propuesta y el clasico.
Demuestra por que ningun enjambre (n, T) puede llevar el optimo al interior del rango
publicado m en [0,30; 2,00]:
ambas aptitudes decrecen monotonamente con m a partir de valores pequenos.

Salida: experiments/results/metrics_reports/curva_aptitud_vs_m.csv
        docs/figures/fig_aptitud_vs_m.png
Uso:    .venv\Scripts\python.exe -X utf8 experiments/curva_aptitud_vs_m.py
"""
import sys
sys.path.insert(0, '.')
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import experiments.pso_grid_search as MFA                                  # F_apt, suma
import experiments.pso_grid_search_fo as MFO                               # F_o

# ampliar los limites de ambos modulos para medir el paisaje completo sin clipping
MFA.LO = np.array([1.0, 0.0]); MFA.HI = np.array([25.0, 2.0])
MFO.LO = np.array([1.0, 0.0]); MFO.HI = np.array([25.0, 2.0])
fapt_propuesta = MFA.fitness
fo_prop = MFO.hacer_fitness("propuesta")
fo_clas = MFO.hacer_fitness("clasico")

MS = np.array([0.05, 0.0703, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.70,
               1.00, 1.20, 1.50, 2.00])
R = 25.0

filas = ["m,Fapt_propuesta,Fo_propuesta,Fo_clasico"]
ap, fp, fc = [], [], []
for m in MS:
    x = np.array([R, m])
    a = fapt_propuesta(x); b = fo_prop(x); c = fo_clas(x)
    ap.append(a); fp.append(b); fc.append(c)
    filas.append(f"{m},{a:.4f},{b:.4f},{c:.4f}")
    print(f"m={m:5.3f} | F_apt(prop)={a:.4f} | F_o(prop)={b:.4f} | F_o(clas)={c:.4f}",
          flush=True)

out = "experiments/results/metrics_reports/curva_aptitud_vs_m.csv"
open(out, "w", encoding="utf-8").write("\n".join(filas))

plt.rcParams.update({"font.family": "serif", "font.size": 11})
fig, ax = plt.subplots(figsize=(8.0, 4.2))
ax.plot(MS, ap, "o-", color="#8b1a1a", lw=1.6, ms=4,
        label="F_apt (tesis) — propuesta, r=25")
ax.plot(MS, fp, "s--", color="#4d4d4d", lw=1.3, ms=4,
        label="F_o (FPUNA) — propuesta, r=25")
ax.plot(MS, fc, "^:", color="#999999", lw=1.3, ms=4.5,
        label="F_o (FPUNA) — clásico, r=25")
# La banda es el RANGO PUBLICADO, m en [0,30; 2,00], que es el que la tesis hereda y sobre el que
# corre su barrido. Antes sombreaba [0,5; 2] y lo rotulaba «rango sugerido», que no es de ningun
# trabajo: ni el de la referencia ni este. Y la unica marca vertical era m* = 0,0703 —el optimo de
# la aptitud paralela F_apt, que la tesis NO adopta—, de modo que la figura contradecia a su propio
# epigrafe, que dice que el optimo dentro del rango cae en su piso, m* = 0,30.
PISO, TECHO = 0.30, 2.00
ax.axvspan(PISO, TECHO, color="#dddddd", alpha=0.45, lw=0)
ax.text((PISO + TECHO) / 2, ax.get_ylim()[0] + 0.06,
        f"rango publicado m ∈ [{PISO:.2f}; {TECHO:.2f}]".replace(".", ","),
        fontsize=9.5, color="#666666", ha="center")
# Las dos marcas que importan, cada una diciendo lo que es. Las etiquetas van en la mitad baja del
# eje: arriba se pisaban entre si, con el borde y con los marcadores de las tres curvas.
_lo, _hi = ax.get_ylim()
ax.axvline(0.0703, color="#8b1a1a", lw=0.8, ls=":", alpha=0.8)
ax.axvline(PISO, color="#404040", lw=1.0, ls="--", alpha=0.9)
# Las etiquetas van como bloque en el hueco de abajo a la derecha, con el color y el trazo de su
# propia linea vertical, en lugar de flechas: con flechas cruzaban las tres curvas y el texto
# quedaba ilegible sobre los marcadores.
_yb = _lo + 0.34 * (_hi - _lo)
_dy = 0.085 * (_hi - _lo)
ax.plot([0.86, 0.99], [_yb, _yb], color="#8b1a1a", lw=0.9, ls=":")
ax.text(1.02, _yb, "óptimo de F_apt: m = 0,0703", fontsize=8.8, color="#8b1a1a", va="center")
ax.plot([0.86, 0.99], [_yb - _dy, _yb - _dy], color="#404040", lw=1.0, ls="--")
ax.text(1.02, _yb - _dy, "m = 0,30 adoptado (piso del rango)", fontsize=8.8,
        color="#404040", va="center")
ax.set_xlabel("m — peso de contraste")
ax.set_ylabel("aptitud (promedio, 3 escenas)")
ax.grid(alpha=0.3, lw=0.5)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.legend(fontsize=9.5)
fig.tight_layout()
fig.savefig("docs/figures/fig_aptitud_vs_m.png", dpi=170, facecolor="white")
print("Guardado:", out, "y docs/figures/fig_aptitud_vs_m.png")
