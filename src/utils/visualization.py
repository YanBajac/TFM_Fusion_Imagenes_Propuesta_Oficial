"""visualization.py – Funciones para graficar métricas del benchmark."""

from pathlib import Path
import matplotlib.pyplot as plt


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
