$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Python = "python"

function Invoke-Paper6Step {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$Script,
        [string[]]$Arguments = @()
    )

    Write-Host "Paper 6 reproduction: $Label"
    & $Python $Script @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Paper 6 reproduction step failed: $Label (exit code $LASTEXITCODE)"
    }
}

$E1Json = Join-Path $Root "results\e1_dataset_audit.json"
$E1Csv = Join-Path $Root "results\e1_dataset_audit.csv"
if ((Test-Path $E1Json) -and (Test-Path $E1Csv)) {
    Write-Host "Paper 6 reproduction: E1 public electrophysiology dataset audit already exists; reusing local audit"
} else {
    Invoke-Paper6Step `
        -Label "E1 public electrophysiology dataset audit" `
        -Script (Join-Path $Root "scripts\audit_p6_electrophysiology_datasets.py")
}

$E2Json = Join-Path $Root "results\e2_event_semantics_audit.json"
$E2Csv = Join-Path $Root "results\e2_event_semantics_audit.csv"
if ((Test-Path $E2Json) -and (Test-Path $E2Csv)) {
    Write-Host "Paper 6 reproduction: E2 event-semantics audit already exists; reusing local audit"
} else {
    Invoke-Paper6Step `
        -Label "E2 event-semantics audit" `
        -Script (Join-Path $Root "scripts\audit_p6_event_semantics.py")
}

$ManifestJson = Join-Path $Root "results\e2_ds004117_transition_windows.json"
$ManifestCsv = Join-Path $Root "results\e2_ds004117_transition_windows.csv"
if ((Test-Path $ManifestJson) -and (Test-Path $ManifestCsv)) {
    Write-Host "Paper 6 reproduction: E2 transition-window manifest already exists; reusing local manifest"
} else {
    Invoke-Paper6Step `
        -Label "E2 transition-window manifest build" `
        -Script (Join-Path $Root "scripts\build_p6_ds004117_transition_windows.py")
}

Invoke-Paper6Step `
    -Label "E3 one-run signal extraction smoke" `
    -Script (Join-Path $Root "scripts\run_p6_e3_ds004117_signal_smoke.py")

Invoke-Paper6Step `
    -Label "E3-E6 default multi-run signal analysis" `
    -Script (Join-Path $Root "scripts\run_p6_e3_e6_ds004117_multi_run.py")

$BatchGlob = Join-Path $Root "features\ds004117_multi_run\ds004117_batch*_bandpower_delta_features.csv"
$BatchFiles = Get-ChildItem -Path $BatchGlob -ErrorAction SilentlyContinue
if ($BatchFiles.Count -gt 0) {
    Invoke-Paper6Step `
        -Label "aggregating existing full-cohort batch feature files" `
        -Script (Join-Path $Root "scripts\aggregate_p6_e3_e6_ds004117_batches.py") `
        -Arguments @("--label-prefix", "batch", "--analysis-label", "full_cohort_batched", "--n-perm", "200")
} else {
    Write-Host "Paper 6 reproduction: no full-cohort batch feature files found; default run remains lightweight."
    Write-Host "See paper6\attachments\A10_One_Command_Reproduction.md for full-cohort batch extraction commands."
}

Invoke-Paper6Step `
    -Label "E7 ds004752 external convergent analysis" `
    -Script (Join-Path $Root "scripts\run_p6_e7_ds004752_external_convergent.py")

if (Test-Path (Join-Path $Root "results\e3_e6_ds004117_full_cohort_batched_results.json")) {
    Invoke-Paper6Step `
        -Label "current figure generation" `
        -Script (Join-Path $Root "scripts\make_p6_figures.py")

    Invoke-Paper6Step `
        -Label "E8 final claim audit" `
        -Script (Join-Path $Root "scripts\write_p6_final_claim_audit.py")
}
