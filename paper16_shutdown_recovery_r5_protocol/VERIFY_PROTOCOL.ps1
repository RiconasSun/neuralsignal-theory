$ErrorActionPreference = 'Stop'
$taskRepo = Split-Path -Parent $PSScriptRoot
$taskPython = Join-Path $taskRepo 'paper16_m1/work/runtime/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) { throw 'Existing runtime required; do not download sources or fit as a fallback.' }
Push-Location -LiteralPath $taskRepo
try {
    & $taskPython -B -X utf8 -m paper16_shutdown_recovery_r5_protocol.verify_protocol
    if ($LASTEXITCODE -ne 0) { throw 'Protocol metadata verification failed.' }
} finally { Pop-Location }
