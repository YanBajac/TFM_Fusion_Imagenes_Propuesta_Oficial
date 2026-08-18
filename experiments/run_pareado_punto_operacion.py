# -*- coding: utf-8 -*-
"""Prueba PAREADA entre el punto de operacion adoptado y el re-ajustado a la tarea.

POR QUE NO ALCANZA CON LOS TOTALES. La grilla dice que el punto adoptado (25; 0,30) conserva 57 de 119
objetos en la particion de reserva y que (5; 0,10) conserva 76. Comparar 57 contra 76 no dice si la
diferencia es consistente: podria ser que el re-ajuste gane 30 objetos y pierda 11, o que gane 19 y no
pierda ninguno, y las dos cosas dan el mismo total con solidez muy distinta. Lo que corresponde es un
McNemar sobre los objetos discordantes, que es la prueba para dos medidas binarias sobre los MISMOS
casos.

Y LA MISMA PRUEBA CONTRA LOS COMPARATIVOS, porque el punto re-ajustado queda a uno o dos objetos de la
piramide de Laplace y del DWT: con n = 119 eso no autoriza a decir «los supera». La prueba lo dice.

LAS DOS PARTICIONES SE INFORMAN POR SEPARADO, y no se promedian: en m3fd_comp se ELIGIO el punto y en
m3fd_test se VALIDA. Mezclarlas volveria a meter la seleccion dentro del numero que se reporta.

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/run_pareado_punto_operacion.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
from scipy.stats import binomtest

MR = ROOT / "experiments" / "results" / "metrics_reports"
SALIDA = MR / "pareado_punto_operacion.csv"
ADOPTADO = (25, 0.30)
CANDIDATO = (5, 0.10)
PROP = "Propuesta_Novedosa"


def mcnemar(a, b):
    """McNemar exacto sobre dos vectores binarios pareados. Devuelve (gana_a, gana_b, p).

    Exacto y no la aproximacion chi2 porque los discordantes son pocos —del orden de veinte— y ahi la
    aproximacion no vale. Es la misma prueba que el trabajo ya usa para el conteo por escena de M3FD.
    """
    g = int(((a == 1) & (b == 0)).sum())
    p_ = int(((a == 0) & (b == 1)).sum())
    n = g + p_
    if n == 0:
        return g, p_, 1.0
    return g, p_, float(binomtest(g, n, 0.5).pvalue)


def cargar(pref):
    suf = "" if pref == "m3fd_comp" else f"_{pref}"
    det = pd.read_csv(MR / f"grilla_complementariedad_detalle{suf}.csv")
    ref = pd.read_csv(MR / f"complementariedad_objetos{suf}.csv")
    ref["clave"] = (ref.escena.map(lambda s: str(int(s)) if str(s).isdigit() else str(s))
                    + "|" + ref.clase + "|" + ref.objeto.astype(str))
    # los objetos exclusivos de UNA modalidad: el universo donde la condicion tiene sentido
    unica = ref[((ref.VIS == 1) & (ref.IR == 0)) | ((ref.IR == 1) & (ref.VIS == 0))].copy()
    return det, unica


def vector(det, r, m, claves):
    d = det[(det.r == r) & (det.m.round(4) == round(m, 4))].set_index("clave").detectado
    return claves.map(lambda k: int(d.get(k, 0)))


def main():
    filas = []
    for pref in ("m3fd_comp", "m3fd_test"):
        try:
            det, unica = cargar(pref)
        except FileNotFoundError as e:
            print(f"  {pref}: falta {Path(e.filename).name}; se omite")
            continue
        claves = unica.clave
        etiqueta = "seleccion" if pref == "m3fd_comp" else "reserva"
        print(f"\n{'=' * 92}\n{pref}  ({etiqueta}) · {len(claves)} objetos exclusivos de una modalidad")
        print("=" * 92)

        v_ad = vector(det, *ADOPTADO, claves)
        v_ca = vector(det, *CANDIDATO, claves)
        g, p_, p = mcnemar(v_ca, v_ad)
        print(f"\n  el re-ajuste {CANDIDATO} contra el adoptado {ADOPTADO}")
        print(f"    conserva {int(v_ca.sum())} contra {int(v_ad.sum())} de {len(claves)}")
        print(f"    discordantes: gana {g} · pierde {p_} · McNemar exacto p = {p:.4g}")
        filas.append({"particion": pref, "rol": etiqueta, "comparacion": "reajustado_vs_adoptado",
                      "n": len(claves), "a": int(v_ca.sum()), "b": int(v_ad.sum()),
                      "gana": g, "pierde": p_, "p": p})

        # y contra cada comparativo, con el punto re-ajustado
        print(f"\n  el re-ajuste {CANDIDATO} contra cada comparativo")
        for e in [c for c in unica.columns
                  if c not in ("escena", "clase", "objeto", "clave", "VIS", "IR", PROP)]:
            v_e = unica.set_index("clave")[e].reindex(claves).fillna(0).astype(int)
            g, p_, p = mcnemar(v_ca.values, v_e.values)
            veredicto = ("no se distingue" if p >= 0.05 else
                         ("gana el re-ajuste" if g > p_ else f"gana {e}"))
            print(f"    vs {e:18} {int(v_ca.sum()):>3} contra {int(v_e.sum()):>3} · "
                  f"gana {g:>2} pierde {p_:>2} · p = {p:.4g}  {veredicto}")
            filas.append({"particion": pref, "rol": etiqueta,
                          "comparacion": f"reajustado_vs_{e}", "n": len(claves),
                          "a": int(v_ca.sum()), "b": int(v_e.sum()),
                          "gana": g, "pierde": p_, "p": p})

    d = pd.DataFrame(filas)
    d.to_csv(SALIDA, index=False)
    print(f"\n  -> {SALIDA.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
