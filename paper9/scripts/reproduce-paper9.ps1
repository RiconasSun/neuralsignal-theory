$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PaperRoot = Split-Path -Parent $ScriptDir
$RepoRoot = Split-Path -Parent $PaperRoot

Set-Location $RepoRoot
python paper9/scripts/run_paper9.py
python paper9/scripts/finalize_paper9_submission.py
