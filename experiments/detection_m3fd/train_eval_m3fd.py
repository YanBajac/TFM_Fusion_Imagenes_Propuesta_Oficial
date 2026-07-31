# -*- coding: utf-8 -*-
"""
train_eval_m3fd.py — Entrena UN unico YOLO sobre el dataset mixto VIS+IR de M3FD
y lo evalua por INFERENCIA sobre la validacion de cada modalidad/metodo de fusion.

La logica del experimento (idea del director): las clases son complementarias
(People domina en IR, Lamp en VIS); un modelo entrenado con ambas modalidades
deberia detectar AMBAS clases a la vez solo cuando la entrada es la imagen
fusionada. Se reporta mAP global y AP@0.5 por clase.

Uso:
  python experiments\detection_m3fd\train_eval_m3fd.py --datasets-dir datasets `
      --model yolov8n.pt --epochs 40 --imgsz 640 --device 0
"""
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments" / "results" / "metrics_reports" / "detection_m3fd_map.csv"

METODOS = ["VIS", "IR", "PiramideLaplace", "RatioPiramide", "DWT", "DTCWT",
           "Curvelet", "TopHat_Clasico", "Propuesta_Novedosa"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets-dir", default="datasets")
    ap.add_argument("--methods", default=",".join(METODOS))
    ap.add_argument("--model", default="yolov8n.pt")
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--device", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--skip-train", action="store_true",
                    help="usa runs/m3fd/mixto/weights/best.pt ya entrenado")
    ap.add_argument("--pesos", choices=["best", "last"], default="best",
                    help="checkpoint a evaluar: best.pt (elegido en el val) o last.pt")
    a = ap.parse_args()
    from ultralytics import YOLO
    import pandas as pd

    dd = Path(a.datasets_dir)

    def hallar_pesos(cual="best"):
        """Localiza best.pt o last.pt del mixto (ultralytics puede anidar runs/)."""
        cands = sorted(ROOT.glob(f"runs/**/mixto/weights/{cual}.pt"),
                       key=lambda p: p.stat().st_mtime)
        return cands[-1] if cands else None

    def informe_convergencia(pesos):
        """Verifica que el val haya mejorado con las epocas y a que epoca corresponde
        el checkpoint elegido. Si el maximo del val esta en la epoca 1, la seleccion
        no esta midiendo aprendizaje y el experimento no es interpretable."""
        res = pesos.parent.parent / "results.csv"
        if not res.exists():
            print("[AVISO] no encuentro results.csv; no puedo verificar convergencia")
            return
        h = pd.read_csv(res)
        h.columns = [c.strip() for c in h.columns]
        col = next((c for c in h.columns if "mAP50(B)" in c and "95" not in c), None)
        if col is None:
            print("[AVISO] results.csv sin columna de mAP50; salto la verificacion")
            return
        mejor_ep = int(h.loc[h[col].idxmax(), "epoch"])
        print(f"\n--- convergencia del val ({len(h)} epocas) ---")
        print(f"  mAP50 del val: epoca 1 = {h[col].iloc[0]:.5f} | "
              f"ultima = {h[col].iloc[-1]:.5f} | maximo = {h[col].max():.5f} (epoca {mejor_ep})")
        if mejor_ep <= 1:
            print("  ATENCION: el maximo del val esta en la primera epoca. El modelo no mejora\n"
                  "  sobre el val, de modo que la seleccion de checkpoint no mide aprendizaje.\n"
                  "  Revisar el split antes de reportar estas cifras.")
        else:
            print(f"  OK: el val mejora durante el entrenamiento (maximo en la epoca {mejor_ep}"
                  f" de {len(h)}).")

    best = hallar_pesos(a.pesos)

    # ---------- 1. entrenamiento unico sobre el mixto VIS+IR ----------
    if a.skip_train and best is not None:
        print("Salteo entrenamiento; uso", best)
    else:
        data = dd / "m3fd_mixto" / "data.yaml"
        if not data.exists():
            print("ERROR: falta", data, "- corre antes prepare_m3fd.py"); sys.exit(2)
        print("===== Entrenando modelo unico (VIS+IR mezcladas) =====")
        model = YOLO(a.model)
        kw = dict(data=str(data), epochs=a.epochs, imgsz=a.imgsz, batch=a.batch,
                  seed=a.seed, deterministic=True, project="runs/m3fd", name="mixto",
                  exist_ok=True, verbose=False)
        if a.device != "":
            kw["device"] = a.device
        model.train(**kw)
        best = hallar_pesos(a.pesos)

    # ---------- 2. inferencia sobre cada set de prueba ----------
    assert best is not None, f"no se encontró {a.pesos}.pt bajo runs/**/mixto/weights/"
    print(f"Pesos ({a.pesos}):", best)
    informe_convergencia(best)
    modelo = YOLO(str(best))
    nombres = modelo.names          # {idx: nombre}
    filas = []
    for m in [x.strip() for x in a.methods.split(",") if x.strip()]:
        data = dd / f"m3fd_test_{m}" / "data.yaml"
        if not data.exists():
            print(f"[AVISO] falta {data}; salto {m}"); continue
        print(f"----- Evaluando {m} -----")
        kw = dict(data=str(data), split="val", verbose=False)
        if a.device != "":
            kw["device"] = a.device
        met = modelo.val(**kw)
        fila = {"method": m,
                "mAP50": round(float(met.box.map50), 4),
                "mAP50_95": round(float(met.box.map), 4),
                "precision": round(float(met.box.mp), 4),
                "recall": round(float(met.box.mr), 4)}
        # AP@0.5 por clase (indices de clases presentes en la validacion)
        for k, idx in enumerate(met.box.ap_class_index):
            fila[f"AP50_{nombres[int(idx)]}"] = round(float(met.box.ap50[k]), 4)
        filas.append(fila)
        print(f"  {m}: mAP50={fila['mAP50']} | " +
              " ".join(f"{c}={v}" for c, v in fila.items() if c.startswith("AP50_")))

    df = pd.DataFrame(filas)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # FUSION en lugar de sobrescritura: si se corre con --methods para reevaluar solo
    # algunos metodos, la version anterior borraba las filas de todos los demas.
    # Las filas nuevas reemplazan a las viejas del mismo metodo; el resto se conserva.
    if OUT.exists():
        previo = pd.read_csv(OUT)
        nuevos = set(df["method"])
        conserva = previo[~previo["method"].isin(nuevos)]
        if len(conserva):
            print(f"\nConservo {len(conserva)} fila(s) previa(s) de metodos no reevaluados: "
                  + ", ".join(conserva["method"]))
        df = pd.concat([conserva, df], ignore_index=True)
    orden = {m: k for k, m in enumerate(METODOS)}
    df = df.sort_values("method", key=lambda s: s.map(lambda x: orden.get(x, 99))).reset_index(drop=True)
    df.to_csv(OUT, index=False)
    print("\n===== M3FD: mAP por metodo (modelo unico VIS+IR) =====")
    print(df.to_string(index=False))
    print("\nGuardado:", OUT)


if __name__ == "__main__":
    main()
