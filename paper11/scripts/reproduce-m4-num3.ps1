$ErrorActionPreference = 'Stop'
$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
$root = Split-Path -Parent $PSScriptRoot
Push-Location (Split-Path -Parent $root)
try {
    python paper11/scripts/run_m4_num3.py --register
    if ($LASTEXITCODE -ne 0) { throw 'NUM3 registration mismatch; no testing permitted' }
    New-Item -ItemType Directory -Force -Path paper11/results/M4_amendment3 | Out-Null
    cmd /d /c "python paper11/scripts/run_m4_num3.py 2>&1" | Tee-Object paper11/results/M4_amendment3/execution.log
    $code = $LASTEXITCODE
    python paper11/scripts/report_m4_num3.py
    if ($LASTEXITCODE -ne 0) { throw 'NUM3 report, identity or regression validation failed' }
    if ($code -ne 0) { throw 'NUM3 mandatory numerical gate FAIL: STOP; M4 INCONCLUSIVE' }
    Write-Output 'Controlled gate PASS only. Frozen real M4 numerical checks remain mandatory before cohort/holdout claims.'
} finally { Pop-Location }
