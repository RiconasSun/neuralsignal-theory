param([string]$Python = 'C:/Users/85993/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe',
      [ValidateSet('replay','execute')][string]$Mode = 'replay')
$ErrorActionPreference = 'Stop'
$Script = Join-Path $PSScriptRoot 'run_r2.py'
& $Python $Script verify
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python $Script $Mode
exit $LASTEXITCODE
