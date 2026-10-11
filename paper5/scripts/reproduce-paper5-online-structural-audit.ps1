$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Workspace = Split-Path -Parent $Root
$Python = Join-Path $Workspace "paper1\.venv\Scripts\python.exe"

& $Python (Join-Path $Root "scripts\audit_openneuro_structural_metadata.py") --dataset ds001635 --dataset ds001634 --dataset ds004469
& $Python (Join-Path $Root "scripts\run_paper5_e1_e8.py")
