param([string]$Python = "")
$ErrorActionPreference = 'Stop'
if (-not $Python) { $Python = Join-Path $env:USERPROFILE 'AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' }
$previousP13EPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $PSScriptRoot 'work\ad_vendor'
    if ($previousP13EPath) { $env:PYTHONPATH += [IO.Path]::PathSeparator + $previousP13EPath }
    Push-Location (Split-Path -Parent $PSScriptRoot)
    try {
        & $Python -B -m paper13_ki_execution1.verify_exploratory_E
        if ($LASTEXITCODE -ne 0) { throw 'Saved M4/synthetic E verification failed.' }
    } finally { Pop-Location }
} finally { $env:PYTHONPATH = $previousP13EPath }
Write-Output 'Saved M4 identities and synthetic E path verified; no E/D values read and no real fits rerun.'
