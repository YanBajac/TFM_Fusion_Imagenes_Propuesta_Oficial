# -*- coding: utf-8 -*-
"""Corre los detectores sobre los cuadros de seguimiento y la prueba y guarda lo necesario para el analisis.

Por cada detector (entrada x semilla):
  1. mAP global y AP50 por clase en la prueba, con el validador de Ultralytics.
  2. Todas las predicciones de personas y luces con confianza >= 0,05, en los cuadros de seguimiento
     (sobrante), en la validacion y en la prueba. Se guardan crudas para que el umbral se aplique
     despues: el analisis calibra un umbral por detector en los cuadros de seguimiento, y
     la prueba es la union de 'test' y 'val'.

Corre en el procesador por defecto, para no frenar el entrenamiento; con el argumento 0 usa la GPU.

SALIDAS en experiments/results/metrics_reports/:
  m3fd_v2_map.csv            una fila por detector
  m3fd_v2_predicciones.csv   una fila por prediccion: entrada, semilla, parte, imagen, clase, caja, conf

Es reanudable: un detector ya evaluado se salta. El analisis lo hace analizar_v2.py.

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/detection_m3fd/evaluar_v2.py
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATOS = ROOT / "datasets"
RUNS = ROOT / "runs" / "m3fd_v2"
MR = ROOT / "experiments" / "results" / "metrics_reports"
NAMES = ["People", "Car", "Bus", "Motorcycle", "Lamp", "Truck"]
CLASES = {0: "People", 4: "Lamp"}
CONF_MIN = 0.05
DISPOSITIVO = sys.argv[1] if len(sys.argv) > 1 else "cpu"


def detectores():
    for d in sorted(RUNS.glob("*_s*")):
        if (d / "weights" / "last.pt").exists() and (d / "results.csv").exists():
            filas = (d / "results.csv").read_text(encoding="utf-8").strip().splitlines()
            if len(filas) - 1 >= 40:
                entrada, s = d.name.rsplit("_s", 1)
                yield entrada, int(s), d / "weights" / "last.pt"


def main():
    from ultralytics import YOLO
    f_map, f_pred = MR / "m3fd_v2_map.csv", MR / "m3fd_v2_predicciones.csv"
    hechos = set()
    if f_map.exists() and f_pred.exists():
        a = set(map(tuple, pd.read_csv(f_map)[["entrada", "semilla"]].values.tolist()))
        b = set(map(tuple, pd.read_csv(f_pred, usecols=["entrada", "semilla"]).drop_duplicates()
                    .values.tolist()))
        hechos = a & b
    for entrada, semilla, pesos in detectores():
        if (entrada, semilla) in hechos:
            continue
        print(f"  {entrada} semilla {semilla}", flush=True)
        modelo = YOLO(str(pesos))
        # en el procesador, para no competir por la GPU con el entrenamiento que sigue corriendo
        r = modelo.val(data=str(DATOS / f"m3fd2_{entrada}" / "data.yaml"), split="test",
                       imgsz=640, batch=16, plots=False, verbose=False, device=DISPOSITIVO)
        fila = {"entrada": entrada, "semilla": semilla,
                "mAP50": round(float(r.box.map50), 4), "mAP50_95": round(float(r.box.map), 4)}
        for i, c in enumerate(r.box.ap_class_index):
            fila[f"AP50_{NAMES[int(c)]}"] = round(float(r.box.ap50[i]), 4)
        filas = []
        # sobrante: calibra el umbral; test y val: la prueba
        for parte in ("sobrante", "val", "test"):
            carpeta = DATOS / f"m3fd2_{entrada}" / "images" / parte
            for img in sorted(carpeta.glob("*.jpg")):
                res = modelo.predict(str(img), conf=CONF_MIN, imgsz=640, verbose=False,
                                     device=DISPOSITIVO)[0]
                b = res.boxes
                if b is None or not len(b):
                    continue
                for caja, c, cf in zip(b.xyxy.cpu().numpy(), b.cls.cpu().numpy().astype(int),
                                       b.conf.cpu().numpy()):
                    if c in CLASES:
                        filas.append({"entrada": entrada, "semilla": semilla, "parte": parte,
                                      "imagen": img.stem, "clase": CLASES[c],
                                      "x1": round(float(caja[0]), 1), "y1": round(float(caja[1]), 1),
                                      "x2": round(float(caja[2]), 1), "y2": round(float(caja[3]), 1),
                                      "conf": round(float(cf), 4)})
        # se escriben juntas, al final de cada detector, para que un corte no deje uno a medias
        pd.DataFrame(filas).to_csv(f_pred, mode="a", header=not f_pred.exists(), index=False)
        pd.DataFrame([fila]).to_csv(f_map, mode="a", header=not f_map.exists(), index=False)
    print(f"  -> m3fd_v2_map.csv y m3fd_v2_predicciones.csv en {MR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
