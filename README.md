# Fusión de Imágenes Infrarrojas y Visibles mediante Morfología Matemática

> **Tesis de Maestría en Ciencias de Datos**
> Universidad Comunera (UCOM)
> Autores: Lic. Juan Pablo Bazán, Ing. Yan Bajac
> Director: D.Sc. Julio César Mello

> **Propuesta central (definitiva):** una fusión VIS/IR basada en transformadas Top-Hat de
> **una sola escala** definida por el radio `r`: se **promedian** las respuestas de cuatro elementos
> estructurantes **lineales** (0°, 45°, 90°, 135°, longitud `2r+1`) y se **suman** a la respuesta de un
> **disco** `B_r` (esquema de Bala et al., 2024); entre fuentes gana el detalle dominante y se
> reconstruye con `F = I_base + m·WTH − m·BTH`. Los hiperparámetros `(r, m)` se ajustan por
> **enjambre de partículas (PSO)** con aptitud orientada a fusión, eligiendo la configuración del
> enjambre mediante un **barrido de 25 combinaciones** (partículas 2–10 × iteraciones 10–50,
> replicando el diseño de Ortega y Espinoza 2025) → **óptimo global: r = 25, m = 0.070**.
> Se compara contra **seis métodos**: cinco del estado del arte —Pirámide de Laplace (LP), Ratio of
> low-pass Pyramid (RP, Toet 1989), Wavelet discreta (DWT), Dual-Tree Complex Wavelet (DTCWT) y
> Curvelet (CVT)— más la **metodología clásica de la transformada Top-Hat**, sobre el **TNO Image
> Fusion Dataset** (20 pares) con **12 métricas sin referencia**, y se evalúa su impacto en
> **detección de objetos** entrenando YOLOv8 sobre el dataset etiquetado **LLVIP** (mAP).

---

## Índice

1. [Descripción del problema](#1-descripción-del-problema)
2. [Marco teórico](#2-marco-teórico)
   - [Fusión de imágenes multimodal](#21-fusión-de-imágenes-multimodal)
   - [Morfología matemática](#22-morfología-matemática)
   - [Transformada Top-Hat](#23-transformada-top-hat)
   - [Propuesta novedosa: fusión Top-Hat de una sola escala (método central)](#24-propuesta-novedosa-fusión-top-hat-de-una-sola-escala-método-central)
   - [Métodos comparativos del benchmark](#25-métodos-comparativos-del-benchmark)
   - [Métricas de evaluación](#26-métricas-de-evaluación)
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

Esta tesis propone y evalúa una **fusión morfológica Top-Hat de una sola escala** (la *Propuesta
Novedosa*), la contrasta estadísticamente con cinco métodos del estado del arte y con la metodología
clásica de la transformada Top-Hat, y mide su efecto sobre una tarea de detección de objetos con un
dataset etiquetado.

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

### 2.4 Propuesta novedosa: fusión Top-Hat de una sola escala (método central)

Integra el filtro morfológico multiángulo de dos etapas de Bala et al. (2024) —respuestas lineales
promediadas **sumadas** a la respuesta del disco— en el esquema de fusión ponderada por PSO de
Ortega y Espinoza (2025).

1. **Elementos estructurantes** (escala única de radio `r`): un disco `B_r` y cuatro segmentos
   lineales `L_{r,θ}` de longitud `2r+1` (θ = 0°, 45°, 90°, 135°).

2. **Operador combinado por suma.** Se **promedian** las cuatro respuestas Top-Hat lineales y se
   **suman** a la respuesta del disco (análogo para BTH con el cierre):

   ```
   WTH_líneas = (1/4)·Σθ [ f − γ(f, L_{r,θ}) ]
   WTH        = WTH_líneas + WTH_disco              (idéntico para BTH)
   ```

   El promedio angular atenúa el ruido direccional; la suma acumula la evidencia de las estructuras
   direccionales e isótropas.

3. **Combinación entre fuentes y reconstrucción** sobre `I_base = (VIS + IR)/2`:

   ```
   WTH_F = máx(WTH^VIS, WTH^IR)      BTH_F = máx(BTH^VIS, BTH^IR)
   F     = I_base + m·WTH_F − m·BTH_F
   ```

4. **Optimización por PSO.** La configuración del enjambre se eligió con un **barrido de 25
   combinaciones** (partículas `n ∈ {2,4,6,8,10}` × iteraciones `T ∈ {10,20,30,40,50}`, replicando
   el Cuadro 1 de Ortega y Espinoza 2025), con `r ∈ [1,25]` (rango del mismo trabajo) y
   `m ∈ [0.05,1.20]`, maximizando la aptitud orientada a fusión `F = SSIM + Qabf + 0.5·SCD − Nabf`.
   **Óptimo global:** `r = 25`, `m = 0.070` (F = 1.9843), alcanzado consistentemente con `n = 10` y
   `T ≥ 30`; los enjambres de 2 partículas caen en el óptimo local `r = 1`. Tabla completa:
   `experiments/results/metrics_reports/pso_grid_search.csv`.

Implementación: `src/fusion/optimal_top_hat.py` (`fuse_optimal(vis, ir, r, m, mode="sum")`);
barrido en `experiments/pso_grid_search.py`.

### 2.5 Métodos comparativos del benchmark

| Método | Descripción | Referencia |
|--------|-------------|------------|
| **Pirámide de Laplace (LP)** | Descomposición Gaussiana-Laplaciana (4 niveles); detalle por máxima actividad | Burt y Adelson (1983) |
| **Ratio of low-pass Pyramid (RP)** | Razones entre niveles gaussianos; se conserva la razón que más se aparta de 1; reconstrucción multiplicativa | Toet (1989) |
| **Wavelet discreta (DWT)** | Subbandas de detalle/aproximación (Haar, 3 niveles); detalle por máxima magnitud | — |
| **Dual-Tree Complex Wavelet (DTCWT)** | 6 subbandas direccionales complejas por nivel (4 niveles), invariante al desplazamiento | Kingsbury |
| **Curvelet (CVT, vía wavelet 2D)** | Subbandas direccionales (db4, 3 niveles); máxima magnitud en detalle | Candès et al. (2006) |
| **Top-Hat clásico** | Fusión morfológica básica: disco `B_5`, `F = I_base + máx(WTH) − máx(BTH)` sin ponderación | — |

Implementación: `src/fusion/comparatives.py`. Todos se evalúan con la misma implementación de
métricas, sobre los mismos 20 pares.

### 2.6 Métricas de evaluación

Evaluación con **12 métricas sin referencia**: seis de actividad/información y seis estándar de
calidad de fusión (el evaluador implementa además FMI y los índices de Piella).

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

**Calidad de imagen — TNO Image Fusion Dataset (20 pares).** La *Propuesta Novedosa* (`r=25, m=0.070`)
logra la **menor tasa de artefactos por amplio margen** (**Nabf = 0.041**, 2.7 veces menos que el
mejor rival) y la **mayor similitud estructural** (**SSIM = 0.782**); en Qabf, SCD y VIF queda
**segunda**, a milésimas del líder de cada columna.

| Método | Qabf ↑ | Nabf ↓ | SSIM ↑ | SCD ↑ | VIF ↑ |
|--------|:---:|:---:|:---:|:---:|:---:|
| Pirámide de Laplace (LP) | 0.442 | 0.108 | 0.721 | 1.322 | **0.410** |
| Ratio of low-pass Pyramid (RP) | 0.497 | 0.212 | 0.721 | **1.468** | 0.384 |
| Wavelet discreta (DWT) | 0.489 | 0.229 | 0.716 | 1.322 | 0.303 |
| Dual-Tree Complex Wavelet (DTCWT) | **0.501** | 0.151 | 0.739 | 1.376 | 0.360 |
| Curvelet (CVT) | 0.476 | 0.192 | 0.731 | 1.321 | 0.307 |
| Top-Hat clásico | 0.305 | 0.585 | 0.578 | 1.360 | 0.334 |
| **Propuesta Novedosa (r=25, m=0.070)** | 0.500 | **0.041** | **0.782** | 1.450 | 0.368 |

El **Top-Hat clásico** —la referencia morfológica directa— solo gana en actividad bruta (EN, MG, SF) a
costa del mayor Nabf del estudio (0.585): la diferencia con la propuesta aísla el aporte del banco
disco + líneas y del ajuste `(r, m)` por PSO. En el **ranking global** (7 métodos, 12 métricas) la
propuesta es 1ª en Nabf y SSIM y 2ª en Qabf/SCD/VIF; las métricas de actividad, que premian el realce
agresivo, bajan su promedio. En los contrastes de **Wilcoxon-Holm** (60, propuesta vs. los 5 del
estado del arte) resulta significativamente mejor en 25, peor en 27 (concentrados en las métricas de
actividad) y sin diferencia en 8.

**Detección — LLVIP (YOLOv8n reentrenado por método, mismas etiquetas, solo cambia la fusión).**
Toda fusión supera con claridad al VIS solo, pero ninguna al IR solo (el peatón nocturno es
esencialmente térmico); entre las fusiones, la propuesta es competitiva sin ser la líder. *La
superioridad en calidad de imagen no se traslada automáticamente a la detección* (H3 parcial).

| Entrada | mAP@0.5 ↑ | mAP@0.5:0.95 ↑ |
|---------|:---:|:---:|
| **IR (solo)** | **0.957** | **0.663** |
| Pirámide de Laplace (LP) | 0.949 | 0.651 |
| Dual-Tree Complex Wavelet (DTCWT) | 0.948 | 0.633 |
| Wavelet discreta (DWT) | 0.946 | 0.614 |
| Curvelet (CVT) | 0.941 | 0.639 |
| Top-Hat clásico | 0.938 | 0.609 |
| **Propuesta Novedosa (r=25, m=0.070)** | 0.936 | 0.609 |
| Ratio Pyramid (RP) | 0.926 | 0.538 |
| VIS (solo) | 0.808 | 0.451 |

---

## 4. Estructura del proyecto

```
TFM_Fusion_Imagenes_Propuesta_Oficial/
│
├── data/raw/                       # VIS/ e IR/ con nombres coincidentes (20 pares TNO)
│   (data/LLVIP/ y datasets/ quedan fuera del repo por tamaño — ver .gitignore)
│
├── src/
│   ├── datasets.py                 # Carga y emparejado VIS/IR
│   ├── fusion/
│   │   ├── optimal_top_hat.py      # fuse_optimal (PROPUESTA NOVEDOSA, mode="sum", r=25, m=0.0703)
│   │   └── comparatives.py         # LP / RP / DWT / DTCWT / CVT / Top-Hat clásico
│   ├── metrics/
│   │   └── evaluators.py           # 16 métricas + METRIC_DIRECTION (incl. FMI, Q0/QW/QE)
│   └── utils/                      # io, visualización, reorganización del dataset
│
├── experiments/
│   ├── run_all_fusions.py          # Benchmark: los 7 métodos sobre el dataset -> all_metrics.csv
│   ├── run_stats_analysis.py       # Friedman + Wilcoxon(Holm) + ranking
│   ├── pso_grid_search.py          # Barrido PSO 5x5 (Cuadro 1 FPUNA) -> r=25, m=0.0703
│   ├── make_montajes_cualitativos.py # 20 montajes por escena (propuesta en rojo)
│   ├── make_figuras_metodo.py      # Figuras del método (banco de SE, ejemplo de modalidades)
│   ├── make_avances_report.py      # Regenera docs/Avances_Tesis.pdf (HTML -> PDF con Edge)
│   ├── make_avances_excel.py       # Regenera docs/Avances_Tesis_Tablas.xlsx (10 hojas)
│   ├── detection_llvip/            # Reentrenamiento de detección con LLVIP (mAP concluyente)
│   │   ├── prepare_llvip.py        #   genera datasets YOLO fusionados por método (labels compartidas)
│   │   └── train_eval_llvip.py     #   entrena YOLOv8 por método y compara mAP (CSV acumulativo)
│   └── results/metrics_reports/    # all_metrics.csv, ranking, friedman, wilcoxon, detección
│
├── notebooks/                      # 01 (EDA) y 03 (análisis estadístico)
├── docs/
│   ├── Tesis_Borrador_V3.docx      # Documento principal (propuesta suma r=25; formato UCOM/Villalba)
│   ├── Avances_Tesis.pdf           # Informe de avances · Avances_Tesis_Tablas.xlsx (tablas)
│   ├── Tesis_Defensa_Presentacion.pptx # Presentación de defensa (17 láminas, notas del orador)
│   ├── figures/                    # Figuras del libro (fuente y montajes cualitativos)
│   └── reportes_finales/           # Metodología de evaluación de detección
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
git clone https://github.com/YanBajac/TFM_Fusion_Imagenes_Propuesta_Oficial.git
cd TFM_Fusion_Imagenes_Propuesta_Oficial

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
from src.fusion.optimal_top_hat import fuse_optimal            # propuesta central
from src.metrics.evaluators import evaluate_all

pairs = list_pairs()
vis, ir = load_pair(*pairs[0])

# Propuesta Novedosa (configuración óptima del PSO, operador con suma de ramas)
fused = fuse_optimal(vis, ir, r=25, m=0.0703, mode="sum")

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

# 3. Barrido de configuraciones PSO (25 combinaciones, reanudable) -> r=25, m=0.0703
python experiments/pso_grid_search.py

# 4. Montajes cualitativos (20 escenas, propuesta en rojo)
python experiments/make_montajes_cualitativos.py
```

Salidas en `experiments/results/metrics_reports/`: `all_metrics.csv`, `descriptive_means.csv`,
`ranking_methods.csv`, `friedman_results.csv`, `wilcoxon_results.csv`.

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
`experiments/results/metrics_reports/detection_llvip_map.csv`).

---

## 9. Notebooks de análisis

| Notebook | Propósito |
|----------|-----------|
| `01_EDA_dataset.ipynb` | Exploración visual y estadística del dataset |
| `03_stats_analysis.ipynb` | Análisis cuantitativo, boxplots, Wilcoxon/Friedman |

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
