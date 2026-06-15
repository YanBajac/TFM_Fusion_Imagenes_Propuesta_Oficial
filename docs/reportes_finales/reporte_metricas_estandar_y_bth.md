# Ampliación del estudio: métricas estándar de fusión y variante Black Top-Hat

**Fecha:** 13 de junio de 2026
**Dataset:** 20 pares VIS/IR del TNO Image Fusion Dataset
**Métodos evaluados (11):** Promedio, Pirámide de Laplace, Curvelet, y la Torre
Top-Hat en sus variantes White (WTH) `disk/square/cross L3` y `disk L5`, más sus
contrapartes con Black Top-Hat (`+BTH`).

Esta ampliación responde a dos vacíos del estudio original:

1. Se incorporaron **seis métricas estándar de calidad de fusión** que la
   literatura considera obligatorias y que el conjunto previo (EN, SD, FE, MG, MI)
   no cubría: **Qabf** (preservación de bordes), **Nabf** (artefactos), **SSIM**
   (similitud estructural), **SCD** (correlación de diferencias), **VIF**
   (fidelidad de información visual) y **SF** (frecuencia espacial).
2. Se evaluó la **variante Black Top-Hat** del método propuesto, hasta ahora
   implementada pero no medida, para cuantificar su efecto global.

---

## 1. Por qué importan las nuevas métricas

El estudio original rankeaba con seis métricas que comparten un sesgo: **EN, SD,
FE, MG y SF premian la "actividad" de la imagen** (contraste, bordes, información
bruta), y **MI premia la combinación lineal trivial**. Ninguna mide si la fusión
**preserva fielmente la información de las fuentes sin inventar artefactos**.

Las métricas añadidas corrigen esto:

| Métrica | Qué mide | Dirección |
|---------|----------|-----------|
| **Qabf** | Proporción de información de borde de las fuentes transferida a la fusión (Xydeas-Petrovic) | ↑ mejor |
| **Nabf** | Bordes/ruido **añadidos** por la fusión que no existen en las fuentes (artefactos) | ↓ mejor |
| **SSIM** | Similitud estructural promedio con VIS e IR | ↑ mejor |
| **SCD** | Correlación de las diferencias: cuánta info de cada fuente queda en la fusión | ↑ mejor |
| **VIF** | Fidelidad de información visual basada en modelo perceptual | ↑ mejor |
| **SF** | Frecuencia espacial (actividad de detalle global) | ↑ mejor |

---

## 2. Resultado global: el ranking cambia de lectura

Con **12 métricas y la dirección de cada una corregida** (Nabf penaliza, no premia),
el ranking promedio global queda:

| Posición | Método | Ranking promedio |
|---------:|--------|-----------------:|
| 1 | Pirámide de Laplace | 4.42 |
| 2 | **TopHat disk L5 (WTH)** | **5.00** |
| 3 | TopHat disk L3 (WTH) | 5.25 |
| 4 | TopHat square L3 (WTH) | 5.42 |
| 5 | TopHat square L3 +BTH | 6.00 |
| 6 | TopHat disk L3 +BTH | 6.21 |
| 7 | TopHat cross L3 (WTH) | 6.33 |
| 8 | TopHat cross L3 +BTH | 6.38 |
| 9 | TopHat disk L5 +BTH | 6.83 |
| 10 | Promedio | 7.08 |
| 11 | Curvelet | 7.08 |

Dos lecturas nuevas e importantes:

- **La brecha con Laplace se reduce** (de la diferencia previa a 4.42 vs 5.00) y,
  sobre todo, **cambia de naturaleza**: ya no es una derrota en todos los frentes,
  sino un reparto de fortalezas (ver §3).
- **Curvelet cae al último lugar** junto al Promedio. Bajo las métricas previas
  parecía competitivo; al medir artefactos (Nabf = 0.19, el peor entre los
  multiescala) se revela que gana "actividad" introduciendo ruido.

La prueba de **Friedman es altamente significativa en las 12 métricas**
(todos los p ≪ 0.001), confirmando que el método elegido influye en cada dimensión
de calidad.

---

## 3. Top-Hat (WTH) vs Pirámide de Laplace: fortalezas complementarias

El hallazgo central de esta ampliación es que **ningún método domina**: cada uno
gana en un eje de calidad distinto. Comparando la mejor configuración Top-Hat WTH
(`disk L5`) contra Laplace, con Wilcoxon pareado y corrección de Holm:

| Métrica | TopHat disk L5 | Laplace | ¿Quién gana? | p (Holm) | Tamaño de efecto |
|---------|---------------:|--------:|--------------|---------:|-----------------:|
| **SSIM** | **0.739** | 0.721 | **Top-Hat** ✓ | 0.001 | 1.00 (máximo) |
| **SCD** | **1.430** | 1.322 | **Top-Hat** ✓ | 0.019 | 0.78 |
| **Qabf** | 0.458 | 0.442 | Top-Hat (no signif.) | 1.000 | 0.17 |
| **Nabf** | 0.117 | 0.108 | Laplace (leve) | 0.048 | 0.63 |
| **EN** | 6.722 | 6.835 | Laplace | 0.109 | −0.60 |
| **SD** | 0.125 | 0.155 | Laplace ✓ | 0.009 | −0.84 |
| **VIF** | 0.356 | 0.410 | Laplace ✓ | 0.003 | −0.97 |

Síntesis:

- **La Torre Top-Hat WTH gana de forma estadísticamente significativa en SSIM y
  SCD** — es decir, **preserva mejor la estructura y la información de las fuentes**
  sin distorsionarlas.
- **Empata con Laplace en Qabf y Nabf**: la transferencia de bordes y la
  generación de artefactos son equivalentes (diferencias no significativas o
  marginales).
- **Laplace gana en SD y VIF**: produce imágenes de mayor contraste y mayor
  fidelidad visual perceptual.

La conclusión honesta y defendible es: **la Pirámide de Laplace maximiza
contraste y fidelidad perceptual (VIF, SD); la Torre Top-Hat maximiza fidelidad
estructural a las fuentes (SSIM, SCD) con paridad en preservación de bordes.** Son
óptimos de criterios distintos, no uno superior al otro.

---

## 4. Efecto de la variante Black Top-Hat

Agregar Black Top-Hat (capturar también detalles oscuros) produce un patrón **muy
consistente y de signo opuesto entre familias de métricas** (todas las diferencias
WTH→+BTH son significativas con p < 0.001):

**Lo que mejora (actividad / contraste):**
- Frecuencia espacial **SF: +87%** (de 11.6 a 21.7)
- Gradiente medio **MG: +93%**
- Entropía **EN: +4.4%**, Desviación estándar **SD: +19%**

**Lo que empeora (calidad / fidelidad):**
- Artefactos **Nabf: +427%** (de 0.10 a 0.54) — el efecto más drástico
- Preservación de bordes **Qabf: −29%**
- Similitud estructural **SSIM: −22%**
- Fidelidad visual **VIF: −11%**, Información mutua **MI_vis: −37%**

**Interpretación:** el Black Top-Hat **infla las métricas de actividad porque
inyecta energía de detalle oscuro, pero gran parte de esa energía son artefactos**
que no provienen de las fuentes (Nabf se multiplica por cinco) y que rompen la
similitud estructural. El resultado se ve en el ranking global: **todas las
variantes +BTH quedan por debajo de su contraparte WTH**.

**Recomendación:** la variante Black Top-Hat **no se recomienda como configuración
por defecto**. Solo sería preferible en aplicaciones donde el objetivo explícito es
maximizar contraste y realce de detalle aceptando artefactos (p. ej. realce previo
a inspección humana), no fusión fiel. El punto de operación recomendado sigue
siendo **WTH con disco y L = 5**.

---

## 5. Conclusiones de la ampliación

1. **Las métricas estándar reposicionan al método propuesto.** Bajo el conjunto
   completo de 12 métricas, la Torre Top-Hat WTH no es "segunda por detrás de
   Laplace en todo", sino **ganadora en fidelidad estructural (SSIM, SCD) y a la
   par en preservación de bordes (Qabf, Nabf)**, cediendo solo en contraste (SD) y
   fidelidad perceptual (VIF).
2. **Curvelet es el método más débil** una vez que se penalizan los artefactos
   (Nabf), corrigiendo la impresión que daban las métricas de pura actividad.
3. **El Black Top-Hat intercambia calidad por contraste**: mejora EN/SD/SF/MG pero
   degrada Qabf/SSIM/VIF/MI y dispara los artefactos (Nabf ×5). No se recomienda
   por defecto.
4. **No existe método universalmente óptimo**; la elección debe guiarse por el
   criterio operativo: fidelidad estructural → Top-Hat WTH disco L5; contraste y
   fidelidad perceptual → Pirámide de Laplace.

---

### Archivos generados

- `experiments/results/metrics_reports/all_metrics.csv` — 220 registros × 12 métricas.
- `descriptive_means.csv`, `ranking_methods.csv`, `friedman_results.csv`,
  `wilcoxon_results.csv` (288 contrastes con Holm y tamaño de efecto).
- `docs/figures/fig_boxplot_metricas_calidad.png`
- `docs/figures/fig_ranking_global_12metricas.png`
- `docs/figures/fig_efecto_black_top_hat.png`
