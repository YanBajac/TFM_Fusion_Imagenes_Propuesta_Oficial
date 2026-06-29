"""
evaluators.py
-------------
Metricas cuantitativas para evaluar la calidad de imagenes fusionadas.

Metricas clasicas (sin referencia, sobre la imagen fusionada o sus fuentes):
  - Entropia de Shannon (EN)          (mayor mejor)
  - Desviacion Estandar (SD)          (mayor mejor)
  - Eficiencia de Fusion (FE)         (mayor mejor)
  - Gradiente Medio (MG)              (mayor mejor)
  - Informacion Mutua (MI_vis, MI_ir) (mayor mejor)
  - Frecuencia Espacial (SF)          (mayor mejor)

Metricas estandar de calidad de fusion (Xydeas-Petrovic 2000, Sheikh-Bovik
2006, Aslantas-Bendes 2015, Kumar 2013):
  - Qabf : preservacion de bordes basada en gradiente  [0,1]   (mayor mejor)
  - Nabf : ruido / artefactos anadidos por la fusion    >=0     (menor mejor)
  - SSIM : similitud estructural promedio con fuentes   [0,1]   (mayor mejor)
  - SCD  : suma de correlaciones de las diferencias     ~[-2,2] (mayor mejor)
  - VIF  : fidelidad de informacion visual promedio     >=0     (mayor mejor)

Convencion: imagenes en escala de grises float en [0,1].
"""

import numpy as np
from scipy.stats import entropy as scipy_entropy
from scipy.signal import convolve2d, fftconvolve
from skimage.metrics import structural_similarity


METRIC_DIRECTION = {
    "EN": "max", "SD": "max", "FE": "max", "MG": "max",
    "MI_vis": "max", "MI_ir": "max", "SF": "max",
    "Qabf": "max", "Nabf": "min", "SSIM": "max", "SCD": "max", "VIF": "max",
    "FMI": "max", "Q0": "max", "QW": "max", "QE": "max",
}


def _to_uint8(img):
    return (np.clip(img, 0.0, 1.0) * 255).astype(np.uint8)


def _histogram(img, bins=256):
    hist, _ = np.histogram(img.flatten(), bins=bins, range=(0, 1))
    hist = hist / hist.sum()
    return hist


def entropy(img):
    """Entropia de Shannon. (mayor mejor)"""
    hist = _histogram(img)
    return float(scipy_entropy(hist + 1e-12, base=2))


def std_dev(img):
    """Desviacion estandar (contraste). (mayor mejor)"""
    return float(np.std(img))


def fusion_efficiency(fused, vis, ir):
    """FE = EN(fusionada) / promedio EN(fuentes). (mayor mejor)"""
    en_f = entropy(fused)
    en_sources = (entropy(vis) + entropy(ir)) / 2.0
    return float(en_f / (en_sources + 1e-12))


def mean_gradient(img):
    """Gradiente Medio (nitidez de bordes). (mayor mejor)"""
    gx = np.gradient(img, axis=1)
    gy = np.gradient(img, axis=0)
    grad = np.sqrt(gx**2 + gy**2)
    return float(np.mean(grad))


def mutual_information(fused, source, bins=64):
    """Informacion Mutua entre fusionada y fuente. (mayor mejor)"""
    f_flat = (np.clip(fused, 0, 1) * (bins - 1)).astype(int).flatten()
    s_flat = (np.clip(source, 0, 1) * (bins - 1)).astype(int).flatten()
    joint_hist = np.zeros((bins, bins))
    np.add.at(joint_hist, (f_flat, s_flat), 1)
    joint_hist /= joint_hist.sum()
    p_f = joint_hist.sum(axis=1)
    p_s = joint_hist.sum(axis=0)
    nz = joint_hist > 0
    p_f_mat = p_f[:, None] * p_s[None, :]
    mi = np.sum(joint_hist[nz] * np.log2(joint_hist[nz] / p_f_mat[nz]))
    return float(mi)


def spatial_frequency(img):
    """Frecuencia Espacial (actividad espacial global). (mayor mejor)
    SF = sqrt(RF^2 + CF^2), calculada en escala [0,255]."""
    f = np.clip(img, 0.0, 1.0) * 255.0
    rf = np.sqrt(np.mean(np.diff(f, axis=1) ** 2))
    cf = np.sqrt(np.mean(np.diff(f, axis=0) ** 2))
    return float(np.sqrt(rf**2 + cf**2))


# --- Qabf y Nabf: marco de preservacion de gradiente -----------------------
_SOBEL_X = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
_SOBEL_Y = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]], dtype=np.float64)


def _grad_strength_orientation(p):
    sx = convolve2d(p, _SOBEL_X, mode="same", boundary="symm")
    sy = convolve2d(p, _SOBEL_Y, mode="same", boundary="symm")
    g = np.sqrt(sx**2 + sy**2)
    a = np.zeros_like(g)
    mask = sx != 0
    a[mask] = np.arctan(sy[mask] / sx[mask])
    a[~mask] = np.pi / 2.0
    return g, a


def _Q_pair(g_src, a_src, g_f, a_f):
    Tg, kg, Dg = 0.9994, -15.0, 0.5
    Ta, ka, Da = 0.9879, -22.0, 0.8
    G = np.zeros_like(g_src)
    gt = g_src > g_f
    lt = g_src < g_f
    eq = ~(gt | lt)
    G[gt] = g_f[gt] / (g_src[gt] + 1e-12)
    G[lt] = g_src[lt] / (g_f[lt] + 1e-12)
    G[eq] = g_f[eq]
    A = 1.0 - np.abs(a_src - a_f) / (np.pi / 2.0)
    Qg = Tg / (1.0 + np.exp(kg * (G - Dg)))
    Qa = Ta / (1.0 + np.exp(ka * (A - Da)))
    return Qg * Qa


def _qabf_nabf(fused, vis, ir):
    gA, aA = _grad_strength_orientation(vis)
    gB, aB = _grad_strength_orientation(ir)
    gF, aF = _grad_strength_orientation(fused)
    QAF = _Q_pair(gA, aA, gF, aF)
    QBF = _Q_pair(gB, aB, gF, aF)
    wA, wB = gA, gB
    denom = np.sum(wA + wB) + 1e-12
    qabf = float(np.sum(QAF * wA + QBF * wB) / denom)
    artifacts = ((gF > gA) & (gF > gB)).astype(np.float64)
    nabf = float(np.sum(artifacts * ((1.0 - QAF) * wA + (1.0 - QBF) * wB)) / denom)
    return qabf, nabf


def ssim_fusion(fused, vis, ir):
    """SSIM promedio de la fusionada respecto a VIS e IR. (mayor mejor)"""
    s_vis = structural_similarity(fused, vis, data_range=1.0)
    s_ir = structural_similarity(fused, ir, data_range=1.0)
    return float(0.5 * (s_vis + s_ir))


def _corr(a, b):
    a = a.flatten() - a.mean()
    b = b.flatten() - b.mean()
    denom = np.sqrt(np.sum(a**2) * np.sum(b**2)) + 1e-12
    return float(np.sum(a * b) / denom)


def scd(fused, vis, ir):
    """SCD = r(F-IR, VIS) + r(F-VIS, IR). (mayor mejor, optimo ~2)"""
    return _corr(fused - ir, vis) + _corr(fused - vis, ir)


def _gauss_window(n, sigma):
    ax = np.arange(-(n // 2), n // 2 + 1)
    g = np.exp(-(ax**2) / (2.0 * sigma**2))
    g = np.outer(g, g)
    return g / g.sum()


def _vifp(ref, dist, sigma_nsq=2.0):
    ref = ref.astype(np.float64)
    dist = dist.astype(np.float64)
    num = 0.0
    den = 0.0
    for scale in range(1, 5):
        n = 2 ** (4 - scale + 1) + 1
        sd = n / 5.0
        win = _gauss_window(n, sd)
        if scale > 1:
            ref = fftconvolve(ref, win, mode="valid")[::2, ::2]
            dist = fftconvolve(dist, win, mode="valid")[::2, ::2]
        mu1 = fftconvolve(ref, win, mode="valid")
        mu2 = fftconvolve(dist, win, mode="valid")
        mu1_sq, mu2_sq, mu1_mu2 = mu1 * mu1, mu2 * mu2, mu1 * mu2
        sigma1_sq = fftconvolve(ref * ref, win, mode="valid") - mu1_sq
        sigma2_sq = fftconvolve(dist * dist, win, mode="valid") - mu2_sq
        sigma12 = fftconvolve(ref * dist, win, mode="valid") - mu1_mu2
        sigma1_sq = np.maximum(sigma1_sq, 0)
        sigma2_sq = np.maximum(sigma2_sq, 0)
        g = sigma12 / (sigma1_sq + 1e-10)
        sv_sq = sigma2_sq - g * sigma12
        g = np.where(sigma1_sq < 1e-10, 0.0, g)
        sv_sq = np.where(sigma1_sq < 1e-10, sigma2_sq, sv_sq)
        sigma1_sq = np.where(sigma1_sq < 1e-10, 0.0, sigma1_sq)
        g = np.where(sigma2_sq < 1e-10, 0.0, g)
        sv_sq = np.where(sigma2_sq < 1e-10, 0.0, sv_sq)
        sv_sq = np.where(g < 0, sigma2_sq, sv_sq)
        g = np.maximum(g, 0)
        sv_sq = np.maximum(sv_sq, 1e-10)
        num += np.sum(np.log10(1.0 + g * g * sigma1_sq / (sv_sq + sigma_nsq)))
        den += np.sum(np.log10(1.0 + sigma1_sq / sigma_nsq))
    return float(num / (den + 1e-12))


def vif_fusion(fused, vis, ir):
    """VIF promedio de la fusionada respecto a VIS e IR. (mayor mejor)"""
    f = np.clip(fused, 0, 1) * 255.0
    v = np.clip(vis, 0, 1) * 255.0
    i = np.clip(ir, 0, 1) * 255.0
    return float(0.5 * (_vifp(v, f) + _vifp(i, f)))


# --- FMI: Fusion Mutual Information (Haghighat 2011), sobre mapas de gradiente ---
def _nmi(a, b, bins=64):
    a = (np.clip(a, 0, 1) * (bins - 1)).astype(int).flatten()
    b = (np.clip(b, 0, 1) * (bins - 1)).astype(int).flatten()
    j = np.zeros((bins, bins)); np.add.at(j, (a, b), 1); j /= j.sum()
    pa = j.sum(1); pb = j.sum(0); nz = j > 0
    pab = (pa[:, None] * pb[None, :])
    I = np.sum(j[nz] * np.log2(j[nz] / pab[nz]))
    Ha = -np.sum(pa[pa > 0] * np.log2(pa[pa > 0]))
    Hb = -np.sum(pb[pb > 0] * np.log2(pb[pb > 0]))
    return float(2.0 * I / (Ha + Hb)) if (Ha + Hb) > 1e-12 else 0.0


def _grad_feat(x):
    gx = np.gradient(x, axis=1); gy = np.gradient(x, axis=0)
    g = np.sqrt(gx ** 2 + gy ** 2)
    mn, mx = g.min(), g.max()
    return (g - mn) / (mx - mn + 1e-12)


def fmi(fused, vis, ir):
    """Fusion Mutual Information (gradiente, normalizada, ~[0,1]; mayor mejor)."""
    fF, fV, fI = _grad_feat(fused), _grad_feat(vis), _grad_feat(ir)
    return 0.5 * (_nmi(fF, fV) + _nmi(fF, fI))


# --- Indices de calidad de fusion de Piella & Heijmans (2003): Q0, QW, QE ---
def _q0_and_var(a, b, w=7):
    from scipy.ndimage import uniform_filter
    a = a.astype(np.float64); b = b.astype(np.float64)
    mu_a = uniform_filter(a, w); mu_b = uniform_filter(b, w)
    va = np.maximum(uniform_filter(a * a, w) - mu_a ** 2, 0)
    vb = np.maximum(uniform_filter(b * b, w) - mu_b ** 2, 0)
    cov = uniform_filter(a * b, w) - mu_a * mu_b
    num = 4.0 * cov * mu_a * mu_b
    den = (va + vb) * (mu_a ** 2 + mu_b ** 2)
    q = np.where(den > 1e-12, num / den, 1.0)
    return q, va, vb


def _piella_QW(a, b, f, w=7):
    qaf, sa, _ = _q0_and_var(a, f, w)
    qbf, sb, _ = _q0_and_var(b, f, w)
    lam = sa / (sa + sb + 1e-12)
    local = lam * qaf + (1.0 - lam) * qbf
    Q0 = float(np.mean(local))
    c = np.maximum(sa, sb)
    QW = float(np.sum((c / (c.sum() + 1e-12)) * local))
    return Q0, QW


def piella_indices(fused, vis, ir, w=7, alpha=1.0):
    """Devuelve (Q0, QW, QE) de Piella (mayor mejor, ~[0,1])."""
    Q0, QW = _piella_QW(vis, ir, fused, w)
    ea, eb, ef = _grad_feat(vis), _grad_feat(ir), _grad_feat(fused)
    _, QWe = _piella_QW(ea, eb, ef, w)
    QE = float(QW * (QWe ** alpha))
    return Q0, QW, QE


def evaluate_all(fused, vis, ir):
    """Calcula todas las metricas. Claves: EN, SD, FE, MG, MI_vis, MI_ir,
    SF, Qabf, Nabf, SSIM, SCD, VIF, FMI, Q0, QW, QE."""
    qabf, nabf = _qabf_nabf(fused, vis, ir)
    q0, qw, qe = piella_indices(fused, vis, ir)
    return {
        "EN":     entropy(fused),
        "SD":     std_dev(fused),
        "FE":     fusion_efficiency(fused, vis, ir),
        "MG":     mean_gradient(fused),
        "MI_vis": mutual_information(fused, vis),
        "MI_ir":  mutual_information(fused, ir),
        "SF":     spatial_frequency(fused),
        "Qabf":   qabf,
        "Nabf":   nabf,
        "SSIM":   ssim_fusion(fused, vis, ir),
        "SCD":    scd(fused, vis, ir),
        "VIF":    vif_fusion(fused, vis, ir),
        "FMI":    fmi(fused, vis, ir),
        "Q0":     q0,
        "QW":     qw,
        "QE":     qe,
    }
