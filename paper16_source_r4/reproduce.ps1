param([string]$Python=(Join-Path $PSScriptRoot '..\paper16_m1\work\runtime\Scripts\python.exe'))
$ErrorActionPreference='Stop'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Supply pinned Python3.11.15 runtime; no source/download fallback.' }
$env:PYTHONDONTWRITEBYTECODE='1'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    Write-Output ('PowerShell '+$PSVersionTable.PSVersion.ToString()+'; saved-only R4 source/QC audit, protected existing states required')
    & $Python -B -m paper16_source_r4.verify_saved
    if ($LASTEXITCODE -ne 0) { throw "Saved R4 audit failed: $LASTEXITCODE" }
} finally { Pop-Location }
