param([string]$Manifest = '')
$ErrorActionPreference = 'Stop'
$taskRepo = Split-Path -Parent $PSScriptRoot
$taskPython = Join-Path $taskRepo 'paper16_m1/work/runtime/Scripts/python.exe'
$taskScript = Join-Path $taskRepo 'ops/evidence/2026-10-21/p16-m3-m5-shutdown-recovery-r5/reproduce_saved.py'
Push-Location -LiteralPath $taskRepo
try {
    $taskArgs = @('-B', $taskScript)
    if ($Manifest) { $taskArgs += @('--manifest', $Manifest) }
    & $taskPython @taskArgs
    if ($LASTEXITCODE -ne 0) { throw "Saved-only verification failed, exit=$LASTEXITCODE" }
} finally { Pop-Location }
