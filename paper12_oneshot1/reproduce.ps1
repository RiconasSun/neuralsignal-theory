param([string]$Python='')
$ErrorActionPreference='Stop'
if (-not $Python) {$Python=(Get-Command python -ErrorAction Stop).Source}
$taskRoot=Split-Path $PSScriptRoot -Parent
Push-Location $taskRoot
try {
    & $Python -B -m unittest paper12_oneshot1.test_audit
    if ($LASTEXITCODE -ne 0) {throw "Public audit regressions failed: $LASTEXITCODE"}
    & $Python -B -m paper12_oneshot1.reproduce_saved
    if ($LASTEXITCODE -ne 0) {throw "Saved stopped-audit reproduction failed: $LASTEXITCODE"}
} finally {Pop-Location}
