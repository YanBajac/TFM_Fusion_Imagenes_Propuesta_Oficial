# -*- coding: utf-8 -*-
"""Control con imagenes degradadas, ordenando solo los siete metodos y el promedio simple.

POR QUE. run_stats_seis_metricas.py ordena las catorce entradas del control (control_negativo.csv): los siete
metodos, el promedio simple de las fuentes («base») y seis versiones degradadas de ese promedio, con ruido o
desenfocadas. El puesto de cada entrada depende de con quien se la ordena, y la Seccion 4.5.3 del libro informa
tambien el orden sin las seis versiones degradadas, en una escala de 1 a 8. Este script lo calcula con las
mismas funciones y las mismas seis metricas (EN, SD, MG, MI, SSIM y PSNR, con MI como promedio por imagen de
MI_vis y MI_ir).

Como control, comprueba que las metricas de los siete metodos en control_negativo.csv son las de
all_metrics.csv, imagen por imagen, salvo el redondeo: all_metrics.csv guarda seis decimales.

SALIDA en experiments/results/metrics_reports/: control_ocho_entradas.csv (el promedio simple figura como
«base», el nombre que le da control_negativo.csv)

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/control_ocho_entradas.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))

from run_stats_seis_metricas import SEIS, MDIR, con_mi_unificada, rangos_intrabloque  # noqa: E402

DEGRADADAS = ("ruido_", "desenfoque_")


def main():
    dcn = con_mi_unificada(pd.read_csv(MDIR / "control_negativo.csv"))
    allm = con_mi_unificada(pd.read_csv(MDIR / "all_metrics.csv"))
    metodos = sorted(allm["method"].unique())
    entradas = metodos + ["base"]
    sobran = sorted(b for b in dcn["brazo"].unique() if b not in entradas and not b.startswith(DEGRADADAS))
    if sobran or len(metodos) != 7:
        raise SystemExit(f"entradas inesperadas: {sobran}; metodos en all_metrics.csv: {len(metodos)}")

    # control: los siete metodos del control son los de all_metrics.csv
    dif = 0.0
    for m in metodos:
        a = dcn[dcn["brazo"] == m].set_index("imagen")[SEIS].sort_index()
        b = allm[allm["method"] == m].set_index("image")[SEIS].sort_index()
        if list(a.index) != list(b.index):
            raise SystemExit(f"{m}: las imagenes del control no son las de all_metrics.csv")
        dif = max(dif, float(np.abs(a.values - b.values).max()))
    print(f"  metodos del control frente a all_metrics.csv: diferencia maxima {dif:.1e}")
    if dif > 5e-7 + 1e-12:                    # medio digito del sexto decimal
        raise SystemExit("ABORTA: las metricas de los metodos no coinciden con all_metrics.csv")

    d8 = dcn[dcn["brazo"].isin(entradas)]
    tabla = rangos_intrabloque(d8, "brazo", "imagen", SEIS)
    tabla["rango_6"] = tabla[SEIS].mean(axis=1)
    tabla = tabla.round(3).sort_values("rango_6")
    tabla.insert(0, "puesto", range(1, len(tabla) + 1))
    tabla.to_csv(MDIR / "control_ocho_entradas.csv")

    print(f"\n  === Control con {len(tabla)} entradas, seis metricas, {d8['imagen'].nunique()} imagenes ===")
    print(tabla.to_string())
    print(f"  -> {(MDIR / 'control_ocho_entradas.csv').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
