param([string]$Python='')
$ErrorActionPreference='Stop'
if (-not $Python) {$Python=(Get-Command python -ErrorAction Stop).Source}
$taskRoot=(Get-Item $PSScriptRoot).Parent.Parent.Parent.Parent.FullName
Push-Location $taskRoot
try {
    & ./paper12_singleowner1/reproduce.ps1 -Python $Python
    if ($LASTEXITCODE -ne 0) {throw 'Saved production evidence/statistics verification failed'}
    & $Python -B (Join-Path $PSScriptRoot 'verify_report.py')
    if ($LASTEXITCODE -ne 0) {throw 'Independent saved report semantic reproduction failed'}
    & $Python -B (Join-Path $PSScriptRoot 'verify_engineering.py')
    if ($LASTEXITCODE -ne 0) {throw 'Exact native security/production receipt roster check failed'}
    & $Python -B -c "import runpy,sys; runpy.run_path(sys.argv[1],run_name='__main__')" (Join-Path $PSScriptRoot 'verify_binding_receipts.py')
    if ($LASTEXITCODE -ne 0) {throw 'Public SYN signature/binding/durable-chain integrity failed'}
    & $Python -B (Join-Path $PSScriptRoot 'verify_failure_archive.py') --self-test
    if ($LASTEXITCODE -ne 0) {throw 'Historical failure archive and self-reference regression failed'}
} finally {Pop-Location}
