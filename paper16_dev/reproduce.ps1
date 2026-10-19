param([string]$Python = (Join-Path $PSScriptRoot '..\paper16_m1\work\runtime\Scripts\python.exe'))
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Supply -Python for the pinned Python3.11.15 environment; no live data fallback.' }
$env:PYTHONDONTWRITEBYTECODE='1'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    & $Python -m paper16_dev.verify_saved
    if ($LASTEXITCODE -ne 0) { throw "Saved stop reproduction failed: $LASTEXITCODE" }
} finally { Pop-Location }
