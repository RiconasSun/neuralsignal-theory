$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repo
$python = Join-Path $repo 'paper16_m1/work/runtime/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Missing pinned runtime; no fitting or source acquisition allowed.' }
& $python -B -m paper16_termination_feasibility1.archive_identity
if ($LASTEXITCODE -ne 0) { throw 'Frozen identity failed' }
& $python -B -m paper16_termination_feasibility1.test_saved
if ($LASTEXITCODE -ne 0) { throw 'Saved evidence regressions failed' }
& $python -B -m paper16_termination_feasibility1.reproduce
if ($LASTEXITCODE -ne 0) { throw 'Saved-only reproduction failed' }
