$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repo
$python = Join-Path $repo 'paper16_m1/work/runtime/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Missing pinned Python runtime; no automatic source acquisition or fitting permitted.' }
& $python -B -m paper16_pg_forensics_r1.integrity
if ($LASTEXITCODE -ne 0) { throw 'Forensic archive payload identity failure' }
& $python -B -m paper16_pg_forensics_r1.tests
if ($LASTEXITCODE -ne 0) { throw 'Forensic regression failure' }
& $python -B -m paper16_pg_forensics_r1.audit
if ($LASTEXITCODE -ne 0) { throw 'Saved-only forensic reproduction failure' }
