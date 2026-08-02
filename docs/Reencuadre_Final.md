# Reencuadre final — texto para aplicar al libro

Encuadre adoptado: **auditoría del protocolo de evaluación**. El trabajo pasa a tener **dos
aportes**: el operador propuesto y su caracterización, y la auditoría de la validez
discriminativa del criterio con que se lo evalúa, usando el propio desarrollo como caso de
estudio.

Todas las cifras de este documento fueron recomputadas sobre el corpus vigente de 20 pares el
1 de agosto de 2026 y provienen de los CSV versionados en `experiments/results/metrics_reports/`.
Las siete hipótesis son contrastables con experimentos que **ya están corridos y versionados**.

---

## 1. Objetivo general

**Texto actual:**

> «Proponer y evaluar la Propuesta Novedosa, un método de fusión de imágenes visibles e
> infrarrojas basado en la transformada Top-Hat con elementos estructurantes circulares y
> lineales sobre una sola escala y parámetros optimizados por enjambre de partículas (PSO),
> comparándolo con la metodología clásica de fusión Top-Hat y con métodos representativos del
> estado del arte, y analizando su impacto en tareas posteriores de detección de objetos.»

**Texto propuesto:**

> Diseñar, implementar y caracterizar un operador de fusión de imágenes visibles e infrarrojas
> basado en la transformada Top-Hat de una sola escala con un banco de cinco elementos
> estructurantes —un disco y cuatro segmentos lineales orientados—, determinando en qué
> dirección desplaza el punto de operación de la fusión frente a la metodología clásica y a
> cinco configuraciones de referencia del estado del arte sobre el TNO Image Fusion Dataset; y
> auditar, con ese mismo desarrollo como caso de estudio, la validez discriminativa del
> protocolo de evaluación empleado —una batería de métricas sin referencia interpretadas como
> «mayor es mejor», la elección de hiperparámetros guiada por esas mismas métricas y el
> contraste con una tarea posterior de detección de objetos—, estableciendo en qué medida el
> orden de mérito que ese protocolo produce autoriza conclusiones sobre la calidad de una
> imagen fusionada y sobre su utilidad en una tarea posterior.

**Qué cambia y por qué.** Se retira «parámetros optimizados por enjambre de partículas» del
enunciado, porque ninguno de los dos hiperparámetros de la configuración evaluada es un
resultado de la optimización (ver H5). Se sustituye «evaluar» por «caracterizar», que es lo que
los datos permiten. Y se incorpora el segundo aporte, acotado explícitamente al protocolo
empleado en este trabajo y no a la literatura en general.

---

## 2. Objetivos específicos

Se pasa de cuatro a cinco.

### OE1 — Formulación del operador y ablación del banco

**Actual:** «…cuyas respuestas lineales se promedian y **se confrontan por máximo** con la del
disco…»

**Propuesto:**

> Formular e implementar el operador tal como efectivamente se evalúa: sobre una sola escala de
> radio *r* se calculan las transformadas Top-Hat y Bottom-Hat con un disco *B_r* y con cuatro
> elementos estructurantes lineales orientados a 0°, 45°, 90° y 135° de longitud 2r+1; las
> cuatro respuestas lineales se **promedian** y ese promedio se **suma** a la respuesta del
> disco; la comparación por máximo por píxel se aplica **únicamente entre las respuestas
> obtenidas del visible y del infrarrojo**, no entre las ramas del banco; y la reconstrucción es
> aditivo-sustractiva ponderada sobre *I_base* = (VIS + IR)/2. Aislar el aporte del banco
> mediante una ablación con hiperparámetros fijos.

> **Corrección de un error de hecho.** El objetivo actual describe una variante que no es la
> evaluada: el código suma el promedio de las líneas a la respuesta del disco
> (`src/fusion/optimal_top_hat.py`, modo `sum`); el máximo opera entre fuentes.

### OE2 — Alcance real de la optimización

**Actual:** «Optimizar automáticamente los hiperparámetros del método (el radio *r* … y el peso
de contraste *m*) mediante PSO…»

**Propuesto:**

> Delimitar el alcance real de la optimización por enjambre de partículas: establecer cuál de
> los hiperparámetros determina efectivamente la aptitud declarada y cuál constituye una
> decisión de diseño, caracterizar la forma de la función de aptitud sobre el espacio de
> búsqueda, y justificar el peso adoptado con criterios independientes de esa aptitud.

### OE3 — Caracterización del punto de operación

> Comparar el operador con la metodología clásica y con cinco configuraciones de referencia del
> estado del arte sobre nueve métricas sin referencia, con pruebas no paramétricas (Friedman y
> Wilcoxon con corrección de Holm), organizando los resultados en bloques de **actividad
> espacial** y **fidelidad a las fuentes** en lugar de un único orden agregado, y verificando la
> robustez del resultado frente a un ajuste simétrico de los hiperparámetros de los comparativos.

### OE4 — Auditoría de la validez discriminativa del criterio

> Evaluar si la batería de métricas empleada discrimina calidad de fusión, mediante tres
> pruebas: un control negativo con degradaciones conocidas, un análisis de redundancia interna
> entre métricas, y la sensibilidad del orden de mérito a la composición del conjunto.

### OE5 — Contraste externo en tarea posterior

> Medir el efecto de la fusión sobre la detección de objetos con dos experimentos
> independientes, y contrastar el orden de mérito de las métricas de imagen con el orden de
> utilidad en la tarea, operacionalizando el objetivo mediante un **conteo por escena** de
> recuperación de clases complementarias y no solo mediante el mAP promedio.

---

## 3. Problema general

**Propuesto:**

> ¿En qué dirección desplaza el punto de operación de la fusión VIS/IR un operador Top-Hat de
> una escala con banco de cinco elementos estructurantes, y en qué medida el protocolo de
> evaluación con el que se lo juzga —métricas sin referencia de tipo «mayor es mejor»,
> hiperparámetros elegidos sobre esas mismas métricas y validación en tarea posterior— permite
> sostener conclusiones sobre la calidad de la imagen fusionada y sobre su utilidad práctica?

---

## 4. Hipótesis

Siete hipótesis, todas contrastables con experimentos versionados.

### H1 — El operador desplaza el punto de operación *(afirmativa, sobre la propuesta)*

> El operador con banco de cinco elementos estructurantes no mejora la fusión de manera
> uniforme: desplaza su punto de operación hacia el realce de actividad espacial, en contra de
> la fidelidad estructural.

**Se sostiene.** Contra las cinco configuraciones de referencia, con Wilcoxon-Holm: en el bloque
de actividad (EN, SD, FE, MG, SF) **24 de 25 contrastes son favorables y ninguno adverso**; en el
de fidelidad (MI_vis, MI_ir, SSIM, PSNR) **17 de 20 son adversos** y uno solo favorable.

### H2 — El ordenamiento es propiedad del criterio, no del operador

> El orden de mérito de los métodos no es una propiedad del operador sino del criterio con que
> se lo evalúa.

**Se sostiene.** Con las nueve métricas del trabajo la propuesta es **1.ª de 7 (3,394)**; con las
diecisiete que el mismo evaluador calcula desciende a **3.ª (3,459)** y el primer lugar pasa a la
Pirámide de Laplace (3,147). No cambia nada del operador ni de las imágenes fusionadas.

### H3 — La batería de nueve métricas no distingue detalle útil de ruido

> El conjunto de nueve métricas de tipo «mayor es mejor» es insuficiente como criterio de
> calidad, porque sus métricas de actividad crecen monótonamente con la varianza inyectada.

**Se sostiene** (`run_control_negativo.py`). El rango de una fusión artificial de ruido gaussiano
mejora monótonamente con σ: **8,917 → 7,850 → 6,972 → 6,767** para σ = 0,02 / 0,05 / 0,10 / 0,20.
En la configuración de ocho entradas alcanza el **segundo puesto** con σ ≥ 0,10, por delante de
los seis métodos comparativos. Incorporando Nabf —única métrica implementada con dirección
inversa— el rango del ruido se degrada, y con las diecisiete cae al fondo de la tabla (10,138).

### H4 — Redundancia interna de la batería

> La batería contiene al menos una métrica que no aporta información independiente.

**Se sostiene.** FE = EN / media(EN de las fuentes), y el denominador no depende del método: los
rangos intra-bloque de EN y FE son **idénticos en las 20 imágenes** y su χ² de Friedman coincide
(**88,285714** en ambas). El número efectivo de dimensiones evaluadas es ocho, no nueve.

### H5 — La configuración evaluada no la determina la optimización

> La optimización no determina la configuración adoptada: ambos hiperparámetros son decisiones
> apoyadas en parte del mismo criterio con el que después se evalúa.

**Se sostiene.** El argmax de la aptitud dentro del rango publicado es **r = 1** (F_o = 1,7350),
no r = 25 (1,7057). Y el peso queda en **m = 0,30 en las 25 configuraciones** porque es el piso
del rango: F_o decrece estrictamente en *m*. El peso sí está justificado por criterios
independientes (equivalencia del realce y rango dinámico, ver §5), pero **no por la búsqueda**.

### H6 — El orden de calidad no predice la utilidad en detección

> El orden de mérito de las métricas de imagen no predice el orden de utilidad en una tarea
> posterior, y ninguna fusión supera por un margen distinguible a la mejor modalidad individual.

**Se sostiene.** Correlación de Spearman entre el rango de calidad y el mAP de LLVIP:
**ρ = +0,214, p = 0,645** — sin asociación, y con el signo contrario al esperado. En el conteo
por escena sobre **232 escenas** con ambas clases complementarias, la propuesta recupera ambas
en **50,0 %** frente al **53,0 % del visible solo**, con 8 escenas ganadas y 15 perdidas
(McNemar p = 0,2100). De las 90 escenas críticas resuelve 2. El único contraste significativo de
la familia, tras Holm, es la Pirámide de Laplace frente al infrarrojo.

### H7 — Aporte específico del banco, con hiperparámetros igualados

> Con (r, m) igualados, el banco de cinco elementos produce un perfil distinto del disco único.

**Se sostiene** (`run_ablacion_banco.py`). Con (r, m) = (25; 0,30) fijos, la suma de ramas es el
**mejor de los seis brazos con las nueve métricas** (3,222 frente a 3,367 del disco único), y
cae al cuarto con las diecisiete (3,621 frente a 3,153). La dirección del aporte es la misma que
enuncia H1, y su dependencia del criterio es la que enuncia H2. La imagen base sin operador
queda **última** de los seis brazos (4,359), de modo que el mérito no proviene de la base.

---

## 5. Conclusiones del capítulo 6

1. **El operador desplaza el punto de operación de la fusión y no la mejora de manera
   uniforme.** Gana en actividad espacial (24 de 25 contrastes favorables, ninguno adverso) y
   cede en fidelidad (17 de 20 adversos).
2. **Bajo el criterio del trabajo de referencia, el operador encabeza el benchmark.** Es 1.º de
   7 con 3,394, con separación estadísticamente significativa (permutación con 20.000 réplicas,
   p = 0,00005; Wilcoxon-Holm sobre el rango medio, 5 de 6 rivales a favor).
3. **Ese resultado es robusto frente al ajuste de los comparativos.** Dándoles el mismo paso de
   ajuste, ninguna de las cinco configuraciones de referencia lo alcanza. El Top-Hat clásico lo
   supera por 0,061, pero con m = 1 frente a m = 0,30: a igual peso la propuesta gana por 0,683.
4. **El banco de cinco elementos aporta sobre el disco único** con hiperparámetros igualados
   (3,222 frente a 3,367), y el mérito no proviene de la imagen base, que queda última.
5. **El peso adoptado está justificado por criterios independientes de la aptitud:** m = 0,30
   sobre este operador equivale a m = 1,26 sobre un disco único —dentro del rango publicado— y
   mantiene la saturación en 0,73 % frente al 6,50 % que produciría m = 1.
6. **El orden de mérito depende de la composición del conjunto de métricas.** Con nueve el
   operador es 1.º; con diecisiete, 3.º. El orden es propiedad del criterio.
7. **La batería de nueve métricas no discrimina detalle útil de ruido.** Una fusión artificial
   de ruido alcanza el segundo puesto de ocho, y su rango mejora al aumentar la varianza.
8. **La batería contiene redundancia:** FE es EN reescalada; las dimensiones efectivas son ocho.
9. **La optimización no determina la configuración evaluada.** El argmax de la aptitud es r = 1
   y el peso queda en el piso del rango.
10. **El orden de calidad no predice el orden de utilidad en detección** (ρ = +0,214, p = 0,645).
11. **Ninguna fusión supera a la mejor modalidad individual en la tarea.** En LLVIP el
    infrarrojo solo lidera; en el conteo por escena la propuesta queda por debajo del visible.
    **La hipótesis de que la mejora de calidad se traslade a la detección se rechaza**, con
    muestra suficiente (232 escenas).
12. **Aporte metodológico:** un protocolo de evaluación de fusión debe incluir al menos una
    métrica que penalice artefactos, declarar la redundancia entre sus componentes, y separar
    el ajuste de hiperparámetros del criterio de evaluación. El trabajo aporta los tres
    controles que lo verifican, versionados y reproducibles.

---

## 6. Limitaciones a declarar (apartado 1.6)

1. El corpus son 20 pares del TNO que corresponden a **13** escenas físicamente distintas
   (conteo exacto sobre los nombres de archivo: `APC_1` y `APC_3` aportan tres vistas cada una,
   `soldier_behind_smoke` tres instantes y `soldier_in_trench` dos; las nueve restantes son
   únicas). La estimación previa de «unas 11» quedó corregida el 2 de agosto de 2026; los
   contrastes pareados asumen independencia entre bloques. Verificado que las conclusiones
   sobreviven al agregar por escena.
2. Un par del subconjunto original estaba corrupto (el archivo visible era copia del infrarrojo)
   y se sustituyó por `Triclobs_Kaptein_1123`, declarado en `src/datasets.PARES_EXCLUIDOS`.
3. En seis pares del corpus el visible y el infrarrojo no son capturas simultáneas.
4. El radio se eligió sobre las métricas de evaluación: hay circularidad parcial, acotada por el
   experimento de ajuste simétrico.
5. La aptitud se optimiza sobre 3 de las 20 escenas, que también integran el conjunto de
   evaluación.
6. Las nueve métricas son todas de tipo «mayor es mejor»; ninguna penaliza artefactos.
7. El evaluador calcula ocho métricas adicionales que no se incorporan al análisis, por
   fidelidad metodológica con el trabajo de referencia.
8. El comparativo rotulado CVT es una wavelet db4 y no la transformada curvelet; los cinco
   métodos de referencia cubren cuatro familias.
9. La Pirámide de Laplace fusiona su banda base por máxima actividad en lugar de promediarla.
10. Los experimentos de detección usan una sola semilla.
11. LLVIP no tiene partición de prueba separada de la de selección; se reporta con el checkpoint
    final para no heredar el sesgo de selección.
12. Los resultados corresponden a escenas de vigilancia nocturna; la transferencia a otros
    dominios no está evaluada.

---

## 7. Qué no cambia

El capítulo 2 (marco teórico) salvo la subsección nueva sobre validez de las métricas; el
capítulo 3 salvo las correcciones de la descripción del operador y del PSO; y **todos los
resultados numéricos**, que no se recalculan: lo que cambia es qué se afirma sobre ellos.
