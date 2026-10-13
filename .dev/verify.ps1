$ErrorActionPreference = "Stop"

& "$PSScriptRoot/verify-pyright.ps1"

& "$PSScriptRoot/verify-ruff.ps1"

& "$PSScriptRoot/test.ps1"

Write-Host ""
Write-Host "========================================"
Write-Host "Project verification completed." -ForegroundColor Green
Write-Host "========================================"