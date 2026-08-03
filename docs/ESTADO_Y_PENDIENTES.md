# Estado y pendientes — 3 de agosto de 2026

Punto de retomada. Todo lo que sigue está verificado; lo que no, está marcado como tal.

## Cómo correr las cosas

Las dependencias viven en `.venv`, **no** en el Python del sistema:

```
.venv\Scripts\python.exe -X utf8 experiments/<script>.py
```

Tres verificadores, todos en 0 fallos al cierre:

| Script | Qué comprueba |
|---|---|
| `verificar_entregables.py` | los cuatro entregables contra los CSV: medias, ranking, detección, afirmaciones retiradas, coherencia entre documentos, figuras embebidas por md5, montajes y paginación |
| `verificar_libro.py` | el libro en detalle, incluido el índice y las cinco figuras embebidas |
| `triar_hallazgos.py` | reparte los 106 hallazgos de la reverificación en YA_APLICADO / A_LEER / PENDIENTE; acepta `--gravedad` y `--doc` |

Compilar el libro exige la cirugía XML del scratchpad (desempaquetar el docx, editar
`word/document.xml`, reempaquetar, PDF por LibreOffice). **Al terminar hay que
recalcular el índice**: es texto fijo, no un campo de Word, y cualquier inserción lo
desfasa.

## Estado de los entregables

| | | |
|---|---|---|
| Libro | 72 pág. | 36 referencias auditadas, sección 5.8 de auditoría del protocolo |
| Deck | 22 láminas + reserva | |
| Avances | 60 pág. | |
| README | 563 líneas | |

## Pendientes, por prioridad

### 1. Cuatro hallazgos `falso` sin aplicar

```
.venv\Scripts\python.exe -X utf8 experiments/triar_hallazgos.py --gravedad falso
```

- **Deck, lámina 19 — el más grave.** Dice «H6 RECHAZADA» y corresponde **SE SOSTIENE**.
  H6 enuncia que *el orden de mérito no predice la utilidad en la tarea*, y la
  evidencia de la propia fila (ρ = +0,214, p = 0,645, el conteo por escena) la
  **confirma**. Lo que queda rechazado es la hipótesis contraria. Error introducido al
  reetiquetar las hipótesis del deck; la lámina 6 la enuncia bien.
- **Libro, Apéndice B.** Cita `pso_grid_search.csv` como la tabla de la aptitud
  publicada; ese archivo es de la aptitud **paralela F_apt** (su columna se llama
  distinto). La de F_o es `pso_grid_search_fo_propuesta.csv`.
- **Libro §6.1.** Queda vivo el pasaje sobre los líderes de Q0/QW; la parte de §5.3 ya
  se corrigió. Líderes reales: Q0 → DTCWT (0,7411), QW/FMI/QE → pirámide de Laplace.
- Uno más del libro, en el mismo filtro.

### 2. Los 26 hallazgos restantes de la reverificación

13 PENDIENTE y 17 A_LEER en `docs/fuentes/triage.json`, con el reemplazo propuesto de
cada uno. Dos que ya se leyeron y son reales:

- **Avances p. 24** reporta el experimento de peso igualado como «de 3,961 a 4,711»
  mientras el libro, el deck y el README reportan **3,528 frente a 3,694**.
- **Avances p. 11** da un F_o que contradice la Tabla 1 del propio informe, cuatro
  páginas antes.

**Criterio de trabajo, que conviene mantener:** verificar cada hallazgo ejecutando el
cálculo antes de escribir. De 17 verificados, 17 resultaron reales — pero en esta
sesión los agentes también entregaron dos cifras equivocadas (el conteo de `r_opt`,
que es 16 de 25 y no 18; y el margen a peso igualado, que es 0,167 y no 0,683). Donde
el hallazgo describa un experimento inexistente: poner el resultado medido, o retirar
la afirmación.

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
- **Notas del orador del deck**: escritas por lámina en `docs/Plan_Deck_Defensa.md`,
  con presupuesto de tiempo para los 20 minutos. Sin aplicar.
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
