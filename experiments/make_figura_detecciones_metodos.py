# -*- coding: utf-8 -*-
"""Comparativa cualitativa de detecciones: varias escenas x las diez entradas.

Pedido del orientador: comparar las detecciones sobre las imagenes de las demas
metodologias, sobre mas de un escenario, e incluir la metodologia del trabajo de referencia.

Dos precisiones sobre el contenido:

1. La metodologia de la referencia NO es el comparativo «Top-Hat clasico» del benchmark.
   Aquel corre con r = 5 y m = 1, la parametrizacion manual clasica. Su metodologia es el
   mismo operador de disco unico con (r, m) hallados por su PSO, y el barrido con la aptitud
   Fo devuelve r = 25 y m = 0,30 —la misma configuracion que la propuesta—, de modo que la
   comparacion entre ambas aisla el banco de cinco elementos frente al disco unico. Se agrega
   como decima entrada y se fusiona al vuelo con el mismo camino de prepare_m3fd.py.

2. Las escenas NO se eligen por conveniencia. La regla se declara y se aplica sobre
   complementariedad_por_escena.csv, e incluye el caso ADVERSO a la propuesta:
     - la escena con mas objetos donde la propuesta recupera ambas clases y el visible no,
     - la escena con mas objetos donde el visible las recupera y la propuesta no,
     - la escena con mas objetos donde ambas las recuperan,
     - y la ya publicada, para poder cruzarla con la figura anterior.

Salida: docs/figures/fig_m3fd_detecciones_<escena>.png (una por escena)
        experiments/results/metrics_reports/detecciones_metodos_escena.csv (todas las filas)
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

from src.fusion.comparatives import tophat_classic_fusion

CONF = 0.30                      # el mismo umbral de la figura publicada
PEOPLE, LAMP = 0, 4
GRANATE, AZUL = "#c00000", "#1f4e79"
MR = Path("experiments/results/metrics_reports")
POR_ESCENA = MR / "complementariedad_por_escena.csv"
JSON_PUB = MR / "figura_detecciones_m3fd.json"
SALIDA_CSV = MR / "detecciones_metodos_escena.csv"
TMP = Path("experiments/results/fused_images/_tmp_deteccion")

# la decima entrada se fusiona al vuelo; las nueve primeras ya estan en datasets/m3fd_comp_*
REF_PSO = ("Ref_PSO", "Metodología de la referencia (disco, PSO: r=25, m=0,30)", (25, 0.30))
ENTRADAS = [("VIS", "VIS"), ("IR", "IR"),
            ("PiramideLaplace", "Pirámide de Laplace"), ("RatioPiramide", "Ratio Pyramid"),
            ("DWT", "DWT"), ("DTCWT", "DTCWT"), ("Curvelet", "CVT"),
            ("TopHat_Clasico", "Top-Hat clásico (r=5, m=1)"),
            (REF_PSO[0], REF_PSO[1]),
            ("Propuesta_Novedosa", "Propuesta (r=25, m=0,30)")]


def hallar_best():
    c = sorted(Path(".").glob("runs/**/mixto/weights/best.pt"), key=lambda p: p.stat().st_mtime)
    assert c, "no hay best.pt del mixto; correr antes el pipeline M3FD"
    return str(c[-1])


def gris01(p):
    """Gris en [0, 1] y estrictamente 2D.

    prepare_m3fd.py aplana con g2d() por la misma razon: la lectura puede devolver un canal
    extra, y entonces la resta contra la apertura morfologica no difunde.
    """
    im = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
    if im is None:
        return None
    im = np.asarray(im)
    if im.ndim == 3:
        im = im[..., 0]
    return im.astype(np.float32) / 255.0


def fusionar_referencia(stem):
    """Fusiona VIS+IR con el operador de la referencia a su (r, m) de PSO.

    Replica el camino de prepare_m3fd.py: gris en [0, 1], el IR redimensionado al VIS si
    hiciera falta, y la salida guardada como uint8.
    """
    TMP.mkdir(parents=True, exist_ok=True)
    dest = TMP / f"{stem}.jpg"
    if dest.exists():
        return dest
    v = gris01(f"datasets/m3fd_comp_VIS/images/val/{stem}.jpg")
    i = gris01(f"datasets/m3fd_comp_IR/images/val/{stem}.jpg")
    if v is None or i is None:
        return None
    if i.shape != v.shape:
        i = cv2.resize(i, (v.shape[1], v.shape[0]))
    r, m = REF_PSO[2]
    f = tophat_classic_fusion(v, i, r=r, m=m)
    cv2.imwrite(str(dest), (np.clip(f, 0, 1) * 255).astype(np.uint8))
    return dest


def escenas_elegidas():
    """La regla declarada en el encabezado, aplicada sobre el CSV por escena."""
    d = pd.read_csv(POR_ESCENA)
    p = d.pivot(index="escena", columns="entrada", values="recupera_ambas")
    gt = d.groupby("escena")[["gt_People", "gt_Lamp"]].first()
    z = p.join(gt)
    z["objetos"] = z.gt_People + z.gt_Lamp
    pub = None
    if JSON_PUB.exists():
        j = json.loads(JSON_PUB.read_text(encoding="utf-8"))
        pub = next((e["escena"] for e in j["escenas"] if e["lado"] == "lamp"), None)

    def top(sel, etiqueta):
        g = z[sel].sort_values("objetos", ascending=False)
        return (f"{int(g.index[0]):05d}", etiqueta, int(g.iloc[0].objetos)) if len(g) else None

    fuera = []
    if pub:
        fuera.append((pub, "la escena ya publicada", int(z.loc[int(pub), "objetos"])))
    for sel, et in (((z.Propuesta_Novedosa == 1) & (z.VIS == 0),
                     "la propuesta recupera ambas y el visible no"),
                    ((z.Propuesta_Novedosa == 0) & (z.VIS == 1),
                     "el visible recupera ambas y la propuesta no"),
                    ((z.Propuesta_Novedosa == 1) & (z.VIS == 1),
                     "ambas recuperan las dos clases")):
        t = top(sel, et)
        if t and t[0] not in [f[0] for f in fuera]:
            fuera.append(t)
    return fuera


def cajas(res, clase):
    b = res.boxes
    if b is None or len(b) == 0:
        return np.zeros((0, 4))
    cf = b.conf.cpu().numpy()
    cl = b.cls.cpu().numpy().astype(int)
    return b.xyxy.cpu().numpy()[(cf >= CONF) & (cl == clase)]


def figura_de(modelo, stem, etiqueta, filas_csv):
    lab = Path(f"datasets/m3fd_comp_VIS/labels/val/{stem}.txt")
    cls = [int(l.split()[0]) for l in lab.read_text().splitlines() if l.strip()]
    gp, gl = cls.count(PEOPLE), cls.count(LAMP)
    print(f"\nescena {stem} ({etiqueta}) · verdad de campo: {gp} personas, {gl} luces")

    paneles = []
    for clave, titulo in ENTRADAS:
        if clave == REF_PSO[0]:
            ruta = fusionar_referencia(stem)
        else:
            ruta = Path(f"datasets/m3fd_comp_{clave}/images/val/{stem}.jpg")
            ruta = ruta if ruta.exists() else None
        if ruta is None:
            print(f"  falta la entrada {clave}")
            continue
        img = cv2.cvtColor(cv2.imread(str(ruta)), cv2.COLOR_BGR2RGB)
        r = modelo.predict(str(ruta), conf=CONF, verbose=False)[0]
        cp, cl_ = cajas(r, PEOPLE), cajas(r, LAMP)
        paneles.append((titulo, img, cp, cl_, clave))
        filas_csv.append({"escena": stem, "criterio": etiqueta, "entrada": clave,
                          "etiqueta": titulo, "people_detectadas": len(cp),
                          "lamp_detectadas": len(cl_), "people_gt": gp, "lamp_gt": gl,
                          # DETECTA, no «recupera»: aca se cuentan las cajas por encima del
                          # umbral, mientras complementariedad_por_escena.csv cuenta aciertos
                          # emparejados con la verdad de campo. No son la misma cantidad.
                          "detecta_ambas": bool(len(cp) and len(cl_))})
        print(f"  {titulo:46s} People {len(cp):2d}/{gp}  Lamp {len(cl_):2d}/{gl}")

    ncol = 3
    nfil = int(np.ceil(len(paneles) / ncol))
    fig, axes = plt.subplots(nfil, ncol, figsize=(12.6, 2.62 * nfil))
    for ax, (titulo, img, cp, cl_, clave) in zip(np.ravel(axes), paneles):
        ax.imshow(img)
        for x1, y1, x2, y2 in cp:
            ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False,
                                   edgecolor=GRANATE, lw=1.3))
        for x1, y1, x2, y2 in cl_:
            ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False,
                                   edgecolor=AZUL, lw=1.3))
        destaca = clave in ("Propuesta_Novedosa", REF_PSO[0])
        ax.set_title(f"{titulo} — People: {len(cp)} · Lamp: {len(cl_)}", fontsize=8,
                     fontweight="bold" if destaca else "normal")
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_edgecolor(GRANATE if clave == "Propuesta_Novedosa"
                            else ("#1f4e79" if clave == REF_PSO[0] else "#bbbbbb"))
            s.set_linewidth(1.8 if destaca else 0.6)
    for ax in np.ravel(axes)[len(paneles):]:
        ax.axis("off")
    fig.suptitle(f"M3FD, escena {stem} — {etiqueta}. Detecciones del modelo único VIS+IR "
                 f"sobre cada entrada (conf ≥ {CONF:.2f}; People en granate, Lamp en azul; "
                 f"verdad de campo: {gp} personas y {gl} luces)", fontsize=9, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 1 - 0.035 / nfil * 4))
    dest = Path(f"docs/figures/fig_m3fd_detecciones_{stem}.png")
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest, dpi=165, facecolor="white")
    plt.close(fig)
    print(f"  -> {dest}")
    return dest


def main():
    from ultralytics import YOLO
    modelo = YOLO(hallar_best())
    elegidas = escenas_elegidas()
    print("escenas elegidas por la regla declarada:")
    for s, et, n in elegidas:
        print(f"  {s}  {et}  ({n} objetos)")
    filas = []
    for stem, etiqueta, _ in elegidas:
        figura_de(modelo, stem, etiqueta, filas)
    d = pd.DataFrame(filas)
    d.to_csv(SALIDA_CSV, index=False)
    print(f"\n{len(d)} filas ({d.escena.nunique()} escenas x {d.entrada.nunique()} entradas)")
    print(f"-> {SALIDA_CSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
