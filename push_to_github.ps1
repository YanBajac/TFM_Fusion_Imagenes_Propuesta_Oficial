# push_to_github.ps1
# Script de un solo uso: limpia, stageia, commitea y pushea los cambios de la tesis.
# Ejecutar desde PowerShell parado en la raiz del repo:
#     cd C:\Users\Usuario\Documents\mastertesis\tesis_mciencias_datos
#     .\push_to_github.ps1
# Si Windows bloquea el script: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

$ErrorActionPreference = 'Stop'

Write-Host "==> Repositorio:" (Get-Location)

# 1) Quitar lock huerfano si existe
if (Test-Path .git\index.lock) {
    Write-Host "==> Quitando .git\index.lock huerfano..."
    Remove-Item .git\index.lock -Force
}

# 2) Stage selectivo (modificados + figuras + presentacion)
Write-Host "==> Stage de archivos..."

# Modificados ya trackeados (los toma git add -u sobre paths puntuales)
git add `
  .gitignore `
  README.md `
  requirements.txt `
  docs/Tesis_Borrador.docx `
  docs/reportes_finales/reporte_benchmark_multiescala.md `
  experiments/run_all_fusions.py `
  notebooks/01_EDA_dataset.ipynb `
  notebooks/02_fusion_tests.ipynb `
  notebooks/03_stats_analysis.ipynb `
  src/__init__.py `
  src/datasets.py `
  src/fusion/__init__.py `
  src/fusion/comparatives.py `
  src/fusion/prop_top_hat.py `
  src/metrics/__init__.py `
  src/metrics/evaluators.py `
  src/utils/__init__.py `
  src/utils/io.py `
  src/utils/visualization.py

# Nuevos a incluir
git add docs/figures/
git add docs/Tesis_Avance_Presentacion.pptx

# Excluir explicitamente backups y data sin tracking previo
# (data/raw.zip y Tesis_Borrador_BACKUP_eucaliptos.docx no se agregan)

Write-Host ""
Write-Host "==> Resumen del staging:"
git status -s

Write-Host ""
$confirmacion = Read-Host "Continuar con commit y push a origin/main? (s/N)"
if ($confirmacion -ne 's' -and $confirmacion -ne 'S') {
    Write-Host "Cancelado. Para deshacer el staging: git reset"
    exit 0
}

# 3) Commit
Write-Host "==> Creando commit..."
git commit -F .git_commit_msg.txt

# 4) Push
Write-Host "==> Pushing a origin/main..."
git push origin main

Write-Host ""
Write-Host "Listo. Verifica en https://github.com/YanBajac/tesis_mciencias_datos"
