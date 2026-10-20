param()
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskPython = Join-Path $taskRoot 'paper16_m1/work/runtime/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) { throw 'Pinned runtime/protected saved states required; no reacquisition or fitting fallback.' }
Push-Location -LiteralPath $taskRoot
try {
    & $taskPython -B -m paper16_development_r3.archive_check
    if ($LASTEXITCODE -ne 0) { throw "Saved-only R3 archive check failed: $LASTEXITCODE" }
} finally { Pop-Location }
