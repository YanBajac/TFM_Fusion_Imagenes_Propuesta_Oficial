# Estado y pendientes — 4 de agosto de 2026

Punto de retomada. Todo lo que sigue está verificado; lo que no, está marcado como tal.

**Los 106 hallazgos de la reverificación quedaron en 0 PENDIENTE: 91 aplicados y 15 que
solo se pueden decidir leyendo.** El detalle de los quince está más abajo.

## Cómo correr las cosas

Las dependencias viven en `.venv`, **no** en el Python del sistema:

```
.venv\Scripts\python.exe -X utf8 experiments/<script>.py
```

Tres verificadores, todos en 0 fallos al cierre:

| Script | Qué comprueba |
|---|---|
| `verificar_entregables.py` | los cuatro entregables contra los CSV: medias, ranking, detección, afirmaciones retiradas, coherencia entre documentos, **quince** figuras embebidas por md5, montajes, paginación, el texto del deck que el PDF recorta y el texto que queda **debajo** de una figura |
| `verificar_libro.py` | el libro en detalle: cifras retiradas, medias, rangos, detección, sección 5.8, **las 79 entradas del índice** y las cinco figuras embebidas |
| `triar_hallazgos.py` | reparte los 106 hallazgos de la reverificación en YA_APLICADO / A_LEER / PENDIENTE; acepta `--gravedad` y `--doc` |

El libro se edita con **python-docx** cuando el cambio es de texto: los párrafos del cuerpo
tienen un solo run, así que basta `p.runs[0].text = ...` y `doc.save()`. Después, PDF por
LibreOffice:

```
"C:\Program Files\LibreOffice\program\soffice.exe" --headless --convert-to pdf --outdir docs docs\Tesis_Borrador_V3.docx
```

**Al terminar hay que revisar el índice**: es texto fijo, no un campo de Word, y un párrafo
más largo mueve un salto de página y lo desfasa en silencio. Pasó dos veces el 4 de agosto
—§5.4 de la 49 a la 50 y §6.2 de la 65 a la 66— y las dos las cazó el bloque 8 de
`verificar_libro.py`, que ahora comprueba las 79 entradas y no solo las seis de 5.8.

## Estado de los entregables

| | | |
|---|---|---|
| Libro | 73 pág. | 36 referencias auditadas, sección 5.8 de auditoría del protocolo |
| Deck | 22 láminas + reserva | |
| Avances | 60 pág. | |
| README | 563 líneas | |

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

## Pendientes, por prioridad

### 1. Los quince hallazgos `A_LEER`

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

### 4. Decisiones del autor

- **`docs/_local` (44 MB)**: diez instantáneas fechadas del libro, un `BACKUP_actual` y
  un estudio de 14 MB. **Ninguna está en git, así que borrarlas es irreversible.**
  Recomendación: dejarlas, o borrar solo las `_pre_*`.
- **DOI del resto de la bibliografía**: 15 de 36 entradas lo llevan. APA 7 los pide
  todos y hay 21 más verificados, pero completarlos depende del reglamento de la UCOM,
  que sigue siendo el pendiente externo.
- **Notas del orador del deck**: escritas por lámina en `docs/Plan_Deck_Defensa.md`, con
  presupuesto de tiempo para los 20 minutos. Se aplicaron las de la 18 y la 19, que
  decían lo contrario de su lámina; **las demás siguen sin revisar**, y el precedente dice
  que hay que compararlas una por una con el cuerpo de su lámina.
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
