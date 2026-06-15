"""visualization.py – Funciones para graficar comparaciones visuales y métricas."""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt


def plot_comparison(
    images: dict[str, np.ndarray],
    title: str = "Comparación de métodos de fusión",
    save_path: str | Path | None = None,
) -> None:
    """
    Muestra un mosaico con las imágenes de cada método.

    Parameters
    ----------
    images : dict  {nombre_método: imagen_array}
    title  : str   Título general de la figura.
    save_path : opcional – si se provee, guarda la figura.
    """
    n = len(images)
    fig, axes = plt.subplots(1, n, figsize=(4 * n, 4))
    if n == 1:
        axes = [axes]

    for ax, (name, img) in zip(axes, images.items()):
        ax.imshow(img, cmap="gray", vmin=0, vmax=1)
        ax.set_title(name, fontsize=10)
        ax.axis("off")

    fig.suptitle(title, fontsize=13, y=1.02)
    plt.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(str(save_path), dpi=150, bbox_inches="tight")
    plt.show()


def plot_metrics_bar(
    metrics_df,
    metric: str,
    title: str | None = None,
    save_path: str | Path | None = None,
) -> None:
    """
    Genera un gráfico de barras comparativo para una métrica dada.

    Parameters
    ----------
    metrics_df : pd.DataFrame  con columnas 'method' y la métrica indicada.
    metric     : str  nombre de la columna de la métrica a graficar.
    """
    grouped = metrics_df.groupby("method")[metric].mean().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(8, 4))
    grouped.plot(kind="bar", ax=ax, color="steelblue", edgecolor="black")
    ax.set_title(title or f"Comparación – {metric}", fontsize=12)
    ax.set_ylabel(metric)
    ax.set_xlabel("Método")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(str(save_path), dpi=150, bbox_inches="tight")
    plt.show()
