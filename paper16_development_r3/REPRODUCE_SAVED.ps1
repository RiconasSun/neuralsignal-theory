param()
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskPython = Join-Path $taskRoot 'paper16_m1/work/runtime/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) { throw 'Pinned protected Python runtime missing; no fallback or source reacquisition.' }
Push-Location -LiteralPath $taskRoot
try {
    & $taskPython -B -m paper16_development_r3.reproduce
    if ($LASTEXITCODE -ne 0) { throw "Saved-only reproduction failed: $LASTEXITCODE" }
} finally { Pop-Location }
