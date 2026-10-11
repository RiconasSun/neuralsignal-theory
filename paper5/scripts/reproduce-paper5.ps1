$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Python = "python"

Write-Host "Paper 5 reproduction: HCP-YA 2025 structural proxy pipeline"
Write-Host "Requires authorized HCP/BALSA S3 credentials in paper5/.secrets."

& $Python (Join-Path $Root "scripts\hcp_s3_download.py") --subjects 100 --fast-template --download --workers 8
& $Python (Join-Path $Root "scripts\hcp_smoke_validate.py")
& $Python (Join-Path $Root "scripts\hcp_e2_e3_smoke_states.py")
& $Python (Join-Path $Root "scripts\hcp_e4_e8_structural_proxy.py") --seeds-per-parcel 60 --n-perm 10000 --rebuild-connectomes
