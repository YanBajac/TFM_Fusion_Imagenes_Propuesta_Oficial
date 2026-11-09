# -*- coding: utf-8 -*-
"""Bootstrap salvaje por grupos ESTUDENTIZADO y con la nula impuesta, para los contrastes de la deteccion.

POR QUE. diferencia() de analizar_v2.py multiplica por los pesos de Webb la suma por grupo de la funcion de
influencia y toma los cuantiles de esa suma, sin estudentizar. Con diez grupos ese intervalo equivale al de una
normal (la desviacion de las replicas es la del error estandar robusto), y no es el procedimiento de Cameron,
Gelbach y Miller (2008) ni el de Webb (2023): ellos imponen la hipotesis nula al generar las replicas y comparan
estadisticos t (WCR-t). Con grupos pocos y de tamano desigual, la diferencia importa.

El calculo de analizar_v2.py, que produjo los CSV oficiales, no se modifica. Igual que tasas_precisas_v2.py,
este script lo IMPORTA y corre su main() en una carpeta temporal, con round sin redondear y con diferencia()
envuelta; las etiquetas y las imagenes de datasets/m3fd2_VIS las lee del repositorio y son imprescindibles.
La envoltura devuelve lo mismo que la original y, ademas, calcula para cada contraste
  - el valor p del WCR-t a dos colas para la nula «diferencia = 0»;
  - el intervalo del 95 % que resulta de invertir ese mismo contraste: los valores d0 de la diferencia cuya nula
    «diferencia = d0» no se rechaza al 5 %.
Todas las nulas usan la misma matriz de pesos (B replicas, pesos de Webb, semilla fija), asi que el intervalo es
coherente con el valor p.

SALIDA en experiments/results/metrics_reports/: m3fd_v2_bootstrap_estudentizado.csv

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/detection_m3fd/bootstrap_estudentizado_v2.py
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

ALFA = 0.05
registro = []


def t_replicas(ajusteV, ajusteI, res, V, grupo, gs, W):
    """Estadistico de cada replica d* = ajuste + w_g * residuo: la diferencia equilibrada y su error estandar
    robusto por grupos, calculados como en analizar_v2.diferencia()."""
    K = len(gs)
    nV, nI = V.sum(), (~V).sum()
    nVg = np.array([(V & (grupo == g)).sum() for g in gs])
    nIg = np.array([(~V & (grupo == g)).sum() for g in gs])
    RV = np.array([res[V & (grupo == g)].sum() for g in gs])
    RI = np.array([res[~V & (grupo == g)].sum() for g in gs])
    wRV, wRI = W @ RV, W @ RI
    est = 0.5 * (ajusteV + wRV / nV) + 0.5 * (ajusteI + wRI / nI)
    # suma por grupo de la funcion de influencia de cada replica
    S = (0.5 / nV * (W * RV - np.outer(wRV / nV, nVg))
         + 0.5 / nI * (W * RI - np.outer(wRI / nI, nIg)))
    se = np.sqrt(K / (K - 1) * (S ** 2).sum(axis=1))
    return est, se


def wcr(d, dirs, grupo, W):
    """Valor p del WCR-t para «diferencia = 0» y el intervalo del 95 % que da invertirlo."""
    V = dirs == "V"
    gs = np.unique(grupo)
    nV, nI = V.sum(), (~V).sum()
    mV, mI = d[V].mean(), d[~V].mean()
    est, se, _ = estimar(d, V, grupo, gs)

    def valor_p(d0):
        # minimos cuadrados con la restriccion 0.5 a + 0.5 b = d0 (a y b, las medias de cada direccion)
        lam = 2 * (mV + mI - 2 * d0) / (1 / nV + 1 / nI)
        aR, bR = mV - lam / (2 * nV), mI - lam / (2 * nI)
        res = d - np.where(V, aR, bR)
        e, s = t_replicas(aR, bR, res, V, grupo, gs, W)
        return float(np.mean(np.abs((e - d0) / s) >= abs((est - d0) / se)))

    def limite(adentro, afuera):
        # biseccion entre un valor que no se rechaza y uno que si
        for _ in range(60):
            medio = 0.5 * (adentro + afuera)
            if valor_p(medio) >= ALFA:
                adentro = medio
            else:
                afuera = medio
        return 0.5 * (adentro + afuera)

    paso = 10 * se
    assert valor_p(est - paso) < ALFA and valor_p(est + paso) < ALFA, "el intervalo excede diez errores"
    return valor_p(0.0), limite(est, est - paso), limite(est, est + paso)


def estimar(d, V, grupo, gs):
    K = len(gs)
    nV, nI = V.sum(), (~V).sum()
    mV, mI = d[V].mean(), d[~V].mean()
    psi = np.where(V, 0.5 * (d - mV) / nV, 0.5 * (d - mI) / nI)
    s = np.array([psi[grupo == g].sum() for g in gs])
    return 0.5 * mV + 0.5 * mI, np.sqrt(K / (K - 1) * (s ** 2).sum()), s


def envolver(original):
    def diferencia(d, dirs, grupo):
        salida = original(d, dirs, grupo)
        d, dirs, grupo = np.asarray(d, float), np.asarray(dirs), np.asarray(grupo)
        K = len(np.unique(grupo))
        # la misma semilla y el mismo numero de replicas que el modulo
        W = np.random.default_rng(0).choice(a.WEBB, size=(a.B, K))
        p, lo, hi = wcr(d, dirs, grupo, W)
        registro.append({"diferencia": salida[0], "p_wcr": p, "wcr_lo": lo, "wcr_hi": hi, "grupos": K})
        return salida
    return diferencia


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
    reg = pd.DataFrame(registro)
    assert np.allclose(cont["diferencia"].values, reg["diferencia"].values, atol=1e-12), "orden distinto"
    # control: la parte que no cambia tiene que ser la de los contrastes precisos ya publicados
    precisos = pd.read_csv(MR / "m3fd_v2_contrastes_precisos.csv", dtype={"punto": str})
    for c in ("diferencia", "ic_lo", "ic_hi"):
        assert np.allclose(cont[c].values, precisos[c].values, atol=1e-12), f"cambio {c}"

    salida = pd.concat([cont[["punto", "contra", "diferencia", "ic_lo", "ic_hi"]],
                        reg[["p_wcr", "wcr_lo", "wcr_hi", "grupos"]]], axis=1)
    salida["replicas"] = a.B
    salida.to_csv(MR / "m3fd_v2_bootstrap_estudentizado.csv", index=False)
    for _, f in salida[salida["contra"].isin([a.CLASICO, a.PROMEDIO])].iterrows():
        print(f"  {f['punto']:>5} vs {f['contra']:<15} dif {100 * f['diferencia']:6.2f}  "
              f"t [{100 * f['ic_lo']:6.2f}, {100 * f['ic_hi']:6.2f}]  "
              f"WCR p = {f['p_wcr']:.4f}  [{100 * f['wcr_lo']:6.2f}, {100 * f['wcr_hi']:6.2f}]")
    print("  -> m3fd_v2_bootstrap_estudentizado.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
