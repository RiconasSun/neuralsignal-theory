param([string]$Python)
$ErrorActionPreference='Stop'
if (-not $Python) { $Python=Join-Path (Split-Path -Parent $PSScriptRoot) 'paper15_dev/work/runtime/Scripts/python.exe' }
if (-not (Test-Path -LiteralPath $Python)) { throw 'Provide -Python with pinned requirements already installed. This saved-only command never downloads or refits real data.' }
$Python=(Resolve-Path -LiteralPath $Python).Path
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    & $Python -W error::ResourceWarning -m paper15_r1.saved_verify
    if ($LASTEXITCODE -ne 0) { throw "P15 R1 saved-evidence reproduction failed: $LASTEXITCODE" }
} finally { Pop-Location }
