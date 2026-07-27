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
> **enjambre de partículas (PSO)** con la aptitud publicada `Fo = SSIM_avg + E_n + PSNR_n` (Ortega y
> Espinoza 2025), eligiendo la configuración del enjambre mediante un **barrido de 25 combinaciones**
> (partículas 2–10 × iteraciones 10–50, Cuadro 1 del mismo trabajo) sobre su **espacio de búsqueda
> publicado** `r ∈ [1,25]`, `m ∈ [0.30, 2.00]` → **configuración oficial: r = 25, m = 0.30**.
> Se compara contra **seis métodos**: cinco del estado del arte —Pirámide de Laplace (LP), Ratio of
> low-pass Pyramid (RP, Toet 1989), Wavelet discreta (DWT), Dual-Tree Complex Wavelet (DTCWT) y
> Curvelet (CVT)— más la **metodología clásica de la transformada Top-Hat**, sobre el **TNO Image
> Fusion Dataset** (20 pares) con **nueve métricas sin referencia**, todas de tipo «mayor es mejor».
> El impacto en **detección de objetos** se evalúa con dos experimentos: YOLOv8 reentrenado por
> método sobre **LLVIP** (mAP) y un **detector único VIS+IR** sobre **M3FD** con clases
> complementarias (People/IR, Lamp/VIS).

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
8. [Evaluación orientada a tarea (detección LLVIP y M3FD)](#8-evaluación-orientada-a-tarea-detección-llvip-y-m3fd)
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
   el Cuadro 1 de Ortega y Espinoza 2025), sobre el **espacio de búsqueda publicado**
   `r ∈ [1,25]` y `m ∈ [0.30, 2.00]`, maximizando la aptitud del mismo trabajo
   `Fo = SSIM_avg + E_n + PSNR_n`. Las **25 configuraciones convergen al mismo peso**,
   `m* = 0.30` (límite inferior del rango), porque los dos términos de fidelidad de `Fo` decrecen al
   aumentar el realce y dominan sobre la entropía normalizada. Para el radio, `Fo` favorece el valor
   trivial `r = 1` —que desactiva el banco de SE—, mientras que las nueve métricas de evaluación
   (todas «mayor es mejor») favorecen `r = 25`: a igual peso, `r = 25` supera a `r = 1` en entropía,
   contraste, contenido de bordes, gradiente medio y frecuencia espacial. **Configuración oficial:**
   `r = 25`, `m = 0.30`. Tabla completa:
   `experiments/results/metrics_reports/pso_grid_search_fo_propuesta.csv`.

Implementación: `src/fusion/optimal_top_hat.py` (`fuse_optimal(vis, ir, r, m, mode="sum")`);
barrido en `experiments/pso_grid_search_fo.py`. El análisis que sustenta la elección de `m` está en
`experiments/analisis_aptitud_operador.py`, `barrido_metricas_vs_m.py` y `comparativa_visual_m.py`.

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

Evaluación con **nueve métricas sin referencia**, alineadas con la metodología de referencia y
**todas de tipo «mayor es mejor»** (el evaluador implementa además Qabf, Nabf, SCD, VIF, FMI y los
índices de Piella, que no se reportan en el análisis).

| Símbolo | Nombre | Dirección |
|---------|--------|-----------|
| **EN** | Entropía de Shannon | ↑ |
| **SD** | Desviación estándar (contraste) | ↑ |
| **FE** | Eficiencia / entropía de bordes | ↑ |
| **MG** | Gradiente medio | ↑ |
| **MI_vis / MI_ir** | Información mutua con cada fuente | ↑ |
| **SF** | Frecuencia espacial | ↑ |
| **SSIM** | Similitud estructural promedio con las fuentes | ↑ |
| **PSNR** | Relación señal-ruido de pico frente a ambas fuentes | ↑ |

Análisis estadístico no paramétrico: **Friedman** global por métrica, **Wilcoxon** pareado con
corrección de **Holm** y tamaño de efecto rank-biserial, y **ranking promedio** respetando la dirección
de cada métrica. Implementación: `src/metrics/evaluators.py` y `experiments/run_stats_analysis.py`.

---

## 3. Resultados principales

**Calidad de imagen — TNO Image Fusion Dataset (20 pares).** La *Propuesta Novedosa*
(`r=25, m=0.30`) **lidera la entropía** (`EN = 6.989`) y el **contenido de bordes**
(`FE = 1.105`) del benchmark, y queda **segunda** en desviación estándar (`SD = 0.148`), gradiente
medio (`MG = 0.035`) y frecuencia espacial (`SF = 17.34`); cede, en cambio, en las métricas de
fidelidad a las fuentes (`SSIM = 0.668`, `PSNR = 17.25`) y en información mutua, lideradas por los
métodos multiescala.

| Método | EN ↑ | SD ↑ | FE ↑ | MG ↑ | MI_vis ↑ | MI_ir ↑ | SF ↑ | SSIM ↑ | PSNR ↑ |
|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Pirámide de Laplace (LP) | 6.835 | **0.155** | 1.079 | 0.025 | **2.118** | **1.072** | 13.04 | 0.721 | 20.27 |
| Ratio of low-pass Pyramid (RP) | 6.829 | 0.130 | 1.079 | 0.027 | 1.170 | 0.881 | 13.34 | 0.721 | 21.97 |
| Wavelet discreta (DWT) | 6.700 | 0.120 | 1.059 | 0.027 | 1.285 | 0.881 | 13.93 | 0.716 | 22.78 |
| Dual-Tree Complex Wavelet (DTCWT) | 6.706 | 0.121 | 1.060 | 0.025 | 1.289 | 0.891 | 13.03 | **0.739** | 22.79 |
| Curvelet (CVT) | 6.665 | 0.117 | 1.053 | 0.026 | 1.304 | 0.884 | 13.15 | 0.731 | **22.84** |
| Top-Hat clásico | 6.933 | 0.139 | 1.096 | **0.047** | 0.872 | 0.586 | **22.86** | 0.578 | 17.49 |
| **Propuesta Novedosa (r=25, m=0.30)** | **6.989** | 0.148 | **1.105** | 0.035 | 0.962 | 0.671 | 17.34 | 0.668 | 17.25 |

En el **ranking agregado** de las nueve métricas la propuesta ocupa el **2.º lugar (3.67)**, detrás de
la pirámide de Laplace (3.44) y por delante de DTCWT y del Top-Hat clásico (4.00). En los contrastes
de **Wilcoxon-Holm** (45, propuesta vs. los cinco métodos del estado del arte) resulta
significativamente **mejor en 24**, peor en 19 y sin diferencia en 2: gana a **los cinco** en `EN`,
`FE`, `MG` y `SF`, y a cuatro de cinco en `SD`.

Frente al **Top-Hat clásico** —la referencia morfológica directa— la propuesta gana de forma
significativa en **seis de las nueve métricas** (`EN`, `SD`, `FE`, `MI_vis`, `MI_ir` y `SSIM`:
0.668 vs 0.578) y cede solo en gradiente medio y frecuencia espacial, donde el disco único inyecta el
detalle sin ponderación. La diferencia entre ambos aísla el aporte del banco disco + líneas y del
ajuste `(r, m)` por PSO. Los resultados **escena por escena** (las 20 imágenes) están en el informe de
avances, con el formato del Cuadro 2 del trabajo de referencia.

**Detección — LLVIP (YOLOv8n reentrenado por método, mismas etiquetas, solo cambia la fusión).**
Toda fusión supera con claridad al VIS solo, pero ninguna al IR solo (el peatón nocturno es
esencialmente térmico); la propuesta queda en el **extremo inferior de la banda de fusiones**.

| Entrada | mAP@0.5 ↑ | mAP@0.5:0.95 ↑ |
|---------|:---:|:---:|
| **IR (solo)** | **0.957** | **0.663** |
| Pirámide de Laplace (LP) | 0.949 | 0.651 |
| Dual-Tree Complex Wavelet (DTCWT) | 0.948 | 0.633 |
| Wavelet discreta (DWT) | 0.946 | 0.614 |
| Curvelet (CVT) | 0.941 | 0.639 |
| Top-Hat clásico | 0.938 | 0.609 |
| Ratio Pyramid (RP) | 0.926 | 0.538 |
| **Propuesta Novedosa (r=25, m=0.30)** | 0.913 | 0.617 |
| VIS (solo) | 0.808 | 0.451 |

**El peso de contraste: métricas de actividad vs. desempeño en tarea.** El análisis de `m`
(`docs/figures/fig_aptitud_vs_operador.png` y `fig_comparativa_m.png`) documenta el hallazgo
metodológico central del trabajo: (a) el operador propuesto extrae **4.3 veces** más energía de
detalle que el disco único, de modo que su peso óptimo es proporcionalmente menor —`m·|W|` es lo que
fija el realce—; (b) `Fo` decrece de forma **monótona** al aumentar `m` en ambos operadores, por lo
que su óptimo cae siempre en el piso del rango permitido; y (c) las métricas de actividad crecen con
el realce hasta que la **saturación** degrada la imagen (12–20 % de píxeles saturados en `m = 2`
frente a ~1 % en `m = 0.30`). En consecuencia, **optimizar las métricas de actividad y optimizar el
desempeño de detección son objetivos distintos**, y ambos criterios deben reportarse por separado.

**Detección — M3FD (clases complementarias, un único detector VIS+IR).** Con dos clases de
visibilidad opuesta (**People** domina en IR: 0.220 vs 0.178; **Lamp** solo se ve en VIS: 0.135 vs
0.018), **todas las fusiones recuperan ambas clases en una sola imagen** —algo que el IR no logra, al
ser ciego a las luces—. La Ratio Pyramid alcanza el mejor promedio del par (0.165), el único valor que
supera a **ambas** modalidades individuales (VIS 0.157, IR 0.119); la propuesta alcanza un promedio
intermedio (0.124; People 0.146 y Lamp 0.101). La prueba visual con las detecciones dibujadas
(`docs/figures/fig_m3fd_detecciones.png`) es elocuente: en una escena la fusión detecta **seis
personas** frente a dos del VIS y dos del IR, y en otra conserva las **cuatro luces** que el IR no
detecta en absoluto. Resultados: `detection_m3fd_map.csv` (ver §8.1).

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
│   │   ├── optimal_top_hat.py      # fuse_optimal (PROPUESTA NOVEDOSA, mode="sum", r=25, m=0.30)
│   │   └── comparatives.py         # LP / RP / DWT / DTCWT / CVT / Top-Hat clásico
│   ├── metrics/
│   │   └── evaluators.py           # evaluador completo; el análisis reporta nueve métricas
│   └── utils/                      # io, visualización, reorganización del dataset
│
├── experiments/
│   ├── run_all_fusions.py          # Benchmark: los 7 métodos sobre el dataset -> all_metrics.csv
│   ├── run_stats_analysis.py       # Friedman + Wilcoxon(Holm) + ranking
│   ├── pso_grid_search_fo.py       # Barrido PSO 5x5 con Fo y rango publicado -> m* = 0.30
│   ├── analisis_aptitud_operador.py # Ganancia del operador y descomposición de Fo
│   ├── barrido_metricas_vs_m.py    # Las nueve métricas en función de m
│   ├── comparativa_visual_m.py     # Control visual de saturación por peso m
│   ├── make_montajes_cualitativos.py # 20 montajes por escena (propuesta en rojo)
│   ├── make_figuras_metodo.py      # Figuras del método (banco de SE, ejemplo de modalidades)
│   ├── make_figura_detecciones_m3fd.py # Prueba visual M3FD (detecciones VIS/IR/fusión)
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
│   ├── Tesis_Defensa_Presentacion.pptx # Presentación de defensa (19 láminas, notas del orador)
│   └── figures/                    # Figuras del libro (fuente y montajes cualitativos)
│
├── ejecutar_llvip.ps1              # Lanzador del pipeline LLVIP en la PC (GPU)
├── ejecutar_m3fd.ps1               # Lanzador del experimento de clases complementarias (M3FD)
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
fused = fuse_optimal(vis, ir, r=25, m=0.30, mode="sum")

metrics = evaluate_all(fused, vis, ir)
print(metrics)   # el análisis usa: EN, SD, FE, MG, MI_vis, MI_ir, SF, SSIM, PSNR
```

---

## 7. Ejecución de experimentos

```powershell
# 1. Fusiones (todos los métodos) y métricas -> all_metrics.csv
python experiments/run_all_fusions.py

# 2. Análisis estadístico (Friedman, Wilcoxon+Holm, ranking)
python experiments/run_stats_analysis.py

# 3. Barrido de configuraciones PSO con Fo y el rango publicado -> m* = 0.30
python experiments/pso_grid_search_fo.py --operator propuesta

# 4. Montajes cualitativos (20 escenas, propuesta en rojo)
python experiments/make_montajes_cualitativos.py
```

Salidas en `experiments/results/metrics_reports/`: `all_metrics.csv`, `descriptive_means.csv`,
`ranking_methods.csv`, `friedman_results.csv`, `wilcoxon_results.csv`.

---

## 8. Evaluación orientada a tarea (detección LLVIP y M3FD)

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

### 8.1 Clases complementarias (M3FD): un modelo, dos objetos, una imagen fusionada

Experimento complementario sobre **M3FD** (TarDAL, CVPR 2022; 4.200 pares VIS/IR con 6 clases
YOLO): un **único** YOLOv8 se entrena con imágenes VIS **e** IR mezcladas (con sus etiquetas) y se
evalúa **por inferencia** sobre la validación en cada modalidad y en cada método de fusión. Las
clases son complementarias —**People** domina en IR (firma térmica) y **Lamp** en VIS—, de modo que
solo la imagen fusionada permite detectar ambas a la vez. Se comparan las dos modalidades
individuales y los siete métodos del benchmark, incluida la propuesta en su configuración oficial
(`Propuesta_Novedosa`: r=25, m=0.30).

```powershell
# Requiere M3FD (Detection) descargado: https://github.com/JinyuanLiu-CV/TarDAL
powershell -ExecutionPolicy Bypass -File .\ejecutar_m3fd.ps1 -M3FD "data\M3FD"
```

**Resultados** (`detection_m3fd_map.csv`): la complementariedad es extrema — el IR domina People
(AP@0.5 = 0.220) pero es prácticamente ciego a Lamp (0.018); el VIS presenta el patrón espejo
(0.178 / 0.135). **Todas las fusiones recuperan ambas clases en una sola imagen**, algo que el IR no
logra. La Ratio Pyramid alcanza el mejor promedio del par (0.165) y es la única entrada que supera a
ambas modalidades individuales (VIS 0.157, IR 0.119); la propuesta alcanza un promedio intermedio
(0.124; People 0.146 y Lamp 0.101): el realce elevado que optimiza las métricas de actividad no
favorece al detector.

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
