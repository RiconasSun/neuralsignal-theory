# Independent single-object metadata preaccess review 1

Mission: `P16-M2-NATIVE-LINK-DIAGNOSTIC-R1`.

Decision: **REPAIR_REQUIRED**. Open P0: **0**. Open P1: **1**. No actual source inspection is admitted by this report. Preserve this candidate/review and obtain fresh exact-source re-review after the metadata-classification repair. This is independent internal scientific/source review, not third-party custody or external peer review.

## Identity and scope

BASE `a0065c66aaa84ad39a985903fcd77bdc1e1e711c`. Read the complete current owner request,247-row baseline/goldenstandards, upstream audit, access registration, offline failure analysis, complete link inspector/transport/worker/supervisor and tests. All247 owner-linked rows exactly match their UTF8 source lines. Independently verified every334 M1 and58 M2 payload hash/byte count and all registration prior-source pins: unchanged.

Only this report was written. Testing used synthetic in-memory HDF5, mocked HTTP and fixed synthetic child processes. No network, real NWB/source object, dataset/scalar value, running/neural array, fit, QC, M2 restart or Final access occurred.

The exact approved source would be only Development mouse726162197/session750749662/file1026124242, declared size2818447324 and ETag `"5a68875f05100"`. This is a new bounded metadata diagnosis, not a retry or retrospective repair of the stopped M2 scientific attempt.

## P1 — Outcome A ignores metadata-visible contradictions to the unchanged source contract

Location: `paper16_linkdiag_r1/links.py`, `Inspector.run` compatibility checks.

The inspector records canonical timestamp unit metadata but outcome A currently checks only matching object identity, binary64/vector/equal shapes and rotation-data units/scaling. It can therefore report `INTERNAL_LINK_METADATA_COMPATIBLE` despite safely observed metadata that contradict the unchanged native running reader contract.

Reviewer synthetic counterexamples, with the existing legitimate internal alias fixture and `no_dataset_values()` active:

1. Set `/processing/running/running_speed/timestamps.attrs['unit']='milliseconds'`: outcome **A**, while the returned objects explicitly record milliseconds. Setting it to `unknown` also returns A.
2. Keep canonical rotation data unit radians but set the rotation parent group's unit to degrees: outcome **A**. The accepted M2 reader explicitly rejects that contradictory metadata rather than overriding/rescaling it.
3. Recreate rotation/source/end timestamp datasets with matching shape `[0]` or `[2000001]`, native float64 and correct unit attributes: outcome **A** in both cases. The unchanged M2 source contract requires `0<len<=2,000,000`.

The owner permits A only when the inspected structure supports a narrowly scoped resolver preserving the registered source semantics. Explicit seconds/scaling/rotation-unit or original row-cap incompatibilities cannot be silently left for future array validation while labeling the metadata compatible. An unknown essential unit must remain unresolved rather than being supplied from SDK intent.

Required repair: before A, check the metadata-visible existing time-unit/identity-scaling and original row-count constraints, including the alias, registered source timestamps and end timestamps; reject explicit contradictions as source-schema incompatibility and preserve essential missing/unknown metadata as inconclusive unless an authoritative native schema establishes it. Retain the existing rotation-data/parent conflict rule. Do not require a running-speed parent TimeSeries data unit such as cm/s to equal its timestamp unit—those are different quantities. Record the actual observed metadata and failed constraint. Add focused no-value synthetic regressions for the demonstrated cases. Do not change time units, rescale timestamps, alter the2,000,000 ceiling, infer biology, or modify M1/M2 historical code.

These cases belong to one compatibility-classification defect family. The link's literal target and structural object identity may still be separately reported; they are not a reason to ignore contradictory source metadata.

## Other preaccess checks

- The hard-link-only old failure tree is accurately described. The old generic exception cannot establish missing/soft/external/cyclic/corrupt versus legitimate alias. Historical39 requests/81912 payload/81951 reserved bytes, failed attempt and27 unattempted sources remain immutable.
- Logical access is restricted before lookup to the nine registered running paths/prefixes plus root metadata and predeclared identity metadata paths. The current live path list does not read identity dataset values. Root attrs and small allowlisted attributes/shape/dtype/object addresses are metadata only.
- `getlink=True` inspects one flat component before dereference. Only a HardLink component is directly opened. External links are recorded and rejected without opening another file; unknown/intermediate/neural targets and cycles are rejected. A registered SoftLink is recorded before target validation, then only the fixed authorized target is manually traversed. No unrestricted `file[path]` resolver is substituted into M2.
- Literal target, normalized candidate and expected-path match are distinct from actual resolved same-file/object-address evidence. Relative targets containing `..` remain unresolved; lexical normalization is not claimed as native resolution proof. Matching shapes alone do not establish object identity or timing equivalence.
- Dataset getitem/array/iteration/read_direct canaries block common value APIs, including identity scalars. The inspected production code uses no low-level data read or chunk inspection. Same-row numeric timing, durations, finite/order checks, behavior coverage and all physiological assertions remain outside this mission.
- Transport is pinned to one file ID/size/ETag, exact206/Content-Range/length and finite request chunks. Reservations precede each request and are durably journaled; payload-chunk byte counts/headers/completed range hashes and component events are persisted. The current code does **not** retain raw response bodies, so saved-only reproduction cannot re-decode HDF5 links from these hashes alone.
-8MiB reservation/payload ceiling,128 requests,131072-byte chunks,600-second external parent watchdog and cooperative cached/request deadlines are implemented without retry. Exclusive parent and child claims prevent a second invocation. In-flight/partial byte uncertainty remains conservatively bounded rather than falsely exact. A timely parent/complete child receipt is required before accepting an actual outcome; a diagnostic result never restarts M2.
- The source approval gate requires the four exact implementation/registration/test hashes, zero integer P0/P1 and canonical report hash, plus immutable historical source pins. Future approval must bind the repaired bytes, not this rejected candidate.

Q1–Q5 remain unobserved until the authorized single actual inspection: exact failing component, link class, literal/candidate, target identity and strength of identity evidence cannot be filled with synthetic results. Q6–Q7 require the actual metadata compatibility assessment, including the P1 repair above. Q8 must retain all later numeric row/causality/coverage/physiology assertions as unvalidated. Any proposed future resolver is conditional on actual A and needs separate authorization; there is no production activation here.

## Independently executed synthetic checks

Executed `paper16_m1/work/runtime/Scripts/python.exe -B -m unittest paper16_linkdiag_r1.test_diagnostic -v`: observed exit0, **11/11 tests PASS**. The extra counterexamples above expose missing classification coverage despite that PASS. The existing tests cover safe alias identity versus shape coincidence, hard/missing/soft/external/cyclic/relative/unexpected/neural paths, no-value canaries, HTTP/source identity/reservations/cache/partial body accounting and watchdog/duplicate attempt denial.

Investigated the possible h5py callback exception-wrapping concern. On a valid flushed synthetic file, injecting ResourceLimit at all34 actually reached callback positions propagated ResourceLimit directly in the pinned environment;66 later injection points completed without reaching the limit. No ResourceLimit-to-OSError P1 was established. The initial unflushed reviewer image produced an unrelated invalid-header error; the flushed positive baseline passed before drawing conclusions. A durable resource-exhaustion marker would be a defensive improvement, not an experimentally established defect here.

Retaining completed bounded metadata response bodies with fail-on-missing-range offline replay would strengthen independent reproducibility without extra GETs. It is a justified prospective improvement under the unchanged budget, not a standalone mandatory P1 when execution-backed journal reproduction and its limits are described honestly. Do not claim raw HDF5 replay without retained bytes. Likewise, snapshot-copying initial component events would align in-memory pending rows with the already append-only JSONL; current JSONL serializes before later resolution and is not silently rewritten.

## Exact reviewed hashes

|Path|SHA256|
|---|---|
|paper16_linkdiag_r1/ACCESS_REGISTRATION.json|8fbe75e4053e9cd65e148098a3b400aea97760245e4064b19a36461937a56177|
|paper16_linkdiag_r1/links.py|24154be9d85001274b3158cbcce83ce837c3a9982563223e6d65db6237d5b4be|
|paper16_linkdiag_r1/inspect_source.py|a16946405f2676e8c3e60158b51c0126a60f0687adb933a99144ede8c1cdde2f|
|paper16_linkdiag_r1/test_diagnostic.py|c5435a460418ceb346742bd7ca6c59158e0557344baa10dac67f6d0e30cd83b0|
|paper16_linkdiag_r1/OFFLINE_FAILURE_ANALYSIS.md|252f41896cda6849dd99b54811cceeb0ae14aeacf9fb532f1730ac0a9c6dfc5b|
|E/OWNER_REQUEST.txt|639855609c68618895eceb8dc51f25487778ea1f60543ec51a3d296933e48604|
|E/baseline.json|ab01d85c87a856bcbedefdb1d47dc98b9d9286ae2ad336d8019e36b1f9ae2cd1|
|E/goldenstandards.md|b451437cac81f4c5962775143e804d08d2d8c20b6b0af52b3434fac0952c37d0|
|E/UPSTREAM_HASH_AUDIT.json|84bb8d1aaa5948ed214900c57a912ba28071873beabc2ed857a8d547e1925fb3|

`E` is `ops/evidence/2026-10-18/p16-m2-native-link-diagnostic-r1`. No additional P0/P1 was established in the complete metadata-only preaccess scope. No source access is required for the repair or regression tests. Reviewer writers are **COMPLETE/quiescent** after sealing this report.
