# -*- coding: utf-8 -*-
"""run_control_negativo.py — validez discriminativa del conjunto de nueve metricas.

QUE PRUEBA. El conjunto de nueve metricas del trabajo es enteramente de tipo "mayor es mejor",
de modo que inyectar mas actividad de alta frecuencia solo puede subir el puntaje: no hay
ningun termino que castigue el ruido ni los artefactos (la unica metrica implementada que lo
hace, Nabf, no forma parte del conjunto). Si eso es asi, una "fusion" sin ningun merito -la
media de las fuentes mas ruido gaussiano- deberia escalar el ranking al aumentar la varianza
del ruido.

Este control lo mide. Es un CONTROL NEGATIVO en el sentido clasico: un procedimiento que
sabemos malo, cuyo puntaje deberia ser bajo. Si puntua alto, lo que falla es el criterio.

Brazos:
  base                 (VIS+IR)/2, sin operador
  desenfoque_k         base suavizada con un nucleo gaussiano de tamano k (destruye detalle)
  ruido_sigma          base + N(0, sigma), con sigma creciente (agrega detalle FALSO)
  <metodos reales>     los siete metodos del benchmark, para ubicar el ruido entre ellos

Salidas (experiments/results/metrics_reports/):
  control_negativo.csv            una fila por brazo x imagen
  control_negativo_ranking.csv    rango intra-bloque de cada brazo, con y sin Nabf
Uso:
  .venv\Scripts\python.exe -X utf8 experiments/run_control_negativo.py [--semilla 0]
"""
import argparse
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.datasets import list_pairs, load_pair
from src.metrics import evaluate_all
from src.metrics.evaluators import METRIC_DIRECTION
from experiments.run_all_fusions import METHODS  # los siete metodos, con su configuracion

SALIDA = ROOT / "experiments" / "results" / "metrics_reports"
NUEVE = ["EN", "SD", "FE", "MG", "MI_vis", "MI_ir", "SF", "SSIM", "PSNR"]
SIGMAS = [0.02, 0.05, 0.10, 0.20]
DESENFOQUES = [5, 11]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semilla", type=int, default=0)
    a = ap.parse_args()

    pares = list_pairs()
    print(f"control negativo sobre {len(pares)} pares | semilla {a.semilla}")
    t0 = time.time()
    filas = []
    for k, (vp, ip) in enumerate(pares, 1):
        vis, ir = load_pair(vp, ip)
        base = np.clip(0.5 * (vis.astype(np.float32) + ir.astype(np.float32)), 0, 1)
        brazos = {"base": base}
        for kk in DESENFOQUES:
            brazos[f"desenfoque_{kk}"] = cv2.GaussianBlur(base, (kk, kk), 0)
        # el ruido usa una semilla por imagen para que el experimento sea reproducible
        rng = np.random.default_rng(a.semilla * 100000 + k)
        for s in SIGMAS:
            r = rng.normal(0.0, s, size=base.shape).astype(np.float32)
            brazos[f"ruido_{s:.2f}"] = np.clip(base + r, 0, 1)
        for nombre, fn in METHODS.items():
            brazos[nombre] = fn(vis, ir)
        for nombre, f in brazos.items():
            filas.append({"brazo": nombre, "imagen": vp.stem, **evaluate_all(f, vis, ir)})
        print(f"  [{k:2d}/{len(pares)}] {vp.stem[:40]:40s} ({time.time() - t0:5.1f}s)", flush=True)

    df = pd.DataFrame(filas)
    SALIDA.mkdir(parents=True, exist_ok=True)
    df.to_csv(SALIDA / "control_negativo.csv", index=False)
    METS = [c for c in df.columns if c in METRIC_DIRECTION]

    def rangos(mets):
        out = {}
        for m in mets:
            piv = df.pivot(index="imagen", columns="brazo", values=m)
            out[m] = piv.rank(axis=1, ascending=(METRIC_DIRECTION[m] == "min"),
                              method="average").mean(axis=0)
        return pd.DataFrame(out).mean(axis=1)

    r9 = rangos(NUEVE)
    r9n = rangos(NUEVE + ["Nabf"])
    r17 = rangos(METS)
    res = pd.DataFrame({"rango_9": r9.round(3), "rango_9_mas_Nabf": r9n.round(3),
                        "rango_17": r17.round(3)}).sort_values("rango_9")
    res.to_csv(SALIDA / "control_negativo_ranking.csv")

    print(f"\nLISTO en {(time.time() - t0) / 60:.1f} min\n")
    print("=== RANGO INTRA-BLOQUE DE CADA BRAZO (menor = mejor) ===")
    print(res.to_string())

    PROP = "Propuesta_Novedosa"
    ruidos = [b for b in res.index if b.startswith("ruido_")]
    print("\n=== LECTURA ===")
    print(f"  posicion de la propuesta con las nueve metricas: "
          f"{list(res.sort_values('rango_9').index).index(PROP) + 1} de {len(res)}")
    for b in sorted(ruidos):
        pos = list(res.sort_values("rango_9").index).index(b) + 1
        mejor = res.loc[b, "rango_9"] < res.loc[PROP, "rango_9"]
        print(f"  {b:12s} puesto {pos:2d} de {len(res)} con nueve metricas"
              f"{'  <-- SUPERA A LA PROPUESTA' if mejor else ''}")
    print("\n  monotonia del ruido (si el rango mejora al subir sigma, el criterio premia el ruido):")
    for b in sorted(ruidos):
        print(f"    {b:12s} rango_9 = {res.loc[b, 'rango_9']:.3f}   "
              f"con Nabf = {res.loc[b, 'rango_9_mas_Nabf']:.3f}   "
              f"17 metricas = {res.loc[b, 'rango_17']:.3f}")
    print("\n  Nota: la columna con Nabf muestra el efecto de agregar UNA metrica que penaliza")
    print("  artefactos; es el contraste que justifica declarar la limitacion del conjunto.")


if __name__ == "__main__":
    main()
