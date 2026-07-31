# -*- coding: utf-8 -*-
"""
prepare_m3fd.py — Prepara el experimento de deteccion con clases complementarias
sobre M3FD (TarDAL, CVPR 2022): un UNICO modelo entrenado con imagenes VIS + IR
mezcladas (con sus etiquetas), evaluado por inferencia sobre la validacion en
cada modalidad y en cada metodo de fusion.

Descarga del dataset (M3FD Detection: carpetas de imagenes ir/vi + labels YOLO):
  https://github.com/JinyuanLiu-CV/TarDAL  (enlaces M3FD en el README)

La particion es ALEATORIA, ESTRATIFICADA por presencia de People/Lamp, y consta de
TRES conjuntos DISJUNTOS:
  train -> ajuste de pesos
  val   -> seleccion del checkpoint y monitoreo; nunca se reporta
  test  -> unica particion sobre la que se miden las metricas por metodo
(La version anterior partia de forma secuencial y usaba el mismo conjunto como val y
como test; ver el docstring de particionar() para el efecto que eso tenia.)

Genera:
  <out>/m3fd_mixto/                      train y val = VIS+IR mezcladas (2N imagenes)
  <out>/m3fd_test_<METODO>/              TEST fusionado por metodo (labels compartidas)

Clases (orden de TarDAL): People, Car, Bus, Motorcycle, Lamp, Truck
  - People -> dominante en IR (firma termica)  |  Lamp -> dominante en VIS
Uso:
  python experiments\detection_m3fd\prepare_m3fd.py --m3fd_root data\M3FD_Detection \
      --train-n 2000 --val-n 500 --test-n 500 --seed 0
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
    "Propuesta_Novedosa": lambda v, i: fuse_optimal(v, i, 25, 0.30, mode="sum"),  # config oficial (F_o, rango publicado)
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


# --------------------------------------------------------------------------- split
IDX_PEOPLE = NAMES.index("People")
IDX_LAMP = NAMES.index("Lamp")


def clases_presentes(lb):
    """Conjunto de indices de clase presentes en una etiqueta."""
    cs = set()
    for ln in leer_label(lb).strip().splitlines():
        ln = ln.strip()
        if ln:
            try:
                cs.add(int(ln.split()[0]))
            except (ValueError, IndexError):
                pass
    return cs


def _reparto(n, fracs):
    """Reparte n en len(fracs) partes segun fracs, con metodo de resto mayor."""
    crudo = [n * f for f in fracs]
    base = [int(x) for x in crudo]
    falta = n - sum(base)
    orden = sorted(range(len(fracs)), key=lambda i: crudo[i] - base[i], reverse=True)
    for i in orden[:falta]:
        base[i] += 1
    return base


def particionar(pares, n_train, n_val, n_test, semilla=0):
    """Particion ALEATORIA, ESTRATIFICADA y DISJUNTA en train / val / test.

    Por que no un corte secuencial: M3FD esta ordenado por captura, de modo que
    `pares[:2000]` y `pares[2000:2500]` caen en escenas distintas y con
    distribuciones de clase incompatibles (en el corte original el train tenia
    People 55,1 % / Lamp 4,3 % y el val People 9,4 % / Lamp 13,1 %). Con ese
    desplazamiento de prior el modelo preentrenado en COCO puntuaba mejor en el val
    que cualquier modelo ajustado al train, y la seleccion de checkpoint se quedaba
    con la epoca 1 de 40.

    Se estratifica por la presencia de las dos clases complementarias que reporta la
    tesis (People, dominante en IR; Lamp, dominante en VIS) para que las tres
    particiones tengan proporciones comparables de ambas.

    Las tres particiones son disjuntas y cumplen roles distintos:
      train -> ajuste de pesos
      val   -> seleccion de checkpoint y monitoreo (nunca se reporta)
      test  -> unica particion sobre la que se reportan metricas por metodo
    """
    rng = np.random.default_rng(semilla)
    estratos = {}
    for k, (_, _, lb) in enumerate(pares):
        cs = clases_presentes(lb)
        estratos.setdefault((IDX_PEOPLE in cs, IDX_LAMP in cs), []).append(k)
    total = n_train + n_val + n_test
    N = len(pares)
    fr = [n_train / total, n_val / total, n_test / total]
    tr, va, te = [], [], []
    for clave, idxs in sorted(estratos.items()):
        idxs = list(idxs)
        rng.shuffle(idxs)
        cupo = min(len(idxs), int(round(total * len(idxs) / N)))
        sel = idxs[:cupo]
        a, b, c = _reparto(len(sel), fr)
        tr += sel[:a]
        va += sel[a:a + b]
        te += sel[a + b:a + b + c]
    for nombre, parte in (("train", tr), ("val", va), ("test", te)):
        rng.shuffle(parte)
    assert not (set(tr) & set(va)), "train y val se solapan"
    assert not (set(tr) & set(te)), "train y test se solapan"
    assert not (set(va) & set(te)), "val y test se solapan"
    return ([pares[k] for k in tr], [pares[k] for k in va], [pares[k] for k in te])


def resumen_clases(nombre, parte):
    """Imprime el reparto de objetos por clase de una particion."""
    cuenta = {n: 0 for n in NAMES}
    tot = 0
    for _, _, lb in parte:
        for ln in leer_label(lb).strip().splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                cuenta[NAMES[int(ln.split()[0])]] += 1
                tot += 1
            except (ValueError, IndexError):
                pass
    det = "  ".join(f"{n} {100.0 * c / max(1, tot):4.1f}%" for n, c in cuenta.items() if c)
    print(f"  {nombre:5s} {len(parte):5d} pares | {tot:6d} objetos | {det}")
    return cuenta, tot

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m3fd_root", required=True)
    ap.add_argument("--out", default="datasets")
    ap.add_argument("--train-n", type=int, default=2000)
    ap.add_argument("--val-n", type=int, default=500,
                    help="particion de SELECCION de checkpoint (no se reporta)")
    ap.add_argument("--test-n", type=int, default=500,
                    help="particion de REPORTE, disjunta del val")
    ap.add_argument("--seed", type=int, default=0)
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
    pedido = a.train_n + a.val_n + a.test_n
    if len(pares) < pedido:
        print(f"AVISO: hay {len(pares)} pares y se pidieron {pedido}; se reparte lo disponible")
    print(f"\nParticion estratificada y disjunta (semilla {a.seed}):")
    train, val, test = particionar(pares, a.train_n, a.val_n, a.test_n, semilla=a.seed)
    for nombre, parte in (("train", train), ("val", val), ("test", test)):
        resumen_clases(nombre, parte)
    print("  val  = seleccion de checkpoint (no se reporta) | test = unica particion reportada\n")

    out = Path(a.out)
    # ---------- dataset mixto de entrenamiento ----------
    mixto = out / "m3fd_mixto"
    # Se borra el contenido previo: con un split nuevo, los archivos del anterior
    # quedarian mezclados y podrian filtrar imagenes de test dentro del train.
    for sp in ("train", "val"):
        shutil.rmtree(mixto / "images" / sp, ignore_errors=True)
        shutil.rmtree(mixto / "labels" / sp, ignore_errors=True)
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

    # ---------- sets de prueba por metodo: se construyen sobre TEST ----------
    # Antes se construian sobre el mismo `val` que servia para elegir el checkpoint,
    # de modo que el modelo se seleccionaba midiendo en las imagenes que luego se
    # reportaban. Ahora `test` es disjunto de `val` y de `train`.
    metodos = ["VIS", "IR"] + list(FUSERS.keys())
    for m in metodos:
        d = out / f"m3fd_test_{m}"
        for sp in ("images", "labels"):
            shutil.rmtree(d / sp / "val", ignore_errors=True)
        (d / "images" / "val").mkdir(parents=True, exist_ok=True)
        (d / "labels" / "val").mkdir(parents=True, exist_ok=True)
    for k, (vp, ip, lb) in enumerate(test):
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
            print(f"  test fusionado {k+1}/{len(test)}...", flush=True)
    for m in metodos:
        data_yaml(out / f"m3fd_test_{m}", "images/val", "images/val")
    print("LISTO. Mixto +", len(metodos), "sets de prueba en", out.resolve())

if __name__ == "__main__":
    main()
