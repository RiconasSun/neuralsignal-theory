$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$runtime = Join-Path $PSScriptRoot 'work/runtime/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $runtime)) { throw 'Install Python >=3.11 and paper16_m0/requirements.txt in paper16_m0/work/runtime first. This reproduction does not install or access the network.' }
$env:PYTHONDONTWRITEBYTECODE = '1'
Push-Location -LiteralPath $repo
try {
    & $runtime -m paper16_m0.code.saved_reproduce
    if ($LASTEXITCODE -ne 0) { throw "Saved-only reproduction failed: $LASTEXITCODE" }
} finally { Pop-Location }
