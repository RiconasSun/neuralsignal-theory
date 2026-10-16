param([string]$Python = "")
$ErrorActionPreference = 'Stop'
if (-not $Python) { $Python = Join-Path $env:USERPROFILE 'AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' }
$previousP13SavedPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $PSScriptRoot 'work\ad_vendor'
    if ($previousP13SavedPath) { $env:PYTHONPATH += [IO.Path]::PathSeparator + $previousP13SavedPath }
    Push-Location (Split-Path -Parent $PSScriptRoot)
    try {
        & $Python -B -m paper13_ki_execution1.verify_saved_progress
        if ($LASTEXITCODE -ne 0) { throw 'Saved progress reproduction failed.' }
    } finally { Pop-Location }
} finally { $env:PYTHONPATH = $previousP13SavedPath }
Write-Output 'Saved progress reproduced without source access, real fitting, new controls or final D outcomes.'
