param([switch]$FreshQC, [string]$Python = 'C:/Users/85993/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe')
$ErrorActionPreference = 'Stop'
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Push-Location $Root
try {
    & $Python paper11_v2/scripts/run_r0_amend1.py verify
    if ($LASTEXITCODE -ne 0) { throw 'R0 amendment input or holdout/failure integrity mismatch' }
    $Action = if ($FreshQC) { 'run' } else { 'replay' }
    & $Python paper11_v2/scripts/run_r0_amend1.py $Action
    $Code = $LASTEXITCODE
    if ($Code -ne 0) { exit $Code }
} finally { Pop-Location }
