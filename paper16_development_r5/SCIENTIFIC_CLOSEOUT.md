# P16 R5 scientific closeout

Mission: P16-M3-M5-SHUTDOWN-RECOVERY-R5. Execution BASE: `b7bb1227379462c2c7a1cef40ab0d0e99a6d020b`.

Scientific verdict: **STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE**. Complete M4 is not accepted. E, Final C/D, M6 and P17 remain unauthorized and unexecuted. This document supersedes the initial in-progress status in CURRENT_HANDOFF.md, which is retained unchanged as historical evidence.

## Phase A

The original, unextended 24-hour preflight gate passed before any new A fitting. Primary and independent saved-state checks admitted 3,992 historical optimizer states (952 R3, 3,040 R4) and 216 analytic B0 certificates. R3 `ftol=1e-12` and R4 `ftol=0` origins remain explicit. No failed, incomplete or diagnostic endpoint was admitted.

The accepted production source/test freeze is PREFIT_FREEZE_MANIFEST_V3.json (SHA256 `e0a1aa9979b6e4c998fb2d12553763af7317b3e8268f60a360772543b9d86bb4`). The exact independent approval is the evidence folder's PREFIT_APPROVAL.json, backed by PREFIT_REVIEW_3.md and native certification 6: 64 tests passed, no errors, failures or skips. Earlier unsuccessful tooling attempts, certifications, source snapshots and reviews are preserved; their results are not substituted by the successful attempt.

## Original Phase B and interruption

Exactly one 48-hour A/M4 stage was claimed, SHA256 `bd9516949e54d746371a9e4662ef29d63fe1997420f5dd1beafe2f8072f5315c`, starting 2026-10-21T17:25:31.796190+00:00 with the unchanged deadline 2026-10-23T17:25:31.796190+00:00. The original ordered task list, initializer, solver policy, bounds, seeds, lambda, PG, AD and fixed-step FD thresholds were unchanged. There was one scientific worker and no scientific retry or stage restart.

After an operator environment/monitoring interruption, native Windows inspection found the original supervisor, worker and independent observer absent, with no matching scientific module processes. The exact original named Job was also absent (`OpenJobObjectW` error 2); no termination request was necessary. The boot identity was unchanged, which does not establish the cause of process loss.

The original worker did not leave SCIENTIFIC_STOP.json, SUPERVISION.json, SUPERVISOR_FAILURE.json or WORKER_COMPLETE.json. None is fabricated. Exact native exit code, interruption time and cause remain unknown. The separately registered external closeout is EXTERNAL_CLOSEOUT_REGISTRATION_1.json; the immutable snapshot is EXTERNAL_INTERRUPTION_SNAPSHOT.json; the external stop receipt is the evidence folder's EXTERNAL_SCIENTIFIC_STOP.json.

The latest saved file modification timestamp is 2026-10-21T20:24:18.401433+00:00. This is a persisted-file timestamp, not an exact interruption time. The native absence observation is recorded separately at 2026-10-22T00:46:03.1537071Z.

## Exact task reconciliation

| New R5 work | Count |
|---|---:|
| Frozen planned tasks | 2,479 |
| Actual ordered attempts | 625 |
| Completed numerical passes | 624 |
| Recorded numerical failures | 0 |
| Incomplete attempts | 1 |
| Unattempted tasks | 1,854 |
| Completed states independently qualified before interruption | 624 |

The partial task is `774672366:S01:D:None:11:GLOBAL` with 339 parameters. Its original initializer and partial logs are retained. It has no RESULT.json, DIAGNOSTICS.json, endpoint.npz or completed derivative certificate. Its 482 reserved/482 completed FG receipts and 460 accepted iterations do not establish numerical acceptance. The partial vector is not a reusable endpoint or warm start.

All 624 completed states had already received the original independent coordinate/journal checks. The external integrity review verified their 6,864 attested file hashes and original completion/initializer/token joins without new model calls, NPZ decoding or repeated numerical certification. Their saved maximum PG is 1.9994999633375816e-6 (gate 1e-5), AD scaled error 5.773159728050814e-15 (gate 1e-8), and fixed-FD error 4.914744457761022e-11 (original h=1e-5, gate 2e-5). These maxima describe the completed prefix only.

| Saved resource evidence | Completed prefix | Partial attempt |
|---|---:|---:|
| FG completed receipts | 149,629 | 482 |
| Accepted iterations | 140,627 | 460 |
| FD reservations | 1,069,824 | 1,176 |
| AD reservations | 1,872 | 1 |
| Analytic checkpoint reservations | 1,872 | 1 |

Partial diagnostic reservations are not completed derivative checks; their completed-call counts are unknown. No favorable finite-difference scale or solver-success flag replaced an original numerical acceptance rule.

## Scientific limits and preservation

The full M4 target remains 6,471 optimizer states and 216 B0 certificates. The 3,992 historical optimizer states were admitted for R5 reuse and 624 new completed states were independently qualified (4,616 completed/qualified states in total). The remaining 1,855 required tasks comprise the new partial attempt plus 1,854 unattempted tasks. This does not admit a complete M4 package. No complete M4 state/selection manifest, M4 approval, E entitlement or E result is created.

All R1–R4 STOPs, R3 failed evidence, R4 shutdown evidence, earlier partial states, source freezes, unsuccessful reviews and preflight attempts remain immutable. This process interruption is not a numerical-gradient defect, a biological result, a recovered historical PASS, or evidence that every remaining model would pass or fail. M4 numerical completion would itself not validate biological hypotheses, independent Final performance, CWP or NAP.

Only saved-evidence closeout is now permitted. Any further scientific computation requires a separate prospective owner authorization; this mission does not reuse or resume the partial attempt. Public transmission of the new private-derived payload requires separate approval of the exact proposed Git commit and file manifest. Protected neural arrays and credentials are excluded from that proposed publication.

## Reproduction and closure annexes

The saved-only PowerShell entry point is `powershell.exe -NoProfile -File .\paper16_development_r5\reproduce_saved.ps1`. It requires the complete local protected saved-state archive. Its actual execution receipt, final independent review, requirement verification and exact publication manifest are separate hash-bound closure annexes; executable exit status alone cannot turn an incomplete verification into PASS. A saved integrity PASS reproduces this STOP and cannot produce M4 scientific PASS or authorize E/Final.
