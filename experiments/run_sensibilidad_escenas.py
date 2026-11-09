"""
run_sensibilidad_escenas.py
---------------------------
Repite el analisis de seis metricas tomando como bloque la ESCENA y no el par.

POR QUE. Los veinte pares del corpus vienen de trece escenas: APC_1, APC_3 y soldier_behind_smoke
aportan tres tomas cada una y soldier_in_trench aporta dos (escenas_distintas.csv). Friedman, Wilcoxon
y el ranking de run_stats_seis_metricas.py tratan los veinte pares como bloques independientes, y dos
tomas de una misma escena no lo son del todo: los valores p de ese analisis son optimistas. Aca se
promedian, metodo por metodo, las metricas de las tomas de cada escena, y se rehace todo con trece
bloques. Si el orden y las decisiones se mantienen, la dependencia entre tomas no cambia la lectura.

No recalcula ninguna metrica: lee all_metrics.csv y el mapa par -> escena de escenas_distintas.csv.
Usa las mismas funciones y los mismos once contrastes que run_stats_seis_metricas.py.

Genera:
  sensibilidad_escenas_ranking.csv    promedio de rangos con 13 bloques
  sensibilidad_escenas_friedman.csv   Friedman por metrica con 13 bloques
  sensibilidad_escenas_wilcoxon.csv   los 66 contrastes con 13 bloques, junto a los de 20 pares

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/run_sensibilidad_escenas.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))

from run_stats_seis_metricas import (SEIS, ACTIVIDAD, FIDELIDAD, MDIR, con_mi_unificada,
                                     rangos_intrabloque, holm)


def main():
    df = con_mi_unificada(pd.read_csv(MDIR / "all_metrics.csv"))
    mapa = pd.read_csv(MDIR / "escenas_distintas.csv").set_index("par")["escena"]
    faltan = sorted(set(df["image"]) - set(mapa.index))
    assert not faltan, f"pares sin escena en escenas_distintas.csv: {faltan}"
    df["escena"] = df["image"].map(mapa)
    esc = df.groupby(["method", "escena"], as_index=False)[SEIS].mean()
    metodos = sorted(esc["method"].unique())
    escenas = sorted(esc["escena"].unique())
    print(f"  {df['image'].nunique()} pares -> {len(escenas)} escenas, {len(metodos)} metodos")

    # ------------------------------------------------------------------ ranking
    tabla = rangos_intrabloque(esc, "method", "escena", SEIS)
    tabla["rango_6"] = tabla[SEIS].mean(axis=1)
    tabla["rango_actividad"] = tabla[ACTIVIDAD].mean(axis=1)
    tabla["rango_fidelidad"] = tabla[FIDELIDAD].mean(axis=1)
    tabla = tabla.round(3).sort_values("rango_6")
    tabla.insert(0, "puesto", range(1, len(tabla) + 1))
    tabla.to_csv(MDIR / "sensibilidad_escenas_ranking.csv")

    # ------------------------------------------------------------------ Friedman
    filas = []
    for m in SEIS:
        piv = esc.pivot(index="escena", columns="method", values=m).loc[escenas, metodos]
        chi2, p = stats.friedmanchisquare(*[piv[c].values for c in metodos])
        filas.append({"metric": m, "chi2": chi2, "p_value": p, "significant_05": p < 0.05})
    fr = pd.DataFrame(filas)
    fr.to_csv(MDIR / "sensibilidad_escenas_friedman.csv", index=False)

    # ------------------------------------------------------------------ Wilcoxon
    morfologicos = [x for x in metodos if x.startswith("TopHat") or x.startswith("Propuesta")]
    comparativos = [x for x in metodos if x not in morfologicos]
    contrastes = [(a, b) for a in morfologicos for b in comparativos]
    contrastes.append(("Propuesta_Novedosa", "TopHat_Clasico"))
    bloques = []
    for m in SEIS:
        piv = esc.pivot(index="escena", columns="method", values=m).loc[escenas, metodos]
        filas = []
        for a, b in contrastes:
            xa, xb = piv[a].values, piv[b].values
            try:
                _, p = stats.wilcoxon(xa, xb)
            except ValueError:
                p = 1.0
            filas.append({"metric": m, "morfologico": a, "comparativo": b,
                          "diff_13": round(float(xa.mean() - xb.mean()), 4), "p_13": p})
        bdf = pd.DataFrame(filas)
        bdf["p_holm_13"] = holm(bdf["p_13"].values)
        bloques.append(bdf)
    wx = pd.concat(bloques, ignore_index=True)

    # junto a la version de veinte pares, para ver que decisiones cambian
    w20 = pd.read_csv(MDIR / "wilcoxon_seis_metricas.csv")[
        ["metric", "morfologico", "comparativo", "diff", "p_holm"]].rename(
        columns={"diff": "diff_20", "p_holm": "p_holm_20"})
    wx = wx.merge(w20, on=["metric", "morfologico", "comparativo"], how="left")
    wx["sig_20"] = wx["p_holm_20"] < 0.05
    wx["sig_13"] = wx["p_holm_13"] < 0.05
    wx["mismo_signo"] = np.sign(wx["diff_13"]) == np.sign(wx["diff_20"])
    wx["misma_decision"] = wx["sig_20"] == wx["sig_13"]
    wx.to_csv(MDIR / "sensibilidad_escenas_wilcoxon.csv", index=False)

    # ------------------------------------------------------------------ resumen
    r20 = pd.read_csv(MDIR / "ranking_seis_metricas.csv", index_col=0)
    print("\n  === Ranking, seis metricas: 20 pares frente a 13 escenas ===")
    comp = pd.DataFrame({"rango_20": r20["rango_6"], "puesto_20": r20["puesto"],
                         "rango_13": tabla["rango_6"], "puesto_13": tabla["puesto"]})
    print(comp.sort_values("rango_13").to_string())
    print("\n  === Friedman con 13 escenas ===")
    print(fr.to_string(index=False))
    n = len(wx)
    print(f"\n  === Wilcoxon + Holm: {n} contrastes ===")
    print(f"    mismo signo de la diferencia: {int(wx['mismo_signo'].sum())} de {n}")
    print(f"    misma decision al 5 %:        {int(wx['misma_decision'].sum())} de {n}")
    cambian = wx[~wx["misma_decision"]]
    if len(cambian):
        print("    cambian de decision:")
        print(cambian[["metric", "morfologico", "comparativo", "diff_20", "p_holm_20",
                       "diff_13", "p_holm_13"]].to_string(index=False))
    print(f"\n  -> 3 archivos sensibilidad_escenas_*.csv en {MDIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
