param([switch]$FreshQC, [string]$Python = 'C:/Users/85993/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe')
$ErrorActionPreference = 'Stop'
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Push-Location $Root
try {
    & $Python paper11_v2/scripts/run_r0_amend1_repair.py verify
    if ($LASTEXITCODE -ne 0) { throw 'Registered audit repair integrity failed' }
    & $Python -m unittest discover -s paper11_v2/tests -p 'test_r0_amend1_repair.py' -v
    if ($LASTEXITCODE -ne 0) { throw 'Audit repair regression failed' }
    $Action = if ($FreshQC) { 'run' } else { 'replay' }
    & $Python paper11_v2/scripts/run_r0_amend1_repair.py $Action
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally { Pop-Location }
