# Experimentos aplicativos de detección (YOLO · RF-DETR · Keras)

Evalúan el **efecto de la fusión** en tareas posteriores, comparando **4 modalidades de
entrada** sobre **3 modelos**. Como este entorno no tiene GPU, se ejecutan en tu PC/Colab.

## Modalidades de entrada (la variable del experimento)
1. **VIS** — solo visible.
2. **IR** — solo infrarrojo.
3. **Anterior** — Torre Top-Hat (método anterior, `TopHatFusion('disk',5)`).
4. **Óptimo Multiescala** — propuesta central (`OptimalMultiscaleFusion(n=6, base_radius=2.89, m=0.10)`).

> Las imágenes están registradas, por lo que las **etiquetas son idénticas** para las 4 modalidades.
> Las fusiones ya están generadas en `experiments/results/fused_images/` (Optimo_Multiescala, TopHat_disk_L5, …).

## Modelos
| Modelo | Notebook | Métricas |
|---|---|---|
| **YOLO** (Ultralytics, 1 etapa) | `notebooks/04_yolo_roboflow_deteccion.ipynb` | mAP@0.5, mAP@0.5:0.95, P, R, F1, FPS |
| **RF-DETR** (transformer, Roboflow) | `notebooks/06_rfdetr_deteccion.ipynb` | mAP@0.5, mAP@0.5:0.95, P, R, F1, latencia |
| **Keras** (clasificación, MobileNetV2) | `notebooks/05_keras_clasificacion_downstream.ipynb` | accuracy, P, R, F1, TFLite |

## Pasos
1. Subí un dataset etiquetado VIS/IR a **Roboflow** (clases p. ej. `person`, `car`) o usá **M3FD**.
2. Abrí cada notebook en **Colab con GPU**, pegá tu API key y corré: genera las 4 modalidades
   (aplicando la fusión y conservando las etiquetas), entrena un modelo por modalidad y guarda el CSV.
3. Mandame `yolo_por_modalidad.csv`, `rfdetr_por_modalidad.csv` y el de Keras: hago la estadística
   (Friedman/Wilcoxon), las figuras y la sección de resultados (Parte B) de la tesis.

## Demo offline (referencial, ya corrida acá)
`python experiments/detection/demo_offline_modalidades.py` → detectabilidad con el detector clásico
HOG (sin GPU) sobre las modalidades, en `detection_demo_modalidades.csv`. Es solo una verificación
del pipeline; la comparación concluyente sale de YOLO/RF-DETR en GPU.

## Inferencia rápida con YOLO (sin entrenar, sin etiquetas)
`python experiments/detection/run_detection_eval.py --detector yolo` (requiere ultralytics/torch en tu PC)
corre un YOLO preentrenado sobre todas las modalidades, incluida `Optimo_Multiescala`, y reporta
detectabilidad + FPS.
