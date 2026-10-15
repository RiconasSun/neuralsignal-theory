param([string]$Python='', [switch]$PublicOnly)
$ErrorActionPreference='Stop'
if (-not $Python) {$Python=(Get-Command python -ErrorAction Stop).Source}
$taskRoot=Split-Path $PSScriptRoot -Parent
Push-Location $taskRoot
try {
    if ($PublicOnly) { & $Python -B -m paper12_cseal1.reproduce_saved --public-only }
    else { & $Python -B -m paper12_cseal1.reproduce_saved }
    if ($LASTEXITCODE -ne 0) {throw "Saved-only C seal verification failed: $LASTEXITCODE"}
} finally {Pop-Location}
