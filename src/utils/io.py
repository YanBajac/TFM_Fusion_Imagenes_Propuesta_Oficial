"""io.py – Funciones para guardar imágenes y métricas en disco."""

from pathlib import Path
import cv2
import numpy as np
import pandas as pd


def save_image(img: np.ndarray, path: str | Path) -> None:
    """Guarda una imagen float [0,1] como PNG en la ruta indicada."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    img_uint8 = (np.clip(img, 0.0, 1.0) * 255).astype(np.uint8)
    cv2.imwrite(str(path), img_uint8)


def save_metrics_csv(records: list[dict], path: str | Path) -> None:
    """
    Guarda una lista de diccionarios de métricas como CSV.

    Parameters
    ----------
    records : list of dict
        Cada dict contiene al menos 'method', 'image' y las métricas.
    path : str | Path
        Ruta de salida del archivo CSV.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(records)
    df.to_csv(path, index=False, float_format="%.6f")
    print(f"Métricas guardadas en: {path}")
