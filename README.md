# Fusión de Imágenes Infrarrojas y Visibles mediante Morfología Matemática

> **Tesis de Maestría en Ciencias de Datos**
> Universidad Comunera (UCOM)
> Autores: Lic. Juan Pablo Bazán, Ing. Yan Bajac
> Director: D.Sc. Julio César Mello

> **Propuesta central (definitiva):** una **fusión morfológica multiescala** VIS/IR basada en
> transformadas Top-Hat que, en cada escala, **promedia** las respuestas de cuatro elementos
> estructurantes **lineales** (0°, 45°, 90°, 135°) y toma el **máximo** frente a la respuesta de un
> **disco**; agrega las escalas por **máximo por píxel** (sin cascada) y reconstruye con el esquema
> aditivo-sustractivo de Bala et al. (2024), con un peso de contraste `m`. Los hiperparámetros `(n, m)`
> se ajustan por **enjambre de partículas (PSO)**. Se compara con una variante preliminar en cascada,
> con la Torre Top-Hat (método anterior) y con baselines clásicos sobre el **TNO Image Fusion Dataset**
> (20 pares) usando **16 métricas sin referencia**, y se evalúa su impacto en **detección de objetos**
> entrenando YOLOv8 sobre el dataset etiquetado **LLVIP** (mAP).

---

## Índice

1. [Descripción del problema](#1-descripción-del-problema)
2. [Marco teórico](#2-marco-teórico)
   - [Fusión de imágenes multimodal](#21-fusión-de-imágenes-multimodal)
   - [Morfología matemática](#22-morfología-matemática)
   - [Transformada Top-Hat](#23-transformada-top-hat)
   - [Propuesta novedosa: fusión multiescala (método central)](#24-propuesta-novedosa-fusión-multiescala-método-central)
   - [Variante preliminar en cascada y Torre Top-Hat](#25-variante-preliminar-en-cascada-y-torre-top-hat)
   - [Algoritmos de referencia (baselines)](#26-algoritmos-de-referencia-baselines)
   - [Métricas de evaluación](#27-métricas-de-evaluación)
3. [Resultados principales](#3-resultados-principales)
4. [Estructura del proyecto](#4-estructura-del-proyecto)
5. [Instalación](#5-instalación)
6. [Uso rápido](#6-uso-rápido)
7. [Ejecución de experimentos](#7-ejecución-de-experimentos)
8. [Evaluación orientada a tarea (detección LLVIP)](#8-evaluación-orientada-a-tarea-detección-llvip)
9. [Notebooks de análisis](#9-notebooks-de-análisis)
10. [Dependencias](#10-dependencias)
11. [Referencias](#11-referencias)

---

## 1. Descripción del problema

Las cámaras **visibles (VIS)** capturan la reflectancia de la luz, ofreciendo alta resolución textural
y de color pero siendo sensibles a condiciones de iluminación adversas (noche, niebla, humo). Las
cámaras **infrarrojas (IR)** detectan la radiación térmica emitida por los objetos, siendo robustas a
la oscuridad pero con menor resolución espacial y detalle de textura.

La **fusión de imágenes** VIS+IR busca generar una única imagen que combine las fortalezas de ambas
modalidades, mejorando la percepción para vigilancia y seguridad perimetral, detección de personas en
visibilidad reducida, guía de vehículos autónomos e inspección industrial y médica.

Esta tesis propone y evalúa una **fusión morfológica multiescala** (la *Propuesta Novedosa*), la
contrasta estadísticamente con una variante preliminar, con un método anterior y con baselines
clásicos, y mide su efecto sobre una tarea de detección de objetos con un dataset etiquetado.

---

## 2. Marco teórico

### 2.1 Fusión de imágenes multimodal

La fusión combina información complementaria de dos o más sensores para obtener una representación más
completa de una escena. El esquema general opera en tres etapas: **preprocesamiento** (registro,
normalización), **fusión en dominio transformado** (descomposición multiescala, regla de fusión por
capa y reconstrucción) y **evaluación** mediante métricas sin referencia. La revisión de Singh et al.
(2023) sitúa los métodos morfológicos dentro de la taxonomía de técnicas de fusión y motiva el uso de
métricas sin referencia (PLIF) cuando no existe imagen ideal de referencia.

### 2.2 Morfología matemática

Marco algebraico para el análisis de estructuras geométricas en imágenes. Sus operaciones
fundamentales (escala de grises, elemento estructurante `b`):

| Operación | Definición | Efecto visual |
|-----------|-----------|---------------|
| **Dilatación** `δ(f,b)` | máximo local bajo `b` | engruesa estructuras claras, rellena valles |
| **Erosión** `ε(f,b)` | mínimo local bajo `b` | adelgaza estructuras, elimina picos |
| **Apertura** `γ(f,b) = δ(ε(f,b),b)` | erosión seguida de dilatación | elimina objetos claros menores que `b` |
| **Cierre** `φ(f,b) = ε(δ(f,b),b)` | dilatación seguida de erosión | rellena huecos oscuros menores que `b` |

### 2.3 Transformada Top-Hat

- **White Top-Hat (WTH):** `WTH(f,b) = f − γ(f,b)` → resalta estructuras brillantes menores que `b`.
- **Black Top-Hat (BTH):** `BTH(f,b) = φ(f,b) − f` → resalta estructuras oscuras menores que `b`.

El **tipo de SE** (disco, línea, …) determina qué orientaciones de detalle se enfatizan y el **diámetro**
controla la escala.

### 2.4 Propuesta novedosa: fusión multiescala (método central)

Adapta a la fusión VIS/IR el realce multiescala de Román et al. (2024) y la reconstrucción
aditiva-sustractiva con promedio multidireccional de Bala et al. (2024), optimizando la fusión
ponderada por PSO al estilo de Ortega y Espinoza (2025).

1. **Operador por escala.** En cada escala `i` (SE de diámetro `d_i = 2i+1`) se **promedian** las cuatro
   respuestas lineales y se toma el **máximo por píxel** frente a la respuesta del disco:

   ```
   WTH_líneas = (1/4)·Σθ [ f − γ(f, b_θ) ]          (θ = 0°, 45°, 90°, 135°)
   WTH_i      = máx( WTH_líneas , WTH_disco )        (idéntico para BTH_i)
   ```

   El promedio angular atenúa el ruido direccional; el máximo frente al disco preserva por igual
   estructuras orientadas e isótropas. *(Esta combinación es la aportación propia.)*

2. **Agregación multiescala por máximo** (sin diferencias en cascada):

   ```
   WTH_M = máx_{i=1..n} WTH_i        BTH_M = máx_{i=1..n} BTH_i
   ```

3. **Combinación entre fuentes y reconstrucción** sobre `I_base = (VIS + IR)/2`:

   ```
   WTH_M = máx(WTH_M^VIS, WTH_M^IR)      BTH_M = máx(BTH_M^VIS, BTH_M^IR)
   F     = I_base + m·WTH_M − m·BTH_M
   ```

4. **Optimización por PSO.** Los hiperparámetros `(n, m)` se ajustan con enjambre de partículas
   (20 partículas × 20 iteraciones) maximizando una aptitud orientada a fusión
   `F = SSIM + Qabf + 0.5·SCD − Nabf`. **Óptimo hallado:** `n = 8`, `m = 0.12`.

Implementación: `src/fusion/novel_fusion.py` (`NovelMultiscaleFusion`); PSO en
`experiments/pso_novel.py`.

### 2.5 Variante preliminar en cascada y Torre Top-Hat

- **Variante multiescala en cascada** (preliminar / ablación): combina los cinco SE por **máximo** y
  añade **diferencias en cascada** entre escalas (ecuaciones 15–21 de Román et al.), con `(n, r, m)`
  optimizados por PSO (`n=6`, `r≈2.89`, `m=0.10`). Implementación:
  `src/fusion/optimal_top_hat.py` (`OptimalMultiscaleFusion`).
- **Torre Top-Hat** (método anterior): descomposición iterativa con un **único disco por escala** y
  reglas de selección manuales; fusión de detalle por máxima actividad local y base por promedio.
  Implementación: `src/fusion/prop_top_hat.py` (`TopHatFusion`).

### 2.6 Algoritmos de referencia (baselines)

| Método | Descripción | Referencia |
|--------|-------------|------------|
| **Promedio** | `F = 0.5·VIS + 0.5·IR` — cota inferior de complejidad | — |
| **Pirámide de Laplace** | Descomposición Gaussiana-Laplaciana (4 niveles); fusión por máxima actividad | Burt y Adelson (1983) |
| **Curvelet (vía wavelet 2D)** | Subbandas direccionales (db4, 3 niveles); máxima magnitud en detalle | Candès et al. (2006) |

### 2.7 Métricas de evaluación

Evaluación con **16 métricas sin referencia**: seis clásicas de actividad/información, seis estándar de
calidad de fusión y cuatro adicionales tomadas de la revisión de Singh et al. (2023).

| Símbolo | Nombre | Dirección |
|---------|--------|-----------|
| **EN** | Entropía de Shannon | ↑ |
| **SD** | Desviación estándar (contraste) | ↑ |
| **FE** | Eficiencia de fusión | ↑ |
| **MG** | Gradiente medio | ↑ |
| **MI_vis / MI_ir** | Información mutua con cada fuente | ↑ |
| **SF** | Frecuencia espacial | ↑ |
| **Qabf** | Preservación de bordes (Xydeas-Petrović) | ↑ |
| **Nabf** | Ruido/artefactos añadidos por la fusión | ↓ |
| **SSIM** | Similitud estructural con las fuentes | ↑ |
| **SCD** | Suma de correlaciones de las diferencias | ↑ |
| **VIF** | Fidelidad de información visual | ↑ |
| **FMI** | Feature Mutual Information (Haghighat et al., 2011) | ↑ |
| **Q0 / QW / QE** | Índices de calidad de Piella y Heijmans (2003) | ↑ |

Análisis estadístico no paramétrico: **Friedman** global por métrica, **Wilcoxon** pareado con
corrección de **Holm** y tamaño de efecto rank-biserial, y **ranking promedio** respetando la dirección
de cada métrica. Implementación: `src/metrics/evaluators.py` y `experiments/run_stats_analysis.py`.

---

## 3. Resultados principales

**Calidad de imagen — TNO Image Fusion Dataset (20 pares).** La *Propuesta Novedosa* (`n=8, m=0.12`)
ofrece el perfil **más limpio y estructuralmente fiel**: la **menor tasa de artefactos** entre los
métodos reales (**Nabf = 0.030**) y la **mayor similitud estructural** entre los no triviales
(**SSIM = 0.785**), con buena preservación de bordes y correlación (**Qabf = 0.484**, **SCD = 1.397**,
**VIF = 0.354**). La variante preliminar en cascada lidera Qabf (0.514) y SCD (1.453) a costa de más
artefactos (Nabf 0.065) y algo menos de SSIM (0.775).

| Método | Qabf ↑ | Nabf ↓ | SSIM ↑ | SCD ↑ | VIF ↑ |
|--------|:---:|:---:|:---:|:---:|:---:|
| Promedio (trivial) | 0.310 | 0.000 | 0.792 | 1.325 | 0.331 |
| Pirámide de Laplace | 0.442 | 0.108 | 0.721 | 1.322 | 0.410 |
| Curvelet | 0.476 | 0.192 | 0.731 | 1.321 | 0.307 |
| Torre Top-Hat (disco, L5) | 0.458 | 0.117 | 0.739 | 1.430 | 0.356 |
| Variante en cascada (preliminar) | **0.514** | 0.065 | 0.775 | **1.453** | 0.369 |
| **Propuesta Novedosa** | 0.484 | **0.030** | **0.785** | 1.397 | 0.354 |

**Detección — LLVIP (YOLOv8, mismas etiquetas, solo cambia la fusión).** La superioridad en calidad de
imagen **no se traslada** directamente a la detección: el **IR solo** obtiene el mejor mAP, la fusión
**supera al VIS solo**, y las fusiones simples igualan o superan a las morfológicas.

| Entrada | mAP@0.5 ↑ | mAP@0.5:0.95 ↑ |
|---------|:---:|:---:|
| **IR (solo)** | **0.957** | **0.663** |
| Pirámide de Laplace | 0.949 | 0.651 |
| Promedio | 0.948 | 0.639 |
| Propuesta Novedosa | 0.905 | 0.618 |
| Variante en cascada | 0.899 | 0.628 |
| VIS (solo) | 0.808 | 0.451 |

**Conclusión honesta:** la *Propuesta Novedosa* es un método orientado a **fidelidad y limpieza** de la
imagen fusionada, no necesariamente a la detectabilidad. La variante Black Top-Hat no se recomienda por
defecto (sube contraste pero degrada Qabf/SSIM/VIF y multiplica los artefactos). *Superioridad en
calidad de imagen ≠ superioridad en detección.*

---

## 4. Estructura del proyecto

```
tesis_mciencias_datos/
│
├── data/raw/                       # VIS/ e IR/ con nombres coincidentes (20 pares TNO)
│   (data/LLVIP/ y datasets/ quedan fuera del repo por tamaño — ver .gitignore)
│
├── src/
│   ├── datasets.py                 # Carga y emparejado VIS/IR
│   ├── fusion/
│   │   ├── novel_fusion.py         # NovelMultiscaleFusion (PROPUESTA NOVEDOSA, método central)
│   │   ├── optimal_top_hat.py      # OptimalMultiscaleFusion (variante preliminar en cascada)
│   │   ├── prop_top_hat.py         # TopHatFusion (Torre Top-Hat, método anterior)
│   │   └── comparatives.py         # average / laplacian_pyramid / curvelet
│   ├── metrics/
│   │   └── evaluators.py           # 16 métricas + METRIC_DIRECTION (incl. FMI, Q0/QW/QE)
│   └── utils/                      # io, visualización, reorganización del dataset
│
├── experiments/
│   ├── run_all_fusions.py          # Ejecuta todos los métodos sobre el dataset
│   ├── run_stats_analysis.py       # Friedman + Wilcoxon(Holm) + ranking
│   ├── pso_novel.py                # PSO de la Propuesta Novedosa (n, m)  -> n=8, m=0.12
│   ├── pso_optimal_multiscale.py   # PSO de la variante en cascada (n, r, m)
│   ├── detection_llvip/            # Reentrenamiento de detección con LLVIP (mAP concluyente)
│   │   ├── prepare_llvip.py        #   genera datasets YOLO fusionados por método (labels compartidas)
│   │   └── train_eval_llvip.py     #   entrena YOLOv8 por método y compara mAP (CSV acumulativo)
│   ├── detection/                  # Detectabilidad por inferencia (TNO, sin etiquetas)
│   ├── make_*figure*.py            # Generación de figuras de la tesis
│   └── results/metrics_reports/    # all_metrics.csv, ranking, friedman, wilcoxon, detección
│
├── notebooks/                      # 01–07 (EDA, fusión, stats, detección)
├── docs/
│   ├── Tesis_Borrador.docx         # Documento principal (formato UCOM/Villalba, 26 ecuaciones, índice)
│   ├── figures/                    # Figuras del libro
│   └── reportes_finales/           # Reportes cuali/cuantitativos
│
├── ejecutar_llvip.ps1              # Lanzador del pipeline LLVIP en la PC (GPU)
├── reparar_torch_gpu.ps1           # Reinstala torch con CUDA (GPU)
├── push_to_github.ps1              # Commit + push asistido
├── requirements.txt
└── README.md
```

---

## 5. Instalación

**Requisitos:** Python 3.11+

```powershell
git clone https://github.com/YanBajac/tesis_mciencias_datos.git
cd tesis_mciencias_datos

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Las imágenes de cada modalidad deben tener el **mismo nombre de archivo** en `data/raw/VIS/` y
`data/raw/IR/` para el emparejado automático.

---

## 6. Uso rápido

```python
from src.datasets import list_pairs, load_pair
from src.fusion.novel_fusion import NovelMultiscaleFusion     # propuesta central
from src.metrics.evaluators import evaluate_all

pairs = list_pairs()
vis, ir = load_pair(*pairs[0])

# Propuesta Novedosa (configuración óptima del PSO)
fuser = NovelMultiscaleFusion(n=8, m=0.12)
fused = fuser.fuse(vis, ir)

metrics = evaluate_all(fused, vis, ir)
print(metrics)   # EN, SD, FE, MG, MI_vis, MI_ir, SF, Qabf, Nabf, SSIM, SCD, VIF, FMI, Q0, QW, QE
```

---

## 7. Ejecución de experimentos

```powershell
# 1. Fusiones (todos los métodos) y métricas -> all_metrics.csv
python experiments/run_all_fusions.py

# 2. Análisis estadístico (Friedman, Wilcoxon+Holm, ranking)
python experiments/run_stats_analysis.py

# 3. Optimización por PSO de la Propuesta Novedosa (reanudable) -> n=8, m=0.12
python experiments/pso_novel.py
```

Salidas en `experiments/results/metrics_reports/`: `all_metrics.csv`, `comparativa_con_propuesta.csv`,
`descriptive_means.csv`, `ranking_methods.csv`, `friedman_results.csv`, `wilcoxon_results.csv`,
`metrics_extra_fmi_piella.csv`.

---

## 8. Evaluación orientada a tarea (detección LLVIP)

Para una comparación **concluyente** del efecto de la fusión en la detección se reentrena el mismo
detector (YOLOv8) sobre cada versión fusionada del dataset **LLVIP** (VIS/IR alineado y etiquetado,
peatones nocturnos). Las **etiquetas son idénticas** para todos los métodos: solo cambian los píxeles
fusionados, de modo que la diferencia de mAP aísla el efecto del método.

```powershell
# Pipeline completo en la PC (con GPU). Requiere el dataset LLVIP descomprimido.
powershell -ExecutionPolicy Bypass -File .\ejecutar_llvip.ps1 -LLVIP "D:\datasets\LLVIP"
```

Esto ejecuta `experiments/detection_llvip/prepare_llvip.py` (genera los datasets YOLO fusionados por
método) y `train_eval_llvip.py` (entrena y compara mAP, acumulando en
`experiments/results/metrics_reports/detection_llvip_map.csv`). La carpeta `experiments/detection/`
mantiene la evaluación previa por **inferencia** sobre TNO (sin etiquetas).

---

## 9. Notebooks de análisis

| Notebook | Propósito |
|----------|-----------|
| `01_EDA_dataset.ipynb` | Exploración visual y estadística del dataset |
| `02_fusion_tests.ipynb` | Comparación visual rápida de configuraciones |
| `03_stats_analysis.ipynb` | Análisis cuantitativo, boxplots, Wilcoxon/Friedman |
| `04_yolo_roboflow_deteccion.ipynb` | Entrenamiento YOLO por modalidad (Colab, mAP) |
| `05_keras_clasificacion_downstream.ipynb` | MobileNetV2 transfer learning (tarea alternativa) |
| `06_rfdetr_deteccion.ipynb` | Detección con RF-DETR |
| `07_colab_deteccion_automatica.ipynb` | Flujo de detección automática en Colab |

---

## 10. Dependencias

`numpy`, `opencv-python`, `scikit-image`, `scipy`, `PyWavelets`, `pandas`, `matplotlib`, `seaborn`,
`jupyter`, `ipykernel`, `openpyxl`, `plotly`, `torch`, `torchvision` (ver `requirements.txt`).
La detección con YOLO/RF-DETR requiere `ultralytics` / `rfdetr` (preferentemente con GPU CUDA).

---

## 11. Referencias

- Serra, J. (1982). *Image Analysis and Mathematical Morphology*. Academic Press.
- Soille, P. (2003). *Morphological Image Analysis*. Springer.
- Burt, P. & Adelson, E. (1983). The Laplacian Pyramid as a Compact Image Code. *IEEE Trans. Commun.*
- Candès, E. et al. (2006). Fast Discrete Curvelet Transforms. *SIAM Multiscale Model. Simul.*
- Kennedy, J. & Eberhart, R. (1995). Particle Swarm Optimization. *Proc. ICNN*.
- Xydeas, C. & Petrović, V. (2000). Objective image fusion performance measure. *Electronics Letters*.
- Piella, G. & Heijmans, H. (2003). A new quality metric for image fusion. *Proc. ICIP*.
- Haghighat, M. et al. (2011). A non-reference image fusion metric based on mutual information of image features. *Computers & Electrical Engineering*.
- Ma, J. et al. (2019). Infrared and visible image fusion methods and applications: A survey. *Information Fusion*, 45.
- Singh, S. et al. (2023). A review of image fusion: methods, applications and performance metrics. *(revisión de referencia del estado del arte)*.
- Bala, A. A. et al. (2024). Hybrid technique for fundus image enhancement using a modified morphological filter and a denoising net.
- Román, J. C. M., Vázquez Noguera, J. L. & Legal-Ayala, H. (2024). Algoritmo de realce de contraste multiescala con Top-Hat (SE circulares y lineales).
- Ortega Rodríguez, M. A. & Espinoza Ríos, G. A. (2025). Optimización de los parámetros de fusión Top-Hat mediante PSO. FPUNA.

---

> *Este repositorio forma parte de la investigación de tesis de Maestría en Ciencias de Datos.*
> *El código está organizado para la reproducibilidad total de los experimentos.*
