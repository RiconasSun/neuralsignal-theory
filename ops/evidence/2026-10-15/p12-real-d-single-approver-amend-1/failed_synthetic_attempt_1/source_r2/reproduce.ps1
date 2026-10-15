param([string]$Python='', [switch]$Synthetic, [string]$Attempt='')
$ErrorActionPreference='Stop'
if (-not $Python) {$Python=(Get-Command python -ErrorAction Stop).Source}
$taskRoot=Split-Path $PSScriptRoot -Parent
Push-Location $taskRoot
try {
    if ($Synthetic) {
        if (-not $Attempt) {$Attempt=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds().ToString()}
        & $Python -B -m paper12_singleowner1.run_synthetic $Attempt
    } else { & $Python -B -m paper12_singleowner1.reproduce_saved }
    if ($LASTEXITCODE -ne 0) {throw "P12 production engineering reproduction failed: $LASTEXITCODE"}
} finally {Pop-Location}
