# Verificación C1 + C5 — API pública o local
param(
    [string]$ApiUrl = "http://localhost:8000"
)

$ErrorActionPreference = "Stop"
$base = $ApiUrl.TrimEnd("/")
$log = @()
$ok = $true

function Test-Step($name, $scriptBlock) {
    try {
        & $scriptBlock
        $script:log += "[OK] $name"
        Write-Host "[OK] $name" -ForegroundColor Green
    } catch {
        $script:log += "[FAIL] $name - $($_.Exception.Message)"
        Write-Host "[FAIL] $name - $($_.Exception.Message)" -ForegroundColor Red
        $script:ok = $false
    }
}

Write-Host "Verificando API: $base" -ForegroundColor Cyan

Test-Step "GET /api/v1/status" {
    $r = Invoke-RestMethod -Uri "$base/api/v1/status" -Method Get
    if ($r.status -ne "ok") { throw "status no es ok" }
}

Test-Step "GET /api/v1/occupation/vagon_1" {
    $r = Invoke-RestMethod -Uri "$base/api/v1/occupation/vagon_1" -Method Get
    if (-not $r.vagon_id) { throw "sin vagon_id" }
    $script:before = $r.headcount
}

Test-Step "POST /api/v1/analyze" {
    $body = @{
        zone_id = "vagon_1"
        headcount = 33
        status = "warning"
        timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    } | ConvertTo-Json
    $r = Invoke-RestMethod -Uri "$base/api/v1/analyze" -Method Post -ContentType "application/json" -Body $body
    if ($r.headcount -ne 33) { throw "headcount no actualizado" }
}

Test-Step "GET occupation tras POST" {
    $r = Invoke-RestMethod -Uri "$base/api/v1/occupation/vagon_1" -Method Get
    if ($r.headcount -ne 33) { throw "occupation no refleja POST" }
}

Test-Step "GET /api/v1/occupation/vagon_1/history" {
    $r = Invoke-RestMethod -Uri "$base/api/v1/occupation/vagon_1/history?limit=10" -Method Get
    if ($r.points.Count -lt 1) { throw "history vacío" }
}

Write-Host ""
if ($ok) {
    Write-Host "Todas las pruebas pasaron." -ForegroundColor Green
    exit 0
} else {
    Write-Host "Algunas pruebas fallaron." -ForegroundColor Red
    exit 1
}
