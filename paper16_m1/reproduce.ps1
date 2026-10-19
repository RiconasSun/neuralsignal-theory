param([string]$Python = (Join-Path $PSScriptRoot 'work\runtime\Scripts\python.exe'))
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Supply -Python pointing to Python3.11.15 with the pinned requirements installed.' }
$env:PYTHONDONTWRITEBYTECODE='1'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    & $Python -m paper16_m1.code.verify
    if ($LASTEXITCODE -ne 0) { throw "Saved-only specification verification failed: $LASTEXITCODE" }
} finally { Pop-Location }
