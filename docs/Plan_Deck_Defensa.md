## PLAN DE EDICIÓN DEL DECK DE DEFENSA
Fuente leída: `C:\Users\Usuario\Documents\unv\mastertesis\tesis_mciencias_datos\docs\Tesis_Defensa_Presentacion.pptx` (19 diapositivas, volcado completo con python-pptx, incluidas tabla y notas del orador). Todas las cifras del plan fueron re-verificadas contra los CSV vigentes de `experiments/results/metrics_reports/` y contra `docs/Reencuadre_Final.md`.

---

# 0. Reestructuración: mapa viejo → nuevo (19 → 22 diapositivas)

| Nueva | Viene de | Título nuevo |
|---|---|---|
| 1 | 1 | (portada) |
| 2 | 2 | Contenido |
| 3 | 3 | 1. Problema: dos preguntas, no una |
| **4** | **NUEVA** | 2. Los dos aportes de la tesis |
| 5 | 4 | 3. Objetivos |
| 6 | 5 | Hipótesis de trabajo |
| 7 | 6 | 4. La transformada Top-Hat y la fusión clásica |
| 8 | 7 | 5. El operador: banco de SE y suma de ramas |
| 9 | 8 | 6. Alcance real de la optimización por PSO |
| 10 | 9 | 7. Diseño experimental |
| 11 | 10 | 8. Resultados cualitativos |
| 12 | 11 | Resultados cuantitativos por bloques — medias sobre 20 pares |
| 13 | 12 | Análisis estadístico: el punto de operación se desplaza (H1) |
| **14** | **NUEVA** | 9. Auditoría I — ¿discrimina calidad la batería? (H3, H4) |
| **15** | **NUEVA** | Auditoría II — el orden de mérito es propiedad del criterio (H2) |
| **16** | **NUEVA** | Auditoría III — ¿cuánto aporta el banco? (H7) |
| 17 | 13 | 10. Contraste externo I — detección en LLVIP (H6) |
| 18 | **14 + 15 fundidas** | Contraste externo II — M3FD: el conteo por escena (H6) |
| 19 | 16 | 11. Contraste de las siete hipótesis |
| 20 | 17 | Conclusiones |
| 21 | 18 | Recomendaciones y trabajo futuro |
| 22 | 19 | Muchas gracias |
| R | (de la vieja 15) | RESERVA — montaje de detecciones M3FD (sin numerar) |

---

# 1. Cambios por diapositiva

## Diapositiva 1 — Portada
**Shape `Text 2` (subtítulo), ANTES:**
```
Una propuesta de Top-Hat/Bottom-Hat de una sola escala con elementos estructurantes
de disco y lineales, optimizada por PSO
```
**DESPUÉS:**
```
Un operador Top-Hat/Bottom-Hat de una sola escala con un banco de cinco elementos
estructurantes — y una auditoría del protocolo con que se lo evalúa
```

**NOTAS, ANTES:** `Saludo a la mesa. Presentar el título y a los autores. Una frase: la tesis propone y valida un método de fusión de imágenes visibles e infrarrojas basado en morfología matemática de una sola escala, optimizado automáticamente.`
**DESPUÉS:**
```
Saludo a la mesa. Presentar el título y a los autores. Una frase de encuadre: la tesis tiene dos aportes — un operador de fusión VIS/IR por morfología matemática de una sola escala, y una auditoría del protocolo de evaluación con que se lo juzga, usando el propio desarrollo como caso de estudio.
```

---

## Diapositiva 2 — Contenido
**Shape `Text 2`, ANTES (9 párrafos):**
```
1.  Problema y justificación
2.  Objetivos e hipótesis
3.  Marco: la transformada Top-Hat y la fusión clásica
4.  Propuesta novedosa: banco de elementos estructurantes y suma de ramas
5.  Optimización de hiperparámetros por PSO
6.  Diseño experimental
7.  Resultados: cualitativos, cuantitativos y estadísticos
8.  Evaluación orientada a tarea: detección en LLVIP y M3FD
9.  Conclusiones y recomendaciones
```
**DESPUÉS (11 párrafos):**
```
1.  Problema: dos preguntas, no una
2.  Los dos aportes de la tesis
3.  Objetivos e hipótesis (cinco objetivos específicos, siete hipótesis)
4.  Marco: la transformada Top-Hat y la fusión clásica
5.  El operador: banco de cinco elementos estructurantes y suma de ramas
6.  Alcance real de la optimización por PSO
7.  Diseño experimental: el benchmark y los controles de la auditoría
8.  Resultados: el punto de operación del operador
9.  Auditoría del protocolo de evaluación (tres controles)
10. Contraste externo: detección en LLVIP y M3FD
11. Contraste de hipótesis, conclusiones y recomendaciones
```
*Maquetación: bajar el cuerpo a 16 pt para que las 11 líneas quepan en los 3.657.600 EMU del recuadro.*

**Footer `Text 1`:** `2 / 19` → `2 / 22`

**NOTAS, ANTES:** `Recorrido de 20 minutos: del problema al método, del método a la evidencia (calidad de imagen, estadística y detección), y de la evidencia a las conclusiones.`
**DESPUÉS:**
```
Recorrido de 20 minutos. Señalar que los puntos 1 a 8 son el primer aporte —el operador y su caracterización— y el punto 9 el segundo: la auditoría del criterio con que se lo evaluó. Los resultados negativos de los puntos 9 y 10 son parte del diseño del trabajo, no una concesión.
```

---

## Diapositiva 3 — Problema y justificación
**Título `Text 0`, ANTES:** `1. Problema y justificación`
**DESPUÉS:** `1. Problema: dos preguntas, no una`

**Shape `Text 2`, ANTES (5 párrafos):**
```
El sensor visible (VIS) aporta detalle y textura, pero se degrada en baja iluminación.
El sensor infrarrojo (IR) capta la firma térmica (personas, vehículos), pero pierde el contexto de la escena.
La fusión a nivel de píxel integra ambas fuentes en una sola imagen útil para vigilancia nocturna.
Los métodos multiescala (pirámides, wavelets, curvelets) son efectivos pero pueden introducir artefactos.
La morfología matemática permite un operador de una sola escala: interpretable, de bajo costo y con pocos artefactos.
```
**DESPUÉS (5 párrafos):**
```
El sensor visible (VIS) aporta detalle y textura pero se degrada en baja iluminación; el infrarrojo (IR) capta la firma térmica pero pierde el contexto de la escena.
La fusión a nivel de píxel integra ambas fuentes en una sola imagen útil para vigilancia nocturna.
Los métodos multiescala (pirámides, wavelets, curvelets) son efectivos y, en los datos de este trabajo, son los más conservadores en artefactos (Nabf: pirámide de Laplace 0,114 frente a 0,374 de la propuesta y 0,586 del Top-Hat clásico).
La morfología matemática ofrece un marco alternativo de una sola escala: interpretable, de bajo costo y con un realce direccional controlable por un solo peso. El compromiso es actividad espacial contra fidelidad, no una ventaja en artefactos.
Y hay un segundo problema, previo al primero: la fusión VIS/IR no tiene imagen de referencia, y se evalúa con baterías de métricas sin referencia leídas todas como «mayor es mejor», con los hiperparámetros elegidos sobre esas mismas métricas.
```

**Footer:** `3 / 19` → `3 / 22`

**NOTAS, ANTES:** `Motivar con la imagen: la misma escena en VIS, IR y fusionada. El problema práctico es la vigilancia nocturna: ni VIS ni IR bastan por separado.`
**DESPUÉS:**
```
Motivar con la imagen: la misma escena en VIS, IR y fusionada. Ni VIS ni IR bastan por separado. Retirar aquí la promesa de «pocos artefactos»: el trabajo no puede sostenerla, porque ninguna de las nueve métricas reportadas penaliza artefactos y la única que sí lo hace, Nabf, coloca a los dos operadores morfológicos como los dos peores del benchmark. Esa constatación es el arranque del segundo aporte.
```

---

## Diapositiva 4 — NUEVA: Los dos aportes de la tesis
*Insertar entre el problema y los objetivos. Layout: título + dos bloques de igual ancho (izquierda «Aporte 1», derecha «Aporte 2») + dos líneas de cierre a todo el ancho.*

**Título:** `2. Los dos aportes de la tesis`
**Footer:** `4 / 22`

**Bloque izquierdo — encabezado:** `Aporte 1 — El operador y su caracterización`
**Bloque izquierdo — cuerpo:**
```
Un Top-Hat/Bottom-Hat de una sola escala con banco de cinco elementos estructurantes: un disco de radio r y cuatro segmentos lineales a 0°, 45°, 90° y 135°.
Determinar en qué dirección desplaza el punto de operación de la fusión frente a la metodología clásica y a cinco configuraciones de referencia del estado del arte.
```

**Bloque derecho — encabezado:** `Aporte 2 — La auditoría del protocolo de evaluación`
**Bloque derecho — cuerpo:**
```
¿Qué autoriza a concluir un criterio formado por nueve métricas sin referencia de tipo «mayor es mejor», hiperparámetros elegidos sobre esas mismas métricas y una validación en tarea posterior?
Con el propio desarrollo como caso de estudio. Los tres controles —control negativo con degradaciones conocidas, ablación del banco con hiperparámetros igualados y ajuste simétrico de los comparativos— están corridos, versionados y son reproducibles.
```

**Cierre a todo el ancho:**
```
La tesis no sostiene que el método sea mejor. Sostiene que desplaza el punto de operación en una dirección determinada, y que el orden de mérito que lo corona es propiedad del criterio.
Pregunta central: ¿en qué dirección desplaza el punto de operación de la fusión un Top-Hat con banco de cinco elementos estructurantes, y en qué medida el protocolo con que se lo juzga autoriza conclusiones sobre la calidad de la imagen y sobre su utilidad práctica?
```

**NOTAS:**
```
Esta es la diapositiva que reencuadra la defensa. Declararlo aquí evita que la auditoría se lea después como autosabotaje: todo lo que sigue, incluidos los resultados negativos, es parte del diseño. Anticipar que el propio libro declara la circularidad del radio, la redundancia de FE y la ausencia de una métrica de artefactos, y que esas tres declaraciones son resultados del trabajo, no concesiones.
```

---

## Diapositiva 5 — Objetivos
**Shape `Text 3` (objetivo general), ANTES:**
```
Desarrollar y evaluar un método de fusión VIS/IR basado en transformadas Top-Hat de una sola escala, con un banco de elementos estructurantes de disco y líneas combinado por suma, optimizado por PSO, comparándolo con la metodología clásica Top-Hat y con métodos representativos del estado del arte.
```
**DESPUÉS:**
```
Diseñar, implementar y caracterizar un operador de fusión VIS/IR basado en la transformada Top-Hat de una sola escala con un banco de cinco elementos estructurantes, determinando en qué dirección desplaza el punto de operación de la fusión frente a la metodología clásica y a cinco configuraciones de referencia sobre el TNO Image Fusion Dataset; y auditar, con ese mismo desarrollo como caso de estudio, la validez discriminativa del protocolo de evaluación empleado.
```

**Shape `Text 5` (objetivos específicos), ANTES (4 párrafos):**
```
Formular el operador: disco de radio r + cuatro líneas orientadas (0°, 45°, 90°, 135°), con las respuestas lineales promediadas y sumadas a la del disco.
Ajustar los hiperparámetros (r, m) mediante PSO, con un barrido de 25 configuraciones del enjambre (Ortega y Espinoza, 2025).
Comparar con la fusión Top-Hat clásica y cinco métodos del estado del arte (LP, RP, DWT, DTCWT, CVT) sobre nueve métricas, con pruebas de Friedman y Wilcoxon–Holm.
Evaluar el efecto en detección de peatones (YOLOv8n reentrenado sobre LLVIP).
```
**DESPUÉS (5 párrafos):**
```
OE1. Formular e implementar el operador tal como efectivamente se evalúa —el promedio de las cuatro líneas se suma a la respuesta del disco; el máximo opera entre fuentes, no entre ramas— y aislar el aporte del banco mediante una ablación con hiperparámetros fijos.
OE2. Delimitar el alcance real de la optimización por PSO: qué hiperparámetro determina la aptitud declarada, qué forma tiene esa aptitud, y con qué criterios independientes de ella se justifica el peso adoptado.
OE3. Comparar con la metodología clásica y cinco configuraciones de referencia sobre nueve métricas (Friedman y Wilcoxon–Holm), organizando los resultados en bloques de actividad espacial y de fidelidad a las fuentes, y verificando la robustez frente a un ajuste simétrico de los comparativos.
OE4. Evaluar si la batería empleada discrimina calidad de fusión, con tres pruebas: control negativo con degradaciones conocidas, redundancia interna entre métricas y sensibilidad del orden de mérito a la composición del conjunto.
OE5. Medir el efecto de la fusión sobre la detección con dos experimentos independientes (LLVIP y M3FD) y contrastar el orden de mérito de las métricas con el de utilidad en la tarea, mediante un conteo por escena y no solo el mAP promedio.
```

**Footer:** `4 / 19` → `5 / 22`

**NOTAS, ANTES:** `Un objetivo general y cuatro específicos: formular, optimizar, comparar y evaluar en tarea. Cada específico se responde en una sección de resultados.`
**DESPUÉS:**
```
Un objetivo general y cinco específicos. Dos precisiones frente a la versión anterior: el objetivo general dice «caracterizar», no «evaluar», y no menciona el PSO, porque ninguno de los dos hiperparámetros de la configuración evaluada es un resultado de la optimización; y OE4 y OE5 incorporan la auditoría del criterio y el segundo experimento de detección. Cada objetivo específico se responde en una sección de resultados.
```

---

## Diapositiva 6 — Hipótesis de trabajo
*Rediseño: reemplazar las seis cajas actuales (`Text 2`…`Text 7`) por un único cuadro de texto de 8.229.600 EMU de ancho con siete párrafos a 12–13 pt, más una línea de pie.*

**Título, ANTES:** `Hipótesis de trabajo`
**DESPUÉS:** `Siete hipótesis de trabajo`

**ANTES (contenido de las seis cajas):**
```
H1 | La combinación del disco con las líneas orientadas —promediadas y sumadas— mejora la actividad, el detalle y el contenido informativo (EN, FE, SD, MG, SF) frente a los métodos del estado del arte, y supera a la metodología clásica Top-Hat en seis de las nueve métricas.
H2 | La optimización de (r, m) por PSO alcanza un desempeño superior al de la parametrización manual del operador clásico.
H3 | Una mejor calidad de fusión se traduce en un mejor desempeño de detección de objetos (mAP) que el de las modalidades individuales.
```
**DESPUÉS (cuadro único, siete párrafos):**
```
H1 (operador) — El banco de cinco elementos estructurantes no mejora la fusión de manera uniforme: desplaza su punto de operación hacia el realce de la actividad espacial, en contra de la fidelidad a las fuentes.
H2 (criterio) — El orden de mérito de los métodos no es una propiedad del operador, sino del criterio con que se lo evalúa.
H3 (criterio) — La batería de nueve métricas de tipo «mayor es mejor» es insuficiente como criterio de calidad, porque sus métricas de actividad crecen monótonamente con la varianza inyectada.
H4 (criterio) — La batería contiene al menos una métrica que no aporta información independiente de las demás.
H5 (criterio) — La optimización no determina la configuración adoptada: ambos hiperparámetros son decisiones apoyadas en parte del mismo criterio con el que después se evalúa.
H6 (criterio) — El orden de mérito de las métricas de imagen no predice el orden de utilidad en una tarea posterior, y ninguna fusión supera por un margen distinguible a la mejor modalidad individual.
H7 (operador) — Con el radio y el peso igualados, el banco de cinco elementos produce un perfil distinto del disco único.
```
**Línea de pie (nueva):**
```
H1 se contrasta en §5.4 y §5.6; H6 en §5.5; H2, H3, H4, H5 y H7 en §5.8. Las siete, con experimentos corridos y versionados.
```

**Footer:** `5 / 19` → `6 / 22`

**NOTAS, ANTES:** `Tres hipótesis: H1 sobre el operador, H2 sobre la optimización, H3 sobre la utilidad en tarea. Adelantar que H3 dará el resultado más matizado y honesto de la tesis.`
**DESPUÉS:**
```
Siete hipótesis en dos familias: dos sobre el operador (H1 y H7) y cinco sobre la validez del criterio (H2 a H6). Advertir que H1 afirma un desplazamiento del punto de operación, no una mejora uniforme, y que sostener H6 equivale a rechazar la hipótesis de que la mejora de calidad se traslade a la detección: es un resultado del trabajo, medido sobre 232 escenas.
```

---

## Diapositiva 7 — La transformada Top-Hat y la fusión clásica
**Título, ANTES:** `3. La transformada Top-Hat y la fusión clásica`
**DESPUÉS:** `4. La transformada Top-Hat y la fusión clásica`
**Footer:** `6 / 19` → `7 / 22`
**Cuerpo y notas: sin cambios** (verificado contra `src/fusion/optimal_top_hat.py` y `comparatives.py`; ninguna cifra ni afirmación de esta diapositiva está objetada).

---

## Diapositiva 8 — El operador
**Título, ANTES:** `4. Propuesta novedosa: banco de SE y suma de ramas`
**DESPUÉS:** `5. El operador: banco de SE y suma de ramas`

**Shape `Text 2`, ANTES (5 párrafos):**
```
Una sola escala (sin cascada multiescala).
Promedio de las 4 orientaciones lineales (ec. 7) + respuesta del disco (ec. 8).
Novedad: suma de la rama lineal y la del disco (en lugar del máximo).
Máximo entre fuentes (ec. 10) y reconstrucción ponderada con m (ec. 11).
Esquema de Bala et al. (2024), trasladado del realce de fondo de ojo a la fusión VIS/IR.
```
**DESPUÉS (5 párrafos):**
```
Una sola escala (sin cascada multiescala).
Promedio de las 4 orientaciones lineales (ec. 7) + respuesta del disco (ec. 8).
Novedad: suma de la rama lineal y la del disco, en lugar del máximo (esquema de Bala et al., 2024, trasladado del realce de fondo de ojo a la fusión VIS/IR).
Máximo entre fuentes (ec. 10) —no entre las ramas del banco— y reconstrucción ponderada con m sobre I_base = (VIS + IR)/2 (ec. 11).
El aporte de la suma se aísla en la ablación con (r, m) igualados: es el mejor de los seis brazos con las nueve métricas y el cuarto con las diecisiete, y casi duplica la tasa de artefactos del disco único (Nabf 0,374 frente a 0,185). Diapositiva 16.
```

**Footer:** `7 / 19` → `8 / 22`

**NOTAS, ANTES:** `El corazón de la tesis, leído sobre el flujograma: cinco elementos estructurantes (un disco + cuatro líneas de largo 2r+1) por fuente; las respuestas lineales se promedian y se SUMAN a la del disco — la suma acumula evidencia de ambas geometrías, el máximo solo elige una. Entre fuentes sí se toma el máximo, y la reconstrucción pondera con m. El PSO (caja punteada) calibra r y m.`
**DESPUÉS:**
```
El corazón del primer aporte, leído sobre el flujograma: cinco elementos estructurantes (un disco y cuatro líneas de largo 2r+1) por fuente; las respuestas lineales se promedian y se SUMAN a la del disco — la suma acumula evidencia de ambas geometrías, el máximo solo elige una. Entre fuentes sí se toma el máximo, y la reconstrucción pondera con m. No decir que el PSO calibra r y m: el alcance real de la optimización es la diapositiva siguiente.
```

**IMAGEN A REGENERAR — `ppt/media/image-7-1.png`** (recuadro punteado del flujograma):
ANTES: `PSO ajusta (r, m): barrido 5×5 → r = 25;  m = 0,0703`
DESPUÉS: `Barrido PSO 5×5 → m* = 0,30 (piso del rango publicado);  r = 25 fijado por diseño`

---

## Diapositiva 9 — Alcance real de la optimización
**Título, ANTES:** `5. Optimización por enjambre de partículas (PSO)`
**DESPUÉS:** `6. Alcance real de la optimización por PSO (OE2 / H5)`

**Shape `Text 2`: sin cambios** (`Se optimizan dos hiperparámetros…` / `Aptitud publicada de Ortega y Espinoza (2025), sin pesos arbitrarios:`).

**Shape `Text 3`, ANTES (2 párrafos):**
```
Barrido de 25 configuraciones del enjambre: partículas 2–10 × iteraciones 10–50 (réplica de Ortega y Espinoza, 2025).
Las 25 configuraciones convergen al mismo peso: m* = 0,30, el piso del rango publicado [0,30–2,00]. El radio se fija en r = 25, que maximiza las nueve métricas de evaluación.
```
**DESPUÉS (4 párrafos):**
```
Barrido de 25 configuraciones del enjambre: partículas 2–10 × iteraciones 10–50 (réplica de Ortega y Espinoza, 2025). La aptitud se evalúa sobre 3 de las 20 escenas, que también integran el conjunto de evaluación: no hay partición separada para el ajuste.
El peso queda en m = 0,30 en las 25 configuraciones porque es el piso del rango publicado [0,30–2,00] y F_o decrece estrictamente en m dentro de ese rango. Es saturación en el borde, no convergencia a un óptimo interior.
El radio, en cambio, no converge: la búsqueda devuelve r = 1 en 16 de las 25 (F_o = 1,7350) y r = 25 en 8 (1,7057). El argmax de la aptitud es r = 1. El r = 25 evaluado proviene de la batería de evaluación, que lo prefiere: maximiza el bloque de actividad (EN, SD, FE, MG, SF) en las 20 imágenes, a costa de las cuatro métricas de fidelidad. Se declara la circularidad parcial y se acota con el ajuste simétrico de los comparativos.
El peso sí admite justificación independiente de la aptitud: con m = 0,30 el recorte satura el 0,73 % de los píxeles en promedio y no supera el 1,56 % en ninguna escena; con m = 1 asciende al 6,50 % en promedio y al 16,14 % en el peor caso. Criterio físico, no métrico.
```
*Maquetación: bajar `Text 3` a 11 pt y extender su altura hasta y ≈ 4,95 in reduciendo el mapa de calor a 3.200.000 EMU de alto.*

**Shape `Text 4` (pie del mapa de calor), ANTES:**
```
ω: 0,9 → 0,4 · c₁ = c₂ = 1,5 · r ∈ [1, 25] · m ∈ [0,30; 2,00] (rango publicado)
```
**DESPUÉS (2 párrafos):**
```
ω: 0,9 → 0,4 · c₁ = c₂ = 1,5 · r ∈ [1, 25] · m ∈ [0,30; 2,00] (rango publicado)
En la propia aptitud, no aplicar el operador puntúa mejor que aplicarlo: la base (VIS + IR)/2 obtiene F_o = 1,7583, por encima de 1,7350 y de 1,7057.
```

**Footer:** `8 / 19` → `9 / 22`

**NOTAS, ANTES:** `r controla la escala de las estructuras que se extraen; m cuánto realce se reinyecta. La aptitud publicada F_o combina fidelidad estructural (SSIM), información (entropía) y baja distorsión (PSNR). El barrido replica el Cuadro 1 de la FPUNA: el óptimo global de F_o para este operador es r=25 con m pequeño (≈0,07), que extrae estructuras grandes pero las pondera suavemente.`
**DESPUÉS:**
```
r controla la escala de las estructuras extraídas; m cuánto realce se reinyecta. La aptitud publicada F_o combina fidelidad estructural (SSIM), información (entropía) y baja distorsión (PSNR): dos de sus tres sumandos están del lado de la fidelidad, y de ahí que decrezca en m. Conclusión de H5: ninguno de los dos hiperparámetros de la configuración evaluada es un óptimo interior de la búsqueda — uno contradice su argmax y el otro es el borde del rango. Decirlo antes de que lo pregunte la mesa, y cerrar con la justificación por rango dinámico, que es sólida e independiente de la aptitud.
```

**IMAGEN A REGENERAR — `ppt/media/image-8-2.png`** (título del mapa de calor):
ANTES: `Barrido PSO (rango publicado): todas convergen a m* = 0,30`
DESPUÉS (dos líneas):
```
Barrido PSO (rango publicado): m* = 0,30 en las 25 configuraciones — piso del rango
F_o = 1,7350 corresponde a r = 1 (16 casos); 1,7057 a r = 25 (8 casos); 1,6990 a r = 14 (1)
```

---

## Diapositiva 10 — Diseño experimental
**Título, ANTES:** `6. Diseño experimental`
**DESPUÉS:** `7. Diseño experimental`

*Rediseño a tres columnas de ≈2.700.000 EMU de ancho cada una (x = 457200 / 3200400 / 5943600), y = 1.188.720 a 4.480.560, cuerpo a 11 pt, más una línea de pie a todo el ancho en y ≈ 4.570.000.*

**Columna A — encabezado:** `Benchmark de calidad` *(igual que ahora)*
**Columna A — cuerpo, ANTES:**
```
20 pares VIS/IR del dataset TNO (Toet, 2014).
7 métodos: LP, RP, DWT, DTCWT, CVT, Top-Hat clásico y Propuesta → 140 fusiones.
Nueve métricas sin referencia (EN, SD, FE, MG, MI_vis, MI_ir, SF, SSIM, PSNR).
Friedman global + Wilcoxon pareado con corrección de Holm (α = 0,05).
```
**DESPUÉS:**
```
20 pares VIS/IR del TNO (Toet, 2014), correspondientes a 13 escenas físicamente distintas.
7 métodos: LP, RP, DWT, DTCWT, CVT*, Top-Hat clásico y Propuesta → 140 fusiones.
Nueve métricas sin imagen de referencia (EN, SD, FE, MG, MI_vis, MI_ir, SF, SSIM, PSNR). SSIM y PSNR se calculan contra las fuentes.
Friedman global + Wilcoxon pareado con corrección de Holm (α = 0,05).
```

**Columna B — encabezado (NUEVO):** `Controles de la auditoría`
**Columna B — cuerpo (NUEVO):**
```
Control negativo: siete entradas degradadas añadidas al ranking —imagen base sin operador, cuatro fusiones de ruido gaussiano (σ = 0,02 / 0,05 / 0,10 / 0,20) y dos desenfoques (5×5 y 11×11)— → 14 entradas.
Ablación del banco con (r, m) = (25; 0,30) fijos en seis brazos que solo difieren en cómo se combinan las respuestas morfológicas.
Ajuste simétrico: el mismo tipo de barrido de hiperparámetros concedido a los cinco comparativos y al Top-Hat clásico.
Sensibilidad del criterio: el mismo ranking recalculado con las diecisiete métricas que el evaluador ya computa (nueve + Qabf, Nabf, SCD, VIF, FMI, Q0, QW, QE).
```

**Columna C — encabezado, ANTES:** `Evaluación orientada a tarea`
**DESPUÉS:** `Evaluación en tarea (dos experimentos)`
**Columna C — cuerpo, ANTES:**
```
Dataset etiquetado LLVIP (peatones nocturnos): 2.000 imágenes de entrenamiento y 500 de validación.
YOLOv8n reentrenado por modalidad (40 épocas), 9 entradas: VIS, IR y las 7 fusiones.
Etiquetas idénticas entre modalidades: la diferencia de mAP aísla el efecto del método de fusión.
```
**DESPUÉS:**
```
LLVIP (peatones nocturnos): 2.000 imágenes de entrenamiento y 500 de validación. YOLOv8n reentrenado por modalidad (40 épocas), 9 entradas: VIS, IR y las 7 fusiones.
Etiquetas idénticas entre modalidades: la diferencia de mAP atribuye el efecto al método de fusión.
M3FD (clases de visibilidad opuesta: personas/IR y luces/VIS): detector único VIS+IR y conteo por escena sobre 232 escenas que contienen ambas clases, de las cuales 90 son críticas.
```

**Línea de pie (NUEVA, a todo el ancho):**
```
(*) CVT es una aproximación de tipo curvelet implementada con wavelet 2D db4, no la transformada curvelet: los cinco comparativos cubren cuatro familias. Limitaciones declaradas: los contrastes pareados asumen bloques independientes y las conclusiones se verificaron agregando por escena; LLVIP no tiene partición de prueba separada de la de selección (se reporta el checkpoint final); los experimentos de detección usan una sola semilla, por lo que diferencias de milésimas entre métodos no son distinguibles.
```

**Footer:** `9 / 19` → `10 / 22`

**NOTAS, ANTES:** `Dos evaluaciones complementarias: calidad de imagen (TNO, sin referencia) y utilidad en tarea (LLVIP, con verdad de campo). En LLVIP solo cambian los píxeles de entrada; las etiquetas son las mismas, así el mAP aísla el efecto de la fusión.`
**DESPUÉS:**
```
Tres bloques, no dos: el benchmark de calidad, los cuatro controles de la auditoría y los dos experimentos de detección. En LLVIP solo cambian los píxeles de entrada; las etiquetas son las mismas. Declarar de entrada las limitaciones del pie —13 escenas, CVT como db4, ausencia de partición de prueba y una sola semilla— porque son las primeras cuatro preguntas previsibles de la mesa.
```

---

## Diapositiva 11 — Resultados cualitativos
**Título, ANTES:** `7. Resultados cualitativos`
**DESPUÉS:** `8. Resultados cualitativos`

**Shape `Text 2`, ANTES:**
```
Los 20 montajes por escena están disponibles en el repositorio (docs/figures/cualitativas/).
```
**DESPUÉS:**
```
Los 20 montajes —uno por par, correspondientes a 13 escenas distintas— están en el repositorio (docs/figures/cualitativas/). Obsérvese el patrón consistente con el análisis cuantitativo: más realce de bordes y textura que los multiescala, con pérdida visible de fidelidad radiométrica y más artefactos que el disco único.
```

**Footer:** `10 / 19` → `11 / 22`

**NOTAS, ANTES:** `Escena representativa: la propuesta (recuadro rojo) integra la firma térmica de las personas con la textura de la casa y la vegetación, con menos halos y ruido que RP/DWT y más contraste local que el clásico.`
**DESPUÉS:**
```
Escena representativa: la propuesta (recuadro rojo) integra la firma térmica de las personas con la textura de la casa y la vegetación, y muestra más contraste local que el Top-Hat clásico. No afirmar «menos halos y ruido que RP/DWT»: medido con Nabf, la propuesta (0,374) tiene más artefactos que RP (0,224) y que DWT (0,241). Indicar qué mirar: el realce direccional y, a la vez, el corrimiento radiométrico respecto de las fuentes.
```

---

## Diapositiva 12 — Resultados cuantitativos
**Título, ANTES:** `Resultados cuantitativos — medias sobre 20 pares`
**DESPUÉS:** `Resultados cuantitativos por bloques — medias sobre 20 pares`

**Línea nueva sobre la tabla (cuadro de texto en y ≈ 800.000):**
```
Bloque de ACTIVIDAD ESPACIAL (EN, SD, FE, MG, SF)   |   Bloque de FIDELIDAD A LAS FUENTES (MI_vis, MI_ir, SSIM, PSNR)
```
*Sombrear las cinco cabeceras de actividad en un tono y las cuatro de fidelidad en otro.*

**Tabla `Table 0` — reemplazo completo (6 → 10 columnas, 8 filas), ANTES:**
```
Método | EN ↑ | FE ↑ | SD ↑ | SF ↑ | SSIM ↑
Pirámide de Laplace (LP)          | 6,835 | 1,079 | 0,155 | 13,04 | 0,721
Ratio Pyramid (RP)                | 6,829 | 1,079 | 0,130 | 13,34 | 0,721
Wavelet discreta (DWT)            | 6,700 | 1,059 | 0,120 | 13,93 | 0,716
DTCWT                             | 6,706 | 1,060 | 0,121 | 13,03 | 0,739
Curvelet (CVT)                    | 6,665 | 1,053 | 0,117 | 13,15 | 0,731
Top-Hat clásico                   | 6,933 | 1,096 | 0,139 | 22,86 | 0,578
Propuesta Novedosa (r=25; m=0,30) | 6,989 | 1,105 | 0,148 | 17,34 | 0,668
```
**DESPUÉS (todas las celdas desde `descriptive_means.csv`):**
```
Método | EN ↑ | SD ↑ | FE ↑ | MG ↑ | SF ↑ | MI_vis ↑ | MI_ir ↑ | SSIM ↑ | PSNR ↑
Pirámide de Laplace (LP)          | 6,840 | 0,155 | 1,081 | 0,0252 | 13,22 | 1,924 | 0,918 | 0,706 | 14,94
Ratio Pyramid (RP)                | 6,810 | 0,127 | 1,077 | 0,0275 | 13,62 | 0,949 | 0,650 | 0,705 | 17,37
Wavelet discreta (DWT)            | 6,682 | 0,117 | 1,057 | 0,0275 | 14,19 | 1,076 | 0,666 | 0,701 | 17,59
DTCWT                             | 6,688 | 0,117 | 1,058 | 0,0255 | 13,20 | 1,078 | 0,673 | 0,725 | 17,60
CVT (aprox. wavelet db4)          | 6,645 | 0,113 | 1,051 | 0,0260 | 13,34 | 1,096 | 0,670 | 0,716 | 17,65
Top-Hat clásico (r=5; m=1)        | 6,922 | 0,135 | 1,095 | 0,0478 | 23,10 | 0,787 | 0,493 | 0,564 | 16,87
Propuesta Novedosa (r=25; m=0,30) | 6,986 | 0,144 | 1,105 | 0,0355 | 17,44 | 0,897 | 0,600 | 0,658 | 16,84
```
*Negritas por columna: EN 6,986 (Propuesta) · SD 0,155 (LP) · FE 1,105 (Propuesta) · MG 0,0478 (Top-Hat) · SF 23,10 (Top-Hat) · MI_vis 1,924 (LP) · MI_ir 0,918 (LP) · SSIM 0,725 (DTCWT) · PSNR 17,65 (CVT). Cuerpo de tabla a 10 pt.*

**Shape `Text 2` (prosa de cierre), ANTES (2 párrafos):**
```
La propuesta lidera la entropía (6,989) y el contenido de bordes (1,105) del estudio, con ventaja significativa frente a los cinco métodos del estado del arte en EN, FE, MG y SF; queda segunda en contraste (SD), gradiente y frecuencia espacial.
Cede en las métricas de fidelidad a las fuentes (SSIM 0,668; PSNR) y en información mutua, lideradas por los métodos multiescala. Ranking agregado: 2º de 7 (3,67).
```
**DESPUÉS (2 párrafos):**
```
La propuesta lidera la entropía (6,986) y con ella la eficiencia de fusión (1,105), que es esa misma entropía reescalada por una constante por escena y no una dimensión independiente; queda segunda en contraste (0,144), gradiente medio (0,0355) y frecuencia espacial (17,44), detrás del Top-Hat clásico en las dos últimas. Cede las cuatro métricas de fidelidad, lideradas por los multiescala: MI_vis y MI_ir por la pirámide de Laplace, SSIM por DTCWT y PSNR por la aproximación CVT.
No hay dominancia global: hay un punto de operación desplazado. En el ranking de rangos medios intra-bloque de las nueve métricas la propuesta es 1.ª de 7 (3,394), por delante de la pirámide de Laplace (3,911) y del Top-Hat clásico (3,944) — bajo este criterio.
```

**Footer:** `11 / 19` → `12 / 22`

**NOTAS, ANTES:** `Negritas = mejor por columna. No hay método universalmente dominante: la propuesta lidera SSIM, LP el contraste (SD) y la información mutua, el Top-Hat clásico la actividad (SF). El perfil de la propuesta es la fidelidad estructural.`
**DESPUÉS:**
```
Negritas = mejor por columna. La nota anterior era falsa y hay que corregirla en voz alta si se la recuerda: la propuesta NO lidera SSIM —es la penúltima, 0,658, solo por encima del Top-Hat clásico— y su perfil NO es la fidelidad estructural, sino la actividad espacial. Lo que la tabla muestra es la asimetría de los dos bloques: gana el de actividad y cede el de fidelidad. Y advertir que EN y FE son la misma cantidad, dato que se demuestra en la auditoría.
```

---

## Diapositiva 13 — Análisis estadístico
**Título, ANTES:** `Análisis estadístico`
**DESPUÉS:** `Análisis estadístico: el punto de operación se desplaza (H1)`

**Shape `Text 2`, ANTES (7 párrafos):**
```
Friedman: diferencias significativas en las nueve métricas (p < 0,001).
Wilcoxon pareado (corrección de Holm), Propuesta vs. los 5 métodos del estado del arte:
  EN, FE, MG y SF: mejor y significativa frente a los 5 rivales.
  SD (contraste): mejor y significativa frente a 4 de los 5.
  Cede en fidelidad a las fuentes (SSIM, PSNR) e información mutua: lideran los multiescala.
Frente al Top-Hat clásico gana en 6 de las 9 métricas —entropía, contraste, bordes, ambas informaciones mutuas y SSIM (0,668 vs 0,578)— con significancia estadística.
Ranking global (9 métricas): LP 3,44 · Propuesta 3,67 · DTCWT 4,00 · TH clásico 4,00 · RP 4,11 · CVT 4,33 · DWT 4,44 — la propuesta queda segunda, a 0,23 del líder.
```
**DESPUÉS (7 párrafos):**
```
Friedman: diferencias significativas en las nueve métricas (p < 0,001).
Wilcoxon pareado con corrección de Holm, propuesta frente a las cinco configuraciones de referencia, leído por bloques:
  Bloque de ACTIVIDAD ESPACIAL (EN, SD, FE, MG, SF): 24 de 25 contrastes favorables y significativos, y NINGUNO adverso. El único que no se sostiene es SD frente a la pirámide de Laplace (p_holm = 0,231).
  Bloque de FIDELIDAD A LAS FUENTES (MI_vis, MI_ir, SSIM, PSNR): 17 de 20 adversos y significativos, uno solo favorable y dos no significativos.
  Esa asimetría es H1: el operador no mejora de manera uniforme, desplaza el punto de operación.
Frente al Top-Hat clásico gana en 6 de las 9 métricas —entropía (6,986 vs 6,922), contraste (0,144 vs 0,135), eficiencia de fusión, ambas informaciones mutuas y SSIM (0,658 vs 0,564)— con p_holm ≤ 0,0002; PIERDE con significancia en gradiente medio (0,0355 vs 0,0478) y frecuencia espacial (17,44 vs 23,10), ambas con p_holm = 0,000021 y tamaño de efecto máximo; y empata en PSNR (p_holm = 0,674). Como FE es la entropía reescalada, las dimensiones independientes ganadas son cinco de ocho.
Ranking de rangos medios intra-bloque, nueve métricas: Propuesta 3,394 · LP 3,911 · TH clásico 3,944 · RP 3,983 · DTCWT 4,111 · DWT 4,211 · CVT 4,444 — la propuesta encabeza el benchmark, a 0,517 de la segunda.
```

**Footer:** `12 / 19` → `13 / 22`

**NOTAS, ANTES:** `La evidencia estadística sostiene las ventajas donde la propuesta las reclama: limpieza y estructura, con significancia tras corregir por comparaciones múltiples. El ranking global es honesto: la propuesta no domina todo; domina su perfil.`
**DESPUÉS:**
```
El recuento por bloques es más fuerte que el recuento por métrica y es el que sostiene H1: 24 de 25 a favor en actividad, 17 de 20 en contra en fidelidad. Nombrar las dos derrotas contra el Top-Hat clásico antes de que las nombre la mesa: el clásico realza más (MG y SF), la propuesta preserva más estructura (SSIM, MI). El ranking se calcula promediando los rangos intra-bloque —el compañero habitual de Friedman—, no rankeando los promedios; poder explicarlo si lo preguntan.
```

---

## Diapositiva 14 — NUEVA: Auditoría I (H3, H4)
**Título:** `9. Auditoría I — ¿discrimina calidad la batería de nueve métricas? (H3, H4)`
**Footer:** `14 / 22`

**Bloque 1 — encabezado:** `Control negativo con degradaciones conocidas`
**Bloque 1 — cuerpo:**
```
Se añadieron al ranking siete entradas degradadas junto a los siete métodos: la imagen base sin operador, cuatro fusiones artificiales de ruido gaussiano y dos desenfoques.
Con las nueve métricas, la fusión de ruido con σ = 0,20 queda 3.ª de 14 (rango 6,767), por delante de cinco de los seis métodos comparativos y de la imagen base. Evaluada como octava entrada frente a los siete métodos, queda 2.ª de 8 con σ ≥ 0,10, por delante de los seis comparativos.
Y su rango MEJORA al aumentar el ruido: 8,917 → 7,850 → 6,972 → 6,767 para σ = 0,02 / 0,05 / 0,10 / 0,20. La batería juzga mejor a la imagen cuanto más ruido se le inyecta.
El fallo es específico de la varianza, no de la degradación en general: el desenfoque sí se penaliza y el de 11×11 queda último (9,822).
Y basta una métrica que penalice artefactos para corregirlo: incorporando Nabf el ruido cae al 7.º puesto; con las diecisiete métricas, al último (10,138).
```

**Bloque 2 — encabezado:** `Redundancia interna de la batería`
**Bloque 2 — cuerpo:**
```
FE = EN de la fusión / promedio de las EN de las fuentes. El denominador no depende del método, de modo que dentro de cada par FE es EN reescalada: rangos intra-bloque idénticos en las 20 imágenes y el mismo χ² de Friedman (88,2857). Las dimensiones efectivas son ocho, no nueve.
Excluyendo FE la propuesta sigue primera (3,631 frente a 3,994 de la pirámide de Laplace): la redundancia no explica su primer lugar.
```

**NOTAS:**
```
Es el resultado más contundente del segundo aporte y hay que presentarlo antes de que la mesa lo encuentre en el repositorio. El mensaje no es que la propuesta sea ruido, sino que la batería mide actividad espacial y no calidad de fusión: nueve métricas todas «mayor es mejor», ninguna que penalice artefactos. La receta que se deriva es la misma para los dos hallazgos: declarar la redundancia y añadir una métrica de dirección inversa. Ambos experimentos están versionados en run_control_negativo.py.
```

---

## Diapositiva 15 — NUEVA: Auditoría II (H2)
**Título:** `Auditoría II — el orden de mérito es propiedad del criterio (H2)`
**Footer:** `15 / 22`

**Bloque 1 — encabezado:** `Mismo operador, mismas 140 imágenes, dos composiciones del criterio`
**Bloque 1 — cuerpo:**
```
Con las nueve métricas del trabajo de referencia: la propuesta es 1.ª de 7 (3,394).
Con las diecisiete que el MISMO evaluador ya calcula (nueve + Qabf, Nabf, SCD, VIF, FMI, Q0, QW, QE): desciende a 3.ª (3,459); el primer lugar pasa a la pirámide de Laplace (3,147), el segundo a DTCWT (3,259) y el Top-Hat clásico cae al último (5,000).
No cambié ninguna imagen fusionada. Cambié el conjunto de métricas. Todo orden agregado debe reportarse junto a la composición que lo produce.
```

**Bloque 2 — encabezado:** `Ajuste simétrico de los comparativos`
**Bloque 2 — cuerpo:**
```
El protocolo concede a la propuesta un paso de ajuste que no concede a los comparativos. Dándoselo también a ellos, ninguna de las cinco configuraciones de referencia la alcanza: RP 3,772 · LP 4,028 · DWT 4,167 · DTCWT 4,211 · CVT 4,717, frente a 3,583.
El Top-Hat clásico la supera por 0,061 (3,522) — pero con m = 1, más del triple del peso. A peso igualado (r = 25; m = 0,30 en ambos) la propuesta gana por 0,683: 3,467 frente a 4,150.
Con las diecisiete métricas y los comparativos ajustados la propuesta queda 3.ª (3,821), detrás de la pirámide de Laplace (3,141) y de DTCWT (3,362): la ventaja no es robusta a la composición del conjunto de métricas.
El primer lugar es un resultado sólido DENTRO del criterio del trabajo de referencia, no una propiedad independiente del criterio.
```

**NOTAS:**
```
Estas dos mitades responden por adelantado a las dos objeciones más previsibles: «usted eligió las métricas que le convienen» y «usted ajustó sus hiperparámetros y dejó a los comparativos por defecto». Las dos están corridas y versionadas (run_ajuste_comparativos.py). El matiz que salva el resultado principal es el peso: el clásico ajustado conserva m = 1; a peso igualado la propuesta gana con holgura. Si alguien cita el libro diciendo que en el escenario de diecisiete con comparativos ajustados la propuesta cae al quinto lugar, es una errata del libro: la columna del CSV la deja tercera con 3,821.
```

---

## Diapositiva 16 — NUEVA: Auditoría III (H7)
**Título:** `Auditoría III — ¿cuánto aporta el banco? Ablación con (r, m) igualados (H7)`
**Footer:** `16 / 22`

**Cuerpo:**
```
La comparación con el Top-Hat clásico no aísla el banco: aquel usa r = 5 y m = 1, de modo que la diferencia observada mezcla banco, radio y peso. Para aislarlo se fijaron r = 25 y m = 0,30 en seis brazos que comparten todo salvo la forma de combinar las respuestas morfológicas.
Con las nueve métricas la suma de ramas —la que adopta la propuesta— es la mejor de los seis (3,222), por delante del máximo (3,311) y del disco único (3,367); el promedio queda en 3,533 y las líneas solas y la imagen base empatan últimas (3,783).
Lectura prudente: al retirar FE —que duplica la entropía, justo donde la suma obtiene su mayor ventaja— los seis brazos se comprimen en una banda de 3,444 a 3,631 y la suma baja al 4.º lugar (3,500).
Con las diecisiete métricas el orden se invierte: máximo 2,932 · disco 3,153 · promedio 3,179 · suma 3,621 · líneas 3,756 · base 4,359.
La suma casi duplica la tasa de artefactos del disco único (Nabf 0,374 frente a 0,185): la novedad desplaza el punto de operación hacia el realce, no lo mejora de forma uniforme.
Lo que queda firme en TODAS las composiciones: la imagen base sin operador es la peor de los seis brazos con las diecisiete métricas (4,359). El mérito no proviene de la base. Pero la dirección del aporte depende del criterio — exactamente como enuncia H2.
```

**NOTAS:**
```
Es la respuesta a la pregunta «¿cuánto aporta el banco de cinco elementos, en sí?». Tener el experimento corrido y no mostrarlo sería desperdiciarlo: la lectura honesta —incluida la caída al cuarto lugar al retirar FE— es más defendible que la ausencia. Y conviene decir aquí que r = 1 no desactiva el banco: los cinco elementos siguen activos en una vecindad de 3×3.
```

---

## Diapositiva 17 — Detección en LLVIP
**Título, ANTES:** `8. Detección en LLVIP — mAP@0,5`
**DESPUÉS:** `10. Contraste externo I — detección en LLVIP (H6)`

**Shape `Text 2`, ANTES (3 párrafos):**
```
Toda fusión supera con claridad al visible solo (+0,11 a +0,14 en mAP@0,5); el IR solo lidera (0,957): en peatones nocturnos domina la firma térmica.
La Propuesta Novedosa queda en el extremo inferior de la banda de fusiones (0,913): el realce que premian las métricas de actividad no ayuda al detector.
La calidad de imagen no se traslada automáticamente al mAP (H3 parcial).
```
**DESPUÉS (3 párrafos):**
```
Toda fusión supera al visible solo (de 0,813 a una banda de 0,906–0,952, es decir entre +0,09 y +0,14 en mAP@0,5), pero ninguna alcanza al infrarrojo solo, que lidera con 0,971: en peatones nocturnos domina la firma térmica.
La Propuesta Novedosa queda en el extremo inferior de la banda de fusiones (0,906, a la par de la Ratio Pyramid, 0,906) y a 0,065 del infrarrojo: el realce que premian las métricas de actividad no ayuda al detector — en este caso lo perjudica.
Correlación de Spearman entre el rango de calidad de los siete métodos y su mAP@0,5: ρ = +0,214 con p = 0,645. No hay asociación, y el signo es el CONTRARIO al esperado, puesto que un rango menor indica mejor calidad. Se sostiene H6.
```

**Footer:** `13 / 19` → `17 / 22`

**NOTAS, ANTES:** `El hallazgo más matizado: fusionar aporta muchísimo frente al VIS, pero ninguna fusión supera al IR puro en esta tarea nocturna. Entre fusiones, las diferencias son pequeñas: la calidad de imagen no se traslada automáticamente al mAP.`
**DESPUÉS:**
```
Fusionar aporta mucho frente al VIS, pero ninguna fusión supera al IR puro en esta tarea nocturna. El instrumento que convierte esa observación en un resultado es la correlación de Spearman: sin asociación y con el signo contrario al esperado. Optimizar actividad y optimizar desempeño en tarea son objetivos distintos, y un protocolo de evaluación debe reportar ambos. Recordar que se usa el checkpoint final y una sola semilla: los 0,0001 que separan a la propuesta de la Ratio Pyramid no son distinguibles del ruido de entrenamiento.
```

---

## Diapositiva 18 — M3FD (fusión de las viejas 14 y 15)
**Título, ANTES (vieja 14):** `Clases complementarias en M3FD — un detector único VIS+IR`
**DESPUÉS:** `Contraste externo II — M3FD: el conteo por escena (H6)`

**Figura:** conservar `image-14-1.png` (AP@0,5 por clase, ya regenerada con el split vigente). **Mover `image-15-1.png` a la diapositiva de reserva.**

**Shape `Text 2`, ANTES (3 párrafos de la vieja 14):**
```
Complementariedad extrema: el IR domina People (0,220) pero es ciego a Lamp (0,018); el VIS es el espejo (0,178 / 0,135).
Todas las fusiones recuperan ambas clases en una sola imagen; RP alcanza el mejor promedio del par (0,165) y es la única que supera a ambas modalidades (VIS 0,157; IR 0,119).
La propuesta recupera ambas clases con un promedio intermedio (0,124): detecta seis personas donde cada modalidad detecta dos, pero el realce elevado no maximiza el mAP.
```
**Y el pie de la vieja 15:**
```
Arriba: la fusión detecta 6 personas frente a 2 del VIS y 2 del IR. Abajo: el IR no ve ninguna luz — la fusión conserva las 4.
```
**DESPUÉS (4 párrafos, un solo cuadro):**
```
Complementariedad real pero asimétrica: el infrarrojo domina en personas (AP@0,5 = 0,779 frente a 0,621 del visible) y se degrada en luces (0,348), mientras el visible sostiene ambas clases en un nivel parejo (0,621 y 0,616). No hay patrón espejo: ninguna modalidad es ciega, y el argumento a favor de fusionar es que ninguna es la mejor en las dos clases a la vez.
Promedio del par complementario: la Ratio Pyramid es la única entrada que supera a ambas modalidades (0,622 frente a 0,618 del visible y 0,563 del infrarrojo), por un margen de 0,004. La propuesta alcanza 0,564 —7.ª de las nueve entradas—, por debajo del visible y a la par del infrarrojo; en mAP@0,5 global queda 5.ª de las siete fusiones (0,651 frente a 0,677 de RP).
Conteo por escena, 232 escenas que contienen simultáneamente las dos clases: las fusiones amplían la recuperación conjunta pero no la garantizan. El mejor caso es la pirámide de Laplace (57,8 %); cuatro de las siete fusiones quedan por debajo del visible solo (53,0 %). La propuesta recupera ambas clases en el 50,0 %, con 8 escenas ganadas y 15 perdidas frente al visible (McNemar exacto p = 0,2100) y resuelve 2 de las 90 escenas críticas.
Se sostiene H6, con muestra suficiente: la hipótesis de que la mejora de calidad de imagen se traslade a la tarea queda RECHAZADA, no simplemente sin confirmar.
```

**Footer:** `14 / 22` (viejo `14 / 19`) → `18 / 22`. **Eliminar el footer de la vieja 15 (`15 / 19`).**

**NOTAS (reemplazan las de las viejas 14 y 15), ANTES (14):** `…Las personas solo se ven bien en IR y las luces solo en VIS; la fusión es la única entrada que detecta ambas a la vez. La propuesta es la mejor fusión del estudio en este escenario…`
**DESPUÉS:**
```
Un único YOLOv8n entrenado con VIS+IR mezcladas e inferencia por método, sobre 232 escenas que contienen las dos clases. Corregir dos afirmaciones de la versión anterior: el infrarrojo NO es ciego a las luces (0,348) y la propuesta NO es la mejor fusión del estudio en este escenario. El resultado que sí aporta el experimento es el conteo por escena, que es la operacionalización que pide OE5: la propuesta queda por debajo del visible solo. Si la mesa pide el caso visual, está en la diapositiva de reserva, con sus conteos reales.
```

---

## Diapositiva 19 — Contraste de las siete hipótesis
*Rediseño: reemplazar las nueve cajas actuales por un cuadro único de 8.229.600 EMU con siete párrafos a 12 pt, más una línea de pie.*

**Título, ANTES:** `Contraste de hipótesis`
**DESPUÉS:** `11. Contraste de las siete hipótesis`

**ANTES (contenido de las nueve cajas):**
```
H1 | SOSTENIDA | El banco disco + líneas con suma de ramas supera al Top-Hat clásico en 6 de 9 métricas y al estado del arte en EN, FE, MG y SF, con significancia estadística (Wilcoxon–Holm).
H2 | SOSTENIDA | La configuración hallada por PSO con la metodología de referencia (r = 25; m = 0,30) supera a la parametrización manual del operador clásico (r = 5; m = 1) en seis de las nueve métricas, con significancia estadística.
H3 | PARCIAL   | La fusión supera al visible solo en detección, pero ninguna fusión supera al infrarrojo solo; la mejor calidad de imagen no garantiza el mejor mAP.
```
**DESPUÉS (siete párrafos):**
```
H1 SE SOSTIENE — El operador desplaza el punto de operación y no mejora de forma uniforme: bloque de actividad 24 de 25 contrastes favorables y ninguno adverso; bloque de fidelidad 17 de 20 adversos (Wilcoxon–Holm).
H2 SE SOSTIENE — 1.ª de 7 con las nueve métricas (3,394); 3.ª con las diecisiete (3,459), y el primer lugar pasa a la pirámide de Laplace (3,147). Ninguna imagen fusionada cambió.
H3 SE SOSTIENE — La fusión artificial de ruido gaussiano σ = 0,20 queda 3.ª de 14 y su rango mejora al aumentar σ (8,917 → 6,767). Con Nabf, o con las diecisiete, cae al fondo.
H4 SE SOSTIENE — FE es EN reescalada: rangos idénticos en las 20 imágenes y el mismo χ² de Friedman (88,2857). Ocho dimensiones efectivas, no nueve.
H5 SE SOSTIENE — El argmax de la aptitud es r = 1 (1,7350) y no r = 25 (1,7057): la búsqueda halla r = 1 en 16 de las 25 configuraciones. Y m = 0,30 es el piso del rango publicado.
H6 SE SOSTIENE — ρ de Spearman entre rango de calidad y mAP de LLVIP = +0,214 (p = 0,645), con el signo contrario al esperado. En 232 escenas de M3FD la propuesta recupera ambas clases en el 50,0 % frente al 53,0 % del visible.
H7 SE SOSTIENE — Con (r, m) = (25; 0,30) fijos, la suma de ramas es la mejor de los seis brazos con las nueve métricas (3,222 frente a 3,367 del disco único) y la imagen base queda última con las diecisiete.
```
**Línea de pie (nueva):**
```
Las siete se sostienen. Nótese que sostener H6 equivale a rechazar que la mejora de calidad se traslade a la detección: es un resultado del trabajo, no una limitación.
```

**Footer:** `16 / 19` → `19 / 22`

**NOTAS, ANTES:** `H1 y H2 quedan sostenidas con evidencia estadística. H3 solo parcialmente: es el resultado más honesto del trabajo y anticipa la pregunta natural del tribunal — calidad de imagen y utilidad en tarea son criterios distintos.`
**DESPUÉS:**
```
Las siete hipótesis se sostienen, y cuatro de ellas son hallazgos sobre el criterio, no sobre el operador. No usar la etiqueta «parcial» para H6: con ρ = +0,214, p = 0,645 y 232 escenas, el rechazo de la hipótesis de traslación es limpio y es un aporte. No decir que el PSO halló r = 25: la búsqueda devuelve r = 1, y esa es exactamente H5.
```

---

## Diapositiva 20 — Conclusiones
**Título, ANTES:** `9. Conclusiones`
**DESPUÉS:** `Conclusiones`

**Shape `Text 2`, ANTES (5 párrafos):**
```
Se formuló e implementó de forma reproducible un operador Top-Hat de una sola escala con banco de disco + líneas orientadas y suma de ramas.
El barrido PSO de 25 configuraciones con la aptitud y el rango publicados converge a m* = 0,30 en todas ellas; el radio r = 25 maximiza las nueve métricas de evaluación.
La propuesta lidera la entropía (6,9888) y el contenido de bordes (1,1045) del benchmark y ocupa el segundo lugar del ranking agregado (3,67), tras la pirámide de Laplace (3,44).
Frente a la metodología clásica Top-Hat, el banco de SE y el ajuste automático mejoran seis de las nueve métricas con significancia estadística, incluida la similitud estructural.
Aporte central en detección (M3FD): la fusión detecta en una sola imagen los objetos complementarios —personas (solo en IR) y luces (solo en VIS)— que ninguna modalidad capta por separado; la propuesta es la mejor fusión del estudio.
```
**DESPUÉS (7 párrafos):**
```
1. El operador desplaza el punto de operación de la fusión y no la mejora de manera uniforme: gana en actividad espacial (24 de 25 contrastes favorables, ninguno adverso) y cede en fidelidad a las fuentes (17 de 20 adversos).
2. Bajo el criterio del trabajo de referencia encabeza el benchmark: 1.º de 7 con rango medio 3,394. Concediendo a los comparativos el mismo paso de ajuste, ninguna de las cinco configuraciones de referencia lo alcanza; el Top-Hat clásico lo supera por 0,061, pero con m = 1, y a peso igualado la propuesta gana por 0,683.
3. El banco aporta sobre el disco único con hiperparámetros igualados (3,222 frente a 3,367), y el mérito no proviene de la imagen base, que queda última.
4. Ese orden es propiedad del criterio: con las diecisiete métricas que el mismo evaluador calcula la propuesta es 3.ª (3,459) y el primer lugar pasa a la pirámide de Laplace (3,147). Ninguna imagen fusionada cambió.
5. La batería de nueve métricas no discrimina detalle útil de ruido —una fusión artificial de ruido queda 3.ª de 14 y su rango mejora al aumentar la varianza— y contiene redundancia: FE es EN reescalada, las dimensiones efectivas son ocho.
6. La optimización no determina la configuración evaluada: el argmax de la aptitud es r = 1 y el peso queda en el piso del rango. El peso sí está justificado por un criterio independiente: saturación del 0,73 % frente al 6,50 % que produciría m = 1.
7. El orden de calidad no predice la utilidad en detección (ρ = +0,214; p = 0,645) y ninguna fusión supera a la mejor modalidad individual por un margen distinguible: en LLVIP lidera el infrarrojo (0,971) y en el conteo por escena de M3FD la propuesta queda por debajo del visible (50,0 % frente a 53,0 %, n = 232). Aporte metodológico: un protocolo de evaluación de fusión debe incluir al menos una métrica que penalice artefactos, declarar la redundancia entre sus componentes y separar el ajuste de hiperparámetros del criterio de evaluación.
```
*Maquetación: cuerpo a 11 pt.*

**Footer:** `17 / 19` → `20 / 22`

**NOTAS, ANTES:** `Cinco conclusiones: método formulado, óptimo hallado, perfil de calidad validado, ventaja sobre el clásico demostrada, y la lección sobre calidad vs. tarea.`
**DESPUÉS:**
```
Siete conclusiones: las tres primeras son el primer aporte (dirección del desplazamiento, primer lugar bajo el criterio de referencia y robustez frente al ajuste simétrico) y las cuatro siguientes el segundo (el orden es del criterio, la batería no discrimina ruido, la optimización no determina la configuración, y la calidad no predice la utilidad). Cerrar con el aporte metodológico, que es lo único de esta tesis transferible a cualquier trabajo de fusión.
```

---

## Diapositiva 21 — Recomendaciones y trabajo futuro
**Shape `Text 2`, ANTES (5 párrafos):**
```
Extender la evaluación de detección a otros detectores y al conjunto completo de LLVIP.
Explorar reglas de fusión adaptativas para la rama Black Top-Hat.
Complementar las métricas objetivas con una validación perceptual por observadores.
Evaluar la transferencia a otros dominios (imágenes médicas, aéreas).
Para aplicaciones donde prima la riqueza informativa y el detalle, la propuesta es la opción recomendada; donde prima la fidelidad a las fuentes, los métodos multiescala (DTCWT, CVT) siguen siendo preferibles.
```
**DESPUÉS (2 encabezados + 9 párrafos):**
```
Sobre el protocolo de evaluación (aporte transferible)
Incluir al menos una métrica de dirección inversa que penalice artefactos: con Nabf el control negativo se corrige por completo.
Declarar la redundancia entre las componentes de la batería y reportar el número efectivo de dimensiones, no el nominal.
Separar el ajuste de hiperparámetros del criterio de evaluación, o declarar la circularidad y acotarla con un ajuste simétrico de los comparativos.
Incorporar un control negativo con degradaciones conocidas como requisito mínimo de cualquier benchmark de fusión, y reportar todo orden agregado junto a la composición del conjunto de métricas que lo produce.
Sobre el operador
Extender la evaluación de detección a otros detectores y al conjunto completo de LLVIP, con varias semillas: los experimentos actuales usan una sola.
Explorar reglas de fusión adaptativas para la rama Black Top-Hat, que es donde se concentran los artefactos (Nabf 0,374 frente a 0,185 del disco único).
Complementar las métricas objetivas con una validación perceptual por observadores — el único criterio que el control negativo no puede engañar.
Evaluar la transferencia a otros dominios; los resultados corresponden a escenas de vigilancia nocturna.
Uso recomendado: el operador es recomendable cuando el requisito explícito es maximizar actividad espacial y contraste local, y se acepta el costo en fidelidad y artefactos. Donde prima la fidelidad a las fuentes, la pirámide de Laplace domina la información mutua (1,924 / 0,918) y la tasa de artefactos (Nabf 0,114), DTCWT el SSIM (0,725) y la aproximación CVT el PSNR (17,65). Para alimentar un detector, ninguna fusión de este estudio antes que la mejor modalidad individual.
```
*Maquetación: cuerpo a 11 pt; los dos encabezados en negrita sin viñeta.*

**Footer:** `18 / 19` → `21 / 22`

**NOTAS, ANTES:** `Cerrar con la recomendación práctica: qué método elegir según el criterio operativo. Dejar claro que el pipeline completo es reproducible desde el repositorio.`
**DESPUÉS:**
```
Dos familias de recomendaciones, y la primera es la que trasciende el trabajo: cómo debería evaluarse la fusión VIS/IR. La recomendación de uso ya no dice «la propuesta es la opción recomendada» sin más: la acota al requisito de maximizar actividad y declara el costo. Y añade la advertencia que se desprende de los dos experimentos de detección. Cerrar recordando que el pipeline completo es reproducible desde el repositorio.
```

---

## Diapositiva 22 — Muchas gracias
**Sin cambios de texto.** (Portada y cierre son las dos únicas diapositivas sin número de página, igual que hoy.)

---

## Diapositiva de RESERVA (sin numerar, después de la 22)
**Título:** `Reserva — M3FD: dos escenas de la validación (conf = 0,3)`
**Figura:** `image-15-1.png` (la de la vieja diapositiva 15; ya está regenerada y sus rótulos de panel son correctos).
**Pie:**
```
Arriba (escena 00389): la fusión detecta 11 personas frente a 3 del visible y 10 del infrarrojo, y pierde una lámpara (1 frente a 2 del visible). Abajo (escena 00231): la fusión detecta 7 lámparas frente a 5 del visible y 1 del infrarrojo, y 8 personas frente a 4 del visible y 10 del infrarrojo. La fusión reúne ambas clases en una sola imagen, pero no supera a la mejor modalidad en cada clase por separado; el conteo por escena de la diapositiva 18 muestra con qué frecuencia ocurre.
```

---

# 2. Numeración final «n / N»

Total N = **22** (la reserva no se numera). Reemplazos en el shape `Text 1` de cada diapositiva:

| Nueva | Texto del footer | Reemplaza a |
|---|---|---|
| 1 | (sin footer) | — |
| 2 | `2 / 22` | `2 / 19` |
| 3 | `3 / 22` | `3 / 19` |
| 4 | `4 / 22` | (nuevo) |
| 5 | `5 / 22` | `4 / 19` |
| 6 | `6 / 22` | `5 / 19` |
| 7 | `7 / 22` | `6 / 19` |
| 8 | `8 / 22` | `7 / 19` |
| 9 | `9 / 22` | `8 / 19` |
| 10 | `10 / 22` | `9 / 19` |
| 11 | `11 / 22` | `10 / 19` |
| 12 | `12 / 22` | `11 / 19` |
| 13 | `13 / 22` | `12 / 19` |
| 14 | `14 / 22` | (nuevo) |
| 15 | `15 / 22` | (nuevo) |
| 16 | `16 / 22` | (nuevo) |
| 17 | `17 / 22` | `13 / 19` |
| 18 | `18 / 22` | `14 / 19` (el `15 / 19` se elimina con la fusión) |
| 19 | `19 / 22` | `16 / 19` |
| 20 | `20 / 22` | `17 / 19` |
| 21 | `21 / 22` | `18 / 19` |
| 22 | (sin footer) | — |

---

# 3. Presupuesto de tiempo (≈20 min)

Portada 0:20 · Contenido 0:30 · 3 Problema 1:10 · 4 Dos aportes 1:20 · 5 Objetivos 1:00 · 6 Hipótesis 1:10 · 7 Marco 1:00 · 8 Operador 1:20 · 9 Optimización 1:30 · 10 Diseño 1:10 · 11 Cualitativos 0:40 · 12 Cuantitativos 1:20 · 13 Estadística 1:20 · 14 Auditoría I 1:30 · 15 Auditoría II 1:20 · 16 Auditoría III 1:00 · 17 LLVIP 1:00 · 18 M3FD 1:20 · 19 Hipótesis 1:10 · 20 Conclusiones 1:10 · 21 Recomendaciones 0:50 · 22 Cierre 0:10 → **≈22 min**. Si hay que ajustar a 20 exactos, la única compresión recomendada es fundir las diapositivas 14 y 15 en una sola («Auditoría del criterio: no discrimina ruido y el orden es del criterio»), quedando N = 21; **no** recortar la 16, que es la respuesta a la pregunta más previsible del tribunal.

---

# 4. Imágenes a regenerar (texto embutido, no editable en el pptx)

Solo dos. Todas las demás figuras ya están al día con el corpus vigente y **no deben regenerarse**.

1. `ppt/media/image-7-1.png` (flujograma, diapositiva 8): el recuadro punteado dice `PSO ajusta (r, m): barrido 5×5 → r = 25;  m = 0,0703`. `m = 0,0703` es el peso de una corrida descartada, que solo sobrevive en `all_metrics.csv.bak_m0703`. Texto nuevo indicado en la diapositiva 8.
2. `ppt/media/image-8-2.png` (mapa de calor, diapositiva 9): el título dice `Barrido PSO (rango publicado): todas convergen a m* = 0,30`. Título nuevo de dos líneas indicado en la diapositiva 9. El contenido de la matriz es correcto (16 celdas con 1,7350 = r 1; 8 con 1,7057 = r 25; 1 con 1,6990 = r 14).

---

# 5. Lo que decidí NO cambiar, y por qué

1. **Diapositiva 7 completa (marco Top-Hat).** WTH/BTH, «fusión clásica: un único disco r = 5, máximo entre fuentes y reconstrucción sin ponderación (m = 1)», `F = I_base + WTH_máx − BTH_máx` y «la base I_base es el promedio de las fuentes» son exactos contra `src/fusion/optimal_top_hat.py` y `comparatives.py`. Ningún hallazgo la objeta. Solo cambia el número de sección y el footer.
2. **Las tres primeras viñetas del problema (VIS / IR / fusión a nivel de píxel).** Encuadre correcto y necesario; solo se fusionaron las dos primeras en una línea por espacio.
3. **«Los métodos multiescala … pueden introducir artefactos» — se conserva la afirmación, se retira su uso.** Es una afirmación de la literatura hedgeada con «pueden» que el propio marco teórico del libro sostiene. Lo que se elimina es usarla para conceder ventaja a la morfología, que es donde los datos la contradicen.
4. **Cifras de LLVIP del diseño experimental (2.000 / 500, 40 épocas, 140 fusiones, 9 entradas).** Verificadas en disco; se conservan literalmente y solo se les añaden las limitaciones declaradas.
5. **La etiqueta «sin referencia», resuelta como «sin imagen de referencia» + nota de que SSIM y PSNR se calculan contra las fuentes.** Los hallazgos 35 y 95 se contradicen: uno defiende la etiqueta estándar de la literatura, el otro la considera imprecisa. La redacción adoptada satisface a ambos sin abrir un flanco nuevo.
6. **Las cuatro figuras de datos ya regeneradas** (`image-10-1`, `image-13-1`, `image-14-1`, `image-15-1`) y las tres imágenes de ecuaciones (`image-6-2`, `image-7-2`, `image-7-3`, `image-8-1`). Verificado que `image-13-1` rotula el IR en 0,971 y que `image-15-1` rotula 3/10/11 y 4/5, 10/1, 8/7: el desfase estaba solo en el texto. Regenerarlas sería trabajo perdido y arriesgaría introducir errores.
7. **Diapositiva 22 (cierre) y la URL del repositorio.** Sin cambios.
8. **NO se proyecta el «p = 0,00005 con 20.000 réplicas de permutación»** que `Reencuadre_Final.md` §5, conclusión 2, atribuye a la separación del primer lugar. No existe ningún CSV ni script de permutación en `experiments/results/metrics_reports/` (verificado por listado completo y por búsqueda de «permut» en todo `experiments/`). El deck se defiende contra el repositorio: no se proyecta una cifra que la mesa no pueda encontrar. Si se versiona el script, se puede añadir a la diapositiva 15.
9. **Se descarta el «18 de las 25 configuraciones» del hallazgo 42.** `pso_grid_search_fo_propuesta.csv` da exactamente r = 1 en 16, r = 25 en 8 y r = 14 en 1, y el propio mapa de calor de la diapositiva muestra 16 celdas resaltadas. El deck dice **16**.
10. **Se descarta el «rango interno 6,589 para r = 1» del hallazgo 69.** `ajuste_comparativos_mejores.csv` contiene una sola fila para la propuesta (r = 25, rango 4,867); el valor de contraste no está versionado. Se sustituye por la afirmación verificada: r = 25 maximiza el bloque de actividad en las 20 imágenes y cede las cuatro de fidelidad frente a r = 1.
11. **No se copia el «desciende al quinto lugar (3,821)» del libro (p. 60).** `ajuste_comparativos_ranking.csv`, columna D, deja a la propuesta **tercera** con 3,821 (LP 3,141 · DTCWT 3,362 · Propuesta 3,821 · RP 3,924 · TopHat 4,541 · DWT 4,574 · CVT 4,638). Es una errata del libro; el deck usa «3.ª» y las notas de la diapositiva 15 lo advierten para que el candidato pueda responder si la mesa cita el libro.
12. **No se conserva la vieja diapositiva 15 como diapositiva de exposición.** Titular «La prueba visual» y ofrecer dos escenas como demostración es el razonamiento anecdótico que el segundo aporte desmonta; pero la figura es valiosa para responder preguntas, así que pasa a reserva con sus conteos reales en lugar de eliminarse.
13. **No se reemplaza «Ranking agregado» por «no hay ranking».** El primer lugar con 3,394 es un resultado real y verificado; lo que se corrige es la cifra (era 3,67, de la corrida anterior y calculada rankeando promedios) y lo que se añade es su condición: es propiedad del criterio.