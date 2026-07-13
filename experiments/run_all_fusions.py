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
from src.fusion.optimal_top_hat import OptimalTopHatFusion, OptimalMultiscaleFusion, fuse_optimal
from src.fusion.novel_fusion import fuse_novel
from src.metrics import evaluate_all
from src.utils import save_image, save_metrics_csv

# ---------------------------------------------------------------------------
# Configuración de métodos a comparar
# ---------------------------------------------------------------------------
METHODS = {
    # Baselines
    "Promedio":             lambda v, i: average_fusion(v, i),
    "PiramideLaplace":      lambda v, i: laplacian_pyramid_fusion(v, i, levels=4),
    "Curvelet":             lambda v, i: curvelet_fusion(v, i, levels=3),
    # Metodo propuesto - White Top-Hat (WTH)
    "TopHat_disk_L3":       lambda v, i: TopHatFusion("disk",   levels=3).fuse(v, i),
    "TopHat_square_L3":     lambda v, i: TopHatFusion("square", levels=3).fuse(v, i),
    "TopHat_cross_L3":      lambda v, i: TopHatFusion("cross",  levels=3).fuse(v, i),
    "TopHat_disk_L5":       lambda v, i: TopHatFusion("disk",   levels=5).fuse(v, i),
    # Metodo propuesto - variante con Black Top-Hat (WTH+BTH)
    "TopHat_disk_L3_BTH":   lambda v, i: TopHatFusion("disk",   levels=3, use_black_top_hat=True).fuse(v, i),
    "TopHat_square_L3_BTH": lambda v, i: TopHatFusion("square", levels=3, use_black_top_hat=True).fuse(v, i),
    "TopHat_cross_L3_BTH":  lambda v, i: TopHatFusion("cross",  levels=3, use_black_top_hat=True).fuse(v, i),
    "TopHat_disk_L5_BTH":   lambda v, i: TopHatFusion("disk",   levels=5, use_black_top_hat=True).fuse(v, i),
    # Exploraciones PSO (descartadas)
    "TopHat_Optimo":        lambda v, i: OptimalTopHatFusion(r=1, m=0.3, mode="sum").fuse(v, i),
    "Optimo_Multiescala":   lambda v, i: OptimalMultiscaleFusion(n=6, base_radius=2.89, m=0.10).fuse(v, i),
    "Multiescala_n8":       lambda v, i: fuse_novel(v, i, n=8, m=0.12),
    # PROPUESTA CENTRAL: Top-Hat de una sola escala (disco + 4 lineales por maximo), PSO
    "Propuesta_Novedosa":   lambda v, i: fuse_optimal(v, i, r=12, m=0.1274, mode="max"),
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
