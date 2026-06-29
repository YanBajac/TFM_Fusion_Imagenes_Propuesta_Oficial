# Análisis Integral de la Torre de Fusión Top-Hat (Modo Multiescala)

Este documento detalla los resultados cuantitativos obtenidos al evaluar de forma exhaustiva 720 integraciones totales. Las configuraciones de modo multiescala variaron cruzando:
- 3 Elementos Estructurantes (`disk`, `square`, `cross`)
- 4 Niveles de profundidad (`2`, `3`, `4`, `5`)
- 3 Radios Base del Elemento (`2`, `3`, `5` píxeles)
Sobre los 20 pares base de imágenes VIS/IR extraídas del dataset TNO.

## 1. Configuraciones Óptimas por Métrica

El análisis de las medias globales revela empíricamente las siguientes configuraciones maximizadoras según las métricas sin referencia (buscamos maximizar estos valores):

- **Mejor EN** *(Entropía (riqueza de información))*: Elemento `disk`, Niveles `5`, Radio Base `5` logrando un promedio óptimo de **6.6735**.
- **Mejor SD** *(Desviación Estándar (contraste general))*: Elemento `cross`, Niveles `5`, Radio Base `5` logrando un promedio óptimo de **0.1513**.
- **Mejor FE** *(Eficiencia de Fusión (ganancia relativa de información))*: Elemento `disk`, Niveles `5`, Radio Base `5` logrando un promedio óptimo de **1.0559**.
- **Mejor MG** *(Gradiente Medio (nitidez de bordes y texturas))*: Elemento `disk`, Niveles `5`, Radio Base `2` logrando un promedio óptimo de **0.0226**.
- **Mejor MI_vis** *(Información Mutua transferida desde el sensor Visible)*: Elemento `cross`, Niveles `2`, Radio Base `2` logrando un promedio óptimo de **2.4670**.
- **Mejor MI_ir** *(Información Mutua transferida desde el sensor Térmico (IR))*: Elemento `cross`, Niveles `2`, Radio Base `2` logrando un promedio óptimo de **1.3313**.

## 2. Resumen Estadístico Total (Promedios)

A continuación se expone la tabla íntegra de promedios para las 36 configuraciones evaluadas (ordenada alfabéticamente):

| Structuring_Element   |   Levels |   Base_Radius |     EN |     SD |     FE |     MG |   MI_vis |   MI_ir |
|:----------------------|---------:|--------------:|-------:|-------:|-------:|-------:|---------:|--------:|
| cross                 |        2 |             2 | 6.608  | 0.1488 | 1.0432 | 0.022  |   2.467  |  1.3313 |
| cross                 |        2 |             3 | 6.6175 | 0.1489 | 1.0449 | 0.0221 |   2.3629 |  1.2964 |
| cross                 |        2 |             5 | 6.6264 | 0.1494 | 1.0466 | 0.0221 |   2.2433 |  1.2537 |
| cross                 |        3 |             2 | 6.6322 | 0.1489 | 1.0478 | 0.0223 |   2.3188 |  1.27   |
| cross                 |        3 |             3 | 6.6398 | 0.1492 | 1.0492 | 0.0223 |   2.2106 |  1.234  |
| cross                 |        3 |             5 | 6.649  | 0.15   | 1.0509 | 0.0223 |   2.0892 |  1.1904 |
| cross                 |        4 |             2 | 6.6462 | 0.1491 | 1.0504 | 0.0224 |   2.2124 |  1.2278 |
| cross                 |        4 |             3 | 6.6535 | 0.1497 | 1.0518 | 0.0224 |   2.1033 |  1.1916 |
| cross                 |        4 |             5 | 6.6625 | 0.1507 | 1.0534 | 0.0224 |   1.99   |  1.149  |
| cross                 |        5 |             2 | 6.6559 | 0.1494 | 1.0523 | 0.0225 |   2.1295 |  1.1963 |
| cross                 |        5 |             3 | 6.6631 | 0.1501 | 1.0536 | 0.0225 |   2.0242 |  1.1598 |
| cross                 |        5 |             5 | 6.6697 | 0.1513 | 1.0548 | 0.0225 |   1.92   |  1.1183 |
| disk                  |        2 |             2 | 6.618  | 0.1483 | 1.045  | 0.0222 |   2.4551 |  1.2545 |
| disk                  |        2 |             3 | 6.6258 | 0.1483 | 1.0464 | 0.0223 |   2.3502 |  1.2126 |
| disk                  |        2 |             5 | 6.6365 | 0.1486 | 1.0484 | 0.0222 |   2.2139 |  1.1719 |
| disk                  |        3 |             2 | 6.6446 | 0.1483 | 1.0501 | 0.0224 |   2.2842 |  1.1984 |
| disk                  |        3 |             3 | 6.6521 | 0.1485 | 1.0515 | 0.0224 |   2.1609 |  1.1559 |
| disk                  |        3 |             5 | 6.6586 | 0.1491 | 1.0529 | 0.0223 |   2.0331 |  1.1144 |
| disk                  |        4 |             2 | 6.6592 | 0.1484 | 1.0529 | 0.0225 |   2.1537 |  1.1586 |
| disk                  |        4 |             3 | 6.6646 | 0.149  | 1.054  | 0.0225 |   2.034  |  1.1171 |
| disk                  |        4 |             5 | 6.6693 | 0.1496 | 1.055  | 0.0223 |   1.9243 |  1.0794 |
| disk                  |        5 |             2 | 6.6669 | 0.1487 | 1.0545 | 0.0226 |   2.0547 |  1.1288 |
| disk                  |        5 |             3 | 6.6704 | 0.1493 | 1.0552 | 0.0225 |   1.9461 |  1.0896 |
| disk                  |        5 |             5 | 6.6735 | 0.15   | 1.0559 | 0.0224 |   1.8512 |  1.0522 |
| square                |        2 |             2 | 6.6235 | 0.1483 | 1.046  | 0.0223 |   2.3923 |  1.23   |
| square                |        2 |             3 | 6.6306 | 0.1484 | 1.0474 | 0.0223 |   2.2893 |  1.1955 |
| square                |        2 |             5 | 6.6399 | 0.1489 | 1.0492 | 0.0221 |   2.1669 |  1.1603 |
| square                |        3 |             2 | 6.6484 | 0.1484 | 1.0508 | 0.0224 |   2.2144 |  1.1761 |
| square                |        3 |             3 | 6.6545 | 0.1488 | 1.0521 | 0.0223 |   2.1016 |  1.1391 |
| square                |        3 |             5 | 6.659  | 0.1493 | 1.053  | 0.0221 |   1.9906 |  1.1045 |
| square                |        4 |             2 | 6.661  | 0.1487 | 1.0533 | 0.0225 |   2.0849 |  1.1373 |
| square                |        4 |             3 | 6.6642 | 0.1492 | 1.0541 | 0.0224 |   1.9799 |  1.1018 |
| square                |        4 |             5 | 6.6684 | 0.1498 | 1.0549 | 0.0222 |   1.8895 |  1.0701 |
| square                |        5 |             2 | 6.668  | 0.1491 | 1.0548 | 0.0226 |   1.9917 |  1.109  |
| square                |        5 |             3 | 6.6692 | 0.1495 | 1.0552 | 0.0224 |   1.8973 |  1.0756 |
| square                |        5 |             5 | 6.6685 | 0.1503 | 1.0552 | 0.0222 |   1.8185 |  1.0415 |

## 3. Conclusiones para la Tesis y Guía de Interpretación

1. **Balance de Escala (L y R₀)**: Un número masivo de niveles y radios inmensos no garantiza siempre una mejor métrica; puede introducir saturación. La tabla de arriba ayuda a discernir si un nivel moderado (ej. L=3, R=3) extrae métricas lo suficientemente cercanas al óptimo pero requiriendo menos esfuerzo computacional.
2. **Impacto de la Geometría**: A nivel microscópico, los contornos orgánicos (`disk`) frente a los ángulos rectos (`square`, `cross`) arrojan diferentes valores de **MG**. Revisar cuál elemento triunfa constantemente en Gradiente Medio (`MG`) dictará el mejor preservador de bordes visuales puros.
3. **Múltiples Fuentes (MI)**: La asimetría natural entre los resultados de `MI_vis` y `MI_ir` sube acorde al peso final que la Transformada le da genéticamente a una u otra imagen durante el umbral de 'energía local' por capa.

*Nota Científica: Con estos resultados tabulados es ahora factible formular comparaciones de caja (Boxplots) o validar si la diferencia de Entropía (`EN`) entre geometrías es estadísticamente significativa usando el test de Wilcoxon o Friedman mencionado en el archivo general del repo.*
