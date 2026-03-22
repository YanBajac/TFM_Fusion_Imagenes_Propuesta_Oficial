"""
datasets.py
-----------
Funciones para cargar y gestionar pares de imágenes visibles (VIS) e infrarrojas (IR).
"""

import os
from pathlib import Path
import cv2
import numpy as np


RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"


def load_image(path: str | Path, grayscale: bool = True) -> np.ndarray:
    """Carga una imagen desde disco."""
    flag = cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR
    img = cv2.imread(str(path), flag)
    if img is None:
        raise FileNotFoundError(f"No se pudo cargar la imagen: {path}")
    return img.astype(np.float32) / 255.0


def load_pair(vis_path: str | Path, ir_path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """Carga un par VIS/IR y retorna ambas imágenes normalizadas."""
    vis = load_image(vis_path)
    ir = load_image(ir_path)
    return vis, ir


def list_pairs(vis_dir: str | Path = None, ir_dir: str | Path = None) -> list[tuple[Path, Path]]:
    """
    Retorna una lista de tuplas (vis_path, ir_path) buscando imágenes
    con el mismo nombre en los subdirectorios VIS e IR dentro de raw/.
    """
    vis_dir = Path(vis_dir) if vis_dir else RAW_DIR / "VIS"
    ir_dir = Path(ir_dir) if ir_dir else RAW_DIR / "IR"

    extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
    vis_files = {f.stem: f for f in vis_dir.iterdir() if f.suffix.lower() in extensions}
    ir_files = {f.stem: f for f in ir_dir.iterdir() if f.suffix.lower() in extensions}

    common = sorted(vis_files.keys() & ir_files.keys())
    return [(vis_files[k], ir_files[k]) for k in common]
