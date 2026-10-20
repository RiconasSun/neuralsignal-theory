param()
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskPython = Join-Path $taskRoot 'paper16_m1/work/runtime/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) { throw 'Pinned protected runtime missing; no acquisition or fallback.' }
Push-Location -LiteralPath $taskRoot
try {
    & $taskPython -B -m paper16_development_r2.reproduce
    if ($LASTEXITCODE -ne 0) { throw 'Saved manifest/facts reproduction failed.' }
    & $taskPython -B -m paper16_development_r2.verify_stop_archive
    if ($LASTEXITCODE -ne 0) { throw 'Saved STOP/schema/boundary verification failed.' }
} finally { Pop-Location }
