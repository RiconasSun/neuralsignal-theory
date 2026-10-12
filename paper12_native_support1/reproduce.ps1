param([string]$Python = 'C:/Users/85993/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe', [switch]$FullDigitalTiming)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Supply -Python with Python3.11, requests, h5py, numpy and scipy.' }
$arguments = @((Join-Path $PSScriptRoot 'reproduce.py'))
if ($FullDigitalTiming) { $arguments += '--full-digital-timing' }
& $Python @arguments
if ($LASTEXITCODE -ne 0) { throw "Audit reproduction failed: $LASTEXITCODE" }
