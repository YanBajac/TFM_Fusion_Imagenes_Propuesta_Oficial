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

MDIR = ROOT / "experiments" / "results" / "metrics_reports"
df = pd.read_csv(MDIR / "all_metrics.csv")

METRICS = ["EN", "SD", "FE", "MG", "MI_vis", "MI_ir",
           "SF", "Qabf", "Nabf", "SSIM", "SCD", "VIF"]
methods = sorted(df["method"].unique())
images = sorted(df["image"].unique())

# Matriz [imagen x metodo] por metrica
def metric_matrix(metric):
    piv = df.pivot(index="image", columns="method", values=metric)
    return piv.loc[images, methods]

# ---------------------------------------------------------------- means
means = df.groupby("method")[METRICS].mean().round(4)
means.to_csv(MDIR / "descriptive_means.csv")

# ---------------------------------------------------------------- ranking
# Para cada metrica, rankear metodos por la media (1 = mejor).
rank_tbl = pd.DataFrame(index=methods)
for m in METRICS:
    asc = (METRIC_DIRECTION[m] == "min")  # si min es mejor, ascendente
    # rank de las medias; menor rank = mejor
    r = means[m].rank(ascending=asc, method="average")
    rank_tbl[m] = r
rank_tbl["avg_rank"] = rank_tbl[METRICS].mean(axis=1).round(3)
rank_tbl = rank_tbl.round(2).sort_values("avg_rank")
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
tophats = [x for x in methods if x.startswith("TopHat")]
baselines = [x for x in methods if not x.startswith("TopHat")]

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

wx_rows = []
for m in METRICS:
    mat = metric_matrix(m)
    block = []
    for th in tophats:
        for bl in baselines:
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
    bdf["p_holm"] = holm.round(4)
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
