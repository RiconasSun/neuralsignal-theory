param([string]$Python = 'C:/Users/85993/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe')
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Supply -Python: Python3.11, numpy, h5py, requests.' }
$evidence = Join-Path $PSScriptRoot 'evidence'
New-Item -ItemType Directory -Path $evidence -Force | Out-Null
& $Python (Join-Path $PSScriptRoot 'reproduce.py') 2>&1 | Tee-Object -FilePath (Join-Path $evidence 'powershell.log')
if ($LASTEXITCODE -ne 0) { throw "Saved-only replay failed: $LASTEXITCODE" }
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'replay/reproduction_result.json') -Destination (Join-Path $evidence 'reproduction_result.json')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'replay/tests.log') -Destination (Join-Path $evidence 'tests.log')
