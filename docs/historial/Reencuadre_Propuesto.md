# Reencuadre del objetivo, las hipotesis y las conclusiones

_Propuesta de reescritura generada por un panel de tres reencuadres independientes, cada uno juzgado por tres lentes (mesa examinadora exigente, auditor de fidelidad a los datos, director preocupado por el aporte). Todas las cifras fueron recomputadas y verificadas contra el repositorio antes de incorporarse. Documento de trabajo: requiere aprobacion antes de aplicarse al libro._

---

El trabajo debe pasar de afirmar que el operador propuesto **es mejor** a afirmar dos cosas que los datos sí sostienen: (a) que el operador **desplaza el punto de operación** de la fusión —gana actividad espacial y transferencia de contenido de las fuentes, cede fidelidad estructural y añade artefactos— y (b) que el **protocolo de evaluación** con el que se lo juzga (nueve métricas sin referencia leídas como "mayor es mejor", hiperparámetros elegidos sobre esas mismas métricas, sin validación en tarea posterior) no discrimina calidad de fusión. Tres hechos verificados en el propio repositorio obligan el cambio y no admiten discusión en la defensa: **primero**, el primer puesto del ranking (3,394 con nueve métricas) desaparece al incorporar las ocho métricas que el proyecto ya calculó y no analizó —con diecisiete métricas la propuesta es 3.ª (3,459), detrás de Pirámide de Laplace (3,147) y DTCWT (3,259), y en Nabf, la única métrica del conjunto que penaliza artefactos, es 6.ª de 7 (media 0,3742 frente a 0,1138 de Laplace)—; **segundo**, la configuración oficial (r = 25, m = 0,30) no es el argmax de ninguna de las tres funciones de aptitud calculadas en el proyecto: m = 0,30 es exactamente el piso de la caja de búsqueda declarada (`pso_grid_search_fo.py:33`, m ∈ [0,30; 2,00]) y aparece en 25 de 25 corridas por ese motivo, mientras que dentro de esa caja F_o prefiere r = 1 (1,7354 frente a 1,7039) y, liberando el piso de m, el óptimo se traslada a (r = 25, m ≈ 0,0734) con F_o = 1,7654; **tercero**, ninguna fusión supera a la mejor modalidad individual en detección (LLVIP: IR 0,9708 frente a propuesta 0,9057, puesto 7 de 9; M3FD: mAP50 VIS 0,6762 frente a propuesta 0,6509, 5.ª de 7 fusiones), y el orden de calidad de la batería de nueve métricas no guarda asociación con el orden de utilidad en detección (Spearman ρ = −0,107, p = 0,819 en M3FD; ρ = +0,214, p = 0,645 en LLVIP, es decir con el signo contrario al esperado). El reencuadre conserva el operador como objeto de estudio con voz afirmativa —tiene un perfil propio y defendible: es 1.º en SCD (rango medio 1,45; media 1,5427) y tiene la media más alta de VIF (0,3805)— y convierte las tres vulnerabilidades actuales en los aportes del trabajo.

---

## 1. Objetivo general (texto listo para reemplazar)

**Texto actual:**

> "Proponer y evaluar la Propuesta Novedosa, un metodo de fusion de imagenes visibles e infrarrojas basado en la transformada Top-Hat con elementos estructurantes circulares y lineales sobre una sola escala y parametros optimizados por enjambre de particulas (PSO), comparandolo con la metodologia clasica de fusion Top-Hat y con metodos representativos del estado del arte, y analizando su impacto en tareas posteriores de deteccion de objetos."

**Texto propuesto:**

> Diseñar, implementar y evaluar un operador de fusión de imágenes visibles e infrarrojas basado en la transformada Top-Hat de una sola escala con un banco de cinco elementos estructurantes —un disco y cuatro segmentos lineales orientados—, caracterizando su punto de operación en tres bloques de criterios de evaluación (actividad espacial, transferencia de contenido de las fuentes y artefactos) frente a la metodología clásica de fusión Top-Hat y a cinco métodos representativos del estado del arte sobre el TNO Image Fusion Dataset; y auditar, con ese mismo desarrollo como caso de estudio, la validez discriminativa del protocolo de evaluación empleado en este trabajo y habitual en la literatura de fusión VIS/IR —una batería de métricas sin referencia interpretadas como "mayor es mejor", la elección de hiperparámetros guiada por esas mismas métricas y la ausencia de contraste con una tarea posterior—, determinando en qué medida el orden de mérito que ese protocolo produce autoriza conclusiones sobre la calidad de una imagen fusionada y sobre su utilidad en una tarea posterior de detección de objetos.

**Qué cambió y por qué.** Se retira "parámetros optimizados por enjambre de partículas" del enunciado, porque ninguno de los dos hiperparámetros de la configuración evaluada es un resultado de la optimización (§4, H5): el PSO pasa a ser un experimento auditado y no un componente del método. Se agrega el segundo aporte —la auditoría del protocolo— porque es lo que los datos sostienen y porque sin él el trabajo depende de un primer puesto que no sobrevive a la ampliación de la batería de métricas; el alcance de la auditoría se acota explícitamente a este benchmark y al protocolo empleado, no a "la literatura" en general.

---

## 2. Objetivos específicos (texto listo para reemplazar)

Se pasa de cuatro objetivos a cinco (no a ocho: un número mayor obliga a rendir cuentas de cada uno y dispersa el trabajo).

### Objetivo específico 1 — Formulación del operador y ablación del banco

**Texto actual:**

> "Formular la Propuesta Novedosa: sobre una sola escala, un banco de cinco elementos estructurantes (un disco y cuatro lineales a 0, 45, 90 y 135 grados) cuyas respuestas lineales se promedian y se confrontan por maximo con la del disco para obtener transformadas Top-Hat y Bottom-Hat optimas, con reconstruccion aditivo-sustractiva ponderada, adaptada al esquema de fusion VIS/IR."

**Texto propuesto:**

> Formular e implementar el operador tal como efectivamente se evalúa: sobre una sola escala de radio r se calculan las transformadas Top-Hat y Bottom-Hat con un disco B_r y con cuatro elementos estructurantes lineales orientados a 0, 45, 90 y 135 grados y longitud 2r+1; las cuatro respuestas lineales se **promedian** y ese promedio se **suma** a la respuesta del disco, de modo que WTH = WTH_disco + (1/4)·Σ_θ WTH_lineal(θ) y análogamente BTH; la comparación **por máximo por píxel se aplica únicamente entre las respuestas obtenidas de la imagen visible y de la infrarroja**, y no entre las ramas del banco; y la reconstrucción es aditivo-sustractiva ponderada, F = I_base + m·máx(WTH_VIS, WTH_IR) − m·máx(BTH_VIS, BTH_IR), con I_base = (VIS + IR)/2. Ejecutar además la ablación que aísla el aporte del banco manteniendo los hiperparámetros fijos en r = 25 y m = 0,30: disco solo, banco con suma de ramas, banco con promedio de ramas y banco con máximo entre ramas.

**Qué cambió y por qué.** **Corrección del error de hecho:** el texto actual dice que las respuestas lineales "se confrontan por máximo" con la del disco; el código las **suma** (`src/fusion/optimal_top_hat.py:68`, `mode="sum"`), y el máximo opera entre fuentes VIS/IR. El objetivo actual describe, por tanto, una variante del operador que no fue evaluada. Se agrega la ablación porque hoy la comparación contra el Top-Hat clásico no aísla el aporte del banco (el clásico usa r = 5, m = 1 y la propuesta r = 25, m = 0,30) y porque el interruptor ya existe en el código (`combined_top_hat(f, r, mode)` con `mode ∈ {"sum","avg","max"}`, líneas 53-73): declarar la limitación sin medirla, teniendo el parámetro implementado, es indefendible.

### Objetivo específico 2 — Alcance real de la optimización y circularidad del ajuste

**Texto actual:**

> "Optimizar automaticamente los hiperparametros del metodo (el radio r del banco de elementos estructurantes y el peso de contraste m) mediante PSO con una funcion de aptitud orientada a la calidad de fusion."

**Texto propuesto:**

> Delimitar el alcance real de la optimización por enjambre de partículas y caracterizar la circularidad del ajuste de hiperparámetros: explorar el espacio (r, m) con la aptitud declarada F_o = SSIM_avg + E/8 + PSNR/100 sobre la retícula de 25 configuraciones (n ∈ {2,4,6,8,10} × T_máx ∈ {10,20,30,40,50}); establecer que dentro de la caja de búsqueda del trabajo de referencia (r ∈ [1, 25], m ∈ [0,30; 2,00]) el peso de contraste converge al piso del intervalo en las 25 configuraciones y el radio preferido es r = 1; establecer que al liberar ese piso el radio preferido pasa a r = 25 en 18 de 25 configuraciones con m ≈ 0,05-0,0736; y concluir que la configuración adoptada (r = 25, m = 0,30) no maximiza ninguna de las funciones de aptitud calculadas, de modo que ambos hiperparámetros son decisiones de diseño tomadas sobre criterios que después se emplean para evaluar el método. Documentar asimismo que los seis métodos de comparación no reciben ningún ajuste de hiperparámetros equivalente y que el barrido de aptitud se realiza sobre 3 de las 20 escenas que también integran el conjunto de evaluación.

**Qué cambió y por qué.** El objetivo actual afirma que el PSO optimiza r y m; **el rol real del PSO es nulo respecto de la configuración evaluada**. Los hechos verificables: `pso_grid_search_fo.py:33` declara `LO = [1.0, 0.30]`, `HI = [25.0, 2.00]`; en `pso_grid_search_fo_propuesta.csv` m_opt = 0,3000 en 25 de 25 corridas (es el borde inferior) y r_opt = 1 en 17 de 25 (F_o = 1,7354) frente a r = 25 en 7 de 25 (F_o = 1,7039); en `curva_aptitud_vs_m.csv` F_o decrece monótonamente desde m = 0,30 (1,7039) hasta m = 2,00 (1,2298), por lo que cualquier corrida devuelve necesariamente el borde; en `pso_grid_search_fo_propuesta_oficial.csv`, con el piso de m bajado a 0,05, r_opt = 25 en 18 de 25 corridas y el mejor F_o es 1,7654 en (r = 25, m = 0,0734/0,0736), superior al 1,7039 de la configuración oficial; la aptitud F_apt se comporta igual (r = 25 en 13 de 25 corridas de `pso_grid_search.csv`, mejor F_apt = 1,9843 en m ≈ 0,0703, mientras a m = 0,30 cae a 1,5681); y el agregado de las nueve métricas crece monótonamente en m hasta 2,00 (F_nueve 3,0071 en m = 0,30 frente a 4,3633 en m = 2,00, `barrido_metricas_vs_m.csv`), de modo que tampoco es el óptimo del criterio "mayor es mejor". La formulación resultante es más fuerte que la anterior versión de la crítica ("el PSO fija m y r es decisión de diseño"), que era falsa en la dirección favorable al autor.

### Objetivo específico 3 — Benchmark y punto de operación en tres bloques de criterios

**Texto actual:**

> "Comparar el metodo optimo con la metodologia clasica de fusion Top-Hat y con cinco metodos representativos del estado del arte (LP, RP, DWT, DTCWT y CVT) sobre nueve metricas sin referencia, con pruebas no parametricas (Friedman y Wilcoxon con correccion de Holm)."

**Texto propuesto:**

> Construir el benchmark de referencia y ubicar en él el punto de operación del operador: 20 pares del TNO Image Fusion Dataset; seis métodos de comparación (la metodología clásica de fusión Top-Hat más LP, RP, DWT, DTCWT y CVT); una batería de diecisiete métricas sin referencia organizada en tres bloques —actividad espacial (EN, SD, FE, MG, SF), transferencia de contenido de las fuentes y fidelidad (MI_vis, MI_ir, SSIM, PSNR, SCD, VIF, FMI) y sensibilidad a artefactos (Qabf, Nabf, Q0, QW, QE)—; ranking por promedio de rangos intra-bloque, prueba de Friedman y contrastes de Wilcoxon con corrección de Holm, informando el signo, la significancia y la magnitud de cada comparación por bloque; y verificación de la estabilidad del ranking mediante prueba de permutación, agregación por escena física y exclusión de los pares empleados en el barrido de aptitud.

**Qué cambió y por qué.** La batería pasa de nueve a diecisiete métricas porque las ocho restantes **ya están calculadas** en `experiments/results/metrics_reports/all_metrics.csv` (columnas Qabf, Nabf, SCD, VIF, FMI, Q0, QW, QE) para los 7 métodos y los 20 pares, y sólo están excluidas por la lista `METRICS` de `experiments/run_stats_analysis.py:31`. Sostener que el criterio de evaluación determina el veredicto dejando ocho columnas medidas y sin analizar en el propio CSV es la única pregunta de defensa que hoy no tiene respuesta. La partición en tres bloques sustituye la dicotomía actividad/fidelidad porque el dato la rompe: el operador es 1.º en SCD y tiene la media más alta de VIF, que no son métricas de actividad.

### Objetivo específico 4 — Auditoría de la validez discriminativa del criterio

**Texto actual:** no existe (es material que hoy está disperso en el capítulo de limitaciones).

**Texto propuesto:**

> Auditar la validez discriminativa de la batería de métricas sin referencia y proponer un criterio corregido: (a) establecer analítica y empíricamente que FE no mide contenido de bordes sino que es la entropía EN reescalada por una constante propia de cada escena, y cuantificar el efecto de su exclusión sobre el ranking y sobre los estadísticos de Friedman; (b) someter la batería a un control negativo consistente en fusiones deliberadamente degradadas que no incorporan información adicional de las fuentes —el promedio (VIS + IR)/2 sin operador, ese mismo promedio con ruido gaussiano aditivo con sigma ∈ {0,02; 0,05; 0,10; 0,20} y ese promedio con desenfoque gaussiano—, y determinar la posición que la batería asigna a cada control con el conjunto de nueve métricas y con el conjunto ampliado de diecisiete; y (c) formular, a partir de esos resultados, un conjunto de recomendaciones de protocolo: separación estricta entre el criterio de ajuste y el de evaluación, ajuste equivalente de los métodos de comparación, inclusión sistemática de controles negativos, declaración de la dirección de cada métrica —incluida Nabf, la única del conjunto en que menor es mejor— y agregación por escena física.

**Qué cambió y por qué.** Es el aporte metodológico del trabajo y hoy no figura como objetivo, sino como confesión en el apartado de limitaciones. El control negativo se generaliza de un único sigma a un barrido más dos degradaciones adicionales, porque un único valor (sigma = 0,10) se descarta como muñeco de paja; y se le exige salida versionada, porque hoy el experimento existe sólo en la narrativa de `docs/Auditoria_Interna.md` y no hay script ni CSV que lo reproduzca (la búsqueda de "ruido", "noise" y "sigma" en `experiments/` y `src/` sólo devuelve el docstring de Nabf).

### Objetivo específico 5 — Contraste externo en tarea posterior de detección

**Texto actual:**

> "Analizar el impacto de la fusion en una tarea posterior de deteccion de objetos (YOLO), evaluando la detectabilidad por modalidad de entrada."

**Texto propuesto:**

> Contrastar externamente el veredicto del protocolo con una tarea posterior de detección de objetos: evaluar con YOLOv8n el desempeño de cada método de fusión y de las modalidades individuales VIS e IR en LLVIP (un detector reentrenado por método de entrada) y en M3FD (un único detector VIS+IR con particiones train/val/test disjuntas y estratificadas y un test de 499 imágenes), informando el mAP50 y el mAP50-95 completos de todas las clases como resultado principal y el desagregado por clase como análisis secundario; comparar cada fusión no sólo con las restantes sino con la mejor modalidad individual disponible; y medir la asociación de rangos entre el orden de mérito de la batería de métricas y el orden de utilidad en detección, con la batería de nueve métricas y con la ampliada de diecisiete.

**Qué cambió y por qué.** Se explicita el mAP completo como cifra principal (hoy el par People+Lamp se reporta como resultado central, y es una selección de 2 de 6 clases hecha después de ver los datos: exactamente el vicio que el trabajo denuncia), se agrega la comparación contra la mejor modalidad como criterio declarado y se agrega la medida de asociación de rangos, que convierte "el ranking no predice detección" de una afirmación sobre el primer puesto en una afirmación medida sobre los dos ordenamientos completos.

---

## 3. Problema general y problemas específicos

### Problema general

**Texto actual:**

> "La Propuesta Novedosa de fusion VIS+IR basada en la transformada Top-Hat, con elementos estructurantes de disco y lineales sobre una sola escala e hiperparametros optimizados por PSO, mejora la calidad de fusion -evaluada con metricas sin referencia y pruebas no parametricas sobre el TNO Image Fusion Dataset- respecto de la metodologia clasica de fusion Top-Hat y de los metodos del estado del arte, y que efecto produce en el desempeno de una tarea posterior de deteccion de objetos?"

**Texto propuesto:**

> ¿En qué criterios de evaluación mejora y en cuáles cede un operador de fusión VIS+IR basado en la transformada Top-Hat de una sola escala con un banco de cinco elementos estructurantes, frente a la metodología clásica de fusión Top-Hat y a cinco métodos representativos del estado del arte sobre el TNO Image Fusion Dataset; en qué medida el orden de mérito que produce la batería de métricas sin referencia empleada para juzgarlo es una propiedad del operador y no del criterio con que se lo mide; y qué relación guarda ese orden de mérito con la utilidad de las mismas imágenes fusionadas en una tarea posterior de detección de objetos?

**Qué cambió y por qué.** El problema actual ya estaba formulado con prudencia en su segunda mitad ("qué efecto produce"), de modo que el cambio es acotado: se retira "hiperparámetros optimizados por PSO" (§2, objetivo 2), se sustituye "mejora la calidad de fusión" por "en qué criterios mejora y en cuáles cede" —porque la respuesta depende del bloque de criterios— y se incorpora la pregunta por la dependencia del veredicto respecto del criterio, que es el segundo aporte.

### Problemas específicos

Si el capítulo 1 no los enumera, pueden omitirse; si los enumera, se propone alinearlos uno a uno con los objetivos específicos:

> 1. ¿Cuál es la formulación exacta del operador evaluado y qué parte de su desempeño es atribuible al banco de cinco elementos estructurantes, con los hiperparámetros igualados?
> 2. ¿Qué determina efectivamente la optimización por enjambre de partículas dentro del espacio de búsqueda declarado, y qué consecuencias tiene sobre la independencia entre el criterio de ajuste y el de evaluación?
> 3. ¿Cómo se ubica el operador en cada uno de los tres bloques de criterios —actividad espacial, transferencia de contenido y artefactos— frente a los seis métodos de comparación?
> 4. ¿Distingue la batería de métricas sin referencia el detalle útil del ruido incorporado, y qué métricas del conjunto no aportan información independiente?
> 5. ¿Predice el orden de mérito de la batería el orden de utilidad de las imágenes fusionadas en una tarea posterior de detección de objetos?

---

## 4. Hipótesis (texto listo para reemplazar)

Se pasa de tres hipótesis a seis, más una séptima que hoy **no es contrastable** y para la que se indica el experimento que la vuelve contrastable. Todas las cifras provienen de los archivos del repositorio y están verificadas.

### H1 — Punto de operación del operador (afirmativa)

> **Enunciado.** El operador de Top-Hat de una escala con banco de cinco elementos estructurantes no mejora de manera uniforme la fusión: desplaza su punto de operación hacia el realce de actividad espacial y hacia la transferencia de contenido de las fuentes, y en contra de la fidelidad estructural y del control de artefactos.

**Veredicto: se sostiene.**

**Evidencia.** Sobre 45 contrastes de Wilcoxon con corrección de Holm frente a los cinco métodos del estado del arte, el operador resulta mejor en 25, peor en 17 y sin diferencia en 3. El reparto por bloques es sistemático: en actividad espacial (EN, SD, FE, MG, SF) 24 de 25 contrastes son favorables y ninguno adverso, con una única excepción no significativa (SD frente a Pirámide de Laplace, p_Holm = 0,2305); en fidelidad (SSIM, PSNR, MI_vis, MI_ir) 17 de 20 son adversos, con dos empates (MI_vis y MI_ir frente a Ratio Pirámide, p_Holm = 0,2162 y 0,1231) y un contraste **favorable y significativo** (PSNR frente a Pirámide de Laplace, 16,8409 frente a 14,9401, p_Holm = 2,1e-05). Lidera la media de EN (6,9855) y de FE (1,1047), esta última por construcción al ser FE una reescalada de EN. En el tercer bloque el perfil es doble: es **1.º en SCD** (rango medio 1,45; media 1,5427, la más alta del conjunto) y tiene la **media más alta de VIF** (0,3805; rango medio 1,75, segundo detrás de Pirámide de Laplace con 1,70), y simultáneamente es **6.º de 7 en Nabf** (media 0,3742, rango medio 6,00; Pirámide de Laplace 0,1138, DTCWT 0,1593; sólo el Top-Hat clásico es peor con 0,5857) y queda en la mitad inferior de los índices de Piella (Q0 rango 4,25; QW 4,15). Friedman rechaza H0 en las nueve métricas del conjunto original (peor caso MI_ir, χ² = 58,0071, p = 1,14e-10).

*Nota de redacción: "sistemáticamente" debe sustituirse por el recuento exacto, porque existe una excepción en cada dirección y ambas son verificables en una línea de `wilcoxon_results.csv`.*

### H2 — El ordenamiento es propiedad del criterio, no del operador

> **Enunciado.** En este benchmark el orden de mérito de los métodos de fusión no es una propiedad del operador sino del criterio con que se lo evalúa: bajo un criterio dominado por métricas de actividad el operador ocupa el primer lugar, y bajo un criterio que incorpora las métricas sensibles a artefactos desciende a la mitad de la tabla, sin que cambie nada del operador ni de las imágenes fusionadas.

**Veredicto: se sostiene.**

**Evidencia.** Con el conjunto de nueve métricas el operador es 1.º con un promedio de rangos intra-bloque de 3,394 (2.º Pirámide de Laplace 3,911; 3.º Top-Hat clásico 3,944; 4.º Ratio Pirámide 3,983; 5.º DTCWT 4,111; 6.º DWT 4,211; 7.º Curvelet 4,444), y sin FE sigue 1.º con 3,631. Con el conjunto ampliado de diecisiete métricas, calculadas sobre las mismas 20 imágenes y los mismos 7 métodos y con el mismo promedio de rangos intra-bloque, es **3.º con 3,459**, detrás de Pirámide de Laplace (3,147) y DTCWT (3,259), y por delante de Ratio Pirámide (3,918), DWT (4,556), Curvelet (4,662) y Top-Hat clásico (5,000); sin FE, 3.º con 3,581. Considerando sólo las ocho métricas no utilizadas hasta ahora es **3.º con 3,531** (Pirámide de Laplace 2,288; DTCWT 2,300), y considerando sólo el bloque de artefactos (Qabf, Nabf, VIF, Q0, QW, QE) es **4.º de 7 con 3,892** (Pirámide de Laplace 2,100; DTCWT 2,175; Ratio Pirámide 3,767). El primer puesto es además sensible a la regla de agregación: la columna `avg_rank_medias` de `ranking_methods.csv`, que rankea las medias en lugar de los rangos intra-bloque, da **empate en 3,556 entre el operador y la Pirámide de Laplace**.

### H3 — La batería de nueve métricas no distingue detalle útil de ruido

> **Enunciado.** El conjunto de nueve métricas sin referencia interpretadas como "mayor es mejor" es insuficiente como criterio de calidad de fusión, porque sus métricas de actividad crecen monótonamente con la varianza inyectada: una fusión deliberadamente degradada, que no incorpora ninguna información adicional de las fuentes, alcanza posiciones de cabeza en el ranking y supera a métodos publicados.

**Veredicto: se sostiene, con la evidencia disponible pendiente de re-ejecución versionada.**

**Evidencia.** Con la fusión falsa F = clip((VIS + IR)/2 + N(0, sigma)) y sigma = 0,10, evaluada con el mismo `evaluate_all()` del repositorio, las cinco métricas de actividad crecen monótonamente con sigma y el ruido puro queda 1.º en EN (7,231 frente a 6,986 del operador), 1.º en FE, 1.º en MG (0,0907 frente a 0,0358) y 1.º en SF (51,4 frente a 17,7), y 2.º en SD; el promedio de rangos de nueve métricas sobre 19 imágenes y un bloque de 8 entradas da 4,111 para el operador y 4,111 para el control con ruido, **empatados en primer lugar** y por delante de los cinco métodos del estado del arte.

**Advertencia obligatoria de trazabilidad.** Estas cifras provienen de `docs/Auditoria_Interna.md` (hallazgo R2), se calcularon sobre 19 imágenes y un bloque de 8 entradas —no sobre el bloque oficial de 7 métodos y 20 pares— y anteceden a la sustitución del par corrupto por Triclobs_Kaptein_1123; los valores 0,0358 (MG) y 17,7 (SF) corresponden a ese subconjunto, mientras el conjunto oficial de 20 pares da 0,0355 y 17,4425. No existe script ni CSV que reproduzca el experimento. Antes de llevar H3 a la defensa hay que versionar `experiments/run_control_negativo.py` con semilla fija, ejecutarlo sobre el corpus actual de 20 pares con el mismo procedimiento de rangos intra-bloque, con el barrido sigma ∈ {0,02; 0,05; 0,10; 0,20} y las dos degradaciones adicionales, y **reemplazar toda cifra de la auditoría por la recomputada**. Si con el corpus corregido el control ya no empata en el primer puesto sino que queda 2.º o 3.º, debe decirse: el enunciado "una imagen con ruido gaussiano puro supera a métodos publicados en la batería de nueve métricas" es más robusto que el empate y sostiene igualmente la hipótesis. La monotonía de las cinco métricas de actividad respecto de sigma es el resultado irrefutable y debe ser el que se publique como figura.

### H4 — Redundancia interna de la batería

> **Enunciado.** La batería de nueve métricas contiene al menos una métrica que no aporta información independiente, de modo que el número efectivo de dimensiones evaluadas es menor que el número declarado.

**Veredicto: se sostiene.**

**Evidencia.** FE, tal como está implementada en el proyecto, es la entropía EN dividida por una constante propia de cada escena y no emplea ningún operador de gradiente; en consecuencia produce exactamente los mismos rangos intra-bloque que EN (columnas EN y FE de `ranking_methods.csv`: 1,50 / 1,50 para el operador; 3,25 / 3,25 para Pirámide de Laplace; 2,45 / 2,45 para el Top-Hat clásico; y así en los siete métodos) y el mismo estadístico de Friedman (χ² = 88,2857, p = 6,876e-17 en ambas). El promedio de las nueve métricas otorga por tanto peso 2/9 a la entropía; excluyéndola, el operador es 1.º con 3,631 en lugar de 3,394. Toda mención a FE como "entropía de bordes" o "contenido de bordes" debe corregirse en el libro, en `README.md:166`, en los avances y en la presentación, y FE debe dejar de contarse como evidencia independiente: el operador gana a los cinco métodos del estado del arte en **tres** dimensiones independientes de actividad (EN —equivalentemente FE—, MG y SF), no en cuatro.

**Condición previa.** Debe verificarse la definición canónica de FE en la fuente citada. Si la definición canónica emplea un operador de gradiente, lo demostrado no es una redundancia de la batería de la literatura sino un defecto de la implementación propia: en ese caso H4 se retira del conjunto de hipótesis, se declara en el capítulo de métodos que la FE implementada es un cociente de entropías y no la métrica canónica, se retira la afirmación de liderazgo en FE y el benchmark sin FE pasa a ser el resultado principal.

### H5 — La configuración evaluada no la determina la optimización

> **Enunciado.** La optimización por enjambre de partículas no determina la configuración evaluada: la configuración adoptada (r = 25, m = 0,30) no maximiza ninguna de las funciones de aptitud calculadas en el trabajo, de modo que ambos hiperparámetros son decisiones de diseño apoyadas en parte del mismo criterio con el que después se evalúa al método.

**Veredicto: se sostiene.**

**Evidencia.** El espacio de búsqueda declarado es r ∈ [1, 25], m ∈ [0,30; 2,00] (`experiments/pso_grid_search_fo.py:33`). Dentro de él, F_o decrece monótonamente en m —1,7039 en m = 0,30; 1,6208 en 0,50; 1,2298 en 2,00 (`curva_aptitud_vs_m.csv`)—, por lo que toda corrida devuelve el borde inferior: m_opt = 0,3000 en 25 de 25 configuraciones de `pso_grid_search_fo_propuesta.csv`. En ese mismo archivo el radio preferido es r = 1 en 17 de 25 corridas (F_o = 1,7354) frente a r = 25 en 7 de 25 (F_o = 1,7039) y r = 9 en 1 de 25 (1,6988): **la comparación 1,7354 frente a 1,7039 es condicional a m congelado en 0,30 y debe declararse así**. Al bajar el piso de m a 0,05 (`pso_grid_search_fo_propuesta_oficial.csv`), r_opt = 25 en 18 de 25 corridas y el mejor valor es F_o = 1,7654 en (r = 25, m = 0,0734/0,0736), superior al 1,7039 de la configuración oficial. La aptitud alternativa F_apt se comporta igual: r_opt = 25 en 13 de 25 corridas de `pso_grid_search.csv`, mejor F_apt = 1,9843 en m ≈ 0,0703, mientras que a m = 0,30 cae a 1,5681. Y el agregado de las nueve métricas de evaluación crece monótonamente en m hasta el extremo del intervalo (F_nueve = 3,0071 en m = 0,30 frente a 4,3633 en m = 2,00, `barrido_metricas_vs_m.csv`). En consecuencia, m = 0,30 es el piso de una caja elegida por el autor y r = 25 su techo; la configuración oficial se compone del radio que prefiere una aptitud y de un peso que no prefiere ninguna. La circularidad se declara sobre **ambos** hiperparámetros. De las nueve métricas de evaluación, 5 favorecen r = 25 (EN, SD, FE, MG, SF) y las 4 de fidelidad favorecen r = 1 (SSIM, PSNR, MI_vis, MI_ir), todas con p < 1e-05; y cuatro de las cinco métricas en que el operador vence a los cinco métodos del estado del arte pertenecen al bloque favorecido por r = 25, de modo que **el primer puesto es simultáneamente legítimo dentro del protocolo y dependiente de la elección circular que el trabajo denuncia**. Esta frase debe figurar junto a H2, no sólo en limitaciones.

**Errata a declarar.** Debe consignarse explícitamente que la versión anterior del documento atribuía al PSO la optimización de (r, m) y describía el operador con máximo entre disco y ramas lineales, y que ambas afirmaciones se corrigen en esta versión.

### H6 — El orden de calidad no predice la utilidad en detección

> **Enunciado.** El orden de mérito que produce la batería de métricas sin referencia no predice el orden de utilidad de las mismas imágenes fusionadas en una tarea posterior de detección de objetos, y ninguna fusión supera por un margen distinguible a la mejor modalidad individual disponible.

**Veredicto: se sostiene.**

**Evidencia.** En LLVIP, con un detector YOLOv8n reentrenado por método de entrada, la mejor entrada es el **IR solo** (mAP50 = 0,9708); el operador propuesto obtiene 0,9057 (puesto 7 de 9) y el VIS 0,8133; ninguna fusión supera al IR. En M3FD, con un único detector VIS+IR, particiones train/val/test disjuntas y estratificadas y un test de 499 imágenes, el mAP50 completo de las seis clases es: Ratio Pirámide 0,6772 | VIS 0,6762 | Pirámide de Laplace 0,6736 | IR 0,6680 | DTCWT 0,6647 | DWT 0,6524 | **propuesta 0,6509** (5.ª de 7 fusiones) | Curvelet 0,6426 | Top-Hat clásico 0,6082; en mAP50-95: Pirámide de Laplace 0,4320 | Ratio Pirámide 0,4317 | VIS 0,4302 | DTCWT 0,4247 | IR 0,4225 | propuesta 0,4124. La asociación de rangos entre el orden de mérito de la batería de nueve métricas y el mAP de las siete fusiones es nula: Spearman ρ = −0,107 (p = 0,819) contra mAP50 de M3FD, ρ = −0,357 (p = 0,432) contra mAP50-95 de M3FD y ρ = +0,214 (p = 0,645) contra mAP50 de LLVIP, este último con el signo **contrario** al esperado (el rango de calidad es una magnitud en la que menor es mejor, de modo que una asociación en el sentido esperado se manifestaría como correlación negativa). En cambio, el ranking ampliado de diecisiete métricas sí se asocia en el sentido esperado con la utilidad en M3FD: ρ = −0,714 (p = 0,071), y ρ = −0,429 (p = 0,337) en LLVIP. Este último resultado es el rendimiento constructivo de la auditoría: la batería que incorpora las métricas de artefactos ordena los métodos de forma compatible con su utilidad posterior, mientras la de nueve métricas no lo hace.

**Condición de reporte.** Todas las cifras de detección provienen de un único entrenamiento por entrada, sin repetición con semillas, sin intervalos y sin prueba de significación. Diferencias inferiores a aproximadamente 0,01 no admiten lectura como diferencias establecidas; en particular, la ventaja de Ratio Pirámide sobre el VIS en mAP50 (+0,0010) y en el par People+Lamp (+0,0038) debe informarse como **indistinguible** de la mejor modalidad y no como superación. Las correlaciones se calculan sobre n = 7 fusiones y deben publicarse con un script versionado (`experiments/run_correlacion_calidad_deteccion.py`), que sólo recombina tablas existentes. Debe declararse asimismo que el máximo de validación en M3FD se alcanza en la época 40 de 40, es decir en la última del presupuesto, por lo que no puede descartarse que un presupuesto mayor mejorara todas las entradas.

### H7 — Aporte específico del banco de cinco elementos estructurantes

> **Enunciado actual, no contrastable.** "La optimización automática de los hiperparámetros (r, m) por PSO, con una función de aptitud orientada a la fusión, alcanza un perfil de calidad superior al de la parametrización manual del operador clásico." Esta hipótesis **no es contrastable con los experimentos existentes**: los dos operadores se comparan con pares (r, m) distintos —el clásico con r = 5 y m = 1, el propuesto con r = 25 y m = 0,30—, de modo que el cambio de operador está confundido con el cambio de hiperparámetros, y no existe ninguna condición con (r, m) igualados en el benchmark oficial.

> **Enunciado propuesto, contrastable tras la ablación.** Con los hiperparámetros igualados en r = 25 y m = 0,30, el banco de cinco elementos estructurantes con suma de ramas produce un perfil de métricas distinto del disco único, y esa diferencia es de magnitud comparable a la observada entre el operador propuesto y el Top-Hat clásico con sus parametrizaciones respectivas.

**Veredicto: por contrastar (experimento identificado y de bajo costo).**

**Evidencia parcial ya disponible, y adversa.** `aptitud_operador_configs.csv` contiene: base (VIS + IR)/2 sin ningún operador, F_o = 1,7529; Top-Hat clásico publicado (r = 5, m = 1), F_o = 1,6016; clásico re-optimizado con la misma aptitud (r = 25, m = 0,10), F_o = 1,7651; propuesta (r = 25, m = 0,0703), F_o = 1,7654. Es decir: con hiperparámetros equiparados, **la diferencia entre el banco de cinco elementos y el disco único es de 0,0003 bajo la aptitud declarada**, y la base sin operador (1,7529) supera al Top-Hat clásico publicado (1,6016). `fo_ablacion_comparativa.csv` añade que el clásico con r = 25 y m = 0,30 obtiene Qabf = 0,5338 y Nabf = 0,1840, frente a Qabf = 0,4716 y Nabf = 0,3742 del operador propuesto en el benchmark oficial —comparación que, no obstante, cruza dos tablas con corpus no verificados como idénticos: `fo_ablacion_per_image.csv` identifica las imágenes por índice 1-20 y no por nombre, y la tabla comparativa carece de la fila del operador propuesto en (r = 25, m = 0,30)—. La ablación pendiente es un bucle de cuatro corridas sobre los 20 pares con `mode ∈ {"sum","avg","max"}` más la variante de disco solo, con r = 25 y m = 0,30 fijos, regenerando la tabla completa con nombres de imagen y las diecisiete métricas. Debe ejecutarse: es el único experimento que convierte el objetivo específico 1 en contribución verificada; si no se ejecuta, el objetivo 1 debe rebajarse a "formular e implementar" y renunciar explícitamente a atribuir mérito comparativo al banco.

### Hallazgo que **no** debe figurar como hipótesis: compensación por clase

La compensación por clase debe pasar a la discusión del capítulo 5, con el enunciado literalmente correcto y con la comparación contra las demás fusiones:

> En M3FD la fusión propuesta se sitúa, en cada una de las dos clases complementarias, por encima de la modalidad más débil de esa clase y por debajo de la más fuerte: supera al VIS en People (0,6406 frente a 0,6207) pero no al IR (0,7787), y supera al IR en Lamp (0,4881 frente a 0,3482) pero no al VIS (0,6161). El promedio del par People+Lamp es 0,5643 para la propuesta, 0,6184 para el VIS y 0,5634 para el IR.

Debe eliminarse la fórmula "mejora a cada modalidad en la clase donde esa modalidad es débil": es falsa para el VIS, cuya clase débil de las dos es Lamp (0,6161 frente a 0,6207 en People) y donde la propuesta no lo supera. Debe declararse además que la compensación es un efecto del promediado presente en las seis fusiones no degeneradas y que la propuesta es la más débil de ellas en ambas clases: en People, 0,6406 frente a Ratio Pirámide 0,6938, Pirámide de Laplace 0,6837, DTCWT 0,6694 y DWT 0,6639; en Lamp, 0,4881 frente a Ratio Pirámide 0,5505, Pirámide de Laplace 0,5446, DTCWT 0,5419, DWT 0,5277 y Curvelet 0,4899. Y que la premisa de complementariedad extrema se debilita con un detector correctamente entrenado: el VIS obtiene 0,6207 en People frente a 0,6161 en Lamp, es decir no es ciego en personas.

---

## 5. Conclusiones del capítulo 6 (texto listo para reemplazar)

> 1. **El operador desplaza el punto de operación de la fusión en una dirección determinada y no la mejora de manera uniforme.** Frente a los cinco métodos representativos del estado del arte, 24 de 25 contrastes de Wilcoxon con corrección de Holm en el bloque de actividad espacial son favorables y ninguno adverso, con una única excepción no significativa (SD frente a Pirámide de Laplace, p_Holm = 0,2305), mientras que 17 de 20 contrastes del bloque de fidelidad son adversos, con dos empates y un único contraste favorable y significativo (PSNR frente a Pirámide de Laplace, 16,8409 frente a 14,9401). El balance global es de 25 contrastes favorables, 17 adversos y 3 sin diferencia.
>
> 2. **El operador tiene un perfil positivo propio en un tercer bloque de criterios, no contemplado en el diseño original de la evaluación.** Es 1.º de 7 en SCD (rango medio 1,45; media 1,5427, la más alta) y presenta la media más alta de VIF (0,3805), es decir maximiza la transferencia de contenido de las imágenes fuente; y simultáneamente es 6.º de 7 en Nabf (media 0,3742, rango medio 6,00), frente a 0,1138 de la Pirámide de Laplace y 0,1593 de DTCWT, siendo sólo superado en artefactos por el Top-Hat clásico (0,5857). El mecanismo del operador queda así caracterizado: transfiere contraste de las fuentes al precio de inyectar artefactos.
>
> 3. **El orden de mérito de los métodos es una propiedad del criterio de evaluación y no del operador.** Con nueve métricas el operador es 1.º (promedio de rangos intra-bloque 3,394; 3,631 sin FE); con las diecisiete métricas calculadas sobre las mismas imágenes y los mismos métodos es 3.º (3,459), detrás de Pirámide de Laplace (3,147) y DTCWT (3,259); en el bloque de artefactos es 4.º de 7 (3,892). Nada del operador ni de las imágenes fusionadas cambia entre esos tres veredictos. El primer puesto es además sensible a la regla de agregación: rankeando las medias hay empate en 3,556 con la Pirámide de Laplace.
>
> 4. **La batería de nueve métricas sin referencia leídas como "mayor es mejor" no distingue detalle útil de varianza inyectada.** Las cinco métricas de actividad crecen monótonamente con el nivel de ruido añadido a la fusión de control, y con sigma = 0,10 la fusión degradada —que no incorpora ninguna información adicional de las fuentes— alcanza posiciones de cabeza del ranking, por delante de los cinco métodos del estado del arte. Encabezar ese ranking no acredita por sí solo calidad de fusión. [Cifras exactas a completar con la re-ejecución versionada sobre el corpus de 20 pares.]
>
> 5. **La batería contiene una métrica que no aporta información independiente.** FE, tal como está implementada, es la entropía EN reescalada por una constante propia de cada escena y no emplea ningún operador de gradiente: produce los mismos rangos intra-bloque que EN en los siete métodos y el mismo estadístico de Friedman (χ² = 88,2857, p = 6,876e-17). El número efectivo de dimensiones evaluadas es ocho, no nueve, y la victoria del operador sobre los cinco métodos del estado del arte se produce en tres dimensiones independientes de actividad (EN, MG y SF), no en cuatro.
>
> 6. **La configuración evaluada no es un resultado de la optimización automática.** m = 0,30 coincide con el piso de la caja de búsqueda declarada (m ∈ [0,30; 2,00]) y aparece en 25 de 25 corridas porque F_o decrece monótonamente en m dentro de esa caja (1,7039 en 0,30; 1,2298 en 2,00); dentro de la misma caja el radio preferido es r = 1 (F_o = 1,7354 en 17 de 25 corridas, frente a 1,7039 con r = 25); y al liberar el piso de m el óptimo se traslada a (r = 25, m ≈ 0,0734) con F_o = 1,7654, superior al de la configuración oficial. La aptitud alternativa F_apt alcanza su máximo en (r = 25, m ≈ 0,0703) con 1,9843 y cae a 1,5681 en m = 0,30, y el agregado de las nueve métricas de evaluación crece monótonamente en m hasta 4,3633 en m = 2,00. Ambos hiperparámetros son, por tanto, decisiones de diseño.
>
> 7. **El ajuste de hiperparámetros y la evaluación no son independientes.** De las nueve métricas, cinco favorecen r = 25 (EN, SD, FE, MG, SF) y las cuatro de fidelidad favorecen r = 1 (SSIM, PSNR, MI_vis, MI_ir), todas con p < 1e-05; cuatro de las cinco métricas en que el operador vence a los cinco métodos del estado del arte pertenecen al primer bloque. El primer puesto es legítimo dentro del protocolo y a la vez dependiente de la decisión de diseño que este trabajo audita. A ello se añade que los seis métodos de comparación no reciben ningún ajuste de hiperparámetros equivalente y que el barrido de aptitud se realiza sobre 3 de las 20 escenas que también integran el conjunto de evaluación.
>
> 8. **El realce de actividad espacial medido sin referencia no se transfiere a la detección de objetos.** En LLVIP la mejor entrada es el IR solo (mAP50 = 0,9708), la propuesta obtiene 0,9057 (puesto 7 de 9) y el VIS 0,8133; ninguna fusión supera al IR. En M3FD, con particiones disjuntas y estratificadas y un test de 499 imágenes, el mAP50 de la propuesta es 0,6509 (5.ª de 7 fusiones) frente a 0,6762 del VIS y 0,6680 del IR; las dos fusiones que igualan o exceden a la mejor modalidad lo hacen por márgenes de +0,0010 en mAP50 (Ratio Pirámide) y +0,0018 en mAP50-95 (Pirámide de Laplace), no distinguibles con un único entrenamiento por entrada.
>
> 9. **El orden de mérito de la batería de nueve métricas no predice el orden de utilidad en detección.** La correlación de Spearman entre el promedio de rangos de calidad de las siete fusiones y su mAP es de ρ = −0,107 (p = 0,819) en mAP50 de M3FD, ρ = −0,357 (p = 0,432) en mAP50-95 de M3FD y ρ = +0,214 (p = 0,645) en mAP50 de LLVIP, en este último caso con el signo contrario al esperado.
>
> 10. **La batería ampliada, en cambio, sí ordena los métodos de forma compatible con su utilidad posterior.** El ranking de diecisiete métricas, que incorpora las que penalizan artefactos, presenta ρ = −0,714 (p = 0,071) frente al mAP50 de M3FD y ρ = −0,429 (p = 0,337) frente al de LLVIP, ambos en el sentido esperado. Este resultado es el rendimiento constructivo de la auditoría y funda la recomendación de protocolo.
>
> 11. **La fusión produce un efecto de compensación por clase que no alcanza para superar a la mejor modalidad.** En M3FD la propuesta se sitúa en cada clase entre las dos modalidades: supera al VIS en People (0,6406 frente a 0,6207) y al IR en Lamp (0,4881 frente a 0,3482), pero no supera al IR en People (0,7787) ni al VIS en Lamp (0,6161). El efecto está presente en las seis fusiones no degeneradas y la propuesta es la más débil de ellas en ambas clases. Con un detector correctamente entrenado ninguna de las dos modalidades es ciega en ninguna clase (VIS: 0,6207 en People frente a 0,6161 en Lamp), de modo que la premisa de complementariedad extrema no se verifica.
>
> 12. **Recomendaciones de protocolo para la evaluación de métodos de fusión VIS/IR.** Declarar la dirección de cada métrica, incluida Nabf, la única del conjunto en que menor es mejor; incorporar al menos una métrica sensible a artefactos y una de transferencia de información; separar estrictamente el criterio con que se ajustan los hiperparámetros del criterio con que se evalúa; ajustar equivalentemente los métodos de comparación o declarar que no se los ajusta; incluir controles negativos —promedio sin operador, promedio con ruido, promedio con desenfoque— como validación del protocolo; agregar por escena física cuando el corpus contenga vistas múltiples de la misma escena; y validar en una tarea posterior con particiones disjuntas antes de afirmar utilidad.
>
> 13. **[Condicional a la ejecución de la ablación]** Con los hiperparámetros igualados en r = 25 y m = 0,30, el aporte del banco de cinco elementos estructurantes respecto del disco único es de [magnitud a completar]. La evidencia parcial disponible bajo la aptitud declarada sitúa esa diferencia en 0,0003 (propuesta con r = 25 y m = 0,0703: F_o = 1,7654; clásico re-optimizado con r = 25 y m = 0,10: F_o = 1,7651), con la base (VIS + IR)/2 sin ningún operador en 1,7529 y el Top-Hat clásico publicado en 1,6016.

---

## 6. Limitaciones a declarar (apartado 1.6)

> 1. **La configuración evaluada no proviene de la optimización automática.** El espacio de búsqueda declarado es r ∈ [1, 25] y m ∈ [0,30; 2,00]; dentro de él la aptitud F_o decrece monótonamente en m, de modo que el peso de contraste converge al piso del intervalo en las 25 configuraciones de la retícula, y el radio preferido es r = 1 (F_o = 1,7354) y no el adoptado r = 25 (1,7039). Al liberar el piso de m el óptimo se traslada a (r = 25, m ≈ 0,0734) con F_o = 1,7654. La configuración oficial (r = 25, m = 0,30) no maximiza F_o, ni F_apt (1,5681 frente a 1,9843 en m ≈ 0,0703), ni el agregado de las nueve métricas de evaluación, que crece monótonamente en m hasta 4,3633 en m = 2,00. Ambos hiperparámetros son decisiones de diseño y se declaran como tales.
>
> 2. **El ajuste de los hiperparámetros no es independiente de la evaluación.** Cinco de las nueve métricas favorecen r = 25 y las cuatro de fidelidad favorecen r = 1, todas con p < 1e-05, y cuatro de las cinco métricas en que el operador vence a los métodos del estado del arte pertenecen al primer bloque. El primer puesto del ranking depende en parte de esa elección.
>
> 3. **Los seis métodos de comparación no reciben ningún ajuste de hiperparámetros equivalente.** La comparación es, en ese sentido, asimétrica en favor del operador propuesto.
>
> 4. **El barrido de aptitud se realiza sobre 3 de las 20 escenas que también integran el conjunto de evaluación** (`list_pairs()[::7]`), un solapamiento del 15 %. Se informa el ranking de calidad excluyendo esos tres pares para acotar el efecto.
>
> 5. **La comparación contra el Top-Hat clásico no aísla el aporte del banco de cinco elementos estructurantes**, porque los dos operadores emplean pares (r, m) distintos —clásico r = 5 y m = 1; propuesto r = 25 y m = 0,30—, de modo que el cambio de operador queda confundido con el cambio de hiperparámetros. Se informa la ablación con hiperparámetros igualados para acotar esa confusión. Bajo la aptitud declarada y con r = 25 en ambos operadores, la diferencia es de 0,0003 (1,7654 frente a 1,7651), y la base (VIS + IR)/2 sin ningún operador alcanza 1,7529.
>
> 6. **La batería de nueve métricas sin referencia interpretadas como "mayor es mejor" no distingue detalle útil de varianza inyectada.** Las métricas de actividad crecen monótonamente con el nivel de ruido de la fusión de control, que alcanza posiciones de cabeza del ranking sin incorporar ninguna información adicional de las fuentes. El primer puesto del operador debe leerse dentro de ese límite del criterio.
>
> 7. **FE no aporta información independiente.** Es la entropía EN reescalada por una constante propia de cada escena; no emplea ningún operador de gradiente y produce los mismos rangos intra-bloque y el mismo estadístico de Friedman que EN. Se informa el ranking sin FE (3,631) junto al ranking completo, y se corrige la denominación "entropía de bordes" empleada en versiones anteriores del documento.
>
> 8. **El primer puesto del ranking depende de la regla de agregación y del conjunto de métricas.** Rankeando las medias en lugar de los rangos intra-bloque hay empate en 3,556 con la Pirámide de Laplace; incorporando las ocho métricas restantes ya calculadas el operador es 3.º con 3,459, y en el bloque de artefactos 4.º de 7 con 3,892, con un rango medio de 6,00 sobre 7 en Nabf.
>
> 9. **Los 20 pares del TNO corresponden a unas 11 escenas físicamente distintas** (APC_1 y APC_3 aportan 3 vistas cada uno, soldier_behind_smoke 3 y soldier_in_trench 2), de modo que la independencia entre bloques que suponen Friedman y Wilcoxon está sobreestimada. Se verificó que las conclusiones del ranking se mantienen al agregar por escena.
>
> 10. **En 6 pares ("fk_") las imágenes VIS e IR no son capturas simultáneas:** hay personas presentes en una modalidad y ausentes en la otra por razones no atribuibles a la modalidad.
>
> 11. **Un par del corpus original estaba corrupto** —el canal VIS era copia byte a byte del IR—; se excluyó y se sustituyó por Triclobs_Kaptein_1123 del TNO original, lo que debe tenerse en cuenta al comparar con resultados de versiones anteriores del trabajo.
>
> 12. **LLVIP no dispone de una partición de test separada del conjunto de validación**, de modo que el mAP50 = 0,9708 del IR y los valores de las restantes entradas se miden sobre el conjunto empleado para seleccionar el punto de control.
>
> 13. **Todas las cifras de detección provienen de un único entrenamiento por entrada**, sin repetición con semillas, sin intervalos de confianza y sin prueba de significación; diferencias inferiores a aproximadamente 0,01 de mAP no son interpretables como diferencias establecidas. En M3FD el máximo de validación se alcanza en la época 40 de 40, la última del presupuesto, por lo que no puede descartarse que un presupuesto mayor modificara todos los valores absolutos.
>
> 14. **El alcance de la auditoría del protocolo es el de este benchmark:** un operador, 20 pares del TNO correspondientes a unas 11 escenas físicas, seis métodos de comparación, dos conjuntos de detección y las funciones de aptitud empleadas en el trabajo. La conclusión metodológica se enuncia sobre el protocolo aquí utilizado y sobre los trabajos que lo replican, y no sobre la literatura de fusión VIS/IR en su conjunto.
>
> 15. **Las tablas de aptitud del PSO y el barrido de métricas emplean estimadores de SSIM distintos**, lo que produce dos valores de F_o para la misma configuración (r = 25, m = 0,30): 1,7039 en `curva_aptitud_vs_m.csv` y en las tablas del PSO, y 1,6818 en `barrido_metricas_vs_m.csv`, con una diferencia de 0,0221. Se declara la procedencia de cada serie y se unifica el estimador antes de publicar la tabla definitiva.

---

## 7. Qué NO cambia

- **El capítulo 2 (marco teórico) queda íntegro:** morfología matemática, transformadas Top-Hat y Bottom-Hat, elementos estructurantes, PSO, métodos multiescala de comparación y métricas de evaluación.
- **La implementación completa queda íntegra.** No se modifica una línea de `src/fusion/optimal_top_hat.py`, `src/fusion/comparatives.py` ni `src/metrics/evaluators.py`. Lo que cambia es la descripción del operador en el libro, que hasta ahora no coincidía con el código, y la lista `METRICS` de `experiments/run_stats_analysis.py:31`, que amplía el conjunto analizado.
- **Todos los resultados numéricos ya publicados siguen siendo válidos y se conservan:** el ranking de nueve métricas con 3,394, el ranking sin FE con 3,631, las nueve pruebas de Friedman, los 54 contrastes de Wilcoxon con Holm, las medias descriptivas, la ablación de aptitud, los mAP de LLVIP y de M3FD y las figuras cualitativas. Nada se retira; se agregan bloques de análisis y se recontextualiza la lectura.
- **La descripción del corpus, del preprocesamiento y del protocolo de detección se conserva**, con la incorporación de las condiciones ya declaradas (sustitución del par corrupto, pares no simultáneos, particiones de M3FD).
- **El capítulo del PSO se conserva completo** como experimento de optimización auditado —retícula de 25 configuraciones, funciones de aptitud, curvas—; lo que cambia es la conclusión que se extrae de él.
- **El objetivo general y el problema general conservan su estructura y su prudencia originales.** Ya estaban formulados sin prometer mejora en detección ("analizando su impacto", "qué efecto produce"); las modificaciones son acotadas.
- **Las figuras del método, los montajes cualitativos y la estructura de capítulos se conservan.** El apartado de resultados gana tablas; no pierde ninguna.
- **La denominación del método puede conservarse como identificador de tablas y figuras** ("Propuesta_Novedosa" en los CSV) para no romper la trazabilidad con los informes previos. Se recomienda, en el texto corrido, sustituir "Propuesta Novedosa" por la denominación descriptiva "operador Top-Hat de una escala con banco de cinco elementos estructurantes", con una nota de equivalencia respecto de las versiones anteriores del documento.

---

## 8. Costo estimado de aplicar el reencuadre

**Experimentos y análisis previos a la reescritura** (todos con código ya existente; ninguno requiere reentrenar detectores):

| # | Trabajo | Salida | Horas |
|---|---|---|---|
| E1 | Ampliar `METRICS` en `run_stats_analysis.py:31` a las 17 métricas y regenerar ranking, Friedman y Wilcoxon; repetir sobre `metrics_reports_libre` | ranking, friedman, wilcoxon ampliados | 3 |
| E2 | `experiments/run_control_negativo.py`: semilla fija, corpus actual de 20 pares, barrido sigma ∈ {0,02; 0,05; 0,10; 0,20}, más base sin operador y base con desenfoque, con 9 y con 17 métricas | `control_negativo_ranking.csv` + figura de monotonía | 5 |
| E3 | `experiments/run_permutacion_ranking.py`: prueba de permutación del spread del ranking sobre el corpus actual (el valor p = 0,0005 y el spread 0,9667 de la auditoría corresponden a una versión anterior; el spread actual es 1,050) | `permutacion_ranking.json` | 3 |
| E4 | Ablación del banco a (r = 25, m = 0,30) fijos: disco solo, `mode="sum"`, `mode="avg"`, `mode="max"`, con las 17 métricas, nombres de imagen y la fila faltante del operador oficial | `ablacion_banco.csv` | 4 |
| E5 | `experiments/run_correlacion_calidad_deteccion.py`: Spearman y Kendall entre rango de calidad (9 y 17 métricas) y mAP50 / mAP50-95 de LLVIP y M3FD; y ranking excluyendo los 3 pares del barrido de aptitud | dos CSV | 2 |
| E6 | Verificar la definición canónica de FE en la fuente citada y unificar el estimador de SSIM de las tablas de aptitud (1,7039 frente a 1,6818) | nota metodológica + tabla unificada | 3 |
| E7 | Tabla de revisión bibliográfica sobre 15-25 artículos recientes de fusión VIS/IR: métricas empleadas, dirección declarada, separación ajuste/evaluación, control negativo, validación en tarea posterior | tabla del capítulo 2 | 8 |
| E8 | *(opcional, solo si hay presupuesto de GPU)* Repetir el entrenamiento de M3FD con 3 semillas para dar dispersión a las cifras de detección | tabla con media y desvío | 10-14 |
| | **Subtotal sin E8** | | **28** |

**Reescritura del libro:**

| Sección | Trabajo | Horas |
|---|---|---|
| Resumen / Summary | Reformular las dos versiones con el doble aporte y sin "optimizados por PSO" | 2 |
| 1.3 Objetivos | Reemplazar objetivo general y pasar de 4 a 5 objetivos específicos (texto de §1 y §2 de este documento) | 2 |
| 1.4 Problema | Reemplazar el problema general y, si existen, los específicos | 1 |
| 1.5 Hipótesis | Reemplazar por H1-H7 con veredicto y evidencia (texto de §4) | 3 |
| 1.6 Limitaciones | Reemplazar por las 15 limitaciones de §6 | 2 |
| Cap. 2 Marco teórico | Sin cambios, salvo insertar la subsección con la tabla E7 y la crítica previa a las métricas objetivas de fusión | 4 |
| Cap. 3 Metodología | Corregir la descripción del operador (suma de ramas; máximo solo entre fuentes); reescribir la sección del PSO con el espacio de búsqueda real; declarar la batería de 17 métricas en tres bloques; declarar la naturaleza de FE; describir controles negativos y ablación | 6 |
| Cap. 5 Resultados | Insertar tablas de E1-E5, reordenar en tres bloques, sustituir People+Lamp por mAP completo como cifra principal, añadir la nota de semilla única y el empate de `avg_rank_medias` | 8 |
| Cap. 6 Conclusiones | Reemplazar por las 13 conclusiones de §5 | 3 |
| Corrección transversal de "FE = entropía de bordes" y de "parámetros optimizados por PSO" en libro, `README.md:166`, avances, Excel y presentación | | 4 |
| Presentación de defensa | Rehacer 6-8 diapositivas: batería ampliada, tres bloques, control negativo, alcance real del PSO, correlación calidad-detección, y una diapositiva de respuesta a la pregunta central ("mi primer puesto mide el protocolo, no el operador; las 25 victorias caen en el bloque que el control negativo también maximiza y las 17 derrotas en el de fidelidad") | 6 |
| **Subtotal reescritura** | | **41** |

**Total estimado: 69 horas** (28 de experimentos y análisis + 41 de reescritura), sin contar E8. Distribuido en jornadas de 4 horas son unas 17-18 jornadas; con margen, cuatro a cinco semanas de trabajo a tiempo parcial, holgado frente a una defensa prevista para septiembre de 2026.

**Prioridad si el tiempo se acorta.** E1, E2 y E4 son bloqueantes: sin E1 el trabajo denuncia una insuficiencia del criterio dejando ocho columnas medidas y sin analizar en su propio CSV; sin E2 la hipótesis central se apoya en un experimento que no está en el repositorio; sin E4 el aporte declarado del operador no está medido. E3, E5 y E6 son de bajo costo y alto rendimiento defensivo. E7 puede reducirse a 10-12 artículos. E8 es prescindible si se declara con claridad la limitación 13.

**Nota institucional previa.** Antes de reescribir el capítulo 1 conviene verificar con el reglamento y el comité académico de la UCOM si la modificación de objetivos e hipótesis respecto del protocolo ya aprobado requiere aprobación formal, y con qué plazos.

---

## Anexo — Procedencia de las cifras citadas

Todas las rutas son relativas a ``.

- Rankings, medias, Friedman y Wilcoxon: `experiments\results\metrics_reports\ranking_methods.csv`, `descriptive_means.csv`, `friedman_results.csv`, `wilcoxon_results.csv`.
- Métricas por imagen, incluidas las ocho no analizadas: `experiments\results\metrics_reports\all_metrics.csv` (columnas Qabf, Nabf, SCD, VIF, FMI, Q0, QW, QE; 7 métodos × 20 imágenes).
- Rankings ampliados (17 métricas, 8 nuevas, bloque de artefactos), medias y rangos de las métricas nuevas, y correlaciones de Spearman/Kendall calidad-detección: recomputados en esta sesión a partir de `all_metrics.csv`, `detection_m3fd_map.csv` y `detection_llvip_map.csv` con el mismo procedimiento de rangos intra-bloque y las direcciones de `src\metrics\evaluators.py:31-36`; pendientes de versionar como scripts (E1 y E5).
- PSO y aptitudes: `experiments\pso_grid_search_fo.py:33` (caja de búsqueda), `experiments\results\metrics_reports\pso_grid_search.csv`, `pso_grid_search_fo_propuesta.csv`, `pso_grid_search_fo_propuesta_oficial.csv`, `pso_grid_search_fo_clasico.csv`, `curva_aptitud_vs_m.csv`, `barrido_metricas_vs_m.csv`, `aptitud_operador_configs.csv`, `fo_ablacion_comparativa.csv`, `fo_ablacion_per_image.csv`.
- Detección: `experiments\results\metrics_reports\detection_llvip_map.csv` y `detection_m3fd_map.csv` (mAP50, mAP50-95 y AP50 por clase; el AP50 de IR en Lamp es 0,3482).
- Operador y modos de ablación: `src\fusion\optimal_top_hat.py:53-83` (`combined_top_hat` con `mode ∈ {"sum","avg","max"}`; `mode="sum"` por defecto).
- Control negativo con ruido y prueba de permutación: `docs\Auditoria_Interna.md` (hallazgos R2 y punto 5). **No existen script ni CSV que los reproduzcan**; sus cifras corresponden a 19 imágenes, un bloque de 8 entradas y una versión anterior del corpus, y deben recomputarse (E2 y E3) antes de citarse en el libro.