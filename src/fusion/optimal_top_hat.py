# -*- coding: utf-8 -*-
"""
optimal_top_hat.py
------------------
Método óptimo de fusión VIS/IR basado en Top-Hat con elementos estructurantes
combinados (disco + 4 lineales) y parámetros (r, m) optimizables por PSO.

Inspirado en:
  - Román et al., realce de mamografías con Top-Hat multiescala (SE circulares y
    lineales, máx. por píxel): ecuaciones (9)-(14).
  - Ortega & Espinoza (FPUNA, 2025), fusión VIS/IR con Top-Hat optimizada por PSO:
    I_FUS = I_base + m·máx(WTH_IR, WTH_VIS) − m·máx(BTH_IR, BTH_VIS),  ec. (12).

Operador WTH/BTH combinado (por defecto, modo 'sum'):
    WTH = WTH_disco + (1/4) Σ_θ WTH_lineal(θ),   θ ∈ {0, 45, 90, 135}
    BTH = BTH_disco + (1/4) Σ_θ BTH_lineal(θ)
Modos alternativos: 'avg' = promedio(disco, prom_lineal); 'max' = máx(disco, prom_lineal).
"""
import cv2
import numpy as np

_ANGLES = (0, 45, 90, 135)


def disk_se(r: int) -> np.ndarray:
    r = max(1, int(round(r)))
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def linear_se(r: int, angle_deg: float) -> np.ndarray:
    """Elemento estructurante lineal de longitud 2r+1 y orientación dada."""
    r = max(1, int(round(r)))
    n = 2 * r + 1
    se = np.zeros((n, n), dtype=np.uint8)
    cx = cy = r
    a = np.deg2rad(angle_deg)
    dx, dy = np.cos(a), np.sin(a)
    x0, y0 = int(round(cx - dx * r)), int(round(cy - dy * r))
    x1, y1 = int(round(cx + dx * r)), int(round(cy + dy * r))
    cv2.line(se, (x0, y0), (x1, y1), 1, 1)
    return se


def _open(f, se):
    return cv2.morphologyEx(f, cv2.MORPH_OPEN, se)


def _close(f, se):
    return cv2.morphologyEx(f, cv2.MORPH_CLOSE, se)


def combined_top_hat(f: np.ndarray, r: int, mode: str = "sum"):
    """Devuelve (WTH, BTH) combinando disco + 4 lineales."""
    f = f.astype(np.float32)
    d = disk_se(r)
    wth_disk = f - _open(f, d)
    bth_disk = _close(f, d) - f
    wl = np.zeros_like(f)
    bl = np.zeros_like(f)
    for th in _ANGLES:
        se = linear_se(r, th)
        wl += f - _open(f, se)
        bl += _close(f, se) - f
    wth_lin = wl / len(_ANGLES)
    bth_lin = bl / len(_ANGLES)
    if mode == "sum":
        return wth_disk + wth_lin, bth_disk + bth_lin
    if mode == "avg":
        return 0.5 * (wth_disk + wth_lin), 0.5 * (bth_disk + bth_lin)
    if mode == "max":
        return np.maximum(wth_disk, wth_lin), np.maximum(bth_disk, bth_lin)
    raise ValueError("mode debe ser 'sum', 'avg' o 'max'")


def fuse_optimal(vis: np.ndarray, ir: np.ndarray, r: int = 3, m: float = 1.0,
                 mode: str = "sum") -> np.ndarray:
    """Fusión VIS/IR con el método óptimo basado en Top-Hat (disco + lineales)."""
    if vis.shape != ir.shape:
        ir = cv2.resize(ir, (vis.shape[1], vis.shape[0]))
    base = 0.5 * (vis.astype(np.float32) + ir.astype(np.float32))
    wth_v, bth_v = combined_top_hat(vis, r, mode)
    wth_i, bth_i = combined_top_hat(ir, r, mode)
    wth_max = np.maximum(wth_v, wth_i)
    bth_max = np.maximum(bth_v, bth_i)
    fused = base + m * wth_max - m * bth_max
    return np.clip(fused, 0.0, 1.0).astype(np.float32)


class OptimalTopHatFusion:
    """Interfaz tipo objeto, consistente con TopHatFusion."""
    def __init__(self, r: int = 3, m: float = 1.0, mode: str = "sum"):
        self.r = r; self.m = m; self.mode = mode

    def fuse(self, vis, ir):
        return fuse_optimal(vis, ir, self.r, self.m, self.mode)

    def __repr__(self):
        return f"OptimalTopHatFusion(r={self.r}, m={self.m}, mode={self.mode!r})"


# ===========================================================================
# Método ÓPTIMO MULTIESCALA (fiel al paper de mamografías, 2.1.4 + 2.2)
# 5 elementos estructurantes por escala (4 lineales 0/45/90/135° + 1 disco),
# combinados por máximo por píxel (ec. 13-14), restas en cascada (ec. 15-16),
# máximos por escala (ec. 17-20) y reconstrucción/fusión (ec. 21 adaptada).
# ===========================================================================

def _wth_bth_5se(f: np.ndarray, r: int):
    """WTH_i y BTH_i combinando 5 SE (disco + 4 lineales) por máximo (ec. 9-14)."""
    f = f.astype(np.float32)
    d = disk_se(r)
    wth = f - _open(f, d)
    bth = _close(f, d) - f
    for th in _ANGLES:
        se = linear_se(r, th)
        wth = np.maximum(wth, f - _open(f, se))
        bth = np.maximum(bth, _close(f, se) - f)
    return wth, bth


def _multiscale_components(f: np.ndarray, n: int, base_radius: float):
    """Devuelve (WTH_M, BTH_M, WTHS_M, BTHS_M) de una fuente (ec. 9-20)."""
    WTH, BTH = [], []
    for i in range(1, n + 1):
        r = max(1, int(round(base_radius * i)))
        w, b = _wth_bth_5se(f, r)
        WTH.append(w); BTH.append(b)
    # restas en cascada (ec. 15-16): WTHS tiene longitud n-1
    WTHS, BTHS = [], []
    for i in range(2, n + 1):
        if i == 2:
            WTHS.append(WTH[1] - WTH[0]); BTHS.append(BTH[1] - BTH[0])
        else:
            WTHS.append(WTH[i - 1] - WTHS[i - 3]); BTHS.append(BTH[i - 1] - BTHS[i - 3])
    wth_m = np.maximum.reduce(WTH)
    bth_m = np.maximum.reduce(BTH)
    wths_m = np.maximum.reduce(WTHS) if WTHS else np.zeros_like(f, dtype=np.float32)
    bths_m = np.maximum.reduce(BTHS) if BTHS else np.zeros_like(f, dtype=np.float32)
    return wth_m, bth_m, wths_m, bths_m


def fuse_optimal_multiscale(vis, ir, n: int = 4, base_radius: float = 1.0,
                            m: float = 1.0) -> np.ndarray:
    """
    Fusión VIS/IR con el método óptimo MULTIESCALA (disco + 4 lineales, cascada).
    Reconstrucción (ec. 21 adaptada a fusión, combinando fuentes por máximo):
        F = base + m·(WTH_M + WTHS_M) − m·(BTH_M + BTHS_M)
    """
    if vis.shape != ir.shape:
        ir = cv2.resize(ir, (vis.shape[1], vis.shape[0]))
    base = 0.5 * (vis.astype(np.float32) + ir.astype(np.float32))
    wv, bv, wsv, bsv = _multiscale_components(vis, n, base_radius)
    wi, bi, wsi, bsi = _multiscale_components(ir, n, base_radius)
    wth_m = np.maximum(wv, wi)
    bth_m = np.maximum(bv, bi)
    wths_m = np.maximum(wsv, wsi)
    bths_m = np.maximum(bsv, bsi)
    fused = base + m * (wth_m + wths_m) - m * (bth_m + bths_m)
    return np.clip(fused, 0.0, 1.0).astype(np.float32)


class OptimalMultiscaleFusion:
    """Método óptimo multiescala (propuesta central de la tesis)."""
    def __init__(self, n: int = 4, base_radius: float = 1.0, m: float = 1.0):
        self.n = n; self.base_radius = base_radius; self.m = m

    def fuse(self, vis, ir):
        return fuse_optimal_multiscale(vis, ir, self.n, self.base_radius, self.m)

    def __repr__(self):
        return f"OptimalMultiscaleFusion(n={self.n}, base_radius={self.base_radius}, m={self.m})"
