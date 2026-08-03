# -*- coding: utf-8 -*-
"""Las nueve metricas de la tesis (todas 'mayor es mejor') en funcion del peso m.

Objetivo: determinar, desde la perspectiva de las metricas clasicas de actividad e
informacion (que mejoran al aumentar el realce), donde se ubica el optimo del peso de
contraste m, y si ese optimo cae en el rango [0,5; 2,0] reportado por el trabajo de
referencia (Ortega y Espinoza, 2025).

Usa el evaluador oficial del proyecto (src.metrics.evaluate_all), de modo que los
valores son los mismos que reporta el capitulo de resultados.

Salidas: experiments/results/metrics_reports/barrido_metricas_vs_m.csv
         (una fila por operador x m, con las 9 metricas y los agregados)
Uso: .venv\Scripts\python.exe -X utf8 experiments/barrido_metricas_vs_m.py
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import pandas as pd

from src.datasets import list_pairs, load_pair
from src.fusion.optimal_top_hat import fuse_optimal
from src.fusion.comparatives import tophat_classic_fusion
from src.metrics import evaluate_all

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MR = os.path.join(ROOT, "experiments", "results", "metrics_reports")
SALIDA = os.path.join(MR, "barrido_metricas_vs_m.csv")

# las nueve metricas del libro, todas de tipo "mayor es mejor"
METRICAS = ["EN", "SD", "FE", "MG", "MI_vis", "MI_ir", "SF", "SSIM", "PSNR"]
CLASICAS = ["EN", "SD", "FE", "MG", "SF"]          # actividad e informacion
FIDELIDAD = ["SSIM", "PSNR", "MI_vis", "MI_ir"]     # fidelidad a las fuentes

# constantes de normalizacion al estilo del trabajo de referencia (E/8, PSNR/100):
# cada metrica se divide por una constante que la lleva al orden de la unidad.
NORMA = {"EN": 8.0, "SD": 0.5, "FE": 8.0, "MG": 0.1, "SF": 50.0,
         "MI_vis": 4.0, "MI_ir": 4.0, "SSIM": 1.0, "PSNR": 100.0}

M_GRID = [0.05, 0.0703, 0.10, 0.20, 0.30, 0.50, 0.70, 1.00, 1.20, 1.50, 2.00]
CONFIGS = [("propuesta", 25), ("clasico", 25), ("clasico", 5)]


def fusionar(operador, v, i, r, m):
    if operador == "propuesta":
        return fuse_optimal(v, i, r, m, mode="sum")
    return tophat_classic_fusion(v, i, r=r, m=m)


def main():
    os.makedirs(MR, exist_ok=True)
    escenas = [load_pair(*p) for p in list_pairs()[::7]]   # 3 escenas del barrido PSO
    print(f"{len(escenas)} escenas representativas del TNO", flush=True)

    filas = []
    for operador, r in CONFIGS:
        for m in M_GRID:
            acum = {k: 0.0 for k in METRICAS}
            for v, i in escenas:
                res = evaluate_all(fusionar(operador, v, i, r, m), v, i)
                for k in METRICAS:
                    acum[k] += float(res[k])
            fila = {k: acum[k] / len(escenas) for k in METRICAS}
            fila.update(operador=operador, r=r, m=m)
            # agregados sin pesos, al estilo de la referencia (suma de terminos normalizados)
            fila["F_clasicas"] = sum(fila[k] / NORMA[k] for k in CLASICAS)
            fila["F_fidelidad"] = sum(fila[k] / NORMA[k] for k in FIDELIDAD)
            fila["F_nueve"] = sum(fila[k] / NORMA[k] for k in METRICAS)
            fila["F_o"] = fila["SSIM"] + fila["EN"] / 8.0 + fila["PSNR"] / 100.0
            filas.append(fila)
            print(f"  {operador:9s} r={r:2d} m={m:.4f} | "
                  f"F_clasicas={fila['F_clasicas']:.4f} F_nueve={fila['F_nueve']:.4f} "
                  f"F_o={fila['F_o']:.4f}", flush=True)

    df = pd.DataFrame(filas)[["operador", "r", "m"] + METRICAS
                             + ["F_clasicas", "F_fidelidad", "F_nueve", "F_o"]]
    df.to_csv(SALIDA, index=False)
    print("\nguardado", SALIDA, flush=True)

    # ---------- donde pica cada metrica ----------
    for operador, r in CONFIGS:
        sub = df[(df.operador == operador) & (df.r == r)]
        print(f"\n=== {operador} r={r} : m que maximiza cada metrica ===")
        for k in METRICAS:
            fila = sub.loc[sub[k].idxmax()]
            marca = "  <-- en [0,5; 2,0]" if fila.m >= 0.5 else ""
            print(f"  {k:7s} max={fila[k]:8.4f} en m={fila.m:.4f}{marca}")
        for agg in ["F_clasicas", "F_fidelidad", "F_nueve", "F_o"]:
            fila = sub.loc[sub[agg].idxmax()]
            marca = "  <-- en [0,5; 2,0]" if fila.m >= 0.5 else ""
            print(f"  {agg:12s} max={fila[agg]:8.4f} en m={fila.m:.4f}{marca}")

    # ---------- comparacion propuesta vs clasico en cada agregado ----------
    print("\n=== propuesta (r=25) vs clasico publicado (r=5), en su mejor m por agregado ===")
    prop = df[(df.operador == "propuesta") & (df.r == 25)]
    clas = df[(df.operador == "clasico") & (df.r == 5)]
    for agg in ["F_clasicas", "F_nueve", "F_o"]:
        p = prop.loc[prop[agg].idxmax()]; c = clas.loc[clas[agg].idxmax()]
        gana = "PROPUESTA" if p[agg] > c[agg] else "clasico"
        print(f"  {agg:12s} propuesta {p[agg]:.4f} (m={p.m:.4f}) | "
              f"clasico {c[agg]:.4f} (m={c.m:.4f}) -> gana {gana}")


if __name__ == "__main__":
    main()
