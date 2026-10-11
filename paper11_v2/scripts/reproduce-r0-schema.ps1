param([switch]$Acquire, [string]$Python = 'C:/Users/85993/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe')
$ErrorActionPreference = 'Stop'
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Push-Location $Root
try {
    & $Python paper11_v2/scripts/run_r0_schema.py register
    if ($LASTEXITCODE -ne 0) { throw 'R0 schema registration integrity failed' }
    & $Python -m unittest discover -s paper11_v2/tests -p 'test_r0*.py' -v
    if ($LASTEXITCODE -ne 0) { throw 'R0 regression tests failed' }
    if ($Acquire) {
        & $Python paper11_v2/scripts/run_r0_schema.py acquire
        if ($LASTEXITCODE -ne 0) { throw 'R0 metadata acquisition failed' }
    }
    & $Python paper11_v2/scripts/run_r0_schema.py evaluate
    if ($LASTEXITCODE -ne 0) { throw 'R0 scientific gate failed; do not advance' }
} finally { Pop-Location }
