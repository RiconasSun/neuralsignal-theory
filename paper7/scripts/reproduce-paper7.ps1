$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Python = "python"

function Invoke-Paper7Step {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$Script,
        [string[]]$Arguments = @(),
        [int[]]$AllowedExitCodes = @(0)
    )

    Write-Host "Paper 7 reproduction: $Label"
    & $Python $Script @Arguments
    $code = $LASTEXITCODE
    if ($AllowedExitCodes -notcontains $code) {
        throw "Paper 7 reproduction step failed: $Label (exit code $code)"
    }
    if ($code -ne 0) {
        Write-Host "Paper 7 reproduction: $Label returned expected nonzero gate code $code"
    }
}

Invoke-Paper7Step `
    -Label "E0 HCP-YA dataset and MRtrix/FSL toolchain audit" `
    -Script (Join-Path $Root "scripts\paper7_e0_dataset_toolchain_audit.py") `
    -AllowedExitCodes @(0, 2)

Invoke-Paper7Step `
    -Label "E1 MRtrix ACT/SIFT2 command-plan generation" `
    -Script (Join-Path $Root "scripts\paper7_e1_generate_mrtrix_plan.py")

Invoke-Paper7Step `
    -Label "E1b HCP structural input audit for 3-subject smoke" `
    -Script (Join-Path $Root "scripts\paper7_hcp_structural_input_audit_download.py") `
    -AllowedExitCodes @(0, 2)

Invoke-Paper7Step `
    -Label "E2 checkpointed WSL MRtrix ACT/iFOD2/SIFT2 one-subject smoke" `
    -Script (Join-Path $Root "scripts\paper7_e2_wsl_mrtrix_smoke.py") `
    -AllowedExitCodes @(0, 2)

Invoke-Paper7Step `
    -Label "P7 ACT/SIFT2 engineering diagnostic summary" `
    -Script (Join-Path $Root "scripts\paper7_write_engineering_diagnostic.py")

Invoke-Paper7Step `
    -Label "E3 three-subject final-route ACT/iFOD2/SIFT2 smoke" `
    -Script (Join-Path $Root "scripts\paper7_e3_three_subject_final_route_smoke.py") `
    -Arguments @("--subjects", "100307", "100408", "101107", "--label", "e3_three_subject_final_route_smoke")

Invoke-Paper7Step `
    -Label "E4 ten-subject final-route ACT/iFOD2/SIFT2 connectome QC smoke" `
    -Script (Join-Path $Root "scripts\paper7_e3_three_subject_final_route_smoke.py") `
    -Arguments @("--limit", "10", "--label", "e4_ten_subject_connectome_qc")

Invoke-Paper7Step `
    -Label "E4 ten-subject connectome QC summary" `
    -Script (Join-Path $Root "scripts\paper7_e4_summarize_connectome_qc.py")

Invoke-Paper7Step `
    -Label "E5 fs_default84 label-conversion connectome QC" `
    -Script (Join-Path $Root "scripts\paper7_e5_labelconvert_connectome_qc.py") `
    -Arguments @("--limit", "10")

Invoke-Paper7Step `
    -Label "E5 100307 20k streamline sensitivity" `
    -Script (Join-Path $Root "scripts\paper7_e5_100307_streamline_sensitivity.py") `
    -Arguments @("--subject", "100307", "--streamlines", "20000")

Invoke-Paper7Step `
    -Label "E6 streaming connectome batch 10_2" `
    -Script (Join-Path $Root "scripts\paper7_e6_streaming_connectome_batch.py") `
    -Arguments @("--limit", "12", "--start-index", "10", "--count", "2", "--cleanup-large-intermediates")

Invoke-Paper7Step `
    -Label "E6 streaming connectome batch 12_3" `
    -Script (Join-Path $Root "scripts\paper7_e6_streaming_connectome_batch.py") `
    -Arguments @("--limit", "15", "--start-index", "12", "--count", "3", "--cleanup-large-intermediates")

Invoke-Paper7Step `
    -Label "E6 streaming connectome batch 15_5" `
    -Script (Join-Path $Root "scripts\paper7_e6_streaming_connectome_batch.py") `
    -Arguments @("--limit", "20", "--start-index", "15", "--count", "5", "--cleanup-large-intermediates")

Invoke-Paper7Step `
    -Label "E6 streaming connectome batch 20_5" `
    -Script (Join-Path $Root "scripts\paper7_e6_streaming_connectome_batch.py") `
    -Arguments @("--limit", "25", "--start-index", "20", "--count", "5", "--cleanup-large-intermediates")

Invoke-Paper7Step `
    -Label "E6 streaming connectome batch 25_5" `
    -Script (Join-Path $Root "scripts\paper7_e6_streaming_connectome_batch.py") `
    -Arguments @("--limit", "30", "--start-index", "25", "--count", "5", "--cleanup-large-intermediates")

Invoke-Paper7Step `
    -Label "E6 streaming connectome batch 30_5" `
    -Script (Join-Path $Root "scripts\paper7_e6_streaming_connectome_batch.py") `
    -Arguments @("--limit", "35", "--start-index", "30", "--count", "5", "--cleanup-large-intermediates")

Invoke-Paper7Step `
    -Label "E6 streaming connectome batch 35_5" `
    -Script (Join-Path $Root "scripts\paper7_e6_streaming_connectome_batch.py") `
    -Arguments @("--limit", "40", "--start-index", "35", "--count", "5", "--cleanup-large-intermediates")

Invoke-Paper7Step `
    -Label "E6 streaming connectome batch 40_5" `
    -Script (Join-Path $Root "scripts\paper7_e6_streaming_connectome_batch.py") `
    -Arguments @("--limit", "45", "--start-index", "40", "--count", "5", "--cleanup-large-intermediates")

Invoke-Paper7Step `
    -Label "E6 streaming connectome batch 45_5" `
    -Script (Join-Path $Root "scripts\paper7_e6_streaming_connectome_batch.py") `
    -Arguments @("--limit", "50", "--start-index", "45", "--count", "5", "--cleanup-large-intermediates")

Invoke-Paper7Step `
    -Label "E6 streaming connectome batch 50_5" `
    -Script (Join-Path $Root "scripts\paper7_e6_streaming_connectome_batch.py") `
    -Arguments @("--limit", "55", "--start-index", "50", "--count", "5", "--cleanup-large-intermediates")

Invoke-Paper7Step `
    -Label "E6 streaming connectome batch 55_5" `
    -Script (Join-Path $Root "scripts\paper7_e6_streaming_connectome_batch.py") `
    -Arguments @("--limit", "60", "--start-index", "55", "--count", "5", "--cleanup-large-intermediates")

Invoke-Paper7Step `
    -Label "E6 streaming connectome batch 60_5" `
    -Script (Join-Path $Root "scripts\paper7_e6_streaming_connectome_batch.py") `
    -Arguments @("--limit", "65", "--start-index", "60", "--count", "5", "--cleanup-large-intermediates")

Invoke-Paper7Step `
    -Label "E6 streaming connectome batch 65_5" `
    -Script (Join-Path $Root "scripts\paper7_e6_streaming_connectome_batch.py") `
    -Arguments @("--limit", "70", "--start-index", "65", "--count", "5", "--cleanup-large-intermediates")

Invoke-Paper7Step `
    -Label "E6 streaming connectome batch 70_5" `
    -Script (Join-Path $Root "scripts\paper7_e6_streaming_connectome_batch.py") `
    -Arguments @("--limit", "75", "--start-index", "70", "--count", "5", "--cleanup-large-intermediates")

Invoke-Paper7Step `
    -Label "E6 streaming connectome batch 75_5" `
    -Script (Join-Path $Root "scripts\paper7_e6_streaming_connectome_batch.py") `
    -Arguments @("--limit", "80", "--start-index", "75", "--count", "5", "--cleanup-large-intermediates")

Invoke-Paper7Step `
    -Label "E6 streaming connectome batch 80_5" `
    -Script (Join-Path $Root "scripts\paper7_e6_streaming_connectome_batch.py") `
    -Arguments @("--limit", "85", "--start-index", "80", "--count", "5", "--cleanup-large-intermediates")

Invoke-Paper7Step `
    -Label "E6 streaming connectome batch 85_5" `
    -Script (Join-Path $Root "scripts\paper7_e6_streaming_connectome_batch.py") `
    -Arguments @("--limit", "90", "--start-index", "85", "--count", "5", "--cleanup-large-intermediates")

Invoke-Paper7Step `
    -Label "E6 streaming connectome batch 90_5" `
    -Script (Join-Path $Root "scripts\paper7_e6_streaming_connectome_batch.py") `
    -Arguments @("--limit", "95", "--start-index", "90", "--count", "5", "--cleanup-large-intermediates")

Invoke-Paper7Step `
    -Label "E6 streaming connectome batch 95_5" `
    -Script (Join-Path $Root "scripts\paper7_e6_streaming_connectome_batch.py") `
    -Arguments @("--limit", "100", "--start-index", "95", "--count", "5", "--cleanup-large-intermediates")

Invoke-Paper7Step `
    -Label "E6 streaming cleanup audit" `
    -Script (Join-Path $Root "scripts\paper7_e6_streaming_cleanup_audit.py")

Invoke-Paper7Step `
    -Label "E6 available fs_default84 connectome summary" `
    -Script (Join-Path $Root "scripts\paper7_e6_summarize_available_fsdefault_connectomes.py")

Invoke-Paper7Step `
    -Label "E7 preliminary structural-model interface smoke" `
    -Script (Join-Path $Root "scripts\paper7_e7_preliminary_structural_model_smoke.py")

Invoke-Paper7Step `
    -Label "E7 final 99-subject structural hypothesis test" `
    -Script (Join-Path $Root "scripts\paper7_e7_final_structural_hypothesis_test.py")

Invoke-Paper7Step `
    -Label "P7 final figure generation" `
    -Script (Join-Path $Root "scripts\paper7_make_final_figures.py")

Invoke-Paper7Step `
    -Label "P7 manuscript PDF preview generation" `
    -Script (Join-Path $Root "scripts\paper7_make_manuscript_pdf.py")

Invoke-Paper7Step `
    -Label "P7 single-subject final-route smoke summary" `
    -Script (Join-Path $Root "scripts\paper7_write_final_route_smoke_result.py")

Invoke-Paper7Step `
    -Label "P7 MSMT FOD readiness validator" `
    -Script (Join-Path $Root "scripts\paper7_msmt_fod_readiness_validator.py") `
    -AllowedExitCodes @(0, 2)

Invoke-Paper7Step `
    -Label "E8 claim audit" `
    -Script (Join-Path $Root "scripts\write_paper7_claim_audit.py")
