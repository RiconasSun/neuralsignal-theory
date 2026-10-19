param([string]$Python = (Join-Path $PSScriptRoot '..\paper16_m1\work\runtime\Scripts\python.exe'))
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Supply -Python in the pinned runtime; no download or live-source fallback.' }
$env:PYTHONDONTWRITEBYTECODE='1'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    Write-Output ("PowerShell " + $PSVersionTable.PSVersion.ToString() + "; saved-only reproduction")
    & $Python -B -m paper16_linkdiag_r1.verify_saved
    if ($LASTEXITCODE -ne 0) { throw "Saved metadata reproduction failed: $LASTEXITCODE" }
} finally { Pop-Location }
