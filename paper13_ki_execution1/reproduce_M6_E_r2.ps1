param([string]$Python = "")
$ErrorActionPreference = 'Stop'
if (-not $Python) { $Python = Join-Path $env:USERPROFILE 'AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' }
$previousP13ControlR2Path = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $PSScriptRoot 'work\ad_vendor'
    if ($previousP13ControlR2Path) { $env:PYTHONPATH += [IO.Path]::PathSeparator + $previousP13ControlR2Path }
    Push-Location (Split-Path -Parent $PSScriptRoot)
    try {
        & $Python -B -m paper13_ki_execution1.verify_controls_E_r2
        if ($LASTEXITCODE -ne 0) { throw 'Repaired saved/synthetic control verification failed.' }
    } finally { Pop-Location }
} finally { $env:PYTHONPATH = $previousP13ControlR2Path }
Write-Output 'Current and archived source identities plus synthetic repaired controls verified; no real control run, calibration fitting or final D analysis.'
