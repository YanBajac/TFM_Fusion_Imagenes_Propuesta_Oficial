# -*- coding: utf-8 -*-
"""Arma los diez conjuntos de la deteccion en M3FD, uno por entrada del detector.

Lee la particion de m3fd_v2_particion.csv (particion_tramos_v2.py) y, para cada cuadro de
entrenamiento, seguimiento, validacion y prueba, escribe la imagen de cada entrada: visible, infrarroja,
el promedio simple y las siete fusiones. Las etiquetas son las mismas en los diez conjuntos. La fusion, la
conversion a gris, la conversion de etiquetas VOC a YOLO y el guardado son las funciones de
prepare_m3fd.py, que este script importa como biblioteca.

Salida: datasets/m3fd2_<ENTRADA>/{images,labels}/{train,sobrante,val,test}/<id>.{jpg,txt} y data.yaml

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/detection_m3fd/preparar_v2.py
"""
import importlib.util
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
_spec = importlib.util.spec_from_file_location("prep", ROOT / "experiments" / "detection_m3fd" / "prepare_m3fd.py")
prep = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(prep)

M3FD = ROOT / "data" / "M3FD_Detection"
OUT = ROOT / "datasets"
MR = ROOT / "experiments" / "results" / "metrics_reports"
ENTRADAS = ["VIS", "IR", "Promedio"] + list(prep.FUSERS)
# 'sobrante' son cuadros de bloques de entrenamiento que no entraron en los 2000: los usa Ultralytics para
# monitorear el entrenamiento y el analisis para calibrar el umbral. Asi 'val' queda sin mirar y se suma a
# la prueba.
PARTES = ("train", "val", "test", "sobrante")


def fusionar(e, v, r):
    if e == "VIS":
        return v
    if e == "IR":
        return r
    if e == "Promedio":
        return 0.5 * (v + r)     # la propuesta con m = 0: la base sin ningun detalle agregado
    return prep.FUSERS[e](v, r)


def carpeta(entrada):
    return OUT / f"m3fd2_{entrada}"


def trabajar(tarea):
    i, parte = tarea
    stem = f"{i:05d}"
    destinos = {e: carpeta(e) / "images" / parte / f"{stem}.jpg" for e in ENTRADAS}
    etiquetas = {e: carpeta(e) / "labels" / parte / f"{stem}.txt" for e in ENTRADAS}
    faltan = [e for e in ENTRADAS if not destinos[e].exists() or not etiquetas[e].exists()]
    if not faltan:
        return i, 0.0
    t0 = time.time()
    v = prep.load_gray01(M3FD / "Vis" / f"{stem}.png")
    r = prep.load_gray01(M3FD / "Ir" / f"{stem}.png")
    H, W = v.shape
    texto = prep.voc_a_yolo(M3FD / "Annotation" / f"{stem}.xml", W, H)
    for e in faltan:     # solo lo que falta: agregar una entrada no rehace las otras
        prep.save_uint8(fusionar(e, v, r), destinos[e])
        etiquetas[e].write_text(texto + ("\n" if texto else ""), encoding="utf-8")
    return i, time.time() - t0


def main():
    part = pd.read_csv(MR / "m3fd_v2_particion.csv")
    part = part[part.parte.isin(PARTES)]
    for e in ENTRADAS:
        for s in ("images", "labels"):
            for p in PARTES:
                (carpeta(e) / s / p).mkdir(parents=True, exist_ok=True)
        d = carpeta(e).resolve()
        nombres = ", ".join(f"'{n}'" for n in prep.NAMES)
        (d / "data.yaml").write_text(
            f"path: {d}\ntrain: images/train\nval: images/sobrante\ntest: [images/test, images/val]\n"
            f"nc: {len(prep.NAMES)}\nnames: [{nombres}]\n", encoding="utf-8")
    tareas = list(zip(part.id.astype(int), part.parte))
    print(f"  {len(tareas)} cuadros x {len(ENTRADAS)} entradas = {len(tareas) * len(ENTRADAS)} imagenes")
    t0 = time.time()
    hechos = 0
    with Pool(14) as pool:
        for _, dt in pool.imap_unordered(trabajar, tareas, chunksize=4):
            hechos += 1
            if hechos % 400 == 0:
                print(f"    {hechos}/{len(tareas)}  ({(time.time() - t0) / 60:.1f} min)", flush=True)
    print(f"  listo en {(time.time() - t0) / 60:.1f} min")
    # control: las diez carpetas tienen los mismos archivos y las mismas etiquetas
    ref = {p: sorted(x.name for x in (carpeta("VIS") / "labels" / p).glob("*.txt")) for p in PARTES}
    for e in ENTRADAS:
        for p in PARTES:
            nombres = sorted(x.name for x in (carpeta(e) / "labels" / p).glob("*.txt"))
            imgs = sorted(x.stem for x in (carpeta(e) / "images" / p).glob("*.jpg"))
            assert nombres == ref[p], f"{e}/{p}: etiquetas distintas de VIS"
            assert imgs == [n[:-4] for n in ref[p]], f"{e}/{p}: imagenes y etiquetas no coinciden"
    muestra = ref["test"][:50]
    for e in ENTRADAS[1:]:
        for n in muestra:
            a = (carpeta("VIS") / "labels" / "test" / n).read_text(encoding="utf-8")
            b = (carpeta(e) / "labels" / "test" / n).read_text(encoding="utf-8")
            assert a == b, f"{e}: la etiqueta {n} difiere de la del visible"
    print("  control OK: diez conjuntos con los mismos cuadros y las mismas etiquetas")
    for p in PARTES:
        print(f"    {p}: {len(ref[p])} cuadros")
    return 0


if __name__ == "__main__":
    sys.exit(main())
