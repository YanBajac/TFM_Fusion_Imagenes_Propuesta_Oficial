import os
import time
import numpy as np
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

# Configurar el path para poder importar src
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from src.datasets import get_dataloader
from src.fusion.prop_top_hat import TopHatFusion
from src.metrics.evaluators import evaluate_all

def main():
    print("Iniciando Benchmark de Torre Top-Hat con PyTorch DataLoader...")
    
    # Directorios de salida
    results_dir = project_root / 'experiments' / 'results'
    metrics_dir = results_dir / 'metrics_reports'
    metrics_dir.mkdir(parents=True, exist_ok=True)
    
    # Configurar dataloader
    print("Cargando imágenes...")
    loader = get_dataloader(batch_size=1, shuffle=False)
    
    # Configuraciones a evaluar
    se_types = ['disk', 'square', 'cross']
    levels_list = [2, 3, 4, 5]
    radius_list = [2, 3, 5]
    
    results = []
    
    # Iterar sobre las imágenes
    for idx, (vis_batch, ir_batch) in enumerate(loader):
        # Convertir a numpy para usar cv2.morphologyEx
        vis_np = vis_batch.squeeze().numpy()  # [H, W]
        ir_np = ir_batch.squeeze().numpy()
        
        # Validar consistencia
        if vis_np.ndim != 2:
            if vis_np.ndim >= 3:
                vis_np = vis_np[0]
                ir_np = ir_np[0]
        
        print(f"Procesando Par de Imágenes {idx + 1}/{len(loader)}...")
        
        for se in se_types:
            for lvl in levels_list:
                for r0 in radius_list:
                    fuser = TopHatFusion(se_type=se, levels=lvl, base_radius=r0)
                    
                    start_t = time.time()
                    fused = fuser.fuse(vis_np, ir_np)
                    end_t = time.time()
                    
                    # Guardar la imagen rutada
                    import cv2
                    out_dir = results_dir / 'fused_images' / f"{se}_L{lvl}_R{r0}"
                    out_dir.mkdir(parents=True, exist_ok=True)
                    img_name = f"pair_{idx+1:03d}.png"
                    out_path = out_dir / img_name
                    cv2.imwrite(str(out_path), (fused * 255).astype(np.uint8))
                    
                    # Calcular métricas
                    metrics = evaluate_all(fused, vis_np, ir_np)
                    
                    # Guardar en reporte
                    record = {
                        'Image_ID': f"pair_{idx+1:03d}",
                        'Structuring_Element': se,
                        'Levels': lvl,
                        'Base_Radius': r0,
                        'Time_seconds': end_t - start_t,
                    }
                    record.update(metrics)
                    results.append(record)

    # Crear DataFrame
    df = pd.DataFrame(results)
    
    # Guardar CSV
    csv_path = metrics_dir / 'benchmark_top_hat.csv'
    df.to_csv(csv_path, index=False)
    print(f"\nDatos guardados exitosamente en: {csv_path}")
    
    # ----- PLATAFORMA PLOTLY -----
    print("Generando Dashboard Interactivo con Plotly...")
    html_path = metrics_dir / 'metrics_dashboard.html'
    
    metrics_cols = ['EN', 'SD', 'FE', 'MG', 'MI_vis', 'MI_ir']
    
    # 1. Tabla de Promedios
    group_cols = ['Structuring_Element', 'Levels', 'Base_Radius']
    df_mean = df.groupby(group_cols)[metrics_cols].mean().reset_index()
    df_mean = df_mean.round(4).sort_values(by=group_cols)
    
    # Crear HTML base
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>TopHat Fusion Benchmark Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f4f7f6; color: #333; }}
            h1, h2 {{ color: #2c3e50; }}
            .container {{ max-width: 1200px; margin: auto; background-color: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
            .plot-container {{ margin-bottom: 50px; background-color: #fafbfc; border: 1px solid #e1e4e8; border-radius: 6px; padding: 10px; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 40px; font-size: 14px; }}
            th, td {{ border: 1px solid #dfe2e5; padding: 10px 12px; text-align: center; }}
            th {{ background-color: #f6f8fa; font-weight: bold; color: #24292e; position: sticky; top: 0; }}
            tr:nth-child(even) {{ background-color: #f6f8fa; }}
            .table-container {{ max-height: 500px; overflow-y: auto; border: 1px solid #dfe2e5; margin-bottom: 40px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Torre de Fusión Top-Hat: Análisis Multiescala Completo</h1>
            <p>Se evaluaron todas las configuraciones posibles (36 variantes) sobre los pares de imágenes, totalizando <b>720 iteraciones</b> para demostrar categóricamente el rendimiento en modo multiescala.</p>
            
            <h2>1. Tabla Resumen (Promedios)</h2>
            <div class="table-container">
            {df_mean.to_html(index=False, classes='table')}
            </div>
            
            <h2>2. Distribución General por Elemento Estructurante</h2>
    """
    
    # 2. Generar las figuras de caja e inyectarlas al HTML
    # Boxplot general por elemento estructurante
    for m in metrics_cols:
        fig = px.box(
            df, x='Structuring_Element', y=m, color='Structuring_Element',
            title=f'Impacto Global de Forma en <b>{m}</b> (Agrupando L y r)',
            labels={'Structuring_Element': 'Geometría', m: f'Valor de {m}'},
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(height=450, margin=dict(l=40, r=40, t=50, b=40), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        
        div_str = fig.to_html(full_html=False, include_plotlyjs=False)
        html_content += f'<div class="plot-container">{div_str}</div>\n'
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"Dashboard interactivo generado exitosamente en: {html_path}")

if __name__ == '__main__':
    main()
