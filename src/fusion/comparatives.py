"""
comparatives.py
---------------
Algoritmos de fusión de referencia (baseline) para comparación con el método propuesto.

Métodos implementados:
  - Promedio simple (average)
  - Pirámides de Laplace (Laplacian Pyramid)
  - Curvelet (aproximación vía Wavelet 2D con PyWavelets)
"""

import cv2
import numpy as np

try:
    import pywt
    _PYWT_AVAILABLE = True
except ImportError:
    _PYWT_AVAILABLE = False


# ---------------------------------------------------------------------------
# 1. Promedio simple
# ---------------------------------------------------------------------------
def average_fusion(vis: np.ndarray, ir: np.ndarray) -> np.ndarray:
    """Fusión por promedio ponderado igual (0.5 VIS + 0.5 IR)."""
    return np.clip(0.5 * vis + 0.5 * ir, 0.0, 1.0)


# ---------------------------------------------------------------------------
# 2. Pirámides de Laplace
# ---------------------------------------------------------------------------
def _build_gaussian_pyramid(img: np.ndarray, levels: int) -> list[np.ndarray]:
    pyramid = [img.copy()]
    for _ in range(levels - 1):
        img = cv2.pyrDown(img)
        pyramid.append(img)
    return pyramid


def _build_laplacian_pyramid(gaussian: list[np.ndarray]) -> list[np.ndarray]:
    laplacian = []
    for i in range(len(gaussian) - 1):
        expanded = cv2.pyrUp(gaussian[i + 1], dstsize=(gaussian[i].shape[1], gaussian[i].shape[0]))
        lap = gaussian[i] - expanded
        laplacian.append(lap)
    laplacian.append(gaussian[-1])  # capa base
    return laplacian


def _reconstruct_from_laplacian(laplacian: list[np.ndarray]) -> np.ndarray:
    img = laplacian[-1]
    for lap in reversed(laplacian[:-1]):
        img = cv2.pyrUp(img, dstsize=(lap.shape[1], lap.shape[0])) + lap
    return img


def laplacian_pyramid_fusion(
    vis: np.ndarray,
    ir: np.ndarray,
    levels: int = 4,
) -> np.ndarray:
    """
    Fusión mediante pirámides de Laplace.
    Selección por máxima actividad local en cada nivel.
    """
    gv = _build_gaussian_pyramid(vis, levels)
    gi = _build_gaussian_pyramid(ir, levels)
    lv = _build_laplacian_pyramid(gv)
    li = _build_laplacian_pyramid(gi)

    fused_pyr = []
    for lv_layer, li_layer in zip(lv, li):
        act_v = cv2.GaussianBlur(np.abs(lv_layer), (5, 5), 0)
        act_i = cv2.GaussianBlur(np.abs(li_layer), (5, 5), 0)
        mask = (act_v >= act_i).astype(np.float32)
        fused_pyr.append(mask * lv_layer + (1.0 - mask) * li_layer)

    fused = _reconstruct_from_laplacian(fused_pyr)
    return np.clip(fused, 0.0, 1.0)


# ---------------------------------------------------------------------------
# 3. Curvelet (aproximación vía Wavelet 2D)
# ---------------------------------------------------------------------------
def curvelet_fusion(
    vis: np.ndarray,
    ir: np.ndarray,
    wavelet: str = "db4",
    levels: int = 3,
) -> np.ndarray:
    """
    Aproximación de fusión tipo Curvelet usando Wavelet 2D con PyWavelets.
    Requiere: pip install PyWavelets

    Regla de fusión: máxima energía de coeficiente.
    """
    if not _PYWT_AVAILABLE:
        raise ImportError("PyWavelets no está instalado. Ejecuta: pip install PyWavelets")

    coeffs_v = pywt.wavedec2(vis, wavelet=wavelet, level=levels)
    coeffs_i = pywt.wavedec2(ir,  wavelet=wavelet, level=levels)

    fused_coeffs = []
    for cv_item, ci_item in zip(coeffs_v, coeffs_i):
        if isinstance(cv_item, np.ndarray):
            # Aproximación (cA)
            fused_coeffs.append(0.5 * cv_item + 0.5 * ci_item)
        else:
            # Detalles: tupla (cH, cV, cD)
            fused_tuple = tuple(
                np.where(np.abs(a) >= np.abs(b), a, b)
                for a, b in zip(cv_item, ci_item)
            )
            fused_coeffs.append(fused_tuple)

    fused = pywt.waverec2(fused_coeffs, wavelet=wavelet)
    # Ajustar tamaño en caso de diferencia de 1 pixel
    fused = fused[:vis.shape[0], :vis.shape[1]]
    return np.clip(fused, 0.0, 1.0).astype(np.float32)
