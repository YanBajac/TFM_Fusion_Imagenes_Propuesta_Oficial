# -*- coding: utf-8 -*-
"""
train_eval_llvip.py — Entrena un YOLO por cada version fusionada de LLVIP y compara mAP.

Entrena el MISMO modelo con identica config/semilla sobre cada dataset llvip_<metodo>
(generados por prepare_llvip.py) y reporta mAP@0.5 y mAP@0.5:0.95. Solo cambian los
pixeles fusionados -> la diferencia de mAP es atribuible al metodo de fusion.

Uso:
  python experiments\detection_llvip\train_eval_llvip.py --datasets-dir datasets `
      --methods VIS,IR,Promedio,PiramideLaplace,Optimo_Multiescala,Propuesta_Novedosa `
      --model yolov8n.pt --epochs 40 --imgsz 640 --device 0
"""
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/"experiments"/"results"/"metrics_reports"/"detection_llvip_map.csv"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--datasets-dir", default="datasets")
    ap.add_argument("--methods", default="VIS,IR,Promedio,PiramideLaplace,Optimo_Multiescala,Propuesta_Novedosa")
    ap.add_argument("--model", default="yolov8n.pt")
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--device", default="")     # "0" GPU, "cpu", "" auto
    ap.add_argument("--seed", type=int, default=0)
    a=ap.parse_args()
    from ultralytics import YOLO
    import pandas as pd
    dd=Path(a.datasets_dir); rows=[]
    for m in [x.strip() for x in a.methods.split(",") if x.strip()]:
        data=dd/f"llvip_{m}"/"data.yaml"
        if not data.exists():
            print(f"[AVISO] falta {data}; salto {m}"); continue
        print(f"\n===== Entrenando {m} =====")
        model=YOLO(a.model)
        kw=dict(data=str(data), epochs=a.epochs, imgsz=a.imgsz, batch=a.batch,
                seed=a.seed, deterministic=True, project="runs/llvip", name=m,
                exist_ok=True, verbose=False)
        if a.device!="" : kw["device"]=a.device
        model.train(**kw)
        met=model.val(data=str(data), split="val", verbose=False)
        rows.append({"method":m, "mAP50":round(float(met.box.map50),4),
                     "mAP50_95":round(float(met.box.map),4),
                     "precision":round(float(met.box.mp),4), "recall":round(float(met.box.mr),4)})
        print(f"  {m}: mAP50={rows[-1]['mAP50']}  mAP50-95={rows[-1]['mAP50_95']}")
    df=pd.DataFrame(rows).sort_values("mAP50_95", ascending=False)
    OUT.parent.mkdir(parents=True, exist_ok=True); df.to_csv(OUT, index=False)
    print("\n===== COMPARACION mAP (LLVIP) =====")
    print(df.to_string(index=False)); print("\nGuardado:", OUT)

if __name__=="__main__": main()
