# Estado y pendientes — 10 de agosto de 2026

Punto de retomada. Todo lo que sigue está verificado; lo que no, está marcado como tal.

## El deck quedó al día: las quince láminas aplicadas

El informe de avances **está listo para enviar** (85 páginas, cuatro verificadores en 0 fallos, con
una carilla de resumen en lenguaje llano en la página 2). Y el deck de defensa quedó al día: las
quince láminas con prescripciones sin aplicar están aplicadas, con los apartamientos razonados que se
detallan abajo.

Se contrastó `Plan_Deck_Defensa.md` lámina por lámina contra el pptx real, y el resultado corrige lo
que se venía diciendo: eran **quince láminas con prescripciones sin aplicar**, no las cinco que se
habían identificado. La estructura del plan sí está hecha —23 láminas, las cuatro nuevas existen, la
14 y la 15 viejas están fundidas en la 18, los pies dicen «n / 22», las 23 tienen notas—; lo que
faltaba era texto de cuerpo. En orden de gravedad, y todas hechas:

| Lámina | Qué falta |
|---|---|
| ~~**19**~~ | **HECHA el 11 de agosto.** Las nueve cajas pasaron a un cuadro único con **las siete hipótesis** a 11,5 pt, más la línea de pie. Ver abajo. |
| ~~**21**~~ | **HECHA el 11 de agosto.** Los cinco párrafos «ANTES» pasaron a dos encabezados y nueve párrafos a 11 pt: las cuatro recomendaciones sobre el protocolo y el uso recomendado acotado. Ver abajo. |
| ~~**10**~~ | **HECHA el 11 de agosto.** Tres columnas con los cuatro controles de la auditoría y la línea de pie con las cuatro limitaciones declaradas. Ver abajo. |
| ~~**20**~~ | **HECHA el 11 de agosto.** Siete conclusiones numeradas —tres del primer aporte, cuatro del segundo— y cierre con el aporte metodológico. Ver abajo. |
| ~~**12**~~ | **HECHA el 11 de agosto.** Tabla de diez columnas con las nueve métricas, los dos bloques rotulados, y de paso se corrigió un desborde que venía de antes. Ver abajo. |
| ~~**8**~~ | **HECHA el 11 de agosto.** Los cinco párrafos reescritos: la cita de Bala plegada en la novedad y el renglón liberado con el aporte del banco aislado. Ver abajo. |
| ~~**9**~~ | **HECHA el 11 de agosto.** Título con «(OE2 / H5)», declarada la circularidad del conjunto de ajuste y agregada la aptitud de la imagen base, con una acotación que el plan no tenía. Ver abajo. |
| ~~**3**~~ | **HECHA el 11 de agosto.** Agregado el párrafo del segundo problema, que es lo que le da sentido al título. |
| ~~**4**~~ | **HECHA el 11 de agosto.** Agregada la «Pregunta central». |
| ~~**13**~~ | **HECHA el 11 de agosto.** El desglose de fidelidad cierra las 20 comparaciones y el p5 descuenta FE: cinco de ocho dimensiones. |
| ~~**1**~~ | **HECHA el 11 de agosto.** Subtítulo con los dos aportes, y de paso se fue un error de tipeo: decía «de **diso** y lineales». |
| ~~**2**~~ | **HECHA el 11 de agosto.** El punto 7 con su subtítulo y las notas con el corte entre los dos aportes. |
| ~~**11**~~ | **HECHA el 11 de agosto.** Pie de dos líneas que dice qué mirar y conecta con el análisis cuantitativo. |
| ~~**23**~~ | **HECHA el 11 de agosto.** «Reserva — M3FD: dos escenas de la validación (conf ≥ 0,30)». |
| ~~**18**~~ | **HECHA el 11 de agosto.** El cuarto párrafo con el veredicto de H6, con la figura al 85 % y no al 69 % que se temía. |

**Con esto el deck queda con las quince láminas al día.** Lo único que no se aplicó de
`Plan_Deck_Defensa.md` son las prescripciones que el propio trabajo dejó atrás, listadas más abajo, y
las tres cifras que no se pueden verificar.

**Tres cosas que no hay que proyectar sin resolver antes.** (1) Las «13 escenas físicamente
distintas» que el plan pide para las láminas 10 y **11 no están en ningún CSV ni script**: la cifra
aparece sólo en el plan, agrupando los 20 nombres salen 13 o 14 según si las dos tomas de
`soldier_in_trench` cuentan como una escena, y encima el corpus cambió al sustituir el par corrupto.
Si se quiere el número, hay que fijar y versionar el criterio de agrupamiento. En la lámina 10 se
resolvió diciendo la forma verificable —«hay series de hasta tres tomas de la misma escena»—; en la
11 conviene hacer lo mismo. (2) EN de Curvelet:
la fuente da 6,6445, el deck imprime 6,644 y el plan 6,645. (3) MI_ir de Curvelet: la fuente da
0,6695 y el plan 0,670. Los dos últimos son fronteras de redondeo, hay que alinearlas con el
generador de la tabla.

### Láminas 19 y 21: hechas el 11 de agosto, y lo que aparecieron en el camino

**Lámina 19.** Las nueve cajas (etiqueta + veredicto + cuerpo, por tres filas) no admiten siete
filas, así que pasaron a un cuadro único con la geometría que ya usa la lámina 20, a 11,5 pt, que es
el cuerpo de la lámina 18. Las siete hipótesis con su veredicto, más la línea de pie que separa las
dos del operador (H1 y H7) de las cinco del criterio (H2 a H6). El render deja 17 pt de aire antes
del pie.

**Al verificar sus cifras apareció un defecto de fondo: el ρ = +0,214 de H6, que el deck ya
proyectaba, no lo calculaba ningún script.** Vivía sólo en documentos de texto —el plan del deck y
dos archivados—, y uno de ellos lo declara como pendiente de versionar («E5»). Una cifra sin
generador es una cifra que nadie puede rehacer. Se escribió
`experiments/run_correlacion_calidad_deteccion.py`, que recalcula la correlación de Spearman y de
Kendall entre el rango medio de calidad de las siete fusiones y su mAP, con tres conjuntos de
métricas (nueve, nueve sin FE, diecisiete) y dos medidas en LLVIP y M3FD: doce contrastes. **El
valor del deck se confirmó**: ρ = 0,2143 con p = 0,6445. El script trae tres controles, y uno de
ellos comprueba que su rango medio con las nueve coincide con `ranking_methods.csv`.

**Y ese script encontró algo que conviene tener a mano en la defensa.** Con las nueve métricas
reportadas ninguno de los cuatro contrastes es significativo, que es lo que sostiene H6. Pero con el
conjunto ampliado de diecisiete, sobre el mAP@0,5:0,95 de M3FD, **sí aparece asociación y en la
dirección esperada: ρ = −0,8929 con p = 0,0068**. Son doce contrastes sobre siete métodos, así que
no sobrevive a la corrección por multiplicidad (Bonferroni 0,0816) y es una pista, no un resultado.
Dice lo mismo que el control negativo: la batería de nueve no predice la utilidad y la ampliada
apunta a que sí. Quedó escrito en las notas del orador de la lámina 19, con la advertencia de
presentarlo así.

**Lámina 21.** Los cinco párrafos «ANTES» pasaron a dos encabezados y nueve párrafos a 11 pt: las
cuatro recomendaciones sobre el protocolo —el aporte transferible, que no estaba en ninguna lámina—
y las cinco sobre el operador, con el uso recomendado acotado. Ya no dice «la propuesta es la opción
recomendada» sin más: declara el costo en fidelidad y artefactos y nombra al líder de cada métrica.

**Se corrigió una afirmación falsa del plan.** El plan pedía decir que «con Nabf el control negativo
se corrige por completo». Se comprobó y **no es cierto**: al sumar Nabf el brazo de ruido con
σ = 0,20 baja del 3.er al 7.º puesto de 14, pero **todavía le gana a Curvelet (7,525) y al Top-Hat
clásico (7,600)**. Recién con las diecisiete queda último (10,138). La lámina dice eso, que además
es mejor argumento: una métrica sola no alcanza, y por eso la cuarta recomendación pide el control
negativo como requisito del benchmark.

### Láminas 10 y 20: hechas el 11 de agosto

**Lámina 10.** El diseño experimental pasó de dos columnas a tres. La lámina 4 promete dos aportes, y
el segundo es la auditoría del protocolo, pero el diseño experimental proyectaba sólo el benchmark de
calidad y la detección: **los cuatro controles que sostienen el segundo aporte no aparecían en ninguna
lámina**. Ahora hay una columna «Controles de la auditoría» con el control negativo, la ablación del
banco, el ajuste simétrico y la sensibilidad del criterio, más una línea de pie con las cuatro
limitaciones declaradas —CVT como wavelet db4, las series de tomas de la misma escena, la ausencia de
partición de prueba en LLVIP y la única semilla—, que son las primeras preguntas previsibles de la
mesa. Cierra el hallazgo **n99**.

Dos apartamientos del plan, los dos a propósito. El plan escribe «Toet, 2014» y el deck dice **«Toet,
2017»**, que es la entrada correcta. Y el plan pide decir «20 pares correspondientes a 13 escenas
físicamente distintas»: **esa cifra no está en ningún archivo del repositorio**, sólo en el plan.
Agrupando los veinte nombres por prefijo dan 13 grupos, pero uno junta `soldier_in_trench_1`
(meting016) y `_2` (meting055), que son sesiones de medición distintas; contadas aparte son 14. Sin un
criterio de agrupamiento versionado el número no se defiende, así que la lámina dice la forma que sí
se verificó —hay series de hasta tres tomas de la misma escena— y las notas explican el 13 o 14 por si
lo preguntan.

De maquetación aparecieron dos cosas en el render. Los encabezados de una sola línea no alcanzan: el
tercero, «Evaluación en tarea (dos experimentos)», se parte en dos y **su segunda línea se dibujaba
encima del primer renglón del cuerpo**. Se les dio alto de dos renglones y los tres cuerpos arrancan
a la misma altura. Y las columnas de 2.700.000 EMU que proponía el plan dejan calles de 43.200 EMU
—menos de medio milímetro—, con lo que las tres se leen como un bloque: se usaron 2.600.000 con
calles de 214.800, que suman el ancho útil exacto.

**Lámina 20.** Las cinco conclusiones con la arquitectura de un solo aporte pasaron a **siete
numeradas**: las tres primeras del operador y las cuatro del criterio, cerrando con el aporte
metodológico, que es lo único de la tesis transferible a otro trabajo de fusión y el puente natural a
la lámina 21.

**Se corrigió otra cifra del plan.** Su conclusión 2 dice «a peso igualado la propuesta gana por
0,683». Sale del cálculo defectuoso que este documento ya registra —el generador metía al clásico dos
veces en el pool y diluía los siete rangos—. Se recalculó desde `control_tophat_igual_peso.csv`
sustituyendo al clásico dentro del benchmark de siete: **3,528 frente a 3,694**. No copiar el 0,683 a
ninguna lámina.

### Láminas 12, 8 y 9: hechas el 11 de agosto, y un chequeo nuevo

**Lámina 12.** Se titulaba «Resultados cuantitativos por bloques» y no se veía ningún bloque: la
tabla proyectaba cinco métricas y su prosa de cierre citaba MG 0,0355, MI_vis, MI_ir y PSNR, **cuatro
cifras que el tribunal no tenía a la vista**. Es el peor caso en una lámina de resultados: el orador
nombra números que la pantalla no muestra. Ahora la tabla tiene diez columnas con las nueve métricas,
y los dos bloques se marcan **dos veces** —un rótulo centrado sobre cada grupo de columnas y dos tonos
de gris en las cabeceras— por si la proyección pierde el matiz. El script **lee las celdas del CSV** en
vez de tenerlas escritas, y calcula las negritas con la dirección de cada métrica tomada de
`src/metrics/evaluators.py`: así ni los valores ni el «cuál es el mejor» pueden quedar viejos.

**Y apareció un defecto que ningún chequeo veía, anterior a este trabajo.** El último renglón de la
prosa de cierre de la lámina 12 **se dibujaba en y = 408,9 pt sobre una lámina de 405**, o sea fuera
de la lámina: en la proyección el cierre de la lámina de resultados simplemente no estaba. El bloque 9
no lo detecta porque comprueba que el texto **llegue** al PDF, y llegaba — LibreOffice lo dibuja
igual, pasado el borde. Se descubrió mirando el render. Se agregó el **bloque 23**, que exige que
ningún bloque de texto de ninguna lámina pase el borde; se probó que discrimina corriéndolo contra el
PDF comiteado de antes, donde marca la lámina 12, y contra el de ahora, donde pasa. Se barrieron las
23 láminas: era la única.

**Lámina 8.** Los cinco párrafos eran los «ANTES» del plan palabra por palabra. La cita de Bala se
plegó dentro de la viñeta de la novedad, que es de donde viene el esquema, y el renglón liberado ahora
dice el **aporte de la suma aislado en la ablación**: mejor de los seis brazos con las nueve métricas,
**cuarto con las diecisiete**, y duplica la tasa de artefactos del disco único (Nabf 0,374 frente a
0,185; la razón es 2,02, así que va «duplica» y no «casi duplica»). Se precisó también que el máximo
opera **entre fuentes** y no entre las ramas del banco, que es la confusión más fácil de cometer
mirando el flujograma.

**Lámina 9.** Título con el sufijo «(OE2 / H5)»; declarada la circularidad del ajuste —la aptitud se
promedia sobre 3 de las 20 escenas que **también** integran el conjunto de evaluación, sin partición
separada—; y agregada la comparación con la imagen base.

**Se corrigió otra afirmación del plan, y esta importa.** El plan pide decir «en la propia aptitud, no
aplicar el operador puntúa mejor que aplicarlo: la base obtiene F_o = 1,7583, por encima de 1,7350 y
de 1,7057». Sin acotar **es falso**: `aptitud_operador_configs.csv` muestra que la propuesta con
m = 0,0703 alcanza 1,7715 y el clásico reoptimizado 1,7715, los dos **por encima** de la base. La
afirmación vale **dentro del rango publicado**, y así quedó escrita. Con la acotación el argumento es
más fuerte, porque muestra que lo que produce el resultado es el rango heredado.

De maquetación, la 9 dio dos cosas. Al crecer el p0 con la circularidad, el p1 se fue **fuera de la
lámina** (y = 406,5): se subió el recuadro a 2.620.000 —justo debajo de la ecuación de F_o— y se le
quitaron «(1,7350)» y «1,7057», que ahora los dice el recuadro de la derecha en la misma lámina. Y los
**dos cuadros de la lámina estaban pegados sin calle**: el izquierdo terminaba exactamente donde
arranca el derecho, y con el texto llegando al borde quedaban 1,7 pt de aire. Se angostó el izquierdo
a 4.350.000 y se bajó medio punto el cuerpo; la calle real quedó en 20,5 pt.

### Las ocho últimas: 1, 2, 3, 4, 11, 13, 18 y 23, hechas el 11 de agosto

Las cuatro que tenían un párrafo faltante son las que más cambian el sentido de su lámina. La **3** se
titulaba «dos preguntas, no una» y planteaba sólo la primera; ahora enuncia el segundo problema, que
es la falta de imagen de referencia y las métricas «mayor es mejor» con los hiperparámetros elegidos
sobre ellas mismas. La **4** ganó la «Pregunta central», que era **el único enunciado explícito de la
pregunta de investigación en todo el deck** y no estaba en ninguna parte. La **13** cerró dos cuentas
que quedaban abiertas a la vista: sin «y dos no significativos» el desglose del bloque de fidelidad
daba 18 de 20, y sin la frase que descuenta FE el deck decía «6 de las 9» dos láminas después de haber
demostrado que FE no es una dimensión independiente —son **cinco de ocho**—. Y la **18** por fin lleva
el veredicto de H6.

La **portada** anunciaba un solo aporte, «Una propuesta… optimizada por PSO», que la lámina 4 desmonta
y que sus propias notas ya corregían. **Y traía un error de tipeo: «de diso y lineales».** En la
portada de una defensa. Se fue con el reemplazo.

La **23** dejó de titularse «La prueba visual»: llamar «prueba» a dos escenas es exactamente el
razonamiento anecdótico que el segundo aporte desarma, y así lo dice el §5 del plan.

**El párrafo de la 18 no necesitaba encoger la figura al 69 %.** Estaba diferido por eso. Se intentó
primero sin tocarla, acortando el p0 y omitiendo el «margen de 0,004» que el plan ofrecía como
opcional —el p1 ya dice 0,622 contra 0,618, así que el margen se lee solo—, pero el veredicto entrába
al PDF a medias: LibreOffice recortaba «no la hipótesis. Es un resultado del trabajo, no una
limitación», que es justo el caso que el bloque 9 está puesto para atrapar. Con la figura al **85 %**,
manteniendo centro y proporción, entra completo y sobran 15 pt.

En la 18 se usó la formulación de la lámina 19 y no la del plan, que escribe «queda RECHAZADA» a
secas: eso contradice a la 19, que dice «lo que queda rechazado es la traslación de la calidad a la
tarea, no la hipótesis». En la 11 se omitió «correspondientes a 13 escenas distintas», por el mismo
motivo que en la 10.

### Y el bloque 10 y una debilidad del verificador

El **bloque 10** marcó que el párrafo nuevo de la lámina 3 quedaba **1,1 pt por debajo de la figura**:
el texto terminaba en y = 242,3 y la figura arranca en 241,2. Se bajó el cuerpo a 11,5 pt y quedan
4,5 pt de aire.

Y apareció algo peor, en el verificador mismo. Al publicar la tabla de diez columnas de la lámina 12
—que trae MI_vis de la Ratio Pyramid = 0,949— el aviso de los mAP de LLVIP pasó de reclamar tres
métodos a reclamar uno. **Parecía una mejora y no lo era**: `contiene()` hacía `v in t` a secas, y las
variantes de dos decimales son cortas, así que la búsqueda de «0,94» (Curvelet 0,9403 y DWT 0,9394)
quedaba satisfecha por el «0,949» de otra métrica. El chequeo se estaba aflojando solo. Ahora
`contiene()` exige que el número aparezca **como cifra entera**: ni un dígito ni un separador seguido
de dígito antes o después. Se probó con doce casos límite, y el discriminador **encontró un error de
índice** en la primera versión —con un solo carácter después del número se salía del string—. El aviso
volvió a marcar los tres que de verdad faltan.

Dos cosas de mecánica que conviene recordar si se vuelve a tocar el deck. **Un `text_frame`
siempre conserva su primer párrafo**, así que al vaciar un cuadro hay que quitarle también su
`<a:pPr>`: si no, ese párrafo mantiene la viñeta y la sangría del original mientras los que crea
`add_paragraph()` salen limpios, y la lámina queda con el primer renglón viñeteado y los demás no
—se vio en el render de la 21—. Y **el bloque 9 compara contra el PDF comiteado del deck**, de modo
que después de editar el `.pptx` hay que regenerar `docs/Tesis_Defensa_Presentacion.pdf` con
LibreOffice o el chequeo informa, con razón, que los párrafos nuevos no llegan al PDF.

**Y el aviso de maquetación, que se cumplió.** Nueve de las quince láminas crecían en texto sobre recuadros que ya
están llenos, y este deck tiene dos antecedentes de texto que no llega al PDF y de texto tapado por
una figura. Después de **cada** edición hay que correr los bloques 9 y 10 de
`verificar_entregables.py`.

**Prescripciones que ya están aplicadas y que no hay que volver a aplicar.** Las dos figuras de la
§4 del plan están regeneradas, y a propósito con texto distinto del que el plan proponía: el título
que pedía el plan hablaba de «16 casos», reparto de una sola semilla que el estudio de 500 corridas
dejó atrás. Por lo mismo, **no reintroducir «r = 1 en 16 de las 25» en ninguna lámina**. El «gana
por 0,683: 3,467 frente a 4,150» del plan también está superado: el deck dice 3,528 frente a 3,694,
margen 0,166, que es el cálculo correcto. La lámina 10 va con «Toet, 2017» y no con el «Toet, 2014»
del plan. Y las láminas 5, 6, 7, 14, 15, 16, 17 y 22 están completas.

**Los 106 hallazgos de la reverificación están CERRADOS: 96 aplicados y 10 resueltos, con cero
`A_LEER` y cero `PENDIENTE`.** De los diez últimos, cinco eran defectos reales y cinco resultaron
no serlo al leerlos. El registro con la razón de cada cierre está en `docs/fuentes/resueltos.json`;
el detalle de lo que se corrigió, en la sección del 8 de agosto.

## Cómo correr las cosas

Las dependencias viven en `.venv`, **no** en el Python del sistema:

```
.venv\Scripts\python.exe -X utf8 experiments/<script>.py
```

Tres verificadores, todos en 0 fallos al cierre:

| Script | Qué comprueba |
|---|---|
| `verificar_entregables.py` | los cuatro entregables contra los CSV: medias, ranking, detección, afirmaciones retiradas, coherencia entre documentos, **quince** figuras embebidas por md5, montajes, paginación, el texto del deck que el PDF recorta, el texto que queda **debajo** de una figura, las páginas del informe que **derraman** su contenido, las formulaciones retiradas del barrido PSO **leyendo también las notas del orador** y el cruce de **toda cita contra la bibliografía** |
| `verificar_libro.py` | el libro en detalle: cifras retiradas, medias, rangos, detección, sección 5.8, **las 79 entradas del índice** y las cinco figuras embebidas |
| `triar_hallazgos.py` | reparte los 106 hallazgos de la reverificación en YA_APLICADO / A_LEER / PENDIENTE; acepta `--gravedad` y `--doc` |

El libro se edita con **python-docx** cuando el cambio es de texto: los párrafos del cuerpo
tienen un solo run, así que basta `p.runs[0].text = ...` y `doc.save()`. Después, PDF por
LibreOffice:

```
"C:\Program Files\LibreOffice\program\soffice.exe" --headless --convert-to pdf --outdir docs docs\Tesis_Borrador_V3.docx
```

El deck se edita con **python-pptx** y su PDF sale por el mismo camino:

```
"C:\Program Files\LibreOffice\program\soffice.exe" --headless --convert-to pdf --outdir docs docs\Tesis_Defensa_Presentacion.pptx
```

**LibreOffice es el renderizador con que se produjeron los dos PDF commiteados**: se comprobó el
5 de agosto reconvirtiendo las versiones de `HEAD` y comparándolas contra los PDF del repo —74 y
23 páginas, 0 páginas con texto distinto y huellas de píxeles idénticas—. O sea que recompilar no
repagina nada. Conviene repetir esa comprobación antes de recompilar si alguien edita en Word.

Si se cambia una figura **incrustada** en el deck, regenerarla en `docs/figures` no alcanza: hay
que reescribir la parte de imagen del paquete. `sh.image` es un envoltorio y asignarle `_blob` no
persiste; la parte real es `sh.part.related_part(sh._element.blip_rId)`.

**Al terminar hay que revisar el índice**: es texto fijo, no un campo de Word, y un párrafo
más largo mueve un salto de página y lo desfasa en silencio. Pasó dos veces el 4 de agosto
—§5.4 de la 49 a la 50 y §6.2 de la 65 a la 66— y las dos las cazó el bloque 8 de
`verificar_libro.py`, que ahora comprueba las 79 entradas y no solo las seis de 5.8.

## Estado de los entregables

Medido el 5 de agosto sobre los archivos compilados, no copiado de la versión anterior:

| | | |
|---|---|---|
| Libro | 74 pág. | **38** referencias auditadas, sección 5.8 de auditoría del protocolo |
| Deck | 22 láminas + reserva (23 pág. de PDF) | |
| Avances | 82 pág. | cero derrames de página; la portada es la única sin pie |
| README | 572 líneas | |

## Cerrado el 3 de agosto (sesión de la tarde) — el deck

**Hallazgo 26, el más grave, aplicado.** Lámina 19: la etiqueta de H6 decía
«RECHAZADA» en rojo y ahora dice «SE SOSTIENE» en el mismo verde de H1 y H5, con el
cuerpo reescrito («lo que queda rechazado es la traslación de la calidad a la tarea, no
la hipótesis»). Las cinco cifras se recalcularon antes de escribir: IR 0,9708 contra
0,9515 de la mejor fusión, ρ = +0,214 con p = 0,6445 (`spearmanr` sobre `avg_rank` y
`mAP50` de las siete fusiones), y `binomtest(8, 23, 0.5)` = 0,21004 sobre las 232
escenas de `complementariedad_resumen.csv`.

**Dos defectos más del deck, encontrados de paso y corregidos:**

1. **Notas del orador que decían lo contrario de su lámina** — el mismo patrón del
   commit anterior, que se saltó estas dos. La 19 seguía con las notas de la versión de
   tres hipótesis («H3 solo parcialmente») y la 18 afirmaba que las personas solo se ven
   en IR y las luces solo en VIS, justo lo que el cuerpo de su lámina desmiente. Ojo con
   el plan: `Plan_Deck_Defensa.md` prescribe para la 19 «cuatro de ellas son hallazgos
   sobre el criterio» y **son cinco** (H2, H3, H4, H5 y H6 llevan la etiqueta *criterio*
   en la lámina 6). Se escribió cinco.
2. **Texto que no llegaba al PDF.** LibreOffice recorta en el borde de la lámina, así
   que lo que no entra no se dibuja y no queda rastro. La **18 perdía entero el tercer
   párrafo** —el conteo por escena, que es la operacionalización de OE5—, la **5**
   perdía la última palabra de OE5 y además «empleado.» tocaba «Objetivos específicos»,
   y la **23** perdía el cierre del pie. Se corrigió bajando dos cuerpos de letra en la
   5 (13,5 → 13 y 13 → 12,5 pt) y encogiendo la figura en la 18 y la 23 para darle su
   lugar al texto. Los altos se calcularon con las métricas de la fuente, no a ojo.

**Comprobación ya automatizada:** comparar el texto de cada shape del pptx con el de su
página en el PDF detecta este recorte sin mirar geometría. Es el **bloque 9 de
`verificar_entregables.py`**. Con eso el deck pasó de 6 párrafos con texto perdido a 0, y
la comprobación discrimina: desalineando lámina y página marca 134 párrafos.

Queda **sin aplicar, a decisión del autor:** el plan pide para la lámina 18 un cuarto
párrafo («Se sostiene H6, con muestra suficiente…»). No se puso porque obliga a encoger
la figura a ~69 % de su ancho original; con la 19 ya corregida el deck no se contradice.

## Cerrado el 4 de agosto — los siete PENDIENTE y dos defectos nuevos

Los siete se verificaron ejecutando el cálculo antes de escribir, y los siete resultaron
reales. Tres venían **aplicados a medias**, de modo que lo que faltaba era menos de lo que
decía el triador.

**Libro** (hallazgos 70, 74, 85, 88, 95 y los dos de numeración vieja): los apéndices A y B
citaban `pso_grid_search.py`, `pso_grid_state.json` y `pso_grid_search.csv`, que son de la
aptitud **paralela F_apt** (columna `F_opt`, `m_opt` de 0,05 a 0,1117, diez radios
distintos); §5.3 atribuía a la propuesta «fidelidad estructural y limpieza» cuando tiene el
**peor SSIM del benchmark** (0,6584) y el segundo peor Nabf; la conclusión 2 publicaba
**SSIM = 0,739**, cifra que no está en ninguna fuente (es 0,7249); la primera recomendación
invocaba una «variante WTH+BTH directa» que no existe; §4.7 y §3.10 describían contrastes de
«configuraciones WTH» y de un «método anterior» inexistentes (los que se corren son once por
métrica, 99 en total); la conclusión 4 apoyaba el sesgo de la información mutua en un
«promedio simple» que no es del benchmark (es el brazo `base` de la ablación: MI_vis 1,3120 y
MI_ir 0,8537, las más altas de los seis, con la SD más baja, 0,1055); y **§5.6 y la conclusión
1 seguían con la numeración vieja de tres hipótesis**, la conclusión 1 afirmando «H3 no se
sostiene» cuando §5.8.2 dice literalmente «Se sostiene H3». También §1.2 y §2.1, que
prometían evidencia sobre una profundidad `L` y un radio base `r₀` que el operador no tiene.

**Deck** (29, 30, 34): el cuarto párrafo de la lámina 20 atribuía la mejora al «banco de SE y
el ajuste automático», contra lo que dicen las láminas 9 y 16; las láminas 13 y 19 decían
«ninguno adverso» cuando el contraste 25 sí es adverso en dirección y lo que le falta es
significancia (SD frente a la pirámide de Laplace, p_Holm = 0,231); y las láminas 8 y 9 tenían
texto **debajo** de una figura.

**Avances** (61, 67): reportaba el control de peso igualado como «de 3,961 a 4,711, gana por
0,683». El generador agregaba el clásico a peso igualado como **octavo brazo** del escenario B
dejando también al clásico con m = 1 en el pool, así que el operador clásico competía dos
veces y los siete rangos se diluían. El cálculo del libro es una **sustitución** dentro del
benchmark de siete y da 3,528 frente a 3,694. Y publicaba Fo = 1,6870 en m = 0,30, que es la
aptitud reconstruida con `evaluate_all`, mientras la Tabla 1 del propio informe, el libro y el
deck publican la del enjambre, 1,7057.

**README** (55): «solo la imagen fusionada permite detectar ambas a la vez», que el propio
README desmiente quince líneas más abajo (el VIS recupera ambas clases en el 53,0 % de las 232
escenas, más que la propuesta y más que cuatro de las siete fusiones).

### Dos defectos que no estaban en ninguna lista

1. **El flujograma del método estaba obsoleto DENTRO de los dos entregables.**
   `docs/figures/fig_flujo_propuesta.png` ya rotulaba «El PSO ajusta m; el radio es decisión
   de diseño → r = 25; m = 0,30», pero las copias embebidas —`word/media/image5.png` y
   `ppt/media/image-7-1.png`, el mismo md5 en las dos— seguían diciendo «PSO ajusta (r, m):
   barrido 5×5 → r = 25; m = 0,0703». Ese **0,0703 es el óptimo de la aptitud paralela**, no
   el peso adoptado, y atribuir r = 25 al PSO contradice la lámina 9 y §5.8.5. Se sustituyeron
   byte a byte (mismas dimensiones, 1309×1694).
2. **Texto tapado por figuras.** La lámina 8 tenía la segunda línea del título debajo del
   flujograma (26 % del span) y la 9 perdía el final de un renglón bajo el mapa de calor. En el
   PDF el texto **sigue estando** y se puede seleccionar, así que el chequeo de recorte no lo
   ve: hay que cruzar bboxes. Se acortó el título a una línea y se angostó el cuadro de la 9.

### Tres chequeos nuevos, para que no vuelvan

| Dónde | Qué comprueba | Discriminación comprobada |
|---|---|---|
| `verificar_entregables.py` bloque 9 | texto del pptx que no llega al PDF | 6 párrafos antes → 0 después; desalineando lámina y página marca 134 |
| `verificar_entregables.py` bloque 10 | texto debajo de una figura | 2 spans antes → 0 después; el umbral de 0,5 % separa los solapes reales de los roces de borde |
| `verificar_libro.py` bloque 8 | las **79** entradas del índice, no solo las seis de 5.8 | cazó §5.4 y §6.2 en el acto; con un corrimiento de una página marca 79 |

Además la lista de figuras por md5 pasó de 10 a **15**: el flujograma entró en las dos, y con
él `fig_morfologia_tophat.png` y `comparacion_aptitudes.png`. El barrido que encontró el
problema —para cada imagen embebida, buscar su gemela por md5 en `docs/figures`— dejó siete
imágenes «solas» en el libro y seis en el deck: son logos, la portada y las ecuaciones
renderizadas, **pero conviene mirarlas una vez** antes de darlas por buenas.

## Cerrado el 5 de agosto — el deck contra el estudio de estabilidad, y las citas huérfanas

Dos pedidos que parecían chicos y destaparon el triple. El relevamiento previo —en lugar de
editar directo las dos láminas conocidas— es lo que los encontró.

### El deck todavía argumentaba con el barrido de una sola semilla

El deck decía que el PSO devuelve `r = 1` «en 16 de las 25 configuraciones». Ese reparto sale
del barrido publicado, que corre **una semilla por celda**. Con 20 repeticiones por celda el
reparto se da vuelta: `r = 25` en el **51,4 %** de las 500 corridas y `r = 1` en el **45,6 %**.
Y la cuenta vieja además nunca cerró: 16 + 8 = 24, no 25 — la celda que falta (2 partículas ×
10 iteraciones) devuelve `r = 14` con Fo = 1,6990. Ese hueco existía desde antes del estudio.

Lo que caduca es la **frecuencia**, no el **argmax**: que `r = 1` maximice Fo dentro del rango
publicado sigue siendo cierto y es lo que sostiene H5. Con 228 contra 257 el argmax del PSO es
indistinguible entre los dos bordes, y eso **refuerza** H5: la búsqueda no fija el radio.

Seis lugares corregidos, no dos: cuerpo de las láminas 9, 19 y 20, la línea de contexto de la 9
y las notas del orador de la 9 y la 19.

- **La nota de la lámina 19 estaba literalmente invertida**: decía «la búsqueda devuelve
  `r = 1`», y lo que la búsqueda devuelve más seguido es `r = 25`.
- **La nota de la lámina 9 contradecía al informe.** Afirmaba que el óptimo `r = 25, m ≈ 0,07`
  es de la aptitud paralela `F_apt` y **no** de `F_o`. Es falso: en
  `optimo_exacto_fo.csv` el máximo global de Fo está exactamente ahí (1,771465), y la página 16
  del informe ya lo dice. `r = 1` es el argmax de Fo **restringido** a `m ≥ 0,30`. Las dos
  aptitudes pican en `m ≈ 0,0703` (`curva_aptitud_vs_m.csv`). Era texto anterior a que se
  corriera la enumeración exacta.
- **El título de la figura incrustada** decía «todas convergen a m\* = 0,30». Cierto de esas 25
  celdas, pero al lado de las 500 corridas sonaba a propiedad del optimizador. Ahora dice «una
  semilla por celda» y declara que el resaltado marca `r* = 1`, que antes no se decía.
- **Encuadre**: el párrafo de la lámina 9 desbordaba la caja al crecer, y el `%` con espacio
  normal quedaba huérfano al principio del renglón. 17 porcentajes pasaron a espacio duro.

### Cuatro citas sin entrada en la bibliografía, no dos

- **Redmon et al. (2016)** y **Jocher et al. (2023)**, citados en la sección 12 del informe.
  Agregados al capítulo 7, que pasa de 36 a **38 entradas**. La de Jocher cita la versión 8.0.0
  —la que los autores publican— y el informe declara aparte la 8.4.68 con la que se corrió; la
  sección 12 ahora lo aclara para que no se lean como contradicción.
- **Bai et al. (2015)** y **Wang et al. (2017)** en el párrafo 235 del libro: residuo de la
  auditoría, que corrigió esas entradas a **2012** y **2014** por DOI sin propagarlo al cuerpo.
  **No se arreglan cambiando el año**: la oración decía «Trabajos posteriores, como los de…»
  justo después de citar a Bai (2013), y 2012 es *anterior* a 2013. Se reescribió describiendo
  cada trabajo por lo que es —el de 2012 es de realce, no de fusión; el de 2014 usa
  representaciones dispersas, no Top-Hat— y conservando el argumento del hueco.
- **Toet (2014)** en la lámina 10 del deck, el dataset TNO. La entrada correcta es Toet (2017).
  El año 2014 ya estaba en `RETIRADAS`, pero como la cadena lleva la inicial
  (`Toet, A. (2014)`), la forma corta del deck sobrevivía. Lo encontró el chequeo nuevo.

### Dos chequeos nuevos

| Dónde | Qué comprueba | Discriminación comprobada |
|---|---|---|
| `verificar_entregables.py` bloque 12 | las formulaciones retiradas del barrido, con regex cruda y **leyendo el pptx** | los 4 patrones marcan el pptx viejo → 0 en el nuevo. **Dos dan 0 en el PDF**: viven sólo en las notas del orador |
| `verificar_entregables.py` bloque 13 | toda cita en texto tiene entrada en la bibliografía | 5 huérfanas en la versión vieja (2 libro, 2 informe, 1 deck) → 0 ahora |

El bloque 12 va con regex cruda porque `afirmada()` **no** podía verlo: el «no r = 25» que
precede a «que aparece en 8» cae en su ventana de 90 caracteres y la negación lo anulaba, o sea
falso negativo garantizado. Y el bloque 13 no existía en ninguna forma: `verificar_bibliografia.py`
valida el sentido inverso —que lo listado exista en Crossref—, nunca que lo citado esté listado.

Un patrón se probó y **se descartó a propósito**: vigilar «las 25 configuraciones convergen al
mismo peso» marcaba tres afirmaciones **legítimas** —libro, informe y README— donde la frase
habla de las 25 celdas del barrido publicado, y eso es verdad. En el deck se reescribió por
precisión, no por error. Un chequeo así forzaría a reescribir texto correcto.

## Cerrado el 5 de agosto (tarde) — las notas del orador, las 15 que faltaban

Quedaban 15 láminas con notas sin revisar (18 tienen; ya estaban hechas la 9, la 18 y la 19; las
láminas 4, 6, 14, 15 y 16 no tienen). **Once defectos en nueve láminas.** Todas las cifras que las
notas nuevas escriben se recalcularon contra los CSV antes de escribirlas.

Esto importa más de lo que parece: **las notas no se imprimen en el PDF**, así que ningún
verificador las miraba hasta el bloque 12. Se leen en voz alta frente a la mesa.

| Lámina | Decía | El problema |
|---|---|---|
| 1 | «la tesis propone y **valida** un método…» | encuadre de UN aporte, anterior al reencuadre a dos. La lámina 4 dice «la tesis no sostiene que el método sea mejor» |
| 5 | «un objetivo general y **cuatro** específicos» | su propia lámina lista **cinco**. El que se pierde es OE4, la auditoría de la batería — la mitad del segundo aporte |
| 8 | «El PSO (caja punteada) calibra **r y m**» | el flujograma de esa misma lámina dice «el radio es decisión de diseño». Lo contradice su propia figura, la lámina 9 y H5. `Plan_Deck_Defensa.md` ya prescribía el cambio y nunca se aplicó |
| 11 | «con **menos halos y ruido** que RP/DWT» | **falso y al revés**: Nabf 0,374 de la propuesta contra 0,224 de RP y 0,241 de DWT. Contra el Top-Hat clásico sí es más limpia (0,374 contra 0,586) |
| 12 | «si se recuerda la versión anterior de esta nota…» | instrucción sobre el historial del material, inútil frente a la mesa |
| 13 | «sostiene las ventajas donde la propuesta las reclama: **limpieza y estructura**» | es exactamente el bloque donde **pierde**: 17 de 20 contrastes adversos en fidelidad. Lo que la estadística respalda es la actividad espacial (24 de 25) |
| 17 | «entre fusiones las diferencias son **pequeñas**» | la propuesta queda 0,046 por debajo de la mejor fusión — la mitad de lo que la fusión le gana al visible (0,813 → 0,906–0,952) |
| 20 | «**óptimo hallado**» | es justo lo que H5 niega |
| 23 | «invisibles para el detector en VIS» · «el IR no los ve» | las dos escenas estaban mal descriptas. El visible detecta **3 de 10** personas en 00389; el infrarrojo detecta **1 de las 5** luces en 00231 (AP@0,5 Lamp = 0,348), o sea que se degrada pero no es ciego |

Dos ajustes propios sobre lo que salió de la revisión: en la 23 se aclara que los conteos son
**detecciones sobre el umbral y no aciertos emparejados** —la fusión da 7 lámparas donde la verdad
de campo tiene 5, y decirlo evita la pregunta—, y la nota de la 11 se acortó, porque venía
larguísima para un apunte de hablar.

Las notas nuevas **citan** la frase retirada dentro de una instrucción `NO decir «…»`. Es
deliberado —el orador puede tener memorizada la redacción vieja— y es el estilo que ya usaba
`Plan_Deck_Defensa.md`. Efecto colateral: obligó a agregar `'NO '` a `NEGADORES` en
`verificar_entregables.py`, que reconocía `'no '` y `'No '` pero no la mayúscula, con lo cual
cualquier frase de `RETIRADAS` citada así se habría reportado como afirmada. El cuerpo de la
lámina 19 ya tenía el mismo patrón («La optimización NO determina…»).

El PDF del deck **no se regeneró**: se comprobó que ninguna de las cifras nuevas llega al PDF,
porque las notas no se imprimen.

## Cerrado el 5 de agosto (noche) — las cinco láminas que no tenían notas

Las láminas 4, 6, 14, 15 y 16 eran las únicas sin notas del orador. Tres de ellas —14, 15 y 16—
son las de la auditoría del criterio: el segundo aporte, la parte que más preguntas atrae, con
1:30, 1:20 y 1:00 de exposición asignados y sin apunte escrito.

**`Plan_Deck_Defensa.md` ya traía las cinco redactadas; nunca se aplicaron.** Se verificaron contra
el estado actual antes de escribirlas, y **tres afirmaciones del plan resultaron falsas**:

| Lámina | El plan decía | Por qué no va |
|---|---|---|
| 14 | «ambos experimentos están versionados en `run_control_negativo.py`» | **Falso.** Ese script no contiene `avg_rank_sin_FE`, ni `friedman`, ni `chi2`: la redundancia de FE la produce `run_stats_analysis.py`. Mandaba al orador a citar el archivo equivocado ante la mesa |
| 15 | «si alguien cita el libro diciendo que cae al **quinto lugar**, es una errata» | **Vencida.** El libro (p. 62) ya dice «desciende al **tercer** lugar (3,821), por detrás de la pirámide de Laplace (3,141) y de DTCWT (3,362)». Lo mandaba a defenderse de un error que ya no existe |
| 15 | «a peso igualado la propuesta gana **con holgura**» | Son **0,166** — 3,528 contra 3,694. Se da la cifra |
| 4 | «el propio libro declara la **circularidad del radio**» | La palabra no aparece en ninguno de los dos documentos, y H5 va sobre los **dos** hiperparámetros. Lo que el rango heredado fija por completo es el **peso** (m = 0,30 en 499 de 500); con el peso libre r = 25 es el óptimo exacto de Fo. Decirlo al revés regala un flanco |

El deck queda con **notas en las 23 láminas**.

### Un defecto del informe que salió de rebote

Verificando la nota de la lámina 14 apareció que el informe publicaba, en **dos** lugares (p. 21 y
§16), que el ruido «alcanza el segundo puesto entre **ocho** entradas». Es de una corrida
anterior: el control negativo tiene hoy **14 entradas** —los 7 métodos, la imagen base, 4 fusiones
de ruido y 2 desenfoques— y el ruido de σ = 0,20 queda **3.º**, con 5 de los 6 comparativos
detrás. Las dos frases estaban escritas a mano.

No se corrigieron a mano: `make_avances_report.py` ahora **carga `control_negativo_ranking.csv`** y
deriva el ordinal, el total de entradas, el rango y cuántos comparativos quedan detrás. Así no
vuelve a envejecer, que es la misma disciplina que el resto del informe.

## Cerrado el 7 de agosto — por qué la referencia dispersa y esta tesis converge

Consulta del autor: «¿por qué las 500 corridas no funcionan en nuestro proyecto y en el de las
chicas sí?». **La premisa estaba dada vuelta y conviene tenerlo claro para la defensa:** convergencia
es el resultado bueno; dispersión significa que el optimizador no pudo decidir. Las 500 corridas
funcionaron — contestaron que el peso es robusto (499 de 500 en el piso), que el radio no lo fija
la búsqueda (51,4 % contra 45,6 %, que es H5) y que más corridas no pueden mejorar nada porque la
aptitud es determinista y hay 25 radios enteros.

Se agregó la **Tabla 3f** (página 18), que es la comparación manzana con manzana que faltaba. El
estudio de estabilidad optimiza sobre tres imágenes con veinte semillas, o sea mide dispersión
**entre semillas**; la referencia optimiza **por escena**, 5 × 25. El comparable es el barrido por
imagen, 20 × 25:

| | Referencia (disco único) | Esta tesis (banco) | Esta tesis, piso 0,01 |
|---|---|---|---|
| Mediana de m* | 0,6950 | **0,3000** | 0,0436 |
| Corridas en el piso | 13,6 % | **96,6 %** | 38,2 % |
| Radio modal | r = 25 | r = 1 | **r = 25** |
| Corridas con r* = 25 | 83,2 % | 27,2 % | **67,6 %** |

Con el **mismo** rango los dos operadores se comportan al revés; al bajar el piso, el banco se
comporta como el disco. La razón es física y está medida: el banco extrae **4,21 veces** la energía
de detalle del disco, así que la mediana 0,695 que la referencia elige equivale a **m = 0,165** en
este operador — **por debajo del piso 0,30** que ambos heredan. El piso no es un piso para este
operador: está ya pasado el óptimo.

### Un CSV que venía de otro corpus

Armando esa tabla apareció que `pso_por_imagen_libre.csv` tenía **19 imágenes y no 20**: le faltaba
`Triclobs_Kaptein_1123`, el par que sustituyó al corrupto `Athena_heather_IR_hei_vis`. Se había
corrido el 29/07 a las 15:22, **antes** de la sustitución; el otro barrido es de las 19:21. O sea
que la tabla habría comparado columnas de **corpus distintos**, y desde el texto no se ve: las dos
columnas parecen homólogas.

Se recalculó (500 corridas, 20 imágenes) y las cifras casi no se movieron —piso 38,2 % contra el
40,0 % anterior, r = 25 en 67,6 % contra 68,0 %—, así que la conclusión aguanta. Y
`make_avances_report.py` ahora lleva un **assert** que compara los conjuntos de imágenes de los dos
barridos y no deja compilar el informe si difieren.

**Conviene revisar si hay más CSV anteriores al 29/07 19:21**, que es cuando se sustituyó el par:
cualquiera de esa fecha o anterior está sobre el corpus de 19.

## Cerrado el 8 de agosto — la auditoría del informe de avances

Se auditó el informe desde cuatro ángulos (estructura, trazabilidad de las cifras, defensibilidad
ante la mesa, presentación) y se cerraron las cinco primeras prioridades. **Todo lo que sigue se
verificó contra el PDF o el CSV antes de tocarlo**, y la auditoría misma descartó cinco hallazgos
suyos por no sostenerse.

| Qué | Estado |
|---|---|
| **La contradicción del argmax.** La p. 19 decía que r = 25 es «la que la optimización elige» y la conclusión 4, cuarenta páginas después, «el argmax de la aptitud es r = 1» — **sin el calificador de rango**. Las dos ciertas en su marco, escritas como la misma afirmación | corregido |
| **El Anexo publicaba «18 radios distintos y entre 2 y 6 por par»**; el CSV vigente da **17** y **2 a 5**. Del corpus anterior a la sustitución del par corrupto | derivado del CSV |
| **«Con separación estadísticamente significativa»** — no existía ningún test sobre rangos agregados | retirado |
| **«Con muestra suficiente»** (×2) — el contraste es un McNemar exacto con **p = 0,2100**, o sea que no rechaza | reemplazado por la potencia medida |
| **`ranking_methods.csv` trae tres agregaciones** y el informe leía sólo la que más favorece. Con la tercera hay **empate exacto** con Laplace en 3,556 | publicadas las tres |
| **No enunciaba objetivos ni las siete hipótesis**, y usaba «H5» tres veces sin referente | página 3 nueva |
| **El «24 de 25» de las conclusiones** no se derivaba en el cuerpo (§9 contaba 31/19/4, otro corte) | derivado por bloques |
| **El PSO se ajusta sobre 3 de los 20 pares que evalúa**, sin declarar | declarado en §5 |
| **El libro atribuía r = 25 al PSO en cinco lugares** | corregido |

### La potencia del contraste de H6

`experiments/potencia_mcnemar.py`. El test condiciona en los pares discordantes y son **23** (8 a
favor de la propuesta, 15 del visible). Con esos 23 y α = 0,05 la potencia llega a 0,80 recién a
partir de **5,8 puntos porcentuales**; para la diferencia observada de 3,0 puntos es **0,26**. Lo
que queda descartado es una ventaja de 5,8 puntos o más, **no una ventaja de cualquier tamaño**.

El script construye la región de rechazo evaluando el mismo `binomtest` que el informe reporta, no
con una fórmula cerrada, y lleva dos controles: que el nivel real no pase de α (da 0,0347) y que la
potencia con δ = 0 coincida con ese nivel.

### Dos huecos del informe que el mapeo de hipótesis destapó

- **La correlación de rangos entre calidad y tarea —el instrumento de H6— no aparece ni una vez** en
  las 82 páginas. Ni «Spearman», ni el ρ, ni sus valores. Lo que sostiene el rechazo es el conteo
  por escena de §14 con su análisis de potencia.
- **El control negativo de H3** se resume pero no se desarrolla: está en el libro §5.8.2.

Los dos quedan **declarados** al pie de la Tabla 1a, en lugar de dejar que la tabla prometa un
desarrollo que el documento no tiene.

### Lo que la auditoría dijo que NO hay que tocar

> «La autocrítica es el activo defensivo más fuerte que tenés, y es infrecuente. El informe se
> ataca a sí mismo más duro de lo que lo hará la mesa.»

El control negativo con ruido llegando al 3.º puesto de 14; la caída al 3.º con las diecisiete
métricas; que la calidad no se traslada a la detección; que ninguna fusión supera al infrarrojo
solo; la errata de la ecuación (29) declarada de frente. **No suavizar nada de eso.**

## Cerrado el 8 de agosto (noche) — los diez `A_LEER` que faltaban

Con esto la reverificación queda en cero. **Cinco eran defectos reales y cinco no lo eran**, y las
dos mitades importan por igual: dejar un hallazgo como `A_LEER` para siempre es tan malo como no
haberlo mirado.

### Los cinco que sí lo eran

| # | Qué | Dónde |
|---|---|---|
| **n65** | El libro reportaba las métricas de M3FD «sobre 499 imágenes de **validación**», y esos 499 son la partición de **prueba**. `prepare_m3fd.py` dice literalmente que la validación se usa para elegir el checkpoint y **«nunca se reporta»**: el libro decía reportar sobre el conjunto que su propio diseño declara no reportar | libro, 4 pasajes |
| **n106** | `avg_rank_medias` rankeaba las medias **ya redondeadas** a cuatro decimales, lo que inventaba empates: daba RP 4,167 y DWT 4,500 donde corresponde 4,111 y 4,556 | `run_stats_analysis.py` |
| **n94** | SF es la única de las nueve que el evaluador calcula sobre **0–255**, y el libro no lo declaraba: aplicar la ecuación (17) a una imagen en [0, 1] devuelve el valor **dividido por 255** | libro, §4.4 |
| **n93 / n96** | El comentario de `PARES_EXCLUIDOS` decía «19 pares» (son 20), y el docstring de `comparatives.py` listaba un «Promedio simple» que no existe | código |
| **n53 / n56 / n57** | El README omitía `dtcwt` de las dependencias —sin él DTCWT lanza `ImportError`—, decía «Tres controles» listando **cinco**, y su árbol no incluía `experiments/detection_m3fd/` | README |

El n106 tocaba algo que el informe publica: la columna del empate. **El empate 3,556 entre la
propuesta y la pirámide de Laplace se sostiene en las dos versiones**, así que la Tabla 6a no cambia.

### Los cinco que no lo eran

n30 y n34 (deck), n44 (informe), n73 (libro) y n51 (README) ya estaban aplicados o el pasaje que
quedaba era correcto. El triador los marcaba porque **su heurística compara subcadenas**: si la cita
del hallazgo sigue apareciendo, da el pasaje por vivo, y eso no distingue «no se corrigió» de «era
correcto y la aclaración se agregó en otra parte». Cuatro de los cinco eran un **prefijo de la frase
ya corregida**.

Eso no se arregla con más regex. Se agrega `docs/fuentes/resueltos.json`: por hallazgo, la fecha del
cierre y **por qué**, incluidos los que se leyeron y resultaron no ser defectos. `triar_hallazgos.py`
lo lee y les pone estado `RESUELTO`, y el registro gana sobre la heurística porque es una lectura
hecha con su razón escrita.

## Pendientes, por prioridad

### 1. ~~Los quince hallazgos `A_LEER`~~ — cerrado

```
.venv\Scripts\python.exe -X utf8 experiments/triar_hallazgos.py
```

Ninguno es `PENDIENTE`: el triador no pudo decidirlos por máquina y exigen leer. Tres ya
están aplicados y quedan marcados así por el modo en que el triador busca —[30] porque el
texto nuevo **contiene** el viejo como subcadena («…ninguno adverso **con significancia**»),
[34] porque describe un estado visual y no una cadena, y [51] porque su cita es demasiado
corta para ubicarla. Los **doce** que de verdad faltan leer:

| n | doc | gravedad | dónde |
|---|---|---|---|
| 44 | avances | sobreafirmado | p. 3 y Tablas 4a-4e |
| 75 | avances | incoherente | §5.6 y p. 55 |
| 65 | libro | incoherente | p. 53, §5.5, detección con clases |
| 73 | libro | desactualizado | §3.3, §3.6, §1.2 y conclusiones |
| 94 | libro | incoherente | ecuación (17), frecuencia espacial |
| 99 | deck | desactualizado | lámina 10, diseño experimental |
| 53 | readme | incoherente | §10 Dependencias |
| 56 | readme | menor | §3.1, línea 316 |
| 57 | readme | menor | §4, bloque de `experiments/` |
| 93 | código | desactualizado | comentario de `PARES_EXCLUIDOS` |
| 96 | código | menor | docstring de `comparatives.py` |
| 106 | — | menor | columna de `ranking_methods.csv` |

**Criterio de trabajo, que conviene mantener:** verificar cada hallazgo ejecutando el cálculo
antes de escribir. De 24 verificados hasta ahora, 24 resultaron reales — pero los agentes
también entregaron cifras equivocadas (el conteo de `r_opt`, que es 16 de 25 y no 18; el
margen a peso igualado; y el plan del deck, que dice «cuatro hallazgos sobre el criterio»
cuando la lámina 6 etiqueta **cinco**). Donde el hallazgo describa un experimento inexistente:
poner el resultado medido, o retirar la afirmación.

### 3. Bibliografía: dos localizadores incompletos

- **Bajac Figueredo et al. (2024)**, el paper propio del CNMAC: faltan volumen,
  páginas y DOI. Están en la página de las actas de la SBMAC (la serie usa DOI de la
  forma `10.5540/…`). No figura en Crossref.
- **Flores et al. (s. f.)**, el antecedente de mamografías: falta saber si ya se
  publicó, y con qué datos. Preguntar a los coautores de la FPUNA.

Las otras 34 entradas están verificadas. El informe está en
`docs/Auditoria_Bibliografia.md`.

**`docs/fuentes/entradas.json` quedó desfasado, y por eso `verificar_bibliografia.py` grita en
falso.** Ese script no lee el `.docx`: lee ese JSON, que es una instantánea congelada del 2 de
agosto con **33** entradas y los datos **previos** a las correcciones de la auditoría. Todavía
dice Bai 2015, Mukhopadhyay 2001, Toet 2014 y Wang 2017 —los cuatro ya corregidos en el libro, y
Crossref le da la razón al libro—, le faltan Kingsbury (2001), Bajac Figueredo et al. (2024) y
Flores et al. (s. f.), y ahora también Redmon y Jocher. De sus «10 con defectos», cuatro son el
JSON viejo y no el libro.

Trampa al sincronizarlo: `LIBROS = {8, 21, 24}` y `SIN_DOI = {18}` son índices **posicionales**
1-based sobre ese JSON. Insertar entradas en orden alfabético los corre y los rompe en silencio.
Hay que pasarlos a clave apellido+año antes de agregar nada.

No se tocó en esta sesión a propósito: sincronizarlo implica revalidar contra Crossref (tarda
minutos y necesita red), y el cruce citas-contra-bibliografía que hacía falta ya quedó cubierto
por el bloque 13 de `verificar_entregables.py`, que toma como autoridad **el listado impreso del
propio libro** en lugar del snapshot. Queda como decisión: sincronizar el JSON, o retirarlo y
hacer que `verificar_bibliografia.py` lea el `.docx`.

`docs/Auditoria_Bibliografia.md` afirma en su §1 que «el cruce en ambas direcciones no encontró
citas huérfanas ni entradas sin citar». **Eso dejó de ser cierto por sus propias correcciones**:
había cinco. Conviene corregir esa frase del informe de auditoría.

### 3 bis. Lo que venía en los documentos que se archivaron

Al mover nueve documentos de trabajo a `docs/historial/` aparecieron **tres pendientes abiertos que
no estaban en ningún otro lado**. Se traen acá, porque archivar sin migrarlos los enterraba.

- **La negrita de la Tabla 10 del libro significa otra cosa que en las demás.** En las Tablas 4, 5 y
  7 marca el mejor valor de cada columna; en la 10 marca la columna del método propuesto. Hace falta
  una nota al pie que lo aclare. Verificado que sigue abierto: **ninguno de los 518 párrafos del
  libro contiene la palabra «negrita»**. Venía de `Reverificacion_Informe.md`, cuyo único contenido
  útil era éste.
- **El reglamento de la UCOM: nueve requisitos de formato sin verificar** (márgenes, interlineado,
  numeración, tipografía y demás). Están inventariados en el §6 de
  `historial/Informe_Revision_Mesa_Examinadora.docx`, con los valores medidos sobre el libro, que
  siguen valiendo. **Ningún script los mide**: el grep de `interlineado`, `line_spacing` y
  `left_margin` sobre los `.py` no encuentra nada. Es un pendiente externo, del reglamento, no del
  contenido.
- **Validar con el director la reducción de alcance.** El `Plan_Replanteo_TFM.docx` acordado en junio
  preveía tres detectores y se entregó con uno. La decisión está tomada y justificada, pero conviene
  que conste que el director la conoce. Es gobernanza, no técnica.

### 3 ter. La carilla de resumen del informe, y dos defectos que aparecieron al hacerla

El informe de avances lleva ahora una **carilla de resumen en lenguaje llano en la página 2**, antes
del índice, que es lo primero que lee el director: el problema, qué se propone, cómo se evaluó, qué
salió, qué no salió, las tres diferencias con el plan de junio que necesitan su visto bueno, qué
falta y a qué página ir. El documento pasó de 84 a **85 páginas numeradas**.

Meterla al frente corrió toda la numeración en uno. No fueron ochenta y cuatro ediciones: los pies
de la 3 a la 32 son literales, pero de la 33 al final los gobierna **un solo `pg = 33`** que
veintiún `pg += 1` van avanzando. Las sustituciones se hicieron **en orden descendente**, porque
ascendentes convertirían `pie(3)` en `pie(4)` y la pasada siguiente encontraría dos.

Se instaló un **guardián** en el generador: la secuencia de pies del HTML ensamblado tiene que ser
exactamente 2, 3, 4, …, N, sin huecos ni repetidos, y si no lo es **no escribe ni el HTML ni el
PDF**. Se probó que discrimina reconstruyendo el defecto real —la carilla insertada sin renumerar— y
abortó con `faltan [85] · repetidos [2]`, sin tocar el entregable. Y el **bloque 22** del verificador
cierra la otra puerta: la carilla **no puede estrenar ninguna cifra**, todo decimal que cite tiene
que aparecer con ese mismo redondeo en otra página del cuerpo, y cada remisión «sección N (pág. M)»
tiene que caer en la página cuyo encabezado empieza con «N.».

Dos defectos aparecieron en el camino:

- **El Anexo 19 del informe salía con el nombre crudo del archivo**, «Triclobs_Kaptein_1123», donde
  las otras diecinueve escenas llevan nombre legible. El diccionario `ESCENA` del generador seguía
  nombrando el par corrupto retirado y no tenía el que lo sustituyó. El `.get(img, img)` no falla
  nunca, así que nada lo delataba. El **bloque 21** ahora exige que los diccionarios de nombres de
  escena cubran el corpus vivo y no nombren nada de afuera; sobre el diccionario de antes marca las
  dos cosas.
- El chequeo del índice leía la **segunda página física** en lugar de buscar el índice, así que al
  meter la carilla empezó a leer el resumen e informó que el índice citaba «1 de los 37 comienzos de
  sección». El fallo era del chequeo. Ahora la busca, y de paso comprueba que **el resumen venga
  antes del índice**, que es su razón de ser.

Y un defecto que el archivado destapó, ya corregido: **`make_reporte_optimos.py` escribía su PDF en
`docs/`**, así que el documento archivado habría vuelto a aparecer arriba, con pinta de vigente, la
próxima vez que alguien corriera el script. Además su diccionario de nombres de escena todavía
nombraba el par corrupto retirado y le faltaba el que lo sustituyó, `Triclobs_Kaptein_1123`. Se
arreglaron las tres cosas, se regeneró el PDF con el corpus de 20 pares y el **bloque 20** de
`verificar_entregables.py` ahora comprueba las dos caras: que en `docs/` raíz sólo estén los nueve
archivos declarados, y que ningún script escriba ahí fuera de esa lista. Se comprobó que el chequeo
**discrimina**: marca la línea vieja y deja pasar la nueva, sobre nueve casos límite.

### 4. Decisiones del autor

- **`docs/_local` (44 MB)**: diez instantáneas fechadas del libro, un `BACKUP_actual` y
  un estudio de 14 MB. **Ninguna está en git, así que borrarlas es irreversible.**
  Recomendación: dejarlas, o borrar solo las `_pre_*`.
- **DOI del resto de la bibliografía**: 15 de 36 entradas lo llevan. APA 7 los pide
  todos y hay 21 más verificados, pero completarlos depende del reglamento de la UCOM,
  que sigue siendo el pendiente externo.
- **Notas del orador del deck**: ~~pendiente~~ **cerrado el 5 de agosto**. Las **23 láminas**
  tienen notas y todas quedaron verificadas contra el cuerpo de su lámina y contra los CSV. De las
  18 que ya tenían, 14 traían defectos; las 5 que no tenían se escribieron desde lo que el plan
  había dejado redactado, corrigiendo cuatro afirmaciones suyas que no se sostenían.
- **Banda base de la pirámide de Laplace**: el comparativo fusiona su banda base por
  máxima actividad en lugar de promediarla. Declarado en las limitaciones; corregirlo
  cambiaría los resultados de LP.

## Lo que hay que saber para no repetir errores

El patrón de todo el proyecto fue **texto y figuras copiados entre documentos que
después divergen de los datos**. Apareció en el libro, en el deck, en los montajes
cualitativos, dos veces en el README, en las negritas de las tablas y en el abstract
en inglés. Cinco lecciones que costaron caro:

1. **Las figuras eran imágenes con las cifras grabadas y sin generador.** Ahora las
   nueve de datos se generan desde los CSV (`make_figuras_libro.py`,
   `make_figuras_deck.py`) y los generadores afirman sobre los datos antes de dibujar:
   el del ranking falla si el primer puesto no es la propuesta.
2. **El formato también miente.** Las negritas de las Tablas 4, 5 y 7 seguían marcando
   la celda que era óptima con los valores anteriores; en la Tabla 7 señalaban a la
   pirámide de Laplace como líder, la conclusión que el capítulo desmiente.
3. **El abstract en inglés sobrevivió trece cifras obsoletas** porque la lista negra
   del verificador estaba escrita con coma decimal y el inglés usa punto.
4. **Buscar una cadena no alcanza para detectar una afirmación retirada**: el texto
   corregido dice «no hay patrón espejo», «el infrarrojo no es ciego». Hay que mirar la
   negación, y en el README también los marcadores de Markdown (`**no**`).
5. **El Marco Conceptual y las conclusiones describían un método anterior** —Top-Hat
   multiescala, elementos cuadrado y de cruz, profundidad L, radio base r₀, variante
   sin Black Top-Hat—, es decir experimentos que nunca se corrieron. Eso ningún
   verificador automático lo detecta: exige leer.

---

## Lo que nunca se revisó (agregado al cierre)

Distinto de los pendientes de arriba: esto no está en la lista de hallazgos porque
nadie lo mira todavía.

1. **El Excel** (`docs/Avances_Tesis_Tablas.xlsx`, 12 hojas). Es un entregable
   rastreado y ningún verificador lo cubre. Se regeneró en esta sesión y aun así
   contiene `3.67` y `0.913`, las dos cifras retiradas del ranking y del mAP: hay que
   revisar si `make_avances_excel.py` las calcula de una fuente vieja o las tiene
   escritas. **Extender `verificar_entregables.py` al Excel es la mejora de mayor
   rendimiento que queda.**
2. **Los notebooks** (`notebooks/01` EDA y `03` estadístico). No se abrieron en toda la
   sesión; pueden contener cifras y conclusiones de corridas anteriores.
3. **Las Figuras 1 a 6 del libro.** No llevan cifras, así que no pueden contradecir a
   los datos, pero se dibujaron para el método anterior. Dado que el Marco Conceptual
   describía un Top-Hat multiescala con elementos cuadrado y de cruz, conviene mirar si
   la Figura 2, la 3 o la 4 dibujan una cascada multiescala o geometrías que el
   operador no usa.
4. **La variante `libre`** (`metrics_reports_libre/` y su informe). Es un conjunto
   paralelo completo de resultados, nunca auditado. Si no se va a defender, conviene
   decidir si se archiva o se retira.
5. **Cumplimiento del reglamento de la UCOM**: márgenes, portada, estilo de cita,
   orden del frontmatter. Es el pendiente externo y nadie lo verificó.
6. **La implementación de los comparativos**, más allá de la banda base de la pirámide
   de Laplace ya declarada. Nadie auditó LP, RP, DWT, DTCWT ni la aproximación CVT
   buscando otros defectos.
