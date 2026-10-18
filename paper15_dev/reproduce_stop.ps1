param([string]$Python)
$ErrorActionPreference='Stop'
if (-not $Python) { $Python=Join-Path $PSScriptRoot 'work/runtime/Scripts/python.exe' }
if (-not (Test-Path -LiteralPath $Python)) { throw 'Provide -Python with paper15_dev/requirements.txt already installed. No download or scientific rerun is performed.' }
$Python=(Resolve-Path -LiteralPath $Python).Path
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    & $Python -W error::ResourceWarning -m paper15_dev.stop_verify
    if ($LASTEXITCODE -ne 0) { throw "P15 stopped-evidence audit failed: $LASTEXITCODE" }
} finally { Pop-Location }
