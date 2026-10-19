# Independent R2 running-only preaccess review 1

Mission: `P16-M2-RUNNING-PRECISION-RECOVERY-R2`.
BASE: `67188e8e53a5c9a6c2ae7835b8b29aab7768db9e`.
Decision: **REPAIR_REQUIRED — NO REAL ACCESS APPROVAL**.
Open P0: **0**. Open P1: **2**.
Frozen candidate: `PREACCESS_CANDIDATE.json`, SHA256 `45290013a3a8a67079d0da7398309dc3c4e98836fcaa08c0c50863df74b0fc44`, exact12 reviewed content bindings.

This is internal independent review of the prospective source/precision/interface candidate against the full owner request, particularly §§3–8, the accepted precision contract and frozen M1/M2/R1 boundaries. It is not actual source validation, physiological QC, production/scientific PASS, or authorization for first or remaining source access. No real source/NWB/neural/Final array, network, fitting, scoring or AD/FD was used. All executable evidence below is synthetic; only this review report was written as permanent evidence.

## P1-1 — unknown worker phase bypasses independent first-source review

Location: `run_sources.py:210–220`, and the `--worker` branch of main.

The parent main path rejects unknown phases, but direct `--worker` entry calls `worker(phase, deadline)` without that validation. Inside worker, only literal `phase == 'remaining'` invokes `first_review_gate()`, while **every non-'first' phase** selects the other27 objects and expects27. Thus an unrecognized/typo worker phase can enter the remaining-source loop without the required successful first result or independent actual first-source approval. This contradicts the owner first-source condition and the interface's explicit statement that manual worker phase cannot bypass that gate.

Independent synthetic reproduction: I supplied a synthetic28-object registration and matching synthetic stage identity, mocked only actual source execution/file effects, and made `first_review_gate` raise if called. `worker('unrecognized_phase', deadline)` returned0, selected **27** synthetic nonfirst sources, selected no first source, and called the first-review gate **0** times. No real source was opened.

Required repair: reject every phase outside the fixed first/remaining set at the earliest worker entry, before stage claims, journal creation or source-side effects. Add an executable negative regression proving an unknown direct-worker phase selects/opens zero sources and creates no stage/worker/budget artifacts. All valid remaining paths must still require the complete independently bound first-source evidence and external-supervision result; do not remove that existing requirement to repair the branch.

## P1-2 — hard deadline kill can discard already decoded native vectors

Locations: `reader.py:121–123`; `run_sources.py:183,191–193,241`.

The reader captures rotation/start/end sequentially in process memory. The complete native bundle is written only after `native_running` returns. Ordinary caught exceptions can save `PARTIAL_NATIVE_SOURCE.npz`, but the registered external watchdog uses `child.kill()`: that does not execute the exception/finally branch. If a later vector read blocks past the deadline, earlier fully decoded native vectors disappear even though they were already read. The current source-interface/registration promise to retain failed/partial decoded native arrays therefore is not satisfied for the externally enforced timeout path.

Independent synthetic reproduction: an actual child process ran the actual `run_one` control flow with source/HDF5/transport calls replaced by synthetic stubs. The synthetic native reader decoded/captured a two-value float32 rotation vector, wrote a marker proving that checkpoint was reached, then blocked. The actual supervisor killed the child at a three-second deadline and returned124. The marker survived, but the session evidence directory contained **only ATTEMPT.json**, with neither partial nor complete native bundle. No real HDF5/source values or network were involved.

Required repair: durably persist each fully decoded native vector and its precision/byte identity **before reading the next vector**, using exclusive files and flush/fsync. A native manifest can bind the individual completed vector artifacts without duplicating full arrays; first-source approval and result bindings must be updated prospectively to require the exact new artifact set. Keep partial/incomplete states explicit after hard kill rather than fabricating completion, RESULT or native array hashes. Add a hard-kill regression proving already decoded vectors remain available and later vectors/attempt completion remain unpublished. Resource limits and deadline must remain unchanged.

The parent acknowledged both defects while this candidate remained frozen. Proposed fixes are not accepted by this report until preserved, prospectively registered, implemented and independently rereviewed. No candidate bytes were edited during this review.

## Checked contract and source surfaces

The supported storage-versus-computation clarification from contract review2 remains applicable. The candidate correctly preserves native `<f4` rotation bytes with finite exact cast-back equality, supports original `<f8` rotation, requires first-known `<f4`, and accepts native `<f8` timestamps without rounding or correction. `native_arrays` checks vector lengths/capacity/finite values/order/positive duration; feature derivation reuses unchanged frozen `m2_core.running_features`, `role_coverage` and `admission_possible`, checks source-array identities before/after, retains original source-row indices and encodes r/r²/color*r/missing without imputation. These correct surfaces do not clear the two control/evidence defects.

I inspected the restricted link implementation: flat getlink inspection precedes dereference; only the exact diagnosed literal alias can resolve, through canonical HardLink components, with native HDF5 ID/address and same-file comparisons. Hard aliases must match the canonical object. External/relative/cyclic/spoofed/unregistered paths are denied. Canonical dataset metadata guards constrain dtype, shape, radians/seconds and identity scaling. Rotation conversion/offset default behavior follows the historical reader rather than inventing rescaling. Three original identifier/clock scalars are compared to frozen references, with no calendar correction. Value scope permits only those scalars and registered native vectors; unrelated/neural paths and array/iteration/read_direct/partial indexing APIs are denied. This is the existing trusted-host scope, not administrator resistance.

Owner first-source direct coverage is correctly implemented in the normal first path: all original A/B/E×color floor/≥50% checks precede first-source success; failure is FIRST_SOURCE_COVERAGE_STOP and does not authorize the remaining27. Required actual first-source approval binds the declared raw/derived/attempt/stage/supervision/worker/budget snapshot set and exact report. The immutable first budget snapshot must remain a prefix before journal append. The first-review artifact set must be revised consistently with the durable-vector repair; no first-source approval is currently present or granted here.

Normal remaining-source behavior retains valid low-coverage records and the unchanged optimistic14overall/3BO/10FC bound; it never establishes A physiology from behavior. Compatibility/numerical/resource failure stops without retry or replacement. The first-source failure does not prove that the unexamined cohort is impossible. No neural extraction/QC, fits, B/E assessment, sensitivities/nulls, Final or automatic M2–M5 restart is introduced.

The normal transport path reserves before each request, enforces4096requests/object,1MiB/request,134217728 conservative bytes/object and3758096384 total, checks206/Content-Range/ETag, disables redirects, and has no retry/bulk fallback. Incremental payload and incomplete accounting are journaled. Sequential concurrency1 respects the authorized ceiling4. First-stage STAGE_ATTEMPT fixes one14400-second deadline; remaining reuses it, including first-review wall time, without resetting it. External supervision/duplicate attempt guards were inspected and tested. These controls require the two repairs above; the unknown phase may not create an alternative path, and the watchdog must not silently discard completed native reads.

## Independent verification

I independently executed all **17** frozen tests, including the actual synthetic HDF5 image → mocked exact HTTP ranges → actual reader/precision/save interface, successful first coverage and first-coverage stop. **17 PASS**,0.515seconds, pinned Python3.11.15 / NumPy2.4.6 / h5py3.16.0 / requests2.32.5. The reviewer additionally denied socket connections and requests.Session.request throughout these tests; no live request occurred. Missing/failed/incomplete first-review approvals remain rejected in the existing tests, but those tests did not cover the unknown-phase bypass. The existing timeout test confirms termination but not preservation of decoded vectors, which the additional adversarial test disproves.

The17 passing tests cover float32 extreme/subnormal/signed-zero roundtrip, float64 preservation/first dtype, unsupported/nonfinite/order/row/duration rejection, bit/mask/feature identities, strictly past/invalid/missing-zero behavior, link/security/unit/scalar/identity cases, exact HTTP/cache/partial accounting/budgets, external timeout/duplicate denial and cohort floors. They are synthetic interface evidence, not native source success.

I independently verified every hash/size in all334 M1 +58 M2 +100 R1 declared payloads (**492 unchanged**). All28 original Development objects and their original field values agree with the historical M2 registration; all27 denied Final IDs agree exactly. The30 auxiliary source references (28 original compressed clock/invalid headers, original probes metadata and successful roster index) are already covered by the immutable M1 manifest; no unbound replacement header or newly selected source was substituted. Referenced flash arrays/receipts and source interpretation code are also freeze-bound. Historical failures, BASE and scientific definitions remain intact. The R2 real `results/` directory was absent at review end.

## Exact reviewed identities

SHA256; `P/` expands to `paper16_running_r2/`, `E/` to `ops/evidence/2026-10-19/p16-m2-running-precision-recovery-r2/`. All12 candidate hashes independently matched the current bytes.

|Path|SHA256|
|---|---|
|E/PREACCESS_CANDIDATE.json|45290013a3a8a67079d0da7398309dc3c4e98836fcaa08c0c50863df74b0fc44|
|P/PRECISION_CONTRACT_DECISION.md|f880bc5ded9fb4fd0f21cd01f1869138bf9ac0e1b4ed62bab7ed09793b3e10cb|
|P/ACCESS_REGISTRATION.json|837932060ab03ef7be688f11f5d8e43111b1144217041e4abaa9dc18ce240664|
|P/precision.py|ca8da6b64512fea12df94a0a3250f14a8da76233f1b3a98fe69f0836bd093c6a|
|P/reader.py|b1ebbb9b306d36bf20be1dc393b9bb973fbd5df3166a7c53930d3a96f8007e87|
|P/run_sources.py|094f15c9affd7f4190f51f64cb942aab40c408460b4912a7d95c65c559af0e69|
|P/test_running.py|839b459ad831b28957bf797ef897d92a071f422cdb0a2d7822dec0ecceeee5ba|
|P/test_interface.py|e287d497227bd6e18e4d904503510bac102718d6d7513f1e10356724c1982e0d|
|P/READER_SOURCE_INTERFACE.md|28d40c7eccd7372cf5b89433344183252c67a70c02d02d2426e5549beeb8092a|
|E/baseline.json|1b27d6cdfd34d813028b2a4d8cf72b70f2b3397ea43afccac5eefe70dec9e7f7|
|E/goldenstandards.md|ea2264d50a94238f8dfb2f0173ae3567e0a05dd31680c9c1293fe25d141945c8|
|E/PRECISION_CONTRACT_REVIEW_2.md|89bebf9b6a26527c2304d00a92f1af8695577b177e86bd0ed8af9a3e338e3c75|
|E/SYNTHETIC_3.log|bef81e96e6fd195f32383ef4c35158cfd3048700d779b22bdd913bb12634dae5|

Additional inspected dependency identities:

|Path|SHA256|
|---|---|
|E/OWNER_REQUEST.txt|129ad77a54b8a909495f7f8ccc031a65e773053bb8dc1b2003d5feb38bbb6c72|
|P/MISSION_SPEC.json|585b0f6ec15a75ea4b491ff832a6625d7b1a0fda004582f5486b9a26dbc161da|
|paper16_dev/m2_core.py|f275c78f54b203d2a426ec28aadb26ad3d6cdd47ebc3365fdc5432e896a76eee|
|paper16_m1/code/roster_metadata.py|c50c3b913761f3e827415cc6528a0ade17ff14ae889b964cef4d9d08647c93a1|
|paper16_m1/M1_FREEZE_MANIFEST.json|a9e787ae990fda13eb0b1899b9dd2d7e57c039c7b33f6630f3729fd27c19cab6|
|paper16_dev/STOP_FREEZE_MANIFEST.json|e25405af06b877cce70892ee2770183f813fa24d5cdc329fd7b17a4a723c7140|
|paper16_linkdiag_r1/DIAGNOSTIC_FREEZE_MANIFEST.json|ce6670ca01bdad66c71fc769557962feaad65037c943f865f1078a84cc3ab284|

The two P1 findings prohibit preaccess acceptance of this candidate. Preserve this unsuccessful report and candidate before prospective repair; rereview the resulting complete executable/interface/artifact gate without weakening owner thresholds or increasing access/budget. Reviewer writers **COMPLETE / QUIESCENT** after sealing this report.
