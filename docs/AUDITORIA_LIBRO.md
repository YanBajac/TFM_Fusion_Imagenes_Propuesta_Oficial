# Auditoría del libro contra los datos — 14 de agosto de 2026

Ocho revisiones en paralelo, una por bloque del libro, cada una verificando las afirmaciones
de su bloque **contra los CSV de `experiments/results/`** y no contra el informe ni el deck,
para que un error propagado a los tres no se valide solo.

**987 afirmaciones revisadas · 910 respaldadas · 77 marcadas.**

Una revisión adversarial estaba filtrando los falsos positivos cuando se cerró la sesión, así
que **cada punto de esta lista hay que confirmarlo abriendo el CSV antes de tocar el libro**.
Están ordenados por gravedad.


## Gravedad alta (16)

### parrafo 370 (§5.4.3 Ranking promedio) — CONTRADICE

> la piramide de Laplace alcanza un SD promedio mayor (0,1550 frente a 0,1439), pero la propuesta la supera en mas pares de los que pierde, y el rango medio recoge esa consistencia por escena que el promedio aritmetico oculta

**El dato:** Conteo pareado sobre all_metrics.csv (columna SD, 20 filas de Propuesta_Novedosa contra 20 de PiramideLaplace): la propuesta tiene SD mayor en 9 de los 20 pares y menor en 11. Pierde en mas pares de los que gana, justo al reves de lo escrito. Lo confirma wilcoxon_results.csv fila 14 (metric=SD, tophat=Propuesta_Novedosa, baseline=PiramideLaplace): diff=-0,0111, W=72, p=0,2305, effect_r=-0,314, sig_holm_05=False; el signo negativo del rank-biserial dice que la mayoria de los pares favorece a la Laplace. El primer puesto en rango medio (1,65 frente a 2,00) es real pero se explica por otro mecanismo: la propuesta NUNCA baja del 2.o puesto en los 20 pares, mientras la Laplace cae al 3.o, 4.o o 6.o en 5 pares (APC_4_fennek 3.o, APC_1_view_1 4.o, APC_3_view_1 4.o, jeep_in_smoke 4.o, heather 6.o). Es consistencia por no tener malos casos, no por ganar mas duelos.

*(bloque: Parrafos 347-385 (capitulo 5, primera parte: calidad de imagen §5.1-5.4 y evaluacion orientada a tarea §5.5), mas las Tablas 4, 5, 6, 7, 8 y 9 del libro (indices python-docx 27, 28, 29, 30, 31, 32))*

### párrafo 423 (conclusión específica 1) — CONTRADICE

> En el experimento de clases complementarias (M3FD), la fusión muestra su valor distintivo —detecta simultáneamente los objetos térmicos (personas) y los exclusivamente visibles (luces) que cada modalidad pierde por separado—

**El dato:** complementariedad_resumen.csv dice lo contrario para la propuesta: recupera_ambas = 116 de 232 escenas (pct_ambas = 50,0 %) frente a 123 (53,0 %) del VIS solo; gana_vs_VIS = 8 y pierde_vs_VIS = 15; resuelve_criticas = 2 de las 90 escenas críticas. Por clase queda intermedia, no superior: recupera_People 164 (IR: 186) y recupera_Lamp 145 (VIS: 163). Y en detection_m3fd_map.csv el promedio del par (AP50_People + AP50_Lamp)/2 da VIS solo 0,6184 por encima de seis de las siete fusiones y muy por encima de la propuesta (0,5643, 8.º de 9 entradas, solo delante del Top-Hat clásico 0,5065). La única entrada que supera al visible es RatioPiramide (0,6222). La misma conclusión, escrita en §5.8.5 (párrafo 419), es la contraria: «la propuesta recupera ambas en el 50,0 % de los casos, frente al 53,0 % del visible solo». Nota: este mismo exceso («solo la fusión detecta ambas») ya se retiró del README, pero sobrevive en la conclusión 1.

*(bloque: Párrafos 420–442 — Capítulo 6 CONCLUSIONES Y RECOMENDACIONES)*

### párrafo 439 (recomendación 5) — CONTRADICE

> Evaluar híbridos Top-Hat ↔ pirámide de Laplace que combinen la fidelidad a fuentes del primero con la riqueza global del segundo.

**El dato:** La atribución está invertida. descriptive_means.csv: TopHat_Clasico es el ÚLTIMO de los siete en las tres métricas de fidelidad — MI_vis 0,7867, MI_ir 0,4928, SSIM 0,5640 — y PiramideLaplace es el PRIMERO en MI con ambas fuentes (MI_vis 1,9242; MI_ir 0,9178) además de liderar el contraste (SD 0,1550). En ranking_methods.csv los rangos medios del clásico son MI_vis 6,70, MI_ir 6,70 y SSIM 7,00 (peor posible). Si «Top-Hat» refiere a la propuesta, tampoco: MI_vis 0,8970, MI_ir 0,6003, SSIM 0,6584, y el propio párrafo 425 la declara «penalizada por las métricas de fidelidad a las fuentes». La frase habría que darla vuelta: la fidelidad la aporta la pirámide, la actividad el Top-Hat.

*(bloque: Párrafos 420–442 — Capítulo 6 CONCLUSIONES Y RECOMENDACIONES)*

### Parrafo 86 (SUMMARY), parrafo de la evaluacion orientada a tarea — CONTRADICE

> the proposal falls at the lower end of the fusion band (0.906)

**El dato:** semillas_llvip_resumen.csv, columna mAP50_media: Propuesta_Novedosa = 0,9283, que es la 3.a de las siete fusiones (por detras de PiramideLaplace 0,9517 y DTCWT 0,9365, y por delante de Curvelet 0,9259, TopHat_Clasico 0,9234, DWT 0,9183 y RatioPiramide 0,9043). El valor 0,906 es el de UNA semilla: en detection_llvip_semillas.csv, fila method=Propuesta_Novedosa / semilla=0, mAP50 = 0,9057, donde si quedaba 6.a de siete. El SUMMARY no solo cambia la cifra, invierte la conclusion cualitativa, y lo hace despues de anunciar el protocolo de 5 semillas. El RESUMEN en espanol dice lo correcto.

*(bloque: Parrafos 82-167: RESUMEN (p. 83) y SUMMARY (p. 86). Los parrafos 88-167 son el indice de CONTENIDO (titulos y numeros de pagina), sin afirmaciones empiricas.)*

### Parrafo 86 (SUMMARY) — CONTRADICE

> the infrared alone remains the strongest modality (0.971)

**El dato:** semillas_llvip_resumen.csv, fila IR, columna mAP50_media = 0,9611 (desv 0,0139). El 0,971 corresponde a la semilla 0 aislada: detection_llvip_semillas.csv, fila IR / semilla=0, mAP50 = 0,9708 (igual a la corrida unica de detection_llvip_map.csv, ya superada). El RESUMEN en espanol dice 0,961, que es el valor vigente.

*(bloque: Parrafos 82-167: RESUMEN (p. 83) y SUMMARY (p. 86). Los parrafos 88-167 son el indice de CONTENIDO (titulos y numeros de pagina), sin afirmaciones empiricas.)*

### Parrafo 86 (SUMMARY) — CONTRADICE

> every fusion clearly outperforms the visible modality alone (mAP@0.5 from 0.81 to 0.91-0.95)

**El dato:** semillas_llvip_resumen.csv: VIS mAP50_media = 0,7951 (no 0,81) y la banda de las siete fusiones va de 0,9043 (RatioPiramide) a 0,9517 (PiramideLaplace), es decir 0,904-0,952 (no 0,91-0,95). Los valores 0,81 y 0,91-0,95 son los de la semilla 0 (detection_llvip_semillas.csv, semilla=0: VIS 0,8133; fusiones 0,9056-0,9515). El RESUMEN dice 0,795 y 0,904-0,952, que si coinciden con el CSV.

*(bloque: Parrafos 82-167: RESUMEN (p. 83) y SUMMARY (p. 86). Los parrafos 88-167 son el indice de CONTENIDO (titulos y numeros de pagina), sin afirmaciones empiricas.)*

### Parrafos 83 y 86, comparados entre si — INCOHERENCIA

> El SUMMARY invoca el protocolo de 5 semillas ('repeated with 5 training seeds per input, 45 runs in total') y a continuacion reporta las cuatro cifras de una sola semilla, omitiendo los tres resultados que el RESUMEN si da: que el IR supera a 6 de las siete fusiones y no se distingue de la septima, que la propuesta es indistinguible de 4 de sus seis rivales, y el ruido de inicializacion de 0,0128.

**El dato:** Los dos textos describen el mismo experimento con dos conjuntos de numeros distintos. El vigente es el de 5 semillas: semillas_llvip_resumen.csv y semillas_llvip_pareadas.csv (generados por experiments/run_analisis_semillas_llvip.py, fechados 13-ago), frente a detection_llvip_map.csv (29-jul, corrida unica). El SUMMARY quedo con la version vieja. Un lector que compare los dos resumenes concluye cosas opuestas sobre el lugar de la propuesta.

*(bloque: Parrafos 82-167: RESUMEN (p. 83) y SUMMARY (p. 86). Los parrafos 88-167 son el indice de CONTENIDO (titulos y numeros de pagina), sin afirmaciones empiricas.)*

### parrafos 515 y 516 (apendice D, cierre del pseudocodigo y nota) — CONTRADICE

> (r, m) se optimizan por PSO (barrido de 25 configuraciones) -> r = 25, m = 0,30 ... optimiza (r, m) por PSO mediante un barrido de 25 configuraciones de enjambre, con optimo r = 25, m = 0,30

**El dato:** experiments/results/metrics_reports/pso_grid_search_fo_propuesta.csv -el CSV que el propio apendice designa como tabla resumen del barrido en el parrafo 490- dice lo contrario: el maximo de la columna Fo_opt es 1,7350 y corresponde a r_opt = 1 (fila n=2, T=20, y otras 15 filas mas: 16 de las 25 configuraciones convergen a r=1); las 8 filas con r_opt = 25 alcanzan solo Fo_opt = 1,7057. Lo confirma el estado reanudable experiments/results/pso/pso_grid_fo_propuesta_state.json (mejor configuracion n2_T20, gbest r=1,0, m=0,3, gbest_fit=1,734991) y el barrido determinista experiments/results/metrics_reports/optimo_exacto_fo.csv (5.000 filas, 25 radios x 200 pesos): dentro del rango publicado m>=0,30 el argmax es r=1, m=0,30, Fo=1,734991, y r=25 con m=0,30 da 1,705696; el argmax global es r=25 con m=0,07 (Fo=1,771465), que tampoco es la configuracion adoptada. Ademas el apendice se contradice con el resto del libro, que lo dice bien: el parrafo 418 (seccion 5.8.5) afirma «El argmax de la aptitud dentro del rango publicado es r = 1 (Fo = 1,7350) y no r = 25 (1,7057) ... El radio adoptado proviene, pues, de la bateria de evaluacion», y los parrafos 179, 274, 305, 386, 423 y 428 califican r=25 de decision de diseno. El comentario de experiments/run_all_fusions.py (lineas del bloque PROP_R) tambien lo declara: «El RADIO no lo fija el PSO ... r = 25 es una DECISION DE DISENO». La palabra «optimo» es el error: hay que decir que el PSO fija m=0,30 (piso del rango) y que r=25 se adopta sobre la bateria de evaluacion.

*(bloque: Parrafos 482-521 - Capitulo 8 APENDICE (A. Repositorio del codigo; B. Configuraciones del barrido PSO; C. Tablas estadisticas extendidas; D. Pseudocodigos; E. Refinamiento de la regla de fusion; F. Hardware y tiempos))*

### parrafo 518 (apendice E, Refinamiento metodologico de la regla de fusion) — CONTRADICE

> La distincion correcta separa las dos clases de capas: las de detalle se fusionan por maxima actividad local y la base por promedio simple. ... Esto concierne a los metodos comparativos multiescala

**El dato:** El refinamiento NO esta aplicado en la piramide de Laplace, uno de los cuatro comparativos multiescala y el segundo del ranking. En src/fusion/comparatives.py, _build_laplacian_pyramid termina con laplacian.append(gaussian[-1])  # capa base, y laplacian_pyramid_fusion recorre TODAS las capas con el mismo enmascarado: for lv_layer, li_layer in zip(lv, li) ... mask = (act_v >= act_i); es decir, la base sigue fusionandose por maxima actividad local, exactamente la «primera version» que el apendice dice haber corregido. Los otros tres si lo aplican: ratio_pyramid_fusion usa img = 0.5*(gv[levels]+gi[levels]) («base promediada»), dwt_fusion y curvelet_fusion promedian la aproximacion (0.5*cv_item+0.5*ci_item) y dtcwt_fusion promedia el lowpass. Reimplemente la LP con la base por promedio simple sobre los 20 pares: la imagen cambia en 0,10761 de media absoluta (maximo 0,23632) sobre un rango [0,1], y MI_vis pasa de 1,9242 a 1,1171 y MI_ir de 0,9178 a 0,6885. El valor 1,9242 es precisamente el que figura en experiments/results/metrics_reports/all_metrics.csv y en descriptive_means.csv (fila PiramideLaplace, columna MI_vis), de modo que todo el benchmark publicado se calculo con la regla sin refinar. Tiene consecuencia sobre resultados: ranking_methods.csv da a PiramideLaplace el mejor rango medio en MI_vis (1,85) y MI_ir (2,20), y el parrafo 399 del libro afirma que «la piramide de Laplace lidera el contraste (SD) y la informacion mutua». Nota: la Tabla 13 del libro describe la LP solo como «fusion por maxima actividad local», sin mencionar promedio en la base, o sea que coincide con el codigo y discrepa del apendice.

*(bloque: Parrafos 482-521 - Capitulo 8 APENDICE (A. Repositorio del codigo; B. Configuraciones del barrido PSO; C. Tablas estadisticas extendidas; D. Pseudocodigos; E. Refinamiento de la regla de fusion; F. Hardware y tiempos))*

### parrafo 519 (apendice F, Hardware y tiempos de ejecucion) — CONTRADICE

> La totalidad de los experimentos se ejecuto en una notebook estandar (Intel i7, 16 GB de RAM, sin GPU dedicada) bajo Windows 11 con Python 3.11.

**El dato:** experiments/results/metrics_reports/detector_perfil.json, que produce experiments/perfil_detector.py leyendo torch.cuda.is_available() y torch.cuda.get_device_name(0) (lineas 68-69), registra en el bloque «entorno»: "cuda": true y "gpu": "NVIDIA GeForce RTX 4050 Laptop GPU", con torch 2.5.1+cu121 y ultralytics 8.4.68. Los entrenamientos de deteccion no son marginales: el mismo JSON declara amp: true (precision mixta, que requiere GPU para tener sentido), 40 epocas, lote 16, imgsz 640, 12 entrenamientos en LLVIP y 2 en M3FD, con 4.000 pares de entrenamiento en m3fd_mixto. Asi que «la totalidad de los experimentos ... sin GPU dedicada» es falso para la seccion 5.5. Lo que si verifique: Python 3.11 (el interprete del repo es 3.11.14) y Windows 11. El «Intel i7, 16 GB de RAM» no lo registra ningun CSV ni JSON del repositorio (busque columnas y claves con cpu/ram/hardware/entorno en los 68 archivos de metrics_reports).

*(bloque: Parrafos 482-521 - Capitulo 8 APENDICE (A. Repositorio del codigo; B. Configuraciones del barrido PSO; C. Tablas estadisticas extendidas; D. Pseudocodigos; E. Refinamiento de la regla de fusion; F. Hardware y tiempos))*

### parrafo 492 (apendice C, ultima frase) — SIN FUENTE

> Los 54 contrastes de la propuesta frente a sus seis rivales (9 metricas x 6 rivales: los cinco del estado del arte y el Top-Hat clasico, Wilcoxon con Holm y tamano de efecto rank-biserial) se consignan en wilcoxon_propuesta_vs_metodos.csv.

**El dato:** El archivo no existe. `find . -iname "*wilcoxon*"` excluyendo .venv devuelve solo experiments/results/metrics_reports/wilcoxon_results.csv, experiments/results/metrics_reports_libre/wilcoxon_results.csv y experiments/results/metrics_reports/comparacion_aptitudes_wilcoxon.csv. Ningun script lo genera: run_stats_analysis.py escribe exactamente cuatro CSV (lineas 42, 77, 86 y 148: descriptive_means.csv, ranking_methods.csv, friedman_results.csv y wilcoxon_results.csv), y la cadena «wilcoxon_propuesta_vs_metodos» no aparece en ningun .py del arbol. La aritmetica y el desglose si son correctos esta vez: wilcoxon_results.csv tiene 54 filas con tophat=Propuesta_Novedosa (9 por cada uno de Curvelet, DTCWT, DWT, PiramideLaplace, RatioPiramide y TopHat_Clasico) y 45 con tophat=TopHat_Clasico. O sea que los 54 contrastes existen, pero dentro de wilcoxon_results.csv, el archivo que el mismo parrafo cita tres frases antes; la frase es redundante y apunta a un archivo inexistente. Es residuo de una version anterior: docs/fuentes/reverificacion_hallazgos.json ya lo habia senalado (la version vieja decia «48 contrastes ... 9 x 4 rivales»); se corrigieron los numeros pero se dejo el nombre del archivo.

*(bloque: Parrafos 482-521 - Capitulo 8 APENDICE (A. Repositorio del codigo; B. Configuraciones del barrido PSO; C. Tablas estadisticas extendidas; D. Pseudocodigos; E. Refinamiento de la regla de fusion; F. Hardware y tiempos))*

### Tabla 2 «Configuración de la Propuesta Novedosa y del PSO» (d.tables[11]), última fila — CONTRADICE

> Óptimo hallado | r = 25; m = 0,30 (m* del barrido en las 25 configuraciones; Fo = 1,7057)

**El dato:** experiments/results/metrics_reports/pso_grid_search_fo_propuesta.csv: el máximo de Fo_opt en las 25 configuraciones es 1,7350 con r_opt = 1 y m_opt = 0,30, y se alcanza en 16 de las 25 filas. El valor 1,7057 (r_opt = 25) aparece en solo 8 filas, y la fila n=2/T=10 da 1,6990 con r_opt = 14. La rejilla exhaustiva optimo_exacto_fo.csv (5.000 puntos) lo confirma: restringida al rango publicado m >= 0,30, su máximo es r = 1, m = 0,30, Fo = 1,7349913, mientras r = 25, m = 0,30 vale Fo = 1,7056961. Es decir, r = 25 con Fo = 1,7057 no es ni el mejor del barrido ni el óptimo exacto; es el segundo valor más frecuente del barrido.

*(bloque: Las 38 tablas de docs/Tesis_Borrador_V3.docx (d.tables), verificadas celda por celda contra los CSV de experiments/results/metrics_reports/ y, donde fue posible, recomputadas desde los datos por imagen.)*

### Tabla 2 (d.tables[11], fila «Escala (radio)») y tabla de operacionalización de las variables de §4.4 (d.tables[26], fila «Radio del SE (r)») — CONTRADICE

> Escala (radio) | Única, de radio r (ajustado por PSO)  —y— Radio del SE (r) | ... | 1–25 (ajustado por PSO)

**El dato:** El PSO no arroja r = 25: en pso_grid_search_fo_propuesta.csv devuelve r_opt = 1 en 16 de 25 configuraciones, r_opt = 25 en 8 y r_opt = 14 en 1. El r = 25 adoptado proviene de otro criterio: ajuste_comparativos_mejores.csv marca Propuesta_Novedosa|25 con elegida=True y rango_interno_9 = 4,867, es decir fue elegido por el promedio de rangos sobre las nueve métricas de evaluación (run_ajuste_comparativos.py), no por la función de aptitud Fo. El propio libro lo dice en el epígrafe de la Figura 10 («r = 25 por diseño»), de modo que la atribución al PSO en estas dos tablas contradice tanto el CSV como el resto del texto. En cambio m = 0,30 sí es del PSO: m_opt = 0,30 en las 25 configuraciones.

*(bloque: Las 38 tablas de docs/Tesis_Borrador_V3.docx (d.tables), verificadas celda por celda contra los CSV de experiments/results/metrics_reports/ y, donde fue posible, recomputadas desde los datos por imagen.)*

### parrafo 338, §4.3 Diseno — CONTRADICE

> la configuracion optima resultante (r = 25, m = 0,30) se compara sobre los 20 pares con las nueve metricas

**El dato:** experiments/results/metrics_reports/pso_grid_search_fo_propuesta.csv: de las 25 configuraciones, 16 devuelven r_opt = 1 con Fo_opt = 1,7350, ocho devuelven r_opt = 25 con Fo_opt = 1,7057 y una r_opt = 14 (1,6990); el maximo del barrido es r = 1. experiments/results/metrics_reports/optimo_exacto_fo.csv (rejilla exhaustiva 5.000 puntos): dentro del rango publicado m >= 0,30 el argmax es r = 1, m = 0,30, Fo = 1,734991, mientras que (r = 25, m = 0,30) da Fo = 1,705696; el argmax global es r = 25, m = 0,07 con Fo = 1,771465. Es decir, r = 25 no es optimo de la aptitud en ninguna lectura. La configuracion realmente evaluada si es r = 25, m = 0,30 (all_metrics.config.json), pero proviene de la bateria de evaluacion, no del PSO: el propio libro lo dice en el parrafo 418 («El argmax de la aptitud dentro del rango publicado es r = 1 (Fo = 1,7350) y no r = 25 (1,7057)»), en el 423 («r=25 adoptado como decision de diseno») y en la limitacion Novena del parrafo 229 («la configuracion adoptada se apoya en el criterio de evaluacion y no en la optimizacion, que si determina el peso m»)

*(bloque: Parrafos 299-346 (cap. 3 MARCO CONCEPTUAL y cap. 4 MARCO METODOLOGICO), mas la Tabla 26 de operacionalizacion que cuelga del parrafo 339)*

### parrafo 329, §3.15 PSO; y fila «Radio del SE (r) ... 1-25 (ajustado por PSO)» de la Tabla 26 (§4.4) — INCOHERENCIA

> En esta tesis ajusta automaticamente los hiperparametros (r, m) dla Propuesta Novedosa

**El dato:** El PSO determina solo m: en las 25 filas de pso_grid_search_fo_propuesta.csv m_opt = 0,30 sin excepcion (piso del rango LO=[1,0.30], HI=[25,2.00] de experiments/pso_grid_search_fo.py), y optimo_exacto_fo.csv muestra que Fo decrece estrictamente en m desde m = 0,07 (r=25: 1,771465 en m=0,07 -> 1,705696 en m=0,30 -> 1,206633 en m=2,00). El radio no lo fija el PSO: 16 de las 25 configuraciones apuntan a r = 1 y el libro mismo lo declara decision de diseno en los parrafos 418, 423 y en la limitacion Novena. La Tabla 26 repite la atribucion al PSO para r. Nota menor de tipeo en el mismo parrafo: «(r, m) dla Propuesta» por «de la Propuesta»

*(bloque: Parrafos 299-346 (cap. 3 MARCO CONCEPTUAL y cap. 4 MARCO METODOLOGICO), mas la Tabla 26 de operacionalizacion que cuelga del parrafo 339)*

### Tabla 2 «Configuracion de la Propuesta Novedosa y del PSO», ultima fila (tabla que sigue al parrafo 277, seccion 2.2.5) — CONTRADICE

> Optimo hallado: r = 25; m = 0,30 (m* del barrido en las 25 configuraciones; Fo = 1,7057)

**El dato:** El optimo de Fo dentro del rango publicado NO es r = 25. pso_grid_search_fo_propuesta.csv: 15 de las 25 configuraciones devuelven r_opt = 1 con Fo_opt = 1,7350, y las 10 restantes r_opt = 25 con Fo_opt = 1,7057 (el maximo de la columna Fo_opt es 1,7350). optimo_exacto_fo.csv (enumeracion exacta de los 25 radios x 200 pesos): argmax con m >= 0,30 en r = 1, m = 0,30, Fo = 1,734991; en r = 25, m = 0,30 da 1,705696. El valor 1,7057 de la celda es correcto, pero corresponde a la configuracion ADOPTADA, no al optimo; el propio libro lo dice en 5.8.5 («El argmax de la aptitud dentro del rango publicado es r = 1 (Fo = 1,7350) y no r = 25 (1,7057)») y en la limitacion novena. Solo m* = 0,30 es resultado del barrido.

*(bloque: Parrafos 202-298: capitulo 1 PROBLEMA DE INVESTIGACION y capitulo 2 MARCO TEORICO (incluye la Tabla 2 «Configuracion de la Propuesta Novedosa y del PSO» y la Tabla 3 «Metodos comparativos»))*


## Gravedad media (29)

### parrafo 377 (§5.5, tercera lectura de la Tabla 8) — CONTRADICE

> el infrarrojo solo es la modalidad mas fuerte (mAP@0,5 = 0,971; mAP@0,5:0,95 = 0,621)

**El dato:** Esas dos cifras son la corrida de UNA semilla: detection_llvip_map.csv, fila method=IR, mAP50=0,9708 y mAP50_95=0,6211 (equivale a detection_llvip_semillas.csv, IR semilla=0). La Tabla 8 del propio libro publica medias de 5 semillas: IR 0,961 +- 0,0139 y 0,592 +- 0,0259, que es lo que dice semillas_llvip_resumen.csv (mAP50_media=0,9611, mAP50_95_media=0,5919). El mismo parrafo usa medias para todo lo demas (VIS 0,795, LP 0,952, DTCWT 0,936, propuesta 0,9283), asi que mezcla dos bases en una sola oracion y contradice la tabla que esta interpretando. El parrafo 399 del libro ya usa el 0,961 correcto. La conclusion de fondo se sostiene: con medias, IR 0,9611 sigue por encima de toda fusion (mejor fusion LP 0,9517) y en mAP@0,5:0,95 IR 0,5919 supera a la mejor fusion (DTCWT 0,5894).

*(bloque: Parrafos 347-385 (capitulo 5, primera parte: calidad de imagen §5.1-5.4 y evaluacion orientada a tarea §5.5), mas las Tablas 4, 5, 6, 7, 8 y 9 del libro (indices python-docx 27, 28, 29, 30, 31, 32))*

### parrafo 377 (§5.5, primera lectura de la Tabla 8); la misma cifra se repite en el parrafo 399 — CONTRADICE

> toda fusion mejora con claridad sobre el visible solo (0,795 de media frente a una banda de 0,904-0,952, en las 5 semillas, es decir entre +0,09 y +0,14 puntos)

**El dato:** La resta de las cifras que el propio parrafo enuncia da otro resultado: semillas_llvip_resumen.csv, VIS mAP50_media=0,7951; banda de medias de fusion de RatioPiramide 0,9043 a PiramideLaplace 0,9517. 0,9043-0,7951=+0,109 y 0,9517-0,7951=+0,157, o sea entre +0,11 y +0,16, no +0,09 y +0,14. El +0,09/+0,14 sale de restar contra 0,8133, que es el VIS de una sola semilla (detection_llvip_map.csv fila VIS, mAP50=0,8133; tambien el mAP50_max de VIS en semillas_llvip_resumen.csv): 0,9043-0,8133=0,0910 y 0,9517-0,8133=0,1384. Es un resto del calculo viejo con una semilla y subestima la propia ventaja de la fusion.

*(bloque: Parrafos 347-385 (capitulo 5, primera parte: calidad de imagen §5.1-5.4 y evaluacion orientada a tarea §5.5), mas las Tablas 4, 5, 6, 7, 8 y 9 del libro (indices python-docx 27, 28, 29, 30, 31, 32))*

### parrafo 368 (§5.4.2 Comparaciones pareadas Wilcoxon) — CONTRADICE

> cede de manera sistematica en las metricas de fidelidad a las fuentes (SSIM, PSNR) y en la informacion mutua, donde lideran los metodos multiescala

**El dato:** En SSIM si es sistematico: wilcoxon_results.csv filas 77-81, la propuesta pierde significativamente contra los cinco comparativos. En PSNR no: fila 91 (metric=PSNR, tophat=Propuesta_Novedosa, baseline=PiramideLaplace) da diff=+1,9009, effect_r=+0,990, p_holm=0,000021, sig_holm_05=True: la propuesta GANA el PSNR contra la piramide de Laplace de forma significativa, y la Laplace es precisamente un metodo multiescala y el peor PSNR del banco (descriptive_means.csv, PSNR=14,9401, el minimo de los siete; rango medio 6,95 en ranking_methods.csv). Son 4 de 5 derrotas, no cinco. En informacion mutua tampoco: filas 48 (MI_vis vs RatioPiramide, p_holm=0,2162) y 59 (MI_ir vs RatioPiramide, p_holm=0,1231) son no significativas, o sea 4 de 5 en cada una de las dos MI. La palabra «sistematica» sobreafirma tres de las cuatro metricas citadas.

*(bloque: Parrafos 347-385 (capitulo 5, primera parte: calidad de imagen §5.1-5.4 y evaluacion orientada a tarea §5.5), mas las Tablas 4, 5, 6, 7, 8 y 9 del libro (indices python-docx 27, 28, 29, 30, 31, 32))*

### párrafo 428 (conclusión específica 6) — SIN FUENTE

> el radio gobierna la escala de las estructuras que el operador extrae —la aptitud del trabajo de referencia favorece r = 1 y la batería de evaluación r = 25—

**El dato:** La primera mitad sí está: optimo_exacto_fo.csv da con m ≥ 0,30 el máximo en r = 1 (Fo = 1,734991) frente a r = 25 (1,705696). La segunda mitad no tiene CSV. Busqué un barrido de radios sobre la batería de nueve: barrido_metricas_vs_m.csv solo tiene la propuesta en r = 25 (11 pesos; el clásico en r = 5 y r = 25); all_metrics.csv solo contiene la configuración r = 25; y en las tablas del libro solo la Tabla 36 fija r = 25 sin comparar radios. El único CSV que compara los dos radios es comparacion_aptitudes.csv / comparacion_aptitudes_wilcoxon.csv, y ahí (r = 1; m = 0,30) frente a (r = 25; m = 0,070) sale 4 a 4 en la batería de nueve: r = 25 gana EN, SD, FE y SSIM; r = 1 gana MG, MI_vis, MI_ir y SF (PSNR no figura). O sea que ni con pesos distintos la batería «favorece r = 25».

*(bloque: Párrafos 420–442 — Capítulo 6 CONCLUSIONES Y RECOMENDACIONES)*

### párrafo 441 (recomendación 7) — SIN FUENTE

> la metodología clásica Top-Hat conserva su valor como referencia interpretable y de muy bajo costo computacional

**El dato:** Ningún CSV mide el costo de las fusiones. Recorrí las columnas de los 50 CSV de metrics_reports buscando tiempo: solo hay 'segundos' en detection_llvip_semillas.csv (entrenamiento de YOLO) y en pso_grid_search*.csv / pso_repeticiones*.csv (corridas del enjambre). La única fuente de la cifra es el Apéndice F (párrafo 520: «entre 20 y 80 milisegundos», «90 segundos el benchmark»), que es texto sin CSV ni script asociado. Además ese mismo apéndice dice que «la pirámide de Laplace y el curvelet se sitúan en órdenes de magnitud comparables», lo que quita al Top-Hat el «muy bajo costo» como ventaja diferencial.

*(bloque: Párrafos 420–442 — Capítulo 6 CONCLUSIONES Y RECOMENDACIONES)*

### párrafo 431 (conclusión específica 9) — SIN FUENTE

> aplicar selección por actividad a la capa base introduce discontinuidades de iluminación y sesga las métricas de información mutua. Este aprendizaje es transferible a cualquier descomposición multiescala.

**El dato:** No existe ninguna corrida con la base fusionada por máxima actividad. Los seis brazos de ablacion_banco.csv comparten la misma reconstrucción (run_ablacion_banco.py, línea 58: f = base + m*max(wv,wi) - m*max(bv,bi)), y control_negativo.csv solo agrega desenfoques, ruidos y comparativos. La única fuente es el Apéndice (párrafo 518), que lo declara como observación del desarrollo iterativo («Durante el desarrollo iterativo … se identificó») y no como medición; ese apéndice tampoco menciona discontinuidades de iluminación ni sesgo de MI, y aclara que el punto concierne a los comparativos multiescala y no al operador propuesto. Las dos consecuencias afirmadas (discontinuidades, sesgo de MI) y la generalización a «cualquier descomposición multiescala» no están medidas.

*(bloque: Párrafos 420–442 — Capítulo 6 CONCLUSIONES Y RECOMENDACIONES)*

### párrafo 437 (recomendación 3) — INCOHERENCIA

> Replicar la evaluación sobre datasets adicionales (RoadScene, M3FD, MS-COCO multiespectral) para verificar la transferibilidad de las conclusiones.

**El dato:** La recomendación propone como trabajo futuro algo que el trabajo ya hizo: M3FD está evaluado en detection_m3fd_map.csv (9 entradas, mAP y AP50 por clase), en complementariedad_por_escena.csv / complementariedad_resumen.csv / complementariedad_criticas.csv (232 escenas) y en correlacion_calidad_deteccion.csv (filas dataset = M3FD), con script propio en experiments/detection_m3fd/train_eval_m3fd.py. El propio capítulo 6 lo usa dos veces (párrafos 423 y 435). RoadScene y MS-COCO multiespectral sí quedan pendientes.

*(bloque: Párrafos 420–442 — Capítulo 6 CONCLUSIONES Y RECOMENDACIONES)*

### párrafo 428 (conclusión específica 6) — INCOHERENCIA

> la aptitud del trabajo de referencia favorece r = 1

**El dato:** Enunciado sin la salvedad que la propia tesis demostró, queda al revés de §5.8.5. optimo_exacto_fo.csv: con el peso atado al piso heredado (m ≥ 0,30) el máximo está en r = 1 (1,734991), pero con el peso libre el máximo global está en r = 25, m = 0,070 (Fo = 1,771465) y r = 1 pasa a ser el PEOR radio (mejor Fo 1,760748, monótono creciente en r de 1,7607 a 1,7715). El párrafo 418 lo dice explícitamente: «El orden de los radios se invierte … r = 1 pasa a ser el peor». La conclusión 6 conserva la lectura vieja.

*(bloque: Párrafos 420–442 — Capítulo 6 CONCLUSIONES Y RECOMENDACIONES)*

### párrafo 441 (recomendación 7) — INCOHERENCIA

> para aplicaciones donde prima la fidelidad a las fuentes, los métodos multiescala (DTCWT, CVT) siguen siendo preferibles

**El dato:** Vale para SSIM y PSNR, no para la información mutua. descriptive_means.csv: DTCWT lidera SSIM (0,7249) y Curvelet PSNR (17,6523), pero en MI con las fuentes la pirámide de Laplace los duplica (MI_vis 1,9242 frente a 1,0781 de DTCWT y 1,0961 de CVT; MI_ir 0,9178 frente a 0,6728 y 0,6695), y ranking_methods.csv le da a LP el mejor rango medio en ambas (1,85 y 2,20 frente a 3,25/3,30 de DTCWT y 2,65/3,20 de CVT). El párrafo 424 del mismo capítulo se lo atribuye a la pirámide («la pirámide de Laplace … la información mutua con las fuentes»). Conviene precisar de qué fidelidad se habla.

*(bloque: Párrafos 420–442 — Capítulo 6 CONCLUSIONES Y RECOMENDACIONES)*

### Parrafo 83 (RESUMEN); identico en el parrafo 86 del SUMMARY ('tuned automatically by PSO' + 'r=25 by design') — INCOHERENCIA

> el radio r del banco de elementos estructurantes y el peso de contraste m se ajustan automaticamente por Optimizacion por Enjambre de Particulas (PSO) [...] En su configuracion optima (r=25 por diseno; m=0,30, el piso del rango de busqueda)

**El dato:** La misma frase afirma y desmiente que el PSO fije r. El CSV confirma que NO lo fija: en pso_grid_search_fo_propuesta.csv (25 filas, columnas r_opt y Fo_opt) la aptitud es MAYOR con r=1 (Fo_opt = 1,7350 en 15 de las 25 configuraciones) que con r=25 (Fo_opt = 1,7057 en 9), o sea que r=25 es peor para el criterio que supuestamente lo eligio. El propio codigo lo declara (experiments/make_avances_excel.py: 'El radio NO lo fija el PSO [...] r = 25 es una decision de diseno tomada sobre las metricas de evaluacion'). Ademas, ambos parametros adoptados caen en un borde del rango de busqueda r en [1,25] y m en [0,30;2,00] (make_avances_excel.py, 'Rango de busqueda'): el texto lo aclara para m ('el piso del rango') pero no para r, que es el techo. Llamarla 'configuracion optima' sin decir respecto de que induce a error.

*(bloque: Parrafos 82-167: RESUMEN (p. 83) y SUMMARY (p. 86). Los parrafos 88-167 son el indice de CONTENIDO (titulos y numeros de pagina), sin afirmaciones empiricas.)*

### Parrafo 83 (RESUMEN) y parrafo 86 (SUMMARY), tres pasajes cada uno — INCOHERENCIA

> lidera la entropia y la eficiencia de fusion del estudio (EN=6,9855; FE=1,1047) [...] con ventaja estadisticamente significativa sobre los cinco metodos del estado del arte en EN, FE, MG y SF [...] superando de forma significativa al estado del arte en cuatro de las nueve metricas

**El dato:** Las cifras son exactas, pero EN y FE no son dos metricas independientes: verifique en all_metrics.csv que los rangos intra-par de EN y FE son IDENTICOS en los 20 pares (FE es EN dividida por una constante propia de cada par), y esto se ve tambien en friedman_results.csv (EN y FE comparten chi2 = 88,2857 y p = 6,876e-17) y en ranking_methods.csv (columnas EN y FE identicas fila por fila: 1,5 / 3,25 / 2,45 / 3,55 / 4,9 / 5,5 / 6,85). Por lo tanto 'cuatro de las nueve metricas' son en realidad tres resultados independientes (EN=FE, MG, SF), y 'lidera la entropia y la eficiencia de fusion' enuncia dos veces el mismo hecho. El repositorio ya reconoce el problema con la columna avg_rank_sin_FE de ranking_methods.csv, que el resumen no menciona.

*(bloque: Parrafos 82-167: RESUMEN (p. 83) y SUMMARY (p. 86). Los parrafos 88-167 son el indice de CONTENIDO (titulos y numeros de pagina), sin afirmaciones empiricas.)*

### parrafo 399, quinta observacion de la Discusion integrada (la frase abre con «la evaluacion orientada a tarea (deteccion sobre LLVIP, repetida con 5 semillas de entrenamiento por entrada)») — CONTRADICE

> toda fusion supera netamente al visible solo (+0,09 a +0,14 en mAP@0,5)

**El dato:** semillas_llvip_resumen.csv, columna mAP50_media: VIS = 0,7951 y las siete fusiones van de 0,9043 (RatioPiramide) a 0,9517 (PiramideLaplace), o sea de +0,109 a +0,157, no de +0,09 a +0,14. El rango que el libro escribe es el de la corrida de UNA sola semilla: detection_llvip_map.csv da VIS = 0,8133 y fusiones de 0,9056 a 0,9515, es decir +0,092 a +0,138. La cifra quedo sin actualizar cuando se paso a las cinco semillas. La conclusion 1 (parrafo 423) SI reporta el rango de cinco semillas bien («0,795 de media frente a 0,904-0,952, en las 5 semillas»), de modo que el libro se contradice consigo mismo entre §5.7 y §6.1.

*(bloque: Parrafos 386 a 419 (§5.6 Propuesta Novedosa, §5.7 Discusion integrada, §5.8 Auditoria del protocolo: 5.8.1 a 5.8.5) mas las Tablas 10, 11, 12, 13 y 14 del docx (indices python-docx 33, 34, 35, 36 y 37))*

### parrafo 419, cierre de §5.8.5 — SIN FUENTE

> Se sostiene H6, y con muestra suficiente: la hipotesis de que la mejora en las metricas de imagen se traslade a la tarea de deteccion queda rechazada, no simplemente sin confirmar.

**El dato:** El unico calculo de potencia del repositorio es potencia_mcnemar.csv (lo produce experiments/potencia_mcnemar.py). Con los n = 23 discordantes del conteo por escena la potencia llega a 0,80 solo a partir de delta = 5,8 puntos porcentuales (fila delta_pp = 5,8 -> potencia 0,816; delta_pp = 5,7 -> 0,799), y en la diferencia realmente observada de 3,0 pp la potencia es 0,258 (fila delta_pp = 3,0). Los dos contrastes que el parrafo cita no rechazan nada: Spearman p = 0,432 y McNemar p = 0,2100. La afirmacion de suficiencia es correcta unicamente si se le agrega el calificador «para diferencias de 5,8 puntos porcentuales o mas», que el parrafo no pone y cuya cifra no cita. El docstring de experiments/potencia_mcnemar.py senala exactamente esta frase: «Esa frase no tenia ningun calculo detras, y ademas es delicada».

*(bloque: Parrafos 386 a 419 (§5.6 Propuesta Novedosa, §5.7 Discusion integrada, §5.8 Auditoria del protocolo: 5.8.1 a 5.8.5) mas las Tablas 10, 11, 12, 13 y 14 del docx (indices python-docx 33, 34, 35, 36 y 37))*

### parrafo 412, §5.8.3 (lectura de la Tabla 13) — CONTRADICE

> lo que si queda firme en todas las composiciones es que el merito no proviene de la imagen base

**El dato:** ablacion_banco_resumen.csv, columna rango_9_sin_FE: base = 3,506 queda 5.a de los seis brazos, POR DELANTE del brazo de las lineas solas (3,631) y a solo 0,006 de la suma que adopta la propuesta (3,500). O sea que en la composicion sin FE —la que el propio parrafo propone como la lectura prudente— la imagen base no queda ultima y le gana a uno de los brazos del operador. El «en todas las composiciones» solo se cumple en las columnas rango_9 (base 3,783, ultima empatada) y rango_17 (base 4,359, ultima).

*(bloque: Parrafos 386 a 419 (§5.6 Propuesta Novedosa, §5.7 Discusion integrada, §5.8 Auditoria del protocolo: 5.8.1 a 5.8.5) mas las Tablas 10, 11, 12, 13 y 14 del docx (indices python-docx 33, 34, 35, 36 y 37))*

### parrafo 484 (apendice A, inventario de modulos) — CONTRADICE

> src/metrics/evaluators.py (las nueve metricas)

**El dato:** El modulo calcula DIECISIETE metricas, no nueve. El docstring de evaluate_all lo enumera: «Claves: EN, SD, FE, MG, MI_vis, MI_ir, SF, SSIM, PSNR, Qabf, Nabf, SCD, VIF, FMI, Q0, QW, QE», y METRIC_DIRECTION (lineas 28-33) declara direccion para esas mismas 17. experiments/results/metrics_reports/all_metrics.csv tiene 19 columnas: method, image y las 17 metricas. Las nueve son un subconjunto que selecciona otro archivo: experiments/run_stats_analysis.py, linea 31, METRICS = ["EN", "SD", "FE", "MG", "MI_vis", "MI_ir", "SF", "SSIM", "PSNR"], con el comentario «Se descartan Qabf, Nabf, SCD, VIF y las del review (FMI, Q0, QW, QE)». En un apendice que promete reproducibilidad la atribucion importa: quien clone el repo y ejecute evaluators.py obtiene 17 columnas, y las cuatro metricas del review (FMI, Q0, QW, QE) y Nabf sostienen las secciones 5.8.1 y los CSV ranking_mas_nabf.csv y escenas_distintas.csv.

*(bloque: Parrafos 482-521 - Capitulo 8 APENDICE (A. Repositorio del codigo; B. Configuraciones del barrido PSO; C. Tablas estadisticas extendidas; D. Pseudocodigos; E. Refinamiento de la regla de fusion; F. Hardware y tiempos))*

### parrafo 519 (apendice F) — CONTRADICE

> Cada fusion Top-Hat consume entre 20 y 80 milisegundos segun la configuracion

**El dato:** El intervalo no contiene ninguna de las dos configuraciones Top-Hat del benchmark. Medicion directa (mediana de 5 corridas, par APC_1_view_1_fk_06_005, 439x609, mismo interprete del repo): Propuesta_Novedosa con r=25 y m=0,30 -la configuracion adoptada, CONFIG de run_all_fusions.py- 168,1 ms; TopHat_Clasico con r=5 11,6 ms. Es decir, la adoptada cuesta mas del doble del techo declarado y la clasica esta por debajo del piso. El CSV lo corrobora sin necesidad de cronometrar: en pso_grid_search_fo_propuesta.csv el cociente segundos/evaluaciones vale 0,799 s de media en las 8 filas que convergen a r_opt=25 (min 0,75, max 0,833) frente a 0,203 s en las 16 que convergen a r_opt=1; como cada evaluacion de aptitud fusiona las 3 escenas del cache (list_pairs()[::7], las tres que imprime el script), eso da unos 266 ms por fusion a radio grande contra unos 68 ms a radio 1. La cifra a corregir es el techo: con r=25 el banco aplica un disco de 51x51 y cuatro lineas de longitud 51.

*(bloque: Parrafos 482-521 - Capitulo 8 APENDICE (A. Repositorio del codigo; B. Configuraciones del barrido PSO; C. Tablas estadisticas extendidas; D. Pseudocodigos; E. Refinamiento de la regla de fusion; F. Hardware y tiempos))*

### parrafo 484 (apendice A) — INCOHERENCIA

> La totalidad del codigo de esta tesis esta disponible en el repositorio del proyecto, organizado en modulos: [lista de nueve modulos y carpetas]

**El dato:** El inventario omite los scripts que producen varios resultados centrales del libro, y la frase promete «la totalidad del codigo». Faltan, todos existentes y todos con CSV publicado: experiments/detection_m3fd/ (prepare_m3fd.py y train_eval_m3fd.py), que sostiene el experimento de clases complementarias del parrafo 380 y produce detection_m3fd_map.csv, figura_detecciones_m3fd.json y arquitectura_yolo.json -el apendice nombra solo detection_llvip/-; experiments/run_ablacion_banco.py, que produce ablacion_banco.csv, ablacion_banco_resumen.csv y ablacion_banco_contrastes.csv, base de la Tabla 13 y de la seccion 5.8.3 (H7); experiments/optimo_exacto_fo.py, que produce optimo_exacto_fo.csv, el barrido determinista que la seccion 5.8.5 usa para acotar el alcance de H5; experiments/pso_repeticiones.py, que produce las cuatro tablas de repeticiones del estudio de estabilidad; experiments/run_control_negativo.py (seccion 5.8.2, H3) y experiments/run_ajuste_comparativos.py (seccion 5.8.4). En total el directorio experiments/ tiene 46 scripts y el apendice nombra cuatro. Verificado en cambio: los diez archivos y carpetas que si nombra existen todos, y detection_llvip/ contiene exactamente los tres roles que el texto le atribuye (prepare_llvip.py, train_eval_llvip.py, run_semillas_llvip.py).

*(bloque: Parrafos 482-521 - Capitulo 8 APENDICE (A. Repositorio del codigo; B. Configuraciones del barrido PSO; C. Tablas estadisticas extendidas; D. Pseudocodigos; E. Refinamiento de la regla de fusion; F. Hardware y tiempos))*

### parrafo 518 (apendice E, ultima frase) — SIN FUENTE

> El refinamiento elimino discontinuidades de iluminacion y sesgos artificiales en la informacion mutua.

**El dato:** Ningun CSV documenta un antes/despues de ese refinamiento. Los unicos respaldos con nombre de copia en metrics_reports son all_metrics.csv.bak_m0703 y all_metrics.csv.bak_n20, que corresponden a otro peso (m=0,0703) y a otro corpus (n=20 pares), no a un cambio en la regla de fusion. Y en el sentido contrario: el sesgo en la informacion mutua sigue presente, porque la piramide de Laplace conserva la base por maxima actividad local (ver el hallazgo del mismo parrafo). Al recalcular la LP con la base promediada, MI_vis cae de 1,9242 a 1,1171 y MI_ir de 0,9178 a 0,6885; los valores altos son los que estan en all_metrics.csv. La «discontinuidad de iluminacion» tambien es visible en el dato publicado: descriptive_means.csv da a PiramideLaplace el peor PSNR de los siete metodos (14,9401 frente a 17,6523 de Curvelet), que es el sintoma esperable de una base tomada pixel a pixel de una u otra fuente.

*(bloque: Parrafos 482-521 - Capitulo 8 APENDICE (A. Repositorio del codigo; B. Configuraciones del barrido PSO; C. Tablas estadisticas extendidas; D. Pseudocodigos; E. Refinamiento de la regla de fusion; F. Hardware y tiempos))*

### parrafo 519 (apendice F, ultima frase) — SIN FUENTE

> Esta liviandad computacional confirma la viabilidad del metodo para aplicaciones en tiempo real.

**El dato:** Ningun CSV del repositorio mide latencia ni cuadros por segundo del operador; las unicas columnas de tiempo en metrics_reports son «segundos» en pso_grid_search.csv, pso_grid_search_fo_propuesta.csv, pso_grid_search_fo_clasico.csv, las dos de pso_repeticiones y detection_llvip_semillas.csv, y ninguna cronometra una fusion aislada (run_all_fusions.py no importa time ni mide nada). Ademas la medicion directa va en contra: la configuracion adoptada (r=25, m=0,30) tarda 168,1 ms por par de 439x609, es decir unos 6 cuadros por segundo en una sola escala y sin contar captura ni registro, lo que no sostiene «tiempo real» sin calificar la resolucion y la tasa objetivo. Conviene o retirar la frase o acotarla a la resolucion y al radio medidos.

*(bloque: Parrafos 482-521 - Capitulo 8 APENDICE (A. Repositorio del codigo; B. Configuraciones del barrido PSO; C. Tablas estadisticas extendidas; D. Pseudocodigos; E. Refinamiento de la regla de fusion; F. Hardware y tiempos))*

### Tabla de métricas al cierre de §2.2.7, la que sigue a la ecuación (26) (d.tables[25]) — INCOHERENCIA

> Métrica | Definición operativa | Interpretación | Dirección — con doce filas: EN, SD, FE, MG, MI_vis, MI_ir, SF, Qabf, Nabf, SSIM, SCD, VIF

**El dato:** La tabla no cubre ninguno de los dos conjuntos que el libro usa después. Omite PSNR, que es una de las nueve métricas del criterio principal y aparece en las Tablas 5, 6, 7, 12, 13 y 14 (columna PSNR de all_metrics.csv y de ranking_methods.csv). Y omite FMI, Q0, QW y QE, que sí integran el conjunto de diecisiete de las columnas «Con 17» de las Tablas 12, 13 y 14 (METRIC_DIRECTION en src/metrics/evaluators.py tiene exactamente 17 entradas: las 9 más Qabf, Nabf, SCD, VIF, FMI, Q0, QW, QE). El lector no encuentra en el marco la definición de PSNR ni de los cuatro índices de Piella y Haghighat que después ve rankeados.

*(bloque: Las 38 tablas de docs/Tesis_Borrador_V3.docx (d.tables), verificadas celda por celda contra los CSV de experiments/results/metrics_reports/ y, donde fue posible, recomputadas desde los datos por imagen.)*

### Tabla 8 «Detección de peatones en LLVIP» (d.tables[31]), fila de encabezado y las nueve filas de datos — INCOHERENCIA

> Encabezados «mAP@0,5 ↑ (media ± desv.)» y «mAP@0,5:0,95 ↑ (media ± desv.)» frente a «Precisión ↑» y «Recall ↑» sin rótulo

**El dato:** Las columnas de precisión y recall también son medias sobre las cinco semillas, pero el encabezado no lo dice. Recomputado desde detection_llvip_semillas.csv (5 filas por método): Propuesta_Novedosa precisión media 0,9438 y recall medio 0,8285, que son los 0,944 y 0,828 impresos. En cambio detection_llvip_map.csv —el CSV de una sola corrida, semilla 0— da para Propuesta_Novedosa precisión 0,8756 y recall 0,7613. Quien contraste la tabla con ese archivo encontrará una brecha de casi 0,07 punto y creerá que hay un error donde no lo hay. Conviene extender «(media ± desv.)» o al menos «(media)» a las cuatro columnas.

*(bloque: Las 38 tablas de docs/Tesis_Borrador_V3.docx (d.tables), verificadas celda por celda contra los CSV de experiments/results/metrics_reports/ y, donde fue posible, recomputadas desde los datos por imagen.)*

### parrafo 338, §4.3 Diseno — SIN FUENTE

> seleccionando la configuracion del enjambre con un barrido de 25 combinaciones (particulas 2-10 x iteraciones 10-50 ...) sobre un subconjunto de tres escenas representativas

**El dato:** El barrido de 25 combinaciones existe y coincide (pso_grid_search_fo_propuesta.csv, 25 filas con n en {2,4,6,8,10} y Tmax en {10,20,30,40,50}; tres escenas = list_pairs()[::7] -> APC_1_view_1, Athena_APC_4_fennek01, Athena_soldier_behind_smoke_3, tres escenas distintas). Lo que no tiene respaldo es la «seleccion»: ningun CSV registra cual par (n, Tmax) quedo adoptado, y las configuraciones no convergen a un mismo resultado (16 dan r=1, 8 dan r=25, 1 da r=14). pso_repeticiones_resumen_propuesta.csv confirma la inestabilidad: sobre 20 corridas por configuracion, la moda de r alterna entre 1 y 25 y pct_r1 va de 20 % a 65 %. Busque en los 50 CSV de metrics_reports y en experiments/make_reporte_optimos.py, eval_fo_optima.py y analizar_repeticiones.py un artefacto que declare la configuracion elegida del enjambre; no existe

*(bloque: Parrafos 299-346 (cap. 3 MARCO CONCEPTUAL y cap. 4 MARCO METODOLOGICO), mas la Tabla 26 de operacionalizacion que cuelga del parrafo 339)*

### parrafo 342, §4.5 Dataset y preprocesamiento — INCOHERENCIA

> reentrenando el detector YOLOv8n durante 40 epocas con configuracion identica en todas las modalidades

**El dato:** Las 40 epocas, el checkpoint de partida y la configuracion identica se verifican (runs/detect/runs/llvip/*/args.yaml: model yolov8n.pt, epochs 40, seed 0, imgsz 640, batch 16, deterministic True en las 12 modalidades). Lo que falta declarar es el protocolo de checkpoint evaluado: experiments/detection_llvip/train_eval_llvip.py usa --pesos last por defecto y todas las filas de detection_llvip_map.csv y detection_llvip_semillas.csv traen checkpoint = last. El propio script explica que la decision importa («con best.pt se reporta el MAXIMO sobre las epocas medido en el mismo conjunto que se reporta ... sesgo optimista del orden de las diferencias entre metodos», porque LLVIP no tiene test disjunto y el val cumple los dos roles). Busque «pesos», «best», «ultima epoca» y «checkpoint» en los 521 parrafos del libro: no aparece en ninguno

*(bloque: Parrafos 299-346 (cap. 3 MARCO CONCEPTUAL y cap. 4 MARCO METODOLOGICO), mas la Tabla 26 de operacionalizacion que cuelga del parrafo 339)*

### parrafo 342, §4.5 — INCOHERENCIA

> Se utilizo un subconjunto de 2.000 imagenes de entrenamiento y 500 de validacion por modalidad (VIS, IR y cada fusion), reentrenando el detector YOLOv8n

**El dato:** Los tamanos son exactos: las 12 carpetas datasets/llvip_* tienen 2.000 imagenes en images/train y 500 en images/val. Pero el metodo describe un solo entrenamiento por modalidad, y el experimento que sostiene §5.5.1 son cinco semillas: detection_llvip_semillas.csv tiene 45 filas (9 entradas x semillas 0-4), semillas_llvip_resumen.csv reporta n_semillas = 5 en las nueve entradas, y existen runs/detect/runs/llvip_semillas/<metodo>_s1..s4 con seed 1 a 4 y epochs 40. La limitacion Tercera (parrafo 229) si menciona «5 semillas de entrenamiento por entrada en LLVIP», de modo que el capitulo de metodo es el unico lugar donde el protocolo queda incompleto

*(bloque: Parrafos 299-346 (cap. 3 MARCO CONCEPTUAL y cap. 4 MARCO METODOLOGICO), mas la Tabla 26 de operacionalizacion que cuelga del parrafo 339)*

### parrafo 341, §4.5 — INCOHERENCIA

> Las imagenes se reorganizaron en dos directorios paralelos (data/raw/VIS y data/raw/IR) con nombres de archivo coincidentes para emparejado automatico [y] el corpus experimental son veinte pares

**El dato:** data/raw/VIS y data/raw/IR tienen 21 archivos cada uno con nombres coincidentes, no 20: src/datasets.py excluye explicitamente un par (PARES_EXCLUIDOS = {Athena_heather_IR_hei_vis_g}) porque el archivo del slot VIS es copia byte a byte del IR, y list_pairs() devuelve 20. Los residuos siguen en disco: experiments/results/fused_images/<metodo>/ tiene 21 fusiones cada una, la sobrante es justamente Athena_heather_IR_hei_vis_g (all_metrics.csv, en cambio, trae las 140 filas correctas = 7 x 20). Tal como esta redactado el parrafo, el lector que aplique la regla «nombres coincidentes» sobre data/raw obtiene 21 pares y no puede reproducir el veinte; conviene declarar la exclusion y su motivo

*(bloque: Parrafos 299-346 (cap. 3 MARCO CONCEPTUAL y cap. 4 MARCO METODOLOGICO), mas la Tabla 26 de operacionalizacion que cuelga del parrafo 339)*

### Tabla 2, fila «Escala (radio)»; refuerza la apertura del parrafo 276 («Los hiperparametros (r, m) se ajustan maximizando la funcion objetivo del trabajo de referencia») — CONTRADICE

> Escala (radio): Unica, de radio r (ajustado por PSO)

**El dato:** El PSO no fija el radio adoptado: con la aptitud Fo y el rango publicado la busqueda devuelve r = 1 (optimo_exacto_fo.csv y pso_grid_search_fo_propuesta.csv, Fo 1,7350 > 1,7057). El propio parrafo 276 se corrige mas abajo («Para el radio, Fo favorece r = 1»), y 5.6 y 5.8.5 declaran r = 25 decision de diseno. La tabla y la primera frase del parrafo dicen lo contrario que el final del mismo parrafo.

*(bloque: Parrafos 202-298: capitulo 1 PROBLEMA DE INVESTIGACION y capitulo 2 MARCO TEORICO (incluye la Tabla 2 «Configuracion de la Propuesta Novedosa y del PSO» y la Tabla 3 «Metodos comparativos»))*

### Parrafo 276 (seccion 2.2.5, Funcion de aptitud) — CONTRADICE

> Las nueve metricas de evaluacion de esta tesis, todas de tipo «mayor es mejor», favorecen en cambio r = 25.

**El dato:** A igual peso m = 0,30 solo 5 de las 9 favorecen r = 25. Comparando fo_ablacion_per_image.csv (metodo «Propuesta_Fo(r=1,m=0.30)», medias de los 20 pares) con all_metrics.csv (metodo Propuesta_Novedosa, r = 25, m = 0,30): favorecen r = 25 EN 6,5981 -> 6,9855; SD 0,1129 -> 0,1439; FE 1,0423 -> 1,1047; MG 0,0232 -> 0,0355; SF 12,4030 -> 17,4425. Favorecen r = 1 MI_vis 1,3681 -> 0,8970; MI_ir 0,9316 -> 0,6003; SSIM 0,7607 -> 0,6584; y PSNR 17,7407 (pso_por_imagen.csv, filas r = 1, m = 0,30) -> 16,8409, con r = 1 mejor en los 20 pares. Ningun CSV barre las nueve metricas sobre r, de modo que la afirmacion agregada tampoco tiene fuente directa. La version correcta ya esta en el parrafo 389 (5.6): «supera a r = 1 en entropia, contraste, eficiencia de fusion, gradiente medio y frecuencia espacial, mientras r = 1 preserva mejor la fidelidad».

*(bloque: Parrafos 202-298: capitulo 1 PROBLEMA DE INVESTIGACION y capitulo 2 MARCO TEORICO (incluye la Tabla 2 «Configuracion de la Propuesta Novedosa y del PSO» y la Tabla 3 «Metodos comparativos»))*

### Parrafo 229, limitacion novena — CONTRADICE

> Fo favorece r = 1 y las nueve metricas r = 25

**El dato:** La primera mitad es correcta (optimo_exacto_fo.csv: argmax con m >= 0,30 en r = 1). La segunda repite el error del parrafo 276: al mismo peso m = 0,30 solo el bloque de actividad (EN, SD, FE, MG, SF) mejora con r = 25; MI_vis, MI_ir, SSIM y PSNR mejoran con r = 1 (all_metrics.csv frente a fo_ablacion_per_image.csv y pso_por_imagen.csv, cifras del hallazgo anterior).

*(bloque: Parrafos 202-298: capitulo 1 PROBLEMA DE INVESTIGACION y capitulo 2 MARCO TEORICO (incluye la Tabla 2 «Configuracion de la Propuesta Novedosa y del PSO» y la Tabla 3 «Metodos comparativos»))*

### Parrafo 229, limitacion novena, frente a H5 en el parrafo 227 y a la seccion 5.8.5 (parrafo 418) — INCOHERENCIA

> la configuracion adoptada se apoya en el criterio de evaluacion y no en la optimizacion, que si determina el peso m

**El dato:** H5 enuncia lo contrario («la optimizacion no determina la configuracion adoptada, dado que ambos hiperparametros resultan de decisiones apoyadas en parte del mismo criterio con el que despues se evalua») y 5.8.5 concluye «el peso [proviene] del piso del rango publicado». El dato respalda la lectura de frontera, no la de optimo: m = 0,30 es el limite inferior del rango heredado y la aptitud decrece monotonamente en m (curva_aptitud_vs_m.csv, columna Fo_propuesta: 1,7715 en m = 0,0703; 1,7057 en m = 0,30; 1,2067 en m = 2,00), por eso las 25 configuraciones de pso_grid_search_fo_propuesta.csv devuelven m_opt = 0,30. Con el piso liberado el optimo se va a m ~ 0,07 (pso_grid_search.csv, F_apt maximo 1,9843 en r = 25, m = 0,0703). Hay que unificar las tres formulaciones: la del parrafo 229 dice «si determina el peso», H5 dice que ninguno de los dos lo determina.

*(bloque: Parrafos 202-298: capitulo 1 PROBLEMA DE INVESTIGACION y capitulo 2 MARCO TEORICO (incluye la Tabla 2 «Configuracion de la Propuesta Novedosa y del PSO» y la Tabla 3 «Metodos comparativos»))*


## Gravedad baja (32)

### parrafo 359 (§5.3) — INCOHERENCIA

> presenta la mayor tasa de artefactos del benchmark despues del Top-Hat clasico (Nabf 0,3742, frente a 0,1593 de DTCWT)

**El dato:** Las tres cifras son correctas (media de all_metrics.csv columna Nabf: TopHat_Clasico 0,5857, Propuesta_Novedosa 0,3742, DTCWT 0,1593), pero el punto de comparacion elegido no es el mejor del benchmark: el Nabf mas bajo —recordar que en Nabf menor es mejor— es PiramideLaplace con 0,1138, tambien listado en ranking_mas_nabf.csv columna Nabf_medio, y es exactamente la cifra que usa el parrafo 370 para el mismo argumento. Citar a DTCWT como referencia deja la impresion de que es la entrada con menos artefactos y descuadra los dos pasajes entre si.

*(bloque: Parrafos 347-385 (capitulo 5, primera parte: calidad de imagen §5.1-5.4 y evaluacion orientada a tarea §5.5), mas las Tablas 4, 5, 6, 7, 8 y 9 del libro (indices python-docx 27, 28, 29, 30, 31, 32))*

### parrafo 359 (§5.3), en relacion con las Tablas 4 y 5 (parrafos 357 y 358) — INCOHERENCIA

> Estas metricas, ponderadas por bordes y estructura local, complementan a las anteriores: la piramide de Laplace lidera FMI (0,2362), QW (0,8470) y QE (0,3856), y DTCWT lidera Q0 (0,7411) [...] La Propuesta Novedosa lidera en cambio SCD (1,5427) y VIF (0,3805)

**El dato:** Los seis valores y los tres liderazgos son correctos contra all_metrics.csv (medias por metodo: FMI PiramideLaplace 0,2362 maximo; QW 0,8470 maximo; QE 0,3856 maximo; Q0 DTCWT 0,7411 maximo; SCD Propuesta 1,5427 maximo; VIF Propuesta 0,3805 maximo; y la propuesta no encabeza ninguna de las cuatro primeras: FMI 0,1686, QW 0,8087, QE 0,3648, Q0 0,7072). El problema es de trazabilidad: el «Estas metricas» no tiene antecedente. La Tabla 4 trae solo las seis clasicas (EN, SD, FE, MG, MI_vis, MI_ir) y la Tabla 5 solo SF, SSIM y PSNR; ninguna tabla del capitulo 5 presenta FMI, Q0, QW, QE, SCD, VIF, Qabf ni Nabf. Recorri las 38 tablas del docx: la unica que menciona Nabf es la Tabla 14 (indice 35, «Rango con 9 / Con 9 + Nabf / Con 17»), en §5.8. El lector no tiene donde verificar las seis cifras del parrafo.

*(bloque: Parrafos 347-385 (capitulo 5, primera parte: calidad de imagen §5.1-5.4 y evaluacion orientada a tarea §5.5), mas las Tablas 4, 5, 6, 7, 8 y 9 del libro (indices python-docx 27, 28, 29, 30, 31, 32))*

### parrafo 350 (§5.1 Caracterizacion del dataset) — CONTRADICE

> resoluciones del orden de 360x270 a 768x576 pixeles

**El dato:** Medi los 20 pares efectivos en data/raw/VIS y data/raw/IR con PIL: el maximo es 768x576 (correcto, 11 pares) y el minimo es 359x247 —Athena_helicopter_helib_011.bmp, identico en VIS y en IR—, no 360x270. La altura difiere en 23 pixeles (9 %). El resto del corpus va de 599x446 a 749x551. La expresion «del orden de» amortigua, pero el 270 no sale de ningun archivo.

*(bloque: Parrafos 347-385 (capitulo 5, primera parte: calidad de imagen §5.1-5.4 y evaluacion orientada a tarea §5.5), mas las Tablas 4, 5, 6, 7, 8 y 9 del libro (indices python-docx 27, 28, 29, 30, 31, 32))*

### parrafo 352 (§5.2 Analisis cualitativo) — INCOHERENCIA

> el Top-Hat clasico produce la imagen de mayor contraste aparente, pero con halos visibles alrededor de los objetivos termicos

**El dato:** Es un juicio visual sobre la figura 6, no una afirmacion metrica, pero choca con la metrica de contraste del propio trabajo y con el parrafo 356: en descriptive_means.csv la desviacion estandar del Top-Hat clasico es 0,1352, tercera de siete, detras de PiramideLaplace 0,1550 y de la propia Propuesta 0,1439 (rango medio SD en ranking_methods.csv: Propuesta 1,65, Laplace 2,00, TopHat 2,85). Lo que el Top-Hat si lidera es actividad: SF 23,1000 y MG 0,0478, ambos maximos. Conviene decir «mayor realce de bordes» o «mayor frecuencia espacial» para no dejar dos afirmaciones de contraste enfrentadas a cuatro parrafos de distancia.

*(bloque: Parrafos 347-385 (capitulo 5, primera parte: calidad de imagen §5.1-5.4 y evaluacion orientada a tarea §5.5), mas las Tablas 4, 5, 6, 7, 8 y 9 del libro (indices python-docx 27, 28, 29, 30, 31, 32))*

### párrafo 441 (recomendación 7) — INCOHERENCIA

> emplear la Propuesta Novedosa (r = 25, m = 0,30), que lidera la entropía y la eficiencia de fusión del benchmark con un realce controlado

**El dato:** «Realce controlado» choca con la conclusión 8 del mismo capítulo. ranking_mas_nabf.csv / all_metrics.csv: Nabf medio de la propuesta 0,3742, el segundo más alto de los siete y 3,3 veces el de la pirámide de Laplace (0,1138); el párrafo 430 lo describe como «los dos operadores morfológicos son los más agresivos del benchmark». Lo único que sostiene «controlado» es saturacion_vs_m.csv (0,7271 % de recorte en m = 0,30), que es otro fenómeno. Habría que decir «con el recorte por saturación por debajo del 1 %» y no «realce controlado», o declarar el Nabf ahí mismo.

*(bloque: Párrafos 420–442 — Capítulo 6 CONCLUSIONES Y RECOMENDACIONES)*

### párrafo 423, contra el párrafo 425 («sostenido por su liderazgo en el rango medio de entropía, contraste y eficiencia de fusión») — INCOHERENCIA

> quedando segunda en contraste, gradiente medio y frecuencia espacial

**El dato:** Las dos frases son ciertas pero con bases distintas y sin decirlo, y sobre la misma métrica dicen «segunda» y «lidera». En medias (descriptive_means.csv) la propuesta es segunda en SD: 0,1439 detrás de LP 0,1550. En rango medio (ranking_methods.csv) es primera en SD: 1,65, mejor que LP 2,00 y el clásico 2,85. En MG y SF, en cambio, «segunda» es correcto por rango (2,00 en ambas, detrás del clásico con 1,00) pero por media también es segunda, así que la mezcla de criterios solo afecta al contraste.

*(bloque: Párrafos 420–442 — Capítulo 6 CONCLUSIONES Y RECOMENDACIONES)*

### párrafo 423 (conclusión específica 1) — INCOHERENCIA

> el infrarrojo solo (0,961) supera a 6 de las siete, sin distinguirse de la séptima

**El dato:** El conteo es exacto pero el verbo «supera» no descansa en una prueba. semillas_llvip_pareadas.csv: la columna mayor_que_el_ruido es True para IR contra Curvelet, DTCWT, DWT, Propuesta, RatioPiramide y TopHat (6) y False contra PiramideLaplace (dif 0,0094; gana 3 de 5; p_wilcoxon 0,3125), o sea 6 y 1 tal como dice el libro. Pero sig_holm es False en las 36 comparaciones (p_holm = 1,0000) y run_analisis_semillas_llvip.py define mayor_que_el_ruido como |dif_media| > desvío típico (0,0128), no como significancia; con 5 semillas el p mínimo alcanzable del Wilcoxon pareado es 0,0625. Como el párrafo 429 abre con «Las pruebas no paramétricas confirman que las diferencias observadas no son fruto del azar», conviene aclarar que en la parte de detección el criterio es descriptivo (diferencia mayor que el ruido de inicialización) y no una prueba.

*(bloque: Párrafos 420–442 — Capítulo 6 CONCLUSIONES Y RECOMENDACIONES)*

### párrafo 427 (conclusión específica 5) — INCOHERENCIA

> Dentro de la familia Top-Hat, la forma de combinar las respuestas del banco introduce diferencias modestas.

**El dato:** «Modestas» se sostiene en el rango agregado (ablacion_banco_resumen.csv: 3,222 a 3,783, contra 3,394–4,444 del benchmark principal), pero ablacion_banco_contrastes.csv da los 40 contrastes de la suma contra los otros cinco brazos significativos con p_holm = 0,000010 y, en magnitud, mayores que los que el libro llama superioridades: suma menos disco en EN es +0,1939, tres veces el +0,0636 de la propuesta frente al Top-Hat clásico que el párrafo 423 declara «estadísticamente significativa». Modesto en el ranking, no en las métricas: conviene decir cuál de las dos cosas.

*(bloque: Párrafos 420–442 — Capítulo 6 CONCLUSIONES Y RECOMENDACIONES)*

### párrafo 435 (recomendación 1) — INCOHERENCIA

> el desvío de una misma entrada (0,0128 de mAP@0,5)

**El dato:** Falta la palabra «mediano». En semillas_llvip_resumen.csv los nueve desvíos son 0,0063 a 0,0288 y 0,0128 es la mediana (y, por casualidad, el desvío de Curvelet); la media es 0,0129 y el máximo 0,0288 (DWT). El párrafo 379, al pie de la Figura 12, sí dice «el desvío mediano de una misma entrada es 0,0128». La comparación con las distancias entre fusiones sí es correcta: las brechas consecutivas entre las siete medias van de 0,0024 a 0,0152.

*(bloque: Párrafos 420–442 — Capítulo 6 CONCLUSIONES Y RECOMENDACIONES)*

### Parrafo 83 (RESUMEN); 'low cost' implicito en el parrafo 86 ('interpretable single-scale morphological operator') — SIN FUENTE

> aporta un operador morfologico de una sola escala interpretable y de bajo costo

**El dato:** No existe ningun CSV con el costo computacional de la fusion por metodo. Busque: los 50 CSV de metrics_reports (ninguno tiene columna de tiempo de fusion; la columna 'segundos' aparece solo en pso_grid_search*.csv, que mide corridas de PSO, y en detection_llvip_semillas.csv, que mide entrenamiento de YOLO), las subcarpetas fused_images / pso / metrics_reports_libre, y un grep de 'perf_counter', 'tiempo_ms', 'latencia' y 'ms/imagen' sobre experiments/*.py, sin resultados. 'De bajo costo' es una comparacion implicita contra los multiescala que ningun dato medido respalda.

*(bloque: Parrafos 82-167: RESUMEN (p. 83) y SUMMARY (p. 86). Los parrafos 88-167 son el indice de CONTENIDO (titulos y numeros de pagina), sin afirmaciones empiricas.)*

### Parrafo 83 (RESUMEN); identico en el 86 ('evidencing that the enhancement rewarded by activity metrics does not transfer to detection') — SIN FUENTE

> lo que evidencia que el realce que premian las metricas de actividad no se traslada a la deteccion

**El dato:** El unico CSV que prueba esa relacion es correlacion_calidad_deteccion.csv, y no alcanza para 'evidencia': fila conjunto_metricas=nueve / dataset=LLVIP_5sem / medida=mAP50 da spearman_rho = -0,3571 con spearman_p = 0,4316, significativo_05 = False y sobrevive_multiplicidad = False. De las 18 filas del archivo solo una es significativa antes de corregir (diecisiete / M3FD / mAP50_95, rho = -0,8929, p = 0,0068) y ninguna sobrevive Bonferroni. La observacion descriptiva (la propuesta lidera actividad y es 3.a en deteccion) es cierta; el verbo 'evidencia' sobrepasa lo que el test sostiene con n = 7 fusiones.

*(bloque: Parrafos 82-167: RESUMEN (p. 83) y SUMMARY (p. 86). Los parrafos 88-167 son el indice de CONTENIDO (titulos y numeros de pagina), sin afirmaciones empiricas.)*

### Parrafo 83 (RESUMEN) — INCOHERENCIA

> El infrarrojo solo [...] supera a 6 de las siete fusiones, aunque de la septima, la piramide de laplace, no se distingue [...] indistinguible de 4 de sus seis rivales

**El dato:** Los conteos son correctos, pero el criterio no es estadistico y el resumen no lo dice. En semillas_llvip_pareadas.csv las 36 comparaciones tienen p_holm = 1,0 y sig_holm = False sin excepcion (con 5 bloques el p minimo alcanzable del Wilcoxon pareado es 0,0625, de modo que NADA puede resultar significativo). Lo que sostiene 'supera' y 'no se distingue' es la columna mayor_que_el_ruido, definida en experiments/run_analisis_semillas_llvip.py linea 149 como |dif_media| > mediana de los desvios intra-entrada (0,0128). Verificado: IR gana con mayor_que_el_ruido=True contra Curvelet, DTCWT, DWT, Propuesta, RatioPiramide y TopHat_Clasico (6), y False contra PiramideLaplace (dif 0,0094); la Propuesta es False contra Curvelet, DTCWT, DWT y TopHat_Clasico (4 de 6). Como el mismo parrafo usa antes 'ventaja estadisticamente significativa' para el bloque TNO, el lector importa esa lectura a un conteo que no la tiene.

*(bloque: Parrafos 82-167: RESUMEN (p. 83) y SUMMARY (p. 86). Los parrafos 88-167 son el indice de CONTENIDO (titulos y numeros de pagina), sin afirmaciones empiricas.)*

### Parrafo 83 (RESUMEN) y parrafo 86 (SUMMARY) — INCOHERENCIA

> En el ranking agregado de las nueve metricas [...] ocupa el primer lugar (3,39), por delante de la piramide de Laplace (3,91)

**El dato:** Correcto dentro de su alcance (ranking_methods.csv, columna avg_rank: 3,394 contra 3,911), pero el primer puesto no sobrevive a la unica metrica de la bateria en la que menor es mejor. ranking_mas_nabf.csv: al agregar Nabf, la Propuesta pasa de rango_9 = 3,394 (puesto 1) a rango_9_mas_Nabf = 3,655 (puesto 2) y PiramideLaplace pasa de 3,911 (puesto 2) a 3,620 (puesto 1); el Nabf_medio de la Propuesta es 0,3742 frente a 0,1138 de la Laplace. Tampoco se menciona que el 4.o puesto (RatioPiramide, 3,983) esta a 0,04 del 2.o. En un resumen, 'primer lugar' sin acotar el alcance sobrevende un orden fragil.

*(bloque: Parrafos 82-167: RESUMEN (p. 83) y SUMMARY (p. 86). Los parrafos 88-167 son el indice de CONTENIDO (titulos y numeros de pagina), sin afirmaciones empiricas.)*

### parrafo 396, pie de la Tabla 11 — INCOHERENCIA

> las diferencias reflejan el radio hallado (r = 1 donde la aptitud llega a 1,7350 y r = 25 donde llega a 1,7057)

**El dato:** La Tabla 11 del docx contiene tres valores distintos, no dos: la celda n = 2 / T = 10 vale 1,6990. En pso_grid_search_fo_propuesta.csv esa fila (n = 2, Tmax = 10) tiene r_opt = 14, no 1 ni 25. Las otras 24 celdas si se reparten entre r = 1 (1,7350) y r = 25 (1,7057) exactamente como dice el pie. El pie explica «las diferencias» con dos radios cuando el barrido encontro tres.

*(bloque: Parrafos 386 a 419 (§5.6 Propuesta Novedosa, §5.7 Discusion integrada, §5.8 Auditoria del protocolo: 5.8.1 a 5.8.5) mas las Tablas 10, 11, 12, 13 y 14 del docx (indices python-docx 33, 34, 35, 36 y 37))*

### parrafo 412, §5.8.3 — INCOHERENCIA

> la suma desciende al cuarto lugar (3,500), por detras del maximo y del disco (3,444 cada uno)

**El dato:** ablacion_banco_resumen.csv, columna rango_9_sin_FE ordenada: disco 3,444, maximo 3,444, promedio 3,475, suma 3,500, base 3,506, lineas 3,631. El cuarto lugar es correcto, pero el brazo del promedio (3,475) tambien va delante de la suma y el parrafo no lo nombra: se declaran dos brazos por delante para un cuarto puesto que exige tres.

*(bloque: Parrafos 386 a 419 (§5.6 Propuesta Novedosa, §5.7 Discusion integrada, §5.8 Auditoria del protocolo: 5.8.1 a 5.8.5) mas las Tablas 10, 11, 12, 13 y 14 del docx (indices python-docx 33, 34, 35, 36 y 37))*

### parrafo 399, primera observacion de la Discusion integrada — INCOHERENCIA

> es segunda en contraste, gradiente medio y frecuencia espacial

**El dato:** Es cierto en medias (descriptive_means.csv: SD Propuesta 0,1439 frente a 0,1550 de la piramide de Laplace) pero falso en rango medio: ranking_methods.csv, columna SD, da Propuesta 1,65 y PiramideLaplace 2,00, o sea la propuesta PRIMERA en el rango medio del contraste. La conclusion 3 (parrafo 425) usa el otro criterio y escribe «su liderazgo en el rango medio de entropia, contraste y eficiencia de fusion». Las dos frases son correctas cada una en su metrica pero se leen como contradictorias; conviene decir en cada caso si se habla de la media o del rango medio.

*(bloque: Parrafos 386 a 419 (§5.6 Propuesta Novedosa, §5.7 Discusion integrada, §5.8 Auditoria del protocolo: 5.8.1 a 5.8.5) mas las Tablas 10, 11, 12, 13 y 14 del docx (indices python-docx 33, 34, 35, 36 y 37))*

### parrafo 418, §5.8.5, y pie de la Tabla 11 — INCOHERENCIA

> el maximo dentro del rango publicado esta en r = 1 con Fo = 1,7350 ... con el peso libre esta en r = 25 ... con m = 0,070 y Fo = 1,7715

**El dato:** Las cifras salen bien de optimo_exacto_fo.csv (r=1, m=0,30 -> 1,734991; r=25, m=0,07 -> 1,771465; r=25, m=0,30 -> 1,705696) y coinciden con curva_aptitud_vs_m.csv y pso_grid_search_fo_propuesta.csv. Pero en el mismo directorio hay otros dos CSV que calculan la MISMA aptitud sobre las MISMAS tres escenas con otra implementacion del SSIM y dan valores distintos: superficie_aptitud_fo.csv da Fo(r=1, m=0,30) = 1,7191 y Fo(r=25, m=0,30) = 1,6870, y barrido_metricas_vs_m.csv (operador propuesta, r=25, m=0,3000, columna F_o) da 1,687010. Los dos grupos coinciden en la conclusion cualitativa (el argmax dentro del rango publicado esta en r = 1) pero no en los numeros. Si alguna figura o apendice se dibuja desde superficie_aptitud_fo.csv, los valores no cerraran con la prosa: hay que fijar una sola fuente para 1,7350 / 1,7057 / 1,7715.

*(bloque: Parrafos 386 a 419 (§5.6 Propuesta Novedosa, §5.7 Discusion integrada, §5.8 Auditoria del protocolo: 5.8.1 a 5.8.5) mas las Tablas 10, 11, 12, 13 y 14 del docx (indices python-docx 33, 34, 35, 36 y 37))*

### parrafo 418, §5.8.5 (segunda mencion del factor; la primera, «su disco, que extrae 4,21 veces menos energia de detalle», si es correcta) — INCOHERENCIA

> el banco extrae 4,21 veces la energia de detalle del disco

**El dato:** aptitud_operador_energia.csv, columna ganancia_vs_clasico: el 4,205110 de la propuesta esta medido contra «Top-Hat clasico . disco B_5», es decir el disco de radio 5 de la referencia. Contra el disco de radio 25 («Disco B_25 (una rama)», 2,630494) el factor es 4,205/2,630 = 1,60. Como la frase dice «del disco» sin el radio, y el parrafo acaba de hablar del disco de la referencia, se lee bien; pero un lector que entienda «el disco» como el disco a r = 25 —el mismo radio del banco— leera un factor 2,6 veces mayor del real. Conviene escribir «del disco B_5 de la referencia».

*(bloque: Parrafos 386 a 419 (§5.6 Propuesta Novedosa, §5.7 Discusion integrada, §5.8 Auditoria del protocolo: 5.8.1 a 5.8.5) mas las Tablas 10, 11, 12, 13 y 14 del docx (indices python-docx 33, 34, 35, 36 y 37))*

### parrafo 389, §5.6 — SIN FUENTE

> mientras r = 1 preserva mejor la fidelidad a las fuentes

**El dato:** La comparacion a peso igualado se puede hacer con fo_ablacion_per_image.csv (brazo Propuesta_Fo(r=1,m=0.30), 20 imagenes) frente a descriptive_means.csv (Propuesta_Novedosa, r=25, m=0,30), y sale bien en tres de las cuatro metricas de fidelidad: MI_vis 1,3681 frente a 0,8970; MI_ir 0,9316 frente a 0,6003; SSIM 0,7607 frente a 0,6584. La cuarta, PSNR, no se puede comprobar: fo_ablacion_per_image.csv no tiene columna PSNR y ningun otro CSV da PSNR para el brazo r = 1, m = 0,30. El bloque de actividad de la misma frase (EN 6,9855>6,5981, SD 0,1439>0,1129, FE 1,1047>1,0423, MG 0,0355>0,0232, SF 17,4425>12,4030) si esta completo y respaldado.

*(bloque: Parrafos 386 a 419 (§5.6 Propuesta Novedosa, §5.7 Discusion integrada, §5.8 Auditoria del protocolo: 5.8.1 a 5.8.5) mas las Tablas 10, 11, 12, 13 y 14 del docx (indices python-docx 33, 34, 35, 36 y 37))*

### parrafo 519 (apendice F) — CONTRADICE

> la piramide de Laplace y el curvelet se situan en ordenes de magnitud comparables

**El dato:** Comparables entre si y con el Top-Hat clasico, pero no con el metodo propuesto, que es el sujeto de la frase anterior. Medicion directa sobre el mismo par (mediana de 5): PiramideLaplace 6,6 ms, Curvelet 8,3 ms, TopHat_Clasico (r=5) 11,6 ms, Propuesta_Novedosa (r=25, m=0,30) 168,1 ms. La propuesta esta mas de un orden de magnitud por encima de LP y CVT, no en el mismo orden.

*(bloque: Parrafos 482-521 - Capitulo 8 APENDICE (A. Repositorio del codigo; B. Configuraciones del barrido PSO; C. Tablas estadisticas extendidas; D. Pseudocodigos; E. Refinamiento de la regla de fusion; F. Hardware y tiempos))*

### parrafo 519 (apendice F) — SIN FUENTE

> La ejecucion completa del benchmark (140 fusiones: 7 metodos x 20 pares) toma aproximadamente 90 segundos.

**El dato:** El conteo si esta respaldado: all_metrics.csv tiene 140 filas, 7 metodos (Curvelet, DTCWT, DWT, PiramideLaplace, Propuesta_Novedosa, RatioPiramide, TopHat_Clasico) x 20 imagenes. Los 90 segundos no los registra ningun CSV y run_all_fusions.py no cronometra nada. Los reproduje en orden de magnitud instrumentando el bucle real del script sobre 4 pares x 7 metodos: 16,1 s, que extrapolados a 20 pares dan 81 s. Pero el desglose desmiente la atribucion implicita: de esos 16,1 s, 1,6 s son las 28 fusiones y 14,5 s son las llamadas a evaluate_all. El coste del benchmark es de las 17 metricas, no de las fusiones; la frase da a entender lo contrario.

*(bloque: Parrafos 482-521 - Capitulo 8 APENDICE (A. Repositorio del codigo; B. Configuraciones del barrido PSO; C. Tablas estadisticas extendidas; D. Pseudocodigos; E. Refinamiento de la regla de fusion; F. Hardware y tiempos))*

### parrafo 484 (apendice A, ultima frase) — INCOHERENCIA

> El archivo requirements.txt consigna las dependencias exactas.

**El dato:** requirements.txt no fija ninguna version exacta: sus 20 lineas usan todas el operador >= (numpy>=1.26, opencv-python>=4.9, torch>=2.0, ultralytics>=8.2, ...) y no contiene ni un solo ==. Son versiones minimas, no exactas, y para dos paquetes eso no es inocuo en reproducibilidad: detector_perfil.json registra que los entrenamientos corrieron con ultralytics 8.4.68 y torch 2.5.1+cu121, muy por encima de los minimos declarados. O se cambia «exactas» por «minimas», o se congela un requirements con pines (pip freeze).

*(bloque: Parrafos 482-521 - Capitulo 8 APENDICE (A. Repositorio del codigo; B. Configuraciones del barrido PSO; C. Tablas estadisticas extendidas; D. Pseudocodigos; E. Refinamiento de la regla de fusion; F. Hardware y tiempos))*

### parrafo 490 (apendice B) — INCOHERENCIA

> Cada combinacion del barrido ejecuta una corrida PSO independiente con semilla propia (25 corridas, 4.500 evaluaciones de fusion en total).

**El dato:** Las 25 corridas con semilla propia estan bien (pso_grid_search_fo.py: init_swarm(n, seed=1000*n+T)), y la suma de la columna «evaluaciones» de pso_grid_search_fo_propuesta.csv es exactamente 4.500, que coincide con la suma de n x Tmax sobre las 25 filas y con la suma de «evals» de las 25 configuraciones del state.json. Pero esas 4.500 son evaluaciones de la APTITUD, no fusiones: cada llamada a fitness recorre las 3 escenas del cache (allp[::7], y el state.json las nombra: APC_1_view_1_fk_06_005, Athena_APC_4_fennek01_005, Athena_soldier_behind_smoke_3_meting012-1700), de modo que el barrido ejecuta 13.500 fusiones. Conviene decir «4.500 evaluaciones de la aptitud (13.500 fusiones, tres escenas por evaluacion)».

*(bloque: Parrafos 482-521 - Capitulo 8 APENDICE (A. Repositorio del codigo; B. Configuraciones del barrido PSO; C. Tablas estadisticas extendidas; D. Pseudocodigos; E. Refinamiento de la regla de fusion; F. Hardware y tiempos))*

### Epígrafe de la Tabla 11 «Barrido de configuraciones del PSO» (d.tables[34]) — INCOHERENCIA

> Las 25 configuraciones convergen al mismo peso óptimo (m* = 0,30); las diferencias reflejan el radio hallado (r = 1 donde la aptitud llega a 1,7350 y r = 25 donde llega a 1,7057)

**El dato:** pso_grid_search_fo_propuesta.csv tiene tres valores distintos de Fo_opt, no dos: 1,7350 (r=1, 16 filas), 1,7057 (r=25, 8 filas) y 1,6990 (r=14, 1 fila: n=2, T=10). La celda n=2/T=10 de la propia tabla imprime 1,6990, así que el paréntesis del epígrafe no explica una de las 25 celdas que el lector tiene delante. La afirmación sobre m* = 0,30 sí está respaldada: m_opt = 0,30 en las 25 filas.

*(bloque: Las 38 tablas de docs/Tesis_Borrador_V3.docx (d.tables), verificadas celda por celda contra los CSV de experiments/results/metrics_reports/ y, donde fue posible, recomputadas desde los datos por imagen.)*

### Tabla 7 (d.tables[30]), epígrafe y columna «Global» — INCOHERENCIA

> Tabla 7. Ranking promedio por método y métrica (1 = mejor) — con columnas SD, MG, SF, SSIM, PSNR, MI_ir y Global

**El dato:** La columna Global es el promedio sobre las NUEVE métricas (avg_rank de ranking_methods.csv), no sobre las seis mostradas, y el epígrafe no lo aclara. Para la Propuesta Novedosa las seis columnas visibles promedian 3,692 (1,65+2,00+2,00+5,90+5,35+5,25)/6, pero la celda Global dice 3,39, porque incluye EN = 1,50, FE = 1,50 y MI_vis = 5,40, que la tabla no muestra. El número es correcto —lo recompute desde all_metrics.csv y da 3,394— pero es irreproducible a partir de la tabla impresa. El epígrafe de la Figura 8 sí lo declara; el de la Tabla 7 no.

*(bloque: Las 38 tablas de docs/Tesis_Borrador_V3.docx (d.tables), verificadas celda por celda contra los CSV de experiments/results/metrics_reports/ y, donde fue posible, recomputadas desde los datos por imagen.)*

### Epígrafe de la Tabla 12 «Control negativo» (d.tables[35]) — INCOHERENCIA

> rango medio de los siete métodos y de siete entradas degradadas

**El dato:** De las siete filas que no son métodos, seis son degradaciones (ruido gaussiano σ = 0,02; 0,05; 0,10; 0,20 y desenfoque 5×5 y 11×11) y la séptima es «Imagen base (VIS+IR)/2», que run_control_negativo.py define como «base (VIS+IR)/2, sin operador», es decir el control sin procesar, no una entrada degradada. Los 14 brazos de control_negativo.csv se reparten en 7 métodos + 6 degradaciones + 1 base.

*(bloque: Las 38 tablas de docs/Tesis_Borrador_V3.docx (d.tables), verificadas celda por celda contra los CSV de experiments/results/metrics_reports/ y, donde fue posible, recomputadas desde los datos por imagen.)*

### parrafo 344, §4.6 Implementacion — INCOHERENCIA

> Toda la implementacion se realizo en Python 3.11 con las bibliotecas NumPy, OpenCV, scikit-image, SciPy, PyWavelets, Pandas, Matplotlib y Seaborn

**El dato:** Python 3.11 es correcto (.venv/Scripts/python.exe -V -> 3.11.14) y las ocho bibliotecas estan en requirements.txt, igual que la organizacion modular (src/datasets.py, src/fusion, src/metrics, src/utils) y el control de versiones (.git presente). Pero la lista omite dependencias sin las cuales dos experimentos del libro no corren: dtcwt>=0.12, que src/fusion/comparatives.py importa para el comparativo DTCWT del benchmark, y torch/torchvision/ultralytics>=8.2, que experiments/detection_llvip/train_eval_llvip.py necesita para el YOLOv8n de §5.5. Las tres estan declaradas en requirements.txt

*(bloque: Parrafos 299-346 (cap. 3 MARCO CONCEPTUAL y cap. 4 MARCO METODOLOGICO), mas la Tabla 26 de operacionalizacion que cuelga del parrafo 339)*

### parrafo 338, §4.3; y bloque de variables dependientes de la Tabla 26 (§4.4) — INCOHERENCIA

> totalizando 140 fusiones evaluadas con las nueve metricas sin referencia, base del analisis estadistico inter-metodo

**El dato:** Las 140 fusiones y las nueve metricas del analisis son correctas (all_metrics.csv, 140 filas; METRICS = EN, SD, FE, MG, MI_vis, MI_ir, SF, SSIM, PSNR en experiments/run_stats_analysis.py, que descarta expresamente Qabf, Nabf, SCD, VIF, FMI, Q0, QW y QE; friedman_results.csv tiene esas nueve filas y la Tabla 26 declara exactamente esas nueve dependientes). La incoherencia es con el capitulo de resultados: all_metrics.csv calcula 17 columnas de metricas y §5.3 reporta las de afuera de la bateria (parrafo 359: FMI 0,2362, QW 0,8470, QE 0,3856, Q0 0,7411) igual que §5.8.1 con Nabf (parrafos 403 y 430). Quien lea solo §4.3 y §4.4 no espera esas tablas; conviene decir en el metodo que se computan trece-diecisiete metricas y que nueve son la bateria del analisis estadistico

*(bloque: Parrafos 299-346 (cap. 3 MARCO CONCEPTUAL y cap. 4 MARCO METODOLOGICO), mas la Tabla 26 de operacionalizacion que cuelga del parrafo 339)*

### Parrafo 227 (1.5 Hipotesis), hoja de ruta final — INCOHERENCIA

> H1 se contrasta en las secciones 5.4 y 5.6; H6 en la seccion 5.5; y H2, H3, H4, H5 y H7 en la seccion 5.8

**El dato:** El titulo de 5.8.5 es «Alcance de la optimizacion y contraste con la tarea (H5, H6)» y el parrafo 401 dice que los cinco experimentos de 5.8 «contrastan las hipotesis H2, H3, H4, H5, H6 y H7». La hoja de ruta deja H6 solo en 5.5 y omite 5.8.5, donde efectivamente se cierra (correlacion de Spearman y conteo por escena, parrafo 419).

*(bloque: Parrafos 202-298: capitulo 1 PROBLEMA DE INVESTIGACION y capitulo 2 MARCO TEORICO (incluye la Tabla 2 «Configuracion de la Propuesta Novedosa y del PSO» y la Tabla 3 «Metodos comparativos»))*

### Parrafo 229, limitacion tercera — INCOHERENCIA

> pero con una sola en M3FD sobre un subconjunto de LLVIP (2.000 imagenes de entrenamiento y 500 de validacion, 40 epocas)

**El dato:** El 2.000/500 es de LLVIP, no de M3FD. detector_perfil.json, clave «datos»: llvip_Propuesta_Novedosa train 2000 / val 500; m3fd_mixto train 4000 / val 1002; m3fd_test_Propuesta_Novedosa val 499; m3fd_comp_Propuesta_Novedosa val 232 (40 epocas en ambos, clave «hiperparametros»). Coincide con 4.5 (parrafo 342) y con 5.5 (parrafo 380: «2.000 pares de entrenamiento, 500 de validacion y 500 de prueba, de los cuales 499 resultan utilizables» y «4.000 imagenes» mezclando modalidades). Tal como esta redactada, la frase atribuye a M3FD un subconjunto de LLVIP.

*(bloque: Parrafos 202-298: capitulo 1 PROBLEMA DE INVESTIGACION y capitulo 2 MARCO TEORICO (incluye la Tabla 2 «Configuracion de la Propuesta Novedosa y del PSO» y la Tabla 3 «Metodos comparativos»))*

### Parrafo 284 (2.2.7 Metricas de evaluacion), ultima frase — INCOHERENCIA

> la evaluacion empirica de esta tesis reporta el subconjunto de nueve metricas descrito

**El dato:** all_metrics.csv trae las 17 columnas (EN, SD, FE, MG, MI_vis, MI_ir, SF, SSIM, PSNR, Qabf, Nabf, SCD, VIF, FMI, Q0, QW, QE) y la seccion 5.8.1 las reporta y las usa: recalculando desde all_metrics.csv con Nabf invertida obtengo los mismos rangos medios que el parrafo 403 (PiramideLaplace 3,147; DTCWT 3,259; Propuesta 3,459; TopHat_Clasico 5,000) y el 9+Nabf (LP 3,620; Propuesta 3,655). La frase deberia decir que el benchmark principal usa las nueve y que la auditoria del protocolo usa las diecisiete.

*(bloque: Parrafos 202-298: capitulo 1 PROBLEMA DE INVESTIGACION y capitulo 2 MARCO TEORICO (incluye la Tabla 2 «Configuracion de la Propuesta Novedosa y del PSO» y la Tabla 3 «Metodos comparativos»))*

### Parrafo 227, enunciado de H6 — INCOHERENCIA

> H6: el orden de merito de las metricas de imagen no predice el orden de utilidad en una tarea posterior de deteccion

**El dato:** Se cumple con la bateria de nueve (correlacion_calidad_deteccion.csv, fila conjunto=nueve / LLVIP_5sem / mAP50: rho = -0,3571, p = 0,4316; fila nueve / LLVIP / mAP50: rho = +0,2143), que es lo que contrasta 5.8.5. Pero el mismo CSV tiene un caso con asociacion en el sentido esperado: conjunto=diecisiete / M3FD / mAP50_95, rho = -0,8929, p = 0,0068 (no sobrevive Bonferroni, p = 0,1224). El enunciado conviene acotarlo a «las nueve metricas de la bateria empleada» para que diga exactamente lo que el capitulo 5 contrasta.

*(bloque: Parrafos 202-298: capitulo 1 PROBLEMA DE INVESTIGACION y capitulo 2 MARCO TEORICO (incluye la Tabla 2 «Configuracion de la Propuesta Novedosa y del PSO» y la Tabla 3 «Metodos comparativos»))*


## Lo que esta auditoría no cubre

- Las **citas bibliográficas** no se verificaron contra las fuentes originales.
- Los cálculos no se volvieron a ejecutar: se compararon contra los CSV ya producidos.
- La revisión adversarial quedó a medias, así que puede haber falsos positivos en la lista.
- Las **cifras** ya están cubiertas por otro lado: `experiments/trazar_libro.py` traza las
  502 del libro y hoy da **cero sin fuente**. Lo que esta auditoría agrega son las
  afirmaciones **verbales** —«supera a», «lidera», «sistemáticamente»— que un rastreo de
  números no puede juzgar.
