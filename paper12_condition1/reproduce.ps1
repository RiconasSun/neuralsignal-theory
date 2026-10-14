param([string]$Python='')
$ErrorActionPreference='Stop'
if (-not $Python) {$Python=(Get-Command python -ErrorAction Stop).Source}
$env:PYTHONDONTWRITEBYTECODE='1'
& $Python (Join-Path $PSScriptRoot 'reproduce_saved.py')
if ($LASTEXITCODE -ne 0) {throw "Bounded optimizer saved reproduction failed: $LASTEXITCODE"}
