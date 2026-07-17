# push_to_github.ps1
# Commitea y pushea los cambios de la tesis a origin/main.
# USO (PowerShell, parado en cualquier lado):
#     powershell -ExecutionPolicy Bypass -File .\push_to_github.ps1
# (o:  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass ; .\push_to_github.ps1 )

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
Write-Host "==> Repositorio:" (Get-Location) -ForegroundColor Cyan

# 1) Quitar lock huerfano si quedo alguno
if (Test-Path .git\index.lock) {
    Write-Host "==> Quitando .git\index.lock huerfano..." -ForegroundColor Yellow
    Remove-Item .git\index.lock -Force
}

# 2) Reconstruir el indice desde HEAD (corrige cualquier estado raro del index)
Write-Host "==> Reconstruyendo el indice (git reset)..." -ForegroundColor Cyan
git reset -q

# 3) Stage de todo lo modificado/nuevo. El dataset LLVIP y datasets/ estan en .gitignore.
Write-Host "==> git add -A ..." -ForegroundColor Cyan
git add -A

# 4) Control de seguridad: si se estan por subir demasiados archivos, probablemente
#    se cuela un dataset; abortar para revisar el .gitignore.
$staged = @(git diff --cached --name-only)
$n = $staged.Count
Write-Host ("==> Archivos en el stage: {0}" -f $n) -ForegroundColor Cyan
if ($n -gt 500) {
    Write-Host "ATENCION: hay mas de 500 archivos en el stage." -ForegroundColor Red
    Write-Host "Probablemente se este colando un dataset. Revisa .gitignore y:" -ForegroundColor Red
    Write-Host "    git reset" -ForegroundColor Red
    Write-Host "Primeras lineas del stage:" -ForegroundColor Yellow
    $staged | Select-Object -First 30 | ForEach-Object { Write-Host "   $_" }
    exit 1
}

Write-Host ""
Write-Host "==> Resumen del staging:" -ForegroundColor Cyan
git status -s

Write-Host ""
$resp = Read-Host "Continuar con commit y push a origin/main? (s/N)"
if ($resp -ne 's' -and $resp -ne 'S') {
    Write-Host "Cancelado. Para deshacer el staging:  git reset" -ForegroundColor Yellow
    exit 0
}

# 5) Commit (mensaje en .git_commit_msg.txt)
Write-Host "==> Creando commit..." -ForegroundColor Cyan
if (Test-Path .git_commit_msg.txt) {
    git commit -F .git_commit_msg.txt
} else {
    git commit -m "Libro: formato/diseno Villalba + marco teorico ampliado (26 ecuaciones, indice, Figura 5 PSO)"
}

# 6) Push
Write-Host "==> Pushing a origin/main..." -ForegroundColor Cyan
git push origin main

Write-Host ""
Write-Host "Listo. Verifica en https://github.com/YanBajac/TFM_Fusion_Imagenes_Propuesta_Oficial" -ForegroundColor Green
Read-Host "Enter para cerrar"
