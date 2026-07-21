"""
comparatives.py
---------------
Algoritmos de fusión de referencia (baseline) para comparación con el método propuesto.

Métodos implementados (benchmark de la tesis):
  - LP    : Pirámide de Laplace (Burt y Adelson)
  - RP    : Ratio of low-pass Pyramid (Toet 1989)
  - DWT   : Transformada Wavelet Discreta (db1, máx |coef| en detalle)
  - DTCWT : Dual-Tree Complex Wavelet Transform (paquete dtcwt)
  - CVT   : Curvelet (aproximación vía Wavelet 2D db4 con PyWavelets)
  - TopHat clásico : fusión morfológica básica con disco (WTH/BTH por máximo)
  - Promedio simple (auxiliar)
"""

import cv2
import numpy as np

try:
    import pywt
    _PYWT_AVAILABLE = True
except ImportError:
    _PYWT_AVAILABLE = False

try:
    import dtcwt as _dtcwt
    _DTCWT_AVAILABLE = True
except ImportError:
    _DTCWT_AVAILABLE = False


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


# ---------------------------------------------------------------------------
# 4. Ratio of low-pass Pyramid (Toet, 1989)
# ---------------------------------------------------------------------------
def ratio_pyramid_fusion(vis: np.ndarray, ir: np.ndarray, levels: int = 4) -> np.ndarray:
    """
    Fusión por pirámide de razones de paso bajo (RoLP).
    En cada nivel se forma la razón R_l = G_l / expand(G_{l+1}) y se elige,
    píxel a píxel, la razón que más se aparta de 1 (mayor contraste local).
    Reconstrucción multiplicativa desde la base promediada.
    """
    eps = 1e-6
    gv = _build_gaussian_pyramid(vis.astype(np.float32), levels + 1)
    gi = _build_gaussian_pyramid(ir.astype(np.float32), levels + 1)

    def _ratios(g):
        rs = []
        for l in range(levels):
            up = cv2.pyrUp(g[l + 1], dstsize=(g[l].shape[1], g[l].shape[0]))
            rs.append((g[l] + eps) / (up + eps))
        return rs

    rv, ri = _ratios(gv), _ratios(gi)
    fused_r = [np.where(np.abs(a - 1.0) >= np.abs(b - 1.0), a, b) for a, b in zip(rv, ri)]

    img = 0.5 * (gv[levels] + gi[levels])          # base promediada
    for l in reversed(range(levels)):
        up = cv2.pyrUp(img, dstsize=(fused_r[l].shape[1], fused_r[l].shape[0]))
        img = fused_r[l] * (up + eps)
    return np.clip(img, 0.0, 1.0).astype(np.float32)


# ---------------------------------------------------------------------------
# 5. Transformada Wavelet Discreta (DWT)
# ---------------------------------------------------------------------------
def dwt_fusion(vis: np.ndarray, ir: np.ndarray, wavelet: str = "db1",
               levels: int = 3) -> np.ndarray:
    """
    Fusión DWT clásica: aproximación por promedio y detalle por máxima
    magnitud de coeficiente (wavelet Haar/db1 para diferenciarla de la
    aproximación curvelet, que usa db4).
    """
    if not _PYWT_AVAILABLE:
        raise ImportError("PyWavelets no está instalado. Ejecuta: pip install PyWavelets")
    coeffs_v = pywt.wavedec2(vis, wavelet=wavelet, level=levels)
    coeffs_i = pywt.wavedec2(ir, wavelet=wavelet, level=levels)
    fused_coeffs = []
    for cv_item, ci_item in zip(coeffs_v, coeffs_i):
        if isinstance(cv_item, np.ndarray):
            fused_coeffs.append(0.5 * cv_item + 0.5 * ci_item)
        else:
            fused_coeffs.append(tuple(
                np.where(np.abs(a) >= np.abs(b), a, b)
                for a, b in zip(cv_item, ci_item)))
    fused = pywt.waverec2(fused_coeffs, wavelet=wavelet)
    fused = fused[:vis.shape[0], :vis.shape[1]]
    return np.clip(fused, 0.0, 1.0).astype(np.float32)


# ---------------------------------------------------------------------------
# 6. Dual-Tree Complex Wavelet Transform (DTCWT)
# ---------------------------------------------------------------------------
def dtcwt_fusion(vis: np.ndarray, ir: np.ndarray, levels: int = 4) -> np.ndarray:
    """
    Fusión DTCWT (Kingsbury): aproximación por promedio y subbandas complejas
    direccionales por máxima magnitud. Requiere: pip install dtcwt
    """
    if not _DTCWT_AVAILABLE:
        raise ImportError("dtcwt no está instalado. Ejecuta: pip install dtcwt")
    t = _dtcwt.Transform2d()
    pv = t.forward(vis.astype(np.float64), nlevels=levels)
    pi = t.forward(ir.astype(np.float64), nlevels=levels)
    lowpass = 0.5 * (pv.lowpass + pi.lowpass)
    highpasses = []
    for hv, hi in zip(pv.highpasses, pi.highpasses):
        mask = np.abs(hv) >= np.abs(hi)
        highpasses.append(np.where(mask, hv, hi))
    fused = t.inverse(_dtcwt.Pyramid(lowpass, tuple(highpasses)))
    fused = fused[:vis.shape[0], :vis.shape[1]]
    return np.clip(fused, 0.0, 1.0).astype(np.float32)


# ---------------------------------------------------------------------------
# 7. Top-Hat clásico (fusión morfológica básica)
# ---------------------------------------------------------------------------
def tophat_classic_fusion(vis: np.ndarray, ir: np.ndarray, r: int = 5,
                          m: float = 1.0) -> np.ndarray:
    """
    Metodología clásica de la transformada Top-Hat para fusión de imágenes:
    un único disco de radio r, detalle brillante y oscuro por máximo entre
    fuentes, reconstrucción aditivo-sustractiva (sin ponderación con m = 1,
    el caso clásico; m ajustable para la variante optimizada por PSO del
    esquema de Ortega y Espinoza, 2025):
        F = (VIS+IR)/2 + m·máx(WTH_v, WTH_i) − m·máx(BTH_v, BTH_i)
    """
    se = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    v = vis.astype(np.float32)
    i = ir.astype(np.float32)
    wth_v = v - cv2.morphologyEx(v, cv2.MORPH_OPEN, se)
    wth_i = i - cv2.morphologyEx(i, cv2.MORPH_OPEN, se)
    bth_v = cv2.morphologyEx(v, cv2.MORPH_CLOSE, se) - v
    bth_i = cv2.morphologyEx(i, cv2.MORPH_CLOSE, se) - i
    base = 0.5 * (v + i)
    fused = base + m * np.maximum(wth_v, wth_i) - m * np.maximum(bth_v, bth_i)
    return np.clip(fused, 0.0, 1.0).astype(np.float32)
