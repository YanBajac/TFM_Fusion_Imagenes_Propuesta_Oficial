# -*- coding: utf-8 -*-
"""Define la parte de prueba final de la deteccion en M3FD y sus grupos para la inferencia.

La prueba es la union de los cuadros 'test' y 'val' de m3fd_v2_particion.csv: la validacion no participa
en el entrenamiento (el seguimiento usa los cuadros sobrantes), asi que se suma a la prueba. Se aplican
dos filtros de fuga contra los 2000 cuadros de entrenamiento:

  1. casi duplicado en el visible: SSIM >= mediana del SSIM entre cuadros consecutivos (128 x 96), con
     preseleccion de los 10 candidatos de mayor correlacion. Ya se aplico a 'test' en la particion; aca se
     aplica tambien a 'val';
  2. las dos camaras: la menor de las dos correlaciones (visible e infrarroja, miniaturas de 64 x 48
     normalizadas) contra algun cuadro de entrenamiento supera el primer cuartil de esa misma medida entre
     cuadros consecutivos.

Los grupos son los bloques de la particion que quedan en la prueba, unidos cuando son contiguos.

Salida: experiments/results/metrics_reports/m3fd_v2_prueba.csv (id, parte, tramo, grupo, filtros, entra)

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/detection_m3fd/prueba_v2.py
"""
import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from skimage.metrics import structural_similarity as ssim

ROOT = Path(__file__).resolve().parents[2]
M3FD = ROOT / "data" / "M3FD_Detection"
MR = ROOT / "experiments" / "results" / "metrics_reports"


def cargar(i, carpeta):
    return cv2.imread(str(M3FD / carpeta / f"{i:05d}.png"), cv2.IMREAD_GRAYSCALE)


def vec(im, tam):
    v = cv2.resize(im, tam, interpolation=cv2.INTER_AREA).astype(np.float64).ravel()
    return (v - v.mean()) / (v.std() + 1e-9)


def main():
    part = pd.read_csv(MR / "m3fd_v2_particion.csv")
    ids = part.id.astype(int).tolist()
    forma, mv, mi, s128 = {}, {}, {}, {}
    for i in ids:
        a, b = cargar(i, "Vis"), cargar(i, "Ir")
        forma[i] = a.shape
        mv[i], mi[i] = vec(a, (64, 48)), vec(b, (64, 48))
        s128[i] = cv2.resize(a, (128, 96), interpolation=cv2.INTER_AREA)
    n = mv[ids[0]].size

    # umbrales, medidos entre cuadros consecutivos
    cons_ssim, cons_min = [], []
    for a, b in zip(ids[:-1], ids[1:]):
        if b == a + 1 and forma[a] == forma[b]:
            cons_ssim.append(ssim(s128[a], s128[b], data_range=255))
            cons_min.append(min(mv[a] @ mv[b], mi[a] @ mi[b]) / n)
    u1 = float(np.median(cons_ssim))
    u2 = float(np.percentile(cons_min, 25))
    print(f"  filtro 1: SSIM visible >= {u1:.3f} (mediana entre consecutivos)")
    print(f"  filtro 2: menor correlacion de las dos camaras >= {u2:.3f} (primer cuartil entre consecutivos)")

    tr = part[part.parte == "train"].id.astype(int).values
    cand = part[part.parte.isin(["test", "val"])].copy()
    ce = cand.id.astype(int).values
    Vtr, Itr = np.stack([mv[i] for i in tr]), np.stack([mi[i] for i in tr])
    Vte, Ite = np.stack([mv[i] for i in ce]), np.stack([mi[i] for i in ce])
    cv_, ci_ = Vte @ Vtr.T / n, Ite @ Itr.T / n
    minimo = np.minimum(cv_, ci_)
    cand["corr_min_max"] = minimo.max(axis=1)
    cand["filtro2"] = cand.corr_min_max >= u2
    top = np.argsort(-cv_, axis=1)[:, :10]
    f1 = []
    for k, i in enumerate(ce):
        s = max((ssim(s128[i], s128[tr[j]], data_range=255) for j in top[k] if forma[tr[j]] == forma[i]),
                default=0.0)
        f1.append(s >= u1)
    cand["filtro1"] = f1
    # los 'test' que la particion ya habia sacado por el filtro 1 no estan en cand; los 'val' si
    cand["entra"] = ~(cand.filtro1 | cand.filtro2)

    # grupos: bloques contiguos entre los que quedan
    bloques = sorted(cand[cand.entra].tramo.unique())
    gid, g, prev = {}, -1, None
    for b in bloques:
        if prev is None or b != prev + 1:
            g += 1
        gid[b] = g
        prev = b
    cand["grupo"] = cand.tramo.map(gid)
    cand.to_csv(MR / "m3fd_v2_prueba.csv", index=False)

    q = cand[cand.entra]
    print(f"\n  candidatos: {len(cand)} ({(cand.parte == 'test').sum()} de prueba y "
          f"{(cand.parte == 'val').sum()} de validacion)")
    print(f"  salen por el filtro 1: {int(cand.filtro1.sum())}; por el filtro 2: {int(cand.filtro2.sum())}")
    print(f"  prueba final: {len(q)} cuadros, {int(q.personas.sum())} personas y {int(q.luces.sum())} luces")
    print(f"  {q.tramo.nunique()} bloques en {q.grupo.nunique()} grupos; las luces estan en "
          f"{q[q.luces > 0].grupo.nunique()} grupos")
    print(q.groupby("grupo").agg(cuadros=("id", "size"), personas=("personas", "sum"),
                                 luces=("luces", "sum")).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
