$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PaperRoot = Split-Path -Parent $ScriptDir
$RepoRoot = Split-Path -Parent $PaperRoot

Set-Location $RepoRoot
python paper10/scripts/run_paper10.py
