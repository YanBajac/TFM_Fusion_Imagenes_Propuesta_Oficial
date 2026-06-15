# Fusión de Imágenes Infrarrojas y Visibles mediante Morfología Matemática

> **Tesis de Maestría en Ciencias de Datos**  
> Universidad Comunera (UCOM) 
> Autor: Lic. Juan Pablo Bazan , Ing. Yan Bajac
> Director: D.Sc Julio Cesar Mello 

---

## Índice

1. [Descripción del problema](#1-descripción-del-problema)
2. [Marco teórico](#2-marco-teórico)
   - [Fusión de imágenes multimodal](#21-fusión-de-imágenes-multimodal)
   - [Morfología matemática](#22-morfología-matemática)
   - [Transformada Top-Hat](#23-transformada-top-hat)
   - [Torre Top-Hat (método propuesto)](#24-torre-top-hat-método-propuesto)
   - [Algoritmos de referencia (baselines)](#25-algoritmos-de-referencia-baselines)
   - [Métricas de evaluación](#26-métricas-de-evaluación)
3. [Estructura del proyecto](#3-estructura-del-proyecto)
4. [Instalación](#4-instalación)
5. [Uso rápido](#5-uso-rápido)
6. [Ejecución de experimentos](#6-ejecución-de-experimentos)
7. [Notebooks de análisis](#7-notebooks-de-análisis)
8. [Dependencias](#8-dependencias)
9. [Referencias](#9-referencias)

---

## 1. Descripción del problema

Las cámaras **visibles (VIS)** capturan la reflectancia de la luz solar, ofreciendo alta resolución
textural y de color pero siendo sensibles a condiciones de iluminación adversas (noche, niebla, humo).
Las cámaras **infrarrojas (IR)** detectan la radiación térmica emitida por los objetos, siendo
robustas a la oscuridad pero con menor resolución espacial y detalle de textura.

La **fusión de imágenes** VIS+IR busca generar una única imagen que combine las fortalezas de ambas
modalidades, mejorando la percepción visual para aplicaciones como:

- Vigilancia y seguridad perimetral
- Detección de personas en entornos de visibilidad reducida
- Guía de vehículos autónomos
- Inspección industrial y médica

Esta tesis propone y evalúa un método basado en la **Torre Top-Hat morfológica** con múltiples
geometrías de elemento estructurante y múltiples niveles de descomposición.

---

## 2. Marco teórico

### 2.1 Fusión de imágenes multimodal

La fusión de imágenes (del inglés *image fusion*) es el proceso de combinar información complementaria
proveniente de dos o más sensores para obtener una representación más completa de una escena.
El esquema general opera en tres etapas:

1. **Preprocesamiento:** alineación espacial (registro), normalización de intensidades y
   redimensionado a resolución común.
2. **Fusión en dominio transformado:** descomposición de cada imagen en representaciones
   multi-escala (pirámides, wavelets, morfológicas), aplicación de una *regla de fusión* por capa
   y reconstrucción.
3. **Evaluación:** cuantificación de la calidad mediante métricas sin referencia.

### 2.2 Morfología matemática

La **morfología matemática** es un framework algebraico para el análisis de estructuras geométricas
en imágenes, basado en la teoría de retículas completas. Sus operaciones fundamentales son:

| Operación | Definición | Efecto visual |
|-----------|-----------|---------------|
| **Erosión** `ε(f,b)` | mínimo local ponderado por `b` | adelgaza estructuras, elimina picos |
| **Dilatación** `δ(f,b)` | máximo local ponderado por `b` | engruesa estructuras, rellena valles |
| **Apertura** `γ(f,b) = δ(ε(f,b),b)` | erosión seguida de dilatación | elimina objetos menores que `b` |
| **Cierre** `φ(f,b) = ε(δ(f,b),b)` | dilatación seguida de erosión | rellena huecos menores que `b` |

donde `f` es la imagen y `b` el **elemento estructurante (SE)** que define la geometría del vecindario.

### 2.3 Transformada Top-Hat

Las transformadas **Top-Hat** extraen componentes de alta frecuencia que la apertura/cierre no puede
reconstruir:

- **White Top-Hat (WTH):** `WTH(f,b) = f − γ(f,b)` → resalta estructuras brillantes más pequeñas que `b`.
- **Black Top-Hat (BTH):** `BTH(f,b) = φ(f,b) − f` → resalta estructuras oscuras más pequeñas que `b`.

La elección del **tipo de SE** (disco, cuadrado, cruz, línea) determina qué orientaciones y geometrías
de detalle se enfatizan. El **radio `r`** del SE controla la escala de los detalles capturados.

### 2.4 Torre Top-Hat (método propuesto)

El método propuesto introduce una **descomposición multi-escala morfológica** denominada
*Torre Top-Hat*:

```
Nivel 1 (r=r₀):     WTH₁ = f − γ(f, b_{r₀})         → detalles finos
Nivel 2 (r=2·r₀):   WTH₂ = R₁ − γ(R₁, b_{2r₀})      → detalles medios
   ⋮
Nivel N (r=N·r₀):   WTH_N = R_{N-1} − γ(R_{N-1}, b_{Nr₀})
Residual:           R_N = f − Σ WTH_k               → estructura base
```

donde `R_k` es el residual acumulado. La fusión se realiza capa a capa aplicando una
**regla de selección por actividad local** (energía filtrada con Gaussiana):

```
F_k = mask_k · WTH_k^VIS + (1 − mask_k) · WTH_k^IR
mask_k = 1  si  Actividad(WTH_k^VIS) ≥ Actividad(WTH_k^IR)
```

La imagen fusionada se reconstruye por simple suma de todas las capas fusionadas.

**Parámetros experimentados:**

- Geometrías de SE: `disco`, `cuadrado`, `cruz`
- Número de niveles: `L ∈ {2, 3, 4, 5}`
- Radio base: `r₀ ∈ {2, 3, 5}`

### 2.5 Algoritmos de referencia (baselines)

| Método | Descripción |
|--------|-------------|
| **Promedio** | `F = 0.5·VIS + 0.5·IR` — mínima complejidad, sirve como cota inferior |
| **Pirámide de Laplace** | Descomposición Gaussiana-Laplaciana multi-nivel; fusión por máxima actividad por banda |
| **Curvelet / Wavelet 2D** | Descomposición en subbandasde orientación múltiple; fusión por máxima energía de coeficiente |

### 2.6 Métricas de evaluación

Todas las métricas son **sin referencia** (*no-reference*), ya que no existe una imagen fusionada
óptima conocida.

| Símbolo | Nombre | Interpretación | Dirección |
|---------|--------|----------------|-----------|
| **EN** | Entropía de Shannon | Riqueza de información en la imagen | ↑ mejor |
| **SD** | Desviación Estándar | Contraste global | ↑ mejor |
| **FE** | Factor de Eficiencia de Fusión | EN(fusionada) / EN(fuentes) — ganancia informacional | ↑ mejor |
| **MG** | Gradiente Medio | Nitidez y preservación de bordes | ↑ mejor |
| **MI** | Información Mutua | Similitud de contenido con cada fuente | ↑ mejor |

El análisis estadístico incluye pruebas no paramétricas de Wilcoxon y Friedman para
comparación multi-método.

---

## 3. Estructura del proyecto

```
tesis_mciencias_datos/
│
├── data/
│   ├── raw/                    # Imágenes originales (subcarpetas VIS/ e IR/)
│   └── processed/              # Imágenes preprocesadas (alineadas, normalizadas)
│
├── src/                        # Código fuente principal
│   ├── datasets.py             # Carga y emparejado de imágenes VIS/IR
│   ├── fusion/
│   │   ├── prop_top_hat.py     # Clase TopHatFusion (método propuesto)
│   │   └── comparatives.py    # average_fusion, laplacian_pyramid_fusion, curvelet_fusion
│   ├── metrics/
│   │   └── evaluators.py       # EN, SD, FE, MG, MI, evaluate_all()
│   └── utils/
│       ├── io.py               # save_image, save_metrics_csv
│       └── visualization.py    # plot_comparison, plot_metrics_bar
│
├── notebooks/
│   ├── 01_EDA_dataset.ipynb    # Exploración del dataset (histogramas, estadísticas)
│   ├── 02_fusion_tests.ipynb   # Pruebas visuales rápidas de TopHatFusion
│   └── 03_stats_analysis.ipynb # Análisis estadístico completo de métricas
│
├── experiments/
│   ├── run_all_fusions.py      # Script maestro: ejecuta todos los métodos
│   └── results/
│       ├── fused_images/       # Imágenes fusionadas por método
│       └── metrics_reports/    # all_metrics.csv con resultados cuantitativos
│
├── docs/
│   ├── Tesis_Borrador.docx     # Documento principal (formato Enrique Villalba)
│   ├── referencias/            # Papers y material bibliográfico
│   └── reportes_finales/       # Reportes estadísticos cuali/cuantitativos
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 4. Instalación

**Requisitos:** Python 3.11+

```powershell
# 1. Clonar el repositorio (o situarse en la carpeta del proyecto)
git clone <url-del-repo>
cd tesis_mciencias_datos

# 2. Crear entorno virtual
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install -r requirements.txt
```

**Organizar el dataset** colocando las imágenes dentro de:
```
data/raw/VIS/   ← imágenes en espectro visible  (*.png / *.jpg)
data/raw/IR/    ← imágenes infrarrojas          (*.png / *.jpg)
```
Las imágenes de cada modalidad deben tener el **mismo nombre de archivo** para ser emparejadas
automáticamente.

---

## 5. Uso rápido

```python
from src.datasets import list_pairs, load_pair
from src.fusion import TopHatFusion
from src.metrics import evaluate_all

# Cargar un par VIS/IR
pairs = list_pairs()
vis, ir = load_pair(*pairs[0])

# Fusionar con el método propuesto
fuser = TopHatFusion(se_type='disk', levels=3, base_radius=3)
fused = fuser.fuse(vis, ir)

# Evaluar
metrics = evaluate_all(fused, vis, ir)
print(metrics)
# {'EN': 7.42, 'SD': 0.21, 'FE': 1.05, 'MG': 0.038, 'MI_vis': 3.1, 'MI_ir': 2.9}
```

---

## 6. Ejecución de experimentos

El script `experiments/run_all_fusions.py` procesa automáticamente todos los pares del dataset
con todos los métodos configurados y guarda:
- Imágenes fusionadas en `experiments/results/fused_images/<método>/`
- Métricas consolidadas en `experiments/results/metrics_reports/all_metrics.csv`

```powershell
python experiments/run_all_fusions.py
```

Salida esperada:
```
Procesando 50 pares con 7 métodos...

  OK  Promedio                  | img_001  EN=7.1234
  OK  TopHat_disk_L3            | img_001  EN=7.4421
  ...
Done. 350 registros guardados en experiments/results/metrics_reports/all_metrics.csv
```

---

## 7. Notebooks de análisis

Lanzar Jupyter desde la raíz del proyecto:

```powershell
jupyter notebook
```

| Notebook | Propósito |
|----------|-----------|
| `01_EDA_dataset.ipynb` | Exploración visual y estadística del dataset |
| `02_fusion_tests.ipynb` | Comparación visual rápida de configuraciones de `TopHatFusion` |
| `03_stats_analysis.ipynb` | Análisis cuantitativo completo, boxplots, pruebas de Wilcoxon/Friedman |

---

## 8. Dependencias

| Paquete | Uso |
|---------|-----|
| `numpy` | Operaciones matriciales |
| `opencv-python` | Morfología, pirámides, I/O de imágenes |
| `scikit-image` | Filtros y métricas auxiliares |
| `scipy` | Estadísticas (Wilcoxon, Friedman, entropía) |
| `PyWavelets` | Descomposición wavelet para baseline Curvelet |
| `pandas` | Gestión de resultados en DataFrames/CSV |
| `matplotlib` / `seaborn` | Visualización |
| `jupyter` | Entorno de notebooks |
| `openpyxl` | Exportación a Excel |

---

## 9. Referencias

- Serra, J. (1982). *Image Analysis and Mathematical Morphology*. Academic Press.
- Burt, P. & Adelson, E. (1983). The Laplacian Pyramid as a Compact Image Code. *IEEE Trans. Commun.*
- Candès, E. et al. (2006). Fast Discrete Curvelet Transforms. *SIAM Multiscale Model. Simul.*
- Li, S. et al. (2017). Pixel-level image fusion: A survey of the state of the art. *Information Fusion*, 33, 100–112.
- Ma, J. et al. (2019). Infrared and visible image fusion methods and applications: A survey. *Information Fusion*, 45, 153–178.
- Gonzalez, R. & Woods, R. (2018). *Digital Image Processing* (4th ed.). Pearson.

---

> *Este repositorio forma parte de la investigación de tesis de Maestría en Ciencias de Datos.*  
> *El código está organizado para reproducibilidad total de los experimentos.*
