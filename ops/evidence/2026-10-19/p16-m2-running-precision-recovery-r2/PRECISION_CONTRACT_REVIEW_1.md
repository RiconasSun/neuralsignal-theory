# Independent R2 precision-contract review 1

Mission: `P16-M2-RUNNING-PRECISION-RECOVERY-R2`.
Exact BASE: `67188e8e53a5c9a6c2ae7835b8b29aab7768db9e`.
Current contract-candidate decision: **REPAIR_REQUIRED**.
Open P0: **0**. Open P1: **2**.
Normative M1 precision finding: **SOURCE_STORAGE_COMPUTE_CLARIFICATION_SUPPORTED**.

This is independent internal scientific/contract review only. It is not preaccess approval, reader certification, source-value validation, successful recovery, archival approval or third-party review. No real source, NWB, numeric/neural array, Final, network, fit, likelihood or AD/FD was accessed or executed. No new reader was written. Only this report was written.

## M1 storage-versus-computation decision

I compared the complete current M1 normative machine-readable files and their co-normative source, stimulus, equations, numerical, statistics, controls and holdout documents, with the current R2 owner request and the executed M2 implementation. I found **no explicit normative M1 requirement that rotation SOURCE STORAGE be float64**. Therefore the owner condition requiring `CONTRACT_AMENDMENT_REQUIRED` on finding that specific contradiction is not triggered by the reviewed M1 text.

This conclusion is based on positive identification of each relevant precision clause, not treating the numerical policy as optional:

|Normative surface|Relevant requirement and scope|Rotation source float64 mandate?|
|---|---|---|
|M1_SCIENTIFIC_PROTOCOL.md, final paragraph|Names protocol.json, NUMERICAL_POLICY.json and controls.json as normative, with source/equations/QC/statistics/null/holdout documents co-normative. Mandatory source/numerical failure STOP remains.|No specific rotation storage rule.|
|protocol.json, behavior.primary/series/source_unit/availability/source_zero_removal/raw_transform|Native net rotation radians divided by native same-row end minus start; exact named running series; no processed velocity/dx fallback; strictly past parent, duration/age limits, explicit missingness and 50% role/color availability.|No source dtype constraint for rotation.|
|SOURCE_OBSERVATION_QC.md:5|“Native timing arrays/IDs preserve binary64 bits.” The context is native timing, stimulus support and observation masks.|Rotation increments are not timing arrays; this clause cannot be extended silently to their source storage.|
|SOURCE_OBSERVATION_QC.md:13|Same-row net_rotation radians / actual native end−start; duration(0,.1], end strictly before bin, age(0,.1], no invalid overlap, latest valid interval, missing near-zero-deleted rows; tanh/r²/color*r/missing.|No source rotation dtype constraint.|
|STIMULUS_CONTRACT.md:5,7 and final paragraph|Native float64 onset/stop stimulus metadata; original IDs/order and binary NPZ timing, no decimal reconstruction.|Stimulus timing contract, not wheel increment source storage.|
|FEATURE_AND_MODEL_EQUATIONS.md, nuisance and final numerical/compute clauses|Frozen running nuisances and float64-safe exponential bounds; explicitly refers to NUMERICAL_POLICY as numerical/compute contract.|Arithmetic/model requirements, no raw rotation storage mandate.|
|NUMERICAL_POLICY.json:3 and objective/certificate clauses|`dtype: float64`, with model objective, initialization, gradients, bounds, optimization and fixed derivative certificates.|Requires binary64 computation. It does not identify HDF5 rotation storage or prohibit exact promotion of lower-precision source increments.|
|controls.json and FALSIFICATION_AND_SENSITIVITY_PLAN.md|Running complete-case/missingness robustness, identical masks/targets and mandatory numerical-failure precedence.|No alternate rotation storage requirement.|
|STATISTICAL_ANALYSIS_PLAN.md; BO_FC_TRANSPORT_PLAN.md|Equal-mouse statistics and fixed coverage/transport floors; no outcome-driven replacement.|No rotation dtype clause.|
|EVALUATION_BOUNDARY.md; A1_A10_PROSPECTIVE_CLAIM_AUDIT.md; README.md|Role isolation, future authorization, source/production gates and limited claim scope.|No rotation dtype clause.|

I also inspected the M1 executable specification and metadata checks. `code/spec.py:past_rotation` expresses the same running arithmetic and finite/causal input conditions without a source-storage dtype requirement. `code/roster_metadata.py:evaluate` requires float64 stimulus start/stop and integer IDs; `code/verify.py`'s binary64 check is specifically over `['start','stop']`. Neither is a hidden rotation-source storage oracle. Historical superseded drafts and rejected candidates are preserved evidence, not replacements for the current accepted normative texts.

In contrast, unchanged executed `paper16_dev/source_running.py:134` applies `dtype == np.dtype('float64')` to **all `[rot, ts, end]`** at the HDF5 dataset boundary. Unchanged `m2_core.py:running_features` also expects an already-float64 computation array for rotation. The former is the implementation's extra source-storage restriction; the latter is consistent with promoting native float32 increments before binary64 arithmetic. The all-three source guard is real historical behavior and cannot be rewritten retroactively, but its mere existence does not establish an otherwise absent M1 scientific source-storage requirement. R1's B diagnosis under that executed contract remains correct and immutable.

Every finite IEEE binary32 value has an exact binary64 representation (binary32 significand/exponent range is contained in binary64). Accordingly, prospectively preserving the native float32 increment array and exactly promoting it for the unchanged binary64 interval division and tanh can preserve the registered mathematical estimand. This is not recovery of extra source/sensor precision. Future tests and actual first-source evidence must still demonstrate original dtype/bit preservation, signed-zero/extreme/subnormal roundtrip, finite-value rejection, original binary64 timestamp bytes, source identity/units/scaling, same-row provenance/order/duration, restricted alias identity, missingness and causal lookup. None is established by this contract review.

## P1-1 — current golden standard narrows the accepted rotation input class

Location: `goldenstandards.md:5`: “Otherwise new version permits only nativefloat32 rotation”.

The requested prospective repair adds native `<f4` support while preserving the previously accepted native float64 rotation case for other original Development sources. The current unqualified “only” freezes a narrower reader input class instead. It can reject an original `<f8` source without any scientific need, despite the identical original running semantics and the no-silent-shrink preservation rule. It also differs from the implementation contract proposed to this reviewer. No real source result is available or needed to identify that discrepancy.

Required prospective correction: distinguish **the first diagnosed session's expected `<f4` source** from the **cohort reader's accepted source classes `<f4` and existing `<f8`**. Preserve native storage bytes/dtype; promote only finite `<f4` exactly, keep finite `<f8` unchanged, and retain binary64 timestamps only. Other dtypes/scaling remain denied. This correction must precede source implementation/registration and does not authorize changing M1, the old reader, R1 or the frozen owner baseline.

## P1-2 — proposed first-source continuation conflicts with the latest owner gate

Locations: current owner `OWNER_REQUEST.txt:140,148,152`, compared with `goldenstandards.md:9` and the proposed interpretation that only first-source compatibility/numerical failure stops remaining-source access.

Owner §5 explicitly includes “Frozen role/color running coverage” in the first-source verification list and then states “If the source fails these requirements, STOP.” Section6 permits the remaining27 only after the first corrected source passes. The older M2 implementation's loop records coverage failure as negative eligibility and continues other sources, but that historical loop cannot override this newer explicit first-source condition. The current golden wording does not preserve that first-source coverage stop, and therefore could authorize the other27 after a first-source coverage failure. That is a consequential access-boundary difference, not merely a reporting distinction.

Required correction: follow the current owner literally. First session750749662 must pass source/identity/representation/numerical gates **and** every original A/B/E×color direct `role_coverage` coverage gate (at least50% available bins plus original A30/B8/E8 presentation floor) before any of the remaining27 is attempted. If that first source has valid arrays but fails the coverage predicate, retain it as a **source-valid, coverage-negative** result and STOP; remaining27 are NOT_ATTEMPTED. This cannot establish that the entire original cohort is impossible. No alternate session, retry, mask selection or optimistic bound may bypass the first-source authorization gate. Following this literal owner condition resolves the conflict without inventing user intent or changing the owner baseline.

The parent has acknowledged both prospective documentation defects and stated the above corrections will be preserved/versioned before implementation. This report certifies the present uncorrected candidate as REPAIR_REQUIRED; that acknowledgement is not retrospective acceptance of changed bytes.

## Validity, eligibility and original potential-coverage bound

Outside the newer first-source access condition, the requested distinction is supported by the frozen original implementation:

* A valid source must have correct identity/schema/units/scaling/finite ordered native arrays, positive durations and causal/missingness behavior. An integrity/compatibility/mandatory numerical failure remains STOP, not “coverage unavailable.”
* `m2_core.py:role_coverage` reports direct coverage by A/B/E×color: full source-valid presentation count, six-bin denominator, available count/fraction and the original threshold/floor predicate. Legitimate low availability is negative behavioral eligibility, not an unsafe link or invalid source representation.
* Its `possible_after_observation_support` is only an **optimistic upper bound**: for each role/color take the greatest available-bin counts across the minimum allowed number of original presentations. The original preregistered mask-bound clarification explicitly forbids using that calculation to select the analysis mask. Selected-unit/common support is unknown during this running-only mission. A possible bound does not prove such a common mask exists or qualify biological admission; an impossible bound can exclude that mouse from potential admission.
* `admission_possible` counts only records passing all potential role/color predicates and retains the original **14 total /3 BO /10 FC** floor. No source or subject replacement is permitted. For the remaining27, once they are actually authorized by the first-source pass, valid-source low coverage can be retained as a negative eligibility record and incorporated into the original cohort aggregate. Later compatibility/numerical failures still STOP and preserve unattempted identities.

No physiological, cohort-wide source, potential cohort viability, fit, B/E or Final outcome can be asserted now. The original all55/28Dev/27Final identities, all thresholds, models, role splits, controls and budgets remain unchanged. This review grants no automatic M2–M5 continuation.

## Exact checked identities and preservation

I independently checked every declared SHA256/size in the current334 M1,58 M2 and100 R1 freezes: all match. Exact BASE/HEAD matches the owner; current changes are only the new R2 P/E namespaces. No old scientific/source evidence was modified. The current R2 baseline has197 rows (191 owner nonempty lines plus six preservation/review/closure conditions) and remains prospective.

All hashes below are SHA256. `E/` expands to `ops/evidence/2026-10-19/p16-m2-running-precision-recovery-r2/`.

|File|SHA256|
|---|---|
|E/OWNER_REQUEST.txt|129ad77a54b8a909495f7f8ccc031a65e773053bb8dc1b2003d5feb38bbb6c72|
|E/baseline.json|1b27d6cdfd34d813028b2a4d8cf72b70f2b3397ea43afccac5eefe70dec9e7f7|
|E/goldenstandards.md (rejected current wording)|c009a1610c551eb1394d4a0cba5b502ec06365d957813ad05354102e91fae786|
|paper16_running_r2/MISSION_SPEC.json|585b0f6ec15a75ea4b491ff832a6625d7b1a0fda004582f5486b9a26dbc161da|
|paper16_m1/M1_FREEZE_MANIFEST.json|a9e787ae990fda13eb0b1899b9dd2d7e57c039c7b33f6630f3729fd27c19cab6|
|paper16_m1/M1_SCIENTIFIC_PROTOCOL.md|26e208f18bc68f970ea5ffc04e554419115cfd1456fb77a1ccd51c1dd5aff5f3|
|paper16_m1/protocol.json|36d074bdf8af121346d444a1f3b2eaf0b235c1327e88701d33863ad6c7f85746|
|paper16_m1/SOURCE_OBSERVATION_QC.md|0fdb5e57a0b1e7de1559704b1926d42c1a099cab5534fb8dd6f43d6183f83214|
|paper16_m1/STIMULUS_CONTRACT.md|cc00f9cda6f9ef95a0b5c3e2a3c30817e031b54f0b0f6673dbcc85b0b0db0b99|
|paper16_m1/FEATURE_AND_MODEL_EQUATIONS.md|c77bae6b9e221431c677633bb9502a85149dc977918eed01fd58b5c994d0fccc|
|paper16_m1/NUMERICAL_POLICY.json|9409657df46117ef20cfbde078898aa5346d448b974a5e86f3997238d07b49b8|
|paper16_m1/controls.json|5ea6b238ad854e7cbff62985a2a79aa36cc7d9957056f4cd7c435df7ce5961a7|
|paper16_m1/FALSIFICATION_AND_SENSITIVITY_PLAN.md|7ed3dee978efdc28e831d6e03557e44b4634771d4b52d78ef0148437e40ac42b|
|paper16_m1/STATISTICAL_ANALYSIS_PLAN.md|31172581801620e73ff7b34ed7fb2492ec53ee5aedb0d9c13a7e88f626ef6669|
|paper16_m1/BO_FC_TRANSPORT_PLAN.md|9b28c54749013731496e40b1a69d7bf9761d9bfc377829d5125b6a5f0593f9c1|
|paper16_m1/EVALUATION_BOUNDARY.md|de51ccd7b88fbc5cf48404a637cfd3858dcdaf844440077d4367b1ce3c0a79c8|
|paper16_m1/A1_A10_PROSPECTIVE_CLAIM_AUDIT.md|e528c59db8e52e6f4484696524f7f6d812acdbb6181b28fd8037fddae6f7f8a5|
|paper16_m1/README.md|74da07eda52cf721d2778b0af0a3c9327be5ee72b6b8f34318458c8dea0ad6e1|
|paper16_m1/code/spec.py|2e8daa11c9205893c24309f34379218847000d0a6895de8c5ea62eb2f644d01f|
|paper16_m1/code/roster_metadata.py|c50c3b913761f3e827415cc6528a0ade17ff14ae889b964cef4d9d08647c93a1|
|paper16_m1/code/verify.py|48774c06c18454ff47ac3033ec1a8c3a12b935cb6a351531bdf49a9c0078095c|
|paper16_dev/STOP_FREEZE_MANIFEST.json|e25405af06b877cce70892ee2770183f813fa24d5cdc329fd7b17a4a723c7140|
|paper16_dev/source_running.py|fc2edbea4e0ec958e5c11d147cc57de4dec063e8ecfd2d7b1add726f887efa33|
|paper16_dev/m2_core.py|f275c78f54b203d2a426ec28aadb26ad3d6cdd47ebc3365fdc5432e896a76eee|
|ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/M2_MASK_BOUND_CLARIFICATION.json|7c568e795881d1c074e0e967c7895f969a5a671e30a1c041752c3744bd59272c|
|paper16_linkdiag_r1/DIAGNOSTIC_FREEZE_MANIFEST.json|ce6670ca01bdad66c71fc769557962feaad65037c943f865f1078a84cc3ab284|

The precision clarification itself is supported; the two current prospective contract defects must be repaired and independently rereviewed. No real access is approved by either conclusion. Reviewer writers **COMPLETE / QUIESCENT** after sealing this report.
