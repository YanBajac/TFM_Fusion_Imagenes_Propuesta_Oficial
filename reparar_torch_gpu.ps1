# ============================================================
#  reparar_torch_gpu.ps1
#  Reemplaza el PyTorch CPU-only por la build con CUDA (GPU).
#  USO:  powershell -ExecutionPolicy Bypass -File .\reparar_torch_gpu.ps1
#        (opcional) -Cuda cu118   |   -Cuda cu121 (default)   |   -Cuda cu124
# ============================================================
param([string]$Cuda = "cu121")
Set-Location $PSScriptRoot
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) { Write-Host "No hay .venv" -ForegroundColor Red; exit 1 }
. .\.venv\Scripts\Activate.ps1

Write-Host "=== GPU detectada por el driver (nvidia-smi) ===" -ForegroundColor Cyan
nvidia-smi
Write-Host ""
Write-Host "Reinstalando PyTorch con CUDA ($Cuda)... (descarga grande, paciencia)" -ForegroundColor Cyan
python -m pip uninstall -y torch torchvision
python -m pip install torch torchvision --index-url "https://download.pytorch.org/whl/$Cuda"

Write-Host "`n=== Verificacion ===" -ForegroundColor Cyan
python -c "import torch; print('torch', torch.__version__); print('CUDA disponible:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NINGUNA')"
Write-Host "`nSi 'CUDA disponible: True' -> listo, corre ejecutar_llvip.ps1." -ForegroundColor Green
Write-Host "Si sigue False -> tu driver puede ser viejo: reintenta con -Cuda cu118" -ForegroundColor Yellow
Read-Host "`nEnter para cerrar"
