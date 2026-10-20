# Independent pre-execution review, revision2

MISSION: P16-NUMERICAL-TERMINATION-POLICY-FEASIBILITY-1

Decision: **REQUEST_CHANGES**. open_P0=0; open_P1=1 (P1-01 remains partially unresolved). No prefit approval is issued. Real A remains unstarted and prohibited until independent acceptance.

## P1-01: validate interruption evidence and journal ordering

The saved-only repair correctly preserves one consumed attempt, allows unavailable endpoint/certificate fields, rejects numerical PASS on incomplete evidence, and avoids reconstructing missing endpoints. However, `reproduce.check_incomplete` treats existence of STOP.json, SUPERVISION.json or EXECUTION_FAILURE.json as sufficient interruption proof without loading or validating any of their contents. Empty/invalid STOP content or a normally successful supervision receipt can therefore qualify. The surrounding real verification checks claim limits but does not compare the consumed claim's stage to saved STAGE.json.

Filtering CALLS by known event names also silently discards unknown events and fails to preserve the reservation/completion ordering. Reviewer independently demonstrated with pure in-memory mocked saved inputs, without any files or scientific execution:

- `[UNKNOWN(call77)]` is accepted and reported as zero FG.
- `[COMPLETED(call1), RESERVED_BEFORE_EVALUATION(call1)]` is accepted and reported as a complete FG pair.

These contradict the requested partial-evidence reproduction and fail-closed journal checks from review1. They affect owner R-108 (complete journals), R-121–123 (evidence-supported exact INCONCLUSIVE/STOP), R-138 (resource/access ledger), and R-142 (saved-only reproduction). They do not demonstrate a worker, model or numerical-policy defect.

Complete the same narrow saved-only repair: parse and validate the actual observed STOP/failure or abnormal supervision/deadline reason; bind claim.stage to saved STAGE; reject unknown journal events and require contiguous alternating reservation/completion pairs with at most the final reservation unfinished; retain original caps and explicit missing scientific values. Add pure saved negative regressions for invalid/missing interruption contents, normal supervision masquerading as STOP, stage mismatch and the two demonstrated journal defects. Do not add real attempts, rerun the four optimization fixtures, change worker mathematics, or reinterpret the old R3 STOP.

## Confirmed preservation and valid work

Independently verified all43 revision2 prefit payload identities and all19 original CODE_FREEZE entries. Code freeze remains 9f43af1408f83f7f888159857b59c9acbe11e25b084b0cc8ac0f6ed6ec51d006. The exact worker/broker/math/policy/testing surface from review1 is unchanged, so its15 native synthetic checks and saved four-fixture assessment remain applicable. Reviewer reran only the seven new pure saved-state regressions:7/7 PASS; their missing negative cases are documented above. No optimization, objective/gradient evaluation, real A raw/y access, B/E/Final access or policy tuning occurred. REAL_CLAIM.json remains absent.

Revision1 review, old reproducer and manifest are preserved. Other conclusions of review1 stand, with no additional P0/P1 discovered. Preserve this unsuccessful revision2 review and its exact candidate before the next narrow repair. This is an execution prerequisite review, not scientific outcome acceptance.

## Binding

Revision2 PREFIT_MANIFEST.json SHA256: bdce8651014a182dabd5acd81b6448394920ae212c5313b1065f7cf070adcc80 (43 payloads).

Current reproduce.py SHA256: 4f460629ff52c7f3261cfb036621b5a5a19ba9f46e86a16b9dad5af0e37fcb21

Current test_saved.py SHA256: ea830a4700b6f39cae34e1a54691b3e22128f3089032528a5200f0fe6a5b56b2

Prior review1 SHA256: 20eaabff29451fd9bfb72c6b5176d0299fc82ba3bed4df1bea1c2abd3f9d87c0.
