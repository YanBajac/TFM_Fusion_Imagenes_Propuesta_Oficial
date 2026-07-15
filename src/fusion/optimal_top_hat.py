# -*- coding: utf-8 -*-
"""
optimal_top_hat.py
------------------
PROPUESTA NOVEDOSA: fusión VIS/IR basada en Top-Hat de una sola escala con
elementos estructurantes combinados (disco + 4 lineales) por SUMA de ramas,
y parámetros (r, m) optimizados por PSO.

Basado en:
  - Bala et al. (2024), filtro morfológico multiángulo de dos etapas (ecs. 1-9):
    respuestas lineales promediadas + respuesta del disco, combinadas por suma.
  - Ortega & Espinoza (FPUNA, 2025), fusión VIS/IR con Top-Hat optimizada por PSO:
    I_FUS = I_base + m·máx(WTH_IR, WTH_VIS) − m·máx(BTH_IR, BTH_VIS),  ec. (12).

Operador WTH/BTH combinado (propuesta: modo 'sum'):
    WTH = WTH_disco + (1/4) Σ_θ WTH_lineal(θ),   θ ∈ {0, 45, 90, 135}
    BTH = BTH_disco + (1/4) Σ_θ BTH_lineal(θ)
Modos alternativos para ablación: 'avg' y 'max'.
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
