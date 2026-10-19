# Independent actual metadata review — offline only

Mission: `P16-M2-NATIVE-LINK-DIAGNOSTIC-R1`.

Evidence decision: **ACCEPTED_ACTUAL_METADATA_EVIDENCE_B**. Open evidence/reporting P0: **0**. Open evidence/reporting P1: **0**, provided the distinctions below are preserved in the final package.

Grounded scientific disposition: **SOURCE_SCHEMA_INCOMPATIBLE (B)** under the unchanged frozen reader/diagnostic contract. The internal alias itself is structurally identified and compatible; a separate rotation-storage dtype incompatibility prevents overall outcome A. This is not a final candidate, Git closure or M2 scientific PASS review. No production repair, numeric validation or M2 restart is authorized.

## Scope and method

Read only saved receipts, journals, raw metadata range responses and frozen source/specification. Opened the saved ranges through `SavedRangeReader` as the byte source to h5py with `no_dataset_values()` active. No network, original NWB/source object, dataset/scalar value, running/neural array, model or QC operation was accessed. Only this unique review report was written.

BASE remains `a0065c66aaa84ad39a985903fcd77bdc1e1e711c`. The actual receipt binds registration `72badf889acdafbaf02f9179ec1412dfea85ef211f2a7e520d1bd40d82835600`; the executed inspector is `cd9979978a5f266eb005449c1ed4233d56d89930a57422cf34540411ac02f71b`. Its source identity is the exact registered original Development mouse726162197/session750749662/file1026124242, size2818447324, ETag `"5a68875f05100"`.

Offline re-execution of `Inspector.run` from **only** the saved44 metadata responses reproduced the same `SCHEMA` exception and all **33 component events exactly**, byte-for-data-structure equality with the component JSONL and receipt audit. Dataset value canary calls were **0**. No missing range or acquisition fallback was used.

## Actual structural findings

|Logical object|Stored metadata|
|---|---|
|Root|NWB2.2.2, namespace core, neurodata_type NWBFile|
|running_wheel_rotation/timestamps|SoftLink with literal absolute target `/processing/running/running_speed/timestamps`; normalized candidate identical|
|Resolved rotation timestamp target|Same approved file, HDF5 address19550656, Dataset shape[365911], dtype`<f8`, unit seconds, interval1|
|Registered running_speed/timestamps|Same file/address19550656 and identical stored metadata|
|running_wheel_rotation/data|Dataset address22481568, shape[365911], dtype`<f4`, unit radians, conversion1.0, resolution−1.0|
|running_speed_end_times/timestamps|Dataset address22480144, shape[365911], dtype`<f8`, unit seconds, interval1|

The initial SoftLink event correctly retains pending object identity; the separate resolved event records same-file/address identity. This is stronger than a plausible target string or matching shape. It still does not establish correspondence or validity of numeric rows.

## Q1–Q8

**Q1 — Exact earlier failing component:** the final `timestamps` component at `/processing/running/running_wheel_rotation/timestamps`. The three preceding components are HardLinks/Groups in the actual audit. Given the unchanged pinned object and old hard-link-only loop, this SoftLink is the identified original traversal blocker. Earlier saved-stop reports appropriately left it unknown before this new investigation; do not rewrite them retroactively.

**Q2 — Actual class:** SoftLink. It is not an ExternalLink or a missing component in the inspected source. No assertion that it was corrupted is supported.

**Q3 — Literal and normalized target:** both are `/processing/running/running_speed/timestamps`. The actual literal is absolute and contains no unresolved parent traversal. This finding is not borrowed from the synthetic fixture or SDK writer.

**Q4 — Registered target identification:** yes, structurally and without numeric reads. The approved manual metadata traversal reaches the registered timestamp dataset in the same file.

**Q5 — Identity strength:** resolved same-file identity plus HDF5 object address19550656, not merely shape/path resemblance. The alias and registered target share that actual object. Equal365911 lengths of data/start/end arrays are a separate structural fact and do not prove same-row timing or valid durations.

**Q6 — Scientific feature definition:** resolving this exact internal alias alone need not change the intended same-row net_rotation/actual-duration feature. However, actual rotation storage is `<f4`, whereas frozen `source_running.native_running` requires all rotation/start/end vectors to be native float64. The current diagnostic expressly preserves that contract and therefore correctly returns B. This metadata finding does **not** show float32 timestamps, corrupted measurements or that M1's behavioral estimand itself must change. M1 explicitly emphasizes binary64 native timing and float64 computation; distinguish those from source storage dtype. Whether a future storage-type accommodation is semantically acceptable or requires a source/scientific-contract amendment needs a separate owner-scoped decision. No unilateral reinterpretation is authorized here.

**Q7 — Future resolver:** the observed fixed internal alias can support an allowlist-restricted structural resolver concept. It is **not sufficient** to restore compatibility because the additional dtype gate would still fail. Overall outcome B does not authorize the routine A-only repair proposal/activation or M2 restart. Preserve the dtype/reader disagreement and seek separate prospective source-contract adjudication before considering implementation, values or another source attempt.

**Q8 — Still unvalidated:** actual numeric finiteness, duplicate/order properties, end>start, interval duration and age limits, row correspondence, rotations/rates, strict-past feature outputs, source invalidity overlap, running availability by role/color, unit observation support, A physiology, cohort14/3BO/10FC feasibility, model/numerical performance and Final activity. No dataset values were read. Row counts/units/clock metadata alone cannot establish any of these.

## Why B rather than A

The receipt reports `Native binary64/vector metadata contradicts contract`. Offline replay reproduced that precise decision. The decisive offending metadata is **rotation/data dtype`<f4`**; alias/source/end timestamp dtypes are`<f8` and their recorded units are seconds. Matching lengths are within the original capacity bound and do not remove the rotation-storage mismatch.

The emitted receipt's generic `problem_path` is the alias timestamp path because the frozen classifier associates the combined dtype/vector check with that path. Preserve that original receipt. The final report should separately identify the actual dtype offender as `/processing/running/running_wheel_rotation/data`; do not claim the alias timestamp dataset itself is float32. The original SoftLink rejection and the newly discovered dtype incompatibility are two different blockers, encountered in that order.

The overall outcome must not be silently upgraded to A because the alias is legitimate. Conversely, do not describe B as an unsafe link, inherently invalid Allen source, biological QC failure or a measured running-coverage failure. A source-reader schema discrepancy is what is established.

## Transport and execution accounting

Independently reconciled:

-44 reserved requests,44 response-header events,47 payload-chunk events,44 completed saved range bodies.
-85,712 newly observed payload bytes,85,756 reserved bytes: exactly payload+44 one-byte allowances. Range records and body SHA256/lengths pass SavedRangeReader validation; journal totals agree with the receipt and all headers are206 with the pinned ETag.
- Parent child_exit0, not killed, valid_completed_inspectiontrue, elapsed **5.406seconds**, before the registered600-second deadline. This is successful completion of a negative diagnostic, not source/behavior/model success.
- Running numeric values0, neural values0, additional source sessions0, forbidden dataset-value calls0. One exact-object diagnostic was completed; no other or Final source was inspected.

Keep these new counts separate from the immutable original M2 ledger39 requests/81,912 payload/81,951 reserved bytes, one failed source attempt and27 unattempted Development sessions. The new metadata diagnosis does not convert that earlier attempt into a completed M2 source gate. No further live access or retry is authorized after the completed diagnostic.

## Reporting recommendations

Preserve one overall B disposition while reporting the positive structural alias identity and negative dtype result side by side. Answer all eight questions at their actual evidence level. State zero numeric/neural reads and unvalidated running semantics explicitly. Do not prepare/activate a resolver-only production repair under the conditional outcome-A permission. The minimal next action is a separately authorized decision about the native-storage/reader schema contract, keeping binary64 timestamps, scientific transform, thresholds, cohort, model and Final restrictions intact; the current mission must stop after its reviewed archive.

The final full package remains to be sealed and independently reviewed. No final PASS, remote commit, readback or clean-tree result is asserted here.

## Exact checked evidence hashes

|Artifact|SHA256|
|---|---|
|results/SOURCE_INSPECTION_RECEIPT.json|0a559fc4e4540b35b9d140501c2958fe865b9e849cdd41392f8bb50b8d116b2e|
|results/SUPERVISION.json|78677fb00c32dd14fbbc5a00cc125f11087e6269c2b9f7bf8e437df0f6d24699|
|results/INSPECTION_ATTEMPT.json|db9017b384e3e4048b8aa8f79902ff68bdbbe02af677c90cfca3a0435f5868ca|
|results/SOURCE_OPEN_ATTEMPT.json|72fbb8167531aeb61060d9db7e6da5bc37d6fffdc032307ced7008465f0e2217|
|results/RANGE_JOURNAL.jsonl|a82c2f3830746b29a04f958ecd7d9460bd8b8ab94d86b39a2e1cdad66f519ea1|
|results/COMPONENT_JOURNAL.jsonl|475963a15c226833dd40557211ca687fb1960f946226688662616429f866742f|
|E/SOURCE_INSPECTION_1.log|8b6136d75e6a5a75f5e57a5cb9e4d0f3af2318f27334159339120aa09f762ec1|

`results/` is under `paper16_linkdiag_r1/`; `E` is `ops/evidence/2026-10-18/p16-m2-native-link-diagnostic-r1`. Every raw metadata response is individually bound by its receipt range SHA256 and was verified in offline replay. Reviewer writers are **COMPLETE/quiescent** after sealing.
