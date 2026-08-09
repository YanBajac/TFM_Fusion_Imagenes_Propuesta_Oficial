# -*- coding: utf-8 -*-
"""Diferencias pareadas de la propuesta contra su rival mas fuerte, con intervalo de confianza.

Motivo. En sus 82 paginas el informe no publica NI UNA medida de dispersion: ni un intervalo de
confianza, ni un error estandar, ni un rango intercuartil. Todo son medias sobre 20 pares. Ademas
la Tabla 6 anuncia «con correccion de Holm y tamano de efecto rank-biserial» y despues no muestra
ningun p-valor ni ningun tamano de efecto: solo las etiquetas mejor / peor / ~. Las dos columnas
—p_holm y effect_r— ya estan calculadas en wilcoxon_results.csv.

Sin dispersion, una ventaja de 0,17 en entropia parece ruido de redondeo aunque no lo sea, y una
de 0,003 parece un resultado aunque no lo sea. Con 20 pares y un diseno pareado el intervalo es
barato de calcular y decide la lectura.

Que se calcula. Para cada una de las nueve metricas del criterio, la comparacion contra el RIVAL
MAS FUERTE en esa metrica —el mejor de los seis comparativos, que es la comparacion exigente— y:

  - la diferencia media pareada sobre los 20 pares (propuesta menos rival),
  - su intervalo de confianza al 95 % por bootstrap percentil sobre los pares,
  - en cuantos de los 20 pares la propuesta queda por delante,
  - el p de Wilcoxon con correccion de Holm y el tamano de efecto rank-biserial, tomados de
    wilcoxon_results.csv, que es donde el informe dice que estan.

El bootstrap remuestrea PARES, no valores sueltos, porque el diseno es pareado: cada par aporta
una diferencia y esa es la unidad de remuestreo. La semilla es fija para que el intervalo
publicado sea reproducible; sin eso el numero cambiaria en cada compilacion del informe.

Salida: experiments/results/metrics_reports/dispersion_pareada.csv
Uso:    .venv\\Scripts\\python.exe -X utf8 experiments/dispersion_pareada.py
"""
import os
import sys
from pathlib import Path

os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np
import pandas as pd

REP = Path("experiments/results/metrics_reports")
SALIDA = REP / "dispersion_pareada.csv"
PROP = "Propuesta_Novedosa"
METS = ["EN", "SD", "FE", "MG", "MI_vis", "MI_ir", "SF", "SSIM", "PSNR"]
B = 10_000          # remuestreos
SEMILLA = 20260808  # fija: el intervalo publicado tiene que ser el mismo en cada compilacion


def ic_bootstrap(dif, b=B, semilla=SEMILLA, alfa=0.05):
    """IC percentil de la media, remuestreando los pares con reemplazo."""
    rng = np.random.default_rng(semilla)
    n = len(dif)
    idx = rng.integers(0, n, size=(b, n))
    medias = dif[idx].mean(axis=1)
    return (float(np.percentile(medias, 100 * alfa / 2)),
            float(np.percentile(medias, 100 * (1 - alfa / 2))))


def main():
    am = pd.read_csv(REP / "all_metrics.csv")
    wl = pd.read_csv(REP / "wilcoxon_results.csv")
    imgs = sorted(am.image.unique())
    rivales = [m for m in sorted(am.method.unique()) if m != PROP]
    print(f"{len(imgs)} pares · {len(rivales)} comparativos · {len(METS)} metricas")
    print(f"bootstrap: {B} remuestreos de PARES, semilla {SEMILLA}\n")

    piv = {m: am[am.method == m].set_index("image").loc[imgs] for m in am.method.unique()}
    filas = []
    for met in METS:
        prop = piv[PROP][met].to_numpy(float)
        # el rival mas fuerte en esta metrica: el de mayor media (las nueve son «mayor es mejor»)
        medias = {r: float(piv[r][met].mean()) for r in rivales}
        rival = max(medias, key=medias.get)
        riv = piv[rival][met].to_numpy(float)
        dif = prop - riv
        lo, hi = ic_bootstrap(dif)
        w = wl[(wl.tophat == PROP) & (wl.baseline == rival) & (wl.metric == met)]
        ph = float(w.p_holm.iloc[0]) if len(w) else float("nan")
        er = float(w.effect_r.iloc[0]) if len(w) else float("nan")
        filas.append({
            "metrica": met, "rival_mas_fuerte": rival,
            "media_propuesta": round(float(prop.mean()), 6),
            "media_rival": round(medias[rival], 6),
            "dif_media": round(float(dif.mean()), 6),
            "ic95_lo": round(lo, 6), "ic95_hi": round(hi, 6),
            "pares_a_favor": int((dif > 0).sum()), "pares": len(dif),
            "p_holm": round(ph, 6), "effect_r": round(er, 6),
            # el intervalo excluye el cero: la direccion se sostiene con 95 % de confianza
            "ic_excluye_cero": bool(lo > 0 or hi < 0),
        })
        signo = "+" if dif.mean() >= 0 else ""
        print(f"  {met:7s} vs {rival:18s} {signo}{dif.mean():9.4f}  "
              f"IC95 [{lo:+.4f}; {hi:+.4f}]  {(dif>0).sum():2d}/{len(dif)} pares  "
              f"p_Holm {ph:.4f}  r {er:+.3f}"
              f"{'' if (lo > 0 or hi < 0) else '   <- el IC incluye el cero'}")

    t = pd.DataFrame(filas)
    # Control: el signo de la diferencia media y el de effect_r tienen que coincidir. Si no,
    # una de las dos fuentes esta describiendo otra comparacion.
    disc = t[(t.dif_media * t.effect_r < 0) & (t.p_holm < 0.05)]
    assert len(disc) == 0, (
        f"la diferencia media y el tamano de efecto discrepan en signo: {list(disc.metrica)}")
    # Control: la media de la diferencia pareada tiene que ser la diferencia de las medias.
    assert np.allclose(t.dif_media, t.media_propuesta - t.media_rival, atol=1e-5), \
        "la diferencia pareada no coincide con la diferencia de medias"

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(SALIDA, index=False)
    n_ex = int(t.ic_excluye_cero.sum())
    print(f"\n{n_ex} de {len(t)} intervalos excluyen el cero")
    print(f"-> {SALIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
