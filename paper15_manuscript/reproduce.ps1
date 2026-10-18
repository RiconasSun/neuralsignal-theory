param([string]$Python = '')
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repo
if (-not $Python) { $Python = Join-Path $PSScriptRoot 'work/render-runtime/Scripts/python.exe' }
if (-not (Test-Path -LiteralPath $Python)) { throw 'Document Python environment missing. Install pinned paper15_manuscript/requirements.txt and pass -Python. This command never downloads neural data or runs scientific workers.' }
if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'CANDIDATE.json'))) { throw 'Frozen publication candidate missing. Authoring revisions must be rebuilt,reviewed and frozen before saved reproduction can certify them.' }
$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
& $Python -m paper15_manuscript.build
if ($LASTEXITCODE -ne 0) { throw "Saved-only manuscript reproduction failed with exit $LASTEXITCODE" }
