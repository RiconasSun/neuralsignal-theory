param([string]$Python = "", [string]$Revision = "r2")
$ErrorActionPreference = 'Stop'
if (-not $Python) {
    $localCandidate = Join-Path $env:USERPROFILE 'AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $localCandidate) { $Python = $localCandidate }
    else { $Python = (Get-Command python -ErrorAction Stop).Source }
}
& $Python (Join-Path $PSScriptRoot 'verify_saved.py') --revision $Revision
if ($LASTEXITCODE -ne 0) { throw 'Saved metadata or proposed-protocol verification failed' }
& $Python -m unittest discover -s $PSScriptRoot -p test_contract.py -v
if ($LASTEXITCODE -ne 0) { throw 'Synthetic/metadata regression failed' }
Write-Output 'Saved-only metadata reproduction PASS. No neural fitting or protocol activation.'
