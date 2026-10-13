. "$PSScriptRoot/common.ps1"

Invoke-Step "Pytest" {
    python -m pytest -q
}