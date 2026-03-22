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
    TopHatFusion,
    average_fusion,
    laplacian_pyramid_fusion,
    curvelet_fusion,
)
from src.metrics import evaluate_all
from src.utils import save_image, save_metrics_csv

# ---------------------------------------------------------------------------
# Configuración de métodos a comparar
# ---------------------------------------------------------------------------
METHODS = {
    # Baselines
    "Promedio":         lambda v, i: average_fusion(v, i),
    "PiramideLaplace":  lambda v, i: laplacian_pyramid_fusion(v, i, levels=4),
    "Curvelet":         lambda v, i: curvelet_fusion(v, i, levels=3),
    # Método propuesto – distintas configuraciones
    "TopHat_disk_L3":   lambda v, i: TopHatFusion("disk",   levels=3).fuse(v, i),
    "TopHat_square_L3": lambda v, i: TopHatFusion("square", levels=3).fuse(v, i),
    "TopHat_cross_L3":  lambda v, i: TopHatFusion("cross",  levels=3).fuse(v, i),
    "TopHat_disk_L5":   lambda v, i: TopHatFusion("disk",   levels=5).fuse(v, i),
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

    print(f"Procesando {len(pairs)} pares con {len(METHODS)} métodos...\n")
    records = []

    for vis_path, ir_path in pairs:
        vis, ir = load_pair(vis_path, ir_path)
        image_name = vis_path.stem

        for method_name, fuse_fn in METHODS.items():
            try:
                fused = fuse_fn(vis, ir)
            except Exception as exc:
                print(f"  [SKIP] {method_name} / {image_name}: {exc}")
                continue

            # Guardar imagen fusionada
            out_img = FUSED_DIR / method_name / f"{image_name}.png"
            save_image(fused, out_img)

            # Calcular métricas
            metrics = evaluate_all(fused, vis, ir)
            records.append({"method": method_name, "image": image_name, **metrics})

            print(f"  OK  {method_name:25s} | {image_name}  EN={metrics['EN']:.4f}")

    # Guardar métricas consolidadas
    save_metrics_csv(records, METRICS_CSV)
    print(f"\nDone. {len(records)} registros guardados en {METRICS_CSV}")


if __name__ == "__main__":
    main()
