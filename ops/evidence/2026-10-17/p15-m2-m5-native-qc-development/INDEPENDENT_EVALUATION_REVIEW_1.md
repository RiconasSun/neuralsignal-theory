# Independent internal E integration review 1

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Review date: 2026-10-18 UTC.

Decision: **REPAIR_REQUIRED_BEFORE_E_ACCESS**. Open P0: 0. Open P1: 3. Preserve this unsuccessful review. No actual B/E/Final neural observation, score, source/network request, raw cache or real fit was accessed or executed by this reviewer. Only this new review artifact was written. Running unchanged A fits are outside this new integration review.

## P1-01: the pre-E gate does not close the complete sensitivity-state dependency set

`verify_E_gate` requires aggregate preparation/plan/attempt receipts and verifies the listed fit files, but it does not require or verify all original subject x eleven case state files before E access, including unavailable case states. It also does not invoke the existing full `verify_plan` subject/case/ridge/budget reconciliation. Some state/gate checks occur only later in score_case, after E has already been loaded. An unavailable case has no fit receipt at all, so its identity/reason is not closed by the present attempt-only checks. Missing or altered state/mask/unit/scaler information can therefore be discovered after the one-shot boundary instead of preventing release.

Required narrow repair: before the E claim or any E neural load, verify the exact frozen subject/case denominator, all state hashes and status/reasons, complete registered plan correspondence and all completed fit/gate/state identities. Include mandatory bindings for every case, including unavailable states, rather than accepting only whichever files an optional hash map happens to contain. Bind the other load-bearing main-source/preprocessing/attempt markers through their registered hash closure. Do not fabricate unavailable states or weaken their coverage requirements.

Required synthetic tests: omitted/altered available case, omitted/altered unavailable case, incomplete subject/case preparation, plan/ridge mismatch, interrupted/mismatched fit, stale completion hash and valid complete closure. Every denied case must perform zero E neural I/O and consume no E batch claim.

## P1-02: control progress and failed-suite evidence are lost before the per-mouse write

`run_controls` holds all suite/replicate results only in memory and returns after all four suites complete. `run` writes a mouse's control file only after that return. If a later replicate/suite fails, completed earlier replicates and even complete earlier suites for that mouse disappear; only the outer batch error survives. There is no durable failed-suite/replicate receipt or preserved prefix seed/mapping/result history. Because the E claim correctly forbids rerunning, that lost evidence cannot be reconstructed by a permitted resume.

I independently injected a failure on the second reference call after the first synthetic replicate completed. The exception propagated, but the number of durable write calls inside run_controls was zero. This confirms a preservation gap; the existing arithmetic tests do not exercise it.

Required narrow repair: durable append-only per-mouse/suite progress with START/COMPLETE/FAILED context, replicate ordinal, seed, mapping identity and completed results before advancing. Preserve all completed prefix evidence and the exact failure location. A crash residue or failure still denies another batch; do not implement resume, replacement draws or retuning. Test failure after a completed prefix, crash residue, concurrent/duplicate E claims and preservation of previous successful suites.

## P1-03: control bundles include an unregistered eighth model

FrozenPredictors contains the selected B0 as well as B1-B4,D,C,S. For N1/N2/N4, run_controls calls its score method with families=None, so a fully available bundle also evaluates B0. The frozen control definition names B1-B4,D,C,S and limits each bundle to up to seven models. B0 adds no registered contrast and need not be evaluated for these controls. Although N3's two-model restriction can keep the aggregate work below the 28x999 ceiling, it does not make the eight-model bundle conform to the registered operator set.

Required repair: restrict N1/N2/N4 control scoring explicitly to the seven registered families, preserving every available family and the shared realization. Keep main original-result B0 reporting unchanged. Add a synthetic model-call audit proving no B0 control evaluation, at most seven models per bundle, N3 only B1/B4, and no extra random draw for an additional contrast.

## Contract-consistent surfaces reviewed

The new worker checks stage prerequisites before an exclusive fsynced E_BATCH_CLAIM. Existing STARTED/completed/failed claims deny another batch; no retry or optimizer is introduced. The ten fixed selected subjects drive the main, eleven-case and control loops. Primary statistics receive selection['subjects'] as the expected cohort. Missing secondary families preserve fixed slots rather than retuning. Final source access is rejected by the Development source-state boundary.

The source constructs N2's strict-past wheel magnitude over epochStart-.5 to epochStart, with the median estimated from A-only valid epochs; E wheel values are metadata, not neural outcome tuning. It freezes control coverage from task/wheel metadata before E. Donor control arrays retain original targets/task, rebuild past-only neural history and C state from surrogate counts, and pass surrogate past counts to the D filter. N3 replaces only design columns24-37 inclusive, retains original neural/C streams, evaluates B1/B4 and labels the B4-LL wheel diagnostic copied across correction slots. Those labels do not imply D/C wheel-null evidence.

Reference summary uses the fixed 999-replicate plus-one calculation, equal-mouse common exposures and four-slot Holm correction per contrast, with unavailable panels p=1. Sensitivity summary reports only baseline-derived primary/own/other contrasts and does not borrow baseline sensitivities as D/C/S robustness. All computed labels remain exploratory/validated=false. These source observations do not certify an actual scientific suite or remove the three findings above.

## Fresh independent verification and identities

Executed `paper15_dev/work/runtime/Scripts/python.exe -W error::ResourceWarning -m unittest paper15_dev.test_evaluation -v`: **10 tests PASS**, exit0. These cover surrogate history/C construction, D past filtering, wheel-only substitution, seed pre-bin mixture, strict-past wheel, effect slots/Q mismatch, reference pseudocount/Holm, sensitivity unavailability and basic access denial. The additional injected-prefix failure check above exposed missing durable evidence; no real assessment ran.

| File | SHA256 |
|---|---|
| paper15_dev/evaluation.py | 6d9827ab9b55963f76e77ef51b2dfc3b0ae18198cd9bfc7cb42efe95850379ba |
| paper15_dev/evaluation_support.py | 01fe5bf8fb3000f4d53cf8b133de23ea6d2f26c2a82b00a07d93e500fd9062a8 |
| paper15_dev/test_evaluation.py | 38f198fba2e623154bab437dda06d478a7384c209b27f85550141cb1ca50944b |

Do not create an executable E-release gate or run the real batch until the repaired full candidate and actual preceding fit/selection/sensitivity evidence pass independent review. No historical source, numerical failure or scientific threshold is reclassified by this report.
