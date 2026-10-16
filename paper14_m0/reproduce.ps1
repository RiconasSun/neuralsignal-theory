param([string]$Python = '')
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
if (-not $Python) {
    $bundled = 'C:\Users\85993\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $bundled) { $Python = $bundled } else { $Python = 'python' }
}
$previous = Get-Location
try {
    Set-Location -LiteralPath $root
    & $Python -m paper14_m0.reproduce
    if ($LASTEXITCODE -ne 0) { throw "Saved-only reproduction failed with exit $LASTEXITCODE" }
} finally { Set-Location -LiteralPath $previous }
