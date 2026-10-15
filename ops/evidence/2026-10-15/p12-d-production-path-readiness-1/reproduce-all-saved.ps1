param([string]$Python='')
$ErrorActionPreference='Stop'
if (-not $Python) {$Python=(Get-Command python -ErrorAction Stop).Source}
$taskRoot=(Get-Item $PSScriptRoot).Parent.Parent.Parent.Parent.FullName
Push-Location $taskRoot
try {
    & ./paper12_production1/reproduce.ps1 -Python $Python
    if ($LASTEXITCODE -ne 0) {throw 'Saved production evidence/statistics verification failed'}
    & $Python -B (Join-Path $PSScriptRoot 'verify_report.py')
    if ($LASTEXITCODE -ne 0) {throw 'Independent saved report semantic reproduction failed'}
    & $Python -B (Join-Path $PSScriptRoot 'verify_engineering.py')
    if ($LASTEXITCODE -ne 0) {throw 'Exact native security/production receipt roster check failed'}
    & $Python -B (Join-Path $PSScriptRoot 'verify_binding_receipts.py')
    if ($LASTEXITCODE -ne 0) {throw 'Public SYN signature/binding/durable-chain integrity failed'}
} finally {Pop-Location}
