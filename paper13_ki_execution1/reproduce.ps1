param([string]$Python = "")
$ErrorActionPreference = 'Stop'
if (-not $Python) {
    $candidate = Join-Path $env:USERPROFILE 'AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $candidate) { $Python = $candidate }
    else { $Python = (Get-Command python -ErrorAction Stop).Source }
}
$missionVendor = Join-Path $PSScriptRoot 'work\ad_vendor'
$priorPythonPath = $env:PYTHONPATH
try {
    if (Test-Path -LiteralPath $missionVendor) {
        $env:PYTHONPATH = $missionVendor
        if ($priorPythonPath) { $env:PYTHONPATH += [IO.Path]::PathSeparator + $priorPythonPath }
    }
    Push-Location (Split-Path -Parent $PSScriptRoot)
    try {
        & $Python -m paper13_ki_execution1.verify_checkpoint
        if ($LASTEXITCODE -ne 0) { throw 'Saved/synthetic checkpoint verification failed. Pinned requirements must be installed; no automatic network installation is performed.' }
    } finally { Pop-Location }
} finally { $env:PYTHONPATH = $priorPythonPath }
Write-Output 'Saved M1/engineering checkpoint verified. Real physiology and scientific evaluation remain unexecuted.'
