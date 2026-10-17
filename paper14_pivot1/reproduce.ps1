param([string]$Python = "C:\Users\85993\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe")
$ErrorActionPreference = 'Stop'
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    & $Python -m paper14_pivot1.reproduce
    if ($LASTEXITCODE -ne 0) { throw "Saved-only reproduction failed: $LASTEXITCODE" }
} finally {
    Pop-Location
}
