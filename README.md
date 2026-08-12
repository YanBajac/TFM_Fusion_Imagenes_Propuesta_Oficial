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
> wavelet db4 rotulada CVT (ver §2.5)— más la **metodología clásica de la transformada Top-Hat**, sobre el **TNO Image
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
   - [Segundo aporte: auditoría del protocolo de evaluación](#31-segundo-aporte-auditoría-del-protocolo-de-evaluación)
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
| **Wavelet Daubechies db4 (rotulada CVT)** | Descomposición wavelet 2D (db4, 3 niveles); máxima magnitud en detalle, promedio en aproximación. **No es la transformada curvelet**: comparte algoritmo con la DWT y solo cambia la base — igualando la base, ambas dan resultados idénticos | Daubechies (1992); la aproximación por wavelet se emplea en la literatura en lugar de Candès et al. (2006) |
| **Top-Hat clásico** | Fusión morfológica básica: disco `B_5`, `F = I_base + máx(WTH) − máx(BTH)` sin ponderación | — |

Implementación: `src/fusion/comparatives.py`. Todos se evalúan con la misma implementación de
métricas, sobre los mismos 20 pares.

> **Sobre el recuento de familias.** Los cinco métodos de referencia cubren en rigor **cuatro
> familias**: pirámides (LP, RP), wavelets separables (DWT y el comparativo rotulado CVT, que
> comparten algoritmo), wavelets complejas (DTCWT) y morfología (Top-Hat clásico). Conviene
> declararlo así y no hablar de cinco familias independientes.

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
| Wavelet db4 (CVT) | 6.644 | 0.113 | 1.051 | 0.026 | 1.096 | 0.669 | 13.34 | 0.716 | **17.65** |
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
(`p_Holm = 0.674`). Este contraste se publica en `wilcoxon_results.csv`; la versión anterior del script
solo cruzaba los métodos morfológicos contra el estado del arte y no los comparaba entre sí.

> **Alcance de esta comparación.** No aísla el aporte del banco disco + líneas: los dos operadores no
> comparten hiperparámetros (el clásico usa `r = 5`, `m = 1`; la propuesta `r = 25`, `m = 0.30`), de
> modo que la diferencia refleja conjuntamente el cambio de operador y el de `(r, m)`. Aislar el
> aporte del banco requiere un experimento con `(r, m)` idénticos.

Los resultados **escena por escena** (las 20 imágenes) están en el informe de avances (Tablas 4a-4e,
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
| **IR (solo)** | **0.971** | **0.621** |
| Pirámide de Laplace (LP) | 0.952 | 0.565 |
| Dual-Tree Complex Wavelet (DTCWT) | 0.949 | 0.603 |
| Wavelet db4 (CVT) | 0.940 | 0.608 |
| Wavelet discreta (DWT) | 0.939 | 0.602 |
| Top-Hat clásico | 0.933 | 0.609 |
| **Propuesta Novedosa (r=25, m=0.30)** | 0.906 | 0.581 |
| Ratio Pyramid (RP) | 0.906 | 0.500 |
| VIS (solo) | 0.813 | 0.450 |

**El peso de contraste: métricas de actividad vs. desempeño en tarea.** El análisis de `m`
(`docs/figures/fig_aptitud_vs_operador.png` y `fig_comparativa_m.png`) documenta el hallazgo
metodológico central del trabajo: (a) el operador propuesto extrae **4,21** veces más energía de
detalle que el disco único, de modo que su peso óptimo es proporcionalmente menor —`m·|W|` es lo que
fija el realce—; (b) `Fo` decrece de forma **monótona** al aumentar `m` en ambos operadores, por lo
que su óptimo cae siempre en el piso del rango permitido; y (c) las métricas de actividad crecen con
el realce hasta que la **saturación** degrada la imagen (del 0,73 % de pixeles saturados en m = 0,30 al 6,50 % en m = 1 y el 21,62 % en m = 2 en `m = 2`
frente a ~1 % en `m = 0.30`). En consecuencia, **optimizar las métricas de actividad y optimizar el
desempeño de detección son objetivos distintos**, y ambos criterios deben reportarse por separado.

**Detección — M3FD (clases complementarias, un único detector VIS+IR).** Con dos clases de
visibilidad desigual, la complementariedad es **real pero asimétrica**: el IR domina en **People**
(`AP@0.5 = 0.779` frente a 0.621 del VIS) y se degrada en **Lamp** (0.348), mientras el VIS sostiene
ambas clases en un nivel parejo (0.621 y 0.616). **No hay patrón espejo y ninguna modalidad es
ciega**: el argumento a favor de fusionar es que ninguna es la mejor en las dos clases a la vez.
La Ratio Pyramid es la única entrada cuyo promedio del par (0.622) supera a las dos modalidades
(VIS 0.618, IR 0.563); la propuesta alcanza 0.564, al nivel del IR solo y por debajo del VIS.

En el **conteo por escena** —232 escenas que contienen simultáneamente las dos clases, que es la
operacionalización que pide el objetivo— la propuesta recupera ambas en el **50.0 %** frente al
**53.0 % del visible solo**, con 8 escenas ganadas y 15 perdidas (McNemar exacto `p = 0.2100`), y
resuelve 2 de las 90 escenas críticas. El mejor caso es la pirámide de Laplace (57.8 %) y cuatro de
las siete fusiones quedan por debajo del visible. La prueba visual
(`docs/figures/fig_m3fd_detecciones.png`) muestra 11 personas en la fusión frente a 3 del VIS y 10
del IR en una escena, y 7 luces frente a 5 del VIS y 1 del IR en la otra. Resultados:
`detection_m3fd_map.csv` y `complementariedad_resumen.csv` (ver §8.1).

### 3.1 Segundo aporte: auditoría del protocolo de evaluación

El trabajo no solo propone el operador: **audita el criterio con que se lo juzga**, usando el propio
desarrollo como caso de estudio. Cinco controles, todos versionados y reproducibles:

- **Control negativo** (`run_control_negativo.py`). Con las nueve métricas, una fusión artificial de
  **ruido gaussiano** con `σ = 0.20` queda **3.ª de 14 entradas** (rango 6.767), por delante de cinco
  de los seis métodos comparativos, y su rango **mejora** al aumentar el ruido
  (8.917 → 7.850 → 6.972 → 6.767 para σ = 0.02 / 0.05 / 0.10 / 0.20). El fallo es específico de la
  varianza: el desenfoque sí se penaliza. Basta incorporar `Nabf` —la única métrica implementada con
  dirección inversa— para que el ruido caiga al 7.º puesto, y al último con las diecisiete.
- **Redundancia interna.** `FE = EN(fusión) / media(EN de las fuentes)`, y ese denominador no depende
  del método: dentro de cada par `FE` es `EN` reescalada, con rangos intra-bloque idénticos y el mismo
  χ² de Friedman (88.2857). Las dimensiones efectivas son **ocho, no nueve**.
- **Sensibilidad a la composición del criterio.** Con las nueve métricas la propuesta es 1.ª (3.394);
  con las diecisiete que el mismo evaluador ya calcula desciende a 3.ª (3.459) y el primer puesto pasa
  a la pirámide de Laplace (3.147). **No cambia ninguna imagen fusionada**: cambia el conjunto de
  métricas.
- **Ajuste simétrico** (`run_ajuste_comparativos.py`). Concediendo a los comparativos el mismo paso de
  ajuste, ninguna de las cinco configuraciones de referencia alcanza a la propuesta, pero el Top-Hat
  clásico la supera por 0.061 — con `m = 1`, más del triple del peso. Ejecutándolo a peso igualado
  (`r = 25, m = 0.30` en ambos) la propuesta conserva el primer lugar: 3.528 frente a 3.694.
- **Ablación del banco** (`run_ablacion_banco.py`). Con `(r, m)` fijos, la suma de ramas es el mejor de
  los seis brazos con las nueve métricas (3.222 frente a 3.367 del disco único); al retirar `FE` los
  brazos se comprimen (3.444–3.631) y la suma baja al 4.º lugar. La imagen base sin operador queda
  última, de modo que el mérito no proviene de la base.

La conclusión metodológica: un protocolo de evaluación de fusión debe incluir al menos una métrica que
penalice artefactos, declarar la redundancia entre sus componentes y separar el ajuste de
hiperparámetros del criterio de evaluación. Detalle en la sección 5.8 del libro.

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
│   ├── run_control_negativo.py     # Auditoría: ruido y desenfoque en el ranking (H3)
│   ├── run_ablacion_banco.py       # Auditoría: los 6 brazos del banco a (r, m) fijos (H7)
│   ├── run_ajuste_comparativos.py  # Auditoría: ajuste simétrico de los comparativos
│   ├── run_ranking_mas_nabf.py     # Auditoría: el ranking con las nueve + Nabf (la recomendación
│   │                               #   del trabajo aplicada a su propio benchmark)
│   ├── run_correlacion_calidad_deteccion.py # ¿el orden de calidad predice el mAP? (H6)
│   ├── run_escenas_distintas.py    # Cuántas escenas físicas hay en los 20 pares, con el criterio
│   │                               #   tomado de la estructura de carpetas del TNO
│   ├── run_saturacion_vs_m.py      # Recorte por saturación en función de m
│   ├── run_complementariedad_escenas.py # Conteo por escena en M3FD (232 escenas, H6)
│   ├── make_montajes_cualitativos.py # 20 montajes por escena (propuesta en rojo)
│   ├── make_figuras_metodo.py      # Figuras del método (banco de SE, ejemplo de modalidades)
│   ├── make_figuras_libro.py       # Figuras de datos del libro (7, 8, 10 y 11) desde los CSV
│   ├── make_figuras_deck.py        # Los tres gráficos del deck desde los CSV
│   ├── make_figura_detecciones_m3fd.py # Prueba visual M3FD (detecciones VIS/IR/fusión)
│   ├── make_avances_report.py      # Regenera docs/Avances_Tesis.pdf (HTML -> PDF con Edge)
│   ├── make_avances_excel.py       # Regenera docs/Avances_Tesis_Tablas.xlsx (12 hojas)
│   ├── verificar_entregables.py    # Contrasta los CUATRO entregables contra los CSV (un comando)
│   ├── verificar_libro.py          # Contrasta el PDF del libro contra los CSV y el índice
│   ├── verificar_bibliografia.py   # Contrasta las referencias contra Crossref y OpenAlex
│   ├── verificar_corpus.py         # Comprueba data/raw contra el manifiesto (md5, pares, canales)
│   ├── detection_llvip/            # Reentrenamiento de detección con LLVIP (mAP concluyente)
│   │   ├── prepare_llvip.py        #   genera datasets YOLO fusionados por método (labels compartidas)
│   │   └── train_eval_llvip.py     #   entrena YOLOv8 por método y compara mAP (CSV acumulativo)
│   ├── detection_m3fd/             # Detección de clases complementarias con M3FD (§8.1)
│   │   ├── prepare_m3fd.py         #   fusiona y arma las particiones (2.000 / 500 / 499)
│   │   └── train_eval_m3fd.py      #   un único modelo mixto VIS+IR, inferencia por entrada
│   └── results/metrics_reports/    # all_metrics.csv, ranking, friedman, wilcoxon, detección
│
├── notebooks/                      # 01 (EDA) y 03 (análisis estadístico)
├── docs/
│   ├── Tesis_Borrador_V3.docx      # Documento principal (74 págs; formato UCOM/Villalba)
│   ├── Tesis_Borrador_V3.pdf       #   el mismo, renderizado, para leerlo sin Word
│   ├── Avances_Tesis.pdf           # Informe de avances (85 págs; resumen llano, índice y Anexos A1-A20)
│   ├── Avances_Tesis_Tablas.xlsx   # Libro de tablas (13 hojas, detalle por escena)
│   ├── Tesis_Defensa_Presentacion.pptx # Defensa (22 láminas + reserva, notas del orador)
│   ├── Tesis_Defensa_Presentacion.pdf  #   el mismo, renderizado
│   ├── ESTADO_Y_PENDIENTES.md      # Estado vivo: qué está cerrado, qué falta y cómo correr todo
│   ├── Auditoria_Bibliografia.md   # Auditoría de las referencias contra Crossref y OpenAlex
│   ├── Plan_Deck_Defensa.md        # Plan de edición del deck (22 láminas)
│   ├── historial/                  # Documentos de trabajo ya cumplidos; NO son el estado actual
│   ├── fuentes/                    # PDF de las fuentes (no se versionan) y datos de verificación
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

**Requisitos:** Python 3.11 o superior. Para los experimentos de detección hace falta además una
GPU con CUDA; todo lo demás corre en CPU.

### 5.1. Bajar el código e instalar

```powershell
git clone https://github.com/YanBajac/TFM_Fusion_Imagenes_Propuesta_Oficial.git
cd TFM_Fusion_Imagenes_Propuesta_Oficial

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 5.2. Conseguir las imágenes

**Las imágenes no vienen en el repositorio.** Pesan y tienen su propia licencia, así que `data/raw`
está excluido del control de versiones. Lo que sí viaja es
[`data/raw/MANIFIESTO_CORPUS.csv`](data/raw/MANIFIESTO_CORPUS.csv), que trae por cada archivo su
tamaño, su **md5** y la **ruta exacta de origen** dentro del dataset original. Con eso el corpus se
reconstruye y se verifica.

El corpus es el **TNO Image Fusion Dataset** de Alexander Toet, publicado en figshare
([10.6084/m9.figshare.1008029](https://doi.org/10.6084/m9.figshare.1008029)). Para armarlo:

1. Descargar y descomprimir el TNO.
2. Crear `data/raw/VIS/` y `data/raw/IR/`.
3. Copiar cada archivo según la columna `origen_tno` del manifiesto, renombrándolo al nombre de la
   columna `archivo`. **La imagen visible y la infrarroja de un par tienen que llamarse igual**: es
   así como el código las empareja.

### 5.3. Comprobar que quedó bien

```powershell
.venv\Scripts\python.exe -X utf8 experiments/verificar_corpus.py
```

Comprueba que estén los 42 archivos, que cada md5 coincida, que no haya archivos de más y que
`list_pairs()` devuelva los **20 pares efectivos**. Si dice `0 fallos`, el resto del repositorio se
puede correr.

Vale la pena correrlo aunque la instalación parezca bien. El manifiesto declara **21** pares y el
corpus efectivo son **20**: el par `Athena_heather_IR_hei_vis_g` viene con el canal visible idéntico
al infrarrojo, byte a byte. Con un par así toda métrica de fidelidad da su valor perfecto y el PSNR
se va al infinito, de modo que infla los promedios sin que nada más lo delate. Está declarado como
excluido en el manifiesto y el verificador comprueba que ningún par *no* excluido tenga ese
problema.

### 5.4. Los datasets de detección (opcionales)

Sólo hacen falta para la sección 8. Los dos son públicos y hay que descargarlos aparte:

| Dataset | Para qué | Dónde |
|---|---|---|
| **LLVIP** | detección de peatones nocturnos, un detector por entrada | [bupt-ai-cz.github.io/LLVIP](https://bupt-ai-cz.github.io/LLVIP/) |
| **M3FD** (Detection) | clases complementarias, un único detector VIS+IR | [JinyuanLiu-CV/TarDAL](https://github.com/JinyuanLiu-CV/TarDAL) |

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

El orden importa: cada paso consume las salidas del anterior.

```powershell
# 0. Comprobar el corpus antes de gastar tiempo en lo demás (md5, pares, canales)
python experiments/verificar_corpus.py

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
clases tienen visibilidad desigual —**People** favorece al IR (firma térmica) y **Lamp** al VIS—, de
modo que ninguna modalidad es la mejor en las dos clases a la vez y la imagen fusionada busca
sostener ambas. Se comparan las dos modalidades individuales y los siete métodos del benchmark,
incluida la propuesta en su configuración oficial (`Propuesta_Novedosa`: r=25, m=0.30).

```powershell
# Requiere M3FD (Detection) descargado: https://github.com/JinyuanLiu-CV/TarDAL
powershell -ExecutionPolicy Bypass -File .\ejecutar_m3fd.ps1 -M3FD "data\M3FD"
```

**Resultados** (`detection_m3fd_map.csv` y `complementariedad_resumen.csv`): la complementariedad es
real pero **asimétrica**. El IR domina People (`AP@0.5 = 0.779` frente a 0.621 del VIS) y se degrada
en Lamp (0.348); el VIS sostiene ambas clases en un nivel parejo (0.621 y 0.616). **No hay patrón
espejo y ninguna modalidad es ciega**: lo que justifica fusionar es que ninguna es la mejor en las
dos clases a la vez. La Ratio Pyramid es la única entrada cuyo promedio del par (0.622) supera a
ambas modalidades (VIS 0.618, IR 0.563); la propuesta alcanza 0.564 (People 0.641, Lamp 0.488), al
nivel del IR solo y por debajo del VIS, y en mAP@0.5 global queda 5.ª de las siete fusiones.

En el **conteo por escena** —232 escenas con ambas clases presentes, que es la operacionalización que
pide el objetivo— la propuesta recupera las dos en el **50.0 %** frente al **53.0 % del visible
solo**, con 8 escenas ganadas y 15 perdidas (McNemar exacto `p = 0.2100`), y resuelve 2 de las 90
escenas críticas. El mejor caso es la pirámide de Laplace (57.8 %); cuatro de las siete fusiones
quedan por debajo del visible. El realce elevado que optimiza las métricas de actividad **no** favorece
al detector: la hipótesis de que la mejora de calidad se traslade a la tarea queda **rechazada**, con
muestra suficiente.

---

## 9. Notebooks de análisis

| Notebook | Propósito |
|----------|-----------|
| `01_EDA_dataset.ipynb` | Exploración visual y estadística del dataset |
| `03_stats_analysis.ipynb` | Análisis cuantitativo, boxplots, Wilcoxon/Friedman |

---

## 10. Dependencias

`numpy`, `opencv-python`, `scikit-image`, `scipy`, `PyWavelets`, `dtcwt`, `pandas`, `matplotlib`, `seaborn`,
`jupyter`, `ipykernel`, `openpyxl`, `plotly`, `torch`, `torchvision` (ver `requirements.txt`).
La detección con YOLO/RF-DETR requiere `ultralytics` / `rfdetr` (preferentemente con GPU CUDA).

---

## 11. Referencias

Selección. La bibliografía completa son **36 entradas** en el capítulo 7 del libro, auditadas una por
una contra Crossref, OpenAlex, DataCite y Open Library: ninguna es inventada, se corrigieron siete
localizadores y se agregaron las tres que faltaban. El detalle, con los DOI verificados y lo que
quedó pendiente, está en [`docs/Auditoria_Bibliografia.md`](docs/Auditoria_Bibliografia.md).

- Serra, J. (1982). *Image Analysis and Mathematical Morphology*. Academic Press.
- Soille, P. (2003). *Morphological Image Analysis*. Springer.
- Burt, P. & Adelson, E. (1983). The Laplacian Pyramid as a Compact Image Code. *IEEE Trans. Commun.*
- Daubechies, I. (1992). *Ten Lectures on Wavelets.* SIAM. (base db4 del comparativo rotulado CVT)
- Candès, E. et al. (2006). Fast Discrete Curvelet Transforms. *SIAM Multiscale Model. Simul.* (transformada curvelet propiamente dicha, **no** implementada en este trabajo)
- Kennedy, J. & Eberhart, R. (1995). Particle Swarm Optimization. *Proc. ICNN*.
- Xydeas, C. & Petrović, V. (2000). Objective image fusion performance measure. *Electronics Letters*.
- Piella, G. & Heijmans, H. (2003). A new quality metric for image fusion. *Proc. ICIP*.
- Haghighat, M. et al. (2011). A non-reference image fusion metric based on mutual information of image features. *Computers & Electrical Engineering*.
- Ma, J. et al. (2019). Infrared and visible image fusion methods and applications: A survey. *Information Fusion*, 45.
- Singh, S. et al. (2023). A review of image fusion: methods, applications and performance metrics. *(revisión de referencia del estado del arte)*.
- Kingsbury, N. (2001). Complex wavelets for shift invariant analysis and filtering of signals. *Applied and Computational Harmonic Analysis*, 10(3), 234–253. (base del comparativo DTCWT)
- Toet, A. (2017). The TNO multiband image data collection. *Data in Brief*, 15, 249–251. (fuente del corpus; la entrada anterior la fechaba en 2014, que corresponde al depósito del dataset en Figshare)
- Bala, A. A., Aruna Priya, P. & Maik, V. (2024). Hybrid technique for fundus image enhancement using modified morphological filter and denoising net. *The Journal of Supercomputing*, 80(9), 13317–13340. (esquema aditivo-sustractivo que traslada este trabajo)
- Flores, S., Bujaico, C., Mello-Román, J. C., Vázquez Noguera, J. L. & Legal-Ayala, H. (s. f.). Método de realce de contraste local y nitidez en imágenes mamográficas basado en la transformada top-hat multiescala con elementos estructurantes circulares y lineales. [Manuscrito], Digital Image Processing Research Group, FPUNA. (**antecedente directo del banco circular + lineal**)
- Bajac Figueredo, Y. C., Bazán, J. P., Mello-Román, J. C., Vázquez Noguera, J. L. & Legal-Ayala, H. (2024). Infrared and visible image fusion using the Top Hat transform. *Proceeding Series of the Brazilian Society of Computational and Applied Mathematics* (CNMAC 2024). (**trabajo previo de los autores de esta tesis**)
- Ortega Rodríguez, M. A. & Espinoza Ríos, G. A. (2025). Optimización de los parámetros de la transformada Top-Hat mediante PSO para la fusión de imágenes visibles e infrarrojas. Proyecto de Trabajo Final de Grado, Facultad Politécnica, UNA. (**origen de la aptitud `Fo = SSIMavg + En + PSNRn` y del rango `m ∈ [0.30, 2.00]`**; verificado contra el original)

---

> *Este repositorio forma parte de la investigación de tesis de Maestría en Ciencias de Datos.*
> *El código está organizado para la reproducibilidad total de los experimentos.*
