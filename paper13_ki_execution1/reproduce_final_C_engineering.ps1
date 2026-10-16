param([string]$Python = "")
$ErrorActionPreference = 'Stop'
if (-not $Python) { $Python = Join-Path $env:USERPROFILE 'AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' }
$previousP13CEngineeringPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $PSScriptRoot 'work\ad_vendor'
    if ($previousP13CEngineeringPath) { $env:PYTHONPATH += [IO.Path]::PathSeparator + $previousP13CEngineeringPath }
    Push-Location (Split-Path -Parent $PSScriptRoot)
    try {
        & $Python -B -m paper13_ki_execution1.verify_final_C_engineering
        if ($LASTEXITCODE -ne 0) { throw 'C-only/sensitivity synthetic engineering verification failed.' }
    } finally { Pop-Location }
} finally { $env:PYTHONPATH = $previousP13CEngineeringPath }
Write-Output 'C-only and sensitivity synthetic implementation verified; no actual calibration fit or final D outcome access.'
