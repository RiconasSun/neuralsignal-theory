param([string]$Python = '')
$ErrorActionPreference = 'Stop'
if (-not $Python) {
    $Existing = Join-Path $env:LOCALAPPDATA 'hermes/hermes-agent/venv/Scripts/python.exe'
    if (Test-Path -LiteralPath $Existing) { $Python = $Existing }
    else { $Python = (Get-Command python -ErrorAction Stop).Source }
}
& $Python (Join-Path $PSScriptRoot 'reproduce_saved.py')
if ($LASTEXITCODE -ne 0) { throw "Saved public recovery reproduction failed: $LASTEXITCODE" }
