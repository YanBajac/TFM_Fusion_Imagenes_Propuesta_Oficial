# ============================================================
#  ejecutar_deteccion.ps1
#  Corre la evaluacion de detectabilidad (YOLO + RF-DETR) sobre
#  VIS, IR y los metodos de fusion, incluyendo la Propuesta Novedosa.
#  USO: clic derecho -> "Ejecutar con PowerShell"  (o desde una terminal:
#       powershell -ExecutionPolicy Bypass -File .\ejecutar_deteccion.ps1)
# ============================================================

# 1. Ubicarse en la carpeta del proyecto (donde esta este script)
Set-Location $PSScriptRoot
Write-Host "Proyecto: $PSScriptRoot" -ForegroundColor Cyan

# 2. Activar el entorno virtual si existe; si no, crearlo
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "Activando .venv existente..." -ForegroundColor Green
    . .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "No hay .venv; creando uno nuevo (puede tardar)..." -ForegroundColor Yellow
    python -m venv .venv
    . .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    if (Test-Path ".\requirements.txt") { python -m pip install -r requirements.txt }
}

# 3. Instalar dependencias de los detectores si faltan
Write-Host "Verificando ultralytics (YOLO)..." -ForegroundColor Cyan
python -m pip install --quiet ultralytics

# 4. Correr YOLO (genera detection_novel_yolo.csv)
Write-Host "`n=== YOLO ===" -ForegroundColor Cyan
python experiments\detection\run_detection_novel.py --detector yolo --weights yolov8n.pt

# 5. (Opcional) RF-DETR -- descomentar si lo queres correr
# Write-Host "`n=== RF-DETR ===" -ForegroundColor Cyan
# python -m pip install --quiet "rfdetr"
# python experiments\detection\run_detection_novel.py --detector rfdetr

Write-Host "`nLISTO. Resultados en: experiments\results\metrics_reports\detection_novel_yolo.csv" -ForegroundColor Green
Write-Host "Pasame ese CSV y lo integro a la tabla de metricas." -ForegroundColor Green
Read-Host "`nPresiona Enter para cerrar"
