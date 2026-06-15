# -*- coding: utf-8 -*-
"""Friedman + Wilcoxon (Holm) sobre las métricas de detección por método."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
MDIR = ROOT / "experiments" / "results" / "metrics_reports"
df = pd.read_csv(MDIR / "detection_metrics.csv")
METRICS = ["n_det", "conf_mean", "has_det"]
methods = sorted(df["method"].unique())
images = sorted(df["image"].unique())

def mat(metric):
    return df.pivot_table(index="image", columns="method", values=metric).reindex(index=images, columns=methods)

fr=[]
for m in METRICS:
    M=mat(m).fillna(0).values
    try:
        chi2,p=stats.friedmanchisquare(*[M[:,j] for j in range(M.shape[1])])
    except Exception:
        chi2,p=np.nan,np.nan
    fr.append({"metric":m,"chi2":chi2,"p_value":p,"sig_05":(p is not None and p<0.05)})
pd.DataFrame(fr).to_csv(MDIR/"detection_friedman.csv",index=False)

# Wilcoxon: cada metodo TopHat vs baselines (Promedio, Laplace, Curvelet, VIS, IR) en n_det y conf_mean
baselines=[b for b in ["Promedio","PiramideLaplace","Curvelet","VIS","IR"] if b in methods]
tophats=[t for t in methods if t.startswith("TopHat")]
rows=[]
for metric in ["n_det","conf_mean"]:
    M=mat(metric).fillna(0)
    for th in tophats:
        for bl in baselines:
            a,b=M[th].values,M[bl].values
            try: w,p=stats.wilcoxon(a,b)
            except ValueError: w,p=np.nan,1.0
            rows.append({"metric":metric,"tophat":th,"baseline":bl,
                         "mean_tophat":round(a.mean(),3),"mean_baseline":round(b.mean(),3),
                         "p_value":p})
pd.DataFrame(rows).to_csv(MDIR/"detection_wilcoxon.csv",index=False)
print("=== Friedman (detección) ==="); print(pd.DataFrame(fr).to_string(index=False))
print("\nGuardado detection_friedman.csv y detection_wilcoxon.csv")
