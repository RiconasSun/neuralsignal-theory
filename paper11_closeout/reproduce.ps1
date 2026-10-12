param(
    [string]$Python = 'C:/Users/85993/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe',
    [string]$PdfPython = 'C:/Users/85993/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Python) -or -not (Test-Path -LiteralPath $PdfPython)) {
    throw 'Required local Python runtime absent; provide -Python and -PdfPython. No network or simulated-data fallback.'
}
& $Python (Join-Path $PSScriptRoot 'reproduce.py') --pdf-python $PdfPython
if ($LASTEXITCODE -ne 0) { throw 'Saved-only manuscript reproduction failed; original scientific failures remain unchanged.' }
