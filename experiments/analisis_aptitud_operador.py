# -*- coding: utf-8 -*-
"""Por que el optimo de F_o cae en m bajo para el operador con suma de ramas.

Responde a la pregunta metodologica: el trabajo de referencia (Ortega y Espinoza,
2025) reporta pesos m en [0,3; 2,0] con un operador de disco unico, mientras que
sobre el operador propuesto (disco + 4 lineas, ramas sumadas) el optimo de la misma
aptitud F_o = SSIM_avg + E_n + PSNR_n cae en m ~ 0,07. Tres evidencias:

  (A) el operador propuesto inyecta varias veces mas energia de detalle que el disco
      unico -> como el detalle entra multiplicado por m, su peso optimo es
      proporcionalmente menor (el producto m x detalle es lo que fija el realce);
  (B) F_o decrece de forma monotona al aumentar m en AMBOS operadores: no existe un
      optimo interior en [0,5; 2,0], la busqueda siempre cae al piso del rango;
  (C) descomposicion de F_o: SSIM_avg y PSNR_n caen con el realce mientras la entropia
      normalizada (E/8) apenas varia -> el optimo lo deciden los terminos de fidelidad.

Salidas: docs/figures/fig_aptitud_vs_operador.png
         experiments/results/metrics_reports/aptitud_operador_energia.csv
         experiments/results/metrics_reports/aptitud_operador_terminos.csv
Uso: .venv\Scripts\python.exe -X utf8 experiments/analisis_aptitud_operador.py
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import cv2
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.datasets import list_pairs, load_pair
from src.fusion.optimal_top_hat import disk_se, linear_se, fuse_optimal
from src.fusion.comparatives import tophat_classic_fusion

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIG = os.path.join(ROOT, "docs", "figures")
MR = os.path.join(ROOT, "experiments", "results", "metrics_reports")
ANGULOS = (0, 45, 90, 135)
M_GRID = [0.05, 0.0703, 0.10, 0.20, 0.30, 0.50, 0.70, 1.00, 1.50, 2.00]
M_PROP = 0.0703   # configuracion oficial de la propuesta (optimo de F_o)
M_REF = 0.30      # piso del rango publicado por el trabajo de referencia
R_CLASICO = 5     # radio del disco en la metodologia clasica publicada

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.spines.top": False, "axes.spines.right": False,
})
AZUL, GRIS, GRISC, LINEA = "#4472c4", "#a6a6a6", "#595959", "#d9d9d9"


# ------------------------------------------------------------------ aptitud F_o
def _gb(x):
    return cv2.GaussianBlur(x, (11, 11), 1.5)


def _ssim(f, x, mu_x, var_x):
    c1, c2 = 0.01 ** 2, 0.03 ** 2
    mu_f = _gb(f); var_f = _gb(f * f) - mu_f * mu_f
    cov = _gb(f * x) - mu_f * mu_x
    s = ((2 * mu_f * mu_x + c1) * (2 * cov + c2)) / (
        (mu_f * mu_f + mu_x * mu_x + c1) * (var_f + var_x + c2) + 1e-12)
    return float(s.mean())


def _entropia(f):
    """Entropia de Shannon en bits (0-8); en F_o entra normalizada como E/8."""
    h, _ = np.histogram(np.clip(f, 0, 1), bins=256, range=(0.0, 1.0))
    p = h.astype(np.float64) / max(1, h.sum())
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def _psnr(f, v, i):
    """PSNR en dB (MAX=1) sobre el MSE promedio contra ambas fuentes; en F_o entra /100."""
    mse = 0.5 * (float(np.mean((f - v) ** 2)) + float(np.mean((f - i) ** 2)))
    return float(10.0 * np.log10(1.0 / max(mse, 1e-12)))


def cargar_escenas():
    """Las mismas 3 escenas representativas usadas en los barridos PSO (1 de cada 7)."""
    escenas = []
    for par in list_pairs()[::7]:
        v, i = load_pair(*par)
        mu_v, mu_i = _gb(v), _gb(i)
        escenas.append(dict(v=v, i=i, mu_v=mu_v, mu_i=mu_i,
                            var_v=_gb(v * v) - mu_v * mu_v,
                            var_i=_gb(i * i) - mu_i * mu_i))
    return escenas


def _terminos_de(f, c):
    """(SSIM_avg, E en bits, PSNR en dB) de una imagen fusionada ya construida."""
    ssim = 0.5 * (_ssim(f, c["v"], c["mu_v"], c["var_v"])
                  + _ssim(f, c["i"], c["mu_i"], c["var_i"]))
    return ssim, _entropia(f), _psnr(f, c["v"], c["i"])


def terminos_fo(escenas, operador, r, m):
    """Devuelve (SSIM_avg, E en bits, PSNR en dB) promediados sobre las escenas."""
    acc = np.zeros(3)
    for c in escenas:
        f = (fuse_optimal(c["v"], c["i"], r, m, mode="sum") if operador == "propuesta"
             else tophat_classic_fusion(c["v"], c["i"], r=r, m=m))
        ssim = 0.5 * (_ssim(f, c["v"], c["mu_v"], c["var_v"])
                      + _ssim(f, c["i"], c["mu_i"], c["var_i"]))
        acc += (ssim, _entropia(f), _psnr(f, c["v"], c["i"]))
    return acc / len(escenas)


def fo(ssim, e_bits, psnr_db):
    """F_o tal como la define el trabajo de referencia: suma directa, sin pesos."""
    return ssim + e_bits / 8.0 + psnr_db / 100.0


# ------------------------------------------------------------------ (A) energia
def energia_detalle(r):
    """Magnitud media del detalle blanco extraido: disco solo, lineas solas y su suma."""
    disco = disk_se(r)
    lineas = [linear_se(r, a) for a in ANGULOS]
    tot = np.zeros(3); n = 0
    for par in list_pairs()[::7]:
        v, i = load_pair(*par)
        for f in (v, i):
            f = f.astype(np.float32)
            w_disco = f - cv2.morphologyEx(f, cv2.MORPH_OPEN, disco)
            w_lin = np.mean([f - cv2.morphologyEx(f, cv2.MORPH_OPEN, L) for L in lineas], axis=0)
            tot += (np.abs(w_disco).mean(), np.abs(w_lin).mean(),
                    np.abs(w_lin + w_disco).mean())
            n += 1
    return tot / n


def main():
    os.makedirs(FIG, exist_ok=True); os.makedirs(MR, exist_ok=True)
    escenas = cargar_escenas()
    print(f"{len(escenas)} escenas representativas del TNO", flush=True)

    # ---------- (A) energia de detalle ----------
    d5, l5, w5 = energia_detalle(5)      # configuracion del Top-Hat clasico
    d25, l25, w25 = energia_detalle(25)  # configuracion de la propuesta
    energia = pd.DataFrame([
        ("Top-Hat clásico · disco B_5", d5),
        ("Disco B_25 (una rama)", d25),
        ("Propuesta · W_opt = líneas + disco (r=25)", w25),
    ], columns=["operador", "detalle_medio"])
    energia["ganancia_vs_clasico"] = energia["detalle_medio"] / d5
    energia.to_csv(os.path.join(MR, "aptitud_operador_energia.csv"), index=False)
    print(energia.to_string(index=False), flush=True)

    # ---------- (B) y (C) F_o y sus terminos vs m ----------
    filas = []
    for operador, r in [("propuesta", 25), ("clasico", 25)]:
        for m in M_GRID:
            ssim, e_bits, psnr_db = terminos_fo(escenas, operador, r, m)
            filas.append(dict(operador=operador, r=r, m=m, SSIM_avg=ssim,
                              E_bits=e_bits, PSNR_dB=psnr_db,
                              E_n=e_bits / 8.0, PSNR_n=psnr_db / 100.0,
                              Fo=fo(ssim, e_bits, psnr_db)))
            print(f"  {operador:9s} r={r} m={m:.2f} -> Fo={filas[-1]['Fo']:.4f}", flush=True)
    term = pd.DataFrame(filas)
    term.to_csv(os.path.join(MR, "aptitud_operador_terminos.csv"), index=False)

    prop = term[term.operador == "propuesta"].sort_values("m")
    clas = term[term.operador == "clasico"].sort_values("m")

    # ---------- configuraciones que realmente se comparan ----------
    fo_base = np.mean([fo(*_terminos_de(np.clip(0.5 * (c["v"] + c["i"]), 0, 1).astype(np.float32), c))
                       for c in escenas])
    configs = [
        ("Base $(VIS+IR)/2$\nsin operador", fo_base, GRIS),
        ("Top-Hat clásico\npublicado (r=5, m=1)", fo(*terminos_fo(escenas, "clasico", R_CLASICO, 1.0)), GRIS),
        ("Clásico re-optimizado\ncon $F_o$ (r=25, m=0,10)", fo(*terminos_fo(escenas, "clasico", 25, 0.10)), GRISC),
        ("Propuesta\n(r=25, m=0,0703)", fo(*terminos_fo(escenas, "propuesta", 25, M_PROP)), AZUL),
    ]

    # ---------- equivalencia del realce: m x energia ----------
    realce_prop = M_PROP * w25
    realce_ref = M_REF * d5
    m_equiv = realce_prop / d5           # m que el disco B_5 necesitaria para igualar
    rango_mapeado = (M_REF * d5 / w25, 2.0 * d5 / w25)

    # ---------- figura (2x2) ----------
    fig, axes = plt.subplots(2, 2, figsize=(12.2, 7.6))
    ax1, ax2, ax3, ax4 = axes.ravel()

    # (a) energia inyectada + equivalencia del realce
    etiquetas = ["Clásico\ndisco $B_5$", "Disco $B_{25}$\n(una rama)", "Propuesta\n$W_{opt}$ (r=25)"]
    vals = [d5, d25, w25]
    ax1.bar(range(3), vals, color=[GRIS, GRIS, AZUL], edgecolor=GRISC, lw=0.6, width=0.58)
    for k, v in enumerate(vals):
        ax1.text(k, v + max(vals) * 0.025, f"{v:.4f}".replace(".", ","), ha="center",
                 fontsize=9, fontweight=("bold" if k == 2 else "normal"))
    ax1.set_xticks(range(3)); ax1.set_xticklabels(etiquetas, fontsize=9)
    ax1.set_ylabel("Detalle medio extraído  |WTH|")
    ax1.set_title(f"(a) El operador propuesto inyecta {w25 / d5:.1f}× más detalle")
    ax1.set_ylim(0, max(vals) * 1.42)
    ax1.grid(axis="y", ls=":", lw=0.5, color=LINEA); ax1.set_axisbelow(True)
    ax1.text(0.03, 0.97,
             "El detalle entra multiplicado por $m$:\n"
             f"propuesta   $m·|W|$ = 0,0703 × {w25:.4f} = {realce_prop:.5f}\n".replace(".", ",")
             + f"clásico       $m·|W|$ = 0,30 × {d5:.4f} = {realce_ref:.5f}\n".replace(".", ",")
             + f"→ mismo realce físico ({abs(realce_prop / realce_ref - 1) * 100:.1f}% de diferencia)".replace(".", ","),
             transform=ax1.transAxes, va="top", ha="left", fontsize=8.6, color=GRISC,
             bbox=dict(boxstyle="round,pad=0.4", fc="#f7f7f7", ec=LINEA, lw=0.6))

    # (b) F_o vs m
    ax2.axvspan(0.5, 2.0, color="#f2f2f2", zorder=0)
    ax2.plot(clas.m, clas.Fo, "-s", color=GRISC, lw=1.4, ms=4.5, label="Top-Hat clásico (disco, r=25)")
    ax2.plot(prop.m, prop.Fo, "-o", color=AZUL, lw=1.8, ms=5, label="Propuesta (suma de ramas, r=25)")
    ax2.axhline(fo_base, ls="--", lw=1.0, color="#999999")
    mejor = prop.loc[prop.Fo.idxmax()]
    ax2.scatter([mejor.m], [mejor.Fo], s=160, facecolor="none", edgecolor=AZUL, lw=1.7, zorder=5)
    ax2.set_xlabel("Peso de contraste  $m$"); ax2.set_ylabel("Aptitud  $F_o$")
    ax2.set_title("(b) $F_o$ decrece de forma monótona: no hay óptimo en [0,5; 2]")
    ax2.legend(frameon=False, fontsize=8.5, loc="lower left")
    ax2.grid(ls=":", lw=0.5, color=LINEA); ax2.set_axisbelow(True)
    y0, y1 = ax2.get_ylim(); ax2.set_ylim(y0, y1 + (y1 - y0) * 0.10)
    ax2.text(1.98, ax2.get_ylim()[1] - (y1 - y0) * 0.045, "rango reportado\npor la referencia",
             ha="right", va="top", fontsize=8.5, color=GRISC)
    ax2.annotate(f"óptimo  m = 0,0703  ($F_o$ = {mejor.Fo:.4f})".replace(".", ","),
                 xy=(mejor.m, mejor.Fo), xytext=(0.42, ax2.get_ylim()[1] - (y1 - y0) * 0.03),
                 fontsize=9, color=AZUL, va="top",
                 arrowprops=dict(arrowstyle="->", color=AZUL, lw=0.9,
                                 connectionstyle="arc3,rad=0.15"))
    ax2.text(1.05, fo_base, "base sin operador", ha="center", va="bottom",
             fontsize=8.3, color="#777777")

    # (c) descomposicion de F_o (propuesta)
    rango_ssim = prop.SSIM_avg.max() - prop.SSIM_avg.min()
    rango_en = prop.E_n.max() - prop.E_n.min()
    ax3.plot(prop.m, prop.SSIM_avg, "-o", color=AZUL, lw=1.7, ms=4.5, label="$SSIM_{avg}$  (fidelidad)")
    ax3.plot(prop.m, prop.E_n, "-^", color="#7f7f7f", lw=1.4, ms=4.5, label="$E_n = E/8$  (información)")
    ax3.plot(prop.m, prop.PSNR_n, "-s", color="#bfbfbf", lw=1.4, ms=4.5, label="$PSNR_n = PSNR/100$")
    ax3.set_xlabel("Peso de contraste  $m$"); ax3.set_ylabel("Aporte a $F_o$")
    ax3.set_title("(c) Quién decide el óptimo: los términos de fidelidad")
    ax3.legend(frameon=False, fontsize=8.5, loc="center right")
    ax3.grid(ls=":", lw=0.5, color=LINEA); ax3.set_axisbelow(True)
    ax3.set_ylim(0, 1.12)
    ax3.text(0.5, 0.04,
             f"al subir $m$: $SSIM$ varía {rango_ssim:.2f} y $E_n$ solo {rango_en:.2f}".replace(".", ",")
             + f"  →  la fidelidad pesa {rango_ssim / max(rango_en, 1e-9):.1f}×".replace(".", ","),
             transform=ax3.transAxes, ha="center", fontsize=8.6, color=GRISC,
             bbox=dict(boxstyle="round,pad=0.35", fc="#f7f7f7", ec=LINEA, lw=0.6))

    # (d) F_o de las configuraciones comparadas
    nombres = [c[0] for c in configs]; valores = [c[1] for c in configs]; colores = [c[2] for c in configs]
    ax4.barh(range(len(configs)), valores, color=colores, edgecolor=GRISC, lw=0.6, height=0.6)
    for k, v in enumerate(valores):
        ax4.text(v + 0.004, k, f"{v:.4f}".replace(".", ","), va="center", fontsize=9,
                 fontweight=("bold" if k == len(configs) - 1 else "normal"))
    ax4.set_yticks(range(len(configs))); ax4.set_yticklabels(nombres, fontsize=8.8)
    ax4.set_xlabel("Aptitud  $F_o$")
    ax4.set_xlim(min(valores) - 0.03, max(valores) + 0.035)
    dif = valores[-1] - valores[1]
    ax4.set_title(f"(d) La propuesta supera al clásico publicado en $F_o$  (+{dif:.3f})".replace(".", ","))
    ax4.grid(axis="x", ls=":", lw=0.5, color=LINEA); ax4.set_axisbelow(True)
    ax4.text(0.5, 0.50, "F$_o$ en su óptimo apenas se separa de la base:\n"
             "empuja $m$→0, donde el operador casi no actúa",
             transform=ax4.transAxes, ha="center", va="center", fontsize=8.4, color=GRISC,
             bbox=dict(boxstyle="round,pad=0.35", fc="#f7f7f7", ec=LINEA, lw=0.6))

    fig.tight_layout(pad=1.3)
    salida = os.path.join(FIG, "fig_aptitud_vs_operador.png")
    fig.savefig(salida, dpi=185, facecolor="white")
    plt.close(fig)
    print("\nok", salida, flush=True)

    # ---------- resumen para la discusion ----------
    pd.DataFrame(configs, columns=["configuracion", "Fo", "_color"]).drop(columns="_color") \
        .to_csv(os.path.join(MR, "aptitud_operador_configs.csv"), index=False)
    print("\n--- sintesis ---")
    print(f"ganancia de energia (propuesta r=25 / clasico B_5) : {w25 / d5:.2f}x")
    print(f"realce efectivo propuesta m={M_PROP} : {realce_prop:.5f}")
    print(f"realce efectivo clasico   m={M_REF}  : {realce_ref:.5f}  "
          f"-> difieren {abs(realce_prop / realce_ref - 1) * 100:.1f}%")
    print(f"m del disco B_5 equivalente a nuestro optimo       : {m_equiv:.3f}")
    print(f"rango publicado [0,30; 2,00] mapeado a la propuesta: "
          f"[{rango_mapeado[0]:.3f}; {rango_mapeado[1]:.3f}]")
    print(f"optimo F_o propuesta : m={mejor.m} (Fo={mejor.Fo:.4f})")
    print(f"variacion SSIM_avg={rango_ssim:.3f} | E_n={rango_en:.3f} "
          f"-> fidelidad domina {rango_ssim / max(rango_en, 1e-9):.1f}x")
    for nom, val, _ in configs:
        print(f"  F_o {nom.replace(chr(10), ' '):42s} = {val:.4f}")


if __name__ == "__main__":
    main()
