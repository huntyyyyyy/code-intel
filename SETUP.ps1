# Requires: uv (https://docs.astral.sh/uv/) and JDK 17, not 25.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv not on PATH. Install uv, then re-run."
    exit 1
}

uv sync --extra dev

$env:CODE_INTEL_ROOT = "C:\Users\16145\Downloads\ocs-api-service-develop\ocs-api-service-develop"
$env:JAVA_HOME = "C:\Users\16145\scoop\apps\temurin17-jdk\current"

if (-not (Test-Path $env:CODE_INTEL_ROOT)) {
    Write-Host "Plant missing: $env:CODE_INTEL_ROOT"
    exit 1
}

uv run pytest
uv run python -m code_intel lookup HomeController
