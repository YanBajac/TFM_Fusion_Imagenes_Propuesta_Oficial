# -*- coding: utf-8 -*-
"""
prepare_llvip.py — Construye datasets YOLO FUSIONADOS a partir de LLVIP.

OJO: necesitas el DATASET (no el repo de codigo). Descargalo de:
  https://drive.google.com/file/d/1VTlT3Y7e1h-Zsne4zahjx5q0TK2ClMVv/view
y descomprimilo. Debe contener carpetas 'visible' e 'infrared' (con train/test)
y 'Annotations' (VOC, clase 'person').

Genera <out>/llvip_<metodo>/ (images/{train,val}, labels/{train,val}, data.yaml)
por cada metodo. Las ETIQUETAS son identicas para todos (solo cambian los pixeles).
"""
import argparse, sys
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np, cv2
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from src.fusion.optimal_top_hat import fuse_optimal
from src.fusion.comparatives import (laplacian_pyramid_fusion, ratio_pyramid_fusion,
                                     dwt_fusion, dtcwt_fusion, curvelet_fusion,
                                     tophat_classic_fusion)

def g2d(a):
    a=np.asarray(a); return a[...,0] if a.ndim==3 else a

FUSERS = {
    "PiramideLaplace":    lambda v,i: laplacian_pyramid_fusion(v,i,levels=4),
    "RatioPiramide":      lambda v,i: ratio_pyramid_fusion(v,i,levels=4),
    "DWT":                lambda v,i: dwt_fusion(v,i,levels=3),
    "DTCWT":              lambda v,i: dtcwt_fusion(v,i,levels=4),
    "Curvelet":           lambda v,i: curvelet_fusion(v,i,levels=3),
    "TopHat_Clasico":     lambda v,i: tophat_classic_fusion(v,i,r=5),
    "Propuesta_Novedosa": lambda v,i: fuse_optimal(v,i,25,0.0703,mode="sum"),  # F_apt (barrido PSO 5x5)
    "Propuesta_Fo":       lambda v,i: fuse_optimal(v,i,1,0.30,mode="sum"),     # F_o (rango publicado, optimo r=1)
}
IMG_EXT=(".jpg",".jpeg",".png",".bmp")

def load_gray01(p):
    im=cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
    return None if im is None else im.astype(np.float32)/255.0

def find_dataset_root(root):
    """Devuelve el dir que contiene 'visible' e 'infrared' (busca anidado)."""
    if (root/"visible").is_dir() and (root/"infrared").is_dir(): return root
    for d in root.rglob("visible"):
        if (d.parent/"infrared").is_dir(): return d.parent
    return None

def list_split_images(vroot, split):
    """Devuelve lista de imagenes visibles del split. Soporta visible/train o visible/ plano."""
    sub=vroot/split
    if sub.is_dir():
        return sorted([p for p in sub.iterdir() if p.suffix.lower() in IMG_EXT])
    # plano: visible/*.jpg (sin train/test) -> se reparte luego
    return sorted([p for p in vroot.iterdir() if p.suffix.lower() in IMG_EXT])

def find_ann(root, stem):
    for c in [root/"Annotations"/f"{stem}.xml", root/"Annotations"/"train"/f"{stem}.xml",
              root/"Annotations"/"test"/f"{stem}.xml"]:
        if c.exists(): return c
    hits=list((root).rglob(f"{stem}.xml"))
    return hits[0] if hits else None

def voc_to_yolo(xml_path, W, H):
    out=[]
    try: r=ET.parse(str(xml_path)).getroot()
    except Exception: return out
    for obj in r.findall("object"):
        bb=obj.find("bndbox")
        if bb is None: continue
        x1=float(bb.find("xmin").text); y1=float(bb.find("ymin").text)
        x2=float(bb.find("xmax").text); y2=float(bb.find("ymax").text)
        cx=((x1+x2)/2)/W; cy=((y1+y2)/2)/H; w=(x2-x1)/W; h=(y2-y1)/H
        if w>0 and h>0: out.append(f"0 {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
    return out

def save_uint8(img01, path):
    cv2.imwrite(str(path), (np.clip(g2d(img01),0,1)*255).astype(np.uint8))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--llvip_root", required=True)
    ap.add_argument("--out", default="datasets")
    ap.add_argument("--methods", default="VIS,IR,PiramideLaplace,RatioPiramide,DWT,DTCWT,Curvelet,TopHat_Clasico,Propuesta_Novedosa")
    ap.add_argument("--limit-train", type=int, default=0)
    ap.add_argument("--limit-val", type=int, default=0)
    a=ap.parse_args()
    given=Path(a.llvip_root)
    root=find_dataset_root(given)
    if root is None:
        print("ERROR: no encontre carpetas 'visible' e 'infrared' bajo:", given)
        print(" -> Parece que tenes el REPO de codigo, no el DATASET.")
        print(" -> Descarga el dataset LLVIP de:")
        print("    https://drive.google.com/file/d/1VTlT3Y7e1h-Zsne4zahjx5q0TK2ClMVv/view")
        print("    y apunta --llvip_root a la carpeta que contiene 'visible/' e 'infrared/'.")
        sys.exit(2)
    print("Dataset LLVIP detectado en:", root)
    out=Path(a.out); methods=[m.strip() for m in a.methods.split(",") if m.strip()]
    vroot=root/"visible"; iroot=root/"infrared"
    # determinar splits
    if (vroot/"train").is_dir():
        split_map=[("train","train"), ("test","val")]
        flat=False
    else:
        split_map=[(".","all")]; flat=True
    for m in methods:
        for sp in ("train","val"):
            (out/f"llvip_{m}"/"images"/sp).mkdir(parents=True, exist_ok=True)
            (out/f"llvip_{m}"/"labels"/sp).mkdir(parents=True, exist_ok=True)
    for src_split, yolo_split in split_map:
        vis=list_split_images(vroot, src_split)
        if flat:
            # repartir 80/20
            n=len(vis); cut=int(n*0.8)
            groups=[("train",vis[:cut]),("val",vis[cut:])]
        else:
            lim=a.__dict__["limit_train"] if yolo_split=="train" else a.__dict__["limit_val"]
            if lim: vis=vis[:lim]
            groups=[(yolo_split,vis)]
        for ysplit, lst in groups:
            print(f"Split -> {ysplit}: {len(lst)} pares")
            for k,vp in enumerate(lst):
                stem=vp.stem
                ip = (iroot/src_split/vp.name) if not flat else (iroot/vp.name)
                if not ip.exists():
                    cand=list(iroot.rglob(vp.name)); ip=cand[0] if cand else ip
                if not ip.exists(): continue
                v=load_gray01(vp); i=load_gray01(ip)
                if v is None or i is None: continue
                if v.shape!=i.shape: i=cv2.resize(i,(v.shape[1],v.shape[0]))
                H,W=v.shape[:2]
                ann=find_ann(root, stem); ylab=voc_to_yolo(ann,W,H) if ann else []
                for m in methods:
                    img = v if m=="VIS" else (i if m=="IR" else FUSERS[m](v,i))
                    save_uint8(img, out/f"llvip_{m}"/"images"/ysplit/f"{stem}.jpg")
                    (out/f"llvip_{m}"/"labels"/ysplit/f"{stem}.txt").write_text("\n".join(ylab))
                if (k+1)%200==0: print(f"  {k+1}...")
    for m in methods:
        d=(out/f"llvip_{m}").resolve()
        (d/"data.yaml").write_text(f"path: {d}\ntrain: images/train\nval: images/val\nnc: 1\nnames: ['person']\n")
    print("LISTO. Datasets en", out.resolve())

if __name__=="__main__": main()
