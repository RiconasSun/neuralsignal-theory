$ErrorActionPreference = 'Stop'
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location $root
$out = 'paper11/results/M3_M4_scope_audit'
New-Item -ItemType Directory -Force $out | Out-Null
$env:OPENBLAS_NUM_THREADS = '1'
$ErrorActionPreference = 'Continue'
$testOutput = @(cmd /d /c "python -m unittest discover -s paper11/tests -p test_report_audit.py -v 2>&1")
$testExit = $LASTEXITCODE
$testOutput | Out-File -Encoding utf8 "$out/tests.txt"
$testOutput
$ErrorActionPreference = 'Stop'
if ($testExit -ne 0) { throw 'Report tests failed; no report PASS' }
$ErrorActionPreference = 'Continue'
$runOutput = @(cmd /d /c "python paper11/scripts/report_m3_m4_audit.py 2>&1")
$runExit = $LASTEXITCODE
$runOutput | Out-File -Encoding utf8 "$out/execution.log"
$runOutput
$ErrorActionPreference = 'Stop'
if ($runExit -ne 0) { throw 'Report audit failed' }
Write-Output 'REPORT ONLY: M4 scientific gate remains FAIL; no new model fitting or holdout access.'
