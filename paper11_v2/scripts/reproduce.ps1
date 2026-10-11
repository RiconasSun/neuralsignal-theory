param([string]$Python = 'C:/Users/85993/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe')
$ErrorActionPreference = 'Stop'
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Push-Location $Root
try {
    & $Python paper11_v2/scripts/preflight_r0.py register
    if ($LASTEXITCODE -ne 0) { throw 'R0 final registration integrity failed' }
    & $Python paper11_v2/scripts/preflight_r0.py run
    $Code = $LASTEXITCODE
    if ($Code -eq 2) {
        Write-Output 'R0 DATA_INSUFFICIENT / WAIT_FOR_HUMAN_INPUT reproduced. R1-R3 and final holdouts remain locked.'
        exit 2
    }
    if ($Code -ne 0) { throw 'R0 reproduction failed unexpectedly' }
} finally { Pop-Location }
