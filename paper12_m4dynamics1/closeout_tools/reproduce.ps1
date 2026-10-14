param([string]$Python='')
$ErrorActionPreference='Stop'
if (-not $Python) { $Python=(Get-Command python -ErrorAction Stop).Source }
$env:PYTHONDONTWRITEBYTECODE='1'
& $Python -m unittest discover -s $PSScriptRoot -p test_audit_saved.py -v
if ($LASTEXITCODE -ne 0) { throw 'Saved audit regression failure' }
& $Python (Join-Path $PSScriptRoot 'audit_saved.py')
if ($LASTEXITCODE -ne 0) { throw 'Saved-only evidence audit failure' }
