# Independent fresh preaccess review r5

Mission: `P13-KI-PL-SCIENCE-FIRST-EXECUTION`.
Reviewed UTC: 2026-10-16T15:35:00Z.
Reviewer: separate local reviewer agent; internal review, not external peer review.
Decision: **ACCEPTED_FOR_M2_A_C_ONLY_SOURCE_ACCESS**.
Open P0: **0**. Open P1: **0** for the reviewed source-access, operational-QC and durable-retention scope.
This is prospective engineering/access acceptance, **not** physiological eligibility, D outcome release, scientific PASS or mission completion.

## Exact reviewed candidate and checks

Acceptance binds only `paper13_ki_execution1/PREACCESS_FREEZE_r5.json`, SHA256 **`ae82cb20ce76058cda808b604c2908e8e0b354bcd695a86c0310ea9b13247a74`**, and its **32** frozen files. Read `QC_RETENTION_REPAIR_REGISTRATION_r5.md`, the complete revised `qc.py`, new journal tests, verifier and owner access evidence against the failed r4 review and original activated contract.

Independently verified all **32** current hashes, all **85** original reviewed-contract/source hashes, and all **28** archived r4 hashes using `preaccess_r4_package.zip` or unchanged external evidence files. The failed r4 review/freeze/source remain preserved. Independently confirmed these eight files are byte-identical to r4: `source.py`, `ACTIVATION.json`, `EPOCH_UNIT_ALLOCATION.json`, `ACCESS_DECISION.json`, `models.py`, `features.py`, `fit_engine.py`, `independent_ad.py`. No mathematical definition, threshold, ordering, source policy, allocation or prior scientific finding changed.

Executed `& .\paper13_ki_execution1\reproduce.ps1` afresh: exit **0**, **46 synthetic tests PASS**, 32 current and 85 original hashes verified, with network connections blocked by the verifier. Independent saved-file/hash/archive checks used a PowerShell here-string piped to `python -B -`. No source acquisition entry point, real neural values, real QC, real fitting or D assessment ran. `PREACCESS_APPROVAL.json` and `results/source_access.jsonl` were absent at review time. Only this review file and permitted ignored synthetic test artifacts are written by the reviewer.

Reviewed repair identities:

- `qc.py`: `9739fb8fc1d891aa3884f00229d092f1a8cdfa1fa6b5bfd24e9fed4afe281733`.
- `test_qc_journal.py`: `e4e00ee730127dc50ee8075e78eb861c336185268a422a0bbe1b9fa99abbe160`.

## r4 durable-attempt P1 resolution

The former end-of-mouse-only evidence path is repaired:

- `MOUSE_START` is created exclusively and flushed/fsynced before source work. An existing interrupted or failed journal cannot silently become another attempt.
- Each `UNIT_START` is durable before identity/extraction/QC; `UNIT_COMPLETE` records the A/C-only QC summary and flushes/fsyncs before the next unit. Source/screen errors append `UNIT_ERROR`; the real loop appends `MOUSE_ERROR` and re-raises rather than continuing to remaining units/mice/models.
- Earlier passing/failing QC attempts remain in the append-only journal even if a later source, state-write or completion operation fails. No raw full-record/excluded timestamps or D statistics are logged.
- Successful completion writes `MOUSE_COMPLETE` binding the aggregate result and saved training/calibration state hashes. Reuse requires the same source freeze, completed journal, exact result hash and intact matching state hash. Missing/partial completion or changed state/result/source is denied without overwriting or implicit retry.

The new synthetic regression produces a completed failing QC result for unit 1, injects a source-integrity error for unit 2, confirms both units' durable START/COMPLETE/ERROR sequence and preserved first result, and proves unit 3 is not processed. Additional regressions verify repeated-start refusal without journal changes, successful per-unit fsync/receipt behavior, and incomplete/tampered completion-state/source rejection. These directly cover the independent r4 finding without real outcomes. The P1 is **resolved**.

## Owner authorization and source boundary

The exact direct owner answer remains unchanged and hash-bound in `ACCESS_DECISION.json` and the r5 freeze:

> 允许受信读取器临时解码全记录，仅导出 A/C；禁止将 D 用于 QC、缩放、选型或评分。无法分区的非有限时间戳作源完整性错误停止。

Reply-file SHA256 remains **`b4bcbb861ba4541a45d1360f88b3dec9a17bc48d790871e0027f7e777475e9c6`**. The earlier material access ambiguity is resolved by this explicit owner decision, not by tests or an inferred interpretation. The permitted transient full-record decode and nonfinite source-integrity STOP match the unchanged implementation. No additional owner decision is needed for this exact narrow operation.

The trusted adapter exports only the frozen 60 A or C windows. Excluded B/E/D neural values/counts/QC/scalers/unit decisions/model selection/scores are not exported or used in this phase. D's incidental transient decoding is acknowledged; it is not falsely described as never read, independently blinded or protected by a P12 custody system. Nonfinite/unassignable raw timestamps halt extraction before silent clipping or physiological ranking. Immutable asset/ETag/range checks, hard internal dataset restrictions, unit mapping, temporal masks and denied B/E/D export remain intact.

Real source construction and QC entry still require the explicit owner evidence and a fresh matching accepted review before Session/cache/network creation. The owner-bound freeze, original activation/protocol and exact source bytes are verified. The corrected cache-request identity mechanism and all original numerical criteria remain unchanged; this preaccess acceptance does not predict their later real-data results.

## Accepted next action and continuing gates

The root executor may now record this actual review path/hash as accepted **only for the exact r5 freeze** in `PREACCESS_APPROVAL.json`, then begin **real M2 A/C-only source extraction and physiological QC** across the unchanged 19 candidates. The reviewer does not create that approval record or access real sources.

Preserve the 25-animal denominator, fixed 10/9 roles, first 120 epoch identities, A60/B30/E30 and C60/D60 assignments, first-eight-passing numeric PL policy and all failed/unexamined units. QC uses only A/C's 180 seconds and the frozen spike/ISI/occupancy/rate/refractory/finite/order rules. No reshuffling, lower threshold, favorable replacement or new dataset is allowed. If fewer than eight eligible mice remain in either role, STOP DATA_INSUFFICIENT; a source-integrity failure likewise stops at its preserved evidence, without fitting around it. No actual eligible count is yet measured or certified by this review.

No D outcome export, QC influence, scaling, selection, scoring or final evaluation is released. Original prerequisites for development selection, final C-only calibration, complete model/statistic/source freeze, independent numerical/release review and one final assessment remain mandatory. Any later relevant source/access/QC/scientific/oracle change invalidates affected evidence and requires appropriate fresh verification/review. Historical failed reviews and scientific findings stay immutable.

This acceptance certifies the prospective **M2 access/engineering gate only**. It does not certify real M2 PASS, real model convergence, B*/configuration selection, null/sensitivity results, inference, manuscripts/PDFs or full mission PASS. Future Git commit/push/readback/clean receipts remain separate and are not certified prospectively.
