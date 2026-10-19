# Independent single-object metadata preaccess review 2

Mission: `P16-M2-NATIVE-LINK-DIAGNOSTIC-R1`.

Decision: **ACCEPTED_SINGLE_OBJECT_METADATA_ONLY**. Open P0: **0**. Open P1: **0**.

The exact repaired parent-supervised diagnostic may perform **one** registered metadata-only inspection of the original failed Development object after the canonical review/hash-bound approval is installed. No dataset values, including identity scalars, running/neural arrays, additional source objects or Final data may be read. This is not a production reader approval, scientific M2 PASS, M2 restart, reader-repair execution or authorization to fit/score/QC. Stop after the actual diagnostic and its reviewed archival handoff.

## Exact scope and preservation

BASE remains `a0065c66aaa84ad39a985903fcd77bdc1e1e711c`. Reviewed the complete affected inspector, transport/worker/supervisor, new offline range reader, new tests, current access registration and prospective repair registration. The complete owner247-row source/scope review in PREACCESS_REVIEW_1 remains applicable to unchanged surfaces. The former report remains **REPAIR_REQUIRED/0P0/1P1**, SHA256 `e3d6d8871b036a0a44b9bba85c27f9092ec0e1ed73d0343a54cda2ed82aa2cce`; it is not retroactively accepted.

Independently rehashed all334 M1 and58 M2 payloads and registration prior pins: unchanged. The historical M2 executed reader, stopped attempt, source accounting, science and STOP verdict remain immutable. Checked the original four candidate files and first review inside the rejected archive against their prior hashes; its current archive hash agrees with the preserved receipt. The new repair registration records source_opens_before_repair0 and unchanged scientific thresholds/budget before any native execution.

Only this unique report was written. All execution used synthetic HDF5/HTTP/child fixtures and saved source/hash checks. No real source/NWB/network, dataset/scalar value, running/neural array, model, QC or Final access occurred. This is internal independent review, not third-party custody, external peer review or independent-laboratory validation.

## P1 resolution

The metadata compatibility classifier now enforces the **existing** source requirements before outcome A:

- Equal binary64/vector shapes must have `0<n<=2,000,000`; empty/oversized arrays are explicit metadata incompatibilities.
- Canonical source/end timestamp units must be seconds; absent/empty/unknown essential unit metadata remains unresolved rather than being inferred from SDK intent. Explicit contradictory timestamp conversion/offset is rejected. The alias and registered source timestamp object have proven same-file/address identity, so they cannot evade this check through a second plausible-looking path.
- Canonical rotation data units must be radians, identity scaling is retained and same-quantity rotation-parent unit conflicts are rejected. A running-speed TimeSeries velocity unit such as cm/s is correctly allowed to differ from its timestamp unit.

Focused new regressions cover the original false-A examples and the converse valid velocity/time quantity distinction. Unknown metadata remains inconclusive, explicit contradictions map through the existing schema outcome, and no numeric rescaling, new threshold or scientific amendment was introduced. **Prior P1 resolved.** No additional P0/P1 was established.

## Evidence improvements reviewed

The current registration prospectively adds completed opaque metadata response retention under the unchanged8MiB/128-request/600-second ceilings. `MetadataRangeReader` writes each completed exact response once to `.bin`, fsyncs it and records its relative payload path/hash in the completed range event. The worker always supplies its dedicated metadata-range directory. This creates no additional GET and does not invoke dataset value or data-chunk APIs. Partial/in-flight accounting still distinguishes observed chunks from conservative reserved upper bounds.

`SavedRangeReader` has no network imports or acquisition fallback. It validates each relative `.bin` path within its supplied root, byte count, SHA256, source bounds and consistency of overlapping ranges. Reads can combine existing saved coverage but fail on missing bytes; unsafe paths, corrupt payloads and conflicting overlaps are rejected. It is an offline metadata byte source, not a neural/behavior array decoder. Every actual offline HDF5 replay must still use the no-dataset-value guard and must report incomplete coverage honestly.

`Inspector.record` now deep-copies the initial pending state into the in-memory receipt. Initial path/candidate match is distinct from resolved object identity, both in that receipt and in immediately serialized append-only JSONL. Later resolution no longer mutates the earlier pending snapshot. Relative `..` targets remain unresolved; lexical normalization is not upgraded to native source proof.

## Independently executed tests

Executed from the repository root:

```powershell
& .\paper16_m1\work\runtime\Scripts\python.exe -B -m unittest paper16_linkdiag_r1.test_diagnostic -v
```

Observed exit0, **14/14 tests PASS**. The previous11 methods remain; new coverage addresses metadata contradictions, immutable pending/resolved records, completed body retention, offline HDF5 metadata replay and missing/corrupt/traversal denial. No required prior assertion was removed or weakened.

Reviewer-owned integration additionally generated a valid synthetic HDF5 image, supplied mocked exact-range HTTP responses to the actual transport and retained only the metadata ranges requested by guarded h5py/Inspector operations. **34 ranges,17,648 payload bytes,17,682 reserved bytes** were saved. Reopening through `SavedRangeReader` with no network and no dataset-value calls reproduced the same compatible status and identical object metadata. Independently supplied conflicting overlapping ranges were rejected; absent saved bytes raised MissingSavedRange. These are synthetic integration numbers, not actual-source receipts or a new source inspection.

## Full access and scientific boundary recheck

Only Development mouse726162197/session750749662/file1026124242, size2818447324, ETag `"5a68875f05100"` is registered. Other/Final objects are rejected before open. The nine logical running paths and root/allowed attribute metadata remain fixed; identity scalar **values** are not read. Every flat component is inspected with `getlink=True` first. External links are never dereferenced; unknown/neural/intermediate targets and cycles remain blocked. Only an authorized fixed internal target is manually traversed through safe HardLink components, with actual same-file/object-address evidence separated from path/shape plausibility.

No-dataset-value getitem/array/iteration/read_direct canaries remain active around native inspection. Source URL/size/ETag/range identity checks, pre-request reservation and per-request chunk limit remain unchanged. Exclusive parent/child claims prevent a second diagnostic; the external600-second watchdog and cooperative cache/request/metadata guards remain. Actual outcomes require a complete timely supervision/inspection chain; incomplete or unsafe metadata must not be converted to A. No budget extension, second source or retry is permitted.

Q1–Q5 must be answered from the future **actual** component/range/identity metadata, not these synthetic fixtures. A valid A establishes at most structural internal-link compatibility. It does not establish same-row numeric timing, finite/order/duplicate behavior, actual durations/age, strict-past coverage, physiological admission or validity of an executed production reader. Those remain Q8 limitations and require separately authorized later numeric validation. Q6–Q7 and any optional future resolver proposal must be conditioned on actual compatible metadata; no outcome automatically resumes M2.

The five required source hashes below must be included in the canonical approval. The prospective repair registration and immutable source pins additionally preserve provenance. No approval receipt was written by this reviewer.

## Exact reviewed hashes

|Path|SHA256|
|---|---|
|paper16_linkdiag_r1/ACCESS_REGISTRATION.json|72badf889acdafbaf02f9179ec1412dfea85ef211f2a7e520d1bd40d82835600|
|paper16_linkdiag_r1/links.py|a1e4812418e18b66f6c410ff9cf846d6e1a1e813540de0b9b1dafe6ac1a92141|
|paper16_linkdiag_r1/inspect_source.py|cd9979978a5f266eb005449c1ed4233d56d89930a57422cf34540411ac02f71b|
|paper16_linkdiag_r1/test_diagnostic.py|51b9909bcda69bc15f35c940d345c0650f66090a59dd206ac049ec40de5cc016|
|paper16_linkdiag_r1/saved_ranges.py|1d1c854a921787cb3050b3328b84dc67962704025bae41813f2c79e1772a73c4|
|E/PREACCESS_REPAIR_1_REGISTRATION.json|12e6382ae6524411713952445c5417478203bb3790a544646d79dcce57fbedf3|
|E/REJECTED_PREACCESS_1_CANDIDATE.zip|1b27bb818b4c3a52ce1f7e34cc7fc624e154f2914401bd1b0e1d9cee46034f09|
|E/REJECTED_PREACCESS_1_RECEIPT.json|5648bc30b6914703ae9afcfb58d60285d79758bc9343d8804cd5b98847cb73d7|
|paper16_m1/M1_FREEZE_MANIFEST.json|a9e787ae990fda13eb0b1899b9dd2d7e57c039c7b33f6630f3729fd27c19cab6|
|paper16_dev/STOP_FREEZE_MANIFEST.json|e25405af06b877cce70892ee2770183f813fa24d5cdc329fd7b17a4a723c7140|

`E` is `ops/evidence/2026-10-18/p16-m2-native-link-diagnostic-r1`. All original registered source identity and historical failure pins match. Reviewer writers are **COMPLETE/quiescent** after sealing this report. No scientific success or actual source finding is asserted before the one authorized inspection.
