# Fusión de Imágenes Infrarrojas y Visibles mediante Morfología Matemática

> **Tesis de Maestría en Ciencias de Datos**
> Universidad Comunera (UCOM)
> Autores: Lic. Juan Pablo Bazán, Ing. Yan Bajac
> Director: D.Sc. Julio César Mello

> **Propuesta central:** un **método óptimo multiescala** de fusión VIS/IR basado en transformadas
> Top-Hat con elementos estructurantes **circulares y lineales**, descomposición **en cascada** e
> hiperparámetros optimizados por **enjambre de partículas (PSO)**. Se compara con el método anterior
> (Torre Top-Hat) y con baselines clásicos sobre el **TNO Image Fusion Dataset** (20 pares), usando
> **12 métricas sin referencia**, y se evalúa su impacto en una **tarea de detección** con YOLO.

---

## Índice

1. [Descripción del problema](#1-descripción-del-problema)
2. [Marco teórico](#2-marco-teórico)
   - [Fusión de imágenes multimodal](#21-fusión-de-imágenes-multimodal)
   - [Morfología matemática](#22-morfología-matemática)
   - [Transformada Top-Hat](#23-transformada-top-hat)
   - [Método óptimo multiescala (propuesta central)](#24-método-óptimo-multiescala-propuesta-central)
   - [Torre Top-Hat (método anterior)](#25-torre-top-hat-método-anterior)
   - [Algoritmos de referencia (baselines)](#26-algoritmos-de-referencia-baselines)
   - [Métricas de evaluación](#27-métricas-de-evaluación)
3. [Resultados principales](#3-resultados-principales)
4. [Estructura del proyecto](#4-estructura-del-proyecto)
5. [Instalación](#5-instalación)
6. [Uso rápido](#6-uso-rápido)
7. [Ejecución de experimentos](#7-ejecución-de-experimentos)
8. [Evaluación orientada a tarea (detección)](#8-evaluación-orientada-a-tarea-detección)
9. [Notebooks de análisis](#9-notebooks-de-análisis)
10. [Dependencias](#10-dependencias)
11. [Referencias](#11-referencias)

---

## 1. Descripción del problema

Las cámaras **visibles (VIS)** capturan la reflectancia de la luz solar, ofreciendo alta resolución
textural y de color pero siendo sensibles a condiciones de iluminación adversas (noche, niebla, humo).
Las cámaras **infrarrojas (IR)** detectan la radiación térmica emitida por los objetos, siendo
robustas a la oscuridad pero con menor resolución espacial y detalle de textura.

La **fusión de imágenes** VIS+IR busca generar una única imagen que combine las fortalezas de ambas
modalidades, mejorando la percepción visual para aplicaciones como vigilancia y seguridad perimetral,
detección de personas en visibilidad reducida, guía de vehículos autónomos e inspección industrial y
médica.

Esta tesis propone y evalúa un **método óptimo multiescala** basado en morfología matemática, lo
contrasta estadísticamente con un método anterior y con baselines clásicos, y mide su efecto sobre
una tarea de detección de objetos.

---

## 2. Marco teórico

### 2.1 Fusión de imágenes multimodal

La fusión de imágenes combina información complementaria de dos o más sensores para obtener una
representación más completa de una escena. El esquema general opera en tres etapas: **preprocesamiento**
(registro, normalización), **fusión en dominio transformado** (descomposición multiescala, regla de
fusión por capa y reconstrucción) y **evaluación** mediante métricas sin referencia.

### 2.2 Morfología matemática

La **morfología matemática** es un marco algebraico para el análisis de estructuras geométricas en
imágenes, basado en la teoría de retículas completas. Sus operaciones fundamentales son:

| Operación | Definición | Efecto visual |
|-----------|-----------|---------------|
| **Erosión** `ε(f,b)` | mínimo local bajo `b` | adelgaza estructuras, elimina picos |
| **Dilatación** `δ(f,b)` | máximo local bajo `b` | engruesa estructuras, rellena valles |
| **Apertura** `γ(f,b) = δ(ε(f,b),b)` | erosión seguida de dilatación | elimina objetos menores que `b` |
| **Cierre** `φ(f,b) = ε(δ(f,b),b)` | dilatación seguida de erosión | rellena huecos menores que `b` |

donde `f` es la imagen y `b` el **elemento estructurante (SE)** que define la geometría del vecindario.

### 2.3 Transformada Top-Hat

Las transformadas **Top-Hat** extraen detalles que la apertura/cierre eliminan:

- **White Top-Hat (WTH):** `WTH(f,b) = f − γ(f,b)` → resalta estructuras brillantes más pequeñas que `b`.
- **Black Top-Hat (BTH):** `BTH(f,b) = φ(f,b) − f` → resalta estructuras oscuras más pequeñas que `b`.

El **tipo de SE** (disco, cuadrado, cruz, línea) determina qué orientaciones de detalle se enfatizan
y el **radio `r`** controla la escala.

### 2.4 Método óptimo multiescala (propuesta central)

El método propuesto generaliza la Top-Hat sobre dos ejes: la **geometría del SE** y la **escala**.
Adapta a la fusión VIS/IR la metodología de realce multiescala de Román et al. (2024) y el esquema de
fusión optimizada por PSO de Ortega y Espinoza (2025).

1. **Banco de 5 elementos estructurantes por escala** — un disco y cuatro líneas (0°, 45°, 90°, 135°).
   Las cinco respuestas WTH/BTH se combinan tomando el **máximo por píxel**, captando bordes en
   cualquier orientación sin privilegiar ninguna a priori.
2. **Descomposición multiescala en cascada** — el operador se evalúa en `n` escalas (radios `r·i`); se
   calculan diferencias en cascada (`WTHS_i`) y se agrega cada familia por máximo (`WTH_M`, `WTHS_M`,
   `BTH_M`, `BTHS_M`).
3. **Regla de fusión ponderada** — sobre la base `I_base = (VIS+IR)/2`:

   ```
   F = I_base + m·(WTH_M + WTHS_M) − m·(BTH_M + BTHS_M)
   ```

4. **Optimización por PSO** — los hiperparámetros `(n, r, m)` se ajustan con enjambre de partículas
   (30 partículas × 30 iteraciones) maximizando una aptitud orientada a fusión
   `F = SSIM + Qabf + 0.5·SCD − Nabf`. **Óptimo hallado:** `n=6`, `r≈2.89`, `m=0.10`.

Implementación: `src/fusion/optimal_top_hat.py` (`OptimalMultiscaleFusion`); PSO en
`experiments/pso_optimal_multiscale.py`.

### 2.5 Torre Top-Hat (método anterior)

Descomposición multiescala iterativa con un **único disco por escala** y reglas de selección manuales,
usada como **base de comparación**:

```
Nivel 1 (r=r₀):   WTH₁ = f − γ(f, b_{r₀})
Nivel k (r=k·r₀): WTHₖ = R_{k-1} − γ(R_{k-1}, b_{kr₀})
Residual:         R_L = base de baja frecuencia
F = base_fusionada + Σ WTHₖ^fus − Σ BTHₖ^fus
```

Las capas de detalle se fusionan por **máxima actividad local**; la base, por **promedio**. Modos WTH
(por defecto) y WTH+BTH. Parámetros del benchmark: SE ∈ {disco, cuadrado, cruz}, `L ∈ {2,3,4,5}`,
`r₀ ∈ {2,3,5}`. Implementación: `src/fusion/prop_top_hat.py` (`TopHatFusion`).

### 2.6 Algoritmos de referencia (baselines)

| Método | Descripción | Referencia |
|--------|-------------|------------|
| **Promedio** | `F = 0.5·VIS + 0.5·IR` — cota inferior de complejidad | — |
| **Pirámide de Laplace** | Descomposición Gaussiana-Laplaciana (4 niveles); fusión por máxima actividad | Burt y Adelson (1983) |
| **Curvelet (vía wavelet 2D)** | Subbandas direccionales (db4, 3 niveles); máxima magnitud en detalle | Candès et al. (2006) |

### 2.7 Métricas de evaluación

Evaluación con **12 métricas sin referencia**: seis clásicas de actividad/información y seis estándar
de calidad de fusión.

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

Análisis estadístico no paramétrico: **Friedman** global por métrica, **Wilcoxon** pareado con
corrección de **Holm** y tamaño de efecto rank-biserial, y **ranking promedio** respetando la dirección
de cada métrica. Implementación: `src/metrics/evaluators.py` y `experiments/run_stats_analysis.py`.

---

## 3. Resultados principales

Sobre 20 pares del TNO Image Fusion Dataset:

- El **método óptimo multiescala** lidera las métricas estándar de calidad: **Qabf = 0.514** (1.º),
  **SCD = 1.453** (1.º), **Nabf = 0.065** (la menor entre los métodos no triviales) y **SSIM = 0.775**
  (2.º, solo detrás del promedio trivial). Cede en contraste (SD, EN), por lo que su ranking agregado
  de 12 métricas queda en la franja media (6.67).
- No hay un método universalmente dominante: la **pirámide de Laplace** encabeza el ranking agregado
  (4.42) por su ventaja en contraste y VIF; la **Torre Top-Hat** (disco, L=5) es segunda (5.00) y supera
  a Laplace en fidelidad estructural (SSIM, SCD).
- La variante **Black Top-Hat** no se recomienda por defecto: sube contraste pero degrada Qabf/SSIM/VIF
  y multiplica los artefactos (Nabf ×5).
- En **detección** (YOLOv8n por inferencia), la fusión mejora la detectabilidad de personas frente a
  VIS; las diferencias entre métodos no son estadísticamente significativas con `n=20` sin etiquetas
  (limitación documentada).

---

## 4. Estructura del proyecto

```
tesis_mciencias_datos/
│
├── data/raw/                       # VIS/ e IR/ con nombres coincidentes (20 pares TNO)
│
├── src/
│   ├── datasets.py                 # Carga y emparejado VIS/IR
│   ├── fusion/
│   │   ├── prop_top_hat.py         # TopHatFusion (Torre Top-Hat, método anterior)
│   │   ├── optimal_top_hat.py      # OptimalMultiscaleFusion (propuesta central) + variante monoescala
│   │   └── comparatives.py         # average / laplacian_pyramid / curvelet
│   ├── metrics/
│   │   └── evaluators.py           # 12 métricas + METRIC_DIRECTION
│   └── utils/                      # io, visualización, reorganización del dataset
│
├── experiments/
│   ├── run_all_fusions.py          # Ejecuta todos los métodos sobre el dataset
│   ├── run_stats_analysis.py       # Friedman + Wilcoxon(Holm) + ranking
│   ├── pso_optimal_multiscale.py   # PSO del método óptimo multiescala (n, r, m)
│   ├── pso_optimal_tophat.py       # PSO de la variante monoescala (r, m)
│   ├── detection/                  # Evaluación orientada a tarea (YOLO/RF-DETR/Keras)
│   ├── make_*figure*.py            # Generación de figuras de la tesis
│   └── results/metrics_reports/    # all_metrics.csv, ranking, friedman, wilcoxon, detección
│
├── notebooks/                      # 01–07 (EDA, fusión, stats, detección, Colab)
├── docs/
│   ├── Tesis_Borrador.docx         # Documento principal
│   ├── figures/                    # Figuras del libro
│   └── reportes_finales/           # Reportes cuali/cuantitativos
│
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
from src.fusion.optimal_top_hat import OptimalMultiscaleFusion   # propuesta central
from src.fusion import TopHatFusion                              # método anterior
from src.metrics.evaluators import evaluate_all

pairs = list_pairs()
vis, ir = load_pair(*pairs[0])

# Método óptimo multiescala (configuración óptima del PSO)
fuser = OptimalMultiscaleFusion(n=6, base_radius=2.89, m=0.10)
fused = fuser.fuse(vis, ir)

metrics = evaluate_all(fused, vis, ir)
print(metrics)   # EN, SD, FE, MG, MI_vis, MI_ir, SF, Qabf, Nabf, SSIM, SCD, VIF
```

---

## 7. Ejecución de experimentos

```powershell
# 1. Fusiones (todos los métodos) y métricas -> all_metrics.csv
python experiments/run_all_fusions.py

# 2. Análisis estadístico (Friedman, Wilcoxon+Holm, ranking)
python experiments/run_stats_analysis.py

# 3. Optimización por PSO del método óptimo multiescala (reanudable)
python experiments/pso_optimal_multiscale.py
```

Salidas en `experiments/results/metrics_reports/`: `all_metrics.csv`, `descriptive_means.csv`,
`ranking_methods.csv`, `friedman_results.csv`, `wilcoxon_results.csv`.

---

## 8. Evaluación orientada a tarea (detección)

La carpeta `experiments/detection/` evalúa el efecto de la fusión en una tarea downstream de detección:

```powershell
# Detectabilidad por inferencia (YOLOv8n) sobre VIS, IR y las fusiones
python experiments/detection/run_detection_eval.py --detector yolo

# Resumen y estadística
python experiments/detection/summarize_detection.py
python experiments/detection/stats_detection.py
```

`run_all_applications.py` deja preparado (scaffold) el entrenamiento por modalidad con YOLO, RF-DETR y
Keras; para métricas de mAP concluyentes se requiere un dataset etiquetado (M3FD/LLVIP). Los notebooks
04–07 cubren el flujo en Colab con GPU.

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
La detección con YOLO/RF-DETR requiere `ultralytics` / `rfdetr` (preferentemente con GPU).

---

## 11. Referencias

- Serra, J. (1982). *Image Analysis and Mathematical Morphology*. Academic Press.
- Soille, P. (2003). *Morphological Image Analysis*. Springer.
- Burt, P. & Adelson, E. (1983). The Laplacian Pyramid as a Compact Image Code. *IEEE Trans. Commun.*
- Candès, E. et al. (2006). Fast Discrete Curvelet Transforms. *SIAM Multiscale Model. Simul.*
- Kennedy, J. & Eberhart, R. (1995). Particle Swarm Optimization. *Proc. ICNN*.
- Xydeas, C. & Petrović, V. (2000). Objective image fusion performance measure. *Electronics Letters*.
- Li, S. et al. (2017). Pixel-level image fusion: A survey of the state of the art. *Information Fusion*, 33.
- Ma, J. et al. (2019). Infrared and visible image fusion methods and applications: A survey. *Information Fusion*, 45.
- Román, J. C. M., Vázquez Noguera, J. L. & Legal-Ayala, H. (2024). Algoritmo de realce de contraste multiescala con Top-Hat (SE circulares y lineales).
- Ortega Rodríguez, M. A. & Espinoza Ríos, G. A. (2025). Optimización de los parámetros de fusión Top-Hat mediante PSO. FPUNA.

---

> *Este repositorio forma parte de la investigación de tesis de Maestría en Ciencias de Datos.*
> *El código está organizado para la reproducibilidad total de los experimentos.*
