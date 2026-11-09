"""
run_stats_seis_metricas.py
--------------------------
Rehace el analisis estadistico con el criterio de SEIS metricas que adopta el libro,
en lugar de las nueve de la bateria inicial. No recalcula ninguna metrica: lee el mismo
all_metrics.csv y solo cambia que metricas entran al promedio.

POR QUE SEIS Y NO NUEVE. Las nueve de la bateria inicial no son nueve mediciones independientes:

  - FE es EN reescalada por una constante por escena (ver src.metrics.evaluators.
    fusion_efficiency), de modo que dentro de cada imagen ordena los metodos exactamente
    igual que EN. En el promedio de nueve, la entropia pesa 2/9 en vez de 1/9.
  - SF y MG miden lo mismo (actividad de gradiente) por dos caminos casi equivalentes.
  - MI_vis y MI_ir son la misma metrica evaluada contra cada fuente; contarlas por separado
    le da a la informacion mutua peso doble y, ademas, premia al metodo que se parece a una
    sola de las dos entradas, que es justo lo contrario de lo que se quiere de una fusion.

El criterio de seis: EN, SD y MG (actividad) mas MI, SSIM y PSNR (fidelidad), con
MI = (MI_vis + MI_ir) / 2 calculada POR IMAGEN antes de rankear. Tres de actividad y tres
de fidelidad, ninguna duplicada.

Genera, junto a los archivos de nueve metricas y sin pisarlos:
  descriptive_means_seis.csv        medias por metodo de las seis
  ranking_seis_metricas.csv         promedio de rangos intra-bloque, seis metricas
  friedman_seis_metricas.csv        Friedman por metrica
  wilcoxon_seis_metricas.csv        Wilcoxon pareado con correccion de Holm
  control_negativo_seis_metricas.csv  los 14 brazos del control negativo, seis metricas

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/run_stats_seis_metricas.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
MDIR = ROOT / "experiments" / "results" / "metrics_reports"

# Las seis. Todas son "mayor es mejor", asi que el rango 1 va al valor mas alto.
SEIS = ["EN", "SD", "MG", "MI", "SSIM", "PSNR"]
ACTIVIDAD = ["EN", "SD", "MG"]
FIDELIDAD = ["MI", "SSIM", "PSNR"]


def con_mi_unificada(df):
    """Agrega la columna MI como promedio por fila de MI_vis y MI_ir.

    Se promedia POR IMAGEN, no sobre las medias: el rango de un promedio no es el promedio
    de los rangos, y el que importa aca es el primero.
    """
    out = df.copy()
    out["MI"] = (out["MI_vis"] + out["MI_ir"]) / 2.0
    return out


def rangos_intrabloque(df, col_metodo, col_bloque, metricas):
    """Promedio de rangos intra-bloque, la tabla que acompana a Friedman.

    Dentro de cada bloque (imagen) se rankean los metodos, 1 = mejor, y se promedian
    los rangos sobre los bloques.
    """
    metodos = sorted(df[col_metodo].unique())
    bloques = sorted(df[col_bloque].unique())
    tabla = pd.DataFrame(index=metodos)
    for m in metricas:
        piv = df.pivot(index=col_bloque, columns=col_metodo, values=m).loc[bloques, metodos]
        tabla[m] = piv.rank(axis=1, ascending=False, method="average").mean(axis=0)
    return tabla


def holm(pvalores):
    """Correccion de Holm sobre un vector de p-valores. Devuelve los p ajustados."""
    p = np.asarray(pvalores, dtype=float)
    p = np.where(np.isnan(p), 1.0, p)
    n = len(p)
    orden = np.argsort(p)
    ajust = np.empty(n)
    corriendo = 0.0
    for i, idx in enumerate(orden):
        v = min(1.0, (n - i) * p[idx])
        corriendo = max(corriendo, v)
        ajust[idx] = corriendo
    return ajust


def rank_biserial(a, b):
    """Tamano de efecto matched-pairs rank-biserial para Wilcoxon."""
    d = a - b
    d = d[d != 0]
    if len(d) == 0:
        return 0.0
    r = stats.rankdata(np.abs(d))
    rpos, rneg = r[d > 0].sum(), r[d < 0].sum()
    total = rpos + rneg
    return float((rpos - rneg) / total) if total > 0 else 0.0


def main():
    df = con_mi_unificada(pd.read_csv(MDIR / "all_metrics.csv"))
    metodos = sorted(df["method"].unique())
    imagenes = sorted(df["image"].unique())
    print(f"  {len(metodos)} metodos x {len(imagenes)} imagenes = {len(df)} filas")

    # ------------------------------------------------------------------ medias
    medias = df.groupby("method")[SEIS].mean().round(4)
    medias.to_csv(MDIR / "descriptive_means_seis.csv")

    # ------------------------------------------------------------------ ranking
    tabla = rangos_intrabloque(df, "method", "image", SEIS)
    tabla["rango_6"] = tabla[SEIS].mean(axis=1)
    tabla["rango_actividad"] = tabla[ACTIVIDAD].mean(axis=1)
    tabla["rango_fidelidad"] = tabla[FIDELIDAD].mean(axis=1)
    tabla = tabla.round(3).sort_values("rango_6")
    tabla.insert(0, "puesto", range(1, len(tabla) + 1))
    tabla.to_csv(MDIR / "ranking_seis_metricas.csv")

    # ------------------------------------------------------------------ Friedman
    filas = []
    for m in SEIS:
        piv = df.pivot(index="image", columns="method", values=m).loc[imagenes, metodos]
        chi2, p = stats.friedmanchisquare(*[piv[c].values for c in metodos])
        filas.append({"metric": m, "chi2": chi2, "p_value": p, "significant_05": p < 0.05})
    pd.DataFrame(filas).to_csv(MDIR / "friedman_seis_metricas.csv", index=False)

    # ------------------------------------------------------------------ Wilcoxon
    morfologicos = [x for x in metodos if x.startswith("TopHat") or x.startswith("Propuesta")]
    comparativos = [x for x in metodos if x not in morfologicos]
    contrastes = [(a, b) for a in morfologicos for b in comparativos]
    if "Propuesta_Novedosa" in metodos and "TopHat_Clasico" in metodos:
        contrastes.append(("Propuesta_Novedosa", "TopHat_Clasico"))

    bloques = []
    for m in SEIS:
        piv = df.pivot(index="image", columns="method", values=m).loc[imagenes, metodos]
        filas = []
        for a, b in contrastes:
            xa, xb = piv[a].values, piv[b].values
            try:
                w, p = stats.wilcoxon(xa, xb)
            except ValueError:
                w, p = np.nan, 1.0
            filas.append({
                "metric": m, "morfologico": a, "comparativo": b,
                "media_morfologico": round(float(xa.mean()), 4),
                "media_comparativo": round(float(xb.mean()), 4),
                "diff": round(float(xa.mean() - xb.mean()), 4),
                "wilcoxon_W": w, "p_value": p,
                "effect_r": round(rank_biserial(xa, xb), 3),
            })
        bdf = pd.DataFrame(filas)
        # Holm dentro de cada metrica, igual que en el analisis de nueve.
        bdf["p_holm"] = holm(bdf["p_value"].values)
        bdf["sig_holm_05"] = bdf["p_holm"] < 0.05
        bloques.append(bdf)
    wx = pd.concat(bloques, ignore_index=True)
    wx.to_csv(MDIR / "wilcoxon_seis_metricas.csv", index=False)

    # ------------------------------------------------- control negativo, 14 brazos
    cn = MDIR / "control_negativo.csv"
    if cn.exists():
        dcn = con_mi_unificada(pd.read_csv(cn))
        tcn = rangos_intrabloque(dcn, "brazo", "imagen", SEIS)
        tcn["rango_6"] = tcn[SEIS].mean(axis=1)
        tcn = tcn.round(3).sort_values("rango_6")
        tcn.insert(0, "puesto", range(1, len(tcn) + 1))
        tcn.to_csv(MDIR / "control_negativo_seis_metricas.csv")

    # ------------------------------------------------------------------ resumen
    print("\n  === Ranking con seis metricas (menor = mejor) ===")
    print(tabla[["puesto", "rango_6", "rango_actividad", "rango_fidelidad"]].to_string())
    print("\n  === Medias ===")
    print(medias.to_string())
    prop = wx[(wx["morfologico"] == "Propuesta_Novedosa") & wx["sig_holm_05"]]
    vs_sota = prop[prop["comparativo"] != "TopHat_Clasico"]
    gana = vs_sota[vs_sota["diff"] > 0].groupby("metric").size()
    print("\n  === Propuesta vs los cinco comparativos: contrastes ganados y significativos ===")
    print(gana.to_string() if len(gana) else "  ninguno")
    vs_th = prop[prop["comparativo"] == "TopHat_Clasico"]
    print("\n  === Propuesta vs Top-Hat clasico: metricas con diferencia significativa ===")
    for _, f in vs_th.iterrows():
        signo = "a favor" if f["diff"] > 0 else "en contra"
        print(f"    {f['metric']:6s} {signo}  diff={f['diff']:+.4f}  p_holm={f['p_holm']:.2e}")
    if cn.exists():
        print("\n  === Control negativo, 14 brazos, seis metricas ===")
        print(tcn[["puesto", "rango_6"]].to_string())
    print(f"\n  -> 5 archivos escritos en {MDIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
