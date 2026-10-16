# Independent engineering checkpoint re-review r3

Mission: `P13-KI-PL-SCIENCE-FIRST-EXECUTION`.
Reviewed UTC: 2026-10-16T15:23:25Z.
Reviewer: separate local reviewer agent; internal review, not external peer review.
Engineering decision: **ACCEPTED_FOR_WAIT_FOR_HUMAN_INPUT_CHECKPOINT**.
Open code P0: **0**. Open code P1: **0**. Unresolved required engineering-evidence warnings identified: **0**.
Unresolved owner authorization: **MATERIAL_AUTHORIZATION_AMBIGUITY**, unchanged.
Real neural access: **NOT APPROVED**. This is **not** accepted preaccess permission or mission/scientific PASS.

## Frozen candidate and executed checks

Reviewed `ENGINEERING_FREEZE_r3.json`, SHA256 `0f38250d5aa659f70d216c64448f9f57f0d2dfaab419e5a8c7e33b8efa2ef856`, containing **23** hashes. Read the complete request-binding repair and tests, verifier/default reproduction and updated scope notes against `checkpoint_review_r2.md` and the activated scientific boundaries. The prior failed checkpoint review remains unchanged, SHA256 `8732a3cd04e798ee4ca72fa8eee7ce8714a230d0e374a7f69f4637d2fb0260b5`.

Executed `& .\paper13_ki_execution1\reproduce.ps1` from repository root: fresh exit **0**, **42 synthetic tests PASS**, 23 current hashes and 85 unchanged original reviewed-contract hashes verified. The verifier blocks network connections. Tests use synthetic arrays/in-memory HDF5 and ignored synthetic fit evidence, not real neural data.

Independent PowerShell here-string piped to `python -B -`, using only standard-library saved-file inspection: all **23** current hashes match, all **85** original hashes match, and all **22** r2 hashes match their archived bytes in the preserved **23-file** `checkpoint_r2_package.zip`. The earlier r2 freeze, original wrong cache expectation and failed review remain recoverable historical evidence. No old source/protocol result was rewritten to fit the repair.

Independently confirmed `ACCESS_DECISION.json`, `PREACCESS_APPROVAL.json` and `results/source_access.jsonl` remain absent. No owner approval or actual source access is inferred from an unanswered question. No network, real NWB/neural array, real physiological QC, real fit or final D assessment was accessed. This reviewer writes only this new review file; reproduction creates permitted ignored synthetic artifacts.

## Cache-binding P1 resolution

Evidence: `paper13_ki_execution1/fit_engine.py` request construction before existing-path lookup; exact-GLM reuse, changed-field, changed-HMM-p, incomplete/legacy-request and real-identity tests in `test_fit_engine.py`; updated `IMPLEMENTATION_NOTES.md`.

The former source-hash-only lookup is removed. Before reusing any existing result, `fit` constructs a canonical request containing model kind, ridge, p, source identity, full supplied scientific identity, y/x/offset array shape/dtype/byte digest, initial-vector digest and offset-presence flag. It compares both canonical request content and request hash against the saved PASS. Changed or incomplete/legacy requests stop without overwriting or refitting. Exact matching requests may reuse their original result. Existing failed/interrupted attempts remain nonretryable.

Real-data requests additionally require the declared mouse, partition, configuration, unit, epoch, scaler and protocol identity fields and source hash. The eventual real runner must populate these from the frozen actual manifests and independently verify its own scientific lineage; this review certifies the present binding mechanism, not a nonexistent real workflow.

The corrected positive test now uses the same full request. Eight independent changed-field cases reject altered y, x, ridge, initial, identity/seed, offset, kind and continuous-vs-baseline objective; the HMM test separately rejects changed p. Fixture bytes remain unchanged after mismatches. Incomplete cached requests cannot act as an implicit result-loader API. This directly addresses the independently reproduced GLM-to-HMM substitution from r2.

Changing the old empty-data reuse test is justified as a stale/incorrect test expectation against the original exact-candidate requirement. Its original bytes and the counterexample are preserved. Replacement coverage is stronger and preserves every mathematical/numerical threshold; no scientific acceptance assertion was weakened. The code P1 from r2 is **resolved**.

## Previous repairs and numerical scope

The nonfinite source-integrity repair and its end-to-end NaN/Inf regressions remain intact. Source construction and real QC entry still require hash-bound owner evidence plus an accepted matching fresh preaccess review before source Session/cache/network creation. The missing-approval regression passes. Canary noninterference is not relabeled as access permission.

No relevant mathematical core changed in this repair. The prior bounded assessment of B0-B4 features/objectives, exact joint HMM forward derivatives, fixed continuous past-count state, independent AD/FD, PG polarity, fixed budgets/checkpoints and retained attempts remains supported by the unchanged math and fresh synthetic suite. No additional code P0/P1 was found for this engineering checkpoint. This does not establish real numerical convergence, all real model candidates, selected B*, null/sensitivity execution, inferential assumptions or manuscript completion.

## Gate state and unresolved human decision

| Gate | Current supported state |
|---|---|
| M1 metadata activation/allocation | **PASS for the metadata-only M1 scope**: exact reviewed source hashes, 19 fixed candidate identities, 10/9 roles, first 120 epochs and partition/unit policies preserved; original 25-animal denominator retained. This does not release D or admit mice. |
| M2 real A/C QC | **BLOCKED_HUMAN_INPUT / NOT RUN**. No real source request or QC result exists. |
| M3-M4 real baselines/dynamical fitting | **NOT RUN**. Reviewed synthetic core math is engineering progress only. |
| M5 real development selection/evaluation | **NOT RUN**. No B*, E report or neural comparison exists. |
| M6 calibration/nulls/sensitivities/final D | **NOT RUN**. No final release, D access or scientific assessment is approved. |
| M7 manuscript/scientific completion | **NOT RUN**. No findings or paper/PDF completion is claimed. |

The owner must still decide whether transient trusted full-record selected-unit decoding, including D, is permitted solely for extracting A/C with no excluded-outcome export/use, or whether even that low-level decoding remains forbidden. The current authorization does not uniquely resolve that choice; source format and test success cannot invent permission. If permission is denied, use a genuinely compliant partition/time-indexed source path or obtain the exact missing export. If granted, preserve the explicit decision and bounds, review source-integrity handling and obtain a fresh matching independent preaccess acceptance before real reads.

The present code defect is repaired and the supported safe checkpoint checks are complete. Additional synthetic work cannot resolve the next required owner access decision or legitimately advance real M2. A **WAIT_FOR_HUMAN_INPUT checkpoint archive is appropriate** while that decision remains unanswered. This is an authorization pause, not NEED_ENV, DATA_INSUFFICIENT, NUMERICAL_FAILURE or scientific PASS. The full mission remains incomplete; no future M2-M7 work is silently dropped or redefined as delivered.

## Closure and approval boundary

Accept only this bounded engineering/M1 checkpoint and its honest human blocker. Do **not** use this file to create an accepted neural `PREACCESS_APPROVAL.json`: it explicitly denies such approval pending the owner decision and subsequent fresh source review. Preserve all earlier failed reviews/packages, current candidate hashes and exact pending question.

The root executor may perform the separately required evidence/Git checkpoint closure under existing authorization. Actual exact-file commit, normal `origin/test` push, remote hash/manifest readback and clean-tree verification require their own receipts and are not prospectively certified here. No main promotion or final scientific release is granted. Any relevant later source/protocol/oracle change invalidates the affected review evidence.
