import pandas as pd
from pathlib import Path

base_dir = Path(__file__).resolve().parents[1]
csv_path = base_dir / 'experiments' / 'results' / 'metrics_reports' / 'benchmark_top_hat.csv'
out_path = base_dir / 'docs' / 'reportes_finales' / 'reporte_benchmark_multiescala.md'
out_path.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(csv_path)

# Variables configurables
metrics = ['EN', 'SD', 'FE', 'MG', 'MI_vis', 'MI_ir']
group_cols = ['Structuring_Element', 'Levels', 'Base_Radius']

df_mean = df.groupby(group_cols)[metrics].mean().reset_index()

# Find best parameters for each metric
best_configs = {}
for m in metrics:
    best_row = df_mean.loc[df_mean[m].idxmax()]
    best_configs[m] = {
        'SE': best_row['Structuring_Element'],
        'L': best_row['Levels'],
        'R': best_row['Base_Radius'],
        'Val': best_row[m]
    }

md_content = f"""# Análisis Integral de la Torre de Fusión Top-Hat (Modo Multiescala)

Este documento detalla los resultados cuantitativos obtenidos al evaluar de forma exhaustiva 720 integraciones totales. Las configuraciones de modo multiescala variaron cruzando:
- 3 Elementos Estructurantes (`disk`, `square`, `cross`)
- 4 Niveles de profundidad (`2`, `3`, `4`, `5`)
- 3 Radios Base del Elemento (`2`, `3`, `5` píxeles)
Sobre los 20 pares base de imágenes VIS/IR extraídas del dataset TNO.

## 1. Configuraciones Óptimas por Métrica

El análisis de las medias globales revela empíricamente las siguientes configuraciones maximizadoras según las métricas sin referencia (buscamos maximizar estos valores):

"""

metric_desc = {
    'EN': "Entropía (riqueza de información)",
    'SD': "Desviación Estándar (contraste general)",
    'FE': "Eficiencia de Fusión (ganancia relativa de información)",
    'MG': "Gradiente Medio (nitidez de bordes y texturas)",
    'MI_vis': "Información Mutua transferida desde el sensor Visible",
    'MI_ir': "Información Mutua transferida desde el sensor Térmico (IR)"
}

for m in metrics:
    cfg = best_configs[m]
    md_content += f"- **Mejor {m}** *({metric_desc[m]})*: Elemento `{cfg['SE']}`, Niveles `{cfg['L']}`, Radio Base `{cfg['R']}` logrando un promedio óptimo de **{cfg['Val']:.4f}**.\n"

md_content += """
## 2. Resumen Estadístico Total (Promedios)

A continuación se expone la tabla íntegra de promedios para las 36 configuraciones evaluadas (ordenada alfabéticamente):

"""

# Add markdown table
md_content += df_mean.round(4).sort_values(by=group_cols).to_markdown(index=False)

md_content += """

## 3. Conclusiones para la Tesis y Guía de Interpretación

1. **Balance de Escala (L y R₀)**: Un número masivo de niveles y radios inmensos no garantiza siempre una mejor métrica; puede introducir saturación. La tabla de arriba ayuda a discernir si un nivel moderado (ej. L=3, R=3) extrae métricas lo suficientemente cercanas al óptimo pero requiriendo menos esfuerzo computacional.
2. **Impacto de la Geometría**: A nivel microscópico, los contornos orgánicos (`disk`) frente a los ángulos rectos (`square`, `cross`) arrojan diferentes valores de **MG**. Revisar cuál elemento triunfa constantemente en Gradiente Medio (`MG`) dictará el mejor preservador de bordes visuales puros.
3. **Múltiples Fuentes (MI)**: La asimetría natural entre los resultados de `MI_vis` y `MI_ir` sube acorde al peso final que la Transformada le da genéticamente a una u otra imagen durante el umbral de 'energía local' por capa.

*Nota Científica: Con estos resultados tabulados es ahora factible formular comparaciones de caja (Boxplots) o validar si la diferencia de Entropía (`EN`) entre geometrías es estadísticamente significativa usando el test de Wilcoxon o Friedman mencionado en el archivo general del repo.*
"""

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f"Reporte generado exitosamente en {out_path}")
