$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Workspace = Split-Path -Parent $Root
$Python = Join-Path $Workspace "paper1\.venv\Scripts\python.exe"

& $Python (Join-Path $Root "scripts\run_paper4_e1_e8.py")
