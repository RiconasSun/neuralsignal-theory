# Independent M2 running-only preaccess review 1

Mission: `P16-M2-M5-NATIVE-QC-AND-DEVELOPMENT`.

Decision: **REPAIR_REQUIRED**. Open P0: **0**. Open P1: **2**. **No real source opening is admitted by this review.** Preserve this candidate/report, repair the two issues without changing frozen science, and obtain fresh exact-source re-review before native access. This is internal independent-agent review, not third-party custody, external peer review or scientific validation.

## Scope and identities

Mission BASE: `020388b6a8ed35d7fcba817e5f2bad4412b3dc02`. The immutable M1 scientific source manifest remains `a9e787ae990fda13eb0b1899b9dd2d7e57c039c7b33f6630f3729fd27c19cab6`,334 payloads. Independently recomputed all334 hashes and byte counts: unchanged/PASS.

Read the current owner request, goldenstandards,410-row baseline, running-access registration and mask-bound clarification, complete `m2_core.py`, `source_running.py` and `test_m2.py`, along with the applicable M1 normative source/time/QC/boundary files and pinned NWB writer/running extractor. All owner-linked baseline rows match their exact UTF8 owner source lines. Current review concerns **only running-source access and its non-neural cohort impossibility bound**. It does not certify an A-neural reader, physiological admission, M3 worker, fitting, B selection, E evaluation or any Final activity.

No network, real NWB, real neural array/count, fit, likelihood/AD/FD, or Final access was performed. Only small synthetic in-memory HDF5/HTTP fixtures and saved JSON/source/hash checks were used. Only this unique report was written.

## P1-01 — The registered source-stage deadline does not enclose the source stage

Locations: `source_running.py:167` and `main` from line196.

Registration sets a four-hour total source-stage ceiling. The implementation checks `time.monotonic() >= deadline` only immediately before an **uncached HTTP request**. It does not check expiry before local-pilot hashing or local NWB opens, between sessions, during local/source array work, before result completion writes, or before the final `RUNNING_COHORT_VIABLE_FOR_A_QC` summary. Cached reads bypass the deadline branch. HTTP uses a fixed30-second timeout even when less registered time remains, and a per-socket read timeout is not a total streaming deadline.

Reviewer synthetic demonstration: fill a RangeReader cache with a four-byte mocked response while monotonic time is0 and deadline100; seek back; change mocked time to200. `read(4)` still returns `b'1234'`. No real source request was made. Static control flow also permits the two local-object branches and final success summary after expiry. Thus the current eight tests establish a request-start check, not the registered whole-stage cap.

Required repair: enforce a stage deadline over **all** native/local/source and postprocessing paths, including pre-open/hash checks, bounded loops/chunks, cache reads, completion writes and final viability publication. Requests must be bounded by remaining time; failures must preserve attempts and yield budget STOP, with no continuation/retry or viability PASS after expiry. Because a cooperative check cannot stop a blocked native/local/streaming call, use a small enclosing process watchdog or an equivalently effective cancellation mechanism for the hard wall limit; this does not require a new custody framework. The4h limit itself must remain unchanged.

Concrete regression oracle: use synthetic/local spies or a child fixture that exceeds a short injected deadline before source access and during a blocking source operation. Assert no subsequent source open/request/next-session operation and no viable/success gate can occur; the enclosing runner terminates or cancels by its injected limit and preserves an interrupted/budget-failed attempt. Also cover cached access and expiry immediately before final summary. These tests need no real NWB or network. The source-stage4h engineering budget is distinct from the frozen future48h Development optimizer budget.

## P1-02 — Parent-group unit overrides the canonical NWB data unit

Location: `source_running.py:107`.

The pinned writer constructs `running_wheel_rotation` as a standard NWB TimeSeries with `unit='radians'`; the standard canonical unit is on its `data` dataset, as the code's own comment states. Current code uses `parent.attrs.get('unit', rot.attrs.get('unit'))`, so a group attribute can override a contradictory canonical data attribute.

Reviewer synthetic demonstration: create the existing in-memory behavior fixture with `running_wheel_rotation/data.attrs['unit']='degrees'`, then set its parent group's unit to `radians`. `native_running` accepts it and returns both rows instead of rejecting the source-unit contradiction. Downstream output would certify `native_unit='radians'` although the canonical data unit says degrees. No actual source object was opened.

Required repair: validate the canonical dataset unit directly and fail closed on conflicting/noncanonical parent unit metadata rather than letting it override the dataset. Missing/unknown/wrong unit mappings must stop before reading/using rotation values. Add a regression for the demonstrated conflict, the converse conflict and missing canonical unit. Keep the existing radians/duration formula and no velocity/raw-dx fallback. This is source-schema enforcement, not a change to the running covariate.

## Scientific/source findings otherwise established

- Registration contains exactly the28 original Development session identities. Every original M1 registration field—mouse/session/probe/name/role/protocol/file ID/size/ETag—matches; the denied set is exactly the27 original Final sessions. No source replacement, reroll or Final opening is offered by the running reader.
- The seven logical dataset paths are running rotation data, its timestamps, source running start/end timestamps and scalar identity/clocks. Allowlist rejection occurs before path lookup; soft/external links are rejected. Neural paths and processed velocity data are absent. Native generation2.2.2, session/clock identity, float64/finite/ordered rows and row-count bounds are explicit.
- Source semantics match the pinned writer/extractor: net_rotation is a radians increment, starts/end times are the same running dataframe rows, rotation timestamps alias the running-speed start timestamps, near-zero deleted rows remain missing, and no whole-session normalized velocity or raw-dx fallback is read. Unit verification still requires P1-02.
- The running transform uses net_rotation divided by actual same-row duration, then tanh(rate/10). The parent must end strictly before the target; duration and age are in(0,.1]. Equality is excluded; later rotation values do not alter earlier outputs. Both invalid parent intervals and invalid bridges between parent and target are rejected; latest remaining valid parent is used, and absent data have an explicit flag rather than inferred stationarity.
- Score targets are native onset plus anchored integer20ms multiples5..10. Original150 cuts90/30/30 and frozen known-invalid source masks are used without role recutting. Final gate reporting remains separate from actual A-only physiology.
- The optimistic coverage formula is defensible as an **upper bound**, not an admitted mask: for each role/color, the maximum achievable mean availability over any subset of at least the frozen minimum number of presentations is at most the mean of the largest `floor` available-bin counts. Allowing independent best subsets across roles/colors only makes the bound more optimistic, so failure is an impossibility certificate. The code returns counts/fractions/possibility, not chosen presentation IDs. Full-source ratio failure alone is not used to exclude an animal before unit common support is known. Final actual masks must come from source/unit support under frozen rules, not from those top-ranked availability rows.
- The cohort feasibility check retains all three14overall/3BO/10FC floors and rejects duplicate mice or unknown protocols. Its result is at most permission to consider separately reviewed A-QC execution, not physiological admission or source behavior validity by itself.
- Per-object128MiB and4096 application-request caps, at most1MiB request chunks, exact206/Content-Range/ETag/length checks, no bulk fallback, no automatic retry and exclusive stage/session attempts are present. With exactly28 unique registered objects the sum of per-object caps equals the3.5GiB total ceiling. Whole-stage timing still requires P1-01.
- Existing two local pilots are hash-checked against complete M0 transfer receipts before their behavior-only open. Any source/schema/read failure raises out of the loop, preserving failure evidence and preventing later cohort viability. Actual source receipts cannot be claimed before execution.
- The standalone physiology helper uses A-only valid disjoint windows and the unchanged spike/occupancy/rate/ISI gates. Its synthetic tests are useful component evidence, **not approval of any future native A-neural extraction or complete QC integration**.
- The review gate binds registration/core/reader/tests, M1 manifest/parser and canonical independent report hash before main source access. It requires literal integer zero P0/P1 and accepted running-only decision. A fresh approval must bind repaired source; the current report is not such an approval.

## Independently executed checks and limitations

Executed `paper16_m1/work/runtime/Scripts/python.exe -B -m unittest paper16_dev.test_m2 -v`: observed exit0, **8/8 tests PASS**. These include synthetic causality/future invariance, missingness/invalidity, A-only physiology, original-role coverage and bound, source floors, synthetic NWB/hard-link/neural canary, Final denial and request identity/budget tests. The two additional counterexamples above demonstrate missing coverage despite that PASS.

Saved verification independently checked all334 upstream hashes, exact28/27 registration source sets and complete410-row owner mapping. One initial reviewer owner-string comparison used the process locale implicitly and failed; the explicit-UTF8 recheck found zero line mismatches. This was a reviewer decoding issue, not an alteration or failure of source evidence. No source access resulted.

The source reader has not yet established actual native units/row correspondence or real running coverage; eight synthetic tests cannot establish those biological/source facts. No actual A physiology, model fit or Final claim is admitted. Do not change coverage thresholds, masks, the cohort, transform or budgets to repair these engineering defects.

## Exact checked hashes

|Path|SHA256|
|---|---|
|paper16_dev/M2_ACCESS_REGISTRATION.json|1cff7b690e00da657116b66055091720e8273d7bf934ac1062e1e8eb1e685842|
|paper16_dev/m2_core.py|f275c78f54b203d2a426ec28aadb26ad3d6cdd47ebc3365fdc5432e896a76eee|
|paper16_dev/source_running.py|71c8697850223a262308185248bea8e1c958de19e88efb46f88189f4d091b4bb|
|paper16_dev/test_m2.py|bbb42e534fb75661f930b0658fe9d55d84861b812bce00a08f5e2d327648d95b|
|OWNER_REQUEST.txt in this evidence folder|81e2b7d39442ef8d3ada302051659bd6fc9b8f55d3b3eff373283e9f609cf9f1|
|baseline.json|47d83e074716eb5b32d4fa684fd0ffadeb8d8b96bcecb6c014885ef643c05c75|
|goldenstandards.md|b21ea660e9351beff85ebd51041b90ee090be407be3a83b4d65f7ffca141bdce|
|M2_MASK_BOUND_CLARIFICATION.json|7c568e795881d1c074e0e967c7895f969a5a671e30a1c041752c3744bd59272c|
|paper16_m1/M1_FREEZE_MANIFEST.json|a9e787ae990fda13eb0b1899b9dd2d7e57c039c7b33f6630f3729fd27c19cab6|
|paper16_m1/code/roster_metadata.py|c50c3b913761f3e827415cc6528a0ade17ff14ae889b964cef4d9d08647c93a1|
|paper16_m1/metadata/nwb_writer.py.source|eaa99cc3149379075d02c09fa88a6f40a9151c5a5966ac371e2ee3888be83dbf|
|paper16_m1/metadata/running_extract.py.source|73e59cbbaaf8a6619f04d470a689c2037ccbebb20cc727cb1e6bd096287ee731|

No further P0/P1 was established in this complete running-only preaccess scope. Preserve the unsuccessful review; no source request is required to repair or test either finding. Reviewer writers are **COMPLETE/quiescent** after sealing.
