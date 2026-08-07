# -*- coding: utf-8 -*-
"""Montajes cualitativos (20 escenas TNO): VIS, IR, los comparativos, la referencia y la propuesta.

Calcula las fusiones directamente con src/fusion (no depende de imagenes pre-fusionadas).

LA METODOLOGIA DE LA REFERENCIA ES UNA ENTRADA APARTE, no el comparativo «Top-Hat clasico».
Aquel corre con r = 5 y m = 1, la parametrizacion manual clasica. La metodologia de Ortega y
Espinoza es el MISMO operador de disco unico pero con el (r, m) que halla su PSO, y sobre el
corpus TNO ese barrido devuelve r = 25 y m = 0,30 —verificado en
experiments/results/metrics_reports/pso_grid_search_fo_clasico.csv, donde la mejor aptitud es
Fo = 1,7544 en r = 25, contra 1,7507 en r = 1—. Da la misma configuracion que la propuesta, de
modo que ponerlas una al lado de la otra aisla el BANCO DE CINCO ELEMENTOS frente al disco unico
a hiperparametros identicos: es la ablacion del operador, vista a ojo.

Sin esa columna el montaje comparaba la propuesta optimizada contra un clasico sin optimizar, y
la diferencia mezclaba operador, radio y peso.

Uso (desde la raiz del repo):  .venv\Scripts\python.exe -X utf8 experiments/make_montajes_cualitativos.py
"""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, ".")
from src.datasets import list_pairs, load_pair
from src.fusion import (fuse_optimal, laplacian_pyramid_fusion, ratio_pyramid_fusion,
                        dwt_fusion, dtcwt_fusion, curvelet_fusion, tophat_classic_fusion)

# Hiperparametros de la propuesta (PSO con la aptitud F_o y el rango publicado)
PROP_R, PROP_M = 25, 0.30

# Los de la referencia NO se escriben a mano: se leen de su propio barrido, la celda de mejor
# aptitud. Si se rehace el experimento, el montaje sigue al dato.
_gc = pd.read_csv("experiments/results/metrics_reports/pso_grid_search_fo_clasico.csv")
_best = _gc.loc[_gc.Fo_opt.idxmax()]
REF_R, REF_M = int(_best.r_opt), float(_best.m_opt)
print(f"referencia (disco unico, su PSO): r = {REF_R}, m = {REF_M:.2f}, "
      f"Fo = {_best.Fo_opt:.4f}")

AZUL, GRANATE = "#1f4e79", "#c00000"

OUT = "docs/figures/cualitativas/"
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.family": "serif"})

CELLS = [
    ("VIS", None),
    ("IR", None),
    ("Pirámide Laplace (LP)", lambda v, i: laplacian_pyramid_fusion(v, i, levels=4)),
    ("Ratio Pyramid (RP)", lambda v, i: ratio_pyramid_fusion(v, i, levels=4)),
    ("DWT", lambda v, i: dwt_fusion(v, i, levels=3)),
    ("DTCWT", lambda v, i: dtcwt_fusion(v, i, levels=4)),
    ("Curvelet (CVT)", lambda v, i: curvelet_fusion(v, i, levels=3)),
    # los tres ultimos son la escalera que aisla el aporte: parametrizacion manual -> el mismo
    # disco con el (r, m) de su PSO -> el banco de cinco con esos mismos (r, m).
    ("Top-Hat clásico (r=5, m=1)", lambda v, i: tophat_classic_fusion(v, i, r=5, m=1.0)),
    # Estas dos van en la misma fila y con el titulo en dos lineas: a cuatro columnas el rotulo de
    # una sola linea se recortaba, y ademas asi la primera linea nombra lo que las distingue —el
    # disco unico contra el banco de cinco— que es el motivo de ponerlas juntas. Los (r, m) son
    # identicos, de modo que lo unico que cambia entre los dos paneles es el operador.
    (f"Referencia: disco único\n(su PSO: r={REF_R}, m={REF_M:.2f})".replace(".", ","),
     lambda v, i: tophat_classic_fusion(v, i, r=REF_R, m=REF_M)),
    (f"Propuesta: banco de 5\n(r={PROP_R}, m={PROP_M:.2f})".replace(".", ","),
     lambda v, i: fuse_optimal(v, i, r=PROP_R, m=PROP_M, mode="sum")),
]

# Cuatro columnas y no tres, por dos razones concretas. Con tres, las diez celdas dan cuatro filas
# y la figura pasa de 8,2 a 10,9 pulgadas de alto: el informe mete DOS montajes por pagina y se
# desbordaria. Con cuatro quedan tres filas, la altura vuelve a la original y la paginacion no se
# toca. Y ademas la ultima fila queda con la referencia y la propuesta UNA AL LADO DE LA OTRA,
# que es exactamente la comparacion que aisla el banco.
NCOL = 4
NFIL = -(-len(CELLS) // NCOL)      # techo de la division

for idx, (vp, ip) in enumerate(list_pairs(), 1):
    vis, ir = load_pair(vp, ip)
    stem = os.path.splitext(os.path.basename(str(vp)))[0]
    fig, axes = plt.subplots(NFIL, NCOL, figsize=(11.5, 2.73 * NFIL))
    fig.patch.set_facecolor("white")
    for k, (lab, fn) in enumerate(CELLS):
        ax = axes.ravel()[k]
        img = vis if lab == "VIS" else ir if lab == "IR" else fn(vis, ir)
        ax.imshow(np.clip(img, 0, 1), cmap="gray", vmin=0, vmax=1)
        es_prop = lab.startswith("Propuesta")
        es_ref = lab.startswith("Referencia")
        color = GRANATE if es_prop else (AZUL if es_ref else "black")
        ax.set_title(lab, fontsize=9.5, pad=3, color=color,
                     fontweight="bold" if (es_prop or es_ref) else "normal")
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_edgecolor(GRANATE if es_prop else (AZUL if es_ref else "#555555"))
            sp.set_linewidth(2.2 if (es_prop or es_ref) else 0.6)
    for ax in axes.ravel()[len(CELLS):]:      # las celdas sobrantes de la ultima fila
        ax.axis("off")
    fig.suptitle(f"Escena {idx}: {stem.replace('_', ' ')[:60]}", fontsize=12, y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 1 - 0.03 * 3 / NFIL])
    fig.savefig(os.path.join(OUT, f"montaje_{idx:02d}.png"), dpi=105, facecolor="white")
    plt.close(fig)
    print(f"montaje {idx:02d} ok", flush=True)
print("listo:", OUT)
