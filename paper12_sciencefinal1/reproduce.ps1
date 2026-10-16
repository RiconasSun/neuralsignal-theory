param([string]$Run = 'paper12_sciencefinal1/results/final', [string]$Python = 'python')
$ErrorActionPreference = 'Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    & $Python -B -m unittest paper12_sciencefinal1.test_trusted_host paper12_singleowner1.test_engineering.ScientificTests
    if ($LASTEXITCODE -ne 0) { throw 'Synthetic numerical/transport regressions failed' }
    & $Python -B -m paper12_sciencefinal1.trusted_host reproduce --run $Run
    if ($LASTEXITCODE -ne 0) { throw 'Saved scientific reproduction failed' }
} finally { Pop-Location }
