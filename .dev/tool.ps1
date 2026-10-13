param(
    [Parameter(Mandatory)]
    [ValidateSet(
        "verify",
        "verify-pyright",
        "verify-ruff",
        "test",
        "fix",
        "format",
        "env"
    )]
    [string]$Action
)

switch ($Action) {

    "verify" {
        & "$PSScriptRoot/verify.ps1"
    }

    "verify-pyright" {
        & "$PSScriptRoot/verify-pyright.ps1"
    }

    "verify-ruff" {
        & "$PSScriptRoot/verify-ruff.ps1"
    }

    "test" {
        & "$PSScriptRoot/test.ps1"
    }

    "fix" {
        & "$PSScriptRoot/fix.ps1"
    }

    "format" {
        & "$PSScriptRoot/format.ps1"
    }

    "env" {
        & "$PSScriptRoot/env.ps1"
    }

}