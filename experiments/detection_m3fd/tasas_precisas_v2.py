# -*- coding: utf-8 -*-
"""Las tasas y los contrastes de la deteccion en M3FD con precision completa, sin tocar analizar_v2.py.

POR QUE. analizar_v2.py guarda las proporciones redondeadas a cuatro decimales (round(..., 4)). Al pasarlas a
porcentaje con un decimal hay un segundo redondeo, y en dos celdas el resultado cambia segun como se redondee:
la tasa de ambas camaras de la piramide de Laplace es 97,0534 % (el CSV dice 0,9705, que se imprimia 97,0) y la
equilibrada de DTCWT es 62,9495 % (el CSV dice 0,6295, que redondeado hacia arriba da 63,0). Con cuatro
decimales no hay regla de redondeo que acierte en las dos.

El calculo de analizar_v2.py, que produjo los CSV oficiales, no se modifica. Este script lo IMPORTA y corre
su misma funcion main() con dos cambios que no tocan el calculo:
  1. la funcion round del modulo pasa a devolver el valor sin redondear;
  2. el modulo lee y escribe en una carpeta temporal, con copias de sus dos entradas (predicciones y prueba),
     para no pisar los CSV oficiales; las etiquetas y las imagenes de datasets/m3fd2_VIS las lee del
     repositorio y son imprescindibles.
El bootstrap usa la semilla fija del modulo (default_rng(0)), asi que los intervalos son los mismos. Al final
comprueba que, redondeados a cuatro decimales, los valores coinciden con los CSV oficiales, y guarda:
  m3fd_v2_tasas_precisas.csv       las tasas sin redondear
  m3fd_v2_contrastes_precisos.csv  las diferencias y los intervalos sin redondear

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/detection_m3fd/tasas_precisas_v2.py
"""
import shutil
import sys
import tempfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "detection_m3fd"))
MR = ROOT / "experiments" / "results" / "metrics_reports"

import analizar_v2 as a  # noqa: E402


def main():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for f in ("m3fd_v2_predicciones.csv", "m3fd_v2_prueba.csv"):
            shutil.copy2(MR / f, tmp / f)
        a.MR = tmp
        a.round = lambda x, n=None: x          # solo el round del modulo; el calculo no cambia
        if a.main() != 0:
            raise SystemExit("analizar_v2.main() no termino bien")
        tasas = pd.read_csv(tmp / "m3fd_v2_tasas.csv")
        cont = pd.read_csv(tmp / "m3fd_v2_contrastes.csv")

    # control: redondeados a cuatro decimales, tienen que ser los CSV oficiales
    for nombre, nuevo, claves in (("m3fd_v2_tasas.csv", tasas, ["punto", "entrada"]),
                                  ("m3fd_v2_contrastes.csv", cont, ["punto", "contra"])):
        oficial = pd.read_csv(MR / nombre).set_index(claves)
        n = nuevo.set_index(claves).loc[oficial.index]
        num = [c for c in oficial.columns if pd.api.types.is_float_dtype(oficial[c])]
        dif = (n[num].astype(float).round(4) - oficial[num]).abs().max().max()
        textos = [c for c in oficial.columns if c not in num]
        igual = all((n[c].astype(str) == oficial[c].astype(str)).all() for c in textos)
        print(f"  {nombre}: diferencia maxima al redondear a 4 decimales = {dif:.1e}; "
              f"columnas no numericas iguales: {igual}")
        if dif > 1e-9 or not igual:
            raise SystemExit(f"ABORTA: la corrida sin redondeo no reproduce {nombre}")

    tasas.to_csv(MR / "m3fd_v2_tasas_precisas.csv", index=False)
    cont.to_csv(MR / "m3fd_v2_contrastes_precisos.csv", index=False)
    print("  -> m3fd_v2_tasas_precisas.csv, m3fd_v2_contrastes_precisos.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
