# Evaluación orientada a tarea: detección de objetos sobre imágenes fusionadas

## 1. Motivación

Las métricas sin referencia (EN, SD, Qabf, SSIM, …) miden la **calidad intrínseca**
de la imagen fusionada, pero no responden la pregunta de **utilidad**: ¿una fusión
mejor hace que un sistema posterior (p. ej. un detector de personas o vehículos)
funcione mejor? Esta evaluación *orientada a tarea* (task-driven) conecta la fusión
con su aplicación real y enriquece la investigación: la fusión se juzga por cuánto
ayuda al detector, no solo por su apariencia.

Esquema general del pipeline:

```
VIS  ┐
     ├─►  Fusión (Promedio / Laplace / Curvelet / Top-Hat WTH / Top-Hat WTH+BTH)
IR   ┘                         │
                               ▼
                       Detector (YOLO)
                               │
                               ▼
        Métricas de entrenamiento, producción y detectabilidad
```

## 2. Herramientas

- **YOLO (Ultralytics, v8/v11)** — detector de objetos de una etapa, estándar
  actual para detección en tiempo real. Se entrena un modelo por modalidad/fusión.
- **Roboflow** — gestión, anotación y versionado del dataset etiquetado; exporta en
  formato YOLO listo para entrenar. Permite aumentar y dividir train/val/test.
- **Keras / TensorFlow** — tarea *downstream* alternativa (clasificación con
  transfer learning, p. ej. MobileNetV2) para verificar la utilidad de la fusión en
  un segundo tipo de modelo e independizar las conclusiones de una sola arquitectura.

## 3. Métricas de comparación

### 3.1 Entrenamiento (requieren dataset etiquetado)
| Métrica | Definición | Dirección |
|---|---|---|
| **mAP@0.5** | Precisión media promedio con IoU ≥ 0,5 | ↑ |
| **mAP@0.5:0.95** | mAP promediada sobre IoU 0,5–0,95 (paso 0,05); métrica COCO | ↑ |
| **Precision (P)** | TP / (TP + FP) | ↑ |
| **Recall (R)** | TP / (TP + FN) | ↑ |
| **F1** | 2·P·R / (P + R) | ↑ |
| **Curvas de pérdida** | box/cls/dfl loss vs época (train y val) | ↓ |

### 3.2 Producción (despliegue)
| Métrica | Definición | Dirección |
|---|---|---|
| **FPS** | Imágenes por segundo en inferencia | ↑ |
| **Latencia** | ms por imagen (pre + inferencia + post) | ↓ |
| **Parámetros / FLOPs** | Tamaño y costo computacional del modelo | ↓ |
| **Tamaño del modelo** | MB del archivo de pesos (.pt / .onnx / .tflite) | ↓ |
| **Robustez por escena** | mAP desglosada por condición (día / noche / humo) | ↑ |

### 3.3 Detectabilidad (sin etiquetas)
Permite una comparación rápida cuando no hay anotaciones (caso del TNO):
| Métrica | Definición | Dirección |
|---|---|---|
| **Nº de detecciones** | Detecciones totales/por imagen sobre umbral de confianza | ↑* |
| **Confianza media** | Confianza promedio de las detecciones | ↑ |
| **Tasa de detección de persona/vehículo** | % de imágenes con al menos una detección de la clase | ↑ |

\* En ausencia de *ground truth*, más detecciones no siempre es mejor (puede haber
falsos positivos); por eso se reporta junto a la confianza y se interpreta de forma
relativa entre métodos sobre el **mismo** detector e imágenes.

### 3.4 Confiabilidad estadística
Igual que en el resto de la tesis: **Friedman** global por métrica (métodos como
tratamientos, imágenes como bloques) y **Wilcoxon** pareado con **corrección de
Holm** y tamaño de efecto, para confirmar que las diferencias de detección entre
fusiones no son fruto del azar.

## 4. Protocolo experimental

1. **Dataset etiquetado** (Roboflow o M3FD): pares VIS/IR con cajas de personas y
   vehículos; división train/val/test fija (p. ej. 70/15/15) y semilla fija.
2. **Generación de versiones**: para cada par se produce VIS, IR y las fusiones
   (con el código de `src/fusion/`). Las cajas son idénticas en todas las versiones
   (las imágenes están registradas), de modo que la única variable es la fusión.
3. **Entrenamiento controlado**: mismo modelo base (yolov8n), mismas épocas, imgsz,
   batch y semilla para cada modalidad/fusión. Un entrenamiento por versión.
4. **Evaluación**: mAP/P/R/F1 sobre el split de test; producción (FPS, tamaño) sobre
   el modelo exportado; detectabilidad sobre el set sin etiquetas (TNO).
5. **Análisis estadístico**: Friedman + Wilcoxon (Holm) sobre las métricas por imagen.

## 5. Implementación entregada

- `notebooks/04_yolo_roboflow_deteccion.ipynb` — Colab (GPU): instala Ultralytics y
  Roboflow, descarga el dataset etiquetado, genera las versiones fusionadas, entrena
  un YOLO por modalidad, extrae mAP/P/R/F1 y curvas, mide producción (FPS, parámetros,
  ONNX, tamaño) y corre la comparación estadística.
- `notebooks/05_keras_clasificacion_downstream.ipynb` — Colab: tarea downstream de
  clasificación con Keras (MobileNetV2) sobre las versiones fusionadas; reporta
  accuracy/precision/recall/F1, matriz de confusión y curvas; exporta TFLite y mide
  latencia/tamaño.
- `experiments/detection/run_detection_eval.py` — evaluación local de detectabilidad;
  corre con YOLO (`--detector yolo`, requiere torch) o con el detector clásico
  HOG-SVM de OpenCV (`--detector hog`, offline, sin pesos).
- `experiments/detection/stats_detection.py` — Friedman + Wilcoxon sobre las métricas
  de detección.

## 6. Resultado referencial offline (detector clásico)

A modo de verificación del pipeline de extremo a extremo se ejecutó, dentro de este
entorno sin GPU, el detector clásico **HOG-SVM de personas** (Dalal & Triggs, 2005),
integrado en OpenCV y sin necesidad de pesos externos, sobre VIS, IR y las once
fusiones (20 imágenes cada una). Los resultados están en
`experiments/results/metrics_reports/detection_metrics.csv`.

**Advertencia de interpretación:** el detector HOG es un baseline clásico tunado para
peatones erguidos de buen contraste; sobre el TNO (personas pequeñas, térmicas, a
contraluz) produce pocas detecciones y de alta varianza. Por eso estos números deben
leerse como **prueba de funcionamiento del pipeline**, no como veredicto de utilidad.
La comparación definitiva (mAP/P/R/F1 con un detector profundo) se obtiene ejecutando
el notebook de YOLO/Roboflow en Colab con un dataset etiquetado.

## 7. Limitaciones del entorno

El entorno de cómputo de esta sesión no dispone de GPU y el índice de paquetes de
PyTorch está bloqueado, por lo que YOLO/Keras no se entrenan localmente. El diseño se
entrega como notebooks reproducibles para Google Colab (GPU gratuita) y el dataset
etiquetado se gestiona en Roboflow. El TNO no incluye anotaciones de detección; para
las métricas de entrenamiento (mAP/P/R/F1) se requiere un dataset etiquetado
(Roboflow propio o M3FD, que sí trae cajas).
