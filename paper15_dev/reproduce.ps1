param([string]$Python)
$ErrorActionPreference='Stop'
if (-not $Python) { $Python=Join-Path $PSScriptRoot 'work/runtime/Scripts/python.exe' }
if (-not (Test-Path -LiteralPath $Python)) { throw 'Provide -Python with the pinned requirements. Saved-only command never downloads, fits, or reads neural arrays.' }
$Python=(Resolve-Path -LiteralPath $Python).Path
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    & $Python -W error::ResourceWarning -m paper15_dev.saved_verify
    if ($LASTEXITCODE -ne 0) { throw "P15 saved-evidence reproduction failed: $LASTEXITCODE" }
} finally { Pop-Location }
