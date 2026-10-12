param([string]$Python='', [switch]$Native)
$ErrorActionPreference='Stop'
if (-not $Python) {
    $Existing=Join-Path $env:LOCALAPPDATA 'hermes/hermes-agent/venv/Scripts/python.exe'
    if (Test-Path -LiteralPath $Existing) { $Python=$Existing }
    else { $Python=(Get-Command python -ErrorAction Stop).Source }
}
$Arguments=@((Join-Path $PSScriptRoot 'reproduce.py'))
if ($Native) { $Arguments+='--native' }
& $Python @Arguments
if ($LASTEXITCODE -ne 0) { throw "Checkpoint reproduction failed: $LASTEXITCODE" }
