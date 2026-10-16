param([string]$Python = 'python', [string]$TablePython = '')
$ErrorActionPreference = 'Stop'
if (-not $TablePython) {
    $bundledTablePython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
    if (Test-Path -LiteralPath $bundledTablePython) { $TablePython = $bundledTablePython }
    else { $TablePython = $Python }
}
& $Python (Join-Path $PSScriptRoot 'verify_saved.py') --table-python $TablePython
if ($LASTEXITCODE -ne 0) { throw "KI/PFC saved-only reproduction failed: $LASTEXITCODE" }
