# Propuesta de encuadre del aporte — para conversar con el director

**17 de agosto de 2026.** Este documento no modifica nada. Es una propuesta de redacción para una
decisión que no me corresponde tomar: cómo queda enunciado el objetivo del trabajo.

## El problema, en cuatro frases

El objetivo registrado es **uno**: «proponer un algoritmo novedoso que demuestre eficiencia en su
calidad y aplicación en detección de objetos». El libro y el informe presentan hoy **dos aportes**, el
segundo de los cuales es auditar la validez discriminativa del protocolo de evaluación. Esa segunda
mitad apareció cuando los resultados de detección salieron negativos. Un tribunal puede leerla como un
objetivo reescrito para que los resultados lo satisfagan, y esa lectura es difícil de contestar si el
objetivo ampliado no está declarado como tal.

## Qué demuestra hoy la evidencia, mitad por mitad

**La mitad de calidad: demostrada, con su alcance.** Bajo el criterio del trabajo de referencia —las
nueve métricas sin imagen de referencia— la propuesta encabeza el benchmark: 1.ª de 7 con 3,394 de rango
medio, y conserva el primer puesto al retirar FE, la métrica redundante. El alcance hay que declararlo,
y ya está declarado en el informe: con las diecisiete métricas que el mismo evaluador calcula pasa a
3.ª, e incorporando Nabf a 2.ª. Es un primer puesto **sólido dentro de su criterio y dependiente de
él**.

**La mitad de aplicación: era el problema, y ahora tiene una respuesta.** Al medir la condición
aplicativa —un solo detector entrenado con las dos modalidades, inferencia sobre las fusionadas, y
contar cuántos de los objetos que sólo ve una modalidad conserva la fusión— la propuesta **en su punto
de operación adoptado** queda 6.ª de 7. Pero conservando r = 25 y bajando el peso de 0,30 a 0,10, en una
partición que no participó del ajuste, la conservación pasa de 57 a 74 de 119 objetos: 19 ganados contra
2 perdidos, McNemar exacto **p = 0,00022**. Re-ajustado, el operador es **estadísticamente
indistinguible de cuatro de los seis comparativos** y le gana al Top-Hat clásico. No supera a la Ratio
Pyramid.

## La propuesta: un objetivo, dos mitades, y la auditoría como explicación

El cambio que propongo **no amplía el objetivo**: lo deja como está, con sus dos mitades, y mueve la
auditoría del protocolo del lugar de «segundo aporte» al lugar que le corresponde por la evidencia —**la
explicación de por qué la segunda mitad no se cumplía con el punto de operación adoptado**.

Eso tiene tres ventajas sobre el encuadre actual. No hay objetivo reescrito que defender. La auditoría
deja de ser un agregado y pasa a ser necesaria para el argumento, porque es lo que explica el resultado.
Y el trabajo termina con un hallazgo positivo en lugar de uno negativo.

### Redacción propuesta para el encuadre del aporte

> El trabajo persigue un objetivo con dos mitades: proponer un operador de fusión VIS/IR por morfología
> matemática que demuestre eficiencia en la calidad de la imagen fusionada, y en su aplicación a la
> detección de objetos.
>
> La primera mitad se cumple dentro del criterio del trabajo de referencia, y el trabajo declara la
> dependencia de ese criterio en lugar de ocultarla: el primer puesto se conserva al retirar la métrica
> redundante y se pierde al completar la batería.
>
> La segunda mitad **no se cumplía con el punto de operación adoptado**, y averiguar por qué es lo que
> constituye el aporte metodológico del trabajo. La causa está medida: los hiperparámetros se eligieron
> sobre la batería de métricas de imagen, que premia la actividad espacial, y para la tarea aplicativa
> ese criterio seleccionaba casi el peor punto disponible de dieciocho evaluados. Elegido el punto sobre
> el criterio de la tarea, el operador pasa a ser indistinguible de los comparativos multiescala, con
> una mejora significativa y validada en datos que no participaron del ajuste.
>
> El aporte, entonces, es doble pero no son dos objetivos: es el operador, y la constatación de que el
> protocolo con que se evalúa la fusión no selecciona el punto de operación que la aplicación necesita.

### Y la conclusión que cierra la segunda mitad

> El punto de operación (r = 25; m = 0,30) proviene del piso de un rango de búsqueda heredado del
> trabajo de referencia, calibrado para un operador de disco único. Tres análisis independientes
> coinciden en que ese punto es agresivo para este operador: la equivalencia de energía de detalle
> muestra que equivale a m = 1,26 sobre un disco; el barrido de saturación, que multiplica por nueve la
> proporción de píxeles recortados frente a m = 0,10; y la medición de complementariedad, que lo ubica
> entre los peores de dieciocho configuraciones. Se recomienda adoptar m = 0,10 para la aplicación a
> detección, conservando r = 25 y con él la caracterización de calidad de este informe.

## Lo que hay que decidirle, concretamente

1. **¿Se declara la ampliación del objetivo, o se lo mantiene único con la auditoría como
   explicación?** Mi recomendación es la segunda: no requiere aval sobre un objetivo modificado y es
   más fuerte argumentalmente. Si se prefiere la primera, hay que declararla en el propio texto —«el
   objetivo se amplió durante la ejecución, con aval del director, por tal motivo»— y no dejarla
   implícita.
2. **¿Se adopta m = 0,10 como punto de operación para la aplicación?** Es la decisión con consecuencias
   sobre el resto del trabajo, y hay dos caminos: reportar dos puntos de operación —uno para calidad y
   uno para la tarea, que es en sí mismo el hallazgo— o adoptar uno solo y rehacer el benchmark de
   calidad con m = 0,10, lo que cambiaría todas las cifras del capítulo de resultados.
   **Recomiendo el primero**: dos puntos declarados, porque el hallazgo es precisamente que el criterio
   de calidad y el de la tarea piden puntos distintos.
3. **¿LLVIP se mantiene en el informe?** Su protocolo reentrena por entrada y su clase única es
   térmica, así que no puede medir complementariedad. Recomiendo mantenerlo, ya declarado como control
   de otra pregunta: son 45 corridas de trabajo válido y es el experimento que midió la resolución de
   este tipo de medida (0,0128 de mAP de desvío por semilla).

## Lo que este documento no resuelve

El libro (`docs/Tesis_Borrador_V3.docx`) **no fue modificado** con nada de esto. Su capítulo 6 sigue con
el encuadre de dos aportes y su §5.5 con el resultado de LLVIP como evaluación orientada a tarea. La
reescritura del libro depende de esta decisión, y por eso conviene tomarla antes.

El informe de avances sí incorpora ya la evidencia nueva —la medición por objeto, el barrido del punto
de operación y su validación— en las secciones 13 y 14, y la conclusión correspondiente en la 16. Lo que
no cambió en el informe es el encuadre de «dos aportes» de la apertura de la sección 16, que es
justamente lo que se propone acá.
