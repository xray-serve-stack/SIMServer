function Invoke-Step {
    param(
        [string]$Title,
        [scriptblock]$Command
    )

    Write-Host ""
    Write-Host "========================================"
    Write-Host $Title -ForegroundColor Cyan
    Write-Host "========================================"

    & $Command

    if ($LASTEXITCODE -ne 0) {
        throw "$Title failed."
    }
}