# Plan de reescritura del libro, párrafo por párrafo

Lo produce `experiments/plan_reescritura_libro.py` desde el propio `.docx` y desde
`AUDITORIA_LIBRO.md`. El detalle completo de las mediciones está en
`experiments/results/metrics_reports/estilo_por_parrafo.csv`, una fila por párrafo del cuerpo.

**Dos cosas distintas que arreglar, y conviene no mezclarlas.** Lo que el libro *dice* mal
—las afirmaciones que no coinciden con los datos— y *cómo* está escrito. La primera es
corrección; la segunda es reescritura. Un párrafo que aparece en las dos listas conviene
reescribirlo entero de una sola vez.

## 1. Lo que dice mal: 38 párrafos con hallazgo confirmado

Ordenados por gravedad. La columna «carga» dice si además hay que reescribir el estilo:
rayas y oraciones de más de 40 palabras.

| Párrafo | Zona | Gravedad | Qué falla | Dónde | Carga de estilo |
|---:|:---|:---|:---|:---|:---|
| 276 | cuerpo | alta | CONTRADICE | Tabla 2 | 0 rayas, 5 largas |
| 377 | cuerpo | alta | CONTRADICE | §5.5 | 6 rayas, 3 largas |
| 338 | cuerpo | alta | CONTRADICE | §4.3 | 2 rayas, 2 largas |
| 419 | cuerpo | alta | SIN FUENTE | §5.8.5 | 2 rayas, 1 larga |
| 516 | apendice | alta | CONTRADICE | apéndice D | 2 rayas, 1 larga |
| 518 | apendice | alta | CONTRADICE · SIN FUENTE | apéndice E | 2 rayas, 1 larga |
| 329 | cuerpo | alta | INCOHERENCIA | §3.15 | — |
| 515 | apendice | alta | CONTRADICE | apéndice D | — |
| 83 | frente | media | INCOHERENCIA · SIN FUENTE | RESUMEN | 8 rayas, 6 largas |
| 86 | frente | media | INCOHERENCIA · SIN FUENTE | RESUMEN | 8 rayas, 6 largas |
| 370 | cuerpo | media | CONTRADICE | §5.4.3 | 8 rayas, 6 largas |
| 399 | cuerpo | media | CONTRADICE | §5.5 | 2 rayas, 6 largas |
| 229 | cuerpo | media | CONTRADICE · INCOHERENCIA | limitacion novena | 6 rayas, 5 largas |
| 418 | cuerpo | media | INCOHERENCIA | limitacion novena · §5.8.5 | 6 rayas, 5 largas |
| 423 | cuerpo | media | CONTRADICE | conclusión específica 1 | 8 rayas, 4 largas |
| 412 | cuerpo | media | CONTRADICE · INCOHERENCIA | §5.8.3 | 4 rayas, 3 largas |
| 284 | cuerpo | media | INCOHERENCIA | — | 4 rayas, 2 largas |
| 352 | cuerpo | media | INCOHERENCIA | §5.2 | 0 rayas, 2 largas |
| 368 | cuerpo | media | CONTRADICE | §5.4.2 | 0 rayas, 2 largas |
| 341 | cuerpo | media | INCOHERENCIA | §4.5 | 2 rayas, 1 larga |
| 427 | cuerpo | media | INCOHERENCIA | conclusión específica 5 | 2 rayas, 1 larga |
| 428 | cuerpo | media | INCOHERENCIA | conclusión específica 6 | 2 rayas, 1 larga |
| 441 | cuerpo | media | SIN FUENTE | recomendación 7 | 0 rayas, 1 larga |
| 484 | apendice | media | CONTRADICE · INCOHERENCIA | apéndice A | 2 rayas, 1 larga |
| 492 | apendice | media | SIN FUENTE | apéndice C | 0 rayas, 1 larga |
| 227 | cuerpo | media | INCOHERENCIA | Hipotesis · limitacion novena | — |
| 277 | cuerpo | media | CONTRADICE | Tabla 2 | — |
| 357 | cuerpo | media | INCOHERENCIA | §5.3 | — |
| 358 | cuerpo | media | INCOHERENCIA | §5.3 | — |
| 359 | cuerpo | media | INCOHERENCIA | §5.3 | — |
| 437 | cuerpo | media | INCOHERENCIA | recomendación 3 | — |
| 439 | cuerpo | media | CONTRADICE | recomendación 5 | — |
| 342 | cuerpo | baja | INCOHERENCIA | §4.5 | 0 rayas, 1 larga |
| 344 | cuerpo | baja | INCOHERENCIA | §4.6 | — |
| 350 | cuerpo | baja | CONTRADICE | §5.1 | — |
| 396 | cuerpo | baja | INCOHERENCIA | Tabla 11 | — |
| 435 | cuerpo | baja | INCOHERENCIA | recomendación 1 | — |
| 490 | apendice | baja | INCOHERENCIA | apéndice B | — |

El detalle de cada uno —qué dice el libro, qué dicen los datos y de qué CSV salen— está en
`AUDITORIA_LIBRO.md`, en la sección de su gravedad.

## 2. Cómo está escrito: 48 párrafos con carga de estilo

Estas tres cosas son las que mide un detector, y son las tres que se arreglan sin discutir
el contenido:

- **Rayas (—).** El cuerpo tiene 132 en total. Son incisos: se convierten en
  paréntesis, en comas o en oración aparte. No hay ninguna suelta, así que siempre vienen
  de a pares y se sacan de a pares.
- **Oraciones largas.** La media del cuerpo es de 30,7 palabras. Las de más
  de 40 se parten, y el punto y coma marca dónde: no hay que reordenar palabras.
- **Series ordinales anunciadas.** 26 arranques «Primero/Segundo/…». Alcanza con
  variar el andamio en algunos, sacando el número anunciado al principio del párrafo.

| Párrafo | Palabras | Oración más larga | Largas | Rayas | `;` | Ordinal | Arranca |
|---:|---:|---:|---:|---:|---:|:---:|:---|
| 370 | 379 | 58 | 6 | 8 | 2 |  | La Tabla 7 muestra el ranking promedio de cada método (1 = m… |
| 229 | 437 | 72 | 5 | 6 | 5 | sí | Esta investigación se circunscribe a las siguientes limitaci… |
| 418 | 551 | 73 | 5 | 6 | 2 |  | La optimización no determina la configuración evaluada. El a… |
| 423 | 310 | 91 | 4 | 8 | 2 |  | La Propuesta Novedosa —con las respuestas lineales promediad… |
| 399 | 505 | 97 | 6 | 2 | 2 | sí | Los hallazgos cuantitativos pueden sintetizarse en seis obse… |
| 377 | 204 | 74 | 3 | 6 | 2 | sí | La Tabla 8 admite tres lecturas. Primero, toda fusión mejora… |
| 254 | 181 | 68 | 3 | 4 | 0 |  | La metodología clásica de fusión por transformada Top-Hat co… |
| 276 | 409 | 68 | 5 | 0 | 2 |  | Función de aptitud (Ortega y Espinoza). Los hiperparámetros … |
| 412 | 216 | 61 | 3 | 4 | 2 |  | Con las nueve métricas la suma de ramas —la combinación que … |
| 200 | 204 | 97 | 2 | 4 | 2 |  | Esta tesis se sitúa explícitamente en el espacio de los méto… |
| 237 | 124 | 52 | 2 | 4 | 1 |  | Una visión panorámica reciente la ofrece la revisión de Sing… |
| 271 | 163 | 58 | 2 | 4 | 1 |  | Optimización por Enjambre de Partículas (PSO). El método tie… |
| 284 | 180 | 95 | 2 | 4 | 1 |  | Dado que en la fusión VIS/IR no existe una imagen de referen… |
| 380 | 165 | 74 | 2 | 4 | 0 |  | Detección con clases complementarias (M3FD). Como complement… |
| 382 | 268 | 49 | 4 | 0 | 2 |  | La Tabla 9 muestra una complementariedad real pero asimétric… |
| 416 | 204 | 68 | 2 | 4 | 2 |  | Bajo el protocolo tal como está declarado —escenario A— la p… |
| 205 | 135 | 44 | 2 | 2 | 0 |  | La morfología matemática ofrece un marco intermedio: opera d… |
| 210 | 147 | 147 | 1 | 4 | 1 |  | Diseñar, implementar y caracterizar un operador de fusión de… |
| 260 | 124 | 55 | 1 | 4 | 2 |  | La propuesta central de esta tesis —la Propuesta Novedosa— e… |
| 338 | 139 | 84 | 2 | 2 | 1 |  | El diseño es comparativo inter-método: siete métodos de fusi… |
| 387 | 139 | 57 | 2 | 2 | 1 |  | La Tabla 10 compara la propuesta, en su configuración óptima… |
| 388 | 158 | 75 | 2 | 2 | 4 |  | La significación de estas diferencias se verificó con la pru… |
| 389 | 163 | 66 | 2 | 2 | 0 |  | La elección del peso es robusta: las 25 combinaciones del ba… |
| 219 | 72 | 72 | 1 | 2 | 0 |  | ¿En qué dirección desplaza el punto de operación de la fusió… |
| 221 | 46 | 46 | 1 | 2 | 0 |  | ¿Cómo debe formularse el operador —banco de disco y líneas, … |
| 225 | 43 | 43 | 1 | 2 | 0 |  | ¿La fusión —y en particular el método propuesto— mejora el d… |
| 267 | 102 | 53 | 1 | 2 | 1 |  | Reconstrucción y regla de fusión. Sobre la imagen base I_bas… |
| 285 | 93 | 52 | 1 | 2 | 0 |  | A continuación se formalizan las principales métricas sin re… |
| 341 | 151 | 49 | 1 | 2 | 1 |  | El corpus experimental son veinte pares VIS/IR del TNO Image… |
| 346 | 163 | 82 | 1 | 2 | 1 | sí | Se aplicaron tres procedimientos no paramétricos. Primero, l… |
| 348 | 83 | 83 | 1 | 2 | 0 |  | El capítulo presenta primero la caracterización del corpus y… |
| 352 | 168 | 74 | 2 | 0 | 4 |  | La figura 6 muestra tres pares representativos del dataset j… |
| 356 | 169 | 57 | 2 | 0 | 0 |  | La Tabla 4 presenta los promedios de las seis métricas clási… |
| 368 | 154 | 75 | 2 | 0 | 1 |  | Para precisar dónde residen las diferencias se aplicó la pru… |
| 375 | 82 | 49 | 1 | 2 | 1 |  | Para una evaluación concluyente —con verdad de campo— se ree… |
| 386 | 138 | 87 | 1 | 2 | 2 |  | La Propuesta Novedosa —método central de esta tesis— se opti… |
| 393 | 126 | 66 | 2 | 0 | 1 |  | La Figura 11 resume la optimización del método. El panel izq… |
| 403 | 164 | 55 | 1 | 2 | 0 |  | El orden de mérito no es una propiedad del operador sino del… |
| 408 | 165 | 38 | 0 | 4 | 0 |  | El resultado es inequívoco. Con las nueve métricas, la fusió… |
| 419 | 176 | 54 | 1 | 2 | 0 |  | El contraste con la tarea posterior cierra la auditoría. La … |
| 426 | 81 | 62 | 1 | 2 | 0 |  | La información mutua premia la combinación lineal: en la abl… |
| 427 | 92 | 58 | 1 | 2 | 5 |  | Dentro de la familia Top-Hat, la forma de combinar las respu… |
| 428 | 94 | 65 | 1 | 2 | 1 |  | Los dos hiperparámetros del método son el radio r y el peso … |
| 430 | 90 | 55 | 1 | 2 | 0 |  | El realce morfológico se paga en artefactos, y conviene decl… |
| 207 | 136 | 40 | 0 | 2 | 0 | sí | La justificación de este trabajo descansa sobre tres ejes. P… |
| 261 | 109 | 30 | 0 | 2 | 0 |  | Elementos estructurantes circulares y lineales. El operador … |
| 262 | 37 | 37 | 0 | 2 | 0 |  | Para cada fuente f y radio r, la ecuación (7) define la resp… |
| 311 | 64 | 33 | 0 | 2 | 0 |  | Representación de una imagen como suma de capas que aíslan e… |

## 3. RESUMEN y SUMMARY: el caso más barato y el más visible

- **Párrafo 83**: 604 palabras en un solo párrafo, 10 oraciones, la más larga de 110, 8 rayas y 7 puntos y coma.
- **Párrafo 86**: 524 palabras en un solo párrafo, 10 oraciones, la más larga de 96, 8 rayas y 7 puntos y coma.
- **Párrafo 229**: 437 palabras en un solo párrafo, 11 oraciones, la más larga de 72, 6 rayas y 5 puntos y coma.
- **Párrafo 276**: 409 palabras en un solo párrafo, 11 oraciones, la más larga de 68, 0 rayas y 2 puntos y coma.
- **Párrafo 370**: 379 palabras en un solo párrafo, 9 oraciones, la más larga de 58, 8 rayas y 2 puntos y coma.
- **Párrafo 399**: 505 palabras en un solo párrafo, 9 oraciones, la más larga de 97, 2 rayas y 2 puntos y coma.
- **Párrafo 418**: 551 palabras en un solo párrafo, 17 oraciones, la más larga de 73, 6 rayas y 2 puntos y coma.
- **Párrafo 423**: 310 palabras en un solo párrafo, 5 oraciones, la más larga de 91, 8 rayas y 2 puntos y coma.

Es lo primero que lee un examinador y es donde la longitud de oración es más alta de todo
el libro. Se parte en tres o cuatro párrafos cortando en los puntos y coma que ya tiene.

## 4. Para saber cuándo terminaste

| Qué | Ahora | Objetivo razonable |
|:---|---:|:---|
| Media de palabras por oración | 30,7 | 20 a 24 |
| Oraciones de más de 40 palabras | 121 | menos de la mitad |
| Rayas (—) en el cuerpo | 132 | menos de 40 |
| Arranques ordinales | 26 | menos de 10 |

Volver a correr este script después de cada tanda de reescritura recalcula la tabla.
