param([string]$Python = 'C:/Users/85993/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe')
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Supply -Python with Python3.11, requests, numpy and h5py installed.' }
& $Python (Join-Path $PSScriptRoot 'reproduce.py')
if ($LASTEXITCODE -ne 0) { throw "Saved-metadata replay failed: $LASTEXITCODE" }
