# P11 Milestone Status

P11 - Hippocampal Dynamical Regime

| Milestone | Status | Evidence |
| --- | --- | --- |
| M0 | PASS | [frozen gate](results/M0/gate_result.json), unchanged |
| M1 | PASS | [gate](results/M1/gate_result.json), [QC](results/M1/qc_report.json), [tests](results/M1/tests.txt) |
| M2 | PASS | [gate](results/M2/gate_result.json), [coverage audit](results/M2/coverage_audit.json), [QC](results/M2/QC_REPORT.md) |
| M3 | PASS | [gate](results/M3/gate_result.json), [QC](results/M3/QC_REPORT.md), 483 candidates |
| M4 | FAIL | [gate](results/M4/gate_result.json), [QC](results/M4/QC_REPORT.md); integration accuracy not established |
| M4-NUM-1 | FAIL | [amended gate](results/M4_amendment1/gate_result.json), [numerical audit](results/M4_amendment1/numerical_audit.json); original failure preserved |
| M4-NUM-2 | FAIL | [proposal oracle gate](results/M4_amendment2/gate_result.json); no revised real-data evaluation activated |
| M4-NUM-3 | FAIL | [controlled gate](results/M4_amendment3/gate_result.json), [numerical limitations](results/M4_amendment3/NUMERICAL_LIMITATIONS.md); remediation stopped |
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

## Authorized Numerical Remediation
M4-NUM-1 registered before revised evaluation; numerical threshold remains0.001.
Candidate particles2048/4096/8192; eight repetitions; references16384/32768,
eight repetitions. Original M0-M3 gates, splits and results/M4 unchanged.
First continuous d1 diagnostic passed at4096, discrepancy0.0007312952775541941;
this is partial numerical progress only. Continuous d2 failed at8192:
discrepancy0.0016818397769194165 >0.001, reference uncertainty0.0003261110384436511.
48 smoke seed fits converged (40 reused with checksum checks,8 freshly trained).
Whole grid/cohort incomplete; d3/Hybrid/M5-M7 not executed after failed gate.
Final holdout remains locked. See REPRODUCE_M4_AMENDMENT1.md and the separate
results/M4_amendment1 directory; original scientific verdict remains INCONCLUSIVE.

## NUM2 Proposal Oracle Stop
Implemented observation-guided defensive Laplace importance proposal with exact
ancestor-transition/mixture-q correction and explicit initial/state correction.
13 formula/fail-fast tests pass. Controlled oracle gate FAIL at first fixed
K1/D2 seed1103: maximum per-bin error0.001736609669442446 nats/unit-bin.
No real NUM2 evaluation, registration activation or full cohort follows failure.
Original pre-fail-fast collection (16 replicas,12 failures) and source preserved
under results/M4_amendment2/attempts/initial-collection. Corrected runner stops
on the first failure; no budgets/seeds/thresholds changed. Five scientific gaps
remain open. This is a controlled-fixture numerical limitation, not a new
hippocampal PLDS finding. See REPRODUCE_M4_NUM2.md and separate QC_REPORT.md.

## NUM3 Numerical Feasibility Stop
Prospectively registered independent GH32/48/64 and GL64/96/128 oracles,
scrambled-Sobol guided importance evaluation, budgets8192/32768/131072 and16
fixed repetitions. Initial engineering interruption and lock preserved; r2
corrected equivalent inverse-CDF memory usage and enforced final source identity,
without any numerical-policy change. First mandatory original K1/D2 fixture:
oracle sensitivity9.436895781820573e-15 (not certified absolute error);
final worst-bin acceptance statistic0.0011686586847694219 >0.001.
Raw maximum bin error0.0006401831552509396; trial statistic0.00033673041189710744.
The additional registered per-bin uncertainty criterion failed, not the trial-mean
statistic. No substitution of a favorable endpoint after failure.14/14 focused,
111/111 full regression and6/6 saved-artifact tests PASS. Numerical PowerShell
and saved audit exit1 at the preserved FAIL. No later fixture, real neural
evaluation, full M4 competition or M5-M7. Final holdout remains locked.
Five scientific warnings OPEN. M4 remains INCONCLUSIVE; this does not prove
0.001 infeasible for every numerical method. See REPRODUCE_M4_NUM3_AUDIT.md.
