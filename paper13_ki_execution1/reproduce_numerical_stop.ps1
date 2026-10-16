param([string]$Python = "")
$ErrorActionPreference = 'Stop'
if (-not $Python) { $Python = Join-Path $env:USERPROFILE 'AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' }
$previousP13StopPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $PSScriptRoot 'work\ad_vendor'
    if ($previousP13StopPath) { $env:PYTHONPATH += [IO.Path]::PathSeparator + $previousP13StopPath }
    Push-Location (Split-Path -Parent $PSScriptRoot)
    try {
        & $Python -B -m paper13_ki_execution1.verify_numerical_stop
        if ($LASTEXITCODE -ne 0) { throw 'Saved numerical-stop reproduction failed.' }
    } finally { Pop-Location }
} finally { $env:PYTHONPATH = $previousP13StopPath }
Write-Output 'Saved stop reproduced. No simulation retry, real fit, source request or final D assessment.'
