# Dynamics numerical recovery — saved-evidence closeout

Closeout mission: P12-M4-DYNAMICS-NUMERICAL-RECOVERY-1-CLOSEOUT.
Original mission: P12-M4-DYNAMICS-NUMERICAL-RECOVERY-1. Base e635724f2aae45b7fdf30edb5902beaab425b8e2.
Scientific result remains FAIL / NUMERICAL_INCONCLUSIVE. This is a stopped-evidence archive, not model recovery or scientific validation.

## Exact reconciliation

Original-budget diagnosis completed 216 exact replays, 6 converged and 210 nonconverged, with no independent numerical check failure. Fixed dynamics-only options were prospectively registered before the smoke: maxiter2000/maxfun80000/ftol1e-10/gtol1e-5. Architecture, objective, bounds[-8,8], ridge, seeds, PG<=.001 and independent gradient tolerance<=1e-5 were unchanged.

Smoke planned 216 attempts. Saved summary and 61 individual records establish 61 attempted AND completed fits, 59 converged, 2 nonconverged, 155 unexecuted. There is no evidenced interrupted fit. Discrete CA1 completed36/36 converged; Continuous CA1 completed25 with23 converged. Hybrid and all DG smoke attempts remain unexecuted. Native process completed with exit2, no timeout, role proof PASS/capabilities0 and cleanup0x00000000.

| Failed identity | Iterations | Solver success | PG | Independent terminal check | Disposition |
|---|---:|---|---:|---|---|
| CA1/Continuous/d2/ridge .001/seed11 | 1355 | true | .0016052460119657442 | PASS | Nonconverged under unchanged PG criterion |
| CA1/Continuous/d4/ridge .001/seed11 | 2000 | false | .692604771056502 | Error .00020676306270142608 >1e-5 | Mandatory numerical STOP |

The second record says TOTAL NO. OF ITERATIONS REACHED LIMIT, with zero active-bound hits. Independent objective discrepancy at that point was0; this does not validate its derivatives. The gradient discrepancy could reflect an analytical defect or numerical estimator instability; neither is diagnosed in closeout. The optimizer failure is separately preserved and is not cleared by any future gradient explanation alone.

## Preservation and evidence scope

Original_inventory.json records all original public untracked bytes and prior Stage B draft artifacts. The three stale narrative files have exact original copies under closeout_originals before correction. All actual failure, summary, receipt, protocol, registrations, model/controller sources and unsuccessful test/review records are retained unchanged. No models, synthetic derivative experiments or historical gradient tests are executed in this stage.

The early-stop code does not reach fitted_states.npz publication. Therefore saved smoke evidence DOES NOT contain an endpoint parameter-vector archive. It preserves exact scalar fields and objective/accepted-iteration histories. Stage B may reproduce the authorized single configuration to recover and verify vectors; no vector/hash identity is assumed here.

Training A only was available to the completed role. Saved flags report validation_access=false/final_access=false, no final neural analysis exposure/evaluation. These are historical role/receipt facts, not fresh live-isolation certification. M3=1638 fits and offsets=78 fits were reused; no closeout refits/extraction/source requests. Complete M4, M5/nulls and M6 remain NOT EXECUTED. Native continuity/anatomical/physiological caveats from the curated protocol remain unchanged.

## Defects, warnings and claims

Prior scientific evidence includes 2 nonconverged fits and 1 failed independent numerical check (overlapping the d4 fit); these are neither discarded nor repaired. The original model code has no established mathematical root cause. Scientific warning_count=1: unresolved numerical admission blocks competition. Closeout engineering counts may be bug_count0/warn_count0 only after complete audit/review/remote gate; this does not clear historical warnings.

No CA1/DG biological preference, NAP/CWP validation, mechanistic evidence, complete numerical recovery, full-cohort result, null result or final validation is claimed. One-command saved-only reproduction certifies bytes, recorded identities/cardinality, receipts and CSV parity; it does NOT execute or reproduce numerical fitting, derivative checks or unexecuted science.
