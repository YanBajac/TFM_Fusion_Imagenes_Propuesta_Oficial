# Método óptimo basado en Top-Hat (disco + lineales) optimizado por PSO

**Fecha:** 16 de junio de 2026 · **Dataset:** 20 pares VIS/IR del TNO.

## 1. Motivación y referencias

Esta nueva propuesta integra dos líneas previas del grupo:

1. **Realce con Top-Hat multiescala de elementos circulares y lineales** (Román et al.,
   mamografías): por escala se calculan transformadas con cuatro SE lineales
   (0°, 45°, 90°, 135°) y uno circular, combinándolas para capturar tanto estructuras
   direccionales como regiones sin orientación predominante (ecuaciones 9–14 del paper).
2. **Fusión VIS/IR con Top-Hat optimizada por PSO** (Ortega & Espinoza, FPUNA 2025):
   `I_FUS = I_base + m·máx(WTH_IR, WTH_VIS) − m·máx(BTH_IR, BTH_VIS)`, con PSO ajustando
   el radio `r` del SE y el peso de contraste `m` mediante una aptitud multicriterio
   `F = SSIM_avg + E_n + PSNR_n`.

El **método óptimo** combina ambas: un operador Top-Hat con **elementos estructurantes
disco + lineales**, insertado en el esquema de fusión, con **PSO** optimizando su tamaño
y su peso de contraste.

## 2. Formulación

**Operador combinado** (por escala/SE de radio r):

```
WTH_disco = f − apertura(f, disco_r)
WTH_lineal = (1/4) Σ_θ [ f − apertura(f, lineal_{r,θ}) ],  θ ∈ {0°,45°,90°,135°}
WTH = WTH_disco + WTH_lineal           (modo "suma"; análogo para BTH con cierre)
```

**Fusión** (Ortega & Espinoza, ec. 12), con la imagen base `I_base = (VIS+IR)/2`:

```
I_FUS = I_base + m·máx(WTH_VIS, WTH_IR) − m·máx(BTH_VIS, BTH_IR)
```

**Optimización (PSO).** Variables: radio `r ∈ [1, 9]` y peso `m ∈ [0,3, 2,0]`.
Aptitud multicriterio (a maximizar): `F = SSIM_avg + E_n + PSNR_n` (normalizadas),
con `SSIM_avg` respecto a VIS e IR, `E_n` entropía normalizada y `PSNR_n` respecto a la
imagen base. Configuración: **30 partículas × 30 iteraciones** (≥30), enjambre global
sobre un subconjunto representativo de 10 escenas, inercia decreciente `ω: 0,9→0,4`,
`c1 = c2 = 1,5`.

## 3. Resultado de la optimización

El PSO convergió de forma **estable desde la iteración 3** y a lo largo de las 30
iteraciones al óptimo global:

> **r\* = 1,  m\* = 0,30**   (aptitud F = 1,989)

El óptimo se ubica en el borde inferior del espacio de búsqueda: la aptitud
`SSIM + E + PSNR` —dominada por términos de fidelidad— premia un realce **conservador**
(SE fino, peso moderado), que preserva la similitud con las fuentes. Es un hallazgo en sí
mismo: esa función de aptitud orienta al método hacia la fidelidad antes que al contraste.

## 4. Comparación con las 12 métricas (medias sobre 20 pares)

El método óptimo (disco+lineales, r=1, m=0,30) se evaluó junto a los 11 métodos previos:

| Métrica | TH Óptimo | Promedio | Laplace | TH disco L5 | Curvelet |
|---|---|---|---|---|---|
| **SSIM** ↑ | **0,761** | 0,792 | 0,721 | 0,739 | 0,731 |
| **SCD** ↑ | 1,353 | 1,325 | 1,322 | 1,430 | 1,321 |
| **Qabf** ↑ | 0,448 | 0,310 | 0,442 | 0,458 | 0,476 |
| **Nabf** ↓ | 0,121 | 0,000 | 0,108 | 0,117 | 0,192 |
| **VIF** ↑ | 0,322 | 0,330 | 0,410 | 0,356 | 0,307 |
| **SD** ↑ | 0,113 | 0,109 | 0,155 | 0,125 | 0,117 |
| **EN** ↑ | 6,598 | 6,518 | 6,835 | 6,722 | 6,664 |

Lecturas clave:

- **Lidera la similitud estructural (SSIM) entre todos los métodos reales de fusión**
  (rango 2 de 12, solo por detrás del promedio simple, que es estructuralmente trivial).
- Es **competitivo en preservación de bordes (Qabf 0,448 ≈ Laplace)** y en SCD, con
  artefactos bajos (Nabf 0,121).
- **Cede en contraste e información (SD, EN, FE)**: por eso su ranking global agregado
  sobre las 12 métricas queda en la franja media (≈7,0): el promedio de rangos penaliza
  las dimensiones de contraste que el método sacrifica deliberadamente en favor de la
  fidelidad.

## 5. Conclusión

El método óptimo basado en Top-Hat con elementos **disco + lineales** y parámetros
optimizados por **PSO** constituye una fusión **orientada a la fidelidad estructural**:
maximiza SSIM (entre los métodos reales) manteniendo buena preservación de bordes y bajos
artefactos, a costa de contraste. Refuerza la conclusión transversal de la tesis —no existe
un método universalmente óptimo; cada uno destaca en un criterio— y aporta un mecanismo
**automático y sin ajuste manual** (PSO) para fijar los hiperparámetros morfológicos.

**Trabajo futuro:** explorar una aptitud orientada a contraste/bordes (p. ej. maximizar
Qabf o SD), que llevaría al PSO a un punto de operación distinto; y la variante multiescala
en cascada (ecuaciones 15–21 del paper de mamografías).

### Archivos
- `src/fusion/optimal_top_hat.py` — operador y fusión.
- `experiments/pso_optimal_tophat.py` — PSO reanudable; estado en `experiments/results/pso/`.
- `docs/figures/fig_metodo_optimo.png` — comparación de métricas.
