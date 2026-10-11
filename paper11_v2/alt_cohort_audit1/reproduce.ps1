param([string]$Python = 'C:/Users/85993/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe')
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Provide -Python with a Python runtime containing requests; replay does not use the network.' }
& $Python -m unittest discover -s $PSScriptRoot -p 'test_*.py' -v
if ($LASTEXITCODE -ne 0) { throw 'Controlled regression tests failed' }
& $Python (Join-Path $PSScriptRoot 'verify_saved.py')
if ($LASTEXITCODE -ne 0) { throw 'Saved artifact verification failed' }
Write-Output 'Audit reproduced; INCONCLUSIVE remains INCONCLUSIVE, not scientific PASS.'
