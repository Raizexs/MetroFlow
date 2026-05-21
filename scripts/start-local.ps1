# Arranque local: Postgres + API + instrucciones frontend
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

Write-Host "=== MetroFlow — arranque local ===" -ForegroundColor Cyan

Write-Host "[1/3] Docker: postgres + api..."
docker compose up -d --build
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "Esperando API (15s)..."
Start-Sleep -Seconds 15

Write-Host "[2/3] Verificando API..."
& "$PSScriptRoot\verify-rubric.ps1" -ApiUrl "http://localhost:8000"
if ($LASTEXITCODE -ne 0) {
    Write-Host "API aún no lista; espere y ejecute: .\scripts\verify-rubric.ps1" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== URLs locales ===" -ForegroundColor Green
Write-Host "  API:       http://localhost:8000"
Write-Host "  OpenAPI:   http://localhost:8000/docs"
Write-Host "  Dashboard: cd frontend; npm run dev  ->  http://localhost:5173"
Write-Host ""
Write-Host "Frontend (nueva terminal):" -ForegroundColor Cyan
Write-Host "  cd `"$Root\frontend`""
Write-Host "  npm install"
Write-Host "  npm run dev"
