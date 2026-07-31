# Fusión de Imágenes Infrarrojas y Visibles mediante Morfología Matemática

> **Tesis de Maestría en Ciencias de Datos**
> Universidad Comunera (UCOM)
> Autores: Lic. Juan Pablo Bazán, Ing. Yan Bajac
> Director: D.Sc. Julio César Mello

> **Propuesta central (definitiva):** una fusión VIS/IR basada en transformadas Top-Hat de
> **una sola escala** definida por el radio `r`: se **promedian** las respuestas de cuatro elementos
> estructurantes **lineales** (0°, 45°, 90°, 135°, longitud `2r+1`) y se **suman** a la respuesta de un
> **disco** `B_r` (esquema de Bala et al., 2024); entre fuentes gana el detalle dominante y se
> reconstruye con `F = I_base + m·WTH − m·BTH`. El peso `m` se ajusta por **enjambre de partículas
> (PSO)** con la aptitud publicada `Fo = SSIM_avg + E_n + PSNR_n` (Ortega y Espinoza 2025), eligiendo
> la configuración del enjambre mediante un **barrido de 25 combinaciones** (partículas 2–10 ×
> iteraciones 10–50, Cuadro 1 del mismo trabajo) sobre su **espacio de búsqueda publicado**
> `r ∈ [1,25]`, `m ∈ [0.30, 2.00]`. El radio **no** lo fija la aptitud —`Fo` prefiere `r = 1`— sino que
> es una **decisión de diseño** sobre las métricas de evaluación (ver §2.4).
> **Configuración oficial: r = 25, m = 0.30.**
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
   aumentar el realce y dominan sobre la entropía normalizada; se verificó que `Fo` decrece de forma
   estrictamente monótona en `m` sobre todo el rango, de modo que el óptimo del peso está forzado por
   la forma de la aptitud y no es un artefacto del enjambre.
   **El radio, en cambio, no lo fija el PSO:** dentro de este rango `Fo` prefiere `r = 1`
   (1.7350 frente a 1.7057 en `r = 25`), de manera que `r = 25` es una **decisión de diseño** tomada
   sobre las métricas de evaluación. De las nueve métricas, **cinco favorecen `r = 25`** (EN, SD, FE,
   MG, SF) y las **cuatro de fidelidad favorecen `r = 1`** (SSIM, PSNR, MI_vis, MI_ir), todas con
   `p < 1e-5`. Conviene precisar que `r = 1` **no** desactiva el banco de SE: con `r = 1` el disco es
   la cruz 3×3 y las cuatro líneas orientadas son cuatro máscaras 3×3 distintas. **Configuración
   oficial:** `r = 25`, `m = 0.30`, adoptada priorizando la capacidad de realce y reconociendo que la
   elección del radio se apoya en parte del mismo criterio con el que luego se evalúa. Tabla completa:
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
| **FE** | Ganancia de entropía sobre las fuentes — `EN(F) / media(EN(VIS), EN(IR))` | ↑ |
| **MG** | Gradiente medio | ↑ |
| **MI_vis / MI_ir** | Información mutua con cada fuente | ↑ |
| **SF** | Frecuencia espacial | ↑ |
| **SSIM** | Similitud estructural promedio con las fuentes | ↑ |
| **PSNR** | Relación señal-ruido de pico frente a ambas fuentes | ↑ |

> **Nota sobre FE.** Dentro de un mismo par VIS/IR el denominador de `FE` no depende del método, de
> modo que `FE` es la entropía `EN` reescalada por una constante por escena: produce los mismos rangos
> intra-bloque, el mismo χ² de Friedman y los mismos signos de Wilcoxon. **No es evidencia
> independiente de `EN`** y no se cuenta como métrica adicional. Se conserva porque el trabajo de
> referencia la reporta. El ranking se publica también sin `FE` (columna `avg_rank_sin_FE`).

Análisis estadístico no paramétrico: **Friedman** global por métrica, **Wilcoxon** pareado con
corrección de **Holm** y tamaño de efecto rank-biserial, y **ranking promedio de rangos intra-bloque**
(el acompañante estándar de Friedman) respetando la dirección de cada métrica. Implementación: `src/metrics/evaluators.py` y `experiments/run_stats_analysis.py`.

---

## 3. Resultados principales

**Calidad de imagen — TNO Image Fusion Dataset (20 pares).** La *Propuesta Novedosa*
(`r=25, m=0.30`) **lidera la entropía** (`EN = 6.986`) y la **ganancia de entropía sobre las
fuentes** (`FE = 1.105`, que es `EN` reescalada), y queda **segunda** en desviación estándar
(`SD = 0.144`), gradiente medio (`MG = 0.035`) y frecuencia espacial (`SF = 17.44`); cede, en cambio,
en las métricas de fidelidad a las fuentes (`SSIM = 0.658`, `PSNR = 16.84`) y en información mutua,
lideradas por los métodos multiescala.

> **Nota sobre el corpus.** El subconjunto original tenía un par defectuoso,
> `Athena_heather_IR_hei_vis_g`: su archivo del canal visible era una copia byte a byte del
> infrarrojo (mismo md5), porque el script de preparación tomó `IR_hei_vis_g.bmp` como si fuera el
> nombre de una escena. No era un par VIS/IR sino la misma imagen repetida, y con VIS = IR todo
> método que devolviera la entrada intacta obtenía `SSIM = 1` y un PSNR que desbordaba la escala,
> inflando los promedios de fidelidad de los cinco métodos multiescala. Ese par se **excluye**
> (`src/datasets.PARES_EXCLUIDOS`) y se **sustituye** por `Triclobs_Kaptein_1123`, tomado del TNO
> original: una escena nueva, la más citada de la literatura de fusión, donde el peatón solo es
> visible en el IR mientras el edificio, el sendero y la vegetación tienen su detalle en el VIS.
> El corpus efectivo son **20 pares** sin ningún caso degenerado.

| Método | EN ↑ | SD ↑ | FE ↑ | MG ↑ | MI_vis ↑ | MI_ir ↑ | SF ↑ | SSIM ↑ | PSNR ↑ |
|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Pirámide de Laplace (LP) | 6.840 | **0.155** | 1.081 | 0.025 | **1.924** | **0.918** | 13.22 | 0.706 | 14.94 |
| Ratio of low-pass Pyramid (RP) | 6.810 | 0.127 | 1.077 | 0.028 | 0.949 | 0.650 | 13.62 | 0.705 | 17.37 |
| Wavelet discreta (DWT) | 6.682 | 0.117 | 1.057 | 0.028 | 1.076 | 0.666 | 14.19 | 0.701 | 17.59 |
| Dual-Tree Complex Wavelet (DTCWT) | 6.688 | 0.117 | 1.058 | 0.025 | 1.078 | 0.673 | 13.20 | **0.725** | 17.60 |
| Curvelet (CVT) | 6.644 | 0.113 | 1.051 | 0.026 | 1.096 | 0.669 | 13.34 | 0.716 | **17.65** |
| Top-Hat clásico | 6.922 | 0.135 | 1.095 | **0.048** | 0.787 | 0.493 | **23.10** | 0.564 | 16.87 |
| **Propuesta Novedosa (r=25, m=0.30)** | **6.986** | 0.144 | **1.105** | 0.035 | 0.897 | 0.600 | 17.44 | 0.658 | 16.84 |

En el **ranking agregado** de las nueve métricas —calculado como **promedio de rangos
intra-bloque**, el acompañante estándar de Friedman— la propuesta ocupa el **1.º lugar (3.394)**:
Propuesta 3.394 · LP 3.911 · Top-Hat clásico 3.944 · RP 3.983 · DTCWT 4.111 · DWT 4.211 · CVT 4.444. El resultado es robusto: se mantiene primera al excluir `FE` por redundante (3.631) y al
agregar por escena física. La versión anterior de este análisis rankeaba las *medias* en lugar de
promediar rangos por bloque, lo que descartaba la estructura de bloques que la propia prueba de
Friedman utiliza; se conserva en la columna `avg_rank_medias` solo para trazabilidad.

En los contrastes de **Wilcoxon-Holm** (45, propuesta vs. los cinco métodos del estado del arte)
resulta significativamente **mejor en 25**, peor en 17 y sin diferencia en 3: gana a **los cinco** en
`EN`, `FE`, `MG` y `SF`, y pierde con los cinco en `SSIM`.

Frente al **Top-Hat clásico** —la referencia morfológica directa— la propuesta gana de forma
significativa en **seis de las nueve métricas** (`EN`, `SD`, `FE`, `MI_vis`, `MI_ir` y `SSIM`:
0.658 vs 0.564), cede de forma significativa en gradiente medio y frecuencia espacial, donde el disco
único inyecta el detalle sin ponderación, y no hay diferencia significativa en `PSNR`
(`p_Holm = 0.92`). Este contraste se publica en `wilcoxon_results.csv`; la versión anterior del script
solo cruzaba los métodos morfológicos contra el estado del arte y no los comparaba entre sí.

> **Alcance de esta comparación.** No aísla el aporte del banco disco + líneas: los dos operadores no
> comparten hiperparámetros (el clásico usa `r = 5`, `m = 1`; la propuesta `r = 25`, `m = 0.30`), de
> modo que la diferencia refleja conjuntamente el cambio de operador y el de `(r, m)`. Aislar el
> aporte del banco requiere un experimento con `(r, m)` idénticos.

Los resultados **escena por escena** (las 20 imágenes) están en el informe de avances (Tablas 2a-2e,
con el formato del Cuadro 2 del trabajo de referencia) y en la hoja `Benchmark_por_Escena` del libro
de tablas.

**PSO por escena (Anexos 1-20).** Replicando los anexos del trabajo de referencia, el Cuadro 1
completo se ejecuta sobre **cada** par: 20 escenas × 25 configuraciones = 500 corridas
(`experiments/pso_por_imagen.py` → `pso_por_imagen.csv`; los anexos del informe de avances y la hoja
`PSO_por_Escena`). Dos observaciones sobre el comportamiento de `(r, m)`:

- El **radio varía** con la configuración del enjambre: 17 radios distintos en el conjunto de los
  anexos, entre 2 y 5 valores diferentes por escena. El radio que maximiza `Fo` es `r = 1` en 18 de
  las 20 escenas.
- El **peso se fija en `m = 0.30`** (en 20 de 20 escenas) porque `Fo` **decrece de forma estrictamente
  monótona** al aumentar `m` en todo el rango publicado —barrido de paso 0.05: cero tramos crecientes
  de los 34 evaluados, con `r = 1` y con `r = 25`—, de modo que el máximo se ubica necesariamente en
  el límite inferior del intervalo. No es una limitación de la búsqueda: las únicas 17 filas de 500
  con `m ≠ 0.30` corresponden a configuraciones de pocas partículas o iteraciones que no convergieron.

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
├── data/raw/                       # VIS/ e IR/ (21 archivos; 1 par corrupto excluido -> 20 válidos)
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
│   ├── pso_por_imagen.py           # Cuadro 1 completo sobre cada par -> 500 corridas (Anexos 1-20)
│   ├── make_montajes_cualitativos.py # 20 montajes por escena (propuesta en rojo)
│   ├── make_figuras_metodo.py      # Figuras del método (banco de SE, ejemplo de modalidades)
│   ├── make_figura_detecciones_m3fd.py # Prueba visual M3FD (detecciones VIS/IR/fusión)
│   ├── make_avances_report.py      # Regenera docs/Avances_Tesis.pdf (HTML -> PDF con Edge)
│   ├── make_avances_excel.py       # Regenera docs/Avances_Tesis_Tablas.xlsx (12 hojas)
│   ├── detection_llvip/            # Reentrenamiento de detección con LLVIP (mAP concluyente)
│   │   ├── prepare_llvip.py        #   genera datasets YOLO fusionados por método (labels compartidas)
│   │   └── train_eval_llvip.py     #   entrena YOLOv8 por método y compara mAP (CSV acumulativo)
│   └── results/metrics_reports/    # all_metrics.csv, ranking, friedman, wilcoxon, detección
│
├── notebooks/                      # 01 (EDA) y 03 (análisis estadístico)
├── docs/
│   ├── Tesis_Borrador_V3.docx      # Documento principal (propuesta suma r=25; formato UCOM/Villalba)
│   ├── Avances_Tesis_restringido.pdf  # Informe de avances (54 págs, incluye Anexos 1-20)
│   ├── Avances_Tesis_libre.pdf     # Idem con el rango del peso ampliado
│   ├── Auditoria_Interna.md        # Auditoría del pipeline: defectos, correcciones y alcance
│   ├── Avances_Tesis_Tablas.xlsx   # Libro de tablas (12 hojas, detalle por escena)
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

# 3b. PSO por escena: el Cuadro 1 completo sobre cada par (500 corridas, ~3 min con 10 procesos)
python experiments/pso_por_imagen.py --procesos 10

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
