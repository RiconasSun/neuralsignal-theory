# Independent C production review 1 — unsuccessful candidate1

Mission: P15-M6-INDEPENDENT-FINAL-VALIDATION. Reviewer: `/root/gradient_review`. Date: 2026-10-18 America/Los_Angeles. **Decision: REQUIRES_REPAIR; open_P0=0; open_P1=1; approved_selected_C_calibration=false.** This report certifies no real C fit or pre-D gate. Preserve it unchanged after repair.

Reviewed candidate1 SHA256: `0b65f1a982aa8353b01652a0b1a299f8b1ee2248d41f77c254356e9cc8d44668`, now preserved as C_PRODUCTION_CANDIDATE_ATTEMPT1.json in this evidence directory. The original127 file hashes and external identities were independently checked before implementation changed. C_PRODUCTION_REVIEW_CHECKS_1.json SHA256 `db53dc16019b33da5231b571c94cd9396c479fd917d36bb6f1fb81eab923aafc` retains that exact full map and source hashes.

## P1 — an ordinary sensitivity failure silently aborts all remaining registered evaluation

Candidate1 sensitivity_calibration.execute writes C_SENSITIVITY_REQUIRED_STOP and returns immediately for **any** completed NUMERICAL_FAIL. This includes an ordinary failed optional S02/S03 fit and prevents unrelated remaining fixed cases from being calibrated. The behavior is stricter than the frozen scientific reporting contract and silently removes its unavailable/descriptive paths.

STATISTICS_CONTROLS.md:30,41–42 makes S02/S03 capacity-conditional;:54 requires every missing sensitivity retained and states that mandatory sensitivity failures limit/withhold positive generalization. Its:13,24–25 defines positive-claim coverage separately for each relevant baseline contrast. SCIENTIFIC_PROTOCOL.md:39 requires all registered successes/failure certificates serialized before D; the owner explicitly permits the six/seven-mouse descriptive branch and requires failed/unavailable results reported. An ordinary completed sensitivity numerical failure is not equivalent to a critical source/implementation integrity failure or interruption.

An independent pure synthetic mocked control-flow probe executed the actual candidate1 sensitivity.execute with two planned fits: first an optional S02/B4 numerical failure, then S01. Admission,arrays,model and fit results were mocked explicitly; no real/synthetic likelihood or optimizer was called by this probe. It observed only one fit invocation and the global STOP marker; S01 was never attempted. This demonstrates the missing reporting branch without using actual C observations or D values.

Minimal contract-preserving repair: retain every completed failed fit as invalid with unchanged PG/AD/all-FD criteria,no retry/seed/optimizer replacement; continue the remaining original bounded sensitivity plan; mark the failed subject/case/family unavailable for the applicable fixed comparisons. Do not automatically erase a whole case if another relevant family pair remains valid. Mandatory-case insufficient C-valid coverage limits/withholds the corresponding positive generalization; optional capacity panels retain their conditional restriction. The complete pre-D review must freeze all actual successes/failures/common case cohorts and claims before D. No numerical failure may be relabeled PASS.

Critical source/state/implementation integrity error,unexpected exception or interrupted STARTED residue remains a STOP and cannot be diagnosed/repaired using D. This repair does not weaken such an essential gate or grant automatic D execution. A failed model-family C/D/S main calibration follows the original secondary unavailable/common-cohort rules and cannot shrink the primary cohort or use favorable seeds.

Importantly,the **main** baseline stop is correct: SCIENTIFIC_PROTOCOL.md:41 explicitly requires valid B0–B4 C states for every included primary mouse. Thus main B0/B2/B3 failures are not ordinary secondary-family failures; the owner's emphasis on B1/B4 does not repeal that complete primary gate. Do not weaken the existing main baseline STOP while repairing sensitivity behavior.

## Checked numerical/source components without another P0/P1

The unchanged pure mathematical model/feature/independent AD sources retain the accepted original equations,T normalization,ridge/intercept masks,bounds,float64,original initializers/seeds,L-BFGS-B budget and outward PG. fit_one uses current model.warm/delta for B0 and recorded score exposures,checks finite parameters/gradients/objective/masses,bounds,PG<=.001,independent AD/all FD steps and nonexhaustion;optimizer_success alone cannot pass. Exclusive durable STARTED creation prevents a second attempt. Actual arrays are tied to C states and hashes; global policies come from frozen R1 selection,not a new search or Development coefficients.

The reviewer independently ran37 synthetic production/control/feature/worker tests with ResourceWarning as error,single BLAS/OMP/MKL threads and bytecode disabled. All37 passed,including original24 gradient points,larger-state/bound checks,explicit HMM enumeration/IID,future/reset behavior,role-local C/D schedule isolation,actual synthetic fit_one and duplicate rejection. This does not cover the missing sensitivity failure branch and cannot clear the P1.

Both earlier failed37-test attempts and the documented test-only expected C-role RNG/workspace scratch repairs remain historical evidence. The independent successful run does not claim those earlier errors never occurred. No oracle/assertion was weakened to pass this review.

Current metadata/plans describe six eligible mice/four labs,72 main attempts and320 sensitivity attempts from66 records/64 available cases,with two S03 capacity panels unavailable. Prospective historical-inclusive count is1494+72+320=1886,not an already executed count. Six-mouse scope is DESCRIPTIVE ONLY regardless of later p-values. No real C fitting or D assessment has occurred.

This first review cycle did not certify numerical equivalence of all actual prepared C arrays; that independent actual-source/preparation work remains for repaired-candidate review,with the separate source/physiology review. No whole-recording neural source,D data,real likelihood,AD/FD or fit was accessed/executed here. Only synthetic tests/control-flow and saved source/plan/hash inspection were performed. No paper15_final1 source was edited by this reviewer.

Repair prospectively,preserve candidate1/old worker bytes/this unsuccessful review,add branch regressions and obtain a new exact candidate review before any real C fit. The receipt deliberately rejects calibration and retains the candidate1 map; it must not be changed into a later acceptance.
