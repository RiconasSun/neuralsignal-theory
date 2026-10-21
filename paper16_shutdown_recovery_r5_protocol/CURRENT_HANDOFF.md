# Current R5 protocol handoff

This is a new protocol-only draft based on 5ed9a6854248cd250a097a9e657519ad0a057f64, not recovery execution. Historical ops/daily-operations.md and all R4 sources/reports remain unchanged.

Read PROSPECTIVE_MISSION.md and PROPOSED_EXECUTION_POLICY.json. Proposed future limits are24h saved-only audit/certification +48h new A/M4 stage, one optimizer worker,2479 attempts,6000 FG/1500 accepted iterations per attempt, original PG/AD/fixed-FD rules. Every new task starts from the original initializer. All3992+216 reuse targets are pending new independent admission, not admitted here. M4 must be complete and independently accepted before a separate E request; no automatic E and no Final.

Current checks are public-BASE JSON/hash/task-set consistency only. They do not perform private saved-state audit, model computation, numerical certification or scoring. One command from the repository root at this protocol candidate:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\paper16_shutdown_recovery_r5_protocol\VERIFY_PROTOCOL.ps1
```

Independent protocol review actually accepted ACCEPTED_PROSPECTIVE_PROTOCOL_ONLY, with technical bug_count/warn_count=0/0; future reuse/numerical gates remain NOT_EXECUTED. Git receipts must still actually complete before delivery and are retained in ignored evidence LOCAL_ONLY to avoid commit self-hashes. After reviewed protocol handoff, STOP. Future execution requires separate explicit owner authorization tied to the final protocol commit. Prior permission to push the169-file R4 archive is not numerical-execution permission. This draft contains only new protocol text and indices of already-public BASE metadata; any later private-derived results retain a separate publication boundary.
