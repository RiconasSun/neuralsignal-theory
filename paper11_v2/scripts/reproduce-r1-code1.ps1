param([string]$Python = 'C:/Users/85993/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe')
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Push-Location $Root
try {
    & $Python paper11_v2/scripts/run_r1_code1.py verify
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $Python -m unittest discover -s paper11_v2/tests -p 'test_r1_code1.py' -v
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $Python paper11_v2/scripts/run_r1_code1.py replay
    exit $LASTEXITCODE
} finally { Pop-Location }
