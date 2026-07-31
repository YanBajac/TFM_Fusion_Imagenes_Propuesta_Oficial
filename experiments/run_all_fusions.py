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
# Hiperparametros de la propuesta (operador con SUMA de ramas).
# El PESO lo fija el PSO con la aptitud F_o sobre el rango publicado m in [0,30; 2,00]
# (Ortega y Espinoza, 2025): el optimo converge al piso del rango, m* = 0,30, en las 25
# configuraciones del Cuadro 1, porque F_o decrece de forma estrictamente monotona en m.
#
# El RADIO no lo fija el PSO: dentro de ese rango F_o prefiere r = 1 (1,7354 frente a
# 1,7039 en r = 25). r = 25 es una DECISION DE DISENO tomada sobre las metricas de
# evaluacion, de las cuales cinco lo favorecen (EN, SD, FE, MG, SF) y cuatro favorecen
# r = 1 (SSIM, PSNR, MI_vis, MI_ir). Se adopta priorizando la capacidad de realce; la
# limitacion (elegir el radio con parte del criterio con que luego se evalua) esta
# declarada en el libro. Nota: r = 1 no desactiva el banco de cinco SE -el disco es la
# cruz 3x3 y las cuatro lineas son cuatro mascaras 3x3 distintas-.
PROP_R, PROP_M = 25, 0.30

# Parametros de cada metodo, declarados de forma EXPLICITA y en un solo lugar. De aqui se
# derivan tanto las funciones de fusion como la huella de configuracion que usa el checkpoint,
# de modo que no puedan quedar desalineados.
CONFIG = {
    # Estado del arte
    "PiramideLaplace":  {"levels": 4},
    "RatioPiramide":    {"levels": 4},
    "DWT":              {"levels": 3},
    "DTCWT":            {"levels": 4},
    # Nota: "Curvelet" es una APROXIMACION por wavelet 2D con base db4, no la transformada
    # curvelet de Candes et al. Comparte algoritmo con DWT y solo cambia la base.
    "Curvelet":         {"levels": 3, "wavelet": "db4"},
    # Metodologia clasica de la transformada Top-Hat (basico)
    "TopHat_Clasico":   {"r": 5},
    # PROPUESTA CENTRAL: Top-Hat una escala, disco + 4 lineales por SUMA
    "Propuesta_Novedosa": {"r": PROP_R, "m": PROP_M, "mode": "sum"},
}

METHODS = {
    "PiramideLaplace":  lambda v, i: laplacian_pyramid_fusion(v, i, **CONFIG["PiramideLaplace"]),
    "RatioPiramide":    lambda v, i: ratio_pyramid_fusion(v, i, **CONFIG["RatioPiramide"]),
    "DWT":              lambda v, i: dwt_fusion(v, i, **CONFIG["DWT"]),
    "DTCWT":            lambda v, i: dtcwt_fusion(v, i, **CONFIG["DTCWT"]),
    "Curvelet":         lambda v, i: curvelet_fusion(v, i, **CONFIG["Curvelet"]),
    "TopHat_Clasico":   lambda v, i: tophat_classic_fusion(v, i, **CONFIG["TopHat_Clasico"]),
    "Propuesta_Novedosa": lambda v, i: fuse_optimal(v, i, **CONFIG["Propuesta_Novedosa"]),
}


def huella_config():
    """Huella de la configuracion de los metodos, para invalidar el checkpoint."""
    import hashlib
    import json
    crudo = json.dumps(CONFIG, sort_keys=True, default=str)
    return hashlib.sha256(crudo.encode("utf-8")).hexdigest()[:16]

RESULTS_DIR   = ROOT / "experiments" / "results"
FUSED_DIR     = RESULTS_DIR / "fused_images"
METRICS_DIR   = RESULTS_DIR / "metrics_reports"
METRICS_CSV   = METRICS_DIR / "all_metrics.csv"


def main():
    import argparse
    import json
    ap = argparse.ArgumentParser()
    ap.add_argument("--rehacer", action="store_true",
                    help="ignora el checkpoint y recalcula todo desde cero")
    args = ap.parse_args()

    pairs = list_pairs()
    if not pairs:
        print("No se encontraron pares VIS/IR en data/raw/VIS y data/raw/IR.")
        return

    hc = huella_config()
    SIDECAR = METRICS_CSV.with_suffix(".config.json")
    print(f"huella de configuracion: {hc}")

    # Checkpoint: cargar registros previos y saltar (metodo, imagen) ya hechos.
    #
    # El checkpoint indexaba SOLO por (metodo, imagen), de modo que al cambiar un
    # hiperparametro del operador -por ejemplo el peso m- las filas viejas se daban por
    # hechas y el CSV conservaba las metricas de la configuracion anterior sin ningun aviso.
    # Ahora se guarda junto al CSV la huella de CONFIG y solo se reanuda si coincide.
    records = []
    done = set()
    if args.rehacer:
        print("--rehacer: se ignora el checkpoint y se recalcula todo.")
    elif METRICS_CSV.exists() and METRICS_CSV.stat().st_size > 0:
        import pandas as pd
        try:
            prev = pd.read_csv(METRICS_CSV)
        except Exception:
            prev = None
        hc_prev = None
        if SIDECAR.exists():
            try:
                hc_prev = json.loads(SIDECAR.read_text(encoding="utf-8")).get("huella")
            except Exception:
                hc_prev = None
        # Solo reanudar si el CSV tiene el esquema nuevo (incluye Qabf) Y la configuracion
        # de los metodos es la misma con la que se produjo.
        if prev is not None and "Qabf" in prev.columns and hc_prev == hc:
            records = prev.to_dict("records")
            done = {(r["method"], r["image"]) for r in records}
            print(f"Reanudando: {len(done)} registros previos con la misma configuracion.")
        elif prev is not None and hc_prev != hc:
            print(f"AVISO: la configuracion cambio (huella previa {hc_prev}, actual {hc}).")
            print("       El checkpoint se descarta y se recalcula todo desde cero.")

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

        # Guardar tras cada par (checkpoint), junto con la huella de la configuracion.
        save_metrics_csv(records, METRICS_CSV)
        SIDECAR.write_text(json.dumps({"huella": hc, "config": CONFIG}, indent=2,
                                      sort_keys=True, default=str), encoding="utf-8")

    print(f"\nDone. {len(records)} registros guardados en {METRICS_CSV}")
    print(f"Configuracion registrada en {SIDECAR.name}")


if __name__ == "__main__":
    main()
