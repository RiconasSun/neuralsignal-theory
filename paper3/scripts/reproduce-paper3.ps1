$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Workspace = Split-Path -Parent $Root
$Python = Join-Path $Workspace "paper1\.venv\Scripts\python.exe"

& $Python (Join-Path $Root "scripts\run_paper3_e1.py")
& $Python (Join-Path $Root "scripts\run_paper3_e2_e8.py")
