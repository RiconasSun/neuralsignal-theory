# P15 M1 independent internal scientific/mathematical review r1

Mission: P15-M1-SCIENTIFIC-PROTOCOL-FREEZE. BASE: bac678914065609bb3786ea9437fb2c5a215fb38.

Decision: **CHANGES_REQUIRED_BEFORE_COMPLETE_PROTOCOL_FREEZE**. Actionable P0: **0**. Actionable P1: **3**. This unsuccessful review must remain preserved after repair. No complete M1 acceptance or neural activation is granted.

The reviewer read the exact owner mission, all54 frozen baseline items, golden standards, scientific/source/QC/model/numerical/statistical/control documents, fixed cohort and M0 pins, A1-A10 audit, synthetic/test/reproduction code and saved design tables. The reviewer independently ran `& .\paper15_m1\reproduce.ps1`:15 synthetic tests passed and all3 design tables reproduced exactly, with the fixed cohort byte-identical and6 M0 pins verified. Networking was denied and no real neural cache, real fitting or C/D outcome was accessed. PROTOCOL_FREEZE.json is not yet present; no final freeze verification is implied. No file other than this review was edited, apart from the verifier's ignored work receipts.

## P1-001 — Per-contrast robustness/positive predicates are not fully specified

Location: STATISTICS_CONTROLS.md:15 and the eleven sensitivity definitions; NUMERICAL_SELECTION.md sensitivity scope.

The verdict rule applies the same direction/precision/robustness requirements to secondaries "when applicable", while D temporal-state wording requires "adequate sensitivities". Neither phrase maps the eleven sensitivity panels to each of the five contrasts. The registered sensitivity fits are B0-B4 only; they can compute conditional own/other-history contrasts but cannot establish D/C/S sensitivity robustness. Different implementations could therefore apply, omit or reinterpret required robustness conditions after results, despite the promise of a complete frozen claim oracle.

Required prospective repair: enumerate the exact mandatory gate/sensitivity map per contrast, including coverage, missingness and resulting labels. Conditional own/other-history sensitivity effects may use the already planned baseline fits. For D/C/S, explicitly limit the claim to the tested primary representation settings and state which interpretive controls are required; do not claim untested sensitivity robustness or silently add representation refits/search beyond the frozen budget. Replace the ambiguous applicability phrases with a deterministic decision rule. No changed scientific outcomes, animal or numerical threshold are needed to make that rule concrete before activation.

## P1-002 — Two stochastic/control operator definitions are incomplete

Location: STATISTICS_CONTROLS.md:31 and45.

S07 promises deterministic independent spike thinning but does not specify a per-unit/per-partition RNG seed or stream/order convention. The later hash recipe is stated for surrogate suites/replicates and does not unambiguously bind this sensitivity. N2 stratifies by "pre-epoch wheel displacement" without defining its exact time interval, signed/absolute quantity, strict-past boundary or median/tie handling. These choices change realized masks/strata/reference samples and cannot be left to an outcome-informed implementation.

Required prospective repair: define S07 seed mapping and stable spike order, unit/role identity, one registered draw and no retries; freeze whether selection/QC is applied before thinning. Define N2 displacement endpoints/value, strict-past sampling, the exact A/C reference median population and tie/missing-support policy. Preserve the existing fixed budgets, count-preserving/destructive-reference limitations and original/reference common exposure. This is a completeness repair, not justification for a new favorable reference operator.

## P1-003 — Future C-only extraction lacks explicit treatment of indivisible ALF arrays

Location: SOURCE_QC.md:9/13 and SCIENTIFIC_PROTOCOL.md:39.

Whole-recording ALF spike arrays can require decoding D timestamps while extracting C. The protocol requires finite/ordered/source-support checks and C-only downstream operations, and separately forbids D access until later authorization, but does not resolve whether a future reader may decode the whole source array to provide C. A worker could interpret the global source check as implicit authorization to inspect D, or another could stop. The M1 contract must not inherit a permission from a different earlier mission or let this be decided implicitly at execution.

Required narrow repair: state that M1 grants no such access; future whole-record low-level decoding requires explicit human authorization for a trusted reader before it occurs, with only authorized partitions exported/used and no D-based QC/scaling/selection/scoring. If C cannot be extracted without unauthorized D decoding, stop before C. Scope any permitted global source-integrity checks explicitly and do not expose D neural values to scientific analysis before its gate. No new cryptographic, multi-principal or external custodian system is requested; no C/D payload need be accessed in this mission.

## Reviewed areas without additional P0/P1 findings

The primary estimand B4-B1, actual unit-bin evaluation denominator versus population-bin objective normalization, factorial/exposure terms, B0 constraint solution, model nesting and nominal counts are internally coherent. HMM conditional score likelihood equals full-minus-warm marginal likelihood with differentiation through warm-up; pre-bin filtering and IID-static identity are appropriate. C uses a fixed strictly past finite projection, and the larger static comparator is paired prospectively without claiming parameter count proves equal capacity. The bounded61-per-development and1928-total fit arithmetic agrees with the specified grid/sensitivity scope. Mandatory fixed-step numerical gates cannot be cleared by optimizer success or a favorable FD step.

The20 fixed candidates and12/8 reservation remain intact;18 unknown native equivalences are not claimed admitted. The deterministic future source-resolution/QC procedure and explicit M2/production prerequisites can support a complete protocol status without fabricating completed native admission. The15 synthetic tests are honestly labeled specification oracles, not certification of an unwritten production implementation or all HMM parameter gradients. No repeated pilot audit is needed for these findings.

Mouse-level sign-flip assumptions, hypothetical-versus-measured power, bootstrap/lab dependence, attrition fallback and one-shot D restrictions are explicit. The four surrogate references are disclosed as destructive/conditional-assumption references, not exact mechanistic nulls; they cannot replace the primary animal test. No P13 unstable generator, model winner, physical primitive, independent-lab replication or causal/real-time claim is adopted. Final matrix, freeze timestamp/hash, daily and Git/archive gates remain pending separately from this review.

## Reviewed principal surface SHA256

| Surface | SHA256 |
|---|---|
| SCIENTIFIC_PROTOCOL.md | 7826435a516c5de4a709040230409cc13edf05ac69cdf63c522a14d73cfadb4d |
| SOURCE_QC.md | efc325805d6a4b726633043629f39f5f23bcbde2ae79ce38d55a34b9f696080d |
| FEATURE_MODELS.md | 37ef100353913eb2a99d92ffb9404093b2d850ce326fd6b497dec31ec2453b4e |
| NUMERICAL_POLICY.json | cc0c926b04540f1787e0a005f6566bf42225cb2bca159fd9accdd3e74ab0358e |
| NUMERICAL_SELECTION.md | 34b0ef9737954707d11d61477775d8566c93648ff6fdff46868ef08ac11331ed |
| STATISTICS_CONTROLS.md | b4e5c82fd38598b80c7a6fe2b5bfcee48363ab1cf01379603089b4b0e254acb1 |
| COHORT.csv | b1b29b6f70f81bee2d96884670f1b2105610b676bc489a58a479b253d7fc148c |
| M0_INPUTS.json | 0dadb393eaef90245de8234d00d685eb7050eaf2b540d497f6ffe36db4415858 |
| A1_A10_CLAIM_AUDIT.md | ed23428cf2498b79b918331f354efc688d981235c6bb430352acebac8ee18070 |
| synthetic.py | 2149f86a6a527d1c9ab4704e609a2ac0a4fc5c64555dc522c0d6d4b6a01e062e |
| test_contract.py | 7c9c1f6e03e0a5bf6a4c2cbaefea09abd6ca49308032ec6d13ab861ca8de8625 |
| saved_verify.py | ac088578135d0cf1d6d3d20576bcf8498366eb3667352c0a7ba74bf0232009c4 |
| reproduce.ps1 | 54b738b0b1d130d110f357b2349dcfabf7229f1119a02cfb142d7a6cb47be073 |

This is independent internal review only, not external peer review. Return to bounded prospective specification repair, then obtain focused fresh review. No production worker, real fitting, C/D access, main promotion or Git closure is authorized by this unsuccessful review.
