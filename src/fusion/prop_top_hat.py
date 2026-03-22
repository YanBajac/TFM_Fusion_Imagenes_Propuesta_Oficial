"""
prop_top_hat.py
---------------
Algoritmo de fusión propuesto basado en la Torre Top-Hat (Top-Hat Tower Fusion).
Soporta múltiples geometrías de elemento estructurante y múltiples niveles de descomposición.

Referencia: Tesis de Maestría en Ciencias de Datos – [Tu nombre]
"""

import cv2
import numpy as np
from itertools import product


# ---------------------------------------------------------------------------
# Elementos estructurantes disponibles
# ---------------------------------------------------------------------------
STRUCTURING_ELEMENTS = {
    "disk":    lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)),
    "square":  lambda r: cv2.getStructuringElement(cv2.MORPH_RECT,    (2 * r + 1, 2 * r + 1)),
    "cross":   lambda r: cv2.getStructuringElement(cv2.MORPH_CROSS,   (2 * r + 1, 2 * r + 1)),
}


def white_top_hat(image: np.ndarray, se: np.ndarray) -> np.ndarray:
    """WTH = imagen - apertura morfológica."""
    opened = cv2.morphologyEx(image, cv2.MORPH_OPEN, se)
    return image - opened


def black_top_hat(image: np.ndarray, se: np.ndarray) -> np.ndarray:
    """BTH = cierre morfológico - imagen."""
    closed = cv2.morphologyEx(image, cv2.MORPH_CLOSE, se)
    return closed - image


def top_hat_decomposition(
    image: np.ndarray,
    se_type: str = "disk",
    levels: int = 3,
    base_radius: int = 3,
) -> list[np.ndarray]:
    """
    Descompone la imagen en capas Top-Hat de distintos radios.

    Returns
    -------
    layers : list of np.ndarray
        [wth_1, wth_2, ..., wth_n, residual]
    """
    builder = STRUCTURING_ELEMENTS[se_type]
    layers = []
    residual = image.copy()

    for lvl in range(1, levels + 1):
        radius = base_radius * lvl
        se = builder(radius)
        wth = white_top_hat(residual, se)
        layers.append(wth)
        residual = residual - wth

    layers.append(residual)  # capa base (residual)
    return layers


class TopHatFusion:
    """
    Fusión de imágenes VIS + IR mediante Torre Top-Hat.

    Parameters
    ----------
    se_type : str
        Tipo de elemento estructurante: 'disk', 'square' o 'cross'.
    levels : int
        Número de niveles de descomposición.
    base_radius : int
        Radio inicial del elemento estructurante.
    activity_measure : str
        Medida de actividad para selección de capas: 'max' o 'mean'.
    """

    def __init__(
        self,
        se_type: str = "disk",
        levels: int = 3,
        base_radius: int = 3,
        activity_measure: str = "max",
    ):
        if se_type not in STRUCTURING_ELEMENTS:
            raise ValueError(f"se_type debe ser uno de {list(STRUCTURING_ELEMENTS)}")
        self.se_type = se_type
        self.levels = levels
        self.base_radius = base_radius
        self.activity_measure = activity_measure

    def _activity(self, layer: np.ndarray, win: int = 5) -> np.ndarray:
        """Calcula la medida de actividad local de una capa."""
        blurred = cv2.GaussianBlur(np.abs(layer), (win, win), 0)
        return blurred

    def fuse(self, vis: np.ndarray, ir: np.ndarray) -> np.ndarray:
        """
        Fusiona el par (vis, ir) mediante la Torre Top-Hat.

        Parameters
        ----------
        vis : np.ndarray  (H, W) float32, rango [0, 1]
        ir  : np.ndarray  (H, W) float32, rango [0, 1]

        Returns
        -------
        fused : np.ndarray  (H, W) float32, rango [0, 1]
        """
        assert vis.shape == ir.shape, "Las imágenes deben tener el mismo tamaño."

        layers_vis = top_hat_decomposition(vis, self.se_type, self.levels, self.base_radius)
        layers_ir  = top_hat_decomposition(ir,  self.se_type, self.levels, self.base_radius)

        fused_layers = []
        for lv, li in zip(layers_vis, layers_ir):
            act_v = self._activity(lv)
            act_i = self._activity(li)
            # Selección basada en actividad máxima
            mask = (act_v >= act_i).astype(np.float32)
            fused_layer = mask * lv + (1.0 - mask) * li
            fused_layers.append(fused_layer)

        fused = sum(fused_layers)
        fused = np.clip(fused, 0.0, 1.0)
        return fused

    def __repr__(self) -> str:
        return (
            f"TopHatFusion(se_type={self.se_type!r}, levels={self.levels}, "
            f"base_radius={self.base_radius}, activity={self.activity_measure!r})"
        )
