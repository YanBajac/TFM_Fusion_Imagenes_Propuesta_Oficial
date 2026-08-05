# -*- coding: utf-8 -*-
"""Comparativa cualitativa de detecciones: la MISMA escena en las nueve entradas.

Pedido del orientador: comparar las detecciones sobre las imagenes de las demas
metodologias, no solo de la propuesta. La figura publicada (fig_m3fd_detecciones.png)
muestra VIS, IR y la propuesta; esta muestra las nueve entradas del benchmark de deteccion
sobre la misma escena, con el modelo unico entrenado en VIS+IR mezcladas.

Escena: la misma que la figura publicada, para que el lector pueda cruzar las dos y para no
introducir una segunda regla de seleccion. Se toma del JSON que aquella dejo.

Salida: docs/figures/fig_m3fd_detecciones_metodos.png
        experiments/results/metrics_reports/detecciones_metodos_escena.csv
Uso:    .venv\\Scripts\\python.exe -X utf8 experiments/make_figura_detecciones_metodos.py
"""
import json
import os
import sys
from pathlib import Path

os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, ".")
import cv2
import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

CONF = 0.30                      # el mismo umbral de la figura publicada
PEOPLE, LAMP = 0, 4
GRANATE, AZUL = "#c00000", "#1f4e79"
JSON_PUB = Path("experiments/results/metrics_reports/figura_detecciones_m3fd.json")
SALIDA_FIG = Path("docs/figures/fig_m3fd_detecciones_metodos.png")
SALIDA_CSV = Path("experiments/results/metrics_reports/detecciones_metodos_escena.csv")

ENTRADAS = [("VIS", "VIS"), ("IR", "IR"),
            ("PiramideLaplace", "Pirámide de Laplace"), ("RatioPiramide", "Ratio Pyramid"),
            ("DWT", "DWT"), ("DTCWT", "DTCWT"), ("Curvelet", "CVT"),
            ("TopHat_Clasico", "Top-Hat clásico"),
            ("Propuesta_Novedosa", "Propuesta (r=25, m=0,30)")]


def hallar_best():
    c = sorted(Path(".").glob("runs/**/mixto/weights/best.pt"), key=lambda p: p.stat().st_mtime)
    assert c, "no hay best.pt del mixto; correr antes el pipeline M3FD"
    return str(c[-1])


def escena_publicada():
    """La escena del lado «lamp» de la figura publicada: tiene las dos clases."""
    d = json.loads(JSON_PUB.read_text(encoding="utf-8"))
    for e in d["escenas"]:
        if e["lado"] == "lamp":
            return e["escena"]
    return d["escenas"][0]["escena"]


def gt(stem):
    lab = Path(f"datasets/m3fd_comp_VIS/labels/val/{stem}.txt")
    cls = [int(l.split()[0]) for l in lab.read_text().splitlines() if l.strip()]
    return cls.count(PEOPLE), cls.count(LAMP)


def cajas(res, clase):
    b = res.boxes
    if b is None or len(b) == 0:
        return np.zeros((0, 4))
    cf = b.conf.cpu().numpy()
    cl = b.cls.cpu().numpy().astype(int)
    return b.xyxy.cpu().numpy()[(cf >= CONF) & (cl == clase)]


def main():
    from ultralytics import YOLO
    modelo = YOLO(hallar_best())
    stem = escena_publicada()
    gp, gl = gt(stem)
    print(f"escena {stem} · verdad de campo: {gp} personas, {gl} luces")

    filas, paneles = [], []
    for clave, titulo in ENTRADAS:
        ruta = Path(f"datasets/m3fd_comp_{clave}/images/val/{stem}.jpg")
        if not ruta.exists():
            print(f"  falta {ruta}")
            continue
        img = cv2.cvtColor(cv2.imread(str(ruta)), cv2.COLOR_BGR2RGB)
        r = modelo.predict(str(ruta), conf=CONF, verbose=False)[0]
        cp, cl = cajas(r, PEOPLE), cajas(r, LAMP)
        paneles.append((titulo, img, cp, cl))
        filas.append({"escena": stem, "entrada": clave, "etiqueta": titulo,
                      "people_detectadas": len(cp), "lamp_detectadas": len(cl),
                      "people_gt": gp, "lamp_gt": gl,
                      "recupera_ambas": bool(len(cp) and len(cl))})
        print(f"  {titulo:26s} People {len(cp):2d}/{gp}  Lamp {len(cl):2d}/{gl}")

    n = len(paneles)
    ncol, nfil = 3, int(np.ceil(n / 3))
    fig, axes = plt.subplots(nfil, ncol, figsize=(12.6, 2.75 * nfil))
    for ax, (titulo, img, cp, cl) in zip(np.ravel(axes), paneles):
        ax.imshow(img)
        for x1, y1, x2, y2 in cp:
            ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False,
                                   edgecolor=GRANATE, lw=1.4))
        for x1, y1, x2, y2 in cl:
            ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False,
                                   edgecolor=AZUL, lw=1.4))
        ambas = len(cp) and len(cl)
        ax.set_title(f"{titulo} — People: {len(cp)} · Lamp: {len(cl)}",
                     fontsize=8.5, color="black" if ambas else "#7a1a1a",
                     fontweight="bold" if "Propuesta" in titulo else "normal")
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_edgecolor(GRANATE if "Propuesta" in titulo else "#bbbbbb")
            s.set_linewidth(1.8 if "Propuesta" in titulo else 0.6)
    for ax in np.ravel(axes)[n:]:
        ax.axis("off")
    fig.suptitle(f"M3FD, escena {stem} — detecciones del modelo único VIS+IR sobre cada entrada "
                 f"(conf ≥ {CONF:.2f}; People en granate, Lamp en azul; "
                 f"verdad de campo: {gp} personas y {gl} luces)", fontsize=9.5, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    SALIDA_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SALIDA_FIG, dpi=170, facecolor="white")
    plt.close(fig)

    d = pd.DataFrame(filas)
    d.to_csv(SALIDA_CSV, index=False)
    print(f"\nentradas que recuperan AMBAS clases: {int(d.recupera_ambas.sum())} de {len(d)}")
    print(f"-> {SALIDA_FIG}")
    print(f"-> {SALIDA_CSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
