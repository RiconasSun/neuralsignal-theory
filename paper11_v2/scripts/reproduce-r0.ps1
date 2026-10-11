param([switch]$Acquire, [string]$Python = 'C:/Users/85993/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe')
$ErrorActionPreference = 'Stop'
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
if (-not (Test-Path -LiteralPath $Python)) { throw 'Frozen Python interpreter missing; restore the recorded CPython environment.' }
Push-Location $Root
try {
    & $Python paper11_v2/scripts/run_r0.py register
    if ($LASTEXITCODE -ne 0) { throw 'Registration integrity failed' }
    & $Python -m unittest discover -s paper11_v2/tests -p 'test_r0.py' -v
    if ($LASTEXITCODE -ne 0) { throw 'R0 regression tests failed' }
    if ($Acquire) {
        & $Python paper11_v2/scripts/run_r0.py acquire
        if ($LASTEXITCODE -ne 0) { throw 'Public metadata acquisition failed' }
    }
    & $Python paper11_v2/scripts/run_r0.py evaluate
    if ($LASTEXITCODE -ne 0) { throw 'R0 scientific gate FAIL; do not proceed to R1' }
} finally { Pop-Location }
