# Reentrenamiento de detección con LLVIP (mAP concluyente)

Objetivo: comparar de forma **concluyente** qué método de fusión ayuda más a la
detección, entrenando el mismo detector (YOLOv8) sobre cada versión fusionada de un
dataset **VIS/IR alineado y etiquetado**. Se usa **LLVIP** (peatones, nocturno).

## 1. Descargar LLVIP
Repositorio oficial: https://github.com/bupt-ai-cz/LLVIP
Descomprimir de modo que quede:
```
LLVIP/
  visible/train/*.jpg   visible/test/*.jpg
  infrared/train/*.jpg  infrared/test/*.jpg
  Annotations/*.xml      (formato VOC, clase 'person')
```

## 2. Ejecutar (un comando)
```powershell
powershell -ExecutionPolicy Bypass -File .\ejecutar_llvip.ps1 -LLVIP "D:\datasets\LLVIP"
```
Opcionales: `-LimitTrain 2000 -LimitVal 500 -Epochs 40 -Device 0`
(`-Device 0` usa GPU; `-Device cpu` fuerza CPU. Empezá con un subconjunto para validar.)

## 3. Qué hace
1. `prepare_llvip.py`: por cada método (VIS, IR, Promedio, Laplace, Curvelet,
   TopHat disco L5, Óptimo Multiescala y **Propuesta Novedosa n=8,m=0.12**) genera
   `datasets/llvip_<metodo>/` en formato YOLO. **Las etiquetas son idénticas** para
   todos (solo cambian los píxeles fusionados) → la diferencia de mAP aísla el método.
2. `train_eval_llvip.py`: entrena el mismo `yolov8n.pt` con idéntica config/semilla
   por método y reporta **mAP@0.5** y **mAP@0.5:0.95** → `detection_llvip_map.csv`.

## 4. Protocolo justo
- Mismas particiones, misma config (épocas, imgsz, batch, seed), solo cambia la fusión.
- Para conclusión robusta: repetir con 2–3 semillas y promediar.
- VIS e IR (a un canal) sirven de referencia inferior/superior.

## Notas
- Requiere GPU para tiempos razonables (Colab también sirve con los mismos scripts).
- La fusión opera en escala de grises; las imágenes se guardan en gris (YOLO replica a 3 canales).
