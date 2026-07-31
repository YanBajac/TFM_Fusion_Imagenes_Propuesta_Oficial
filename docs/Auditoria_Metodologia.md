# Auditoria de la metodologia — segunda revision

_Revision en seis frentes que la primera auditoria no cubrio: los seis metodos comparativos, el operador propuesto, el codigo escrito en las ultimas 48 horas, la coherencia entre la teoria del libro y el codigo, la reproducibilidad y la validez del diseno experimental. 69 defectos reportados, 9 confirmados tras refutacion adversarial (ninguno refutado), 14 puntos verificados como correctos._

---

## 1. LA PREGUNTA DE FONDO: ¿ES VÁLIDA LA METODOLOGÍA?

**Respuesta: CON RESERVAS.** No hay fraude ni error que invalide los números, pero el titular del resultado central —«la propuesta es 1.ª del ranking agregado»— **no es defendible tal como está enunciado hoy**. Hay que reformularlo, no rehacer la tesis.

Lo primero, porque es lo que más importa y es una buena noticia:

**Ningún comparativo está en desventaja artificial por mala implementación.** Esto se verificó ejecutando código, no leyendo. Los cinco métodos multiescala pasan el test de identidad (fusionar una imagen consigo misma) con error de 0 a 1,1e-5, es decir sin pérdida por recorte, cast a entero ni remuestreo mal hecho. La DTCWT es la biblioteca de referencia de Kingsbury y usa efectivamente sus 6 subbandas complejas por nivel (24 en total). La Ratio Pyramid es una pirámide de cocientes genuina de Toet, con la protección contra división por cero puesta en el lugar correcto (el cociente tiende a 1, el valor neutro, no a infinito). El único defecto de implementación real del benchmark —la Pirámide de Laplace fusiona su banda base por máxima actividad en vez de promediarla— **favorece a la Laplace y juega en contra de la propuesta**: corregido, la Laplace cae del 2.º al 4.º puesto y la propuesta se mantiene 1.ª. Es decir, el benchmark, en lo que hace a implementación, es conservador respecto de la propuesta.

Dicho eso, hay tres reservas, en orden de gravedad:

**Reserva 1 (la que obliga a reescribir el titular): el ajuste de hiperparámetros es asimétrico y el compuesto de 9 métricas no tiene óptimo interior.** El único hiperparámetro libre de la propuesta que se eligió mirando las métricas de evaluación (r = 25) se eligió así —está autodeclarado en `experiments/run_all_fusions.py:36-43`—, y a ninguno de los seis comparativos se le dio ese paso. Al darlo (800+ fusiones nuevas, control validado contra el CSV oficial con max|dif| = 5e-7), basta darle al Top-Hat clásico su mismo radio r = 25 para que pase a 3,517 y la propuesta a 3,622: **2.º puesto**. Peor: el argmin del compuesto está en el borde de la rejilla para 6 de los 7 métodos, y al extenderla (r = 51) el orden se disuelve. El compuesto de 9 métricas premia monótonamente la inyección de realce; no mide calidad de fusión, mide agresividad. Eso significa que el 1.er puesto es una propiedad del criterio, no del operador.

**Reserva 2: uno de los seis «comparativos» no es un método distinto.** El rotulado «Curvelet» es el mismo código de la DWT con wavelet db4: al igualar la wavelet, `max|curvelet_fusion − dwt_fusion| = 0,000e+00` sobre los 20 pares. No hay ninguna implementación de curvelet en el repo (`requirements.txt` no la tiene). El libro (Tabla 3) lo atribuye a Candès et al. (2006). Es un problema de representación y de crédito bibliográfico, **no de resultados**: quitando ese comparativo la propuesta sigue 1.ª (2,961 frente a 3,444), y quitando también la DWT sigue 1.ª (2,539). Pero «cinco métodos representativos del estado del arte» son en rigor cuatro familias.

**Reserva 3: al configurar la propuesta y el disco único con los mismos (r = 25, m = 0,30), empatan.** El banco de 5 elementos estructurantes no aporta ventaja medible en el compuesto en el punto exacto que la tesis publica (1,500 vs 1,500 sin FE). En 11 de las otras 12 combinaciones (r, m) igualadas la propuesta sí gana, pero la configuración oficial es justamente la del empate.

**Lo que sí sobrevive a todo el estrés aplicado**, y hay que decirlo con la misma claridad:
- **Los cinco métodos del estado del arte nunca destronan a la propuesta**, ni siquiera todos ajustados a la vez (propuesta 3,372; 2.º RP 3,683). El único que la supera es el Top-Hat clásico, que no es estado del arte: es la línea base ancestral de la propia familia.
- **Con `avg_rank_sin_FE` (8 métricas independientes, que la tesis ya publica) la propuesta es 1.ª en los cuatro escenarios de ajuste** (3,631 / 3,800 / 3,463 / 3,631). El vuelco vive únicamente en el conjunto de 9, donde FE es EN duplicada y la entropía pesa 2/9.
- **Las victorias en MG y SF resisten cualquier configuración** (5/5 comparativos, p ≤ 1,2e-2 con Holm). Las de EN y FE no: desaparecen con un paso de ajuste en LP, RP y DWT.
- **La ganancia sobre la propia base es real**: (VIS+IR)/2 sola queda ÚLTIMA de 8 en el compuesto de 9 métricas. El mérito no viene de la base.

---

## 2. QUÉ HAY QUE CORREGIR ANTES DE DEFENDER

Ordenado por gravedad. Total del bloque obligatorio: **≈ 12-14 h**. Con el bloque recomendado: **≈ 24-28 h**.

### Obligatorio (sin esto, la defensa tiene un flanco abierto que la mesa puede abrir sola)

**1. Reformular el titular del ranking y declarar la asimetría de ajuste. (5 h)**
Reemplazar «1.ª del ranking agregado» por dos frases: (a) «1.ª del ranking agregado cuando los seis comparativos se ejecutan en su configuración estándar de la literatura»; (b) reportar `avg_rank_sin_FE` (3,631) como resultado principal, porque es el único de los dos que resiste el ajuste de los comparativos. Añadir a limitaciones un párrafo con las cifras del barrido: basta r = 25 en el Top-Hat clásico para invertir el podio en el conjunto de 9; el compuesto no tiene óptimo interior en r. **No** afirmar que el clásico «le gana»: la diferencia es 0,105 en un compuesto, con 10/20 pares y Wilcoxon p = 0,396, y esa configuración es la última de 7 en Nabf, Qabf, SSIM, Q0 y QW.

**2. La galería del PDF de avances muestra el par excluido y omite un par válido. (1 h)**
`experiments/make_avances_report.py:460` usa `sorted(os.listdir(VIS_D))` en lugar de `list_pairs()`, y la línea 714 recorta a mano `[0:8],[8:16],[16:20]`. Resultado: el «Par 09» del PDF del 30/07 es `Athena_heather_IR_hei_vis_g` —el par cuyo VIS es copia byte a byte del IR, md5 idéntico— y `Triclobs_jeep_in_smoke_R` no aparece. Dos páginas antes, el mismo PDF declara que ese par se excluye. Es la contradicción interna más fácil de encontrar de todo el entregable. Corrección: `[p[0].name for p in list_pairs()]` y bloques calculados sobre `len(pairs_html)`. Regenerar y verificar.

**3. Sincronizar el libro con los datos vigentes. (4 h)**
`docs/Tesis_Borrador_V3.docx` (26/07) y el deck publican el ranking anterior (LP 3,44 1.ª / propuesta 3,67 2.ª) y EN = 6,9888, contra 3,911 / 3,394 y 6,9855 de `ranking_methods.csv` (29/07). El libro está una regeneración por detrás. Tablas 27, 28 y 30 del docx, más las diapositivas 11-12.

**4. Rango de m: corregir la ec. (12) y sus dos réplicas. (2 h)**
La ec. (12) declara m ∈ [0,05; 1,20] —el rango de la variante LIBRE— mientras la Tabla 2, la p. 31, §5.6 y el código dicen [0,30; 2,00]. Mismo error en la tabla de operacionalización §4.4 y en el Apéndice B. **Esto no es cosmético**: dentro del espacio que declara la ec. (12), y con la aptitud oficial F_o, el óptimo es m = 0,05 con F_o = 1,7703, que domina al reportado (1,7354), y la corrida está en el propio repo (`pso_grid_search_fo_propuesta_oficial.csv`). Con la ec. (12) tal como está, el argumento «m* = 0,30 es el límite inferior del rango» se autodestruye. Corregir además «36 configuraciones» → 25 y las referencias del Apéndice A/B al script y CSV abandonados.

**5. §3.16 describe la función de aptitud descartada. (0,5 h)**
Dice que F_o «premia la fidelidad estructural, la preservación de bordes y la correlación, y penaliza los artefactos». F_o = SSIM_avg + EN/8 + PSNR/100 no tiene ningún término de bordes, de correlación ni negativo. Los cuatro atributos son, en el mismo orden, las glosas que el propio libro da de SSIM, Qabf, SCD y Nabf, la aptitud abandonada. Lo grave es la frase «penaliza los artefactos»: la propuesta es 6.ª de 7 en Nabf, la única métrica que penaliza artefactos. Es regalarle la pregunta a la mesa.

**6. La ec. (18) (gradiente medio) es una raíz cuadrada vacía. (0,5 h)**
Verificado en el OMML del DOCX (`<m:rad>` con `<m:e/>` vacío) y en el PDF p. 33 (glifo □). Es la única de las 26 ecuaciones con este defecto. Reescribirla como MG = (1/MN)ΣΣ√(Δx² + Δy²) con Δ = diferencias centradas de `np.gradient`. **Nota importante**: la sospecha de un factor √2 respecto de la definición clásica es falsa —la discrepancia real es del 2,7 %, y con la definición clásica los 120 signos y los 6 p-valores del benchmark de MG son idénticos—. No hay nada que recomputar; es una edición en Word.

**7. Las frases con números tipeados a mano que hoy son falsas. (2 h)**
Especialmente: el documento afirma que «7 de 7 fusiones detectan ambas clases en una sola imagen» cuando el CSV correcto muestra que la propuesta resuelve **0 de 33 escenas críticas** y es batida por 5 de los 6 comparativos. También LLVIP 0,808/0,957, «18 radios», «+0,11 a +0,14», y la viñeta de Avances que atribuye r = 25 a F_o cuando el cuerpo del mismo documento declara lo contrario. Regenerar los montajes cualitativos, que son anteriores a la sustitución del par corrupto.

### Recomendado

**8. Renombrar el comparativo «Curvelet». (2 h)** → «Wavelet Daubechies db4 (3 niveles)»; retirar la cita de Candès et al. (2006) de la Tabla 3; borrar «captura estructuras anisótropas y curvas» de `make_avances_report.py:856-857`; corregir el deck, que es el único artefacto que omite el calificativo «vía wavelet 2D»; reescribir «cinco métodos del estado del arte» como «cinco configuraciones de referencia en cuatro familias». Alternativa costosa (instalar curvelops y recomputar benchmark + estadística + las dos detecciones): 15-20 h, **no la recomiendo**.

**9. Corregir la banda base de la Pirámide de Laplace y recomputar. (8 h)** Dos líneas de código (`fused_pyr[-1] = 0.5*(lv[-1]+li[-1])`) más regenerar métricas, estadística y tablas. Razón para hacerlo aunque perjudique el margen: el párrafo 397 del libro declara como hallazgo metodológico propio que «aplicar selección por actividad a la capa base... sesga las métricas de información mutua» —exactamente el defecto que su propio comparativo tiene—. Es una contradicción código-documento directamente citable. Beneficio colateral: en SD la propuesta pasa de ganar 4/5 a 5/5. Costo: pierde su única victoria en PSNR (1/5 → 0/5) y el 2.º puesto pasa a la Ratio Pyramid.

**10. Estado oculto y trazabilidad. (5 h)** (a) El checkpoint de `run_all_fusions.py` no recalcula al cambiar la configuración del operador —demostrado: con m = 1,50 devolvió el EN de m = 0,30—. (b) Catorce CSV anteriores al 29/07 16:11 (todo el barrido PSO, curvas de aptitud, ablación) son del corpus previo a la sustitución del par corrupto, y el JSON con `done=25` hace que un rerun los reescriba sin recalcular. (c) `metrics_reports_libre/` no tiene script generador y usa 19 pares. (d) 22 archivos modificados y 16 sin versionar en git, incluidos los CSV de estadística y `src/datasets.py`: un clon del repo hoy no reproduce nada de lo vigente. Esto último es 30 minutos y es lo que un jurado técnico puede pedir.

**11. Detalles de figura y apéndice. (2 h)** Figura 4 dice m = 0,0703 en lugar de 0,30; etiquetas 45°/135° cruzadas en la Figura 3; el Apéndice E describe una regla de fusión multiescala que el método ya no tiene; el «disco» es la elipse de OpenCV (sobredimensionada) y las diagonales tienen 37 px, no 51 como declara el texto; cuatro de las diez conclusiones y dos secciones del marco conceptual describen experimentos (cruz, cuadrado, multiescala con L niveles) que no existen en el diseño final.

---

## 3. TERRENO FIRME: LO QUE ESTÁ VERIFICADO Y SE DEFIENDE SIN DUDAR

Esto se comprobó ejecutando código independiente, no leyéndolo. Es bastante, y es mucho más de lo que la mayoría de las tesis puede exhibir:

**El operador propuesto es matemáticamente correcto, dígito a dígito.** Se reimplementaron las ecuaciones (7)-(11) desde el texto del libro, sin mirar el código, y `max|código − ecuaciones| = 0,000e+00` sobre los 20 pares. Apertura y cierre coinciden con erosión-dilatación de OpenCV; se cumplen γ ≤ f y φ ≥ f sin una sola violación; WTH y BTH son ≥ 0 siempre y se anulan en zonas planas; el promedio de las 4 ramas lineales divide por 4 (no por 5) y el disco entra con coeficiente 1; el máximo por píxel es por separado en WTH y BTH; la reconstrucción es exactamente I_base + m·WTH − m·BTH. La Tabla 2 y el pseudocódigo del Apéndice D coinciden. El recorte final a [0,1] afecta 0,793 % de píxeles y 0,179 % de la energía: no destruye información.

**Sutileza que además está bien y suele estar mal en otras tesis**: OpenCV no refleja el kernel en `dilate`, lo que rompería la ec. (1); se verificó que los cinco elementos estructurantes son centralmente simétricos, de modo que la ecuación describe correctamente lo implementado.

**Todo el pipeline cuantitativo es reproducible.** Se regeneró `all_metrics.csv` completo (140 filas × 17 métricas) desde `data/raw/`: diferencia máxima 5e-7 frente al publicado, que es exactamente el redondeo a 6 decimales del CSV. De ahí se derivan exactamente `descriptive_means.csv` (63 celdas, diferencia 0,0), `ranking_methods.csv`, `friedman_results.csv` y `pso_por_imagen.csv`. El PSO está íntegramente sembrado y el multiproceso no altera el resultado.

**La estadística es correcta.** Friedman, Wilcoxon exacto y Holm reproducidos dígito a dígito con implementación independiente. Las direcciones de las métricas son correctas (Nabf a minimizar, y no está en el set de 9). El ranking se corrigió de rango-de-medias a promedio de rangos intra-bloque y se reprodujo a mano sin pandas. La familia de Holm ampliada de 10 a 11 es la elección conservadora y no cambia ninguna conclusión (84 contrastes significativos en ambos casos). La potencia estadística es sobrada para todos los efectos publicados salvo dos contrastes marginales. El ranking es robusto a la redundancia entre métricas al re-pesar por familias.

**La corrección de integridad del corpus es correcta en los datos** (el problema es solo la galería del PDF): los 20 pares vigentes incluyen `Triclobs_jeep_in_smoke_R` y excluyen el par duplicado, en todas las tablas y todos los CSV.

**Los experimentos de detección están limpios.** La partición de M3FD es disjunta, estratificada (desvío máximo 0,2 pp en los cuatro estratos), sin pérdida ni duplicación, reproducible con semilla y **coincide exactamente con lo que está en disco**. Las imágenes que vio el detector son byte a byte las de la configuración publicada (r = 25, m = 0,30), verificado comparando JPEG. Cada modelo se entrenó después de generarse sus imágenes. No hay contaminación por caché en ningún artefacto vigente. El script de complementariedad se reverificó contra los XML VOC originales con tres emparejadores distintos: 612/612 filas idénticas, error de conversión de coordenadas 0,0008 px.

**El mérito no viene de la imagen base.** (VIS+IR)/2 sola es última de 8. El operador aporta +147,7 % en MG y +146,0 % en SF sobre su propia base.

---

## 4. LOS TRES RIESGOS MÁS PROBABLES EN LA DEFENSA

### Riesgo 1 — «Usted eligió r = 25 mirando las mismas nueve métricas con las que después se evalúa, y a los comparativos no les dio ese paso. Si le doy r = 25 al Top-Hat clásico, ¿sigue siendo primero?»

Es el ataque más probable y el más fuerte. **No intente negarlo: adelántelo usted.**

Respuesta preparada: «No, y lo declaro en la sección de limitaciones. Hice el barrido: con r = 25 el Top-Hat clásico pasa a 3,517 y mi método a 3,622 en el conjunto de nueve métricas. Tres cosas al respecto. Primera: ese compuesto no tiene óptimo interior en el radio —crece monótonamente con el realce inyectado y su argmin está en el borde de la rejilla para seis de los siete métodos—, de modo que lo que gana no es el mejor operador sino la configuración más agresiva; extendiendo la rejilla a r = 51 el orden se disuelve. Segunda: el vuelco vive únicamente en el conjunto de nueve, donde FE es entropía duplicada y la entropía pesa 2/9; con las ocho métricas independientes, que también publico, mi método es primero en los cuatro escenarios de ajuste. Tercera: el método que produce el vuelco es el último de los siete en Nabf, Qabf, SSIM, Q0 y QW —compra entropía con artefactos— y la diferencia no es estadísticamente distinguible: mejor en 10 de 20 imágenes, Wilcoxon p = 0,396. Y los cinco métodos del estado del arte no me destronan ni ajustándolos todos a la vez.»

### Riesgo 2 — «Si usted atribuye a Bala et al. (2024) exactamente la combinación disco + líneas orientadas, ¿qué es su aporte? ¿Y su banco de cinco elementos le gana a un solo disco con los mismos parámetros?»

Es el riesgo que la auditoría destapó y del que hoy no hay defensa escrita. Y la respuesta honesta incluye un empate.

Respuesta preparada: «Bala et al. usan el operador multiángulo en fondo de ojo, con un filtro de dos etapas y una red de denoising; yo implemento una sola etapa y lo llevo a fusión VIS-IR, que es un problema distinto, con un esquema de fusión ponderada tomado de Ortega y Espinoza. Mi aporte no es el elemento estructurante: es la evaluación. Y soy explícito en algo incómodo: en la configuración exacta que publico, r = 25 y m = 0,30, el banco de cinco elementos empata con el disco único en el compuesto; gana en once de las doce otras combinaciones (r, m) igualadas que probé, pero no en esa. Eso está en la tabla de ablación.»

Antes de la defensa: **declare el dominio real de Bala et al. y las dos diferencias de implementación en el capítulo 2**, y agregue la tabla de la ablación (r, m) igualados. Si el jurado descubre el empate y no está en el libro, el daño es mucho mayor que si lo lee escrito por usted.

### Riesgo 3 — «Su método es 6.º de 7 en Nabf, pierde con los cinco comparativos en SSIM, y ni siquiera mejora al promedio simple en ninguna métrica de fidelidad. ¿No está simplemente inyectando artefactos?»

Respuesta preparada: «Correcto en el hecho y es el compromiso explícito del operador: es un realzador de estructura, no un fusor de fidelidad. La base (VIS+IR)/2 tiene Nabf = 0 y SSIM 0,7806 contra mis 0,6584, y lo digo en el texto; pero esa base es la última de ocho en el ranking agregado, porque no aporta información: mi operador la mejora +147,7 % en gradiente medio y +146,0 % en frecuencia espacial, con significancia contra los cinco comparativos y corrección de Holm, y esas dos victorias resisten todas las configuraciones que probé. La conclusión que defiendo no es "es el mejor método de fusión", es "en las dimensiones de actividad espacial domina de forma sistemática, y el precio son artefactos y fidelidad estructural, cuantificados". Para una aplicación de detección de objetivos poco contrastados ese compromiso puede convenir; mi experimento de detección, además, no lo confirma, y también lo reporto.»

*(Cuarto riesgo, barato de blindar: «su Curvelet no es una curvelet». La única respuesta admisible es haberlo corregido antes —corrección 8—. Si llega sin corregir, diga la verdad: «es una aproximación vía wavelet db4 separable, está rotulado así en el código, en el README y en la Tabla 3, la cita a Candès no corresponde y la retiro; quitando ese comparativo el resultado no cambia: sigo primero con 2,961 frente a 3,444».)*

---

## 5. VEREDICTO SOBRE EL APORTE

**Sí, queda un aporte original defendible en una maestría en Ciencias de Datos. Pero no es el que la tesis reclama hoy.**

El aporte **no** es «un operador nuevo que supera al estado del arte»: el operador es una adaptación declarada de Bala et al. combinada con el esquema de Ortega y Espinoza, el banco de cinco elementos empata con un disco único en la configuración publicada, y el primer puesto depende del criterio de evaluación y del ajuste asimétrico del radio.

El aporte **sí** es: (a) una infraestructura experimental reproducible de punta a punta —verificada a 5e-7 sobre 20 pares, 17 métricas, siete métodos, Friedman-Wilcoxon-Holm y dos experimentos de detección con particiones disjuntas y estratificadas—, y (b) un hallazgo metodológico sólido y bien evidenciado: **el orden de mérito entre métodos de fusión VIS-IR no es una propiedad de los operadores sino del criterio con que se los evalúa**. Ese hallazgo está respaldado por tres experimentos independientes (el barrido de parámetros, el criterio F_o, y el hecho de que el promedio simple sin fusión maximiza la aptitud declarada) y es más valioso, y mucho más difícil de refutar, que un puesto en una tabla.

**Frase para decir en voz alta ante la mesa:**

> «Implementé y evalué de forma íntegramente reproducible un operador Top-Hat multiángulo de una sola escala para fusión visible-infrarroja, y demostré sobre veinte pares del TNO, con diecisiete métricas y contrastes de Friedman-Wilcoxon-Holm, que aumenta de manera sistemática y estadísticamente significativa la actividad espacial de la imagen fusionada —gradiente medio y frecuencia espacial, cinco de cinco comparativos— al precio cuantificado de fidelidad estructural y artefactos; y en el camino documenté que el orden de mérito entre métodos de fusión depende más del criterio de evaluación y del ajuste de hiperparámetros que del operador mismo, hasta el punto de que la aptitud que la literatura propone para optimizar estos métodos premia por encima de todos ellos a no fusionar.»

Esa frase es verdadera, está respaldada línea por línea por lo verificado, y no puede ser desmontada por ninguna de las preguntas de la sección 4.