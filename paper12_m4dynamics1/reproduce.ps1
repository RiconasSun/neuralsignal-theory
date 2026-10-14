param([string]$Python='')
$ErrorActionPreference='Stop'
if (-not $Python) {
    $Bundled=Join-Path $env:LOCALAPPDATA 'hermes/hermes-agent/venv/Scripts/python.exe'
    if (Test-Path -LiteralPath $Bundled) { $Python=$Bundled }
    else { $Python=(Get-Command python -ErrorAction Stop).Source }
}
& $Python (Join-Path $PSScriptRoot 'reproduce_saved.py')
if ($LASTEXITCODE -ne 0) { throw "Saved dynamics numerical reproduction failed: $LASTEXITCODE" }
