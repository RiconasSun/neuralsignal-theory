param([string]$Python = "")
$ErrorActionPreference = 'Stop'
if (-not $Python) { $Python = Join-Path $env:USERPROFILE 'AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' }
$previousP13DescriptivePath=$env:PYTHONPATH
try {
    $env:PYTHONPATH=Join-Path (Split-Path -Parent $PSScriptRoot) 'paper13_ki_execution1\work\ad_vendor'
    if ($previousP13DescriptivePath) { $env:PYTHONPATH += [IO.Path]::PathSeparator + $previousP13DescriptivePath }
    Push-Location (Split-Path -Parent $PSScriptRoot)
    try {
        & $Python -B -m paper13_descriptive_final1.verify_saved
        if ($LASTEXITCODE -ne 0) { throw 'Saved descriptive verification failed.' }
    } finally { Pop-Location }
} finally { $env:PYTHONPATH=$previousP13DescriptivePath }
Write-Output 'Saved evidence and synthetic checks only. No real C fitting, D rescoring, real null draw or new source access.'
