$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repo
$python = Join-Path $repo 'paper16_m1/work/runtime/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Missing frozen runtime; no automatic installation, fitting or source request.' }
& $python -B -m paper16_termination_feasibility1.reproduce
if ($LASTEXITCODE -ne 0) { throw 'Saved-only verification failed; preserve evidence, never retry scientific fitting.' }
