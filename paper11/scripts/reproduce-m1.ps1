param([string]$Python = "python", [switch]$Acquire)
$ErrorActionPreference = "Stop"
$paperRoot = Split-Path -Parent $PSScriptRoot
$resultRoot = Join-Path $paperRoot "results/M1"
New-Item -ItemType Directory -Force -Path $resultRoot | Out-Null
$runArgs = @((Join-Path $PSScriptRoot "run_m1.py"))
if ($Acquire) { $runArgs += "--acquire" }
& $Python @runArgs | Tee-Object -FilePath (Join-Path $resultRoot "execution.log")
if ($LASTEXITCODE -eq 2) { throw "P11 M1 DATA_INSUFFICIENT. Preserve result; do not enter M2." }
if ($LASTEXITCODE -ne 0) { throw "P11 M1 gate failed. Inspect results/M1; do not enter M2." }
Write-Output "M1 only completed; no features or models were fitted."
