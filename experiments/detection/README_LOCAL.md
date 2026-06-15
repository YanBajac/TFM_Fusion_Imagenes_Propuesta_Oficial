# Ejecutar la evaluación de detección en TU PC (local)

> Este entorno de Cowork no tiene GPU ni PyTorch, por eso YOLO/Keras no corren aquí.
> En tu PC (aunque sea CPU) **sí** funcionan. Seguí estos pasos y mandame el CSV que
> se genera para analizarlo juntos.

## 0) Preparación (una vez)

Abrí PowerShell en la carpeta del proyecto y creá el entorno:

```powershell
cd C:\Users\Usuario\Documents\unv\mastertesis\tesis_mciencias_datos
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install ultralytics opencv-python pandas matplotlib scipy scikit-image
```

La primera vez, Ultralytics descarga solo el modelo `yolov8n.pt` (~6 MB).

---

## OPCIÓN A — Comparación por inferencia (rápida, sin etiquetas, sin entrenar)

Corre un YOLO preentrenado sobre VIS, IR y las 11 fusiones y mide **detectabilidad**
(nº de detecciones, confianza, persona/vehículo) y **producción** (ms, FPS).

```powershell
python experiments\detection\run_detection_eval.py --detector yolo --weights yolov8n.pt
python experiments\detection\summarize_detection.py
python experiments\detection\stats_detection.py
```

Genera en `experiments\results\metrics_reports\`:
- `detection_metrics.csv`  (una fila por imagen)
- `detection_summary.csv`  (tabla por método)  ← **mandame este**
- `detection_comparison.png` (figura)
- `detection_friedman.csv`, `detection_wilcoxon.csv`

Tarda pocos minutos en CPU.

---

## OPCIÓN B — Entrenamiento real con auto-etiquetado (mAP / P / R / F1)

Genera pseudo-etiquetas con un YOLO preentrenado, entrena un YOLO por modalidad
(VIS, IR, Fusión Top-Hat, Fusión Laplace) y reporta **mAP@0.5, mAP@0.5:0.95,
Precision, Recall, F1** + curvas de pérdida.

```powershell
python experiments\detection\train_local_pseudolabels.py --epochs 30 --device cpu
```

- En CPU puede tardar (probá primero `--epochs 10` para una corrida rápida).
- Si tenés GPU NVIDIA: instalá la rueda CUDA de torch y usá `--device 0` (mucho más rápido).

Genera:
- `experiments\results\metrics_reports\detection_training_metrics.csv`  ← **mandame este**
- Curvas y resultados por modalidad en `experiments\results\detection_train\runs\`

**Nota:** la Opción B usa pseudo-etiquetas (lo que el modelo ve en VIS), por lo que
la comparación es **relativa entre modalidades**. Para un mAP absoluto publicable,
anotá un dataset en Roboflow (o usá M3FD) y usá el `notebooks/04_yolo_roboflow_deteccion.ipynb`.

---

## Qué mandarme para analizar

Pegame o subí al repo el/los CSV (`detection_summary.csv` y/o
`detection_training_metrics.csv`). Con eso hago el análisis estadístico, la tabla y
las figuras, y lo integro a la tesis.
