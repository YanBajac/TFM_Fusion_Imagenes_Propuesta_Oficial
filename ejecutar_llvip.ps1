# ============================================================
#  ejecutar_llvip.ps1
#  Pipeline LLVIP: prepara datasets fusionados por metodo (con labels
#  compartidas), entrena un YOLO por metodo y compara mAP.
#
#  USO (PowerShell):
#    powershell -ExecutionPolicy Bypass -File .\ejecutar_llvip.ps1 -LLVIP "D:\datasets\LLVIP"
#  Parametros opcionales:
#    -LimitTrain 2000  -LimitVal 500  -Epochs 40  -Device 0   (Device 0=GPU, cpu=CPU)
#  Descarga de LLVIP: https://github.com/bupt-ai-cz/LLVIP
# ============================================================
param(
  [string]$LLVIP = "",
  [int]$LimitTrain = 2000,
  [int]$LimitVal = 500,
  [int]$Epochs = 40,
  [string]$Device = "auto",
  [string]$Methods = "VIS,IR,PiramideLaplace,RatioPiramide,DWT,DTCWT,Curvelet,TopHat_Clasico,Propuesta_Novedosa"
)
Set-Location $PSScriptRoot
if ($LLVIP -eq "") { $LLVIP = Read-Host "Ruta a la carpeta LLVIP extraida (ej: D:\datasets\LLVIP)" }
if (-not (Test-Path $LLVIP)) { Write-Host "No existe la ruta: $LLVIP" -ForegroundColor Red; exit 1 }

# Entorno
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) { python -m venv .venv }
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip --quiet
python -c "import pandas,numpy,cv2,scipy,skimage" 2>$null
if ($LASTEXITCODE -ne 0) { python -m pip install -r requirements.txt }
python -c "import ultralytics" 2>$null
if ($LASTEXITCODE -ne 0) { python -m pip install ultralytics }

# Auto-detectar GPU/CPU si Device='auto'
if ($Device -eq "auto") {
  $cuda = (python -c "import torch;print('0' if torch.cuda.is_available() else 'cpu')").Trim()
  $Device = $cuda
  if ($Device -eq "cpu") {
    Write-Host "AVISO: no se detecto GPU (torch CPU). El entrenamiento en CPU es MUY lento;" -ForegroundColor Yellow
    Write-Host "       se recomienda Colab (GPU gratis). Continuo en CPU solo si insistis." -ForegroundColor Yellow
  } else { Write-Host "GPU detectada (device=0)." -ForegroundColor Green }
}

# 1) Preparar datasets fusionados (formato YOLO, labels compartidas)
Write-Host "`n=== Preparando datasets LLVIP fusionados ===" -ForegroundColor Cyan
python experiments\detection_llvip\prepare_llvip.py --llvip_root "$LLVIP" --out datasets `
    --methods $Methods --limit-train $LimitTrain --limit-val $LimitVal
if ($LASTEXITCODE -ne 0) { Write-Host "Fallo la preparacion." -ForegroundColor Red; exit 1 }

# 2) Entrenar y comparar mAP
Write-Host "`n=== Entrenando YOLO por metodo y comparando mAP ===" -ForegroundColor Cyan
python experiments\detection_llvip\train_eval_llvip.py --datasets-dir datasets `
    --methods $Methods --model yolov8n.pt --epochs $Epochs --imgsz 640 --device $Device

Write-Host "`nLISTO. Comparacion en: experiments\results\metrics_reports\detection_llvip_map.csv" -ForegroundColor Green
Write-Host "Pasame ese CSV y lo integro al analisis." -ForegroundColor Green
Read-Host "`nPresiona Enter para cerrar"
