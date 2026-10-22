$ErrorActionPreference = 'Stop'
$taskFailure = Join-Path $PSScriptRoot 'INDEPENDENT_R5_M4_AUDIT_FAILURE_1.json'
$taskRepo = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$taskStop = Join-Path $taskRepo 'paper16_development_r5/results/SCIENTIFIC_STOP.json'
$taskDone = Join-Path $taskRepo 'paper16_development_r5/results/WORKER_COMPLETE.json'
$taskEnd = [DateTime]::UtcNow.AddSeconds(50)
while (-not (Test-Path -LiteralPath $taskFailure) -and
       -not (Test-Path -LiteralPath $taskStop) -and
       -not (Test-Path -LiteralPath $taskDone) -and
       [DateTime]::UtcNow -lt $taskEnd) {
    Start-Sleep -Milliseconds 200
}
if (Test-Path -LiteralPath $taskFailure) {
    Get-Content -Raw -LiteralPath $taskFailure
} else {
    Push-Location -LiteralPath $taskRepo
    try {
        $taskRaw = & '.\paper16_m1\work\runtime\Scripts\python.exe' -B -m ops.evidence.2026-10-21.p16-m3-m5-shutdown-recovery-r5.progress
        if ($LASTEXITCODE -ne 0) { throw 'Saved-only progress read failed' }
        $taskValue = $taskRaw | ConvertFrom-Json
        $taskValue | Select-Object attempted,completed,failed_journal_entries,active_task,active_FG_reserved,active_FG_completed,active_accepted_iterations,elapsed_seconds,scientific_stop,M4_ready,worker_complete | ConvertTo-Json -Compress -Depth 8
    } finally { Pop-Location }
}
