param([string]$Python = "")
$ErrorActionPreference = 'Stop'
if (-not $Python) { $Python = Join-Path $env:USERPROFILE 'AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' }
$previousP13CalibrationPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $PSScriptRoot 'work\ad_vendor'
    if ($previousP13CalibrationPath) { $env:PYTHONPATH += [IO.Path]::PathSeparator + $previousP13CalibrationPath }
    Push-Location (Split-Path -Parent $PSScriptRoot)
    try {
        & $Python -B -m paper13_ki_execution1.verify_final_C
        if ($LASTEXITCODE -ne 0) { throw 'Saved/synthetic C-only implementation verification failed.' }
    } finally { Pop-Location }
} finally { $env:PYTHONPATH = $previousP13CalibrationPath }
Write-Output 'Saved/synthetic C-only implementation verified; no real calibration fitting, new control experiment or final D analysis.'
