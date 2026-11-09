# -*- coding: utf-8 -*-
"""Rango promedio de los siete metodos con las diecisiete metricas calculadas.

POR QUE. La Seccion 4.5.3 del libro compara el puesto de la propuesta segun el conjunto de metricas: con las
seis del analisis principal, con las nueve iniciales (ranking_methods.csv) y con las diecisiete que calcula
src.metrics.evaluate_all. Este script rehace la tercera clasificacion desde all_metrics.csv. En cada imagen
ordena los siete metodos por cada metrica (1 = mejor, con el sentido de METRIC_DIRECTION: Nabf es la unica
en la que menor es mejor; empates con rango medio), promedia los rangos sobre las imagenes y despues sobre
las diecisiete metricas, con el mismo peso para todas. La escala va de 1 a 7.

Si el CSV ya existe, antes de escribir comprueba que el calculo lo reproduce (mismos metodos, mismo orden
y la misma cifra hasta 1e-9). Si no coincide, no escribe.

SALIDA en experiments/results/metrics_reports/: ranking_17_metricas.csv

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/ranking_17_metricas.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MDIR = ROOT / "experiments" / "results" / "metrics_reports"
SALIDA = MDIR / "ranking_17_metricas.csv"

from src.metrics.evaluators import METRIC_DIRECTION  # noqa: E402


def ranking(df, metricas):
    """Promedio sobre las metricas del rango intra-imagen promedio de cada metodo."""
    rangos = {}
    for m in metricas:
        piv = df.pivot(index="image", columns="method", values=m)
        rangos[m] = piv.rank(axis=1, ascending=(METRIC_DIRECTION[m] == "min"),
                             method="average").mean(axis=0)
    return pd.DataFrame(rangos).mean(axis=1).sort_values()


def main():
    df = pd.read_csv(MDIR / "all_metrics.csv")
    metricas = [c for c in df.columns if c in METRIC_DIRECTION]
    if len(metricas) != 17:
        raise SystemExit(f"se esperaban 17 metricas en all_metrics.csv y hay {len(metricas)}")
    r = ranking(df, metricas)
    tabla = r.rename("rango_17").rename_axis("method").to_frame()
    tabla["puesto"] = range(1, len(tabla) + 1)
    print(f"  {df['method'].nunique()} metodos x {df['image'].nunique()} imagenes, {len(metricas)} metricas")
    print(tabla.round(3).to_string())

    # control: el CSV existente tiene que salir igual
    if SALIDA.exists():
        previo = pd.read_csv(SALIDA, index_col=0, float_precision="round_trip")
        mismo_orden = list(previo.index) == list(tabla.index) and list(previo.columns) == list(tabla.columns)
        dif = float(np.abs(previo["rango_17"].values - tabla["rango_17"].values).max()) if mismo_orden else np.inf
        puestos = mismo_orden and (previo["puesto"].values == tabla["puesto"].values).all()
        print(f"  control contra {SALIDA.name}: mismo orden {mismo_orden}; diferencia maxima {dif:.1e}")
        if not (mismo_orden and puestos and dif <= 1e-9):
            raise SystemExit(f"ABORTA: el calculo no reproduce {SALIDA.name}; no se escribe")

    tabla.to_csv(SALIDA)
    print(f"  -> {SALIDA.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
