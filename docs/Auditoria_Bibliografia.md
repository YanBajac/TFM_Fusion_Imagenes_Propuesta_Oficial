# Auditoría de la bibliografía — 33 referencias

Verificación realizada el 2 de agosto de 2026 contra Crossref, OpenAlex, DataCite y
arXiv. Método: para cada entrada se buscó el registro exigiendo **coincidencia de
título y de apellidos**, y cuando la coincidencia no se alcanzó se declaró «no
verificada» en lugar de aceptar el candidato más parecido.

Script: `<scratchpad>/fuentes/v2.py`. Datos crudos: `fuentes/v2.json`.

> **Alcance.** Se verificó que las obras **existen** y que sus **datos
> bibliográficos** son correctos. No se verificó que digan lo que la tesis les
> atribuye: eso exige leer los textos, y la mayoría está tras muro de pago (ver
> §4).

---

## 1. Resultado global

| Estado | N.º |
|---|---|
| Correctas | 21 |
| Con defectos confirmados | 8 |
| A verificar por catálogo (libros y tesis sin DOI) | 4 |
| Inventadas o inexistentes | **0** |

**Ninguna referencia es inventada.** Las 33 remiten a trabajos reales y todas
están citadas en el texto; el cruce en ambas direcciones no encontró citas
huérfanas ni entradas sin citar.

---

## 2. Defectos confirmados

### Graves — el localizador declarado no contiene la obra

**2.1 · Ref. 28 — Toet, colección TNO.** Es la fuente del corpus experimental.

- Declara: `Toet, A. (2014). The TNO multiband image data collection. Data in Brief, 4, 187–192.`
- Corresponde: **2017**, *Data in Brief*, **15**, **249–251**, DOI `10.1016/j.dib.2017.09.038`.
- Existe una sola obra con ese título en *Data in Brief* y es la de 2017. El año
  2014 corresponde al depósito del conjunto de datos en Figshare
  (`10.6084/m9.figshare.1008029`, hoy con año de publicación 2022 por versiones
  posteriores), que es una obra distinta —un dataset, no un artículo—.
- Si se quiere citar el corpus y no el artículo, corresponde una entrada de
  dataset aparte.

**2.2 · Ref. 3 — Bai, Zhou y Xue.** Fuente metodológica del realce por top-hat.

- Declara: `(2015). … Optics & Laser Technology, 65, 145–150.`
- El **volumen 65 de esa revista no contiene ningún trabajo de Bai con ese
  título**: la búsqueda por revista, autor y volumen devuelve cero resultados.
- La obra existente es de **2012**, vol. **44(2)**, **328–336**,
  DOI `10.1016/j.optlastec.2011.07.009`.

**2.3 · Ref. 29 — Wang, J. et al., representación dispersa no negativa.**

- Declara: `(2017). … Infrared Physics & Technology, 80, 1–9.`
- El **volumen 80 no contiene ese trabajo**: cero resultados.
- La obra existente es de **2014**, vol. **67**, **477–489**,
  DOI `10.1016/j.infrared.2014.09.019`.

**2.4 · Ref. 17 — Mukhopadhyay y Chanda.** Antecedente morfológico multiescala.

- Declara 2001; el registro es **2000** (*Signal Processing*, 80(4), 685–696,
  DOI `10.1016/S0165-1684(99)00161-9`). Volumen, número y páginas coinciden.
- Importa si en el cuerpo se argumenta precedencia histórica.

### Menores — paginación y localizador

| Ref. | Declara | Corresponde | DOI |
|---|---|---|---|
| 2 · Bai (2013) | 23(1), 244–263 | **542–554** (vol. 23 tiene un solo trabajo suyo con ese título) | `10.1016/j.dsp.2012.09.013` |
| 10 · LLVIP (ICCVW 2021) | 3496–3504 | **3489–3497** | `10.1109/ICCVW54120.2021.00389` |
| 13 · M3FD (CVPR 2022) | 5802–5811 | **5792–5801** | `10.1109/CVPR52688.2022.00571` |
| 19 · Piella y Heijmans | vol. 3 | Crossref registra vol. **2**, paginación `III-173-6`, año de publicación 2004 (congreso de 2003) | `10.1109/ICIP.2003.1247209` |

### Estructural — cita sin respaldo

**2.5 · «Kingsbury» en la Tabla 3.** El comparativo DTCWT lleva como referencia el
apellido **«Kingsbury», sin año y sin entrada en la bibliografía**. Es la única
cita del documento sin respaldo. Corresponde añadir la entrada —el trabajo
canónico es Kingsbury, N. (2001), *Complex wavelets for shift invariant analysis
and filtering of signals*, Applied and Computational Harmonic Analysis, 10(3),
234–253— o remitir a Tao et al. (2010), que ya está en la bibliografía y es el que
efectivamente sustenta la variante usada.

Además, las filas de DWT y Top-Hat clásico de la Tabla 3 tienen «—» en la columna
de referencia, pudiendo remitir a fuentes ya presentes en la bibliografía.

---

## 3. Falsos positivos — no corregir

Un primer emparejador que buscaba solo por título produjo alarmas que la
verificación estricta descartó. Se documentan para que no se «corrijan» por error:

- **Ref. 5 · Burt y Adelson (1983).** Correcta tal como está: DOI
  `10.1109/TCOM.1983.1095851` confirma 1983, *IEEE Transactions on
  Communications*, 31(4), 532–540. El candidato de 2009 era una reimpresión en un
  volumen recopilatorio.
- **Ref. 11 · Kennedy y Eberhart (1995).** Correcta: DOI
  `10.1109/ICNN.1995.488968` confirma *Proceedings of ICNN'95*, vol. 4,
  1942–1948. El candidato de 2007 era un trabajo ajeno de otros autores.
- **Ref. 33 · Zhang y Demiris (2023).** Correcta: DOI `10.1109/TPAMI.2023.3261282`.
  Un primer intento la confundió con *Infrared and Visible Image Fusion using a
  Deep Learning Framework* de Li, Wu y Kittler (ICPR 2018), que es otro trabajo.
- **Recuentos de autores.** Todas las alarmas de «N autores declarados vs M» eran
  de un parser que descartaba apellidos de dos letras (Li, Ma, Yu, Hu, Wu, He,
  Fan). Las listas de autores de la tesis coinciden con las fuentes.

---

## 4. Disponibilidad de los textos

Solo **2 de las 33** se pudieron descargar. El resto está en revistas de
suscripción (Elsevier, IEEE, Springer) y no hay copia legítima de acceso abierto.
No se recurrió a sitios que eluden muros de pago.

### Descargados — en `docs/fuentes/`

| Ref. | Archivo | Fuente |
|---|---|---|
| 10 | `10_LLVIP_Jia_2021.pdf` (22,6 MB) | arXiv 2108.10831v4 |
| 13 | `13_M3FD_Liu_2022.pdf` (14,7 MB) | arXiv 2203.16220v1 |

### Acceso abierto pero no descargable por script

- **Ref. 28 · Toet (2017)**, *Data in Brief*: es **gold OA con licencia
  CC BY-NC-ND**, pero ScienceDirect responde HTTP 403 a las peticiones
  programáticas. Descargable a mano desde
  <https://doi.org/10.1016/j.dib.2017.09.038>.
- **Ref. 16 · Malviya y Saxena (2014)**, *IJCA*: acceso abierto en
  <https://doi.org/10.5120/17691-8656>.

### Cerradas (25)

Refs. 1, 2, 3, 5, 6, 7, 9, 11, 12, 14, 15, 17, 19, 20, 22, 23, 25, 26, 27, 29,
30, 31, 32, 33 y los libros. Para leerlas hace falta acceso institucional. La UCOM
o la biblioteca de la UNA pueden darlo; varias (Friedman 1937, Wilcoxon 1945) están
en JSTOR, al que muchas bibliotecas suscriben.

---

## 5. Lo que queda sin verificar

**5.1 · Ref. 18 — Ortega Rodríguez y Espinoza Ríos (2025).** Es la referencia
**más importante del trabajo**: de ella provienen la función de aptitud
`F_o = SSIM_avg + E_n + PSNR_n`, el rango publicado `m ∈ [0,30; 2,00]` y el
barrido de 25 configuraciones de enjambre. Es un proyecto de trabajo final de
grado de la Facultad Politécnica de la UNA, sin DOI y sin copia localizada en
línea.

Esto tiene una consecuencia que conviene declarar en la defensa: **un lector
externo no puede hoy comprobar de dónde salen la aptitud ni el rango de *m***, que
son las dos decisiones que gobiernan la configuración adoptada. Recomendación:
obtener el PDF de la FPUNA y archivarlo junto a la tesis, o —mejor— reproducir en
un apéndice la definición de la aptitud y el cuadro del barrido con atribución
explícita.

**5.2 · Libros (refs. 8, 21, 24).** Gonzalez y Woods (2018, 4.ª ed.), Serra (1982)
y Soille (2003, 2.ª ed.) no tienen registro propio en Crossref, que solo indexa
reseñas. Son obras de referencia estándar y sus datos son verosímiles, pero
conviene confirmar edición y año en el catálogo de la editorial o de una
biblioteca.

**5.3 · Contenido de las citas.** No se comprobó que cada fuente diga lo que la
tesis le atribuye. Las tres atribuciones que más conviene confirmar leyendo el
texto son:

1. **Bala et al. (2024)** — el esquema aditivo-sustractivo y el promediado de las
   respuestas lineales. Datos bibliográficos verificados exactos por DOI
   (`10.1007/s11227-024-05952-x`, vol. 80(9), 13317–13340); falta el fascículo
   `(9)` en la entrada. La tesis dice trasladar ese esquema del realce de fondo de
   ojo a la fusión VIS/IR: hay que poder sostener que el original hace lo que se
   le atribuye.
2. **Ortega y Espinoza (2025)** — ver 5.1.
3. Las de cada métrica (refs. 1, 9, 19, 22, 30, 32), que sostienen las
   definiciones de las ecuaciones 15 a 26.

---

## 6. Acciones sugeridas, en orden

1. Corregir las ocho entradas con defectos (§2) y añadir la entrada de Kingsbury o
   remitir a Tao et al. (2010).
2. Conseguir el trabajo de Ortega y Espinoza y archivarlo.
3. Añadir DOI a las entradas que lo tienen: APA 7 lo exige y hoy solo la ref. 4 lo
   lleva.
4. Confirmar los tres libros por catálogo.
5. Con acceso institucional, leer al menos Bala et al. (2024) y las seis de
   métricas para cerrar §5.3.
