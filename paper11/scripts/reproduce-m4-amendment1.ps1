$ErrorActionPreference = 'Stop'
Set-Location (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent)
$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
New-Item -ItemType Directory -Force 'paper11/results/M4_amendment1' | Out-Null
python paper11/scripts/run_m4_amendment1.py --register
if ($LASTEXITCODE -ne 0) { throw 'Amendment registration/integrity failed' }
$ErrorActionPreference = 'Continue'
cmd /d /c "python -u paper11/scripts/run_m4_amendment1.py 2>&1" | Tee-Object 'paper11/results/M4_amendment1/execution.log'
$runExit = $LASTEXITCODE
$ErrorActionPreference = 'Stop'
if ($runExit -ne 0) { throw 'Amended scientific gate FAIL; STOP, no downstream or holdout' }
Write-Output 'Amended M4 development gate passed; not a regime/holdout/null verdict.'
