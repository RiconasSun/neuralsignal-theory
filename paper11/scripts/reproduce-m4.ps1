param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
$env:OPENBLAS_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Push-Location $root
try {
    New-Item -ItemType Directory -Force paper11/results/M4 | Out-Null
    $ErrorActionPreference = 'Continue'
    & $Python paper11/scripts/run_m4.py 2>&1 | ForEach-Object { $_.ToString() } | Tee-Object paper11/results/M4/execution.log
    $analysisExit = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    if ($analysisExit -ne 0) { throw 'M4 critical gate failed; stop, no M5 or final test.' }
} finally { Pop-Location }
