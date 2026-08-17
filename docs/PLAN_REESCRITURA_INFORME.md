# Plan de reescritura del informe de avances — 17 de agosto de 2026

Este plan sale de dos cosas que se aclararon hoy y que **cambian la estructura del informe, no su
redacción**. Reescribir párrafos sin resolver esto primero sería trabajo perdido.

## Las dos aclaraciones

**1. El objetivo registrado es UNO, no dos.** Es «proponer un algoritmo novedoso que demuestre
eficiencia en su calidad y aplicación en detección de objetos». El informe y el libro presentan hoy
**dos aportes**, el segundo de los cuales es auditar la validez discriminativa del protocolo de
evaluación. Esa segunda mitad apareció cuando los resultados de detección salieron negativos, y un
tribunal puede leerla como un objetivo reescrito para que los resultados lo satisfagan.

**2. El experimento que responde al objetivo es M3FD, no LLVIP.** La idea aplicativa es: hay objetos
que sólo se ven en el infrarrojo y otros que sólo se ven en el visible, y la fusión tiene que permitir
detectar **ambos**. El protocolo correcto —y es el que el director diseñó— entrena **un** detector con
las imágenes VIS e IR y sus etiquetas, y después **sólo infiere** sobre las fusionadas para comprobar
que detecte las dos clases. Eso es exactamente `experiments/detection_m3fd/train_eval_m3fd.py`, cuyo
docstring dice «la lógica del experimento (idea del director)».

LLVIP, en cambio, **reentrena el detector por cada entrada**, lo que responde otra pregunta: «¿con qué
entrada se entrena el mejor detector?». Y además LLVIP tiene **una sola clase, `person`, que es
térmica**, de modo que ahí no hay complementariedad posible que medir. Su resultado —«ninguna fusión
supera al infrarrojo solo»— **no es evidencia contra el objetivo**, y hoy el informe lo presenta como si
lo fuera.

## Lo que dice el dato bajo el protocolo correcto

En las 232 escenas de M3FD con ambas clases, recuperando **las dos a la vez**:

| Entrada | Recupera ambas | |
|---|---|---|
| Pirámide de Laplace | 57,8 % | |
| Ratio Pyramid | 55,6 % | |
| DTCWT | 54,3 % | |
| **VIS solo** | **53,0 %** | ← la vara |
| DWT | 52,2 % | |
| Curvelet | 50,4 % | |
| **Propuesta** | **50,0 %** | 7.ª de 9 |
| IR solo | 49,1 % | |
| Top-Hat clásico | 47,0 % | |

Dos lecturas, y las dos hay que decirlas:

- **La premisa del objetivo queda confirmada.** Cuatro fusiones recuperan ambas clases más seguido que
  cualquier modalidad sola. La fusión sirve para lo que se propone que sirva.
- **El operador propuesto no la cumple.** Queda por debajo del visible solo. Y se ve por qué en el
  desglose por clase: en `Lamp` —la clase que sólo existe en el canal visible— cae a **0,4881** contra
  **0,6161** del visible. La familia Top-Hat es la que más daño le hace a la clase visible.

La causa es el propio hallazgo del trabajo: el punto de operación (r = 25, m = 0,30) se eligió sobre las
nueve métricas de imagen, que premian actividad espacial, y eso es justo lo que borra las fuentes de luz
de bajo contraste. **Los hiperparámetros se eligieron con un criterio y se los evalúa con otro.**

## Qué se reescribe, en orden

### 1. El encuadre del aporte (§1, 2 págs; §16, 1 pág)

Pasar de «dos aportes» a **un objetivo con dos mitades de evidencia**: la calidad y la aplicación a
detección. La auditoría del protocolo deja de ser un aporte paralelo y pasa a ser **la explicación de
por qué la segunda mitad no se cumple con el punto de operación adoptado** — que es su lugar natural y
además el que no obliga a inventar un objetivo.

### 2. La jerarquía de los dos experimentos de detección (§13, 2 págs; §14, 4 págs)

Hoy §13 es LLVIP y §14 es M3FD, en ese orden, y LLVIP se presenta como «evaluación orientada a tarea».
Hay que invertir la jerarquía: **M3FD es el experimento del objetivo** y LLVIP es un control de otra
pregunta. Concretamente:

- §13 (LLVIP) declara desde el título y el primer párrafo que **reentrena por entrada** y que su clase
  única es térmica, de modo que mide la calidad de la entrada como material de entrenamiento y **no** la
  complementariedad. Su resultado se conserva entero: es un buen control y las cinco semillas valen.
- §14 (M3FD) pasa a ser el capítulo central de la mitad aplicativa, con el protocolo del director
  explicado desde el arranque: un modelo, entrenado con las dos modalidades, inferencia sin reentrenar.

### 3. La afirmación que hay que corregir en varios lugares

«Ninguna fusión supera a la mejor modalidad individual» es verdadera **en LLVIP** y falsa en M3FD, donde
cuatro fusiones superan a las dos modalidades. Hoy aparece como conclusión general. Hay que acotarla al
experimento, y decir el resultado de M3FD, que es el que corresponde al objetivo.

### 4. La hipótesis H6

Está enunciada como «ninguna fusión supera por un margen distinguible a la mejor modalidad individual».
Con el protocolo correcto eso no se sostiene: hay que reformularla o desdoblarla en la parte que
LLVIP contrasta y la parte que M3FD contrasta.

## La condición de éxito, en su forma estricta: hay que agrandar la muestra antes de medir nada

El criterio del autor es más preciso que «recupera ambas clases»: **si el objeto A se detecta sólo en
VIS y el objeto B sólo en IR, entonces A y B tienen que detectarse en la fusionada**. O sea que cada
modalidad aporta justo lo que a la otra le falta.

Eso NO es lo que mide hoy `run_complementariedad_escenas.py`. Su línea 186 define crítica como «ni VIS
ni IR recuperan ambas», que incluye escenas donde una clase se le escapa a las **dos** modalidades —y
ahí ninguna fusión puede recuperarla, porque no se puede crear información que ninguna fuente tiene—.
Esas escenas castigan a todos los métodos por algo que no es de la fusión.

Calculada la condición estricta sobre `complementariedad_por_escena.csv`:

| | |
|---|---|
| Escenas con ambas clases anotadas | 232 |
| Críticas según la definición del script | 90 |
| **Estrictamente complementarias (la condición del autor)** | **5** |

Y de esas cinco: seis de las siete fusiones resuelven **2 de 5**, y la propuesta **1 de 5**.

**Con n = 5 no se puede demostrar nada, ni a favor ni en contra.** Y la causa no es el operador sino el
dataset: las cinco son todas en la dirección VIS→Lamp / IR→People, y **ninguna** al revés, porque en
M3FD el visible también detecta personas bastante bien (AP@0,5 = 0,6207), así que casi nunca se da el
caso de que las pierda. La complementariedad estricta existe, pero es rarísima en esta partición.

### Consecuencia para el orden de trabajo

**La grilla de (r, m) NO se puede medir sobre cinco escenas**: sería ruido. Antes hay que conseguir una
muestra donde la condición estricta esté disponible en cantidad. Tres palancas, de la más barata a la
más cara:

1. **Medir por OBJETO y no por clase.** El autor habla de «objeto A» y «objeto B», y la medida actual es
   por clase: «recupera» significa al menos un verdadero positivo de esa clase en la escena. Contando
   objeto por objeto —para cada objeto anotado, ¿lo detecta sólo el VIS, sólo el IR, los dos, o
   ninguno?— la muestra pasa de 5 escenas a cientos de objetos, y es **más fiel a la condición
   enunciada**. Es la palanca más fuerte y no requiere reentrenar ni volver a fusionar: el script ya
   calcula los verdaderos positivos, hay que emparejarlos por caja en lugar de agregarlos por clase.
2. **Usar M3FD completo** (`data/M3FD_Detection`) en lugar de las 232 escenas, que son sólo la partición
   de validación con ambas clases anotadas. Más escenas, más casos complementarios.
3. **Filtrar escenas nocturnas**, que es donde el visible de verdad pierde a las personas. En las
   carpetas del dataset no hay metadata de día/noche, pero se puede derivar de la luminancia media del
   canal visible, que es barato y defendible.

Recién con la muestra agrandada tiene sentido correr la grilla.

## Lo que queda pendiente de medir, y es la oportunidad

Si el objetivo es detectar ambas clases, **el punto de operación hay que elegirlo sobre ese criterio** y
no sobre la batería de imagen. Se puede probar sin reentrenar nada: el modelo de M3FD ya está entrenado
(`runs/detect/runs/m3fd/mixto/weights/best.pt`), así que basta re-fusionar las 232 escenas con una
grilla de (r, m) y correr inferencia.

Costo medido, no estimado: **566 ms por escena** (imágenes de 768×1024), o sea **131 s de fusión** por
punto de la grilla, más la inferencia y el conteo: **~3 minutos por punto**. Una grilla de doce puntos,
unos 40 minutos.

Antes de correrla hay que **validar el arnés reproduciendo el 50,0 % ya publicado**. Si el script no
reproduce la cifra conocida, la grilla mide cualquier cosa.

Los dos resultados posibles son publicables:

- **Si algún (r, m) pasa el 53,0 % del visible**, el objetivo queda demostrado, y con el argumento más
  fuerte disponible: el operador sirve para la tarea cuando se lo ajusta a la tarea, y la batería de
  métricas de imagen llevaba al punto equivocado.
- **Si ninguno lo pasa**, el resultado es que la familia Top-Hat no sirve para complementariedad. Hay
  que decirlo, y es mejor saberlo ahora que en la defensa.

## Antes de tocar una línea

Esto se habla con el director, y son dos puntos:

1. Que LLVIP reentrenado no responde al objetivo, y que el experimento que sí lo responde es el de M3FD
   que él diseñó.
2. Que se va a buscar el punto de operación del operador **sobre el criterio de complementariedad**.

El experimento de M3FD fue su idea; esta grilla es la continuación natural de ese diseño.
