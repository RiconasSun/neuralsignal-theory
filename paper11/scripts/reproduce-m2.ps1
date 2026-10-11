param([string]$Python = 'python', [switch]$AcquireNix)
$ErrorActionPreference = 'Stop'
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Push-Location $root
try {
    New-Item -ItemType Directory -Force paper11/results/M2 | Out-Null
    if ($AcquireNix) {
        & $Python paper11/scripts/acquire_nix_coverage.py 2>&1 | Tee-Object paper11/results/M2/nix_acquisition.log
        if ($LASTEXITCODE -ne 0) { throw 'Checksum-bound NIX acquisition failed.' }
    }
    & $Python paper11/scripts/run_m2.py 2>&1 | Tee-Object paper11/results/M2/execution.log
    $analysisExit = $LASTEXITCODE
    if (Test-Path paper11/results/M2/qc_report.json) {
        & $Python paper11/scripts/plot_m2_qc.py
        if ($LASTEXITCODE -ne 0) { throw 'Descriptive QC figure generation failed.' }
    }
    if ($analysisExit -ne 0) { throw 'M2 gate failed; do not advance.' }
} finally { Pop-Location }
