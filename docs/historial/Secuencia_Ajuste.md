# Secuencia de ajuste y mejoramiento

Plan de ejecución ordenado, consolidando las dos auditorías (`Auditoria_Interna.md`,
`Auditoria_Metodologia.md`) y el reencuadre propuesto (`Reencuadre_Propuesto.md`).

**Regla de ordenamiento:** nada se escribe en un documento hasta que los números sean
definitivos. Toda corrección que altere una cifra va antes que cualquier redacción, para no
reescribir dos veces. Por eso el libro queda al final, como se acordó.

**Estado al 30/07/2026:** ya cerrado — corpus reparado (par corrupto sustituido por
`Triclobs_Kaptein_1123`), ranking por rangos intra-bloque, FE declarada, r = 25 como decisión
de diseño, contraste Propuesta vs Top-Hat clásico agregado, clamp de PSNR, split de M3FD
estratificado en tres particiones disjuntas, LLVIP reevaluado con `last.pt`, galería del PDF
corregida, y el análisis de complementariedad por escena que mide el objetivo declarado.

---

## Fase 0 — Trazabilidad (0,5 h) · PRIMERO, sin excepción

| # | Tarea | Por qué primero |
|---|---|---|
| 0.1 | Versionar los 38 archivos pendientes (22 modificados + 16 sin seguimiento), incluidos `src/datasets.py` y los CSV de estadística | Hoy un clon del repositorio **no reproduce ninguno** de los resultados vigentes. Es lo más barato de la lista y lo que un jurado técnico puede pedir en el acto. |

Sin coautoría de herramientas en los commits (regla del repositorio).

---

## Fase 1 — Correcciones que ALTERAN números (6 h, o 14 h con la opción 1.2)

Deben completarse antes de escribir una sola cifra en un documento.

| # | Tarea | Horas | Efecto |
|---|---|---|---|
| 1.1 | El checkpoint de `run_all_fusions.py` no recalcula al cambiar la configuración del operador (demostrado: con m = 1,50 devolvió el EN de m = 0,30) | 1 | Sin esto, cualquier recómputo futuro es silenciosamente falso |
| 1.2 | **DECISIÓN:** corregir la banda base de la Pirámide de Laplace (`fused_pyr[-1] = 0.5*(lv[-1]+li[-1])`) y recomputar todo | 8 | Cierra una contradicción código-documento citable: el párrafo 397 del libro declara como hallazgo propio que la selección por actividad en la capa base sesga la información mutua, que es el defecto del propio comparativo. Cuesta: la propuesta pierde su única victoria en PSNR y el 2.º puesto pasa a la Ratio Pyramid. Gana: en SD pasa de 4/5 a 5/5 |
| 1.3 | Regenerar los 14 CSV anteriores al 29/07 (barrido PSO, curvas de aptitud, ablación): son del corpus previo a la sustitución del par corrupto. Borrar el JSON con `done=25` que impide el recálculo | 3 | Hoy conviven cifras de dos corpus distintos |
| 1.4 | Documentar o eliminar `metrics_reports_libre/`: no tiene script generador y usa 19 pares | 1 | Artefacto huérfano e inconsistente |
| 1.5 | Recomputar en cadena: métricas → estadística → tablas | 1 | — |

La detección (LLVIP y M3FD) **no** depende del corpus TNO, así que no hay que repetirla.

---

## Fase 2 — Experimentos que aportan evidencia nueva (21 h)

Ordenados por lo que cada uno responde en la defensa.

| # | Experimento | Horas | Qué pregunta responde |
|---|---|---|---|
| 2.1 | **Ablación del banco** con (r, m) fijos en 25 y 0,30: disco solo / suma / promedio / máximo entre ramas, con las 17 métricas | 4 | *«¿Su banco de cinco elementos le gana a un solo disco con los mismos parámetros?»* — Riesgo 2. Aviso: en la configuración oficial **empatan** (1,500 vs 1,500 sin FE); el resultado ya se conoce y hay que reportarlo |
| 2.2 | **Barrido de parámetros de los comparativos** (niveles en LP, RP, DWT, DTCWT, CVT; radio en el Top-Hat clásico), versionado como script | 3 | *«¿Y si le doy r = 25 al Top-Hat clásico?»* — Riesgo 1. Ya se midió: pasa a 3,517 y la propuesta a 3,622, segundo puesto. Hay que versionarlo y declararlo, no esconderlo |
| 2.3 | ~~Ampliar el análisis oficial a las 17 métricas~~ — **DESCARTADO por decisión del autor (31/07)**: el análisis se mantiene en las nueve métricas del trabajo de referencia, por fidelidad metodológica. En su lugar, **declarar en una frase** que el evaluador calcula además Qabf, Nabf, SCD, VIF, FMI y los índices de Piella y que no se incorporan al análisis, para que no se lea como selección de resultados. Nota: con las 17 la propuesta sería 3.ª (3,459); pierde en Nabf (6.ª) pero gana en SCD y VIF (1.ª en ambas) | 0,5 | Cierra la objeción de haber elegido las métricas convenientes, sin rehacer el análisis |
| 2.4 | **Control negativo con ruido**: `(VIS+IR)/2 + N(0,σ)` con σ ∈ {0,02; 0,05; 0,10; 0,20}, más base sola y base desenfocada | 5 | **Prioridad alta tras la decisión 2.3.** Al mantener las nueve métricas —todas «mayor es mejor»— el conjunto premia el realce sin castigo; este control lo demuestra y permite declararlo como limitación propia en lugar de dejarlo como flanco. Hoy el experimento **no está versionado** |
| 2.5 | **Test ampliado de complementariedad**: repreparar M3FD concentrando el test en los 574 pares que tienen ambas clases anotadas (~414 útiles frente a 68 hoy) | 6 | Es el único camino a significancia estadística en el objetivo declarado. Hoy ninguna diferencia lo alcanza (mejor caso p = 0,070) |

**No hacer:** semillas múltiples de detección. El límite de precisión son las 68 escenas con
ambas clases, no el ruido de inicialización.

---

## Fase 3 — Rótulos, ecuaciones y crédito (7 h) · no alteran números

| # | Tarea | Horas |
|---|---|---|
| 3.1 | Renombrar el comparativo «Curvelet» a «Wavelet Daubechies db4 (3 niveles)»; retirar la cita de Candès et al. (2006); borrar «captura estructuras anisótropas y curvas»; reescribir «cinco métodos del estado del arte» como «cinco configuraciones de referencia en cuatro familias» | 2 |
| 3.2 | Ecuación (12): el rango de m dice [0,05; 1,20] y contradice al resto del libro y al código ([0,30; 2,00]). **No es cosmético:** dentro del rango que declara la ec. (12) el óptimo es m = 0,05 con F_o = 1,7703, que domina al reportado (1,7354), y esa corrida está en el repositorio. Corregir además «36 configuraciones» → 25 | 2 |
| 3.3 | §3.16 describe la función de aptitud **descartada**: dice que F_o «penaliza los artefactos» cuando no tiene ningún término negativo — y la propuesta es 6.ª de 7 en Nabf, la única métrica que los penaliza | 0,5 |
| 3.4 | Ecuación (18) (gradiente medio): raíz cuadrada vacía | 0,5 |
| 3.5 | Figura 4 dice m = 0,0703 en lugar de 0,30; etiquetas 45°/135° cruzadas en la Figura 3; el «disco» es la elipse de OpenCV (sobredimensionada) y las diagonales miden 37 px, no 51 como declara el texto; Apéndice E describe una regla multiescala que el método ya no tiene | 2 |

---

## Fase 4 — Documentos (43 h) · solo con los números cerrados

| # | Entregable | Horas |
|---|---|---|
| 4.1 | Avances (dos variantes o una, según la decisión sobre la libre), Excel y README | 4 |
| 4.2 | **Reencuadre**: objetivo general, 5 objetivos específicos, problema, hipótesis con veredicto, conclusiones y limitaciones (texto ya redactado en `Reencuadre_Propuesto.md`) | 8 |
| 4.3 | **Libro** `Tesis_Borrador_V3.docx`: sincronizar con los datos vigentes (hoy está una regeneración por detrás: publica LP 3,44 / propuesta 3,67 contra 3,911 / 3,394), aplicar el reencuadre, insertar las tablas de la Fase 2 | 25 |
| 4.4 | Presentación de defensa: rehacer 6-8 diapositivas | 6 |

---

## Total y calendario

| Escenario | Horas |
|---|---|
| Mínimo defendible (Fases 0, 1 sin 1.2, 3 y 4) | ~57 |
| Con los experimentos que cierran los tres riesgos (todo salvo 1.2 y 2.5) | ~72 |
| Completo | ~85 |

En jornadas de 4 h: 14, 18 y 21 jornadas respectivamente. Con defensa prevista en septiembre
de 2026 hay margen incluso para el escenario completo.

---

## Decisiones pendientes del autor

1. **¿Corregir la banda base de la Pirámide de Laplace (1.2)?** Perjudica el margen de la
   propuesta pero cierra una contradicción entre el código y un hallazgo que el libro declara
   como propio. Recomendación: sí, corregirla — es el tipo de cosa que un examinador encuentra.
2. **¿Curvelet: renombrar (2 h) o instalar `curvelops` y recomputar (15-20 h)?**
   Recomendación: renombrar. Los resultados no cambian y el crédito queda correcto.
2b. **RESUELTO (31/07): el análisis se mantiene en las nueve métricas clásicas.** Decisión del
   autor, por fidelidad a la metodología del trabajo de referencia. Queda pendiente la frase que
   declara las ocho métricas calculadas y no analizadas (ver 2.3).
3. **¿Cuál de los tres encuadres?** Auditoría del protocolo (7,8/10), caracterización del
   compromiso (7,7) o cambio mínimo (6,7).
4. **¿Test ampliado de complementariedad (2.5)?** Es lo único que puede dar significancia al
   objetivo declarado de la tesis.
5. **¿Qué se hace con la variante libre?** Recomendación: retirarla del paquete de entrega.
6. **Externo:** verificar con el reglamento y el comité de la UCOM si modificar objetivos e
   hipótesis respecto del protocolo aprobado requiere aprobación formal, y con qué plazos.
