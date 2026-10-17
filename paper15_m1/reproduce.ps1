param([string]$Python)
$ErrorActionPreference='Stop'
if (-not $Python) { $Python=Join-Path $PSScriptRoot 'work/runtime/Scripts/python.exe' }
if (-not (Test-Path -LiteralPath $Python)) { throw 'Provide -Python with Python3.11+ and pinned requirements.txt libraries. No data download is performed.' }
$Python=(Resolve-Path -LiteralPath $Python).Path
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    & $Python -m paper15_m1.saved_verify
    if ($LASTEXITCODE -ne 0) { throw "M1 saved-only specification verification failed: $LASTEXITCODE" }
} finally { Pop-Location }
