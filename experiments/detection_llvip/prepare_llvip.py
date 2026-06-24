# -*- coding: utf-8 -*-
"""
prepare_llvip.py — Construye datasets YOLO FUSIONADOS a partir de LLVIP.

LLVIP (descargar de https://github.com/bupt-ai-cz/LLVIP) estructura tipica:
  LLVIP/visible/train/*.jpg   LLVIP/visible/test/*.jpg
  LLVIP/infrared/train/*.jpg  LLVIP/infrared/test/*.jpg
  LLVIP/Annotations/*.xml     (VOC, clase 'person'; cajas validas sobre el par alineado)

Para CADA metodo de fusion genera  <out>/llvip_<metodo>/  con formato YOLO:
  images/train, images/val, labels/train, labels/val, data.yaml
Las ETIQUETAS son identicas para todos los metodos (solo cambian los pixeles).
Asi la comparacion de mAP aisla el efecto del metodo de fusion.

Uso (ejemplo, PowerShell):
  python experiments\detection_llvip\prepare_llvip.py --llvip_root "D:\datasets\LLVIP" `
      --out datasets --methods VIS,IR,Promedio,PiramideLaplace,Optimo_Multiescala,Propuesta_Novedosa `
      --limit-train 2000 --limit-val 500
"""
import argparse, sys, shutil
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np, cv2
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from src.fusion.novel_fusion import fuse_novel
from src.fusion.optimal_top_hat import fuse_optimal_multiscale
from src.fusion.comparatives import average_fusion, laplacian_pyramid_fusion, curvelet_fusion
from src.fusion.prop_top_hat import TopHatFusion

def g2d(a):
    a=np.asarray(a); return a[...,0] if a.ndim==3 else a

# metodos de fusion (operan en gris [0,1] -> imagen fusionada [0,1])
FUSERS = {
    "Promedio":           lambda v,i: average_fusion(v,i),
    "PiramideLaplace":    lambda v,i: laplacian_pyramid_fusion(v,i,levels=4),
    "Curvelet":           lambda v,i: curvelet_fusion(v,i,levels=3),
    "TopHat_disk_L5":     lambda v,i: TopHatFusion("disk",levels=5).fuse(v,i),
    "Optimo_Multiescala": lambda v,i: fuse_optimal_multiscale(v,i,6,2.89,0.10),
    "Propuesta_Novedosa": lambda v,i: fuse_novel(v,i,8,0.120),   # n=8, m=0.12 (PSO)
}

def load_gray01(p):
    im=cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
    return None if im is None else im.astype(np.float32)/255.0

def find_ann(root, stem):
    for c in [root/"Annotations"/f"{stem}.xml", root/"Annotations"/"train"/f"{stem}.xml",
              root/"Annotations"/"test"/f"{stem}.xml"]:
        if c.exists(): return c
    hits=list((root/"Annotations").rglob(f"{stem}.xml"))
    return hits[0] if hits else None

def voc_to_yolo(xml_path, W, H):
    out=[]
    try: r=ET.parse(str(xml_path)).getroot()
    except Exception: return out
    for obj in r.findall("object"):
        bb=obj.find("bndbox");
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
    ap.add_argument("--methods", default="VIS,IR,Promedio,PiramideLaplace,Optimo_Multiescala,Propuesta_Novedosa")
    ap.add_argument("--limit-train", type=int, default=0)
    ap.add_argument("--limit-val", type=int, default=0)
    a=ap.parse_args()
    root=Path(a.llvip_root); out=Path(a.out)
    methods=[m.strip() for m in a.methods.split(",") if m.strip()]
    splits={"train":"train","test":"val"}   # LLVIP usa train/test -> YOLO train/val
    # preparar carpetas
    for m in methods:
        for sp in ("train","val"):
            (out/f"llvip_{m}"/"images"/sp).mkdir(parents=True, exist_ok=True)
            (out/f"llvip_{m}"/"labels"/sp).mkdir(parents=True, exist_ok=True)
    for src_split, yolo_split in splits.items():
        vdir=root/"visible"/src_split; idir=root/"infrared"/src_split
        if not vdir.exists():
            print(f"[AVISO] no existe {vdir}; salto split {src_split}"); continue
        vis=sorted([p for p in vdir.iterdir() if p.suffix.lower() in (".jpg",".png",".bmp")])
        lim = a.__dict__["limit_train"] if yolo_split=="train" else a.__dict__["limit_val"]
        if lim: vis=vis[:lim]
        print(f"Split {src_split}->{yolo_split}: {len(vis)} pares")
        for k,vp in enumerate(vis):
            stem=vp.stem; ip=idir/vp.name
            if not ip.exists(): continue
            v=load_gray01(vp); i=load_gray01(ip)
            if v is None or i is None: continue
            if v.shape!=i.shape: i=cv2.resize(i,(v.shape[1],v.shape[0]))
            H,W=v.shape[:2]
            ann=find_ann(root, stem); ylab=voc_to_yolo(ann,W,H) if ann else []
            for m in methods:
                if m=="VIS": img=v
                elif m=="IR": img=i
                else: img=FUSERS[m](v,i)
                save_uint8(img, out/f"llvip_{m}"/"images"/yolo_split/f"{stem}.jpg")
                (out/f"llvip_{m}"/"labels"/yolo_split/f"{stem}.txt").write_text("\n".join(ylab))
            if (k+1)%200==0: print(f"  {k+1} pares...")
    # data.yaml por metodo
    for m in methods:
        d=(out/f"llvip_{m}").resolve()
        (d/"data.yaml").write_text(
            f"path: {d}\ntrain: images/train\nval: images/val\nnc: 1\nnames: ['person']\n")
    print("LISTO. Datasets en", out.resolve())

if __name__=="__main__": main()
