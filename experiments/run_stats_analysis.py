"""
run_stats_analysis.py
---------------------
Analisis estadistico de all_metrics.csv. Regenera:
  - descriptive_means.csv  : media de cada metrica por metodo
  - ranking_methods.csv    : ranking por metrica (con direccion correcta) y global
  - friedman_results.csv   : prueba de Friedman por metrica
  - wilcoxon_results.csv    : Wilcoxon pareado TopHat vs baselines, con correccion
                              de Holm y tamano de efecto (rank-biserial)
Respeta la direccion de optimizacion: Nabf menor=mejor; el resto mayor=mejor.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.metrics.evaluators import METRIC_DIRECTION

# Directorio de metricas: por defecto el oficial; se puede pasar otro como argumento
# (util para generar variantes del informe con otra configuracion del operador).
MDIR = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    ROOT / "experiments" / "results" / "metrics_reports")
df = pd.read_csv(MDIR / "all_metrics.csv")

# Set de métricas del análisis (alineado con Ortega y Espinoza: clásicas de
# actividad/información + SF, SSIM y PSNR). Se descartan Qabf, Nabf, SCD, VIF y
# las del review (FMI, Q0, QW, QE).
METRICS = ["EN", "SD", "FE", "MG", "MI_vis", "MI_ir", "SF", "SSIM", "PSNR"]
methods = sorted(df["method"].unique())
images = sorted(df["image"].unique())

# Matriz [imagen x metodo] por metrica
def metric_matrix(metric):
    piv = df.pivot(index="image", columns="method", values=metric)
    return piv.loc[images, methods]

# ---------------------------------------------------------------- means
means = df.groupby("method")[METRICS].mean().round(4)
means.to_csv(MDIR / "descriptive_means.csv")
# Las medias SIN redondear, para rankear. El round(4) es para publicar, pero rankear sobre el
# valor redondeado inventa empates que no existen: en MG dos metodos coincidian a cuatro decimales
# y el promedio de rangos resultante daba RatioPiramide 4,167 y DWT 4,500 donde correspondia 4,111
# y 4,556. La columna avg_rank_medias se publica en el informe, asi que la diferencia se lee.
means_full = df.groupby("method")[METRICS].mean()

# ---------------------------------------------------------------- ranking
# Ranking por PROMEDIO DE RANGOS INTRA-BLOQUE: para cada metrica se rankean los
# metodos dentro de cada imagen (1 = mejor) y se promedian los rangos sobre las
# imagenes. Es el acompanante estandar de la prueba de Friedman, que opera
# exactamente sobre esos rangos.
#
# La version anterior rankeaba las MEDIAS (7 numeros por metrica), lo que descarta
# la estructura de bloques y da un resultado distinto; se conserva en la columna
# avg_rank_medias solo para trazabilidad con los informes previos.
#
# FE es la entropia EN reescalada por una constante por escena (ver
# src.metrics.evaluators.fusion_efficiency), de modo que en el promedio de las nueve
# metricas la entropia pesa 2/9. Por eso se publica tambien avg_rank_sin_FE, que
# promedia solo las ocho metricas independientes.
rank_tbl = pd.DataFrame(index=methods)
for m in METRICS:
    asc = (METRIC_DIRECTION[m] == "min")  # si min es mejor, ascendente
    mat = metric_matrix(m)                # [imagenes x metodos]
    rk = mat.rank(axis=1, ascending=asc, method="average")
    rank_tbl[m] = rk.mean(axis=0)

METRICS_INDEP = [m for m in METRICS if m != "FE"]
rank_tbl["avg_rank"] = rank_tbl[METRICS].mean(axis=1).round(3)
rank_tbl["avg_rank_sin_FE"] = rank_tbl[METRICS_INDEP].mean(axis=1).round(3)
rank_tbl["avg_rank_medias"] = pd.concat(
    [means_full[m].rank(ascending=(METRIC_DIRECTION[m] == "min"), method="average")
     for m in METRICS], axis=1).mean(axis=1).round(3)
rank_tbl = rank_tbl.round(3).sort_values("avg_rank")
rank_tbl.to_csv(MDIR / "ranking_methods.csv")

# ---------------------------------------------------------------- Friedman
fr_rows = []
for m in METRICS:
    mat = metric_matrix(m).values  # [imagenes x metodos]
    chi2, p = stats.friedmanchisquare(*[mat[:, j] for j in range(mat.shape[1])])
    fr_rows.append({"metric": m, "chi2": chi2, "p_value": p,
                    "significant_05": p < 0.05})
pd.DataFrame(fr_rows).to_csv(MDIR / "friedman_results.csv", index=False)

# ---------------------------------------------------------------- Wilcoxon
# Metodos morfologicos (propuesta y clasico) contrastados contra el estado del arte
tophats = [x for x in methods if x.startswith("TopHat") or x.startswith("Propuesta")]
baselines = [x for x in methods if x not in tophats]

def rank_biserial(a, b):
    """Tamano de efecto matched-pairs rank-biserial para Wilcoxon."""
    d = a - b
    d = d[d != 0]
    if len(d) == 0:
        return 0.0
    ranks = stats.rankdata(np.abs(d))
    rpos = ranks[d > 0].sum()
    rneg = ranks[d < 0].sum()
    total = rpos + rneg
    return float((rpos - rneg) / total) if total > 0 else 0.0

# Contrastes: cada morfologico contra cada baseline, MAS el contraste entre los dos
# morfologicos (Propuesta vs Top-Hat clasico), que es el que aisla el aporte del banco
# de cinco elementos estructurantes y que la version anterior del script no producia.
CONTRASTES = [(th, bl) for th in tophats for bl in baselines]
if "Propuesta_Novedosa" in methods and "TopHat_Clasico" in methods:
    CONTRASTES.append(("Propuesta_Novedosa", "TopHat_Clasico"))

wx_rows = []
for m in METRICS:
    mat = metric_matrix(m)
    block = []
    for th, bl in CONTRASTES:
            a = mat[th].values
            b = mat[bl].values
            try:
                w, p = stats.wilcoxon(a, b)
            except ValueError:
                w, p = np.nan, 1.0
            block.append({
                "metric": m, "tophat": th, "baseline": bl,
                "mean_tophat": round(float(a.mean()), 4),
                "mean_baseline": round(float(b.mean()), 4),
                "diff": round(float(a.mean() - b.mean()), 4),
                "wilcoxon_W": w, "p_value": p,
                "effect_r": round(rank_biserial(a, b), 3),
            })
    # Correccion de Holm dentro de cada metrica
    bdf = pd.DataFrame(block)
    order = bdf["p_value"].fillna(1.0).argsort().values
    n = len(bdf)
    holm = np.empty(n)
    prev = 0.0
    for rank_i, idx in enumerate(order):
        adj = min(1.0, (n - rank_i) * bdf["p_value"].fillna(1.0).iloc[idx])
        prev = max(prev, adj)
        holm[idx] = prev
    # Sin redondear: un round(4) aplastaba a 0,0 todo p ajustado menor que 5e-05, y los
    # informes publicaban p-valores de exactamente cero, que son imposibles.
    bdf["p_holm"] = holm
    bdf["sig_holm_05"] = bdf["p_holm"] < 0.05
    wx_rows.append(bdf)

wx = pd.concat(wx_rows, ignore_index=True)
wx.to_csv(MDIR / "wilcoxon_results.csv", index=False)

print("=== Medias por metodo ===")
print(means.to_string())
print("\n=== Ranking global (menor = mejor) ===")
print(rank_tbl[["avg_rank"]].to_string())
print("\n=== Friedman ===")
print(pd.DataFrame(fr_rows)[["metric","chi2","p_value","significant_05"]].round(4).to_string(index=False))
print(f"\nWilcoxon: {len(wx)} contrastes guardados.")
