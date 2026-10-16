param([string]$Python = "")
$ErrorActionPreference = 'Stop'
if (-not $Python) {
    $candidate = Join-Path $env:USERPROFILE 'AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $candidate) { $Python = $candidate }
    else { $Python = (Get-Command python -ErrorAction Stop).Source }
}
$previousFamilyReproductionPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $PSScriptRoot 'work\ad_vendor'
    if ($previousFamilyReproductionPath) { $env:PYTHONPATH += [IO.Path]::PathSeparator + $previousFamilyReproductionPath }
    Push-Location (Split-Path -Parent $PSScriptRoot)
    try {
        & $Python -m paper13_ki_execution1.verify_families
        if ($LASTEXITCODE -ne 0) { throw 'Family saved/synthetic verification failed.' }
    } finally { Pop-Location }
} finally { $env:PYTHONPATH = $previousFamilyReproductionPath }
Write-Output 'Saved identities and synthetic family implementation verified; no real fits or scores were rerun.'
