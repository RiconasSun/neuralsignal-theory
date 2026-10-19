param([string]$Python=(Join-Path $PSScriptRoot '..\paper16_m1\work\runtime\Scripts\python.exe'))
$ErrorActionPreference='Stop'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Supply pinned Python3.11.15 runtime; no source/download fallback.' }
$env:PYTHONDONTWRITEBYTECODE='1'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    Write-Output ('PowerShell '+$PSVersionTable.PSVersion.ToString()+'; saved M2 prefix replay, not scientific acceptance')
    & $Python -B -m paper16_dev_r3.saved_m2
    if ($LASTEXITCODE -ne 0) { throw "Saved R3 replay failed: $LASTEXITCODE" }
} finally { Pop-Location }
