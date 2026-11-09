# -*- coding: utf-8 -*-
"""Entrena los 30 detectores de la deteccion en M3FD: diez entradas por tres rondas.

Cada detector parte de los pesos preentrenados de YOLOv8n y se entrena 40 epocas con las imagenes de una
sola entrada (visible, infrarroja, el promedio simple o una fusion). Configuracion identica en los 30; lo
unico que cambia es la imagen y la semilla. Se conserva el ultimo punto de control de cada uno, que es el
que se evalua, sin elegir ninguno mirando la validacion (Seccion 3.5.2 del libro).

EL ORDEN IMPORTA. Se entrenan primero las diez entradas de la ronda 0, despues las de la ronda 1 y despues
las de la ronda 2, de modo que si el tiempo no alcanza quedan rondas completas y no entradas completas.
Dentro de cada ronda van primero visible e infrarroja, que definen los objetos de una sola camara.

Es reanudable: si un detector ya tiene sus 40 epocas, se salta. Registra cada corrida en
experiments/results/metrics_reports/m3fd_v2_entrenamientos.csv.

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/detection_m3fd/entrenar_v2.py
"""
import csv
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATOS = ROOT / "datasets"
RUNS = ROOT / "runs" / "m3fd_v2"
REG = ROOT / "experiments" / "results" / "metrics_reports" / "m3fd_v2_entrenamientos.csv"
PESOS_BASE = ROOT / "yolov8n.pt"
RONDAS = 3
# Los detectores de referencia (visible e infrarroja) definen que objetos son de una sola camara. Llevan
# semillas propias, 3, 4 y 5, para que su azar no quede correlacionado con el de las fusiones, que llevan
# 0, 1 y 2.
REFERENCIA = ["VIS", "IR"]
FUSIONES = ["Promedio", "Propuesta_Novedosa", "TopHat_Clasico", "PiramideLaplace",
            "RatioPiramide", "DWT", "DTCWT", "Curvelet"]
ENTRADAS = REFERENCIA + FUSIONES
EPOCAS, IMGSZ, LOTE = 40, 640, 16
# Explicitos para que queden documentados: son los que elige optimizer='auto' con este presupuesto
# (menos de 10000 iteraciones), y son los que informa el libro (Seccion 3.5.2).
OPTIM = dict(optimizer="AdamW", lr0=0.001, momentum=0.9)
# Si el final proyectado pasa de esta hora (reloj local), las rondas 1 y 2 se entrenan sin validar en cada
# epoca. En la corrida del libro fue asi (columna validar de m3fd_v2_entrenamientos.csv); la convergencia de
# analizar_v2.py solo usa la ronda 0, que siempre valida.
HORA_LIMITE = (17, 15)


def semilla(entrada, ronda):
    return ronda + 3 if entrada in REFERENCIA else ronda


def fijar_semilla_del_cargador(s):
    """Ultralytics 8.4.68 siembra el generador del DataLoader con una constante mas RANK y no mira la
    semilla (data/build.py, linea 348). Sin esto, las tres semillas darian el mismo orden de lotes y los
    mismos aumentos. RANK solo se usa ahi dentro de ese modulo."""
    import ultralytics.data.build as ub
    ub.RANK = s


def completo(dirrun):
    res = dirrun / "results.csv"
    if not (dirrun / "weights" / "last.pt").exists() or not res.exists():
        return False
    filas = res.read_text(encoding="utf-8").strip().splitlines()
    return len(filas) - 1 >= EPOCAS


def registrar(fila):
    nuevo = not REG.exists()
    with REG.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fila))
        if nuevo:
            w.writeheader()
        w.writerow(fila)


def main():
    from ultralytics import YOLO
    assert PESOS_BASE.exists(), f"faltan los pesos preentrenados: {PESOS_BASE}"
    for e in ENTRADAS:
        assert (DATOS / f"m3fd2_{e}" / "data.yaml").exists(), f"falta el conjunto de {e}"
    total = RONDAS * len(ENTRADAS)
    k, validar, inicio, primera = 0, True, time.time(), None
    for ronda in range(RONDAS):
        for e in ENTRADAS:
            k += 1
            s = semilla(e, ronda)
            nombre = f"{e}_s{s}"
            dirrun = RUNS / nombre
            if completo(dirrun):
                print(f"  [{k}/{total}] {nombre}: ya estaba, se salta", flush=True)
                continue
            print(f"  [{k}/{total}] {nombre}: entrenando ({time.strftime('%H:%M')}, "
                  f"validar={validar})", flush=True)
            t0 = time.time()
            estado = "ok"
            try:
                fijar_semilla_del_cargador(s)
                modelo = YOLO(str(PESOS_BASE))
                modelo.train(data=str(DATOS / f"m3fd2_{e}" / "data.yaml"), epochs=EPOCAS, imgsz=IMGSZ,
                             batch=LOTE, seed=s, deterministic=True, project=str(RUNS), name=nombre,
                             exist_ok=True, workers=4, plots=False, verbose=False, val=validar, **OPTIM)
            except Exception:
                estado = "error"
                traceback.print_exc()
            seg = time.time() - t0
            registrar({"entrada": e, "semilla": s, "ronda": ronda, "estado": estado,
                       "segundos": round(seg, 1), "epocas": EPOCAS, "validar": validar,
                       "fin": time.strftime("%Y-%m-%d %H:%M")})
            print(f"      {estado} en {seg / 60:.1f} min", flush=True)
            if primera is None and estado == "ok":
                primera = seg
                fin = inicio + total * primera
                limite = time.mktime(time.localtime()[:3] + HORA_LIMITE + (0, 0, 0, -1))
                if fin > limite:
                    print(f"      final proyectado {time.strftime('%H:%M', time.localtime(fin))}: "
                          f"las rondas 1 y 2 se entrenan sin validar en cada epoca", flush=True)
                    validar_despues = False
                else:
                    validar_despues = True
        if ronda == 0 and primera is not None:
            validar = validar_despues
    return 0


if __name__ == "__main__":
    sys.exit(main())
