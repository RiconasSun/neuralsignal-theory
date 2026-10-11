param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
$env:OPENBLAS_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Push-Location $root
try {
    New-Item -ItemType Directory -Force paper11/results/M3 | Out-Null
    & $Python paper11/scripts/run_m3.py 2>&1 | Tee-Object paper11/results/M3/execution.log
    if ($LASTEXITCODE -ne 0) { throw 'M3 failed; do not advance.' }
} finally { Pop-Location }
