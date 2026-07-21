# ============================================================
#  ejecutar_m3fd.ps1
#  Experimento de deteccion con clases complementarias (M3FD):
#  UN modelo entrenado con VIS+IR mezcladas; inferencia sobre la
#  validacion de cada modalidad y de cada metodo de fusion
#  (incluye el PSO de la tesis y el PSO del libro FPUNA).
#
#  USO (PowerShell, desde la carpeta del repo):
#    powershell -ExecutionPolicy Bypass -File .\ejecutar_m3fd.ps1 -M3FD "data\M3FD"
#  Parametros opcionales:
#    -TrainN 2000  -ValN 500  -Epochs 40  -Device 0   (Device 0=GPU, cpu=CPU)
#  Descarga de M3FD (Detection): https://github.com/JinyuanLiu-CV/TarDAL
# ============================================================
param(
  [string]$M3FD = "",
  [int]$TrainN = 2000,
  [int]$ValN = 500,
  [int]$Epochs = 40,
  [string]$Device = "auto"
)
Set-Location $PSScriptRoot
if ($M3FD -eq "") { $M3FD = Read-Host "Ruta a la carpeta M3FD extraida (ej: data\M3FD)" }
if (-not (Test-Path $M3FD)) { Write-Host "No existe la ruta: $M3FD" -ForegroundColor Red; exit 1 }

# Entorno
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) { python -m venv .venv }
. .\.venv\Scripts\Activate.ps1
python -c "import pandas,numpy,cv2,scipy,skimage" 2>$null
if ($LASTEXITCODE -ne 0) { python -m pip install -r requirements.txt }
python -c "import ultralytics" 2>$null
if ($LASTEXITCODE -ne 0) { python -m pip install ultralytics }

# Auto-detectar GPU/CPU
if ($Device -eq "auto") {
  $cuda = (python -c "import torch;print('0' if torch.cuda.is_available() else 'cpu')").Trim()
  $Device = $cuda
  if ($Device -eq "cpu") {
    Write-Host "AVISO: sin GPU el entrenamiento es MUY lento." -ForegroundColor Yellow
  } else { Write-Host "GPU detectada (device=0)." -ForegroundColor Green }
}

# 1) Preparar mixto + sets de prueba fusionados
Write-Host "`n=== Preparando M3FD (mixto VIS+IR + sets fusionados) ===" -ForegroundColor Cyan
python experiments\detection_m3fd\prepare_m3fd.py --m3fd_root "$M3FD" --out datasets `
    --train-n $TrainN --val-n $ValN
if ($LASTEXITCODE -ne 0) { Write-Host "Fallo la preparacion." -ForegroundColor Red; exit 1 }

# 2) Entrenar modelo unico + inferencia por metodo
Write-Host "`n=== Entrenando modelo unico e infiriendo por metodo ===" -ForegroundColor Cyan
python experiments\detection_m3fd\train_eval_m3fd.py --datasets-dir datasets `
    --model yolov8n.pt --epochs $Epochs --imgsz 640 --device $Device

Write-Host "`nLISTO. Resultados en: experiments\results\metrics_reports\detection_m3fd_map.csv" -ForegroundColor Green
Read-Host "`nPresiona Enter para cerrar"
