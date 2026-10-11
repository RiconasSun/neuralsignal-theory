$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Python = "python"

function Invoke-Paper8Step {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$Script,
        [string[]]$Arguments = @(),
        [int[]]$AllowedExitCodes = @(0)
    )

    Write-Host "Paper 8 reproduction: $Label"
    & $Python $Script @Arguments
    $code = $LASTEXITCODE
    if ($AllowedExitCodes -notcontains $code) {
        throw "Paper 8 reproduction step failed: $Label (exit code $code)"
    }
    if ($code -ne 0) {
        Write-Host "Paper 8 reproduction: $Label returned expected nonzero gate code $code"
    }
}

Invoke-Paper8Step `
    -Label "E0 public dataset and measured-physiology availability audit" `
    -Script (Join-Path $Root "scripts\paper8_e0_public_dataset_physio_audit.py") `
    -AllowedExitCodes @(0, 2)

Invoke-Paper8Step `
    -Label "E1 HCP WM physio download" `
    -Script (Join-Path $Root "scripts\paper8_e1_download_hcp_wm_physio.py") `
    -AllowedExitCodes @(0, 2)

Invoke-Paper8Step `
    -Label "E1-E6 HCP measured-physiology ladder smoke" `
    -Script (Join-Path $Root "scripts\paper8_e1_e6_hcp_physio_ladder.py") `
    -AllowedExitCodes @(0, 2)

Invoke-Paper8Step `
    -Label "current figure generation" `
    -Script (Join-Path $Root "scripts\make_paper8_figures.py")

Invoke-Paper8Step `
    -Label "P8-v2 signal-separation audit" `
    -Script (Join-Path $Root "scripts\paper8_v2_signal_separation_audit.py")

Invoke-Paper8Step `
    -Label "P8-v2 figure generation" `
    -Script (Join-Path $Root "scripts\make_paper8_v2_figures.py")

Invoke-Paper8Step `
    -Label "P8-final ds005795 manifest audit" `
    -Script (Join-Path $Root "scripts\paper8_final_extension_ds005795_manifest_audit.py")

Invoke-Paper8Step `
    -Label "P8-final ds005795 small physiology/BOLD smoke download" `
    -Script (Join-Path $Root "scripts\paper8_final_extension_download_ds005795_smoke.py") `
    -Arguments @("--subjects", "sub-01", "sub-02", "sub-03", "--task", "learning")

Invoke-Paper8Step `
    -Label "P8-final ds005795 physiology timing parse smoke" `
    -Script (Join-Path $Root "scripts\paper8_final_extension_parse_ds005795_physio_smoke.py")

Invoke-Paper8Step `
    -Label "P8-final ds005795 TR-aligned physiology feature smoke" `
    -Script (Join-Path $Root "scripts\paper8_final_extension_build_ds005795_physio_features.py") `
    -Arguments @("--subjects", "sub-01", "sub-02", "sub-03", "--task", "learning")

Invoke-Paper8Step `
    -Label "P8-final ds005795 nuisance-ladder interface smoke" `
    -Script (Join-Path $Root "scripts\paper8_final_extension_ds005795_nuisance_ladder_smoke.py") `
    -Arguments @("--subjects", "sub-01", "sub-02", "sub-03", "--task", "learning")

Invoke-Paper8Step `
    -Label "P8-final ds005795 streaming measured-physiology ladder over all manifest-available learning subjects" `
    -Script (Join-Path $Root "scripts\paper8_final_extension_ds005795_streaming_ladder.py") `
    -Arguments @("--subjects", "sub-01", "sub-02", "sub-03", "sub-04", "sub-05", "--task", "learning")

Invoke-Paper8Step `
    -Label "P8-final ds005795 streaming figure generation" `
    -Script (Join-Path $Root "scripts\make_paper8_ds005795_streaming_figure.py")

Invoke-Paper8Step `
    -Label "P8 manuscript PDF preview generation" `
    -Script (Join-Path $Root "scripts\paper8_make_manuscript_pdf.py")

Invoke-Paper8Step `
    -Label "E8 claim audit" `
    -Script (Join-Path $Root "scripts\write_paper8_claim_audit.py")
