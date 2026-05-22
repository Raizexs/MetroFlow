# Demo: edge ingestor (video EFE) -> API -> dashboard
param(
    [string]$ApiUrl = "http://localhost:8000",
    [int]$MaxFrames = 0
)

$Root = Split-Path $PSScriptRoot -Parent
$AiDir = Join-Path $Root "ai"

Write-Host "=== Demo integrada (video -> API -> dashboard) ===" -ForegroundColor Cyan
& "$PSScriptRoot\verify-rubric.ps1" -ApiUrl $ApiUrl
if ($LASTEXITCODE -ne 0) {
    Write-Host "API no disponible en $ApiUrl" -ForegroundColor Red
    exit 1
}

Set-Location $AiDir
$venvPython = Join-Path $AiDir ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Cree venv en ai/: py -3.14 -m venv .venv; pip install -r requirements.txt" -ForegroundColor Red
    exit 1
}

$args = @(
    "edge_ingestor.py",
    "--preset", "efe",
    "--api", $ApiUrl,
    "--push-interval", "6"
)
if ($MaxFrames -gt 0) {
    $args += @("--max-frames", "$MaxFrames")
}

Write-Host "Ingestor: demo EFE aleatorio (20-40s detencion, POST cada 6s). --live = YOLO real."
Write-Host "Abra el dashboard y espere ~6 s entre cada cambio visible."
& $venvPython @args

Write-Host ""
Write-Host "Dashboard:" -ForegroundColor Green
Write-Host "  Local:  http://localhost:5173"
Write-Host "  Cloud:  su URL de Vercel (VITE_API_URL = API Render)"
