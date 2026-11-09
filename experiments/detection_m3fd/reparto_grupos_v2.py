# -*- coding: utf-8 -*-
"""Reparto por grupo de los objetos de una sola camara, y la diferencia con el Top-Hat clasico sin cada grupo.

POR QUE. Los intervalos de analizar_v2.py usan la varianza robusta por grupos, y los objetos de una sola camara
no se reparten parejo entre los grupos de la prueba. Este script deja a la vista ese reparto y cuanto depende
de cada grupo la diferencia de la propuesta con el Top-Hat clasico (Secciones 4.6.1 y 4.6.2 del libro):
  1. por umbral y por grupo, cuantos objetos son de solo la visible y cuantos de solo la infrarroja, junto
     con los cuadros de cada grupo;
  2. por umbral, la diferencia equilibrada propuesta menos Top-Hat clasico al dejar fuera un grupo por vez
     (solo los grupos que tienen objetos de una sola camara; sacar otro no cambia nada).

Igual que tasas_precisas_v2.py, IMPORTA analizar_v2.py y corre su main() en una carpeta temporal, con copias
de sus dos entradas (predicciones y prueba), para no pisar los CSV oficiales; las etiquetas y las imagenes
de datasets/m3fd2_VIS las lee del repositorio y son imprescindibles. La funcion round del modulo
devuelve el valor sin redondear y diferencia() queda envuelta: devuelve lo mismo que la original y, ademas,
guarda los objetos de cada contraste (su diferencia, su direccion y su grupo). Asi el reparto sale de la
misma seleccion de objetos que el analisis principal. Al final comprueba que las diferencias completas
coinciden con m3fd_v2_contrastes_precisos.csv.

SALIDA en experiments/results/metrics_reports/:
  m3fd_v2_reparto_grupos.csv   objetos de solo visible y de solo infrarroja por grupo y por umbral
  m3fd_v2_dejar_un_grupo.csv   la diferencia propuesta menos Top-Hat clasico sin cada grupo, por umbral

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/detection_m3fd/reparto_grupos_v2.py
"""
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "detection_m3fd"))
MR = ROOT / "experiments" / "results" / "metrics_reports"

import analizar_v2 as a  # noqa: E402

registro = []


def envolver(original):
    def diferencia(d, dirs, grupo):
        registro.append((np.asarray(d, float), np.asarray(dirs), np.asarray(grupo)))
        return original(d, dirs, grupo)
    return diferencia


def equilibrada(d, dirs):
    return 0.5 * d[dirs == "V"].mean() + 0.5 * d[dirs == "I"].mean()


def main():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for f in ("m3fd_v2_predicciones.csv", "m3fd_v2_prueba.csv"):
            shutil.copy2(MR / f, tmp / f)
        a.MR = tmp
        a.round = lambda x, n=None: x          # solo el round del modulo; el calculo no cambia
        a.diferencia = envolver(a.diferencia)
        if a.main() != 0:
            raise SystemExit("analizar_v2.main() no termino bien")
        cont = pd.read_csv(tmp / "m3fd_v2_contrastes.csv", dtype={"punto": str})

    # main() llama a diferencia() una vez por fila de contrastes y en el mismo orden
    assert len(cont) == len(registro), "no coincide el numero de contrastes"
    precisos = pd.read_csv(MR / "m3fd_v2_contrastes_precisos.csv", dtype={"punto": str})
    assert (cont[["punto", "contra"]].values == precisos[["punto", "contra"]].values).all(), "orden distinto"
    calc = np.array([equilibrada(d, dirs) for d, dirs, _ in registro])
    dif = float(np.abs(calc - precisos["diferencia"].values).max())
    print(f"  control: diferencias frente a m3fd_v2_contrastes_precisos.csv, maximo {dif:.1e}")
    if dif > 1e-12:
        raise SystemExit("ABORTA: la corrida no reproduce m3fd_v2_contrastes_precisos.csv")

    prueba = pd.read_csv(MR / "m3fd_v2_prueba.csv")
    prueba = prueba[prueba.entra]
    cuadros = prueba.groupby("grupo").size()

    filas_r, filas_d = [], []
    for (_, fila), (d, dirs, grp) in zip(cont.iterrows(), registro):
        if fila["contra"] != a.CLASICO:
            continue
        punto = fila["punto"]
        total = equilibrada(d, dirs)
        nV, nI = int((dirs == "V").sum()), int((dirs == "I").sum())
        for g in cuadros.index:
            filas_r.append({"punto": punto, "grupo": int(g), "cuadros": int(cuadros[g]),
                            "solo_visible": int(((dirs == "V") & (grp == g)).sum()),
                            "solo_infrarroja": int(((dirs == "I") & (grp == g)).sum()),
                            "total_solo_visible": nV, "total_solo_infrarroja": nI})
        for g in np.unique(grp):
            m = grp != g
            quedan_v, quedan_i = int((dirs[m] == "V").sum()), int((dirs[m] == "I").sum())
            filas_d.append({"punto": punto, "grupo_excluido": int(g),
                            "solo_visible_restantes": quedan_v, "solo_infrarroja_restantes": quedan_i,
                            "diferencia": equilibrada(d[m], dirs[m]) if quedan_v and quedan_i else np.nan,
                            "diferencia_con_todos": total})
    reparto, dejar = pd.DataFrame(filas_r), pd.DataFrame(filas_d)
    reparto.to_csv(MR / "m3fd_v2_reparto_grupos.csv", index=False)
    dejar.to_csv(MR / "m3fd_v2_dejar_un_grupo.csv", index=False)

    for punto, r in reparto.groupby("punto", sort=False):
        v = r.set_index("grupo")["solo_visible"]
        i = r.set_index("grupo")["solo_infrarroja"]
        dos = v.sort_values(ascending=False).iloc[:2]
        mayor = int(r.set_index("grupo")["cuadros"].idxmax())
        print(f"\n  === {punto}: {v.sum()} de solo visible y {i.sum()} de solo infrarroja, "
              f"en {int(((v + i) > 0).sum())} de {len(r)} grupos ===")
        print(f"  solo visible por grupo:    {v.to_dict()}")
        print(f"  solo infrarroja por grupo: {i.to_dict()}")
        print(f"  los dos grupos con mas objetos de solo visible: {dos.to_dict()} = {dos.sum()} de {v.sum()}")
        print(f"  grupo con mas cuadros: {mayor} ({int(cuadros[mayor])} cuadros), "
              f"{int(v[mayor])} de solo visible y {int(i[mayor])} de solo infrarroja")
        dd = dejar[dejar.punto == punto].set_index("grupo_excluido")["diferencia"]
        print(f"  propuesta menos Top-Hat clasico, puntos: con todos "
              f"{100 * dejar[dejar.punto == punto]['diferencia_con_todos'].iloc[0]:.2f}; sin cada grupo "
              + ", ".join(f"{g}: {100 * x:.2f}" for g, x in dd.items()))
    print("  -> m3fd_v2_reparto_grupos.csv, m3fd_v2_dejar_un_grupo.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
