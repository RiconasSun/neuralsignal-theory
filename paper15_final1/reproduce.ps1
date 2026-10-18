param([string]$Python = "")
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskRoot
$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
if (-not $Python) { $Python = Join-Path $taskRoot 'paper15_dev/work/runtime/Scripts/python.exe' }
if (-not (Test-Path -LiteralPath $Python)) { throw 'Pinned Python runtime missing. Supply -Python with the documented frozen requirements; no automatic download or real fit is performed.' }
& $Python -m paper15_final1.saved_verify
if ($LASTEXITCODE -ne 0) { throw "Saved-only verification failed with exit $LASTEXITCODE" }
