$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$bundledPython = 'C:\Users\85993\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe'
if (Test-Path -LiteralPath $bundledPython) { $python = $bundledPython } else { $python = (Get-Command python -ErrorAction Stop).Source }
Push-Location -LiteralPath $repoRoot
try {
    & $python -W error -m paper14_native1.reproduce
    if ($LASTEXITCODE -ne 0) { throw "Saved canonical-native reproduction failed: $LASTEXITCODE" }
} finally { Pop-Location }
