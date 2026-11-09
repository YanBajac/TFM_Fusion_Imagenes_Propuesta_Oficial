# El libro en LaTeX

Esta carpeta contiene el libro de la tesis *Fusión de imágenes infrarrojas y visibles mediante morfología matemática*, con el formato de las tesis de maestría de la Universidad Comunera, y su versión compilada en PDF.

## Contenido

```
docs/libro_v4/
├── Tesis_Bazan_Bajac.pdf  el libro compilado a partir de estas fuentes
├── main.tex              preámbulo, diseño, portada, carátula, hoja de aprobación y orden de los capítulos
├── referencias.bib       la bibliografía, en BibTeX
├── caps/
│   ├── 00_resumen.tex, 00_abstract.tex, 00_agradecimientos.tex
│   ├── 00_siglas.tex              Lista de abreviaturas y símbolos
│   ├── cap1_introduccion.tex      Introducción: problema, hipótesis, objetivos y alcance
│   ├── cap2_marco.tex             Marco teórico y conceptual
│   ├── cap3_metodologia.tex       Metodología
│   ├── cap4_resultados.tex        Resultados
│   ├── cap5_discusion.tex         Discusión
│   ├── cap6_conclusiones.tex      Conclusiones
│   ├── cap7_recomendaciones.tex   Recomendaciones
│   └── anexos.tex                 Participación en congresos y contrastes de Wilcoxon completos
├── tablas/               las siete tablas generadas desde los CSV (no se editan a mano)
└── figuras/              las imágenes del libro y su LEEME.md
```

El título, el subtítulo, los autores, el tutor y la fecha se definen una sola vez, al principio de `main.tex` (`\titulotesis`, `\subtitulotesis`, `\autorA`, `\autorB`, `\tutor`, `\fechaentrega`), y de ahí los toman la portada, la carátula, la hoja de aprobación y los metadatos del PDF.

La compilación produce `main.pdf`; `Tesis_Bazan_Bajac.pdf` es ese mismo resultado con el nombre de publicación.

## Tablas

Las tablas de `tablas/` las escribe `tools/generar_tablas_libro.py` a partir de los CSV de `experiments/results/metrics_reports/`. Cada una es un entorno `table` completo, salvo la de los anexos, que es una `longtable`, y los capítulos las traen con `\input`. Si un resultado cambia, se vuelve a ejecutar el generador desde la raíz del repositorio:

```
python tools/generar_tablas_libro.py
```

El generador borra de `tablas/` cualquier `tabla_*.tex` que ya no produce, para que ningún capítulo traiga una tabla desactualizada.

| Tabla | Capítulo | CSV de origen |
|:---|:---|:---|
| `tabla_medias_seis` | 4 | `descriptive_means_seis.csv`; el orden de los métodos, de `ranking_seis_metricas.csv` |
| `tabla_friedman_seis` | 4 | `friedman_seis_metricas.csv` |
| `tabla_ranking_seis` | 4 | `ranking_seis_metricas.csv` |
| `tabla_wilcoxon_resumen` | 4 | `wilcoxon_seis_metricas.csv` |
| `tabla_v2_tasas` | 4 | `m3fd_v2_tasas_precisas.csv` (si falta, `m3fd_v2_tasas.csv`) y `m3fd_v2_pares_semillas.csv` |
| `tabla_deteccion_tophat` | 4 | `m3fd_v2_contrastes_precisos.csv` (si falta, `m3fd_v2_contrastes.csv`), `m3fd_v2_pares_semillas.csv`, `m3fd_v2_prueba.csv` y `m3fd_v2_bootstrap_estudentizado.csv` |
| `tabla_wilcoxon_completa` | Anexos | `wilcoxon_seis_metricas.csv` y `sensibilidad_escenas_wilcoxon.csv` |

Los scripts que escriben cada CSV figuran en el README de la raíz (sección 5.1). La tabla de las seis métricas del capítulo 3 (`tab:metricas`) está escrita en el propio capítulo, porque no depende de ningún resultado.

## Figuras

Cada figura, salvo el logotipo, tiene su generador en `experiments/`, que la escribe en `figuras/`. La correspondencia entre figuras, generadores y datos está en `figuras/LEEME.md`.

## Compilación

El libro usa la clase `book`, `babel` en español, `biblatex` con el estilo `apa` (paquete `biblatex-apa`) y Biber como procesador de la bibliografía. Se compila con pdfLaTeX. Hay tres caminos, y los tres usan los mismos archivos:

1. **Distribución local** (MiKTeX o TeX Live), desde esta carpeta:

   ```
   latexmk -pdf main.tex
   ```

   o, paso a paso, `pdflatex main`, `biber main`, `pdflatex main` y `pdflatex main`. La primera compilación con MiKTeX puede tardar varios minutos si la distribución descarga paquetes que faltan. Los archivos auxiliares que quedan en esta carpeta, y el `main.pdf`, están excluidos por el `.gitignore`.

2. **Script de compilación**, desde la raíz del repositorio:

   ```
   python tools/compilar_libro_local.py
   ```

   Copia esta carpeta a otra aparte, excluida por el `.gitignore`, y compila allí (pdfLaTeX, Biber y dos pasadas más), para que los archivos auxiliares no queden junto a las fuentes. Al terminar informa la cantidad de páginas, los errores, las referencias y citas sin definir y los renglones que se salen del margen más de 1 pt, e imprime la ruta del PDF. Devuelve un código distinto de cero si hubo errores o referencias sin definir. Necesita `pdflatex` y `biber` en el PATH; en Windows agrega por su cuenta la carpeta de una instalación de MiKTeX para el usuario. Con `--abrir`, en Windows, abre el PDF al terminar.

3. **Overleaf**, desde la raíz del repositorio:

   ```
   python tools/empaquetar_overleaf.py
   ```

   Antes de empaquetar comprueba que las opciones de la clase sean válidas, que los paquetes del preámbulo figuren en su lista de paquetes de TeX Live, que `biblatex` use Biber y que existan todos los archivos incluidos y todas las imágenes referenciadas. Si todo está bien, arma `docs/libro_v4_overleaf.zip` con los `.tex`, el `.bib` y solo las imágenes que el libro usa. El archivo se sube con *New Project > Upload Project*; el compilador es pdfLaTeX y la bibliografía se procesa con Biber.

## Verificación

```
python tools/verificar_libro_v4.py
```

Revisa, sin compilar, lo que más suele romperse:

1. que cada cita del texto tenga su entrada en `referencias.bib`;
2. que cada referencia cruzada apunte a una etiqueta que exista;
3. que cada `\include` e `\input` nombre un archivo que exista;
4. que cada `\includegraphics` apunte a una imagen que exista.

Si alguna de esas comprobaciones falla, termina con código 1. Además informa las entradas del `.bib` que no se citan.

## Bibliografía

`referencias.bib` reúne las referencias en formato BibTeX. `main.tex` la carga con `\addbibresource` y la imprime con el estilo APA en español (`\DeclareLanguageMapping{spanish}{spanish-apa}`), con raya corta en los rangos de páginas. Una referencia nueva se agrega como entrada en ese archivo y se cita con `\textcite` o `\parencite`; `tools/verificar_libro_v4.py` avisa si queda alguna cita sin entrada.
