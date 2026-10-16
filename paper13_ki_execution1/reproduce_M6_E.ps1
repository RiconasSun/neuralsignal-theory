param([string]$Python = "")
$ErrorActionPreference = 'Stop'
if (-not $Python) { $Python = Join-Path $env:USERPROFILE 'AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' }
$previousP13ControlPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $PSScriptRoot 'work\ad_vendor'
    if ($previousP13ControlPath) { $env:PYTHONPATH += [IO.Path]::PathSeparator + $previousP13ControlPath }
    Push-Location (Split-Path -Parent $PSScriptRoot)
    try {
        & $Python -B -m paper13_ki_execution1.verify_controls_E
        if ($LASTEXITCODE -ne 0) { throw 'Saved/synthetic E control-stage verification failed.' }
    } finally { Pop-Location }
} finally { $env:PYTHONPATH = $previousP13ControlPath }
Write-Output 'Saved and synthetic control engineering verified; no real null experiment, source call, fitting or final D analysis.'
