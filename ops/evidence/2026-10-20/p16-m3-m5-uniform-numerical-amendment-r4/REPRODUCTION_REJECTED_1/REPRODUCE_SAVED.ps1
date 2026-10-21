$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonRuntime = Join-Path $repoRoot 'paper16_m1/work/runtime/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonRuntime)) { throw 'Pinned runtime and original protected saved bundle required; no fitting fallback.' }
Push-Location -LiteralPath $repoRoot
try {
    & $pythonRuntime -B -m paper16_development_r4.reproduce_saved
    if ($LASTEXITCODE -ne 0) { throw 'Saved-only R4 reproduction failed.' }
} finally { Pop-Location }
