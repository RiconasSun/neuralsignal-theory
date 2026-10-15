param([string]$Python='')
$ErrorActionPreference='Stop'
if (-not $Python) {$Python=(Get-Command python -ErrorAction Stop).Source}
$env:PYTHONDONTWRITEBYTECODE='1'
& $Python (Join-Path $PSScriptRoot 'reproduce.py')
if ($LASTEXITCODE -ne 0) {throw "Final prerelease audit reproduction failed: $LASTEXITCODE"}
