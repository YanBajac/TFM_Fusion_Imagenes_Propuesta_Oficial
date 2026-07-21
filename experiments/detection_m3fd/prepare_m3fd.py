# -*- coding: utf-8 -*-
"""
prepare_m3fd.py — Prepara el experimento de deteccion con clases complementarias
sobre M3FD (TarDAL, CVPR 2022): un UNICO modelo entrenado con imagenes VIS + IR
mezcladas (con sus etiquetas), evaluado por inferencia sobre la validacion en
cada modalidad y en cada metodo de fusion.

Descarga del dataset (M3FD Detection: carpetas de imagenes ir/vi + labels YOLO):
  https://github.com/JinyuanLiu-CV/TarDAL  (enlaces M3FD en el README)

Genera:
  <out>/m3fd_mixto/                      train = VIS+IR mezcladas (2N imagenes)
  <out>/m3fd_test_<METODO>/              val fusionada por metodo (labels compartidas)

Clases (orden de TarDAL): People, Car, Bus, Motorcycle, Lamp, Truck
  - People -> dominante en IR (firma termica)  |  Lamp -> dominante en VIS
Uso:
  python experiments\detection_m3fd\prepare_m3fd.py --m3fd_root data\M3FD --train-n 2000 --val-n 500
"""
import argparse, sys, shutil
from pathlib import Path
import numpy as np, cv2
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from src.fusion.optimal_top_hat import fuse_optimal
from src.fusion.comparatives import (laplacian_pyramid_fusion, ratio_pyramid_fusion,
                                     dwt_fusion, dtcwt_fusion, curvelet_fusion,
                                     tophat_classic_fusion)

NAMES = ["People", "Car", "Bus", "Motorcycle", "Lamp", "Truck"]
IMG_EXT = (".jpg", ".jpeg", ".png", ".bmp")

# Metodos de fusion a evaluar por inferencia (ambos PSO incluidos)
FUSERS = {
    "PiramideLaplace": lambda v, i: laplacian_pyramid_fusion(v, i, levels=4),
    "RatioPiramide":   lambda v, i: ratio_pyramid_fusion(v, i, levels=4),
    "DWT":             lambda v, i: dwt_fusion(v, i, levels=3),
    "DTCWT":           lambda v, i: dtcwt_fusion(v, i, levels=4),
    "Curvelet":        lambda v, i: curvelet_fusion(v, i, levels=3),
    "TopHat_Clasico":  lambda v, i: tophat_classic_fusion(v, i, r=5),
    "PSO_FPUNA_Fo":    lambda v, i: tophat_classic_fusion(v, i, r=25, m=0.30),   # PSO de Ortega & Espinoza
    "Propuesta_Fapt":  lambda v, i: fuse_optimal(v, i, 25, 0.0703, mode="sum"),  # PSO de la tesis
    "Propuesta_Fo":    lambda v, i: fuse_optimal(v, i, 1, 0.30, mode="sum"),     # ablacion (optimo trivial)
}

def g2d(a):
    a = np.asarray(a); return a[..., 0] if a.ndim == 3 else a

def load_gray01(p):
    im = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
    return None if im is None else im.astype(np.float32) / 255.0

def save_uint8(img01, path):
    cv2.imwrite(str(path), (np.clip(g2d(img01), 0, 1) * 255).astype(np.uint8))

def hallar_dir(root, candidatos):
    for c in candidatos:
        d = root / c
        if d.is_dir() and any(p.suffix.lower() in IMG_EXT for p in d.iterdir()):
            return d
    for d in root.rglob("*"):
        if d.is_dir() and d.name.lower() in [c.lower() for c in candidatos]:
            if any(p.suffix.lower() in IMG_EXT for p in d.iterdir()):
                return d
    return None

def hallar_labels(root):
    """Devuelve (dir, 'yolo'|'voc'): acepta .txt YOLO o .xml VOC (M3FD usa VOC)."""
    for cand in ["labels", "Labels", "label", "Annotation", "annotations"]:
        d = root / cand
        if d.is_dir():
            if any(p.suffix == ".txt" for p in d.rglob("*.txt")):
                return d, "yolo"
            if any(p.suffix == ".xml" for p in d.rglob("*.xml")):
                return d, "voc"
    for d in root.rglob("*"):
        if d.is_dir():
            if any(p.suffix == ".txt" for p in d.iterdir()):
                return d, "yolo"
            if any(p.suffix == ".xml" for p in d.iterdir()):
                return d, "voc"
    return None, None

def buscar_label(labdir, stem, ext):
    c = labdir / f"{stem}{ext}"
    if c.exists():
        return c
    hits = list(labdir.rglob(f"{stem}{ext}"))
    return hits[0] if hits else None

def voc_a_yolo(xml_path, W, H):
    """Convierte un XML VOC de M3FD a lineas YOLO usando el orden de NAMES."""
    import xml.etree.ElementTree as ET
    out = []
    try:
        r = ET.parse(str(xml_path)).getroot()
    except Exception:
        return ""
    sz = r.find("size")
    if sz is not None:
        try:
            W = int(sz.find("width").text) or W
            H = int(sz.find("height").text) or H
        except Exception:
            pass
    for obj in r.findall("object"):
        nombre = (obj.find("name").text or "").strip()
        if nombre not in NAMES:
            continue
        bb = obj.find("bndbox")
        if bb is None:
            continue
        x1 = float(bb.find("xmin").text); y1 = float(bb.find("ymin").text)
        x2 = float(bb.find("xmax").text); y2 = float(bb.find("ymax").text)
        cx = ((x1 + x2) / 2) / W; cy = ((y1 + y2) / 2) / H
        w = (x2 - x1) / W; h = (y2 - y1) / H
        if w > 0 and h > 0:
            out.append(f"{NAMES.index(nombre)} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
    return "\n".join(out)

def data_yaml(d, train_rel, val_rel):
    d = d.resolve()
    nombres = ", ".join(f"'{n}'" for n in NAMES)
    (d / "data.yaml").write_text(
        f"path: {d}\ntrain: {train_rel}\nval: {val_rel}\nnc: {len(NAMES)}\nnames: [{nombres}]\n",
        encoding="utf-8")

def leer_label(lb):
    if lb.suffix == ".txt":
        return lb.read_text(encoding="utf-8", errors="replace")
    return voc_a_yolo(lb, 1024, 768)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m3fd_root", required=True)
    ap.add_argument("--out", default="datasets")
    ap.add_argument("--train-n", type=int, default=2000)
    ap.add_argument("--val-n", type=int, default=500)
    a = ap.parse_args()
    root = Path(a.m3fd_root)
    vdir = hallar_dir(root, ["vi", "Vis", "visible", "vis", "Visible", "RGB"])
    idir = hallar_dir(root, ["ir", "Ir", "infrared", "Inf", "Infrared"])
    labdir, labtipo = hallar_labels(root)
    if not (vdir and idir and labdir):
        print("ERROR: no encontre las carpetas del dataset bajo:", root)
        print("  visible:", vdir, "| infrarrojo:", idir, "| labels:", labdir)
        print("  Descarga 'M3FD Detection' desde https://github.com/JinyuanLiu-CV/TarDAL")
        sys.exit(2)
    print("VIS:", vdir, "\nIR: ", idir, "\nLAB:", labdir, f"({labtipo})")
    ext = ".txt" if labtipo == "yolo" else ".xml"

    vis_all = sorted([p for p in vdir.iterdir() if p.suffix.lower() in IMG_EXT])
    pares = []
    for vp in vis_all:
        ip = idir / vp.name
        if not ip.exists():
            hits = [c for c in idir.iterdir() if c.stem == vp.stem]
            ip = hits[0] if hits else None
        lb = buscar_label(labdir, vp.stem, ext)
        if ip is not None and lb is not None:
            pares.append((vp, ip, lb))
    print(f"pares VIS/IR con label: {len(pares)}")
    if len(pares) < a.train_n + a.val_n:
        print(f"AVISO: menos pares que train+val pedidos; uso {len(pares)}")
    pares = pares[: a.train_n + a.val_n]
    train, val = pares[: a.train_n], pares[a.train_n:]
    print(f"train: {len(train)} pares (x2 modalidades) | val: {len(val)} pares")

    out = Path(a.out)
    # ---------- dataset mixto de entrenamiento ----------
    mixto = out / "m3fd_mixto"
    for sp in ("train", "val"):
        (mixto / "images" / sp).mkdir(parents=True, exist_ok=True)
        (mixto / "labels" / sp).mkdir(parents=True, exist_ok=True)
    for k, (vp, ip, lb) in enumerate(train):
        lab = leer_label(lb)
        for tag, src in (("vi", vp), ("ir", ip)):
            im = load_gray01(src)
            if im is None:
                continue
            save_uint8(im, mixto / "images" / "train" / f"{vp.stem}__{tag}.jpg")
            (mixto / "labels" / "train" / f"{vp.stem}__{tag}.txt").write_text(lab, encoding="utf-8")
        if (k + 1) % 200 == 0:
            print(f"  train {k+1}...", flush=True)
    # val del mixto: ambas modalidades (solo para monitoreo del entrenamiento)
    for vp, ip, lb in val:
        lab = leer_label(lb)
        for tag, src in (("vi", vp), ("ir", ip)):
            im = load_gray01(src)
            if im is None:
                continue
            save_uint8(im, mixto / "images" / "val" / f"{vp.stem}__{tag}.jpg")
            (mixto / "labels" / "val" / f"{vp.stem}__{tag}.txt").write_text(lab, encoding="utf-8")
    data_yaml(mixto, "images/train", "images/val")
    print("mixto OK ->", mixto)

    # ---------- sets de prueba por metodo (solo val) ----------
    metodos = ["VIS", "IR"] + list(FUSERS.keys())
    for m in metodos:
        d = out / f"m3fd_test_{m}"
        (d / "images" / "val").mkdir(parents=True, exist_ok=True)
        (d / "labels" / "val").mkdir(parents=True, exist_ok=True)
    for k, (vp, ip, lb) in enumerate(val):
        v = load_gray01(vp); i = load_gray01(ip)
        if v is None or i is None:
            continue
        if v.shape != i.shape:
            i = cv2.resize(i, (v.shape[1], v.shape[0]))
        lab = leer_label(lb)
        for m in metodos:
            img = v if m == "VIS" else (i if m == "IR" else FUSERS[m](v, i))
            d = out / f"m3fd_test_{m}"
            save_uint8(img, d / "images" / "val" / f"{vp.stem}.jpg")
            (d / "labels" / "val" / f"{vp.stem}.txt").write_text(lab, encoding="utf-8")
        if (k + 1) % 50 == 0:
            print(f"  val fusionada {k+1}/{len(val)}...", flush=True)
    for m in metodos:
        data_yaml(out / f"m3fd_test_{m}", "images/val", "images/val")
    print("LISTO. Mixto +", len(metodos), "sets de prueba en", out.resolve())

if __name__ == "__main__":
    main()
