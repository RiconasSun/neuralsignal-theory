param(
    [string]$Run = 'paper12_sciencefinal1/results/final',
    [string]$Python = 'python',
    [string]$PdfPython = (Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe')
)
$ErrorActionPreference = 'Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    & $Python -B -m unittest paper12_sciencefinal1.test_trusted_host paper12_sciencefinal1.public_scientific_tests.PublicScientificTests
    if ($LASTEXITCODE -ne 0) { throw 'Public synthetic numerical/transport regressions failed' }
    & $Python -B -m paper12_sciencefinal1.trusted_host reproduce --run $Run
    if ($LASTEXITCODE -ne 0) { throw 'Saved scientific reproduction failed' }
    if (-not (Test-Path -LiteralPath $PdfPython -PathType Leaf)) { throw 'Recorded PDF Python runtime is unavailable; supply -PdfPython with ReportLab/PyPDF.' }
    $Marker = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/plugins/openai-primary-runtime/plugins/pdf/skills/pdf/container_tools/mark_artifact_operation_started.mjs'
    if (-not (Test-Path -LiteralPath $Marker -PathType Leaf)) { throw 'Recorded PDF operation marker is unavailable.' }
    $Stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffffff')
    $Out = Join-Path $PSScriptRoot ('work/artifact_reproduction_' + $Stamp)
    & node $Marker --operation-kind create --expected-output-count 6 --output-format pdf
    if ($LASTEXITCODE -ne 0) { throw 'PDF operation registration failed' }
    & $Python -B -m paper12_sciencefinal1.reporting --run $Run --output-newdir $Out
    if ($LASTEXITCODE -ne 0) { throw 'Saved manuscript/figure generation failed' }
    & $PdfPython -B (Join-Path $PSScriptRoot 'render_pdf.py') --directory $Out
    if ($LASTEXITCODE -ne 0) { throw 'Saved PDF generation failed' }
    Write-Output ('SAVED_ONLY_ARTIFACT_REPRODUCTION_PASS ' + $Out)
} finally { Pop-Location }
