# Targeted native HDF5 link diagnosis

Mission: `P16-M2-NATIVE-LINK-DIAGNOSTIC-R1`. BASE: `a0065c66aaa84ad39a985903fcd77bdc1e1e711c`.

**DIAGNOSTIC_STATUS = SOURCE_SCHEMA_INCOMPATIBLE.** The one authorized inspection identified a legitimate same-file internal timestamp alias, followed by a separate native storage-type contradiction. The frozen executed reader requires rotation, start timestamps and end timestamps all to have float64 storage; the actual rotation dataset has float32 storage. This is a completed metadata diagnosis, not M2 scientific PASS, source corruption, failed physiology, or a reason to reinterpret a historical failed attempt.

## Q1–Q8

1. **Failed component:** `/processing/running/running_wheel_rotation/timestamps`, the fourth component after HardLink `processing`, `running`, and `running_wheel_rotation`. The earlier `hard_object()` rejects that final non-HardLink before target inspection. Every traversed component is in `COMPONENT_AUDIT.json` and the append-only source component journal.
2. **Actual class:** `SoftLink`. No ExternalLink, cycle or unexpected target was encountered on these registered paths. This statement does not audit every link elsewhere in the NWB.
3. **Literal target:** `/processing/running/running_speed/timestamps`. **Normalized internal target:** the identical absolute path. Literal text was recorded before target traversal. No relative-target or parent-normalization assumption is needed for this source.
4. **Registered expected object:** yes. Only fixed-target traversal through registered HardLink components was performed. The alias resolves to the registered running-speed timestamp dataset, within the same open pinned source file. No numeric dataset read was needed.
5. **Object identity:** same-file identity and equal HDF5 object-header address **19,550,656** establish the alias/target as the same source object in this inspection. Both have vector shape `[365911]`, dtype `<f8`, unit `seconds`, interval attribute `1`. Shape equality is supporting metadata, not the identity proof. Rotation address **22,481,568**, dtype **`<f4`**, radians, conversion `1.0`, resolution `-1.0`; end timestamps address **22,480,144**, dtype `<f8`, seconds, interval `1`; both shapes `[365911]`.
6. **Scientific running-feature definition:** resolving this particular alias alone need not change that definition. However, the complete observed structure fails the frozen executed native reader's requirement that **all three stored arrays be float64**. M1's binary64 time rules and the executed reader's rotation-storage requirement must not be conflated. Float32 rotation storage does not by itself prove the behavioral estimand must change. Deciding whether storage versus computation precision can be treated as an implementation correction or needs an amended contract is a separate prospective owner decision. No such decision or conversion was made here; promoting float32 cannot recover absent source precision.
7. **Future restricted resolver:** the identified alias is structurally amenable to a narrow same-file resolver, while preserving strict-past rules in principle. That fact does **not** remove the second schema blocker. Outcome B does not permit the outcome-A-only repair proposal or activation. No production patch is supplied. The original reader, M1, scientific thresholds and STOP remain unchanged.
8. **Later numeric validation still required:** identifier/clock scalar equality in any future authorized production run; finite native values; timestamp ordering, duplicate handling and row correspondence; positive actual start/end durations; correct net-rotation interpretation and units/scaling; strict-past availability with actual interval end/age rules; coverage in fixed trial partitions; invalid/missing behavior treatment; physiology, neural QC, numerical model checks and inference. No equal-shape or same-object result validates these. No running speed was calculated and no rows were extracted.

## Separate failure mechanisms

Historical attempt: `ValueError: External/soft/noncanonical source link denied`; final timestamp SoftLink now explains that specific guard failure. The old generic error did not identify link class or target, and no retrospective detail has been inserted into its evidence.

Current diagnostic: after safe target metadata resolution, `Inspector.run()` raises `SCHEMA`, `Native binary64/vector metadata contradicts contract`. Its generic recorded `problem_path` is the alias path. **The actual dtype offender is `/processing/running/running_wheel_rotation/data`**, not the float64 timestamp dataset. This distinction is also recorded in `ROOT_CAUSE.json`. There is no evidence of corrupted timestamp values or unsafe target resolution.

## Source and resource evidence

One Development source only: mouse `726162197`, session `750749662`, probe `769322806`/`probeC`, file ID `1026124242`, declared file length `2818447324`, ETag `"5a68875f05100"`, NWB root version `2.2.2`. Original prospective registration and independently accepted exact five-code/source hashes preceded the source open. Root object identity attributes and every requested dataset's permitted metadata were recorded; identity **scalar dataset values were not read**. All 44 responses were HTTP206 with exact Content-Range length and pinned ETag. This establishes registered range-source identity, **not a whole-file cryptographic NWB hash or a fresh scalar session/clock equality test**.

|Ledger|Attempts|Requests|Payload bytes|Reserved bytes|Elapsed seconds|
|---|---:|---:|---:|---:|---:|
|Historical M2, unchanged|1 failed|39|81912|81951|5.468|
|New metadata diagnosis|1 completed|44|85712|85756|5.406|

The new request count is below128 and payload/reservation below8,388,608 bytes. Parent deadline600 seconds, child exit0, no kill, completion before deadline; complete payload accounting, no in-flight uncertainty. Forty-four exact metadata response bodies and their range/header/hash journals are retained separately from M2. HDF5 requested these bytes for object/link/attribute metadata; no data-chunk API or dataset-value API was invoked. Opaque transport metadata buffers are not saved behavior arrays. No full source download, second object, network retry or automatic extension occurred.

`RUNNING_NUMERIC_VALUES_READ=0`, `NEURAL_VALUES_READ=0`, `ADDITIONAL_SOURCE_SESSIONS=0`. No identity scalar values, QC, model work, source search, B/E or Final C/D. The watchdog/claims are local engineering controls; no protection against a malicious machine administrator or independent third-party custody is claimed.

## Reproduction, preservation and limits

Saved-only reproduction opens the HDF5 metadata through `SavedRangeReader`, which validates saved byte hashes/overlaps and fails if any required range is missing. Socket/HTTP access is denied and dataset value APIs remain blocked. All33 component events, exact schema exception, addresses, dtypes, shapes and source receipts reproduce from retained bytes with zero new source requests. Native Windows PowerShell reproduction also runs the14 prereviewed synthetic tests plus one new synthetic float32-rotation regression. It verifies all334 M1 and58 M2 frozen payload hashes. Runtime is Python3.11.15, h5py3.16.0, NumPy2.4.6, requests2.32.5.

Preserved unsuccessful evidence: first synthetic test-spy oracle error and its source; rejected preaccess review1 and full candidate; all intermediate synthetic logs; first saved-only reproduction's in-memory emitter fixture error and full candidate. That fixture now snapshots mutable pending rows at emission, matching the original immediate JSONL serialization. The original inspector's immutable33 rows already exactly matched native journals; no inspected source, real receipt or PASS oracle was changed. Details: evidence repair receipts and `TEST_ORACLE_REPAIR_2.md`.

Scientific state remains55 metadata candidates,28 Development (5BO/23FC),27 reserved Final BO; all original flash definitions, B0–B4/C/D/S,12 sensitivities, four reference controls, mouse allocation, statistics and original attempt budgets preserved. M3–M5 remain unrun under the original failed prerequisite. No predictive, biological, physiological, equivalence or scientific validation claim is supported.

## Decision and stop

Retain original `STOP_SOURCE_OR_QC`. Archive this **outcome B** and stop. Minimum next action, if the owner wishes to continue, is a separately authorized prospective assessment of the native rotation storage versus frozen reader precision contract, explicitly resolving implementation/scientific implications before any repair or access. This mission supplies no patch or M2 restart. If that contract cannot be resolved without changing the scientific policy, a separately approved amendment or study STOP is necessary; neither is silently selected here.

Final review, exact frozen payload denominator, saved reproduction and actual Git transport/clean proof are separate archive gates. A reviewed content candidate does not self-certify its future commit. Actual closure SHA/readback proof is written after execution in ignored `paper16_linkdiag_r1/work/closure_receipt.json` and reported to the owner.
