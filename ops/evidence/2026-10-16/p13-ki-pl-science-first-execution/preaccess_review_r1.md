# Independent preaccess review r1

Mission: `P13-KI-PL-SCIENCE-FIRST-EXECUTION`.
Reviewed UTC: 2026-10-16T15:08:00Z.
Reviewer: separate local reviewer agent; internal scientific/evidence/code review, not external peer review.
Decision: **REQUEST_CHANGES — REAL NEURAL ACCESS NOT APPROVED**.
P0: **0**. P1: **2**.
Authorization assessment: **MATERIAL_AUTHORIZATION_AMBIGUITY — OWNER DECISION REQUIRED BEFORE REAL SOURCE ACCESS**.

## Reviewed state and executed checks

Read the exact copied owner authorization, all 86 atomic baseline requirements, golden standards, activation/allocation/source-boundary documents, activation/source/QC implementation and all preaccess tests. Reviewed candidate `PREACCESS_FREEZE.json` SHA256 is `527af05a29bafd908b64d88737d93bd5147e8d9772303b5fd77e0d8d3724c904`. All **10** preaccess hashes independently match. All **85** original reviewed-contract/source hashes also independently match.

Executed `python -B -m unittest paper13_ki_execution1.test_preaccess -v`: exit **0**, **16 tests PASS**. Tests use synthetic in-memory arrays/HDF5 only. A separate PowerShell here-string piped to `python -B -` independently compared the 19 allocated records against preserved metadata: exact assets/ETags/header hashes, PL unit row/electrode/label maps and numeric ordering, first 120 refined valid epochs, and A60/B30/E30 versus C60/D60 assignments all match. The proposed 10-development/9-final identity allocation and original 25-animal reference are retained. M1 identity/metadata allocation is supported; real physiological eligibility is unmeasured.

No real neural source, public-source network request or model fit was accessed. No package source, tests, activation, allocation or historical evidence was modified by the reviewer. Only this new review file is written. A second synthetic pipeline experiment, described below, exposed a pre-QC sanitization defect despite the passing direct-screen tests.

## P1 findings

### P1 — Owner must resolve raw D decoding versus the locked D access boundary

Evidence: copied `USER_MISSION.txt:18`, `USER_MISSION.txt:52`, `USER_MISSION.txt:58-60`, `USER_MISSION.txt:76`, `USER_MISSION.txt:92`, `USER_MISSION.txt:149`; activated protocol's unexposed-D/final-release boundary; `paper13_ki_execution1/source.py:98-115`; `SOURCE_BOUNDARY.md`.

The owner authorizes **permitted train/calibration neural access**, requires final D to remain locked, explicitly says **"Do not access D"**, and supplies prerequisites **before opening D**. The source implementation instead decodes each examined unit's entire `spike_times[lo:hi]` full-record values into a NumPy array before clipping to A/C. For final mice this includes D timestamps. This is decoded neural content, not merely opaque adjacent bytes or a storage index. The boundary document is candid about this difference, but an analyst-authored document cannot supply owner permission for it.

Two materially different readings remain plausible: (1) trusted raw ingestion may decode D internally provided D-derived scientific values/statistics never leave the adapter or influence A/C; (2) D neural values themselves must not be decoded before release. The owner rejected keys/ledger/multiprincipal custody, but that establishes the trusted execution environment, not which of these access semantics is intended. The explicit permission to access curated timestamps also does not uniquely resolve its immediately constrained train/calibration scope.

The canaries support **noninterference of A/C exported values/QC** under tested excluded-value changes. They do not establish that D was unread, independently blinded or authorized to be decoded. The existing test denying partition `D` export prevents that API request; it does not prevent `C` export from first decoding D inside `load_unit`. This review therefore cannot approve preaccess by treating a useful noninterference property as permission.

**Required owner decision:** may the trusted source adapter transiently decode each examined unit's full-record curated timestamp array, including locked D timestamps, solely to extract frozen A/C windows, with no B/E/D neural values/counts/statistics/QC/scalers/scores exported, retained as decoded outputs, inspected or used before their gate? If yes, record that exact exception and its limits before re-freeze/re-review. If no, retain the strict no-D-decoding boundary and obtain a contract-valid time-window-indexed/partitioned source or approved export before real neural reads. Do not silently alter "access" to mean only "export."

Material ambiguity gate: authoritative evidence does not uniquely select these interpretations; choosing changes neural access and final-holdout semantics; neither implementation convenience nor a reversible local script is a contract-preserving default; the minimum owner decision is concrete and immediately unlocks source design. Accordingly the correct human blocker is **WAIT_FOR_HUMAN_INPUT**, not NEED_ENV, a scientific numerical failure or a data-insufficiency verdict. All remaining safe independent engineering work can continue without neural access.

### P1 — Window clipping silently removes malformed nonfinite source timestamps before QC

Evidence: `source.py:98-100`, `source.py:110-115`, `qc.py` finite screen; baseline REQ-018 and owner finite/strict-order QC requirement.

`cut_windows` selects by `(times>=start)&(times<stop)`. NaN and infinities fail these comparisons and disappear before `screen` can evaluate finiteness. The existing nonfinite test calls `screen` directly, so it does not exercise this source-to-QC path.

Independent synthetic end-to-end reproduction used one in-memory ragged unit with 60 C windows, each containing three valid spikes, and inserted one NaN between valid observations in the raw source array. `unit_window_export` discarded the NaN; all exported windows were finite and `screen` returned **pass=True, training_spikes=180**. Thus the pipeline can certify QC after silently sanitizing malformed source values. A nonfinite timestamp has no trustworthy temporal assignment; it cannot simply be proven outside A/C by the same comparison that discards it.

Required correction: define and implement a fail-closed source-integrity path for nonfinite/unassignable observations, distinct from full-record physiological QC or held-out rate/order screening. Do not silently clean or rank units using excluded-period quality. The policy must respect the owner-resolved raw-access boundary above; if the trusted decoder is authorized, structurally invalid timestamp input should produce an explicit preserved source-integrity failure rather than an invented finite training record. Add an end-to-end synthetic `load_unit -> unit_window_export -> QC` regression proving malformed values cannot vanish into PASS, then freeze/re-review the corrected source. No real values are needed to fix this defect.

## Supported implementation properties and limits

The source is pinned to the activated 19 assets, exact ETags, sizes and Content-Range values. It rejects soft/external/virtual dataset paths, invalid ragged bounds and unauthorized partition exports before requested value access. The frozen local unit-row identity check and metadata allocation are correct. Network retries and bounded opaque caching are ordinary trusted source engineering, not P12 custody architecture. No provider/clock/anatomy certainty beyond the frozen metadata is claimed.

The operational QC and binning directly preserve the required 60-window/180-second exposure, within-epoch adjacent ISIs, rate/occupancy/minimum-count/refractory gates, numeric first-eight passing selection, no cross-gap ISIs, 100-ms bins and 500-ms warm-up. It records attempted QC and unexamined remaining units rather than labeling every unit good. Passing these synthetic properties is not real M2 admission or validation of any future baseline/dynamical model.

No B/E/D export or fitting has occurred in the reviewed state. No current source exposure or scientific leakage is alleged: the problematic adapter has not been used on real neural input. The review prevents a consequential ambiguous action before it occurs. The owner's M1/M2 activation is valid; approval of this particular full-record-decoding implementation is the unresolved part.

## Next gate

Do **not** issue an accepted `PREACCESS_APPROVAL.json` for this candidate or call real `SourceReader`/QC. Preserve this failed review. Complete the safe synthetic source-integrity repair, obtain the exact owner access decision, update only authorized boundary/implementation evidence, freeze a new candidate and obtain independent preaccess re-review. No M2 scientific PASS, actual eligible-mouse count, model result or final release is certified here. Git commit/push/readback/clean gates remain outside this preaccess approval and cannot be certified prospectively.
