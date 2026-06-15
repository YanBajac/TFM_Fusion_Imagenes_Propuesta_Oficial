# -*- coding: utf-8 -*-
"""Resume detection_metrics.csv en una tabla y una figura comparativa."""
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
MDIR = ROOT / "experiments" / "results" / "metrics_reports"
df = pd.read_csv(MDIR / "detection_metrics.csv")

agg = df.groupby("method").agg(
    det_total=("n_det","sum"),
    det_por_img=("n_det","mean"),
    person_total=("n_person","sum"),
    vehiculo_total=("n_vehicle","sum"),
    imgs_con_det=("has_det","sum"),
    conf_media=("conf_mean", lambda s: s[s>0].mean() if (s>0).any() else 0.0),
    ms_media=("ms","mean"),
).round(3)
agg["FPS"] = (1000/agg["ms_media"]).round(1)
agg = agg.sort_values("det_total", ascending=False)
agg.to_csv(MDIR / "detection_summary.csv")
print(agg.to_string())

# figura
fig, ax = plt.subplots(1, 2, figsize=(14,6))
agg_sorted = agg.sort_values("det_total")
ax[0].barh(agg_sorted.index, agg_sorted["det_total"], color="#2980b9")
ax[0].set_title("Detecciones totales por método (20 imágenes)")
ax[1].barh(agg_sorted.index, agg_sorted["conf_media"], color="#27ae60")
ax[1].set_title("Confianza media de las detecciones")
fig.tight_layout()
fig.savefig(MDIR / "detection_comparison.png", dpi=150)
print("\nGuardado: detection_summary.csv y detection_comparison.png")
