# P11 Milestone Status

P11 - Hippocampal Dynamical Regime

| Milestone | Status | Evidence |
| --- | --- | --- |
| M0 | PASS | [frozen gate](results/M0/gate_result.json), unchanged |
| M1 | PASS | [gate](results/M1/gate_result.json), [QC](results/M1/qc_report.json), [tests](results/M1/tests.txt) |
| M2 | PASS | [gate](results/M2/gate_result.json), [coverage audit](results/M2/coverage_audit.json), [QC](results/M2/QC_REPORT.md) |
| M3 | PASS | [gate](results/M3/gate_result.json), [QC](results/M3/QC_REPORT.md), 483 candidates |
| M4 | FAIL | [gate](results/M4/gate_result.json), [QC](results/M4/QC_REPORT.md); integration accuracy not established |
| M5 | NOT_STARTED | Requires preceding gate and separate execution |
| M6 | NOT_STARTED | Requires preceding gate and separate execution |
| M7 | NOT_STARTED | Requires preceding gate and separate execution |

Eligible subjects: 9; no model comparison performed.
Scientific verdict: INCONCLUSIVE (numerical gate failure, not a neural-regime finding)
M0 protocol and frozen holdouts unchanged. Autonomous advancement authorized,
with the temporary M2 coverage failure resolved through the documented public
NEMAR annex remote. All 23 pinned masked NIX objects passed whole-file SHA256
and exact array inventory checks. Exposure follows the released trial convention,
not independently measured dropout masks. M3 completed; M4 stopped at smoke;
M5-M7 have not executed. No final holdout timestamp values decoded.
See [reproduction](REPRODUCE_M1.md).
See [M2 reproduction](REPRODUCE_M2.md) and [access evidence](results/M2/coverage_access_evidence.json).

At 1024 particles, the corrected single-run conservative discrepancy was
0.0014080063396446991 nats/unit-bin, above the frozen 0.001 threshold.
Budgets 64/256 also failed. No full-cohort regime comparison or final holdout
statistics exist. All 70 final regression tests passed; numerical FAIL remains.
Continuation requires a documented prospective numerical-method amendment,
not routine milestone approval or a relaxed criterion after seeing this outcome.

## Latest M3/M4 Requested-Scope Audit

Saved-output audit: [gate](results/M3_M4_scope_audit/gate_result.json),
[tables and diagnostics](results/M3_M4_scope_audit/QC_REPORT.md).
483 session/candidate rows; 189 subject/candidate rows (9 subjects x21 fixed
candidates; equal session weight within subject). Forty corrected-run smoke
seed fits, four exact HMM validation configurations. Continuous accuracy FAIL;
hybrid not run, not silently excluded or counted as losing.
Requested B0 matches constant Poisson; B1 matches rate/history. Existing task
and timing are separate, so joint B2 is not executed under the frozen grid.
Own-unit five-lag log1p-history ridge-Poisson fits can cover that specific B3
definition, not cross-unit/raw-count AR. Scientific amendment decisions pending.
Report reproduction does not upgrade any milestone gate. No M5-M7 execution.
