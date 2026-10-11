param([string]$Python = "python")
$ErrorActionPreference = "Stop"
$paperRoot = Split-Path -Parent $PSScriptRoot
& $Python (Join-Path $PSScriptRoot "run_m0.py") --verify
if ($LASTEXITCODE -ne 0) { throw "P11 M0 gate failed. Inspect paper11/results/M0; do not enter M1." }
Write-Output "P11 M0 verification completed. No later milestone executed."
