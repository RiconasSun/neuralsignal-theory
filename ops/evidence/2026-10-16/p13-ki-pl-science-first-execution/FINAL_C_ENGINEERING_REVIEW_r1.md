# Independent C-only and sensitivity engineering review r1

Mission: `P13-KI-PL-SCIENCE-FIRST-EXECUTION`.
Reviewed UTC: 2026-10-16T16:50:10Z.
Reviewer: separate local reviewer agent; independent internal scientific/evidence/code review, not external peer review.
Decision: **REQUEST_CHANGES — SENSITIVITY ALIGNMENT ASSEMBLY**.
Open P0: **0**. Open P1: **1**.

No additional P0/P1 was identified in the C-calibration portion at its stated engineering scope. The combined frozen engineering candidate is not accepted until the alignment contract below is repaired. **No actual C fit, real control execution or D release is approved.** Independently completed E-control results and actual frozen C inputs still require the separately requested later pre-execution review.

## Candidate and fresh synthetic evidence

Verified `paper13_ki_execution1/FINAL_C_ENGINEERING_FREEZE.json` SHA256 **2213ec50a542ee640d3e80a9bf6fe2d0b3dcf536b5353a4db917044ba66627d0** and all **103** immutable hashes. Its scope correctly excludes growing E-control outputs and states that it is not actual calibration/release approval.

Read `final_C.py`, `sensitivity_scores.py`, `sensitivity_plan.py`, `descriptive_metadata.py`, focused tests, prospective sensitivity registration and current engineering verifier. Fresh `& .\paper13_ki_execution1\reproduce_final_C_engineering.ps1` returned exit **0**, **124 tests PASS**, with **103 current +85 original hashes** verified. The command performs synthetic tests only, including five C-worker tests and four sensitivity-assembly tests; no real C fit, new real control replicate or D outcome is accessed by it. The preliminary old C verifier/reproducer is outside the current accepted command and is not treated as final evidence. At review inspection, `FINAL_C_APPROVAL.json` and `results/FINAL_C_GATE.json` do not exist.

## P1 — Aligned data are not bound to the planned pre-tone bin/epoch dimensions

Evidence: `paper13_ki_execution1/sensitivity_scores.py:29-34`. The code checks that a supplied parent-ordinal list equals the retained planned ordinals, but then passes `supplied['counts']` and `supplied['q']` directly to `cell()`. It never checks that their epoch-row count equals that list or that their time dimension equals each plan's `observed_full_bins`/pre-tone export bound. The pure evaluator legitimately supports multiple T values, so it does not enforce this alignment-specific restriction instead.

The frozen protocol (`PROPOSED_P13_V2.md:80`) and prospective sensitivity registration require the +100-ms shifted window to exclude the tone-response bin: normally **29 full bins, five warm-up, 24 scored**. Accepting 30 bins under the same valid plan allows an extra post-tone scored bin. It also changes the actual denominator. Checking parent IDs alone is therefore insufficient to implement the stated scientific operator.

Independent synthetic reproduction used the existing sensitivity fixture, replaced its abbreviated plans with real `sensitivity_plan.shifted(...,+.1,...)` metadata, and confirmed every retained +shift row has `observed_full_bins=29`. It left all parent IDs unchanged:

| Supplied +shift arrays | Current accepted result |
|---|---|
| 30 epochs x29 bins x8 units, matching nuisance | Correct 5,760 nominal unit-bins |
| 30 epochs x30 bins x8 units, matching nuisance | **Accepted**, 6,000 nominal unit-bins |
| Previous wrong30 input with +1000 counts confined to the final extra bin | **Accepted**; D mean score changes by **-300.6605876532619** |
| 31 epochs x29 bins x8 units, while ordinal list still has 30 IDs | **Accepted**, reports 31 retained epochs alongside 30 parent IDs |

The counterexample uses only synthetic counts and models. It shows the assembly itself neither rejects a post-tone outcome contribution nor binds numerical rows to original parent identities. No actual D value was read to demonstrate it. The current tests exercise a valid29-bin input and ordinal-list tampering but do not exercise wrong time/epoch dimensions (`test_sensitivity_scores.py:24-38`).

Required repair before this assembly is accepted:

- Bind each aligned input to the exact retained planned parent rows, original unit count/order contract and permitted full pre-tone bin count. Require counts/q epoch dimensions to equal the planned/list length, and require T=the declared consistent plan bin count (normally30 for minus and29 for plus), with the original eight targets and matching11 nuisance columns. Reject missing/inconsistent plan bounds; do not silently truncate an oversized array.
- Validate before calling the scoring operator. If no rows survive, preserve a correctly identified empty cell and reject incompatible nonempty supplied data rather than hiding it.
- Add synthetic regressions for the valid30/29 cases, wrong +shift30 response-bin canary, wrong minus-bin count, extra/missing rows, nuisance dimension mismatch and inconsistent parent/bin plan metadata. Demonstrate no scoring occurs on the forbidden arrays. Preserve this failed candidate/review, prospectively register the ordinary repair, re-freeze and independently re-review.

This is a coding enforcement defect, not permission to change alignment masks/bin IDs, choose a favorable offset or weaken original sensitivity coverage. A future source adapter is not yet accepted; it cannot presently supply independent evidence that makes this unvalidated assembly correct. Even after its adapter is reviewed, validating the plan-to-array contract here prevents a silent integration regression.

## C calibration engineering assessment

For the actually frozen selected policies (D p=.9/ridge.1; S p=.5/ridge.1; C tau(.1,.3)/ridge1/seed23), `final_C.py` schedules **15 baseline +3 D +3 S +1 continuous =22 fits per mouse**, at most **198** for nine final mice. It imports model definitions and globally selected policy metadata, not development coefficients. Baseline initializations/rate estimates, feature scalers and continuous count/hidden moments derive anew from the 60 C epochs. D starts are the original seeds/normal(.05) rule; continuous W is zero and Q/projection seed is frozen. Minimum-objective/lower-seed selection uses C training objectives only. No B/E/D ranking or hyperparameter selection occurs.

The new C B4 offset is built once from the C-selected baseline/scaler and is shared bit-for-bit by D/S/continuous fits. Fit identity includes final mouse/role/C partition, units/epochs/C-state hash, original protocol, amendment, QC source freeze, source/scaler/Q identities and B4 request/offset. All required fit requests and selected requests, coefficients, preprocessing, units/QC, sensitivity masks/metadata and original epochs are serialized. The existing fit engine retains unchanged bounds/objective/PG/AD/fixed-FD gates and full attempts/trajectories. The focused synthetic22-fit test confirms schedule/offset/state/seed serialization without conducting real optimization; the independent numerical/model suite supplies separate mathematical tests.

Role/partition/identity checks precede C-state loading, which validates hash/shape/nonnegative integers/unit IDs. The module has no raw source or D-outcome loader. Exclusive execution journal plus existing fit-attempt rules preserve failures and forbid implicit reruns; injected failure records FAIL and denies a second execution. `policies()` requires the E-control PASS and original physiology/development policies, but the actual E-control artifact, denominator, frozen input/source identities and completed final eligibility must still be independently audited/bound in the later real-C approval. This engineering review does not assert that a presently growing E job has passed or that real C is authorized.

## Other pure sensitivity and descriptor assessment

Original unit masks feed the previously accepted restricted-information operator; no refit/scaler estimate occurs. Whole-epoch recent/provider-active/quartile masks retain original parent/bin identities. Empty/subthreshold cells and their computed scores are retained; six contributors cannot become eight by pooling subthreshold animals. Mandatory panel names remain present, optional panels cannot rescue, and the owner-locked broad primary INCONCLUSIVE verdict is explicit. The alignment-plan-to-array enforcement defect is the one identified above.

The new descriptor reads hash-bound saved headers and original source-table rows, preserving raw provider AP/DV/ML coordinates/attributes with **unverified physical units**. Lower/higher four raw DV ranks and numeric-ID ties are explicitly prospective descriptive subsets, not new confirmatory hypotheses or anatomical-depth truth. The descriptor correctly distinguishes a source-schema genotype field that was not decoded from provider absence; documented Aversion/source matches remain attached. One-probe-per-mouse does not establish independent probe/lab replication. No additional P0/P1 was found in these bounded descriptors; full final descriptive group/leave-group-out reporting is outside this component acceptance and still needs the complete final assembly review.

## Continuing boundaries

Repair only the demonstrated sensitivity contract and preserve original scientific definitions/owner amendment. This finding concerns the new pure sensitivity assembly and does not invalidate the unchanged previously accepted E-control transformations/summary now executing; no actual partial E-control output was opened, evaluated or certified by this review. The reviewer did not access any actual C count bundle, raw neural source, final D outcome, new fit or real control study. Only this new review file is written, apart from ignored synthetic test artifacts.

No full sensitivity execution, final C calibration, final release, D assessment, scientific/full mission PASS, external peer review or prospective Git closure is granted. Actual C execution remains gated both by this repair/re-review and by the separate completed-E/control-input pre-execution review already required by the parent.
