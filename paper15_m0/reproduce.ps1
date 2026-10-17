param([string]$Python)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $PSScriptRoot 'work/runtime/Scripts/python.exe' }
if (-not (Test-Path -LiteralPath $Python)) {
    throw 'Provide -Python with Python 3.11+ and numpy, pandas, scipy installed. This saved-only command never downloads data.'
}
Push-Location $root
try {
    & $Python -m paper15_m0.saved_verify
    if ($LASTEXITCODE -ne 0) { throw "Saved reproduction failed: $LASTEXITCODE" }
} finally { Pop-Location }
