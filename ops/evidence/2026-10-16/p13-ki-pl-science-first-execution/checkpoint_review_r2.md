# Independent engineering checkpoint review r2

Mission: `P13-KI-PL-SCIENCE-FIRST-EXECUTION`.
Reviewed UTC: 2026-10-16T15:20:01Z.
Reviewer: separate local reviewer agent; internal review, not external peer review.
Decision: **REQUEST_CHANGES** for engineering checkpoint acceptance.
P0: **0**. Open code P1: **1**. Unresolved authorization P1: **1**. Total open P1: **2**.
Real neural access: **NOT APPROVED**. `MATERIAL_AUTHORIZATION_AMBIGUITY` remains unresolved; an unanswered owner question is not permission.

## Candidate and fresh checks

Reviewed `ENGINEERING_FREEZE_r2.json`, SHA256 `76c50bbebf31fea6a40a3286bc1d363ecba105d4e7660793dc3404809aec423c`, containing 22 hashes. Read the source-integrity repair, both approval entry gates, new baseline/HMM/continuous math, independent AD implementation, metadata covariates, fit engine, all tests, checkpoint verifier and implementation/readme scope claims against the activated frozen protocol. All **22** current hashes and all **85** original reviewed-contract hashes independently match.

Executed `& .\paper13_ki_execution1\reproduce.ps1` from repository root: exit **0**, **40 synthetic tests PASS** (20 preaccess, 16 model, 4 fit-engine). Network connections are blocked in reproduction. The tests verify source gating and synthetic values; they do not establish real physiological QC, all real candidate convergence, model selection, controls, final inference or paper completion.

Independent saved inspection confirms `ACCESS_DECISION.json`, `PREACCESS_APPROVAL.json` and `results/source_access.jsonl` are absent. Thus the real source entry is blocked and no acquisition journal exists. No real neural arrays, D outcomes, network or scientific fits were accessed by the reviewer. Only this review file and permitted ignored synthetic artifacts from reproduction are written; no source or existing evidence is modified.

## Resolved earlier code finding

The NaN pre-clipping defect from `preaccess_review_r1.md` is resolved. `cut_windows` now raises `SOURCE_INTEGRITY_STOP` for nonfinite/unassignable source values before comparisons can discard them. New end-to-end in-memory HDF5 NaN and Inf regressions cover the actual export path, separately from direct unit QC. The failure is a source-integrity halt, not silent cleaning, outside-window physiological ranking or admission of a fabricated finite record.

The original r1 package/review remains preserved and the snapshot regression passes. This is an ordinary safe synthetic repair before real access. It does not independently authorize decoding the full-record source; that question remains separate below.

## Open P1 findings

### P1 — Saved PASS reuse is not bound to the requested fit/objective/data

Evidence: `paper13_ki_execution1/fit_engine.py:50-59`; `test_fit_engine.py` complete-GLM test, which currently accepts a cached result even with empty data and an empty initial vector; activated protocol's exact candidate/data/seed/objective identity and all-attempt requirements.

For an existing file, `fit` checks only `status == PASS` and `source_hash`, then returns it before examining the new `kind`, data, ridge, p, offset, initial/seed or scientific identity. A unique filename is a caller convention, not a verified candidate binding. A collision or resume with a changed request can silently substitute another fit and its numerical evidence, including across animals/partitions, model families or mandatory starts. The stored `data_sha256` is not checked on reuse.

Independent synthetic reproduction, with no new optimization or real data:

- Used an actual PASS fixture produced by the supplied synthetic suite: `paper13_ki_execution1/work/synthetic_fit_3c77c60c4e4c4b6a88e7319730001a5d/glm.json` (GLM, ridge .1, p=None, 24 initial coefficients).
- Called `fit` on that same path and source hash requesting **HMM**, ridge **10**, p **.98**, new `(1,6,8)` zero y/offset, 16 initial coefficients and a different synthetic mouse/partition/seed identity.
- It returned the prior **GLM PASS unchanged**, without comparing the request. A before/after SHA256 confirmed the fixture was not modified.

Required correction: before any cached PASS reuse, compute and compare a canonical complete request/attempt identity binding at least source/protocol implementation identity, kind, ridge, p, y/x/offset array shapes/dtypes/bytes, initial values/required-start identity, and mouse/partition/config/unit/epoch/scaler identity supplied by the eventual runner. Mismatches must stop without overwriting or silently refitting. Exact matching requests may reuse the original immutable result. A separate explicit read-only result loader may omit request data, but `fit` must not silently treat a different request as that loader. Preserve existing failed/interrupted-attempt refusal. Add independent mutation regressions for data, offset, kind, ridge, p, initial/seed and scientific identity, plus a genuine exact-request reuse case. Freeze/re-review the repair before accepting the numerical engine.

This is useful autonomous engineering still available without owner input or real neural access; therefore the unresolved owner decision is not yet the only remaining checkpoint work.

### P1 — Owner raw-access decision remains a prerequisite, not an engineering approval

The earlier material question remains unanswered: whether trusted source ingestion may transiently decode full-record selected-unit timestamps including locked D solely to filter frozen A/C, with excluded outcomes never exported/used, or whether even that low-level D decoding is forbidden. The owner authorization's train/calibration permission and "Do not access D" instruction cannot be reinterpreted by a model test or implementation note.

The new `require_access_approval` is a useful fail-closed control: direct `SourceReader` construction and real QC entry require both hash-bound owner evidence and an accepted matching fresh review before creating a Session/cache or reading sources. The synthetic missing-approval test passes. No such records exist now. Maintain that state; this checkpoint review must **not** be copied into an accepted neural `PREACCESS_APPROVAL.json`.

After the safe fit-binding repair, if the owner is still unanswered and all other useful safe work is exhausted, a reviewed **WAIT_FOR_HUMAN_INPUT** checkpoint is appropriate. It must identify the same exact owner choice, not a missing environment, scientific data insufficiency, numerical failure or study PASS. Once the owner answers, preserve the explicit decision, review its scope and source-integrity implications, freeze any affected implementation and obtain fresh independent preaccess acceptance before real A/C QC.

## Numerical core assessment and limits

Apart from the cache-binding defect, no additional P0/P1 mathematical discrepancy was found in the reviewed core scope:

- B0-B4 feature dimensions/own/all-other lag groups, epoch resets, training-only population scaling, intercept policy and normalized Poisson/ridge objectives agree with the frozen equations. Current pinned target noise paths are blue-noise series, consistent with the intended metadata covariate; event history is taken strictly before the prediction-bin start.
- The HMM scores the exact joint two-state forward predictive likelihood before assimilation, uses uniform reset/fixed transitions, excludes five warm-up losses while retaining their causal filtering effects, and normalizes by actual scored unit-bins. Its forward derivative recursion matches the independent Autograd objective and full-path synthetic enumeration. Static p=.5 and persistent-state distinctions remain explicit.
- Fixed QR projections and continuous states use precisely one previous-count lag, training-only count/state scaling and 16 readout coefficients. Both dynamical penalties include all added coefficients, unlike unpenalized baseline intercepts.
- Original bound-projected-gradient polarity, all-coordinate independent AD and fixed-step FD comparisons, bound-aware FD, three declared checkpoints, fixed optimizer options, objective-call accounting and retained failures are implemented and tested synthetically. Optimizer success alone is not a numerical PASS gate.

These findings support the **tested core math**, not completion of M3/M4 or validation of future real endpoints. No complete real-data runner, B* selection, null/sensitivity bundle, final-release workflow or manuscript is claimed as delivered; the README and implementation notes accurately disclose that scope. Model/scientific gates remain unexecuted. The fit-engine issue must be fixed before its saved numerical PASS results can be safely bound to future mandatory candidates.

## Required next action and closure

Preserve this failed checkpoint review and current freeze. Repair/test the complete saved-fit identity binding using synthetic data; obtain independent engineering re-review. Keep source access blocked throughout. The owner decision still controls whether the proposed raw adapter may later be approved; engineering correctness does not manufacture that permission. No study PASS, M2 eligible-mouse count, real numerical result, final D release or paper completion is certified here. Git commit/push/readback/clean gates remain separate and are not certified prospectively.
