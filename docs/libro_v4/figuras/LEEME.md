# Figuras del libro

Esta carpeta contiene las catorce imágenes que incluye el libro. En los `.tex` se las nombra sin la extensión, por ejemplo `figuras/fig_ranking_seis`.

Salvo el logotipo, cada figura tiene un generador en `experiments/` que la escribe aquí en PNG a 300 ppp, con fondo blanco. Los generadores se ejecutan desde la raíz del repositorio, por ejemplo:

```
python experiments/make_fig_ajuste_pso_libro_v4.py
```

La tabla siguiente indica el generador de cada figura y los datos que necesita.

| Archivo | Cap. | Etiqueta | Ancho en el `.tex` | Qué muestra | Generador | Qué necesita |
|:---|:---:|:---|:---|:---|:---|:---|
| `fig_modalidades.png` | 1 | `fig:modalidades` | `\textwidth` | Una escena nocturna (Kaptein 1123) en la imagen visible, en la infrarroja y fusionada con la propuesta | `make_fig_modalidades_libro_v4.py` | `data/raw`; `r` y `m` de `all_metrics.config.json` |
| `fig_morfologia_tophat.png` | 2 | `fig:morfologia` | `0.9\textwidth` | Erosión, dilatación, apertura, cierre y las dos Top-Hat sobre una señal de una dimensión | `make_fig_morfologia_libro_v4.py` | Nada: señal sintética |
| `fig_metodologia.png` | 3 | `fig:metodologia` | `\textwidth` | Las etapas del estudio, en dos ramas: calidad de imagen y detección | `make_fig_metodologia_libro_v4.py` | Nada: textos fijos |
| `fig_banco_se.png` | 3 | `fig:banco_se` | `\textwidth` | Los cinco elementos estructurantes del banco, píxel por píxel, con `r = 5` | `make_fig_banco_se_libro_v4.py` | Nada: `disk_se` y `linear_se` de `src/fusion/optimal_top_hat.py` |
| `fig_flujo_propuesta.png` | 3 | `fig:flujo_propuesta` | `0.8\textwidth` | Diagrama de bloques del algoritmo propuesto, de las dos imágenes a la fusionada | `make_fig_flujo_propuesta_libro_v4.py` | Nada: antes de dibujar, rehace la fusión caja por caja sobre imágenes aleatorias y la compara con `fuse_optimal` |
| `fig_ajuste_pso.png` | 4 | `fig:ajuste_pso` | `\textwidth` | Aptitud según el peso `m` con `r = 1` y `r = 25`, y radio final de las 25 corridas del enjambre | `make_fig_ajuste_pso_libro_v4.py` | `optimo_exacto_fo.csv` y `pso_grid_search_fo_propuesta.csv` |
| `montaje_kaptein.png` | 4 | `fig:montaje_kaptein` | `\textwidth` | Kaptein 1123, con una persona de noche: las dos fuentes y los siete métodos | `make_montajes_libro_v4.py` | `data/raw` |
| `montaje_humo.png` | 4 | `fig:montaje_humo` | `\textwidth` | Soldado tendido tras una cortina de humo: las dos fuentes y los siete métodos | `make_montajes_libro_v4.py` | `data/raw` |
| `fig_metricas_cajas.png` | 4 | `fig:metricas_cajas` | `\textwidth` | Las seis métricas en los veinte pares, una caja por método | `make_fig_metricas_cajas_libro_v4.py` | `all_metrics.csv`, `ranking_seis_metricas.csv` y `descriptive_means_seis.csv` |
| `fig_ranking_seis.png` | 4 | `fig:ranking_seis` | `\textwidth` | Rango promedio de cada método sobre las seis métricas | `make_figuras_libro_v4.py`, sin argumentos | `ranking_seis_metricas.csv` |
| `fig_m3fd_ejemplo.png` | 4 | `fig:m3fd_ejemplo` | `\textwidth` | Detecciones del Top-Hat clásico y de la propuesta en un cuadro nocturno de M3FD (cuadro 437) | `make_fig_m3fd_ejemplo_libro_v4.py` | `m3fd_v2_predicciones.csv`, `m3fd_v2_umbrales.csv`, `m3fd_v2_prueba.csv`, `datasets/m3fd2_*` y `data/M3FD_Detection`; con `--verificar`, además los detectores de `runs/m3fd_v2` |
| `fig_m3fd_aciertos.png` | 4 | `fig:m3fd_aciertos` | `\textwidth` | Detecciones de las dos fuentes, del Top-Hat clásico y de la propuesta en dos cuadros de M3FD con un objeto de una sola cámara (cuadros 4025 y 2200) | `make_fig_m3fd_aciertos_libro_v4.py` | `m3fd_v2_predicciones.csv`, `m3fd_v2_umbrales.csv`, `m3fd_v2_prueba.csv`, `datasets/m3fd2_*` y `data/M3FD_Detection`; con `--verificar`, además los detectores de `runs/m3fd_v2` |
| `fig_deteccion_tasas.png` | 4 | `fig:deteccion_tasas` | `\textwidth` | Tasa equilibrada por semilla en las ocho entradas fusionadas y las nueve diferencias entre la propuesta y el Top-Hat clásico | `make_fig_deteccion_tasas_libro_v4.py` | `m3fd_v2_tasas_precisas.csv`, `m3fd_v2_pares_semillas.csv` y `m3fd_v2_contrastes_precisos.csv` |
| `logo_ucom.png` | Portada | | `50mm` | Logotipo de la Universidad Comunera | Ninguno | |

Los generadores están en `experiments/` y los CSV, en `experiments/results/metrics_reports/`. `data/raw` (TNO), `data/M3FD_Detection` (M3FD) y `datasets/m3fd2_*` no se publican: el README de la raíz explica cómo obtenerlos y cómo se generan (secciones 3 y 6).

## Estilo común

Todos los generadores usan `experiments/estilo_figuras_libro.py`:

- Cada figura se dibuja con el ancho al que el `.tex` la incluye (la caja de texto mide 160 mm), de modo que la letra se imprime al tamaño con que se dibuja: en general, 10 pt el texto y 9.5 pt las marcas de los ejes.
- Tipografía Times New Roman si está instalada; si no, DejaVu Serif. Una figura regenerada en un equipo sin Times New Roman cambia de tipografía.
- Fondo blanco y grises; el azul `#4472c4` marca solo a la propuesta. Sin título dentro de la imagen: el título va en el `\caption`.
- Punto decimal y rótulos en castellano. Los nombres de los métodos se leen del diccionario `CORTO` de `tools/generar_tablas_libro.py`, el mismo que usan las tablas.

Si se cambia algo de lo que dibuja un generador, hay que revisar el `\caption` y la nota de la figura en el capítulo correspondiente.

## Atribución de las imágenes

Estas figuras forman parte del libro y no están cubiertas por la licencia MIT del código (ver `LICENSE` en la raíz del repositorio).

- `fig_modalidades.png`, `montaje_kaptein.png` y `montaje_humo.png` reproducen imágenes del *TNO Image Fusion Dataset* (Toet, 2014; https://doi.org/10.6084/m9.figshare.1008029), recortadas, fusionadas y montadas. Esas imágenes siguen bajo la licencia CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), con atribución a A. Toet (TNO).
- `fig_m3fd_ejemplo.png` y `fig_m3fd_aciertos.png` reproducen cuadros de M3FD (Liu et al., 2022; https://doi.org/10.1109/CVPR52688.2022.00571) a modo de cita académica, con su referencia; sus derechos pertenecen a sus autores.
- `logo_ucom.png` es el logotipo de la Universidad Comunera y pertenece a la universidad.
