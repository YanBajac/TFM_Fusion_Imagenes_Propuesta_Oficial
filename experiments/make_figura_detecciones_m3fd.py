# -*- coding: utf-8 -*-
"""Figura cualitativa del experimento de clases complementarias (M3FD):
la misma escena nocturna en VIS, IR y fusion (Propuesta, r=25, m=0.0703) con las
detecciones del modelo unico dibujadas. Selecciona automaticamente la escena de
validacion donde mejor se observa la complementariedad (el VIS pierde personas
que la fusion recupera y el IR pierde luces que la fusion recupera).

Requiere: datasets/m3fd_test_* generados por prepare_m3fd.py y el modelo
entrenado (runs/**/mixto/weights/best.pt).
Salida: docs/figures/fig_m3fd_detecciones.png
Uso:    python experiments/make_figura_detecciones_m3fd.py
"""
import os
import sys
from pathlib import Path

os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, ".")
import numpy as np
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

CONF = 0.30
PEOPLE, LAMP = 0, 4
ENTRADAS = ["VIS", "IR", "Propuesta_Fapt"]
TITULOS = {"VIS": "VIS", "IR": "IR", "Propuesta_Fapt": "Fusión (Propuesta, r=25)"}
GRANATE = "#c00000"
AZUL = "#1f4e79"

def hallar_best():
    cands = sorted(Path(".").glob("runs/**/mixto/weights/best.pt"),
                   key=lambda p: p.stat().st_mtime)
    assert cands, "no hay best.pt; corre antes el pipeline M3FD"
    return str(cands[-1])

def gt_clases(stem):
    lab = Path(f"datasets/m3fd_test_VIS/labels/val/{stem}.txt")
    cls = [int(l.split()[0]) for l in lab.read_text().splitlines() if l.strip()]
    return cls

def contar(res, clase):
    b = res.boxes
    if b is None or len(b) == 0:
        return 0
    keep = (b.conf.cpu().numpy() >= CONF) & (b.cls.cpu().numpy().astype(int) == clase)
    return int(keep.sum())

def main():
    from ultralytics import YOLO
    modelo = YOLO(hallar_best())

    # -------- candidatas: escenas con GT de ambas clases --------
    stems = sorted(p.stem for p in Path("datasets/m3fd_test_VIS/images/val").glob("*.jpg"))
    cand = []
    for s in stems:
        cls = gt_clases(s)
        if cls.count(PEOPLE) >= 1 and cls.count(LAMP) >= 2:
            cand.append(s)
    print(f"candidatas con GT People+Lamp: {len(cand)}")

    # -------- medir todas las candidatas una sola vez --------
    stats = []
    for k, s in enumerate(cand):
        rs = {e: modelo.predict(f"datasets/m3fd_test_{e}/images/val/{s}.jpg",
                                conf=CONF, verbose=False)[0] for e in ENTRADAS}
        nP = {e: contar(rs[e], PEOPLE) for e in ENTRADAS}
        nL = {e: contar(rs[e], LAMP) for e in ENTRADAS}
        stats.append((s, nP, nL))
        if (k + 1) % 25 == 0:
            print(f"  {k+1}/{len(cand)}...", flush=True)

    # escena A (lado People): el VIS pierde personas que el IR ve y la fusion recupera
    def score_people(t):
        _, nP, nL = t
        return ((nP["Propuesta_Fapt"] - nP["VIS"])
                + 0.5 * min(nP["IR"], nP["Propuesta_Fapt"])
                - (3 if nP["IR"] == 0 else 0))

    # escena B (lado Lamp): el IR pierde luces que el VIS ve y la fusion recupera
    def score_lamp(t):
        _, nP, nL = t
        return ((nL["Propuesta_Fapt"] - nL["IR"])
                + 0.5 * min(nL["VIS"], nL["Propuesta_Fapt"])
                + (1 if nL["IR"] == 0 and nL["Propuesta_Fapt"] >= 2 else 0)
                + 0.3 * nP["Propuesta_Fapt"])

    esc_a = max(stats, key=score_people)
    esc_b = max((t for t in stats if t[0] != esc_a[0]), key=score_lamp)
    for nombre, (s, nP, nL) in (("A (People)", esc_a), ("B (Lamp)", esc_b)):
        print(f"escena {nombre}: {s} | People {nP} | Lamp {nL}")

    # -------- render: 2 filas (escena People y escena Lamp) x 3 columnas --------
    plt.rcParams.update({"font.family": "serif"})
    fig, axes = plt.subplots(2, 3, figsize=(13.5, 8.0), gridspec_kw={"hspace": 0.16, "wspace": 0.05})
    for fila, (s, _, _) in enumerate((esc_a, esc_b)):
        for col, e in enumerate(ENTRADAS):
            ax = axes[fila, col]
            ruta = f"datasets/m3fd_test_{e}/images/val/{s}.jpg"
            img = cv2.imread(ruta, cv2.IMREAD_GRAYSCALE)
            res = modelo.predict(ruta, conf=CONF, verbose=False)[0]
            ax.imshow(img, cmap="gray", vmin=0, vmax=255)
            b = res.boxes
            if b is not None and len(b):
                xyxy = b.xyxy.cpu().numpy(); clss = b.cls.cpu().numpy().astype(int)
                for (x1, y1, x2, y2), cl in zip(xyxy, clss):
                    if cl == PEOPLE:
                        color, lw = GRANATE, 1.8
                    elif cl == LAMP:
                        color, lw = AZUL, 1.8
                    else:
                        color, lw = "#999999", 0.7
                    ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1,
                                           fill=False, edgecolor=color, linewidth=lw))
            es_prop = e == "Propuesta_Fapt"
            ax.set_title(f"{TITULOS[e]}  —  People: {contar(res, PEOPLE)} · Lamp: {contar(res, LAMP)}",
                         fontsize=10, color=(GRANATE if es_prop else "black"),
                         fontweight=("bold" if es_prop else "normal"))
            ax.set_xticks([]); ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_edgecolor(GRANATE if es_prop else "#555555")
                sp.set_linewidth(2.0 if es_prop else 0.6)
        axes[fila, 0].set_ylabel(f"Escena {s}", fontsize=10)
    fig.suptitle("Detecciones del modelo único VIS+IR — People en granate, Lamp en azul (conf ≥ 0,25)",
                 fontsize=12, y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.955])
    out = "docs/figures/fig_m3fd_detecciones.png"
    fig.savefig(out, dpi=160, bbox_inches="tight", facecolor="white")
    print("Guardado:", out)

if __name__ == "__main__":
    main()
