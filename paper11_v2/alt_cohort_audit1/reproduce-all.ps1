param([string]$Python = 'C:/Users/85993/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe')
$ErrorActionPreference = 'Stop'
& $Python -m unittest discover -s $PSScriptRoot -p 'test_*.py' -v
if ($LASTEXITCODE -ne 0) { throw 'Controlled tests failed' }
& $Python (Join-Path $PSScriptRoot 'verify_all.py')
if ($LASTEXITCODE -ne 0) { throw 'Complete saved audit verification failed' }
Write-Output 'Faithful metadata audit reproduction; both candidate gates remain INCONCLUSIVE.'
