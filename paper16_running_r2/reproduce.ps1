param([string]$Python=(Join-Path $PSScriptRoot '..\paper16_m1\work\runtime\Scripts\python.exe'))
$ErrorActionPreference='Stop'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Supply the pinned Python3.11.15 environment; no download or live source fallback.' }
$env:PYTHONDONTWRITEBYTECODE='1'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    Write-Output ("PowerShell "+$PSVersionTable.PSVersion.ToString()+"; saved-running-only reproduction")
    & $Python -B -m paper16_running_r2.verify_saved
    if ($LASTEXITCODE -ne 0) { throw "Saved R2 reproduction failed: $LASTEXITCODE" }
} finally { Pop-Location }
