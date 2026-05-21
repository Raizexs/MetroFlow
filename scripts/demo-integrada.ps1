# Demo: edge ingestor -> API -> (dashboard polling)
param(
    [string]$ApiUrl = "http://localhost:8000",
    [int]$MaxFrames = 30
)

$Root = Split-Path $PSScriptRoot -Parent
$AiDir = Join-Path $Root "ai"

Write-Host "=== Demo integrada ===" -ForegroundColor Cyan
& "$PSScriptRoot\verify-rubric.ps1" -ApiUrl $ApiUrl
if ($LASTEXITCODE -ne 0) {
    Write-Host "API no disponible en $ApiUrl" -ForegroundColor Red
    exit 1
}

Set-Location $AiDir
$venvPython = Join-Path $AiDir ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Cree venv en ai/: python -m venv .venv; pip install -r requirements.txt" -ForegroundColor Red
    exit 1
}

Write-Host "Ejecutando edge_ingestor ($MaxFrames frames)..."
& $venvPython edge_ingestor.py --api $ApiUrl --max-frames $MaxFrames --stride 15

Write-Host ""
Write-Host "Abra el dashboard y espere ~5 s para ver el conteo actualizado." -ForegroundColor Green
Write-Host "  Local:    http://localhost:5173"
Write-Host "  Cloud:    su URL de Vercel"
