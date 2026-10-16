param([string]$Python = "")
$ErrorActionPreference = 'Stop'
if (-not $Python) {
    $candidate = Join-Path $env:USERPROFILE 'AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $candidate) { $Python = $candidate }
    else { $Python = (Get-Command python -ErrorAction Stop).Source }
}
$previousBReproductionPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $PSScriptRoot 'work\ad_vendor'
    if ($previousBReproductionPath) { $env:PYTHONPATH += [IO.Path]::PathSeparator + $previousBReproductionPath }
    Push-Location (Split-Path -Parent $PSScriptRoot)
    try {
        & $Python -m paper13_ki_execution1.verify_development_B
        if ($LASTEXITCODE -ne 0) { throw 'Saved/synthetic B verification failed.' }
    } finally { Pop-Location }
} finally { $env:PYTHONPATH = $previousBReproductionPath }
Write-Output 'Saved certificates and synthetic B implementation verified; no neural evaluation was rerun.'
