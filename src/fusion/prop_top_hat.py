"""
prop_top_hat.py
---------------
Algoritmo de fusión propuesto basado en la Torre Top-Hat (Top-Hat Tower Fusion).
Soporta múltiples geometrías de elemento estructurante y múltiples niveles de
descomposición. Opcionalmente incorpora la transformada Black Top-Hat para
capturar simultáneamente detalles brillantes y oscuros.

Esquema:
    Para cada nivel k = 1..L:
        b_k    = SE(tipo, k * r_0)
        gamma  = apertura(R_{k-1}, b_k)            (R_0 = f)
        WTH_k  = R_{k-1} - gamma                    (componentes brillantes)
        BTH_k  = phi(R_{k-1}, b_k) - R_{k-1}        (componentes oscuros, opcional)
        R_k    = gamma                              (residual = apertura)
    base = R_L

La descomposicion sin BTH cumple:  f = sum_k WTH_k + base    (telescoping).

Regla de fusion por capa:
    - Capas de detalle (WTH y BTH): seleccion por actividad local maxima.
    - Capa base (residual): promedio (la base es de baja frecuencia y no debe
      seleccionarse pixel-a-pixel para evitar saltos de iluminacion).
"""

import cv2
import numpy as np


# ---------------------------------------------------------------------------
# Elementos estructurantes disponibles
# ---------------------------------------------------------------------------
STRUCTURING_ELEMENTS = {
    "disk":    lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)),
    "square":  lambda r: cv2.getStructuringElement(cv2.MORPH_RECT,    (2 * r + 1, 2 * r + 1)),
    "cross":   lambda r: cv2.getStructuringElement(cv2.MORPH_CROSS,   (2 * r + 1, 2 * r + 1)),
}


def white_top_hat(image: np.ndarray, se: np.ndarray) -> np.ndarray:
    """White Top-Hat: WTH = f - apertura(f, se). Aisla estructuras brillantes."""
    opened = cv2.morphologyEx(image, cv2.MORPH_OPEN, se)
    return image - opened


def black_top_hat(image: np.ndarray, se: np.ndarray) -> np.ndarray:
    """Black Top-Hat: BTH = cierre(f, se) - f. Aisla estructuras oscuras."""
    closed = cv2.morphologyEx(image, cv2.MORPH_CLOSE, se)
    return closed - image


def top_hat_decomposition(
    image: np.ndarray,
    se_type: str = "disk",
    levels: int = 3,
    base_radius: int = 3,
    use_black_top_hat: bool = False,
) -> dict:
    """
    Descompone la imagen en capas Top-Hat de radio creciente.

    Returns
    -------
    decomposition : dict con claves
        'wth'   : list[np.ndarray]  capas White Top-Hat (longitud L)
        'bth'   : list[np.ndarray]  capas Black Top-Hat (longitud L) o vacia
        'base'  : np.ndarray        residual de baja frecuencia

    Notas
    -----
    Sin BTH: sum(wth) + base == image  (reconstruccion exacta).
    """
    builder = STRUCTURING_ELEMENTS[se_type]
    wth_layers: list = []
    bth_layers: list = []
    residual = image.astype(np.float32, copy=True)

    for lvl in range(1, levels + 1):
        radius = base_radius * lvl
        se = builder(radius)

        opened = cv2.morphologyEx(residual, cv2.MORPH_OPEN, se)
        wth = residual - opened
        wth_layers.append(wth)

        if use_black_top_hat:
            closed = cv2.morphologyEx(residual, cv2.MORPH_CLOSE, se)
            bth = closed - residual
            bth_layers.append(bth)

        # El nuevo residual es la apertura: equivalente a residual - wth, pero
        # se prefiere usar `opened` directamente para evitar errores de FP.
        residual = opened

    return {
        "wth": wth_layers,
        "bth": bth_layers,
        "base": residual,
    }


def _local_activity(layer: np.ndarray, win: int = 5) -> np.ndarray:
    """Magnitud absoluta de la capa, suavizada con un kernel gaussiano."""
    return cv2.GaussianBlur(np.abs(layer), (win, win), 0)


def _select_max_activity(lv: np.ndarray, li: np.ndarray, win: int = 5) -> np.ndarray:
    """Combina dos capas seleccionando, por pixel, la de mayor actividad local."""
    av = _local_activity(lv, win)
    ai = _local_activity(li, win)
    mask = (av >= ai).astype(lv.dtype)
    return mask * lv + (1.0 - mask) * li


class TopHatFusion:
    """
    Fusion de imagenes VIS + IR mediante la Torre Top-Hat.

    Parameters
    ----------
    se_type : str
        Tipo de elemento estructurante: 'disk', 'square' o 'cross'.
    levels : int
        Numero de niveles de descomposicion (L >= 1).
    base_radius : int
        Radio del SE en el primer nivel (r_0 >= 1).
    use_black_top_hat : bool
        Si True, descompone tambien con Black Top-Hat (detalles oscuros).
    base_rule : str
        Como combinar la capa base. 'mean' = promedio (recomendado).
        'max' = seleccion por actividad (comportamiento heredado).
    activity_window : int
        Tamano de la ventana gaussiana para la actividad local. Debe ser impar.
    """

    def __init__(
        self,
        se_type: str = "disk",
        levels: int = 3,
        base_radius: int = 3,
        use_black_top_hat: bool = False,
        base_rule: str = "mean",
        activity_window: int = 5,
    ):
        if se_type not in STRUCTURING_ELEMENTS:
            raise ValueError(f"se_type debe ser uno de {list(STRUCTURING_ELEMENTS)}")
        if base_rule not in ("mean", "max"):
            raise ValueError("base_rule debe ser 'mean' o 'max'")
        if levels < 1:
            raise ValueError("levels debe ser >= 1")
        if base_radius < 1:
            raise ValueError("base_radius debe ser >= 1")
        if activity_window % 2 == 0:
            raise ValueError("activity_window debe ser impar")

        self.se_type = se_type
        self.levels = levels
        self.base_radius = base_radius
        self.use_black_top_hat = use_black_top_hat
        self.base_rule = base_rule
        self.activity_window = activity_window

    def _fuse_base(self, base_v: np.ndarray, base_i: np.ndarray) -> np.ndarray:
        if self.base_rule == "mean":
            return 0.5 * (base_v + base_i)
        return _select_max_activity(base_v, base_i, self.activity_window)

    def fuse(self, vis: np.ndarray, ir: np.ndarray) -> np.ndarray:
        """Fusiona el par (vis, ir) y devuelve la imagen fusionada en [0,1]."""
        if vis.shape != ir.shape:
            raise ValueError("Las imagenes deben tener el mismo tamano.")

        dec_v = top_hat_decomposition(vis, self.se_type, self.levels,
                                      self.base_radius, self.use_black_top_hat)
        dec_i = top_hat_decomposition(ir,  self.se_type, self.levels,
                                      self.base_radius, self.use_black_top_hat)

        # 1) Detalles WTH: max-actividad
        fused_wth_sum = np.zeros_like(vis, dtype=np.float32)
        for lv, li in zip(dec_v["wth"], dec_i["wth"]):
            fused_wth_sum += _select_max_activity(lv, li, self.activity_window)

        # 2) Detalles BTH (si corresponde): max-actividad
        fused_bth_sum = np.zeros_like(vis, dtype=np.float32)
        if self.use_black_top_hat:
            for lv, li in zip(dec_v["bth"], dec_i["bth"]):
                fused_bth_sum += _select_max_activity(lv, li, self.activity_window)

        # 3) Base: promedio (default)
        fused_base = self._fuse_base(dec_v["base"], dec_i["base"])

        # 4) Reconstruccion: F = base + sum(WTH) - sum(BTH)
        fused = fused_base + fused_wth_sum - fused_bth_sum

        return np.clip(fused, 0.0, 1.0).astype(np.float32)

    def __repr__(self) -> str:
        return (
            f"TopHatFusion(se_type={self.se_type!r}, levels={self.levels}, "
            f"base_radius={self.base_radius}, use_black_top_hat={self.use_black_top_hat}, "
            f"base_rule={self.base_rule!r})"
        )
