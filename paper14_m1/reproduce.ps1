param([string]$Python = '')
$ErrorActionPreference = 'Stop'
if (-not $Python) {
    $bundled = 'C:\Users\85993\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $bundled) { $Python = $bundled } else { $Python = 'python' }
}
$previous = Get-Location
try {
    Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
    & $Python -m paper14_m1.reproduce
    if ($LASTEXITCODE -ne 0) { throw "Saved-only checkpoint reproduction failed: $LASTEXITCODE" }
} finally { Set-Location -LiteralPath $previous }
