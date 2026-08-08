# -*- coding: utf-8 -*-
"""Potencia del contraste de McNemar del conteo por escena (H6).

Motivo. El informe afirmaba que la hipotesis de traslacion «se rechaza, con muestra suficiente».
Esa frase no tenia ningun calculo detras, y ademas es delicada: el contraste es un McNemar exacto
con p = 0,21, o sea NO significativo. Rechazar una hipotesis apoyandose en un test que no rechaza
exige decir para que diferencia alcanza la muestra, y eso es una cuenta, no una opinion.

Lo que se calcula. El test de McNemar condiciona en los pares DISCORDANTES: de las 232 escenas,
la propuesta recupera ambas clases donde el visible no en b escenas, y el visible donde la
propuesta no en c escenas; el resto no aporta informacion. Bajo H0 cada discordante es una moneda
justa, de modo que el test es un binomial exacto de dos colas sobre b con n = b + c.

La potencia se calcula CONDICIONAL a esos n discordantes, que es lo estandar para McNemar y lo que
corresponde declarar. Para una diferencia verdadera de delta puntos porcentuales sobre las N
escenas se tiene b - c = delta*N/100 y b + c = n, de modo que la proporcion bajo la alternativa es
p1 = (n + delta*N/100) / (2n); con ella se suma la probabilidad de caer en la region de rechazo.

Salida: experiments/results/metrics_reports/potencia_mcnemar.csv
Uso:    .venv\\Scripts\\python.exe -X utf8 experiments/potencia_mcnemar.py
"""
import os
import sys
from pathlib import Path

os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np
import pandas as pd
from scipy.stats import binom, binomtest

REP = Path("experiments/results/metrics_reports")
SALIDA = REP / "potencia_mcnemar.csv"
ALFA = 0.05
PROP, VIS = "Propuesta_Novedosa", "VIS"


def region_de_rechazo(n, alfa=ALFA):
    """Los valores de b que el binomial exacto de dos colas rechaza, con n discordantes.

    Se usa el mismo criterio que scipy: se rechaza cuando la suma de las probabilidades de los
    resultados no mas probables que el observado no supera alfa. Calcularlo asi —y no con una
    formula cerrada— garantiza que la potencia se mida sobre EXACTAMENTE el test que se reporta.
    """
    return {b for b in range(n + 1) if binomtest(b, n, 0.5).pvalue <= alfa}


def main():
    d = pd.read_csv(REP / "complementariedad_resumen.csv").set_index("entrada")
    b = int(d.loc[PROP, "gana_vs_VIS"])       # escenas donde la propuesta recupera ambas y el VIS no
    c = int(d.loc[PROP, "pierde_vs_VIS"])     # al reves
    n = b + c
    N = int(d.loc[PROP, "escenas"])
    amb_p, amb_v = int(d.loc[PROP, "recupera_ambas"]), int(d.loc[VIS, "recupera_ambas"])
    dif_obs = 100.0 * (amb_p - amb_v) / N

    print(f"escenas N = {N}")
    print(f"  la propuesta recupera ambas en {amb_p} ({100*amb_p/N:.1f} %)")
    print(f"  el visible solo en          {amb_v} ({100*amb_v/N:.1f} %)")
    print(f"  diferencia observada: {dif_obs:+.1f} puntos porcentuales")
    print(f"  discordantes: b = {b} (gana la propuesta), c = {c} (gana el visible), n = {n}")

    pr = binomtest(b, n, 0.5)
    print(f"\nMcNemar exacto de dos colas: p = {pr.pvalue:.4f}"
          f"  ({'rechaza' if pr.pvalue <= ALFA else 'NO rechaza'} al {ALFA:.0%})")

    RR = region_de_rechazo(n)
    print(f"region de rechazo con n = {n}: b <= {max(x for x in RR if x < n/2)} "
          f"o b >= {min(x for x in RR if x > n/2)}  ({len(RR)} valores)")
    # comprobacion: el nivel real del test exacto no puede pasarse de alfa
    nivel = float(sum(binom.pmf(x, n, 0.5) for x in RR))
    print(f"nivel real del test exacto: {nivel:.4f} (<= {ALFA})")
    assert nivel <= ALFA + 1e-12, "la region de rechazo excede el nivel nominal"

    filas = []
    for delta in np.round(np.arange(0.0, 12.01, 0.1), 2):
        dif_conteo = delta * N / 100.0
        p1 = (n + dif_conteo) / (2 * n)
        if not (0.0 <= p1 <= 1.0):
            continue
        pot = float(sum(binom.pmf(x, n, p1) for x in RR))
        filas.append({"delta_pp": delta, "dif_escenas": round(dif_conteo, 2),
                      "p_alternativa": round(p1, 6), "potencia": round(pot, 6)})
    t = pd.DataFrame(filas)

    # Con delta = 0 la potencia tiene que dar el nivel del test: es el control del calculo. La
    # tolerancia es 1e-6 y no 1e-9 porque la columna se guarda redondeada a seis decimales.
    p0 = float(t.loc[t.delta_pp == 0.0, "potencia"].iloc[0])
    assert abs(p0 - nivel) < 1e-6, f"con delta = 0 la potencia deberia ser el nivel: {p0} vs {nivel}"
    print(f"control: con delta = 0 la potencia es {p0:.4f}, igual al nivel del test")

    d80 = t[t.potencia >= 0.80]
    delta80 = float(d80.delta_pp.iloc[0]) if len(d80) else float("nan")
    pot_obs = float(t.iloc[(t.delta_pp - abs(dif_obs)).abs().argsort().iloc[0]].potencia)

    print(f"\npotencia >= 0,80 a partir de delta = {delta80:.1f} puntos porcentuales")
    for dd in (3.0, 5.0, abs(dif_obs), delta80):
        fila = t.iloc[(t.delta_pp - dd).abs().argsort().iloc[0]]
        print(f"   delta = {fila.delta_pp:5.1f} pp -> potencia {fila.potencia:.3f}")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(SALIDA, index=False)
    print(f"\n-> {SALIDA}  ({len(t)} filas)")
    print(f"   p del contraste {pr.pvalue:.4f} · delta al 80 % {delta80:.1f} pp · "
          f"potencia en la diferencia observada {pot_obs:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
