# Independent P16 preaccess protocol review 2

Decision: ACCEPTED_PREACCESS_PROTOCOL_AFTER_REPAIR. Open P0: 0. Open P1: 0.

This is a narrow, internal scientific/source-boundary re-review of the two rejected preaccess findings. It accepts the repaired protocol and synthetic primitives for subsequent metadata eligibility work. It is not approval of spike GET/decode, a real pilot, the eventual pilot reader, whole-mission feasibility, scientific results, or the final Git handoff.

## P1-01 — whole-mouse history and protected Final

CLOSED for this candidate. `allocate_roles` now explicitly consumes historical mouse IDs and historical Final mouse IDs. It unions both sets when excluding fresh Final, regardless of the selected session. `choose_pilots` explicitly consumes historical Final mouse IDs and excludes the entire protected mouse. String conversion handles verified numeric specimen IDs without confusing them with session IDs. Original deterministic allocation and size/session-type pilot ordering are unchanged.

I independently repeated the original cross-session counterexample with fictional mice and session IDs: the previously misclassified mouse is Development and cannot become a pilot when protected. Historical-exposure and protected-Final sets were tested independently, with string and integer historical identifiers; reversed input preserves the Final set. The new regression was demonstrated failing against the original implementation in the preserved RED log and passing after the repair. No existing test assertion was removed or weakened.

These APIs consume verified source specimen identities; they do not themselves discover or certify the historical roster. Before actual allocation/pilot access, the caller must still resolve every historical session against the complete source roster, verify recorded mouse identity, and fail closed on missing/ambiguous mappings. The registered conservative 26-mouse prior exposure and 13-mouse protected-Final treatment must be proved in that later admission evidence. This review does not claim that actual roster integration has already run.

## P1-02 — prospective source-validity predicates

CLOSED. Revision 2 explicitly registers nonnegative amplitude-cutoff and ISI metrics, presence ratio within [0,1], finite/parseable metric requirements, and finite positive probe acquisition sampling rate. These match the already present code predicates; inclusive scientific thresholds remain amplitude <=0.1, presence >=0.95, ISI <=0.5. Same-probe tiers 5/8/12/20, anatomical scope, allocation floors and pilot caps are unchanged. Actual inventories must separately retain and explain source-invalid versus threshold-failing rows; that reporting is a later output obligation, not evidence already supplied by the predicate.

The acquisition module remains a projected metadata downloader. Its revision-2 registration selection and separate ACTIVE input manifest preserve the prior manifest; there is no eligibility, role, spike, fitting or scoring call added to that module.

## Registration, preservation and source wording

Revision 2 time is 2026-10-18T21:35:27.769343+00:00, after the rejected review and before the declared first eligibility calculation or neural access. The current root registration, duplicate code registration and REGISTRATION_RECEIPT_2 hash agree. The zero-count/zero-array receipt is an orchestration declaration corroborated by the reviewed acquisition-only path; it is not an independently measured operating-system access log.

I verified every one of the eight original snapshot file hashes against `preaccess_rejected_candidate_1/SNAPSHOT.json`, including original registration, source rights, core/tests, acquisition code and original receipt. Review 1, its receipt, original counterexamples and the RED/GREEN logs remain present. No previous failure is recast as PASS.

Beyond the two repair clauses, `primary_source_interface` now says compatibility with version-pinned AllenSDK definitions and actual schema/version checks; it correctly rejects object Last-Modified as a release-generation certificate. This is acceptable clarification of the original no-incompatible-generation rule, not proof that any actual NWB object is compatible. Exact objects and reader/schema/common-clock/observation support still require later frozen evidence. Current rights wording accurately separates allowed noncommercial copying/distribution and attributed publication from commercial restrictions; this adds no new correspondence or custody requirement.

## Independent synthetic verification and remaining boundary

All 12 existing synthetic tests passed in this review process with socket/network creation denied. Additional fictional cross-session and source-domain probes passed. Logs/proof are `PREACCESS_INDEPENDENT_SYNTHETIC_2.log` and `.json`. I did not inspect actual unit metadata rows, calculate real VISp eligibility counts, allocate actual animals, open neural arrays, import old workers, fit models or compute predictions/likelihoods. Only reviewer-owned E artifacts were written.

No new preaccess P0/P1 was found. Accepted scope is the repaired pre-count protocol and synthetic primitives only. Before any neural access, freeze and review the complete historical mouse mapping, actual cohort/roles, exact pilot/object/version/hash/byte identities, bounded downloader and pilot reader, source observation/invalid-interval/common-clock handling and access boundaries. Preserve ordinary curated-recording limitations; this review does not demand impossible artifact-free proof. Full bounded M0 feasibility, scientific limitations, independent closeout and origin/test verification remain open.

## Reviewed identity

- `paper16_m0/FEASIBILITY_REGISTRATION.json`: `fc0475a5bdef84ac94b2ead49e5103f11cdae763885eaf3d91a2e1360c5b421d`
- `paper16_m0/FEASIBILITY_REGISTRATION.md`: `33c7f13e29e715740b998730ba3359ecdbe2a15d3c5530563ccca65fa94c6c7b`
- `paper16_m0/SOURCE_RIGHTS_REGISTRY.json`: `a7af653e49d81fc4bbfef52652b22d8fabf0076c32008ad3abbde80bac8bf55d`
- `paper16_m0/code/FEASIBILITY_REGISTRATION.json`: `fc0475a5bdef84ac94b2ead49e5103f11cdae763885eaf3d91a2e1360c5b421d`
- `paper16_m0/code/core.py`: `935cfb8c7483b93d75dcbc01c7354e8f0d559d64ee181c744387d228076e80aa`
- `paper16_m0/code/test_core.py`: `0d6773435df82676a8494d728e3217058a3135c5f6787c79a339345d3f8ba60f`
- `paper16_m0/code/acquire_metadata.py`: `e166b9085f26242cb928fa1f7bab864f18ad3791dc92b5843c760c84c0eeb177`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/OWNER_REQUEST.txt`: `6c3e58e0ea5abd7028c4db0d85bfdef6feef5d273209bb23eeec99d139d07018`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/baseline.json`: `8f6c751ac7c12476bfe2a2fdee946fc7bedc380707c117658d79291e8f285a05`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/REGISTRATION_RECEIPT.json`: `b91d9510ef8e5c994614c0737cc43f534b8c6670e7e9b28f3eb6f24b8e0cdc09`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/REGISTRATION_RECEIPT_2.json`: `2e57e5ded1dc1995bbd4abd5c4ea31867725b33bab013f9fcad0f8db252f276b`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/PREACCESS_PROTOCOL_REVIEW_1.md`: `5c064c4e9c40e05f57d582dcc7270b1d23c1524217519789beb3e5e4de88459b`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/PREACCESS_PROTOCOL_REVIEW_RECEIPT_1.json`: `ed0e09efbb550b8202dfb87161d779b01396dcd4fc9e1eaa30030968e1e5a144`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/PREACCESS_SYNTHETIC_COUNTEREXAMPLES_1.json`: `965b48fd7050859e7283734f93bc16b388947c33ccc9c3baae1b5700c3cdb2d8`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/preaccess_rejected_candidate_1/SNAPSHOT.json`: `335c8890ce908581a47aeba1c8dc4b3ab3e62a71a12347f11fb7194262be904b`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/SYNTHETIC_REPAIR_RED_1.log`: `fc9eb128b3c692558cf518c0539bfd80f0539093798a12ee012f73ff009769ef`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/SYNTHETIC_REPAIR_GREEN_1.log`: `4b064833df9d2c841b69258b9a5388a94fd0e76a5ab6728023de9fd8cec44cc8`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/PREACCESS_INDEPENDENT_SYNTHETIC_2.log`: `4b4ee6cadc3100b67d90369e3031f289e2c6228ba64f66117bffb90e14799904`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/PREACCESS_INDEPENDENT_SYNTHETIC_2.json`: `385db278953ab7409a95138df34ce07288e4f8217990ce414c10c37dd395a630`
