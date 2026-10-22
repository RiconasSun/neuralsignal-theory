# Primary audit stopped: historical journal schema mismatch

Mission: `P16-M3-M5-SHUTDOWN-RECOVERY-R5`.

The single actual primary pass stopped at the first optimizer target,
`726162197:MAIN:B1:951877136:None:0.01`, at 2026-10-21T16:51:16.546324Z.
Optimizer attempted/pass = 1/0; optimizer unattempted = 3,991; B0
attempted/pass = 0/0; B0 unattempted = 216. No later state audit or new
objective, derivative, optimizer, likelihood or score call was performed.

## Static cause

This is a verified audit-harness schema mismatch, not evidence that a required
original R3 artifact was lost or that the historical numerical state failed.

`paper16_development_r3/optimizer.py` lines 69–71 registers each original FG
reservation with event/call/iterations and each completion with
event/call/objective/gradient_inf. It does not write an x vector or a full
gradient into either FG journal entry. The original accepted vectors are
separately retained at lines 75–76; the three checkpoint parameter/gradient
vectors are retained by the original certificate writer at lines 20–48.

`PRIMARY_SAVED_AUDIT.py` line 93 unconditionally calls
`paper16_termination_feasibility1.reproduce.call_prefix`. That newer helper
requires reservation x and completion gradient vectors (its lines 28–30),
which are not fields in the original R3 FG schema. Therefore it raises
`Saved FG vector` on the first R3 reservation. This extra field requirement
was an implementation error in the primary harness.

The frozen R4 admission implementation's `audit_saved.exact_journal` checks
the original R3 scalar FG accounting, accepted-vector sequence and original
checkpoint association without asserting that R3 had R4's newer full-vector
FG journal. The original policy origins must remain distinct.

## Preservation and action boundary

Preserved: the registered primary source, registration, first ledger entries,
all four native launch logs, the first bootstrap stop receipt, and every
historical artifact. The fourth native log is the actual pass's failed
receipt. The older `PRIMARY_AUDIT_STOP.json` remains the first bootstrap
receipt and has not been overwritten.

No complete optimizer/B0 admission matrix or PASS result was produced. The
first state remains `UNADJUDICATED_HARNESS_SCHEMA_MISMATCH`, not admitted and
not declared scientifically defective. The independent reviewer must assess
the exact registered historical schema and any permissible affected-harness
repair before another execution decision. The primary auditor has not
modified the registered script or rerun the scientific audit after this
failure. No production or E/Final work is authorized by this classification.
