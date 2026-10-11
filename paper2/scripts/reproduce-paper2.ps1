$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Python = Join-Path $Root "paper1\.venv\Scripts\python.exe"
$Runner = Join-Path $Root "paper2\scripts\run_paper2.py"

& $Python $Runner @args
