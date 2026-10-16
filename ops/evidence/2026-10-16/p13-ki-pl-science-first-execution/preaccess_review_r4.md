# Independent fresh preaccess review r4

Mission: `P13-KI-PL-SCIENCE-FIRST-EXECUTION`.
Reviewed UTC: 2026-10-16T15:30:46Z.
Reviewer: separate local reviewer agent; internal review, not external peer review.
Decision: **REQUEST_CHANGES — REAL M2 ACCESS ACCEPTANCE WITHHELD**.
Open P0: **0**. Open P1: **1** for durable QC-attempt retention.
The prior material authorization ambiguity is **prospectively resolved by the explicit owner reply**. No scientific gate, eligible cohort or full mission PASS is certified.

## Exact reviewed identity

This review assesses **only** `paper13_ki_execution1/PREACCESS_FREEZE_r4.json`, SHA256 **`3fdd24f58b7e4e3b6c1a4efaa5f98675e9eb67fe71d4bf5dd60ae5275df1aa90`**, containing **28** hashes, and the owner evidence included in that freeze. The earlier r3 checkpoint identity and all unsuccessful reviews/source snapshots remain preserved; no earlier denial or scientific finding is rewritten.

Independently verified all 28 r4 hashes, all 23 unchanged r3 package hashes and all 85 original reviewed-contract/source hashes. Activation hash remains `cf62c24c6f534a4e0d2102d609822e62112958961ee3f339d002a9e7d1424bd6`; activated scientific protocol hash remains `3129ee6017232db49a68136cc0cf04942d4abbf31081ef54782a23ddd3f01660`. Source/QC/math, frozen 19 candidate identities, 10 development/9 final roles, first 120 epochs, unit order and A60/B30/E30 versus C60/D60 partitions are unchanged from the reviewed checkpoint. The original 25-animal denominator and historical study findings remain intact.

## Owner decision and narrow permitted operation

Read the exact `OWNER_SOURCE_ACCESS_REPLY.txt`, `OWNER_SOURCE_ACCESS_EVENT.json`, `ACCESS_DECISION.json` and `PREACCESS_AMENDMENT_r4.md`. The preserved direct human answer is:

> 允许受信读取器临时解码全记录，仅导出 A/C；禁止将 D 用于 QC、缩放、选型或评分。无法分区的非有限时间戳作源完整性错误停止。

Its file SHA256 is **`b4bcbb861ba4541a45d1360f88b3dec9a17bc48d790871e0027f7e777475e9c6`**. The event records the exact pending-question context and answer; the access-decision record binds this exact reply hash, original activation and protocol. Independent string comparison matched the reported human answer exactly. Permission comes from that explicit owner decision, not from canary invariance, an analyst-authored flag or this reviewer inventing intent.

The now-permitted operation is trusted transient full-record timestamp decoding for an examined candidate PL unit **solely to extract the frozen A/C windows**. Unassignable nonfinite timestamps halt source extraction. The amendment does **not** authorize D-derived quality judgments, rates/counts, scalers, unit ranking, model/hyperparameter selection or scoring. It also does not authorize early B/E scientific exports in this phase, D outcome inspection/evaluation, a final release, dataset changes, threshold relaxation or repeated neural policy tuning.

## Implementation and fresh tests

Re-inspected `source.py`, `qc.py`, frozen source policies and the exact amendment against the prior r3 review. Its access/export behavior respects the newly clarified narrow boundary, but the durable attempt-retention P1 below prevents operational acceptance:

- Real `SourceReader` construction and QC entry still require owner evidence and a fresh matching accepted preaccess review before Session/cache/network creation. Exact freeze and review hashes, owner reply hash and all frozen file hashes are checked.
- Immutable activated asset IDs, exact ETags/ranges, hard internal nonvirtual datasets, unit-row identity and storage bounds remain enforced. Raw range caching is explicitly opaque trusted ingestion, not a claim that no D raw bytes/timestamps were read or that independent-principal isolation exists.
- The full-record vector remains inside the trusted extraction path. Only A or C's 60 relative-time windows reach physiological QC and saved training/calibration state. B/E/D partition exports are denied. No full-record physiological rate/order/refractory statistic is used to rank units.
- NaN/Inf/unassignable source values raise `SOURCE_INTEGRITY_STOP` before clipping. They cannot silently disappear or become an invented finite training record, and the source failure is not converted into a unit-quality statistic. The owner explicitly authorized this source-integrity handling.
- The frozen 180-second A/C exposure, within-epoch ISIs, 50-spike/30-ISI/12-occupied gates, rate .1–100 Hz, refractory fraction <=.01, finite/strictly ordered exported timestamps and first eight passing numeric PL IDs remain unchanged. Actual admissibility is still unknown. At least eight eligible development and eight eligible final animals are required before progression; otherwise preserve the failures and STOP DATA_INSUFFICIENT without swapping or relaxing.

Executed `& .\paper13_ki_execution1\reproduce.ps1` afresh: exit **0**, **42 synthetic tests PASS**, current 23 engineering and original 85 hashes verified. Independently verified the additional complete r4 28-file hash set. The suite covers missing-approval denial, B/E/D export denial, excluded finite-value canary invariance, end-to-end nonfinite failure, exact QC/partition/bin properties and the repaired numerical/cache core. No acquisition entry point or real neural/QC/fit path ran during review. `PREACCESS_APPROVAL.json` and `results/source_access.jsonl` were absent at review time.

This reviewer writes only this new review file. No real source, network, spike values, real QC, model fit or D assessment was accessed by the reviewer. The reviewer does not create an approval-record file or certify future execution results.

## P1 — Persist each unit QC attempt before the next source operation

Evidence: `paper13_ki_execution1/qc.py` per-mouse `attempts=[]`, per-unit `q=screen(ts); attempts.append(...)`, and serialization only after the unit loop/source context and training-state write; owner instruction to preserve all QC failures/exclusions; activated all-attempt/failure retention contract.

Per-unit completed QC results are held only in memory until the mouse's final JSON is written. If a later unit raises `SOURCE_INTEGRITY_STOP`, range/version/read failure or another exception, the earlier attempted units and their passing/failing QC summaries are never serialized. The range journal preserves transport, not those physiological QC decisions. The aborting unit itself also has no durable per-unit START/error record. This is a direct loss path for required attempted-QC/failure evidence, even though the overall process stops rather than proceeding scientifically. A console traceback or later possible reconstruction from opaque cache is not retained original attempt evidence.

No real reads occurred, so this is a prospective ordinary engineering defect and can be corrected without revisiting neural outcomes. Add append-only, durable per-unit attempt records tied to mouse/partition/unit/source freeze: START before source value access; COMPLETE with its A/C-only QC summary before attempting the next unit; ERROR/STOP with non-sensitive structural failure classification when extraction or screening fails. Preserve any earlier attempt records if a later read, output write or interruption fails. Do not log full-record/excluded timestamps or D outcomes. The final mouse aggregate should refer to these original records; restarting must not silently overwrite/reclassify attempts or replace a source-integrity scientific stop.

Required regression: synthetic first-unit completed QC (including a failing-QC case), followed by a second-unit injected source-integrity/read exception, must leave durable first-unit and aborting-unit records without producing a successful mouse/M2 gate or neural/model progression. Also verify successful aggregation and replay/partial-state policy under the same frozen input identity. Preserve the current candidate/review, repair using synthetic data, freeze a new candidate and obtain fresh independent preaccess review. The 42 current tests do not exercise this mid-mouse evidence-loss path.

## Next gate and continuing restrictions

Do **not** bind this review as accepted in `PREACCESS_APPROVAL.json` or start real source/QC access. The owner access choice is now resolved and should remain preserved; the blocker is the independently repairable retention defect, not another authorization question. After the safe repair/new freeze and successful fresh independent review, the root may record that actual accepted review and begin only the frozen **M2 A/C extraction and physiological QC** across the unchanged 19 candidates. No real-data experiment is needed to fix the P1, and no M2 pass is predicted.

D outcomes remain locked for analysis. The fact that their timestamps may now be transiently decoded by the trusted source adapter does not release D counts, features, scalers, scores, statistical outcomes or final assessment. Original prerequisite gates, final C-only calibration, exact source/model/statistic freeze, independent release/numerical review and one-final-assessment rule still apply. New B/E/D export implementations or other relevant access/scientific/source changes require their own appropriate fresh verification/review before use.

There is no certification here of 16 eligible animals, real baseline/dynamical convergence, B* or selected configurations, null/sensitivity results, final inference, manuscript/PDF completion or full mission PASS. The earlier owner-blocked checkpoint remains a truthful historical record; this is its prospective access clarification. Actual later Git changes/readback/clean receipts are separate and not certified in advance.
