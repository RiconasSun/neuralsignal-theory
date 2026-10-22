param([string]$Manifest = '')
$ErrorActionPreference = 'Stop'
$taskRepo = Split-Path -Parent $PSScriptRoot
$taskPython = Join-Path $taskRepo 'paper16_m1/work/runtime/Scripts/python.exe'
$taskScript = Join-Path $taskRepo 'ops/evidence/2026-10-21/p16-m3-m5-shutdown-recovery-r5/reproduce_saved.py'
$taskExpectedManifest = Join-Path $PSScriptRoot 'LOCAL_ARCHIVE_MANIFEST.json'
if (-not (Test-Path -LiteralPath $taskPython -PathType Leaf) -or -not (Test-Path -LiteralPath $taskScript -PathType Leaf)) {
    throw 'Registered local runtime or saved-only tool is missing'
}
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $taskPython).Hash.ToLowerInvariant() -ne 'de13d8017f63cb63b0b5bfd2f25e69245c9196433a224856ca1abde1e24d0cb7') {
    throw 'Registered local Python launcher identity changed'
}
if ($Manifest) {
    if ($Manifest.StartsWith('\\') -or $Manifest.StartsWith('//')) { throw 'UNC manifests are forbidden' }
    $taskCandidate = if ([System.IO.Path]::IsPathRooted($Manifest)) { $Manifest } else { Join-Path $taskRepo $Manifest }
    if ([System.IO.Path]::GetFullPath($taskCandidate) -ne [System.IO.Path]::GetFullPath($taskExpectedManifest)) {
        throw 'Only the exact closed local R5 archive manifest is accepted'
    }
}
if (-not (Test-Path -LiteralPath $taskExpectedManifest -PathType Leaf)) { throw 'Closed archive is not available; active work cannot be reproduced' }
Push-Location -LiteralPath $taskRepo
try {
    $taskArgs = @('-B', $taskScript, '--manifest', $taskExpectedManifest)
    & $taskPython @taskArgs
    if ($LASTEXITCODE -ne 0) { throw "Saved-only verification failed, exit=$LASTEXITCODE" }
} finally { Pop-Location }
