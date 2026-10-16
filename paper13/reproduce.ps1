param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
& $Python (Join-Path $PSScriptRoot 'verify_saved.py')
if ($LASTEXITCODE -ne 0) { throw "Saved-only reproduction failed: $LASTEXITCODE" }
