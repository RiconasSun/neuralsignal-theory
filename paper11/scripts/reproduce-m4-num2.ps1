$ErrorActionPreference = 'Stop'
Set-Location (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent)
$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
New-Item -ItemType Directory -Force 'paper11/results/M4_amendment2' | Out-Null
$ErrorActionPreference = 'Continue'
cmd /d /c "python -u paper11/scripts/oracle_m4_num2.py 2>&1" | Tee-Object 'paper11/results/M4_amendment2/execution.log'
$oracleExit = $LASTEXITCODE
$ErrorActionPreference = 'Stop'
python paper11/scripts/report_m4_num2.py
if ($LASTEXITCODE -ne 0) { throw 'NUM2 audit report failed' }
if ($oracleExit -ne 0) { throw 'NUM2 mandatory oracle gate FAIL: STOP, no real evaluation or full cohort' }
throw 'Stopped proposal package has no activated real-evaluation registration; no silent full-cohort execution'
