> **DOCUMENTO ARCHIVADO — no describe el estado actual del proyecto.**
>
> Auditoría ya cerrada: sus nueve defectos están corregidos en el código. **Todas sus cifras son de otro corpus**, el de 19 imágenes, anterior a la sustitución del par corrupto. Se conserva porque es la trazabilidad forense que la sección 5.8 del libro usa sin reproducir, y porque `.gitignore` la designa como el registro del contenido de los respaldos `*.bak_*`.
>
> El estado vigente está en `../ESTADO_Y_PENDIENTES.md` y en los entregables.

---

# Auditoría interna del pipeline experimental

_Revisión en seis dimensiones (integridad de datos, métricas, estadística, optimización, detección y consistencia documental) con verificación adversarial de los hallazgos más graves. 64 hallazgos; 7 de los 8 verificados sobrevivieron al intento de refutación. Todo lo afirmado fue comprobado ejecutando código sobre el repositorio._

---

Auditoría en seis dimensiones más una ronda de refutación adversarial. Todo lo que sigue fue verificado ejecutando código sobre el repositorio, no inferido. Cuando un hallazgo del auditor no sobrevivió a la refutación, lo digo explícitamente.

**Veredicto en una línea.** La implementación del operador, de las métricas y de la maquinaria estadística es sólida y reproducible; lo que está roto es **el criterio de validación** (el conjunto de nueve métricas no distingue detalle de ruido y contiene una métrica duplicada), **un dato de entrada** (un par corrupto), **la atribución del radio r=25 al PSO** (falsa) y, sobre todo, **el experimento de detección M3FD**, que es precisamente el que debería sostener el objetivo declarado de la tesis y no lo sostiene.

---

## 1. Qué está roto y hay que corregir antes de defender

Ordenado por gravedad = (impacto sobre las conclusiones publicadas) x (probabilidad de que el jurado lo pregunte).

### R1 — CRÍTICO. El detector de M3FD es el de la época 1 de 40, y la conclusión titular depende de ese checkpoint

Es el defecto más grave porque afecta al experimento que sostiene el objetivo de la tesis.

Evidencia directa (no inferida): cargué `runs/detect/runs/m3fd/mixto/weights/best.pt` y sus `train_metrics` son idénticos dígito a dígito a la fila `epoch=1` de `results.csv` (mAP50=0,21621, mAP50-95=0,11647, fitness=0,11647), con fecha 16:13:35 sobre un entrenamiento que terminó a las 16:49:16. `last.pt` lleva las métricas de la época 40 (0,18776 / 0,09741). `args.yaml` confirma `patience: 100`, o sea que se entrenaron las 40 épocas y se descartaron 39. El val nunca superó a la época 1.

Causa raíz verificada: `experiments/detection_m3fd/prepare_m3fd.py:162-163` parte secuencialmente (`pares[:2000]`, `pares[2000:2500]`) y las distribuciones son incompatibles — train 31.258 objetos con People 55,1% / Car 38,4% / Lamp 4,3%; val 5.298 objetos con People 9,4% / Car 64,7% / Lamp 13,1%. Con un desplazamiento de prior así, el modelo preentrenado en COCO puntúa mejor en el val que cualquier modelo ajustado al train.

Agravante: los 500 frames de val son **byte a byte** los mismos 500 del test (md5 idéntico entre `m3fd_test_VIS/images/val/02000.jpg` y `m3fd_mixto/images/val/02000__vi.jpg`), así que el checkpoint se eligió midiendo sobre las imágenes que luego se reportan.

Consecuencia demostrada con el contrafactual: reevalué los 9 conjuntos con `last.pt` (protocolo libre de selección). La afirmación central del capítulo — "las mejores fusiones superan en el promedio del par People/Lamp a ambas modalidades individuales" — **se cumple con best.pt** (RatioPiramide 0,1654 > VIS 0,1567 > IR 0,1188) y **no se cumple con last.pt** (mejor fusión PiramideLaplace 0,0989 < IR 0,1087 < VIS 0,1113). También cae "todas las fusiones recuperan ambas clases, algo que el IR no logra": con last.pt el AP de Lamp de la propuesta (0,0112) queda por debajo del IR (0,0159).

Corrección. Rehacer el split de M3FD aleatorio estratificado por clase, con tres particiones disjuntas (train / val de selección / test de reporte), verificar que el val mAP suba con las épocas y solo entonces reportar. Si el mAP de val sigue sin mejorar, el experimento no está midiendo nada y hay que decirlo.
Costo: 1 día. El entrenamiento son ~40 min de GPU; el resto es reescribir el script de preparación (~2 h), las 9 inferencias (~30 min) y rehacer Tabla 9, Figura 9 y la sección de clases complementarias.

Matiz honesto: el hallazgo intermedio "fuga de selección de modelo" es un hecho verificado, pero su efecto declarado estaba invertido. La fuga **favorece** a las fusiones, no a VIS/IR (al pasar a last.pt las 7 fusiones caen de 0,1978-0,2313 a 0,1519-0,1803, por debajo de ambas modalidades). No uses el argumento "la fuga perjudicó a mi método".

### R2 — CRÍTICO. El conjunto de nueve métricas premia el ruido

Construí una fusión falsa sin ningún mérito, `F = clip((VIS+IR)/2 + N(0,sigma))`, y la evalué con el mismo `evaluate_all()` del repositorio sobre los 20 pares. Las cinco métricas de actividad crecen monótonamente con sigma. Con sigma=0,10 el ruido puro queda **1.º en EN (7,231 vs 6,986 de la propuesta), 1.º en FE, 1.º en MG (0,0907 vs 0,0358) y 1.º en SF (51,4 vs 17,7)**, y 2.º en SD. Ranking promedio de nueve métricas sobre 19 imágenes: `Propuesta_Novedosa 4,111` y `RUIDO_sigma0,10 4,111` **empatados en primer lugar**, por delante de los cinco métodos del estado del arte.

El mecanismo es estructural, no un bug: EN, SD, FE, MG y SF son funcionales de actividad de alta frecuencia sin imagen de referencia, y el ruido i.i.d. los maximiza por construcción. `METRIC_DIRECTION` en `src/metrics/evaluators.py:31-36` está bien; el locus es la lista `METRICS` de `experiments/run_stats_analysis.py:31` y el promedio simple de rangos de la línea 52.

Consecuencia sobre el texto. Las frases-evidencia "lidera la entropía (EN = 6,9888) y el contenido de bordes (FE = 1,1045)" y "segunda en contraste, gradiente medio y frecuencia espacial" no acreditan calidad: una imagen deliberadamente degradada las supera en 4 de esas 5.

Corrección. Incorporar al menos una métrica que penalice artefactos, y ya están implementadas y sin usar en `evaluators.py`: `Nabf` (línea 131-142, la única con dirección "min"), `Qabf`, `VIF`, y los índices de Piella Q0/QW/QE. Añadir el experimento de control con ruido al libro como validación del protocolo (es una fortaleza metodológica, no una confesión). Y reetiquetar EN/SD/FE/MG/SF como "actividad espacial", no como "calidad".
Costo: medio día de cómputo y scripts (las métricas ya existen), 1 día de reescritura de la sección 5.4 y las conclusiones.

### R3 — CRÍTICO. FE no es una métrica independiente: es EN dividida por una constante por imagen

`fusion_efficiency()` en `src/metrics/evaluators.py:60-64` devuelve `EN(F) / [(EN(VIS)+EN(IR))/2]`, y el denominador no depende del método. Verificado contra las imágenes crudas, no solo contra el CSV: recargué cada par con `src.datasets.load_pair` y el cociente EN/FE observado coincide con la entropía media de las fuentes (diferencia máxima 1,26e-06, puro redondeo del CSV). Desviación relativa máxima intra-imagen del cociente EN/FE: 9,48e-07. Spearman intra-imagen EN-FE = 1,000 exacto en las 20 imágenes.

Consecuencias medidas. Friedman da chi2 = 81,3818181818182 y p = 1,851e-15 **idénticos** para EN y FE. Las columnas EN y FE de `ranking_methods.csv` son idénticas fila por fila (3,1,5,2,4,7,6). Los 10 contrastes de Wilcoxon de FE no aportan un solo signo nuevo respecto de EN. El Spearman global es 0,046, lo que oculta la redundancia en cualquier diagrama de dispersión.

Efecto sobre el titular. Sin el par corrupto y con las 9 métricas la propuesta es 1.ª (3,556); sin el par corrupto y **sin FE** la propuesta cae a 3.ª empatada (3,875) y la pirámide de Laplace pasa a 1.ª (3,750). Sobre lo publicado (20 imágenes), quitar FE mueve a la propuesta de 3,667 a 4,000, empatada en 3.er/4.º lugar.

Defecto adicional de redacción, que es lo que hace invisible la redundancia. `README.md:166` rotula FE como "Eficiencia / entropía de bordes" y el libro dice "la entropía de bordes (FE)" y "el contenido de bordes (FE = 1,1045)". En `fusion_efficiency()` no hay gradiente, ni Sobel, ni ningún operador de bordes. Además el libro cuenta la entropía dos veces en dos recuentos ("gana a los cinco en EN, FE, MG y SF"; "seis de las nueve métricas (EN, SD, FE, MI_vis, MI_ir y SSIM)") y presenta 9 pruebas de Friedman significativas cuando solo 8 son distintas.

Corrección. Eliminar FE del conjunto y reemplazarla por Qabf (ya implementada), o conservarla declarando explícitamente que es una transformación monótona de EN y no contarla como evidencia independiente. Corregir todas las apariciones de "entropía/contenido de bordes".
Costo: 2 h de regeneración de CSVs, medio día de corrección de texto y recuentos.

### R4 — ALTO. El par `Athena_heather_IR_hei_vis_g` no es un par válido

md5 `056b42a579c2ddbc28d325f5ca909bb0` aparece 3 veces y es el **único** md5 repetido de los 40 archivos: `VIS/Athena_heather_IR_hei_vis_g.bmp` == `IR/Athena_heather_IR_hei_vis_g.bmp` == `IR/Athena_heather_hei_vis.bmp`. El slot de VIS contiene el IR del otro par heather. MSE(VIS,IR)=0,000000 exacto, corr=1,0000; el siguiente par más parecido tiene MSE=0,014261 (APC_3_view_1), cuatro órdenes de magnitud arriba: no hay ningún otro par degenerado ni casi degenerado.

Efecto. Los cuatro métodos multiescala devuelven la imagen intacta y obtienen SSIM=1,000000 y PSNR=120,000 dB, que es el techo del clamp `max(mse, 1e-12)` en `src/metrics/evaluators.py:280`. La contaminación es **asimétrica y en contra de tu método**: al quitar el par, los cinco multiescala pierden entre 5,11 y 5,25 dB de PSNR medio, mientras la propuesta pierde 0,36 dB y el Top-Hat clásico 0,58 dB. Con 20 pares el ranking publicado da LP 3,444 (1.º) y propuesta 3,667 (2.º); con 19 pares la propuesta pasa a 1.ª (3,556) y LP a 2.ª (3,667). El cambio de posición se debe íntegramente a este par. En `pso_por_imagen.csv` es un outlier extremo (F_o_max=2,3833 frente a 1,8815 del siguiente) e infla el F_o_max promedio un 1,8%.

Nota tranquilizadora verificada: la configuración oficial **no** está contaminada. `experiments/pso_grid_search_fo.py:68` toma `allp[::7]`, es decir los índices 0, 7 y 14 (APC_1_view_1, Athena_APC_4, soldier_behind_smoke_2), y el par corrupto es el índice 8.

Corrección. Excluirlo y declararlo (bajar a n=19), o sustituir el archivo VIS por la imagen visible real de esa escena del TNO. Regenerar `all_metrics.csv`, `descriptive_means.csv`, `ranking_methods.csv`, `friedman_results.csv`, `wilcoxon_results.csv` y `pso_por_imagen.csv`. Cambiar el clamp de PSNR por `inf`/`NaN` cuando mse==0, para que un caso así falle de forma visible.
Costo: 2-3 h de cómputo y regeneración, medio día de actualización de tablas.

### R5 — ALTO. El ranking global rankea las medias, no promedia rangos por bloque

`experiments/run_stats_analysis.py:41` construye `means = df.groupby("method")[METRICS].mean()` y la línea 50 hace `means[m].rank(...)`, es decir rankea 7 números por métrica. `ranking_methods.csv` lo confirma: la fila de PiramideLaplace es 3,1,3,7,1,1,6,4,5, ranks enteros 1..7, imposible con promedio de rangos por imagen.

Recalculado sobre el mismo `all_metrics.csv`:

- Rank de las medias (publicado): LP 3,444 (1.º) | Propuesta 3,667 (2.º) | DTCWT 4,000 | TopHat 4,000 | RP 4,111 | CVT 4,333 | DWT 4,444
- Promedio de rangos por imagen (20 bloques x 9 métricas): **Propuesta 3,478 (1.º)** | RP 3,917 | TopHat 3,922 | LP 3,931 (4.º) | DTCWT 4,075 | DWT 4,233 | CVT 4,444

Robustez: excluyendo el par corrupto, propuesta 3,386 (1.ª); agregando por escena, 3,380 (1.ª). LP nunca vuelve a ser 1.ª con rangos por bloque. Y los defectos R4 y R5 se acumulan: incluso con rank de medias, quitar el par corrupto ya pone la propuesta 1.ª.

El verdadero motor del vuelco es el PSNR del par corrupto (LP pasa de rank 5 por media a 6,725 por imagen). Descarta el mecanismo "LP gana MI_vis por un outlier": LP gana MI_vis y MI_ir con ambas agregaciones (media 2,1183, mediana 2,1495, rango medio 1,90), sin outlier.

Dato que descarta cherry-picking, y conviene tenerlo a mano en la defensa: en la variante `metrics_reports_libre` (m=0,0703) la misma corrección deja a la propuesta **última** (4,372 por imagen frente a 5,000 por medias, LP 1.ª en ambas). La corrección no favorece sistemáticamente a la tesis: es un arreglo metodológico genuino.

Corrección. Reemplazar el bloque por rangos intra-bloque, que es el acompañante estándar de Friedman:
`rank_tbl[m] = metric_matrix(m).rank(axis=1, ascending=(METRIC_DIRECTION[m]=="min"), method="average").mean(axis=0)`
Regenerar `ranking_methods.csv`, Tabla 7, Figura 8 y los cuatro pasajes de texto (párrafos 797, 1060, 1064, 1066 del docx). Si prefieres conservar el cálculo actual, hay que renombrarlo "ranking de las medias".
Costo: 1 h de código, medio día de texto y figuras.

### R6 — ALTO. r=25 no es resultado del PSO, y el libro lo afirma en nueve pasajes

Verificado con un barrido determinista independiente (25 radios x 49 valores de m, 24.500 evaluaciones, con las métricas oficiales de `src/metrics/evaluators.py`). En el rango publicado m>=0,30 el argmax global es **r=1, m=0,30**: F_o = 1,7797 (20 pares), 1,7479 (19 pares) y 1,7177 (las 3 escenas del PSO). La configuración oficial r=25, m=0,30 da 1,7138 / 1,6999 / 1,6818 — déficits de 0,0659 (3,7%), 0,0480 y 0,0359 (2,1%). El argmax por imagen es r=1 en **20 de 20** escenas. La propia tabla del PSO publicada da como mejor resultado r=1, m=0,3000, Fo=1,7354 en 17 de 25 configuraciones. F_o decrece monótonamente hasta r=11 (mínimo 1,6779) y recupera solo parcialmente en r=25: es un óptimo local secundario.

r=25 se eligió maximizando las mismas nueve métricas con las que después se rankea la propuesta, y ni siquiera las nueve lo favorecen. Wilcoxon pareado r=1 vs r=25 a m=0,30, 20 pares, todas con p<=5,72e-06: r=25 gana EN, SD, FE, MG y SF; **r=1 gana MI_vis (1,368 vs 0,962), MI_ir (0,932 vs 0,671), SSIM (0,761 vs 0,668) y PSNR (19,42 vs 17,25)**. Es 5-4, no un barrido.

La justificación "r=1 desactiva el banco de elementos estructurantes" es falsa: `disk_se(1)` es la cruz 3x3 y `linear_se(1,theta)` para 0/45/90/135 son cuatro máscaras 3x3 distintas.

Agravante de circularidad: los seis comparativos no reciben ningún ajuste equivalente (`comparatives.py` con niveles fijos, `run_all_fusions.py:47` fija el Top-Hat clásico en r=5).

Corrección. No presentar r=25 como resultado del PSO. Declarar que el PSO fija m (m*=0,30) y que r=25 es una **elección de diseño** tomada sobre las métricas de actividad, reconociendo el sesgo. Sustituir "las nueve métricas favorecen r=25" por "cinco de las nueve (EN, SD, FE, MG, SF) favorecen r=25; las cuatro de fidelidad (SSIM, PSNR, MI_vis, MI_ir) favorecen r=1, todas con p<1e-5". Corregir el pie de la Figura 10 ("PSO: r = 25, m = 0,30") y los párrafos 41, 44, 189, 323, 339, 483, 496, 906, 951, 1034, 1035. Añadir el benchmark en r=1 como análisis de sensibilidad.
Costo: medio día de texto; 3-4 h si añades el benchmark en r=1.

### R7 — MEDIO-ALTO. LLVIP reporta el máximo sobre 40 épocas medido en el mismo val

Los mAP de `detection_llvip_map.csv` son el máximo sobre 40 épocas evaluado en el conjunto que se reporta. El sesgo optimista medido es de 0,013 a 0,075 según el método, **mayor que las brechas entre métodos** (la tabla entera cabe en 0,913-0,957). El ranking entre fusiones se reordena por completo con cualquier agregación honesta. La higiene es correcta por lo demás: los 12 entrenamientos usan configuración y semilla idénticas, las etiquetas son byte-idénticas entre métodos y no hay solape train/val.

Corrección. Reevaluar con `last.pt` (no requiere reentrenar: los pesos ya están) o promediar las últimas k épocas, y declarar el protocolo. Reportar que las diferencias entre fusiones no son distinguibles.
Costo: 2 h.

### R8 — MEDIO. Documentos que afirman lo contrario de sus propias tablas

Las cifras de todos los entregables reproducen fielmente los CSV — verifiqué celda por celda el benchmark de 9 métricas, Friedman, los 45 contrastes de Wilcoxon, el ranking, LLVIP, M3FD y el barrido PSO, sin una sola discrepancia numérica en la variante oficial. El problema es el texto que las envuelve.

- `Avances_Tesis_libre.pdf` conserva la narrativa hard-coded de la variante restringida: afirma que la propuesta lidera EN/FE/SD/MG/SF cuando en m=0,0703 es última en cuatro de esas cinco y ocupa el puesto 7/7. **No entregues ese PDF.**
- La diapositiva de conclusiones de `Tesis_Defensa_Presentacion.pptx` afirma que la propuesta es "la mejor fusión del estudio" en M3FD, cuando es la 6.ª de 7 (mAP50 0,2109; RatioPiramide 0,2314). Es la afirmación más fácil de desmontar en vivo con la propia Tabla 9. Prioridad de corrección alta pese a ser "solo texto".
- El titular "2.º lugar del ranking (3,67)" está repetido en los seis documentos y es un artefacto de R3+R5.
- El apéndice del libro y varias conclusiones describen configuraciones, métricas y experimentos ya eliminados.

Costo: 1 día de edición coordinada de libro, deck, README y avances (dejando el PDF libre fuera o regenerándolo con narrativa dinámica).

### R9 — MEDIO. Defectos menores pero fáciles de preguntar

- `pso_grid_search_fo.py` usa un SSIM propio con ventana gaussiana que sobreestima el término en +0,0172 de media, así que la Tabla 11 y `barrido_metricas_vs_m.csv` reportan **dos valores distintos de la misma cantidad**. Corrección: importar el SSIM oficial y regenerar. Costo: 2 h.
- Bug de truncamiento vs redondeo del radio que hace internamente incoherentes 45 de las 500 filas del anexo PSO por imagen. Costo: 1 h.
- El Excel publica 62 p-valores de Holm iguales a cero por redondeo. Usar notación científica. Costo: 30 min.
- El "barrido de 25 configuraciones" no son 25 réplicas independientes y solo produce 3 valores distintos de aptitud. Reformular el texto. Costo: 1 h.
- Composición del corpus: los 20 pares contienen solo 10 escenas físicamente distintas, así que el n=20 que asumen Friedman y Wilcoxon está inflado ~2x. Recomputado agregando por escena (n=10 y n=19), la conclusión central sobrevive: la propuesta sigue 1.ª en ranking por bloques y Friedman sigue significativo en las 9 métricas. Basta declararlo y añadir el análisis por escena como robustez. Costo: 3 h.
- En los 6 pares "fk_" (APC_1/APC_3) el VIS y el IR no son capturas simultáneas, lo que debilita la lectura de "complementariedad" en esas escenas. Declararlo.
- La comparación clave Propuesta vs Top-Hat clásico no existe en los artefactos de Wilcoxon (el script contrasta morfológicos contra el estado del arte, no entre sí). Añadirla. Costo: 1 h.

---

## 2. Qué está correcto y puedes defender con confianza

Esto lo verifiqué explícitamente y no encontré defecto. Dilo con seguridad si te lo preguntan.

1. **La mecánica de carga y emparejado de datos.** 20/20 pares emparejados por nombre, sin huérfanos, dimensiones idénticas dentro de cada par, todos BMP de 8 bits con paleta de grises, todos normalizados a [0,1]. Las PNG fusionadas guardadas reproducen las métricas publicadas (max |ΔPSNR| = 0,071 dB excluyendo el par corrupto).
2. **Seis de las nueve métricas están bien implementadas** en su definición estándar: EN, SD, SF, MG, SSIM y PSNR. Hay desviaciones de escala o de ventana, pero verifiqué que **no alteran ningún ranking**. El clamp de PSNR se activa 4 de 140 veces y siempre sobre el par corrupto: aislado es inocuo.
3. **La maquinaria inferencial es correcta.** Reproduje exactamente los chi2 y p de Friedman (con corrección de empates verificada contra la fórmula de Conover), los 90 contrastes de Wilcoxon (test exacto, n=20), la corrección de Holm (coincide dígito a dígito con una reimplementación independiente) y el rank-biserial. **No hay ningún p=0** en Friedman: los CSV llevan valores reales (1,9e-15 a 7,4e-21) y la tesis reporta correctamente "< 0,001".
4. **Las superioridades pareadas concretas que el libro afirma son reales.** En `wilcoxon_results.csv`, la propuesta gana 5/5 contra el estado del arte en EN, MG y SF con `sig_holm=True` y p_holm máximo 0,0146. Y la tesis **admite explícitamente** que cede de forma significativa en MI_vis (4/5), MI_ir (5/5), SSIM (5/5) y PSNR (5/5). Esa honestidad es una fortaleza; mantenla.
5. **La separación del ranking sí es estadísticamente significativa.** Un hallazgo intermedio afirmaba lo contrario y quedó refutado. La CD de Nemenyi está mal especificada para rangos promediados sobre métricas (supone varianza intra-bloque 4,0 cuando la real es 0,2955, 13,5 veces menor). Con la nula correcta por permutación (20.000 réplicas) la CD empírica es 0,6667 y el spread observado es 0,9667, p permutacional = 0,00050. Friedman sobre la matriz 20x7 de rangos medios da chi2=47,622, p=1,4e-08. Wilcoxon pareado con Holm sobre el rango medio por imagen: **5 de 6 rivales significativos a favor de la propuesta** (DWT 0,0023; CVT 0,0023; DTCWT 0,0060; TopHat 0,0060; RP 0,0454; solo LP no alcanza, 0,1073).
6. **La aptitud F_o está bien implementada** en `pso_por_imagen.py`, idéntica al módulo oficial. La discretización de m a 4 decimales es inocua (mueve F_o menos de 2,1e-5). Ambos scripts de PSO son reproducibles bit a bit.
7. **La higiene experimental de LLVIP es correcta y verificable.** Los 12 entrenamientos usan configuración y semilla idénticas, las etiquetas son byte-idénticas entre métodos, y no hay solape train/val en ninguno de los dos datasets.
8. **Los números de M3FD son reproducibles.** Reejecuté `model.val()` con `best.pt` y reproduje `detection_m3fd_map.csv` con diferencia 0,0000. El problema es el diseño, no la ejecución.
9. **Fidelidad documento-dato.** Cero discrepancias numéricas entre libro, avances restringido, Excel, README, deck, `Resultados_Optimos_por_Imagen` y los CSV, en la variante oficial m=0,30.
10. **La configuración oficial no está contaminada por el par corrupto** (el PSO usa los índices 0, 7, 14 y el par corrupto es el 8).

---

## 3. La pregunta de fondo

**¿La metodología sostiene el objetivo declarado — detectar en una sola imagen fusionada objetos complementarios que no se detectan en VIS ni en IR por separado?**

## NO.

Y no es por un detalle de cálculo: es que el único experimento diseñado para probarlo devuelve el resultado contrario, con el instrumento descalibrado.

**Dato 1. Ninguna fusión domina a VIS en las dos clases complementarias. Cero de siete.** Calculado sobre `detection_m3fd_map.csv` (AP50 de la clase People, que solo el IR ve bien, y Lamp, que solo el VIS ve bien):

| Entrada | AP50 People | AP50 Lamp | Promedio del par |
|---|---|---|---|
| VIS | 0,1780 | 0,1353 | 0,1567 |
| IR | 0,2198 | 0,0176 | 0,1187 |
| RatioPiramide | 0,1982 | 0,1327 | 0,1654 |
| DWT | 0,1648 | 0,1101 | 0,1375 |
| DTCWT | 0,1594 | 0,1140 | 0,1367 |
| Curvelet | 0,1667 | 0,1002 | 0,1334 |
| **Propuesta_Novedosa** | **0,1464** | **0,1011** | **0,1237** |
| PiramideLaplace | 0,1472 | 0,0961 | 0,1217 |
| TopHat_Clasico | 0,1253 | 0,0543 | 0,0898 |

Ninguna de las 7 fusiones supera a VIS en ambas clases a la vez, y ninguna supera al IR en ambas a la vez (el IR mantiene el mejor People, 0,2198, imbatido). La propuesta pierde contra VIS en **las dos** (0,1464 vs 0,1780 y 0,1011 vs 0,1353). La fusión no produce una imagen que contenga lo mejor de las dos modalidades: produce un compromiso que degrada ambas respecto de la mejor entrada de cada clase.

**Dato 2. La única afirmación positiva que queda no es distinguible del azar.** "La Ratio Pyramid es la única entrada que supera a ambas modalidades en el promedio del par (0,1654 vs 0,1567)": bootstrap pareado p=0,802, cambia de signo al reimplementar el AP, y desaparece con `last.pt` (RP 0,0913, VIS 0,1113). Además no es tu método.

**Dato 3. El detector con el que se mide todo esto es el de la época 1 de 40** (R1). Aunque el resultado hubiese sido favorable, no sería interpretable.

**Dato 4. LLVIP tampoco lo respalda.** El IR solo obtiene mAP50 = 0,957, por encima de las nueve entradas; la propuesta queda en 0,9129, 8.ª de 9, solo por delante del VIS (0,808). Es decir, en el dataset donde la detección funciona bien, fusionar **no aporta nada** sobre usar el IR directamente.

**Dato 5. El argumento alternativo — "es mejor porque lidera el ranking de nueve métricas" — no puede sustituir al de detección**, porque ese ranking corona empatada a una imagen de ruido gaussiano (R2) y cuenta la entropía dos veces (R3).

### Qué lo haría sostenible

Tres caminos, de más a menos costoso. El (a) y el (b) se combinan.

**(a) Rediseñar M3FD y medir lo que realmente afirma el objetivo.** El mAP promediado sobre 500 frames no mide "detectar en una sola imagen objetos que no se detectan por separado". La métrica que corresponde al objetivo es **por escena y por instancia**: número de escenas en las que la imagen fusionada detecta simultáneamente al menos un objeto de la clase térmica y uno de la clase visible, contra el número de escenas en las que VIS lo logra y en las que IR lo logra. Esa es literalmente la hipótesis, es un conteo directo, y la fusión tiene una ventaja estructural real ahí que el promedio de AP diluye: el IR prácticamente no ve Lamp (0,0176) y todas las fusiones lo recuperan multiplicando por 3-8 veces. Requisitos previos: split estratificado, test disjunto del val de selección, y verificar convergencia. Costo: 2-3 días.

**(b) Reencuadrar la tesis de "superioridad" a "caracterización del compromiso".** Lo que los datos sostienen honestamente es: *el operador propuesto, con una sola escala y un banco de cinco elementos estructurantes, maximiza la actividad espacial y la entropía frente a cinco métodos multiescala establecidos con un costo computacional menor, a cambio de una pérdida significativa de fidelidad a las fuentes (SSIM, PSNR, MI); y en detección orientada a tarea ninguna fusión, incluida la propuesta, supera a la mejor modalidad individual, lo que acota el alcance práctico de la fusión morfológica*. Eso es verdadero, verificado, y perfectamente defendible en una maestría. Un resultado negativo bien medido vale más que uno positivo mal medido, y te blinda contra la pregunta incómoda. Costo: 1-2 días de reescritura del capítulo de conclusiones y del resumen; cero cómputo.

**(c) Si necesitas conservar el objetivo en forma afirmativa**, hay que reformularlo como hipótesis contrastada y **rechazada** para el caso de la fusión morfológica, con la evidencia arriba. Es la opción de menor esfuerzo y máxima honestidad, pero exige reescribir el resumen, el objetivo general y las conclusiones, no solo matizarlos.

Lo que **no** funciona: mantener la afirmación actual apoyada en `best.pt` de la época 1. Es el punto donde la defensa se rompe si alguien abre `results.csv`.

---

## 4. Lista priorizada de acciones

### Imprescindibles para defender

| # | Acción | Ref. | Costo |
|---|---|---|---|
| 1 | Corregir la diapositiva de conclusiones del deck: la propuesta es 6.ª de 7 en M3FD, no "la mejor fusión del estudio" | R8 | 30 min |
| 2 | Retirar o regenerar `Avances_Tesis_libre.pdf`: su narrativa contradice sus propias tablas | R8 | 1 h |
| 3 | Excluir el par `Athena_heather_IR_hei_vis_g` (n=19), declararlo, y regenerar los seis CSV. Cambiar el clamp de PSNR a inf/NaN | R4 | 4 h |
| 4 | Cambiar el ranking a promedio de rangos por bloque (3 líneas) y regenerar Tabla 7, Figura 8 y los cuatro pasajes de texto. Sube la propuesta de 2.ª a 1.ª | R5 | 4 h |
| 5 | Declarar que FE es EN reescalada, quitarla del recuento de evidencia independiente, y corregir todas las apariciones de "entropía/contenido de bordes" | R3 | 4 h |
| 6 | Dejar de atribuir r=25 al PSO en los 11 párrafos y en la Figura 10; sustituir "las nueve métricas favorecen r=25" por "cinco de nueve"; eliminar la frase falsa sobre r=1 | R6 | 4 h |
| 7 | Rehacer el split de M3FD (estratificado, tres particiones disjuntas), reentrenar, verificar convergencia del val y rehacer Tabla 9, Figura 9 y la sección de clases complementarias | R1 | 1-2 días |
| 8 | Reescribir el objetivo/resumen/conclusiones según el reencuadre (b) o (c) de la sección 3 | R1 | 1-2 días |
| 9 | Reevaluar LLVIP con `last.pt` (sin reentrenar) y declarar el protocolo; indicar que las diferencias entre fusiones no son distinguibles | R7 | 2 h |
| 10 | Corregir los 62 p-valores de Holm que el Excel publica como 0 | R9 | 30 min |

### Muy recomendables (te fortalecen y son baratas)

| # | Acción | Ref. | Costo |
|---|---|---|---|
| 11 | Añadir Nabf y Qabf (ya implementadas) al conjunto de evaluación e incluir el experimento de control con ruido como validación del protocolo | R2 | 1 día |
| 12 | Unificar el SSIM de `pso_grid_search_fo.py` con el oficial y regenerar la Tabla 11 | R9 | 2 h |
| 13 | Añadir el contraste Wilcoxon Propuesta vs Top-Hat clásico, que hoy no existe en los artefactos | R9 | 1 h |
| 14 | Reportar el análisis agregado por escena (n=10) como robustez y declarar que los 20 pares son 10 escenas | R9 | 3 h |
| 15 | Corregir el bug de truncamiento del radio (45 de 500 filas del anexo PSO) | R9 | 1 h |
| 16 | Limpiar el apéndice y las conclusiones de configuraciones y experimentos ya eliminados | R8 | 3 h |

### Opcionales (mejoran el trabajo, no bloquean la defensa)

| # | Acción | Ref. |
|---|---|---|
| 17 | Añadir el benchmark completo en r=1 como análisis de sensibilidad (es el óptimo real de F_o) | R6 |
| 18 | Dar a los métodos comparativos un ajuste de hiperparámetros equivalente, para eliminar la circularidad de la comparación | R6 |
| 19 | Declarar que los 6 pares "fk_" no son capturas simultáneas | R9 |
| 20 | Reformular el "barrido de 25 configuraciones" (no son réplicas independientes; solo 3 valores distintos de aptitud) | R9 |
| 21 | Sustituir el par corrupto por la imagen VIS real del TNO para recuperar n=20 | R4 |

---

## Dos advertencias finales

**Dos de los defectos juegan en contra de tu método.** El par corrupto regala 5,1-5,25 dB de PSNR a los cinco multiescala y solo 0,36 dB a la propuesta; el ranking de medias te deja 2.º cuando el procedimiento estándar te deja 1.º. Corregirlos **mejora** tu resultado. Preséntalos así, como rigor propio y no como concesión.

**No sobrevendas la corrección del ranking.** En la variante m=0,0703 la misma corrección deja a la propuesta última. Eso demuestra que el arreglo es metodológico y no interesado — y es exactamente el argumento que te conviene si alguien sugiere que ajustaste el cálculo para ganar. Ten el dato preparado.