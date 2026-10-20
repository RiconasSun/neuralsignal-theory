param([string]$Python=(Join-Path $PSScriptRoot '..\paper16_m1\work\runtime\Scripts\python.exe'))
$ErrorActionPreference='Stop'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Pinned private Python 3.11.15 environment required. No source/download or substitute-data fallback.' }
$env:PYTHONDONTWRITEBYTECODE='1'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    Write-Output ('PowerShell '+$PSVersionTable.PSVersion.ToString()+'; saved STOP verification only, no scientific re-execution')
    & $Python -B -m paper16_development_r1.verify_saved
    if ($LASTEXITCODE -ne 0) { throw "Saved STOP reproduction failed: $LASTEXITCODE" }
} finally { Pop-Location }
