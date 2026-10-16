param([string]$Python = "")
$ErrorActionPreference = 'Stop'
if (-not $Python) { $Python = Join-Path $env:USERPROFILE 'AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' }
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    & $Python -B -m paper13_bstar_diag1.verify_saved
    if ($LASTEXITCODE -ne 0) { throw 'Saved diagnostic verification failed.' }
} finally { Pop-Location }
Write-Output 'Saved diagnosis verified. No real conditional simulation, fit, source access or C/D evaluation.'
