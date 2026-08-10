# Historial de documentos de trabajo

Documentos que ya cumplieron su función y **no describen el estado actual del proyecto**.
Se conservan porque son la trazabilidad de decisiones tomadas: por qué se reencuadró el
trabajo, qué se auditó y con qué resultado, y qué se había acordado al principio.

**Nada de acá se usa como referencia de cifras.** Varios traen números de un corpus
anterior —de 19 pares, antes de sustituir el par corrupto— y conclusiones que después se
invirtieron. El estado vigente está en `../ESTADO_Y_PENDIENTES.md` y en los entregables.

| Archivo | Qué es |
|---|---|
| `Reencuadre_Propuesto.md` | borrador de reencuadre descartado a favor de Reencuadre_Final |
| `Reencuadre_Final.md` | su texto ya se aplico al libro; conserva el POR QUE del reencuadre |
| `Secuencia_Ajuste.md` | plan de cinco fases ya ejecutado; acta de las decisiones del autor |
| `Auditoria_Interna.md` | primera auditoria del pipeline; sus nueve defectos estan cerrados |
| `Auditoria_Metodologia.md` | auditoria de la metodologia; acta de nacimiento del segundo aporte |
| `Reverificacion_Informe.md` | cola de un informe; su unico pendiente se migro a ESTADO |
| `Informe_Revision_Mesa_Examinadora.docx` | revision previa a mesa del 3 de julio |
| `Plan_Replanteo_TFM.docx` | acuerdo de alcance de junio, superado por Reencuadre_Final |
| `Resultados_Optimos_por_Imagen.pdf` | óptimo (r, m) de cada escena; anexo de trabajo, no entregable |

Se movieron acá el 8 de agosto de 2026. La carpeta se llama `historial` y no
`_obsoletos` a propósito: `.gitignore` ya declaraba `docs/_obsoletos/`, así que archivar
ahí habría sacado estos nueve documentos del control de versiones.

## Cifras superadas, documento por documento

Tres de los archivados —`Reencuadre_Final.md`, `Auditoria_Metodologia.md` y
`Auditoria_Interna.md`— llevan un aviso en su propio encabezado con el detalle de qué
número de ellos ya no vale y por qué. Se lee antes que cualquier cifra.

El cuarto caso es el PDF, que no se puede encabezar, y su situación es distinta:

- **`Resultados_Optimos_por_Imagen.pdf`** — la copia que estaba versionada **sí traía
  cifras muertas**: exhibía entre sus escenas al par corrupto, cuyo canal visible era una
  copia byte a byte del infrarrojo, de modo que toda métrica de fidelidad le daba su valor
  perfecto. Pero su generador, `experiments/make_reporte_optimos.py`, lee los CSV vigentes,
  así que el arreglo fue volver a correrlo: la copia de acá es del corpus de 20 pares y no
  contiene el par corrupto. Queda archivado igual porque **no es un entregable** —el informe
  de avances ya publica el óptimo por escena—, y por eso el generador ahora escribe
  directamente en esta carpeta y no en `docs/`.
