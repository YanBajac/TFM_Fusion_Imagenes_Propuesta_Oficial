trazar la procedencia de cifras obsoletas, no se auditaron. Los CSV no citados por ningún hallazgo (`fo_ablacion_*`, `superficie_aptitud_fo`, `comparacion_aptitudes*`, `complementariedad_criticas`) quedaron sin re-derivar. La URL pública del repositorio no se comprobó (sin red).

**Plan de deck.** Las notas y varios textos se corrigen contra `docs/Plan_Deck_Defensa.md`, cuyo cumplimiento general no se auditó. Se detectó de paso, sin reportarlo como defecto: la lámina 8 conserva los cinco párrafos «ANTES» (no se aplicó el «DESPUÉS», que agrega la remisión a la ablación), la lámina 18 tiene tres párrafos donde el plan pide cuatro (el cuarto es «Se sostiene H6, con muestra suficiente…»), la lámina 9 no lleva el sufijo «(OE2 / H5)» del título prescrito y el título de la lámina 23 difiere del plan.

**Anexos y tablas por escena del informe.** Cubiertos celda por celda por una dimensión (500 filas × 6 columnas de los Anexos 1-20 contra `pso_por_imagen.csv`; 700 valores y 100 negritas de las Tablas 4a-4e contra `all_metrics.csv`) y solo por muestreo por otra. No hay hueco material, pero la garantía descansa en una sola pasada.

**Observaciones que no son defectos demostrables** (conviene decidir, no corregir):
- Tabla 10 del libro: marca en negrita las cinco celdas de la propuesta, incluidas SD, MG y SF, donde no es la mejor de la fila. Si en esa tabla la negrita significa «columna del método propuesto» y no «mejor valor», conviene declararlo al pie para no chocar con el criterio de las Tablas 4, 5 y 7 (ver G5).
- Deck, lámina 2 (Contenido): la entrada «8. Resultados: el punto de operación del operador» no coincide literalmente con el título de la lámina 11 («8. Resultados cualitativos»). Diferencia nominal.
- Deck: la última lámina numerada es la 21 con denominador 22 en todos los pies; es lo previsto por el plan («| 22 | (sin footer) | — |»).
- `experiments/results/metrics_reports_libre/` mantiene una corrida paralela cuyo `wilcoxon_results.csv` difiere del oficial. No es un defecto, pero es el origen probable del 0,92 del README (M5); conviene rotularla como no publicada.

---

## 5. Cierre

No hay hallazgo inventado en este informe: cada defecto se apoya en una cifra re-derivada desde `all_metrics.csv` o desde los CSV crudos, o en una lectura directa del código. La capa de datos y de estadística está limpia —medias, nueve chi cuadrado, tres rankings y 99 contrastes con Holm reproducidos con error nulo o del orden de 1e-17, y la única incidencia en un artefacto de datos (m23) no la cita ningún documento—. Lo que queda por corregir es texto residual de versiones anteriores del trabajo, concentrado en cuatro focos: el abstract en inglés del libro, el bloque de conclusiones específicas y marco conceptual, el guion y la lámina de hipótesis del deck, y las cifras de detección y dependencias del README. Diez de los 65 defectos son graves en el sentido operativo de que un examinador puede señalarlos en mesa con el propio documento en la mano; el resto son cifras desactualizadas, sobreafirmaciones acotables y maquetación.