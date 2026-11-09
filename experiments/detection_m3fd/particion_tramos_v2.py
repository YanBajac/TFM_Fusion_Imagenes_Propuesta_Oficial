# -*- coding: utf-8 -*-
"""Particion de M3FD por tramos de video, para la deteccion de objetos.

POR QUE POR TRAMOS. Las imagenes de M3FD son cuadros de secuencias de video y los cuadros con numero
consecutivo se parecen mucho entre si. Si se reparten imagen por imagen, un cuadro de prueba tiene casi
siempre un vecino casi identico en el entrenamiento, y el detector se evalua sobre algo que ya vio.

LA REGLA, fijada antes de entrenar (Seccion 3.5.1 del libro):
  1. Los cuadros se agrupan en bloques de 100 numeros consecutivos. Un bloque tambien se corta donde
     cambia el tamano de la imagen.
  2. Los bloques, enteros, se reparten al azar con semilla fija entre prueba (25 %), validacion (10 %) y
     entrenamiento (el resto). Se prueban semillas en orden desde 0 y se toma la primera cuyo reparto deja
     en prueba entre el 20 % y el 35 % de las personas y de las luces.
  3. Entre bloques vecinos asignados a partes distintas se descartan diez cuadros de cada lado.
  4. Del entrenamiento se toman 2000 cuadros al azar con semilla 0; los que sobran quedan como
     'sobrante' (cuadros de seguimiento) y no se usan para entrenar.
  5. Filtro de casi duplicados, global: cada cuadro de prueba se compara con los 2000 de entrenamiento y
     se lo descarta si alguno se le parece tanto como dos cuadros consecutivos de una misma secuencia, es
     decir, con un SSIM mayor o igual que la mediana del SSIM entre cuadros consecutivos. Para que sea
     rapido, primero se preseleccionan los 10 mas parecidos por correlacion de miniaturas de 32 x 24, y
     despues se mide el SSIM exacto en 128 x 96. Asi se descartan tambien las escenas repetidas lejos
     en la numeracion.
     (Comparar el maximo de 2000 correlaciones contra el percentil 95 de un solo par al azar no sirve
     como umbral: ese maximo casi siempre lo supera y descartaria el 81 % de la prueba.)
  6. Control de fuga, despues del filtro: para cada cuadro de prueba se mide el SSIM con el cuadro de
     entrenamiento mas parecido entre sus 30 vecinos de numeracion a cada lado.

POR QUE BLOQUES Y NO CORTES POR SIMILITUD. Cortar donde dos cuadros consecutivos se parecen menos que el
percentil 95 de los pares al azar fragmenta el conjunto en 1046 tramos, con una mediana de un cuadro por
tramo, y deja cuadros de prueba con un vecino casi identico en el entrenamiento (SSIM 0,958).

SALIDAS en experiments/results/metrics_reports/:
  m3fd_v2_particion.csv   un cuadro por fila: id, tramo, parte (train, sobrante, val, test, descartado,
                          descartado_fuga)
  m3fd_v2_fuga.csv        para cada cuadro de prueba, la similitud con el cuadro de entrenamiento mas
                          parecido entre sus 30 vecinos de numeracion a cada lado, que es el control de fuga

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/detection_m3fd/particion_tramos_v2.py
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from skimage.metrics import structural_similarity as ssim

ROOT = Path(__file__).resolve().parents[2]
M3FD = ROOT / "data" / "M3FD_Detection"
MR = ROOT / "experiments" / "results" / "metrics_reports"
TAM = (128, 96)
BLOQUE = 100
MARGEN = 10
VENTANA_FUGA = 30
N_TRAIN = 2000
FRAC = {"test": 0.25, "val": 0.10}
RANGO_PRUEBA = (0.20, 0.35)


def miniatura(i):
    im = cv2.imread(str(M3FD / "Vis" / f"{i:05d}.png"), cv2.IMREAD_GRAYSCALE)
    return im.shape, cv2.resize(im, TAM, interpolation=cv2.INTER_AREA)


def clases(i):
    r = ET.parse(M3FD / "Annotation" / f"{i:05d}.xml").getroot()
    return [o.findtext("name") for o in r.findall("object")]


def main():
    ids = sorted(int(p.stem) for p in (M3FD / "Vis").glob("*.png"))
    print(f"  {len(ids)} cuadros")
    formas, mini = {}, {}
    for i in ids:
        formas[i], mini[i] = miniatura(i)

    consec = np.array([ssim(mini[a], mini[b], data_range=255) if formas[a] == formas[b] else -1.0
                       for a, b in zip(ids[:-1], ids[1:])])
    rng = np.random.default_rng(0)
    pares = rng.choice(ids, size=(2000, 2))
    azar = np.array([ssim(mini[a], mini[b], data_range=255) for a, b in pares
                     if a != b and formas[a] == formas[b]])
    umbral = float(np.percentile(azar, 95))
    print(f"  SSIM consecutivos: mediana {np.median(consec[consec >= 0]):.3f}")
    print(f"  SSIM al azar: mediana {np.median(azar):.3f}, percentil 95 = {umbral:.3f} (umbral de corte)")

    tramo, t, en_bloque = {ids[0]: 0}, 0, 1
    for a, b in zip(ids[:-1], ids[1:]):
        if en_bloque >= BLOQUE or b != a + 1 or formas[a] != formas[b]:
            t += 1
            en_bloque = 0
        tramo[b] = t
        en_bloque += 1
    n_tramos = t + 1
    print(f"  {n_tramos} tramos; mediana {np.median(np.bincount(list(tramo.values()))):.0f} cuadros por tramo")

    cls = {i: clases(i) for i in ids}
    tot_p = sum(c.count("People") for c in cls.values())
    tot_l = sum(c.count("Lamp") for c in cls.values())
    por_tramo = pd.DataFrame({"id": ids, "tramo": [tramo[i] for i in ids],
                              "personas": [cls[i].count("People") for i in ids],
                              "luces": [cls[i].count("Lamp") for i in ids]})
    agg = por_tramo.groupby("tramo").agg(n=("id", "size"), personas=("personas", "sum"),
                                         luces=("luces", "sum"))

    elegido = None
    for semilla in range(200):
        orden = np.random.default_rng(semilla).permutation(agg.index.values)
        parte, acum = {}, {"test": 0, "val": 0}
        for tr in orden:
            n = agg.loc[tr, "n"]
            if acum["test"] < FRAC["test"] * len(ids):
                parte[tr] = "test"; acum["test"] += n
            elif acum["val"] < FRAC["val"] * len(ids):
                parte[tr] = "val"; acum["val"] += n
            else:
                parte[tr] = "train"
        tp = agg[[parte[x] == "test" for x in agg.index]]
        fp, fl = tp.personas.sum() / tot_p, tp.luces.sum() / tot_l
        if RANGO_PRUEBA[0] <= fp <= RANGO_PRUEBA[1] and RANGO_PRUEBA[0] <= fl <= RANGO_PRUEBA[1]:
            elegido = (semilla, parte, fp, fl)
            break
    if elegido is None:
        print("  ABORTA: ninguna semilla deja la prueba dentro del rango pedido")
        return 1
    semilla, parte, fp, fl = elegido
    print(f"  semilla del reparto: {semilla}; en prueba quedan el {100*fp:.1f} % de las personas "
          f"y el {100*fl:.1f} % de las luces")

    df = por_tramo.copy()
    df["parte"] = df.tramo.map(parte)
    # margen entre tramos vecinos asignados a partes distintas
    borde = set()
    for k in range(len(ids) - 1):
        a, b = ids[k], ids[k + 1]
        if tramo[a] != tramo[b] and parte[tramo[a]] != parte[tramo[b]]:
            for j in range(max(0, k - MARGEN + 1), min(len(ids), k + 1 + MARGEN)):
                borde.add(ids[j])
    df.loc[df.id.isin(borde), "parte"] = "descartado"
    tr_ids = df[df.parte == "train"].id.values
    if len(tr_ids) > N_TRAIN:
        keep = set(np.random.default_rng(0).choice(tr_ids, size=N_TRAIN, replace=False))
        df.loc[(df.parte == "train") & ~df.id.isin(keep), "parte"] = "sobrante"
    # filtro de fuga global: correlacion de miniaturas normalizadas contra todo el entrenamiento
    def vector(i):
        v = cv2.resize(mini[i], (32, 24), interpolation=cv2.INTER_AREA).astype(np.float64).ravel()
        return (v - v.mean()) / (v.std() + 1e-9)
    tr = df[df.parte == "train"].id.values
    te = df[df.parte == "test"].id.values
    V_tr = np.stack([vector(i) for i in tr])
    V_te = np.stack([vector(i) for i in te])
    corr = V_te @ V_tr.T / V_tr.shape[1]
    umbral_dup = float(np.median(consec[consec >= 0]))
    cand = np.argsort(-corr, axis=1)[:, :10]
    ssim_dup = np.array([max((ssim(mini[i], mini[tr[j]], data_range=255)
                              for j in cand[k] if formas[tr[j]] == formas[i]), default=0.0)
                         for k, i in enumerate(te)])
    fuga_global = te[ssim_dup >= umbral_dup]
    df.loc[df.id.isin(fuga_global), "parte"] = "descartado_fuga"
    print(f"  filtro de casi duplicados: SSIM >= {umbral_dup:.3f} (mediana entre consecutivos); "
          f"se descartan {len(fuga_global)} de {len(te)} cuadros de prueba")
    df.to_csv(MR / "m3fd_v2_particion.csv", index=False)

    # control de fuga: similitud con el cuadro de entrenamiento mas parecido entre los vecinos cercanos
    en_train = set(df[df.parte == "train"].id)
    filas = []
    for i in df[df.parte == "test"].id:
        vec = [j for j in range(i - VENTANA_FUGA, i + VENTANA_FUGA + 1)
               if j != i and j in en_train and formas[j] == formas[i]]
        s = max((ssim(mini[i], mini[j], data_range=255) for j in vec), default=np.nan)
        filas.append({"id": i, "ssim_max_vecino_train": s})
    fuga = pd.DataFrame(filas)
    fuga.to_csv(MR / "m3fd_v2_fuga.csv", index=False)

    print("\n  === Reparto ===")
    res = df.groupby("parte").agg(cuadros=("id", "size"), personas=("personas", "sum"),
                                  luces=("luces", "sum"))
    print(res.to_string())
    con = fuga.ssim_max_vecino_train.dropna()
    print(f"\n  Control de fuga: {len(con)} de {len(fuga)} cuadros de prueba tienen algun vecino de "
          f"entrenamiento a menos de {VENTANA_FUGA} numeros")
    if len(con):
        print(f"  SSIM con el vecino mas parecido: mediana {con.median():.3f}, maximo {con.max():.3f}; "
              f"{(con >= umbral).sum()} por encima del umbral de corte")
    print(f"\n  -> m3fd_v2_particion.csv y m3fd_v2_fuga.csv en {MR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
