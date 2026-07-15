"""
run_all_fusions.py
------------------
Ejecuta TODOS los métodos de fusión sobre el dataset completo y guarda:
  - Imágenes fusionadas en: experiments/results/fused_images/<método>/
  - Métricas consolidadas en: experiments/results/metrics_reports/all_metrics.csv
"""

import sys
from pathlib import Path

# Asegura que la raíz del proyecto esté en el PYTHONPATH
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.datasets import list_pairs, load_pair
from src.fusion import (
    fuse_optimal,
    laplacian_pyramid_fusion,
    ratio_pyramid_fusion,
    dwt_fusion,
    dtcwt_fusion,
    curvelet_fusion,
    tophat_classic_fusion,
)
from src.metrics import evaluate_all
from src.utils import save_image, save_metrics_csv

# ---------------------------------------------------------------------------
# Configuración de métodos a comparar (benchmark de la tesis)
# ---------------------------------------------------------------------------
# Hiperparámetros de la propuesta hallados por PSO (operador con SUMA de ramas)
PROP_R, PROP_M = 25, 0.0703  # optimo del barrido PSO 5x5 (Cuadro 1 FPUNA): F=1.9843, n=10, T>=30

METHODS = {
    # Estado del arte
    "PiramideLaplace":  lambda v, i: laplacian_pyramid_fusion(v, i, levels=4),
    "RatioPiramide":    lambda v, i: ratio_pyramid_fusion(v, i, levels=4),
    "DWT":              lambda v, i: dwt_fusion(v, i, levels=3),
    "DTCWT":            lambda v, i: dtcwt_fusion(v, i, levels=4),
    "Curvelet":         lambda v, i: curvelet_fusion(v, i, levels=3),
    # Metodologia clasica de la transformada Top-Hat (basico)
    "TopHat_Clasico":   lambda v, i: tophat_classic_fusion(v, i, r=5),
    # PROPUESTA CENTRAL: Top-Hat una escala, disco + 4 lineales por SUMA, PSO
    "Propuesta_Novedosa": lambda v, i: fuse_optimal(v, i, r=PROP_R, m=PROP_M, mode="sum"),
}

RESULTS_DIR   = ROOT / "experiments" / "results"
FUSED_DIR     = RESULTS_DIR / "fused_images"
METRICS_DIR   = RESULTS_DIR / "metrics_reports"
METRICS_CSV   = METRICS_DIR / "all_metrics.csv"


def main():
    pairs = list_pairs()
    if not pairs:
        print("No se encontraron pares VIS/IR en data/raw/VIS y data/raw/IR.")
        return

    # Checkpoint: cargar registros previos y saltar (metodo, imagen) ya hechos.
    records = []
    done = set()
    if METRICS_CSV.exists() and METRICS_CSV.stat().st_size > 0:
        import pandas as pd
        try:
            prev = pd.read_csv(METRICS_CSV)
        except Exception:
            prev = None
        # Solo reanudar si el CSV tiene el esquema nuevo (incluye Qabf).
        if prev is not None and "Qabf" in prev.columns:
            records = prev.to_dict("records")
            done = {(r["method"], r["image"]) for r in records}
            print(f"Reanudando: {len(done)} registros previos encontrados.")

    print(f"Procesando {len(pairs)} pares con {len(METHODS)} metodos...\n")

    for vis_path, ir_path in pairs:
        vis, ir = load_pair(vis_path, ir_path)
        image_name = vis_path.stem

        for method_name, fuse_fn in METHODS.items():
            if (method_name, image_name) in done:
                continue
            try:
                fused = fuse_fn(vis, ir)
            except Exception as exc:
                print(f"  [SKIP] {method_name} / {image_name}: {exc}")
                continue

            out_img = FUSED_DIR / method_name / f"{image_name}.png"
            save_image(fused, out_img)

            metrics = evaluate_all(fused, vis, ir)
            records.append({"method": method_name, "image": image_name, **metrics})
            done.add((method_name, image_name))

            print(f"  OK  {method_name:25s} | {image_name}  EN={metrics['EN']:.4f}")

        # Guardar tras cada par (checkpoint).
        save_metrics_csv(records, METRICS_CSV)

    print(f"\nDone. {len(records)} registros guardados en {METRICS_CSV}")


if __name__ == "__main__":
    main()
