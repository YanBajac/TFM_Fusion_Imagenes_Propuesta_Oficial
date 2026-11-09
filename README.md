# Fusión de imágenes infrarrojas y visibles mediante morfología matemática

**Un operador Top-Hat de una sola escala con un banco de cinco elementos estructurantes: calidad de la fusión y aplicación a la detección de objetos**

Tesis de Maestría en Ciencia de Datos.
Facultad de Informática, Universidad Comunera (UCOM), Asunción, Paraguay, 2026.

- Autores: Lic. Juan Pablo Bazán e Ing. Yan Bajac
- Tutor: D.Sc. Julio César Mello

El repositorio reúne el libro de la tesis, en LaTeX (`docs/libro_v4`) y en PDF ([`docs/libro_v4/Tesis_Bazan_Bajac.pdf`](docs/libro_v4/Tesis_Bazan_Bajac.pdf)), el código que produce sus resultados (`src`, `experiments`, `tools`) y los CSV de los que salen las tablas, las figuras de resultados y casi todas las cifras del texto. La sección 6.6 explica cómo volver a compilar el PDF desde las fuentes.

## Índice

1. [El algoritmo propuesto](#1-el-algoritmo-propuesto)
2. [Hipótesis](#2-hipótesis)
3. [Datos](#3-datos)
4. [Resultados principales](#4-resultados-principales)
5. [Estructura del repositorio](#5-estructura-del-repositorio)
6. [Reproducción](#6-reproducción)
7. [Licencia y atribución de los datos](#7-licencia-y-atribución-de-los-datos)
8. [Cómo citar](#8-cómo-citar)

## 1. El algoritmo propuesto

La tesis propone un algoritmo de fusión de imágenes infrarrojas y visibles basado en morfología matemática. Su núcleo es un operador Top-Hat de una sola escala: todos sus elementos estructurantes comparten un mismo radio `r`. En lugar de un único elemento, emplea un banco de cinco: un disco y cuatro segmentos lineales orientados a 0°, 45°, 90° y 135°.

Con cada elemento se calculan la transformada Top-Hat blanca (WTH), que recoge los detalles claros, y la negra (BTH), que recoge los oscuros. El detalle de cada fuente es la respuesta del disco más el promedio de las respuestas de los cuatro segmentos. La regla de fusión parte del promedio de las dos fuentes, le suma el mayor detalle claro y le resta el mayor detalle oscuro, ambos multiplicados por un peso `m`, y recorta el resultado al intervalo [0, 1]:

```
F = (I_VIS + I_IR) / 2  +  m · max(WTH_VIS, WTH_IR)  −  m · max(BTH_VIS, BTH_IR)
```

El banco de cinco elementos proviene de un método de realce de mamografías (Flores et al., 2026); la forma de combinar sus respuestas, de un método de realce de imágenes de fondo de ojo (Bala et al., 2024); la regla con peso y el ajuste de sus parámetros por enjambre de partículas, de Ortega Rodríguez y Espinoza Ríos (2025), que trabajaron con un único disco.

**Ajuste de los parámetros.** El radio `r` y el peso `m` se ajustaron mediante optimización por enjambre de partículas (PSO), con el radio entre 1 y 25 píxeles y el peso entre 0.30 y 2.00. La aptitud suma la similitud estructural media con las dos fuentes, la entropía dividida por 8 y la PSNR dividida por 100, y promedia esa suma sobre tres pares del TNO. Las 25 corridas, que cruzan cinco cantidades de partículas con cinco de iteraciones, terminaron con `m = 0.30`, el límite inferior del rango; el radio quedó en 1 en dieciséis corridas, en 25 en ocho y en 14 en una. Se adoptó `r = 25` porque prioriza el realce: da más contraste y nitidez que `r = 1`, a cambio de una imagen menos fiel a las fuentes. El peso de 0.30 es un borde del rango y no un máximo interior: en una grilla de 5000 combinaciones, la aptitud fue mayor con pesos menores, con su máximo en `r = 25` y `m = 0.07`.

**Configuración adoptada: `r = 25`, `m = 0.30`.**

**Métodos de comparación.** El Top-Hat clásico, que aplica la misma regla con un único disco de radio 5 y peso 1, y cinco métodos multiescala con sus parámetros por defecto: pirámide de Laplace y pirámide de razón (cuatro niveles), DWT con base de Haar y con base db4 (tres niveles) y DTCWT (cuatro niveles). Los métodos y las métricas están implementados en Python con OpenCV, PyWavelets, dtcwt, NumPy, SciPy y scikit-image.

## 2. Hipótesis

La hipótesis del trabajo, tal como la formula el capítulo 1 del libro, es la siguiente:

> El algoritmo de fusión propuesto, con sus parámetros ajustados mediante optimización por enjambre de partículas, produce imágenes de mejor calidad que el Top-Hat clásico y de calidad comparable a la de cinco métodos multiescala, medida con seis métricas sin referencia. En su aplicación a la detección de objetos, un detector entrenado con sus imágenes encuentra más objetos vistos por una sola cámara que el entrenado con las imágenes del Top-Hat clásico.

Reúne tres afirmaciones: dos sobre la calidad (frente al Top-Hat clásico y frente a los métodos multiescala) y una sobre la aplicación a la detección. Cada una se examina con las pruebas de la evaluación que le corresponde, sin agregar otras.

## 3. Datos

Los conjuntos de datos no se redistribuyen en este repositorio. Cada uno se descarga de su fuente y se coloca en la carpeta que indica la sección 6.2. Solo cinco figuras del libro reproducen imágenes de esos conjuntos: tres del TNO y dos de M3FD (sección 7).

### 3.1 Calidad de imagen: TNO Image Fusion Dataset

La calidad se mide sobre veinte pares nocturnos visible-infrarrojo del *TNO Image Fusion Dataset*, tomados de trece escenas. Diecisiete pares son de la colección Athena y tres de la colección Triclobs. Los pares vienen registrados por sus autores. En buena parte de ellos, la imagen visible proviene de una cámara con intensificador de imagen.

- Toet, A. (2014). *TNO Image Fusion Dataset* [Conjunto de datos]. figshare. https://doi.org/10.6084/m9.figshare.1008029
- Toet, A. (2017). The TNO multiband image data collection. *Data in Brief*, 15, 249–251. https://doi.org/10.1016/j.dib.2017.09.038

El conjunto se distribuye bajo la licencia CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). El repositorio publica solo `data/raw/MANIFIESTO_CORPUS.csv`, que da, para cada uno de los 42 archivos del corpus, su nombre, su tamaño, su md5 y su ruta de origen dentro del conjunto descargado. El manifiesto declara 21 pares, uno de ellos marcado como excluido porque su imagen visible es una copia byte a byte de la infrarroja; `src/datasets.py` lo retira y el corpus efectivo queda en veinte pares.

### 3.2 Detección de objetos: M3FD

La aplicación a la detección se evalúa sobre M3FD (*Multi-scenario Multi-modality Dataset*), con 4200 pares visible-infrarrojo registrados, de día y de noche, en los que cada objeto está marcado con una caja y una de seis clases. El análisis se centra en las personas y las luces.

- Liu, J., Fan, X., Huang, Z., Wu, G., Liu, R., Zhong, W. y Luo, Z. (2022). Target-aware dual adversarial learning and a multi-scenario multi-modality benchmark to fuse infrared and visible for object detection. En *2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)* (pp. 5792–5801). IEEE. https://doi.org/10.1109/CVPR52688.2022.00571

Los enlaces de descarga de M3FD Detection están en el repositorio de sus autores: https://github.com/JinyuanLiu-CV/TarDAL. Los cuadros se repartieron por bloques de video, para que ningún cuadro de prueba tenga un vecino casi idéntico en el entrenamiento: 2000 cuadros de entrenamiento, 474 de seguimiento y una prueba final de 1067 cuadros, con 2045 personas y 864 luces, en once grupos.

### 3.3 Otros recursos externos

- **Pesos preentrenados `yolov8n.pt`** (Ultralytics), punto de partida de los treinta detectores. Se descargan antes de entrenar (sección 6.2).
- **Ortega Rodríguez, M. A. y Espinoza Ríos, G. A. (2025).** *Optimización de los parámetros de la transformada Top-Hat mediante PSO para la fusión de imágenes visibles e infrarrojas* [Trabajo final de grado inédito, Facultad Politécnica, Universidad Nacional de Asunción]. Su PDF no se redistribuye; solo lo lee `experiments/referencia_pso_ortega_espinoza.py`, que extrae sus 125 corridas del enjambre. El CSV resultante sí está publicado.
- **Una distribución de LaTeX** con pdfLaTeX y Biber (MiKTeX, TeX Live u Overleaf), para compilar el libro.

## 4. Resultados principales

Las cifras provienen de los capítulos 4 a 6 del libro y de los CSV de `experiments/results/metrics_reports`.

### 4.1 Calidad de imagen

La calidad se midió con seis métricas sin referencia: tres de actividad, que miden información, contraste y nitidez (entropía, desviación estándar y gradiente medio), y tres de fidelidad, que miden el parecido con las fuentes (información mutua, similitud estructural y relación señal-ruido de pico, PSNR). El análisis aplicó la prueba de Friedman, los contrastes de Wilcoxon con la corrección de Holm y la clasificación por rango promedio, con los veinte pares como bloques.

- **Frente al Top-Hat clásico**, la propuesta ganó en cuatro de las seis métricas (entropía, desviación estándar, información mutua y similitud estructural), perdió en gradiente medio y empató en PSNR, con un valor de p corregido de 0.674.
- **Entre los siete métodos**, obtuvo el mejor rango promedio, 3.642, frente a 3.783 de la DTCWT y 3.908 de la pirámide de Laplace. El margen sobre la DTCWT, de 0.14 puestos, es estrecho y no tiene una prueba propia. El orden depende, además, de las métricas: con las nueve métricas iniciales la propuesta quedó primera, y con diecisiete, tercera, detrás de la pirámide de Laplace y de la DTCWT.
- **Su perfil** es el de un método de realce: tuvo el mejor rango en actividad (1.717) y el sexto en fidelidad (5.567). Frente a los cinco métodos multiescala ganó catorce de los quince contrastes de actividad y perdió trece de los quince de fidelidad.
- **Solidez.** Con trece bloques, uno por escena, la propuesta siguió primera, y 65 de los 66 contrastes conservaron su decisión. En un control con versiones degradadas del promedio simple, el promedio con el ruido más intenso obtuvo el mejor valor de las catorce entradas en las tres métricas de actividad: una ventaja en actividad no prueba, por sí sola, que el detalle agregado sea útil.

### 4.2 Detección de objetos

Se entrenaron treinta detectores YOLOv8n, tres semillas por cada una de diez entradas: la imagen visible, la infrarroja, el promedio simple y las siete fusiones. La medida principal es la tasa de acierto equilibrada: el promedio del acierto sobre los objetos que solo ve la cámara visible y del acierto sobre los que solo ve la infrarroja, según los detectores entrenados con cada cámara.

- **Tasa equilibrada de la propuesta: 61.4 %**, cuarta de las ocho entradas fusionadas. La mayor fue la de la pirámide de Laplace, 66.5 %; el Top-Hat clásico quedó séptimo, con 58.4 %, y el promedio simple obtuvo 60.2 %.
- **Frente al Top-Hat clásico**, la tasa fue 3.0 puntos porcentuales mayor, con un intervalo de confianza del 95 % de 0.0 a 6.0 (error estándar robusto por grupos y distribución t), cuyo límite inferior exacto es de 0.02 puntos.
- **Es una ventaja mínima**: según el par de semillas, la diferencia fue de −3.1 a 7.8 puntos y cambió de signo, y el *bootstrap* salvaje por grupos, estudentizado y con la hipótesis nula impuesta, no excluyó el cero (p = 0.17, intervalo de −3.5 a 5.5). Queda, por eso, como un **hallazgo por confirmar** con más grupos, más semillas y otros detectores.
- Aunque se confirmara, la ventaja no podría atribuirse al banco por sí solo, porque entre los dos métodos cambian a la vez los elementos estructurantes, el radio y el peso. Frente al promedio simple, la diferencia fue de 1.2 puntos, con un intervalo de −6.6 a 9.0.
- No se halló una relación significativa entre el puesto de cada método en calidad y su tasa equilibrada (Spearman, ρ = −0.32, p = 0.48).

### 4.3 Lectura de conjunto

En calidad, la hipótesis se sostiene en lo principal: la propuesta supera al Top-Hat clásico en cuatro de las seis métricas y se ubica entre los métodos multiescala con un perfil propio, que privilegia el realce sobre la fidelidad. En detección, la ventaja frente al Top-Hat clásico queda por confirmar con nuevos entrenamientos y datos.

Alcance: los métodos comparativos se usaron con sus parámetros por defecto, mientras que el radio de la propuesta se eligió sobre los mismos veinte pares con que se evaluó la calidad; los objetos de una sola cámara los definen detectores y no una revisión humana, y la prueba de detección tiene pocos grupos independientes.

## 5. Estructura del repositorio

```
.
├── README.md
├── LICENSE
├── CITATION.cff
├── .gitignore
├── .python-version                  versión de Python del entorno (3.11)
├── requirements.txt                 dependencias de la evaluación de calidad (CPU)
├── requirements-deteccion.txt       torch, torchvision y ultralytics, para la detección (GPU)
├── requirements-lock.txt            versiones exactas del entorno en que se calcularon los resultados
├── reparar_torch_gpu.ps1            reinstala PyTorch con CUDA en Windows
│
├── data/raw/MANIFIESTO_CORPUS.csv   nombre, tamaño, md5 y origen de los 42 archivos del TNO
│
├── src/                             biblioteca
│   ├── datasets.py                  lista y carga los pares de data/raw; retira el par excluido
│   ├── fusion/optimal_top_hat.py    el algoritmo propuesto (fuse_optimal)
│   ├── fusion/comparatives.py       Top-Hat clásico y los cinco métodos multiescala
│   ├── metrics/evaluators.py        métricas sin referencia (evaluate_all)
│   └── utils/                       lectura, escritura y visualización
│
├── experiments/
│   ├── preparar_corpus.py           arma data/raw a partir del TNO descargado
│   ├── verificar_corpus.py          comprueba data/raw contra el manifiesto
│   ├── comprobar_entorno.py         comprueba el intérprete, los paquetes y el corpus
│   ├── perfil_entorno.py            registra el equipo y las versiones (entorno.csv)
│   ├── run_*.py                     fusiones, métricas y análisis estadístico de la calidad
│   ├── ranking_17_metricas.py       rango promedio con las diecisiete métricas
│   ├── control_ocho_entradas.py     control con solo los siete métodos y el promedio simple
│   ├── pso_*.py, analizar_repeticiones.py, optimo_exacto_fo.py, barrido_metricas_vs_m.py,
│   │   referencia_pso_ortega_espinoza.py
│   │                                ajuste de r y m por enjambre de partículas
│   ├── make_*_libro_v4.py           generadores de las figuras del libro
│   ├── estilo_figuras_libro.py      estilo común de las figuras
│   ├── detection_m3fd/              partición, entrenamiento, evaluación y análisis de la detección
│   └── results/
│       ├── metrics_reports/         CSV de resultados (ver la tabla siguiente)
│       └── pso/                     estado reanudable de las corridas del enjambre
│
├── tools/
│   ├── generar_tablas_libro.py      escribe las tablas del libro desde los CSV
│   ├── verificar_libro_v4.py        revisa citas, referencias cruzadas, inclusiones e imágenes del libro
│   ├── compilar_libro_local.py      compila el libro con pdfLaTeX y Biber
│   └── empaquetar_overleaf.py       arma el .zip del libro para Overleaf
│
└── docs/libro_v4/                   el libro en LaTeX (ver docs/libro_v4/LEEME.md)
    ├── Tesis_Bazan_Bajac.pdf        el libro compilado
    ├── main.tex
    ├── referencias.bib
    ├── caps/                        resumen, abstract, agradecimientos, siglas, capítulos 1 a 7 y anexos
    ├── tablas/                      tablas generadas por tools/generar_tablas_libro.py
    └── figuras/                     figuras del libro (ver docs/libro_v4/figuras/LEEME.md)
```

### 5.1 Resultados publicados

Los CSV de `experiments/results/metrics_reports/` son los de la corrida que informa el libro. Al volver a ejecutar un script se sobrescriben, y `git diff` muestra si algo cambió.

| Archivo | Contenido | Lo escribe |
|:---|:---|:---|
| `all_metrics.csv`, `all_metrics.config.json` | Las diecisiete métricas de cada método en cada par, y la configuración con que se calcularon | `run_all_fusions.py` |
| `descriptive_means_seis.csv`, `ranking_seis_metricas.csv`, `friedman_seis_metricas.csv`, `wilcoxon_seis_metricas.csv` | Medias, rango promedio, prueba de Friedman y contrastes de Wilcoxon con Holm, con las seis métricas | `run_stats_seis_metricas.py` |
| `control_negativo.csv`, `control_negativo_seis_metricas.csv` | Control con el promedio simple, con ruido y desenfocado, junto con los siete métodos | `run_control_negativo.py`; `run_stats_seis_metricas.py` |
| `control_ocho_entradas.csv` | El mismo control con solo los siete métodos y el promedio simple, en una escala de 1 a 8 | `control_ocho_entradas.py` |
| `ranking_methods.csv` | Rango promedio con las nueve métricas iniciales | `run_stats_analysis.py` |
| `ranking_17_metricas.csv` | Rango promedio con las diecisiete métricas de `all_metrics.csv` | `ranking_17_metricas.py` |
| `escenas_distintas.csv` | Escena a la que pertenece cada par (trece escenas) | `run_escenas_distintas.py` |
| `sensibilidad_escenas_ranking.csv`, `sensibilidad_escenas_friedman.csv`, `sensibilidad_escenas_wilcoxon.csv` | El análisis de seis métricas con un bloque por escena | `run_sensibilidad_escenas.py` |
| `pso_grid_search_fo_propuesta.csv` | Las 25 corridas del enjambre | `pso_grid_search_fo.py --operator propuesta` |
| `pso_repeticiones_propuesta.csv`, `pso_repeticiones_resumen_propuesta.csv` | Las 500 corridas de control (veinte repeticiones de cada configuración) y su resumen | `pso_repeticiones.py`; `analizar_repeticiones.py` |
| `optimo_exacto_fo.csv` | La aptitud en la grilla de 25 radios por 200 pesos | `optimo_exacto_fo.py --paso 0.01` |
| `ajuste_comparativos.csv` | Métricas por par con distintas configuraciones de cada método; de ahí sale la comparación de `r = 1` con `r = 25` | `run_ajuste_comparativos.py` |
| `barrido_metricas_vs_m.csv` | Métricas en función del peso, en las tres escenas del ajuste | `barrido_metricas_vs_m.py` |
| `referencia_pso_ortega_espinoza.csv` | Las 125 corridas que informan Ortega Rodríguez y Espinoza Ríos (2025) | `referencia_pso_ortega_espinoza.py` |
| `entorno.csv` | Equipo y versiones de los programas | `perfil_entorno.py` |
| `m3fd_v2_particion.csv`, `m3fd_v2_prueba.csv` | Partición de M3FD por bloques y prueba final con sus grupos | `detection_m3fd/particion_tramos_v2.py`; `detection_m3fd/prueba_v2.py` |
| `m3fd_v2_entrenamientos.csv` | Registro de los treinta entrenamientos | `detection_m3fd/entrenar_v2.py` |
| `m3fd_v2_map.csv`, `m3fd_v2_predicciones.csv` | mAP50 por detector y todas sus predicciones de personas y luces | `detection_m3fd/evaluar_v2.py` |
| `m3fd_v2_umbrales.csv`, `m3fd_v2_tasas.csv`, `m3fd_v2_contrastes.csv`, `m3fd_v2_pares_semillas.csv`, `m3fd_v2_convergencia.csv` | Umbrales calibrados, tasas de acierto, contrastes con el intervalo por grupos y la distribución t, diferencias por par de semillas y seguimiento por épocas. Las columnas `wild_lo`, `wild_hi`, `cota`, `desenlace` y `desenlace_wild` de `m3fd_v2_contrastes.csv` y de `m3fd_v2_contrastes_precisos.csv` son auxiliares y el libro no las usa: el *bootstrap* salvaje del libro está en `m3fd_v2_bootstrap_estudentizado.csv` | `detection_m3fd/analizar_v2.py` |
| `m3fd_v2_tasas_precisas.csv`, `m3fd_v2_contrastes_precisos.csv` | Las mismas tasas y contrastes sin redondear | `detection_m3fd/tasas_precisas_v2.py` |
| `m3fd_v2_bootstrap_estudentizado.csv` | *Bootstrap* salvaje por grupos, estudentizado y con la nula impuesta | `detection_m3fd/bootstrap_estudentizado_v2.py` |
| `m3fd_v2_reparto_grupos.csv`, `m3fd_v2_dejar_un_grupo.csv` | Reparto de los objetos de una sola cámara entre los grupos de la prueba, y diferencia entre la propuesta y el Top-Hat clásico al dejar fuera un grupo por vez | `detection_m3fd/reparto_grupos_v2.py` |
| `m3fd_v2_map_resumen.csv`, `m3fd_v2_calidad_deteccion.csv` | mAP50 por entrada y correlación entre calidad y detección | `detection_m3fd/secundarias_v2.py` |

Los scripts están en `experiments/`. Algunos escriben, además, archivos auxiliares que el libro no usa.

Unas pocas cifras del texto no tienen CSV propio: las resoluciones de los pares del TNO y la parte del lado menor de cada imagen que cubre el disco de radio 25 se leen de las imágenes de `data/raw`. Con el corpus armado, este comando imprime si la visible y la infrarroja de cada par tienen el mismo tamaño, las resoluciones con su número de pares y la parte del lado menor que cubre el disco:

```
python -c "from collections import Counter; from src.datasets import list_pairs, load_pair; t=[tuple(x.shape for x in load_pair(*p)) for p in list_pairs()]; print(all(a==b for a,b in t)); c=Counter(f'{a[1]}x{a[0]}' for a,b in t); print(len(c), c.most_common()); print(f'{100*51/max(min(a) for a,b in t):.1f} a {100*51/min(min(a) for a,b in t):.1f} %')"
```

### 5.2 Nombres de los métodos en el código

Los CSV y el código usan nombres internos. Su equivalencia con los del libro es la siguiente:

| En el código y los CSV | En el libro |
|:---|:---|
| `Propuesta_Novedosa` | Propuesta |
| `TopHat_Clasico` | Top-Hat clásico |
| `PiramideLaplace` | Pirámide de Laplace |
| `RatioPiramide` | Pirámide de razón |
| `DWT` | DWT (Haar) |
| `Curvelet` | DWT (db4); es una DWT con base de Daubechies de orden cuatro, no la transformada curvelet |
| `DTCWT` | DTCWT |
| `Promedio`; `base` en `control_negativo.csv` y `control_ocho_entradas.csv` | Promedio simple |
| `VIS`, `IR` | Visible sola, infrarroja sola |

## 6. Reproducción

Todos los comandos se ejecutan desde la raíz del repositorio. En Windows conviene fijar antes la variable `PYTHONUTF8=1` (en PowerShell, `$env:PYTHONUTF8 = "1"`), para que la consola acepte los caracteres de los mensajes.

### 6.1 Entorno

Python 3.11. La evaluación de calidad y el ajuste corren en el procesador:

```
git clone https://github.com/YanBajac/TFM_Fusion_Imagenes_Propuesta_Oficial.git
cd TFM_Fusion_Imagenes_Propuesta_Oficial
python -m venv .venv
.venv\Scripts\Activate.ps1            # Linux o macOS: source .venv/bin/activate
pip install -r requirements.txt
python experiments/comprobar_entorno.py
```

Si PowerShell no deja ejecutar `Activate.ps1`, se habilita solo para esa consola con `Set-ExecutionPolicy -Scope Process Bypass` y se repite la activación. `comprobar_entorno.py` revisa el intérprete, los paquetes y el corpus. Mientras `data/raw` esté vacío, marca una falla en el apartado «corpus» y termina con código 1; esa falla desaparece al armar el corpus (sección 6.2), y las comprobaciones del intérprete y de los paquetes valen igual.

La detección necesita, además, una GPU con CUDA. En Windows, PyPI publica PyTorch solo para el procesador, y con `--extra-index-url` pip elige la versión más nueva de los dos índices, que es la de PyPI. Por eso PyTorch se instala primero desde su propio índice, con las versiones del entorno original, y después el resto:

```
pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements-deteccion.txt
python experiments/comprobar_entorno.py --deteccion
```

Si PyTorch quedó instalado sin CUDA, `reparar_torch_gpu.ps1` reinstala la rueda correcta en Windows (`powershell -ExecutionPolicy Bypass -File .\reparar_torch_gpu.ps1`).

Para repetir el cálculo con las versiones exactas del entorno original (Windows 11, Python 3.11 y CUDA 12.1; el archivo fija paquetes que solo existen en Windows, como `pywinpty`):

```
pip install --no-deps -r requirements-lock.txt --extra-index-url https://download.pytorch.org/whl/cu121
```

El encabezado de `requirements-lock.txt` explica por qué los dos parámetros son necesarios. `entorno.csv` anota el sistema como «Windows 10» porque Python 3.11 informa así la compilación 10.0.26200, que es de Windows 11.

### 6.2 Datos

**TNO.** Descargar y descomprimir el conjunto de figshare (sección 3.1) y armar `data/raw` a partir del manifiesto:

```
python experiments/preparar_corpus.py --tno <carpeta del TNO descomprimido>
python experiments/verificar_corpus.py
```

`preparar_corpus.py` busca cada archivo por su ruta de origen y, si no la encuentra, por su md5; dos archivos del par Triclobs_Kaptein_1123 se convierten a escala de grises de 8 bits antes de compararlos. Con `--simular` informa lo que haría sin escribir nada. `verificar_corpus.py` comprueba que estén los 42 archivos con su md5, que no sobre ninguno, que ningún par del corpus efectivo tenga la imagen visible igual a la infrarroja (el par excluido la tiene, y por eso se lo retira) y que queden los veinte pares efectivos.

**M3FD.** Descomprimir M3FD Detection (sección 3.2) en `data/M3FD_Detection`, con sus carpetas `Vis`, `Ir` y `Annotation`.

**Pesos de YOLOv8n.** Hay que descargarlos antes de entrenar: `experiments/detection_m3fd/entrenar_v2.py` exige el archivo `yolov8n.pt` en la raíz del repositorio y se detiene si no está. Con Ultralytics instalado, este comando lo descarga en la carpeta de trabajo, que tiene que ser la raíz:

```
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

Si Ultralytics ya lo tenía guardado en su propia carpeta de pesos, puede cargarlo desde allí sin copiarlo; en ese caso se copia a mano, o se baja de los *releases* de https://github.com/ultralytics/assets.

### 6.3 Calidad de imagen y ajuste de los parámetros

En este orden, porque cada paso lee lo que escribe el anterior:

```
python experiments/run_all_fusions.py --rehacer        # siete métodos en los veinte pares -> all_metrics.csv
python experiments/run_control_negativo.py             # control con el promedio simple degradado -> control_negativo.csv
python experiments/run_stats_seis_metricas.py          # medias, Friedman, Wilcoxon con Holm y rango promedio, seis métricas
python experiments/run_stats_analysis.py               # rango promedio con las nueve métricas iniciales
python experiments/ranking_17_metricas.py              # rango promedio con las diecisiete métricas
python experiments/control_ocho_entradas.py            # el control con solo los siete métodos y el promedio simple
python experiments/run_escenas_distintas.py            # escena de cada par
python experiments/run_sensibilidad_escenas.py         # el análisis con un bloque por escena
```

`run_all_fusions.py` guarda también las imágenes fusionadas en `experiments/results/fused_images/`, que no se publican. Sin `--rehacer` reanuda desde `all_metrics.csv`: con el CSV publicado y la misma configuración, no recalcula nada. `ranking_17_metricas.py` y `control_ocho_entradas.py` solo leen CSV publicados: el primero, `all_metrics.csv`, y el segundo, además, `control_negativo.csv`.

El ajuste por enjambre y sus comprobaciones:

```
python experiments/pso_grid_search_fo.py --operator propuesta       # las 25 corridas del enjambre
python experiments/pso_repeticiones.py --operator propuesta         # 500 corridas: veinte repeticiones de cada configuración
python experiments/analizar_repeticiones.py                         # resumen de las 500 corridas
python experiments/optimo_exacto_fo.py --paso 0.01                  # grilla de 5000 combinaciones de radio y peso
python experiments/run_ajuste_comparativos.py                       # incluye la comparación de r = 1 con r = 25 en los veinte pares
python experiments/barrido_metricas_vs_m.py                         # métricas en función del peso
python experiments/referencia_pso_ortega_espinoza.py                # requiere el PDF de la obra de referencia
python experiments/perfil_entorno.py                                # equipo y versiones -> entorno.csv
```

Los dos primeros son reanudables y guardan su estado en `experiments/results/pso/`. `pso_grid_search_fo.py` se detiene al agotar su presupuesto de tiempo (`--budget`, 5400 segundos por omisión) y continúa donde quedó en la ejecución siguiente. Con los archivos de estado publicados, una nueva ejecución no repite las corridas: reescribe el CSV a partir del estado. Para repetirlas desde cero se retira antes el archivo de estado correspondiente. La primera repetición de `pso_repeticiones.py` reproduce el barrido de 25 corridas, y el script lo comprueba.

`referencia_pso_ortega_espinoza.py` lee el PDF de Ortega Rodríguez y Espinoza Ríos (2025), que no se distribuye. Por omisión lo busca en `docs/fuentes/ortega_espinoza_2025.pdf`; con `--pdf` se indica otra ruta.

### 6.4 Detección de objetos

Los scripts están en `experiments/detection_m3fd/`:

```
python experiments/detection_m3fd/particion_tramos_v2.py      # partición de M3FD por bloques de cuadros
python experiments/detection_m3fd/prueba_v2.py                # prueba final, filtros de casi duplicados y grupos
python experiments/detection_m3fd/preparar_v2.py              # un conjunto de imágenes por entrada -> datasets/m3fd2_*
python experiments/detection_m3fd/entrenar_v2.py              # treinta detectores, 40 épocas cada uno (GPU) -> runs/m3fd_v2
python experiments/detection_m3fd/evaluar_v2.py 0             # mAP50 y predicciones; el argumento 0 usa la GPU
python experiments/detection_m3fd/analizar_v2.py              # umbrales, objetos de una sola cámara, tasas y contrastes
python experiments/detection_m3fd/secundarias_v2.py           # mAP50 por entrada y relación con la calidad
python experiments/detection_m3fd/tasas_precisas_v2.py        # tasas y contrastes sin redondear
python experiments/detection_m3fd/bootstrap_estudentizado_v2.py
python experiments/detection_m3fd/reparto_grupos_v2.py        # reparto por grupos y diferencia al dejar fuera un grupo por vez
```

`preparar_v2.py` usa como biblioteca `prepare_m3fd.py` (fusión, conversión a escala de grises y paso de las anotaciones al formato de YOLO). `datasets/` y `runs/` son productos intermedios pesados que no se publican. Los treinta entrenamientos tomaron unas siete horas en una NVIDIA GeForce RTX 4050 de portátil (`m3fd_v2_entrenamientos.csv`).

`entrenar_v2.py` y `evaluar_v2.py` son reanudables. `entrenar_v2.py` salta los detectores que ya tienen sus 40 épocas en `runs/m3fd_v2` y agrega una fila por entrenamiento a `m3fd_v2_entrenamientos.csv`. `evaluar_v2.py` da por evaluado todo detector que ya figure en `m3fd_v2_map.csv` y en `m3fd_v2_predicciones.csv`: con los CSV publicados no evalúa nada, y para evaluar de nuevo se retiran antes esos dos archivos. Sin argumento, `evaluar_v2.py` corre en el procesador.

`analizar_v2.py`, `tasas_precisas_v2.py`, `bootstrap_estudentizado_v2.py` y `reparto_grupos_v2.py` (los tres últimos repiten el análisis de `analizar_v2.py` en una carpeta temporal) leen, además de los CSV, las etiquetas y las imágenes de `datasets/m3fd2_VIS` (partes `sobrante`, `val` y `test`, que escribe `preparar_v2.py`): no se pueden rehacer solo con los CSV publicados, y sin esa carpeta se detienen con un `ZeroDivisionError`. `analizar_v2.py` lee además `runs/m3fd_v2/<entrada>_s<semilla>/results.csv` para `m3fd_v2_convergencia.csv`; si falta `runs/`, reescribe ese CSV vacío, y el publicado se recupera con `git checkout`. `secundarias_v2.py` lee también `ranking_seis_metricas.csv`, de la evaluación de calidad.

### 6.5 Tablas y figuras del libro

Las siete tablas de `docs/libro_v4/tablas/` se escriben desde los CSV:

```
python tools/generar_tablas_libro.py
```

Cada figura de `docs/libro_v4/figuras/`, salvo el logotipo, tiene su generador en `experiments/`, que la escribe en esa carpeta a 300 ppp. La lista completa, con los datos que necesita cada una, está en `docs/libro_v4/figuras/LEEME.md`. Las que salen solo de los CSV publicados son estas:

```
python experiments/make_fig_ajuste_pso_libro_v4.py
python experiments/make_fig_metricas_cajas_libro_v4.py
python experiments/make_figuras_libro_v4.py
python experiments/make_fig_deteccion_tasas_libro_v4.py
```

Los diagramas no necesitan datos (`make_fig_morfologia_libro_v4.py`, `make_fig_metodologia_libro_v4.py`, `make_fig_banco_se_libro_v4.py`, `make_fig_flujo_propuesta_libro_v4.py`). `make_fig_modalidades_libro_v4.py` y `make_montajes_libro_v4.py` necesitan `data/raw`, y `make_fig_m3fd_ejemplo_libro_v4.py` y `make_fig_m3fd_aciertos_libro_v4.py` necesitan `data/M3FD_Detection` y `datasets/m3fd2_*`.

### 6.6 Compilación del libro

El PDF publicado, `docs/libro_v4/Tesis_Bazan_Bajac.pdf`, es el resultado de compilar las fuentes de `docs/libro_v4`. El libro se compila con pdfLaTeX y Biber (`biblatex` con el estilo `apa`), y la compilación produce `main.pdf`. Hay tres caminos:

- Con una distribución local, desde `docs/libro_v4`: `latexmk -pdf main.tex`, o bien `pdflatex main`, `biber main` y dos pasadas más de `pdflatex main`.
- Con `python tools/compilar_libro_local.py`, que copia el libro a una carpeta aparte, excluida por el `.gitignore`, y compila allí para no dejar archivos auxiliares junto a las fuentes; informa los errores, las referencias sin definir y los renglones desbordados, e imprime la ruta del PDF. Necesita `pdflatex` y `biber` en el PATH.
- En Overleaf: `python tools/empaquetar_overleaf.py` comprueba el preámbulo, las inclusiones y las imágenes, y arma `docs/libro_v4_overleaf.zip`, que se sube con *New Project > Upload Project*. El compilador es pdfLaTeX y la bibliografía usa Biber.

Antes de compilar, `python tools/verificar_libro_v4.py` comprueba que cada cita tenga su entrada en `referencias.bib`, que cada referencia cruzada apunte a una etiqueta existente y que cada archivo incluido y cada imagen existan. Más detalles en `docs/libro_v4/LEEME.md`.

### 6.7 Uso del algoritmo desde Python

```python
from src.datasets import list_pairs, load_pair
from src.fusion import fuse_optimal, tophat_classic_fusion
from src.metrics import evaluate_all

vis, ir = load_pair(*list_pairs()[0])                 # escala de grises, valores en [0, 1]
f = fuse_optimal(vis, ir, r=25, m=0.30, mode="sum")   # la propuesta, en la configuración adoptada
f_clasico = tophat_classic_fusion(vis, ir, r=5, m=1.0)

m = evaluate_all(f, vis, ir)                          # diecisiete métricas
mi = (m["MI_vis"] + m["MI_ir"]) / 2                   # la información mutua del libro
seis = {"EN": m["EN"], "SD": m["SD"], "MG": m["MG"], "MI": mi, "SSIM": m["SSIM"], "PSNR": m["PSNR"]}
```

## 7. Licencia y atribución de los datos

El código y los resultados se distribuyen bajo la licencia MIT: `src/`, `experiments/` (con los CSV y JSON de `experiments/results/`), `tools/`, `data/raw/MANIFIESTO_CORPUS.csv` y los archivos de la raíz. El texto de la licencia y su alcance están en [LICENSE](LICENSE).

No están cubiertos por esa licencia:

- **El libro**: las fuentes de `docs/libro_v4` (texto, tablas, bibliografía y figuras) y su PDF, `docs/libro_v4/Tesis_Bazan_Bajac.pdf`. Se publica para que los resultados sean verificables, con todos los derechos reservados por sus autores. Puede citarse; su texto no se reutiliza sin permiso.
- **Las imágenes del TNO.** El conjunto no se redistribuye. Las figuras `fig_modalidades.png`, `montaje_kaptein.png` y `montaje_humo.png` reproducen imágenes del *TNO Image Fusion Dataset* (Toet, 2014), recortadas, fusionadas y montadas. Esas imágenes siguen bajo la licencia CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), con atribución a A. Toet (TNO).
- **Las imágenes de M3FD.** El conjunto no se redistribuye. Las figuras `fig_m3fd_ejemplo.png` y `fig_m3fd_aciertos.png` reproducen cuadros de M3FD (Liu et al., 2022) a modo de cita académica, con su referencia; sus derechos pertenecen a sus autores.
- **El logotipo de la Universidad Comunera** (`docs/libro_v4/figuras/logo_ucom.png`), que pertenece a la universidad.
- **Las cifras de Ortega Rodríguez y Espinoza Ríos (2025)** que transcribe `referencia_pso_ortega_espinoza.csv`: son resultados de su trabajo final de grado inédito y se citan como tales.
- **Los recursos externos de la sección 3.3**, que se obtienen aparte con sus propias licencias.

## 8. Cómo citar

Los metadatos están en [CITATION.cff](CITATION.cff).

> Bazán, J. P. y Bajac, Y. (2026). *Fusión de imágenes infrarrojas y visibles mediante morfología matemática* [Tesis de maestría, Universidad Comunera]. https://github.com/YanBajac/TFM_Fusion_Imagenes_Propuesta_Oficial

```bibtex
@mastersthesis{bazan_bajac_2026,
  author  = {Bazán, Juan Pablo and Bajac, Yan},
  title   = {Fusión de imágenes infrarrojas y visibles mediante morfología matemática},
  school  = {Facultad de Informática, Universidad Comunera},
  address = {Asunción, Paraguay},
  type    = {Tesis de Maestría en Ciencia de Datos},
  year    = {2026},
  url     = {https://github.com/YanBajac/TFM_Fusion_Imagenes_Propuesta_Oficial}
}
```

Quien use los datos cita además sus fuentes: el *TNO Image Fusion Dataset* (Toet, 2014; Toet, 2017) y M3FD (Liu et al., 2022), con las referencias de la sección 3.
