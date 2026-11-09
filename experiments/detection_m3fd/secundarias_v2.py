# -*- coding: utf-8 -*-
"""Medidas secundarias de la deteccion de objetos en M3FD (Seccion 3.5.4 del libro).

Se corre DESPUES de analizar_v2.py, con los mismos detectores. No interviene en el examen de la hipotesis:
ninguna de estas medidas se presenta como evidencia a favor.

  1. mAP50 y AP50 de personas y luces por entrada, con media y recorrido entre semillas. Se usan las
     mismas semillas que el analisis principal: el mismo numero para todas las entradas (regla de corte).
     Nota: m3fd_v2_map.csv sale de model.val(split="test"), que evalua las carpetas de prueba y de
     validacion completas (1197 cuadros), sin el segundo filtro de fuga que deja la prueba en 1067.
  2. La relacion entre calidad y deteccion: correlacion de Spearman, sobre los siete metodos, entre el
     rango promedio de las seis metricas en el TNO (ranking_seis_metricas.csv, menor es mejor) y la tasa
     equilibrada con el umbral principal (m3fd_v2_tasas.csv). Con siete puntos es un indicio, no una
     prueba.

Salidas: m3fd_v2_map_resumen.csv, m3fd_v2_calidad_deteccion.csv

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/detection_m3fd/secundarias_v2.py
"""
import sys
from pathlib import Path

import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
MR = ROOT / "experiments" / "results" / "metrics_reports"
REFERENCIA = ["VIS", "IR"]
FUSIONES = ["Promedio", "Propuesta_Novedosa", "TopHat_Clasico", "PiramideLaplace", "RatioPiramide",
            "DWT", "DTCWT", "Curvelet"]
METODOS = [e for e in FUSIONES if e != "Promedio"]


def main():
    mp = pd.read_csv(MR / "m3fd_v2_map.csv").drop_duplicates(["entrada", "semilla"])
    semillas = {e: sorted(mp.loc[mp.entrada == e, "semilla"]) for e in REFERENCIA + FUSIONES}
    faltan = [e for e, s in semillas.items() if not s]
    if faltan:
        print(f"  faltan entradas: {faltan}")
        return 1
    n = min(len(s) for s in semillas.values())
    usar = {(e, s) for e, ss in semillas.items() for s in ss[:n]}
    mp = mp[[(e, s) in usar for e, s in zip(mp.entrada, mp.semilla)]]
    cols = ["mAP50", "AP50_People", "AP50_Lamp"]
    res = mp.groupby("entrada")[cols].agg(["mean", "min", "max"]).round(4)
    res.columns = [f"{a}_{b}" for a, b in res.columns]
    res.insert(0, "semillas", n)
    res = res.sort_values("mAP50_mean", ascending=False)
    res.to_csv(MR / "m3fd_v2_map_resumen.csv")
    print(f"  mAP con {n} semilla(s) por entrada")
    print(res.to_string())

    rk = pd.read_csv(MR / "ranking_seis_metricas.csv", index_col=0)["rango_6"]
    ts = pd.read_csv(MR / "m3fd_v2_tasas.csv")
    ts = ts[ts.punto == "fppi"].set_index("entrada")["equilibrada"]
    d = pd.DataFrame({"rango_calidad": rk.loc[METODOS], "tasa_equilibrada": ts.loc[METODOS]})
    # el rango es menor-es-mejor y la tasa mayor-es-mejor: una rho NEGATIVA significa que el metodo
    # mejor ubicado en calidad es tambien el que mas detecta
    rho, p = stats.spearmanr(d.rango_calidad, d.tasa_equilibrada)
    d["rho_spearman"] = round(float(rho), 4)
    d["p"] = round(float(p), 4)
    d["semillas"] = n
    d.to_csv(MR / "m3fd_v2_calidad_deteccion.csv")
    print(f"\n  Spearman, rango de calidad contra tasa equilibrada, 7 metodos: rho = {rho:+.3f} (p = {p:.3f})")
    print("  (rho negativa: mejor calidad, mas deteccion)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
