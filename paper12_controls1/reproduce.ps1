param([ValidateSet('Saved','Synthetic','SavedSynthetic')][string]$Mode='Saved',[string]$Python='')
$ErrorActionPreference='Stop'
if (-not $Python) {$Python=(Get-Command python -ErrorAction Stop).Source}
$env:PYTHONDONTWRITEBYTECODE='1'
if ($Mode -eq 'Saved') {& $Python (Join-Path $PSScriptRoot 'reproduce_saved.py')}
elseif ($Mode -eq 'Synthetic') {& $Python (Join-Path $PSScriptRoot 'reproduce_synthetic.py')}
else {& $Python (Join-Path $PSScriptRoot 'reproduce_saved_synthetic.py')}
if ($LASTEXITCODE -ne 0) {throw "Prerelease controls reproduction failed: $LASTEXITCODE"}
