param([string]$Python='C:/Users/85993/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe')
$ErrorActionPreference='Stop'
& $Python (Join-Path $PSScriptRoot 'audit.py') replay
exit $LASTEXITCODE
