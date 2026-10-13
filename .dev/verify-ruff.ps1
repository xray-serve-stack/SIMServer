. "$PSScriptRoot/common.ps1"

Invoke-Step "Ruff" {
    ruff check .
}