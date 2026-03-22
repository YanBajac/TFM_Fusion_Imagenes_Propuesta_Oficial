"""
evaluators.py
-------------
Métricas cuantitativas para evaluar la calidad de imágenes fusionadas.

Métricas implementadas:
  - Entropía de Shannon (EN)
  - Desviación Estándar (SD)
  - Eficiencia de Fusión / Factor de Fusión (FE)
  - Gradiente Medio (MG)
  - Información Mutua (MI)
"""

import numpy as np
from scipy.stats import entropy as scipy_entropy
from skimage.filters import sobel


# ---------------------------------------------------------------------------
# Utilidades internas
# ---------------------------------------------------------------------------

def _to_uint8(img: np.ndarray) -> np.ndarray:
    """Convierte imagen float [0,1] a uint8 [0,255]."""
    return (np.clip(img, 0.0, 1.0) * 255).astype(np.uint8)


def _histogram(img: np.ndarray, bins: int = 256) -> np.ndarray:
    """Histograma normalizado de una imagen."""
    hist, _ = np.histogram(img.flatten(), bins=bins, range=(0, 1))
    hist = hist / hist.sum()
    return hist


# ---------------------------------------------------------------------------
# Métricas
# ---------------------------------------------------------------------------

def entropy(img: np.ndarray) -> float:
    """
    Entropía de Shannon.
    Mide la riqueza de información en la imagen.
    Mayor valor → más información.
    """
    hist = _histogram(img)
    return float(scipy_entropy(hist + 1e-12, base=2))


def std_dev(img: np.ndarray) -> float:
    """
    Desviación estándar de los niveles de gris.
    Mayor valor → mayor contraste.
    """
    return float(np.std(img))


def fusion_efficiency(
    fused: np.ndarray,
    vis: np.ndarray,
    ir: np.ndarray,
) -> float:
    """
    Eficiencia de Fusión (FE).
    Relación entre la entropía de la imagen fusionada y el promedio de las fuentes.
    FE > 1 → la fusión aporta más información que las fuentes por separado.
    """
    en_f = entropy(fused)
    en_sources = (entropy(vis) + entropy(ir)) / 2.0
    return float(en_f / (en_sources + 1e-12))


def mean_gradient(img: np.ndarray) -> float:
    """
    Gradiente Medio (MG).
    Mide la nitidez y el detalle de bordes en la imagen.
    Mayor valor → más detalle espacial.
    """
    gx = np.gradient(img, axis=1)
    gy = np.gradient(img, axis=0)
    grad = np.sqrt(gx**2 + gy**2)
    return float(np.mean(grad))


def mutual_information(
    fused: np.ndarray,
    source: np.ndarray,
    bins: int = 64,
) -> float:
    """
    Información Mutua (MI) entre la imagen fusionada y una fuente.
    Mayor valor → mayor similitud de información.
    """
    f_flat = (np.clip(fused, 0, 1) * (bins - 1)).astype(int).flatten()
    s_flat = (np.clip(source, 0, 1) * (bins - 1)).astype(int).flatten()

    joint_hist = np.zeros((bins, bins))
    np.add.at(joint_hist, (f_flat, s_flat), 1)
    joint_hist /= joint_hist.sum()

    p_f = joint_hist.sum(axis=1)
    p_s = joint_hist.sum(axis=0)

    # MI = sum p(f,s) * log( p(f,s) / (p(f)*p(s)) )
    mi = 0.0
    nz = joint_hist > 0
    mi = np.sum(
        joint_hist[nz] * np.log2(joint_hist[nz] / (p_f[nz.any(axis=1)][:, None] * p_s[nz.any(axis=0)])[nz])
    )
    return float(mi)


def evaluate_all(
    fused: np.ndarray,
    vis: np.ndarray,
    ir: np.ndarray,
) -> dict:
    """
    Calcula todas las métricas y las retorna en un diccionario.

    Returns
    -------
    dict con claves: EN, SD, FE, MG, MI_vis, MI_ir
    """
    return {
        "EN":     entropy(fused),
        "SD":     std_dev(fused),
        "FE":     fusion_efficiency(fused, vis, ir),
        "MG":     mean_gradient(fused),
        "MI_vis": mutual_information(fused, vis),
        "MI_ir":  mutual_information(fused, ir),
    }
