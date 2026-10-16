param([string]$Python = "")
$ErrorActionPreference = 'Stop'
if (-not $Python) {
    $candidate = Join-Path $env:USERPROFILE 'AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $candidate) { $Python = $candidate }
    else { $Python = (Get-Command python -ErrorAction Stop).Source }
}
$priorMissionPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $PSScriptRoot 'work\ad_vendor'
    if ($priorMissionPythonPath) { $env:PYTHONPATH += [IO.Path]::PathSeparator + $priorMissionPythonPath }
    Push-Location (Split-Path -Parent $PSScriptRoot)
    try {
        & $Python -m paper13_ki_execution1.verify_baseline_A
        if ($LASTEXITCODE -ne 0) { throw 'M3 saved/synthetic verification failed.' }
    } finally { Pop-Location }
} finally { $env:PYTHONPATH = $priorMissionPythonPath }
Write-Output 'Saved identities and synthetic M3 implementation verified; no real science was rerun.'
