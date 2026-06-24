# -*- coding: utf-8 -*-
"""
Propuesta novedosa de fusión VIS/IR (replanteo, oct-2026).

Operador por escala i (radio r=i, diámetro 2i+1; SE crecientes como en el paper
de mamografías, ec. 9-12):
    WTH_lineal = (1/4) Σ_θ [ f − apertura(f, línea_θ) ]      θ ∈ {0,45,90,135}   (líneas PROMEDIADAS)
    BTH_lineal = (1/4) Σ_θ [ cierre(f, línea_θ) − f ]
    WTH_disco  = f − apertura(f, disco)
    BTH_disco  = cierre(f, disco) − f
    WTH_i = máx(WTH_lineal, WTH_disco)        (ec. 13 corregida: promedio de líneas vs disco)
    BTH_i = máx(BTH_lineal, BTH_disco)        (ec. 14)

Agregación multiescala (máximo por píxel entre las n escalas, ec. 17-18):
    WTH_M = máx_i WTH_i ;  BTH_M = máx_i BTH_i

Fusión VIS/IR (base = reconstrucción de Bala et al., ec. 9, con peso m de la fusión PSO):
    I_base = (VIS + IR) / 2
    WTH_F  = máx(WTH_M^VIS, WTH_M^IR)
    BTH_F  = máx(BTH_M^VIS, BTH_M^IR)
    F = clip( I_base + m·WTH_F − m·BTH_F , 0, 1 )

PSO optimiza (n, m) [y opcionalmente radio base] maximizando una aptitud sobre las métricas.
"""
import numpy as np
import cv2
from .optimal_top_hat import disk_se, linear_se, _open, _close, _ANGLES


def wth_bth_scale(f, r):
    """WTH_i, BTH_i de una escala: líneas promediadas vs disco, por máximo."""
    f = f.astype(np.float32)
    wl = np.zeros_like(f)
    bl = np.zeros_like(f)
    for th in _ANGLES:
        se = linear_se(r, th)
        wl += f - _open(f, se)
        bl += _close(f, se) - f
    wth_lin = wl / len(_ANGLES)          # promedio de las 4 líneas
    bth_lin = bl / len(_ANGLES)
    d = disk_se(r)
    wth_disk = f - _open(f, d)           # disco
    bth_disk = _close(f, d) - f
    return np.maximum(wth_lin, wth_disk), np.maximum(bth_lin, bth_disk)


def multiscale_maps(f, n):
    """WTH_M, BTH_M = máximo por píxel sobre i=1..n (radio r=i)."""
    WTH = None
    BTH = None
    for i in range(1, int(n) + 1):
        w, b = wth_bth_scale(f, i)
        WTH = w if WTH is None else np.maximum(WTH, w)
        BTH = b if BTH is None else np.maximum(BTH, b)
    return WTH, BTH


def fuse_novel(vis, ir, n=6, m=0.5):
    """Fusión VIS/IR con la propuesta novedosa (reconstrucción Bala + peso m)."""
    if vis.shape != ir.shape:
        ir = cv2.resize(ir, (vis.shape[1], vis.shape[0]))
    vis = vis.astype(np.float32)
    ir = ir.astype(np.float32)
    base = 0.5 * (vis + ir)
    wv, bv = multiscale_maps(vis, n)
    wi, bi = multiscale_maps(ir, n)
    wth_f = np.maximum(wv, wi)
    bth_f = np.maximum(bv, bi)
    fused = base + m * wth_f - m * bth_f
    return np.clip(fused, 0.0, 1.0).astype(np.float32)


class NovelMultiscaleFusion:
    """Interfaz tipo objeto (propuesta novedosa, replanteo)."""
    def __init__(self, n=6, m=0.5):
        self.n = n
        self.m = m

    def fuse(self, vis, ir):
        return fuse_novel(vis, ir, self.n, self.m)

    def __repr__(self):
        return f"NovelMultiscaleFusion(n={self.n}, m={self.m})"
