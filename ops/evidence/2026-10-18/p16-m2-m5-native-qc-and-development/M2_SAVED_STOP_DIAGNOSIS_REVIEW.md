# Independent saved-evidence M2 stop diagnosis

Mission: `P16-M2-M5-NATIVE-QC-AND-DEVELOPMENT`.

Decision: **ACCEPTED_SAVED_SOURCE_STOP_DIAGNOSIS**. Open reporting/claim P0: **0**. Open reporting/claim P1: **0**, subject to retaining the exact bounded conclusions below. Scientific execution outcome: **STOP_SOURCE_OR_QC**, specifically an unresolved source-reader representation compatibility gate. This is not a biological/QC exclusion, numerical-model failure, budget exhaustion or successful Development experiment. Mission archival completion remains a separate future closure gate.

## Scope

Reviewed only saved execution log/attempt/failure/supervision receipts, their bindings to the accepted reader/registration/approval, current result-file inventory and frozen source/stopping definitions. No source object, NWB, network, native behavior or neural values were opened, re-read or reacquired. No tests, fits, source repair, link-resolution experiment or retry was executed. Only this report was written. This is internal independent review, not external peer review or third-party validation.

Mission BASE remains `020388b6a8ed35d7fcba817e5f2bad4412b3dc02`. The execution reader is the accepted `source_running.py` SHA256 `fc2edbea4e0ec958e5c11d147cc57de4dec063e8ecfd2d7b1add726f887efa33`; registration SHA256 `1cff7b690e00da657116b66055091720e8273d7bf934ac1062e1e8eb1e685842`. All hashes in the saved access approval match current reviewed files; its canonical review hash matches the accepted running-only review. The prior rejected candidate and reviews retain their original status.

## Reconciled actual attempt

- One registered supervisor invocation and one first Development source attempt are evidenced. First sorted mouse is **726162197**, session **750749662**, matching the frozen registration. The other **27 Development sources are unattempted** in this operation.
- Parent supervision records child_exit **1**, child_killed **false**, valid_source_stage **false**, and elapsed **5.468 seconds** (`283645.921 − 283640.453`). Completion occurred before the four-hour deadline. This was a child source failure, not a watchdog kill or exhausted source budget.
- The failure receipt contains **39** range records. Independently summed their lengths: **81,912 payload bytes**. Reservations are **81,951 bytes**, exactly payload+39 one-byte request allowances. All recorded ranges lie within the registered object size and per-request cap. Range hashes are saved receipt evidence; absent payload bytes were not independently re-decoded by this review.
- Native value-read audit contains only `/identifier`, `/session_start_time` and `/timestamps_reference_time`. Source metadata/attribute lookup progressed further than those scalar reads, but native running rotation/start/end numeric slices had not executed at the recorded failure point. Previously saved M1 stimulus metadata were used; that does not constitute new native running or neural value access.
- There is one session STARTED claim and its corresponding `FAILED_SOURCE_STOP` receipt. The original stage STARTED claim remains preserved alongside failed supervision; it must not be silently rewritten as an unattempted or successful run.
- No running result NPZ or `M2_RUNNING_GATE.json` exists. There is no computed running-availability cohort, native behavior success gate or A physiological result from this attempt. The failure receipt reports zero neural datasets read; source control flow at the traceback is consistent with that scope.

## Exact supported diagnosis and uncertainty

The saved traceback reaches `native_running` line129, calling:

```text
hard_object(file, '/processing/running/running_wheel_rotation/timestamps')
```

`hard_object` raises at its general path/group/HardLink guard with:

```text
ValueError: External/soft/noncanonical source link denied
```

Thus the frozen reader could not traverse that requested timestamp path under its hard-link-only schema. The condition combines several possible cases and checks path components. The log does **not** identify the actual link class, which path component failed, whether a link exists, its target, or whether any target is an internal allowed timestamp dataset. It does **not** establish a soft link, external link, missing dataset, corrupted object, wrong timestamp mapping or source clock error specifically. Those are unresolved possibilities, not findings.

Control flow reached this lookup after rotation attribute checks, but the failure receipt does not preserve separate copies of those attribute values. Do not upgrade that progress to complete running semantics or row-correspondence verification. The actual numeric running arrays were not decoded and compared.

The pinned writer supports the intended same-row start-timestamp relationship and radians net_rotation semantics. It does not establish that every released NWB serialized that relationship as a hard link. A source representation incompatibility with the frozen reader is therefore a grounded interpretation; a biological running-data deficiency or intrinsically invalid Allen source is not.

## Required stopping and reporting consequences

The accepted registration/frozen M1 contract makes a mandatory source-schema failure a global STOP with no retry. Therefore the existing stopping contract requires:

1. Preserve the actual failure, all attempts, exact byte/request accounting, code/approval identities and the27 unattempted sources.
2. Stop real source execution now. Do not inspect the link in the live object, try an alternate resolver, use another source object, read the remaining27, or rerun the source operation under the current registration.
3. Do not start A-neural extraction, A physiological admission, M3 certification, A fitting, B selection, E assessment, sensitivities/references or any Final activity. The invalid parent supervision record independently fails the prerequisite for A access.
4. Report downstream stages as `NOT_RUN_PREREQUISITE_FAILED`, with effects, lambda, admission and actual behavior coverage **not established**. Zero completed fits/zero neural datasets are valid execution counts; they must not be presented as zero biological effect, zero available running coverage or28 physiologically failed mice.
5. Distinguish the failed source compatibility gate from biological QC: the first source is not physiologically assessed, and the remaining27 are unattempted rather than biological exclusions. No14/3BO/10FC impossibility calculation was completed because running availability was never computed.
6. Maintain the prospective exploratory/descriptive claim boundaries and all Final restrictions. Engineering archival PASS, if later earned, must describe closure of this evidence-backed STOP rather than completed M2–M5 science.

No scientific threshold, source mask, cohort or numerical rule needs reinterpretation to record this STOP honestly. The existing preaccess approval certifies a bounded reader implementation; it never guaranteed compatibility or a successful source gate.

## Separate possible next mission — recommendation only

If the owner elects to continue, a narrowly scoped, separately authorized and prospectively registered metadata-only diagnosis could inspect the **link representation and target metadata** for this exact failed source identity. It should distinguish missing/hard/soft/external cases without decoding running/neural arrays, remain pinned to the same object, retain all original failure evidence and use explicit small request/byte/time limits with no retry expansion. Such access is **not authorized by this report**.

Only if actual metadata justify an internal permitted link should a separate reviewed resolver enforce a finite scoped target allowlist within the same frozen object, rejecting external/arbitrary paths, cycles and unexpected targets. Synthetic tests and exact source bindings would precede any separately authorized native attempt. Do not infer that repair or its scientific success in advance; do not relax the hard-link guard ad hoc or treat a new reader as the original successful attempt.

## Exact saved evidence bindings

|Artifact|SHA256|
|---|---|
|E/M2_RUNNING_EXECUTION_1.log|344b7fed818648935e75d6ea2096b4063f2ecdb952a612ccf2388a63b4879539|
|paper16_dev/results/M2_RUNNING_ATTEMPT.json|c9df89b30344dfd258a043f75cc7363eefd3f849c24afa4be7e0311c26cd76ad|
|paper16_dev/results/M2_RUNNING_SUPERVISION.json|a20cfc001719ed0f47cd65a09763634ee336f092d2de35fab6b4f3042fe78377|
|paper16_dev/results/running/750749662.attempt.json|a4f55aa531eff805933255ee6529ad9b63d7a976de15705b55cfb18c06e05099|
|paper16_dev/results/running/750749662.failure.json|6b28b537677fae566ddfab3d9a079dd85a4c87d319c9e8f4f1e3e0593fb9374e|
|E/M2_RUNNING_ACCESS_APPROVAL.json|f73bc3512f063617657135dcf3d3db21dbbff6459f855ffa94b1c1427a513e5b|
|E/M2_RUNNING_ACCESS_REVIEW.md|be6f51a9065c86b57319a0e8c56d00cc7df0be4eb0aa830506b42bf19096ab59|

`E` is `ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development`. No unresolved reporting P0/P1 remains if the exact qualifications above are retained. Complete source root cause remains unresolved; no unsupported causal or biological diagnosis is substituted. Reviewer writers are **COMPLETE/quiescent** after sealing.
