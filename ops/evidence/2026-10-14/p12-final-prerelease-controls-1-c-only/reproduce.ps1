param([string]$Python='')
$ErrorActionPreference='Stop'
if (-not $Python) {$Python=(Get-Command python -ErrorAction Stop).Source}
$env:PYTHONDONTWRITEBYTECODE='1'
$target=Join-Path $PSScriptRoot 'reproduce_saved.py'
& $Python $target
if ($LASTEXITCODE -ne 0) {throw "C-only saved-evidence reproduction failed: $LASTEXITCODE"}
