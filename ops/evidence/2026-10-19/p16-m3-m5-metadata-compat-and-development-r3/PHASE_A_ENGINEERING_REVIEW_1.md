# Independent Phase A engineering review — candidate 1

mission: P16-M3-M5-METADATA-COMPAT-AND-DEVELOPMENT-R3

BASE: e740f6ac80ad1348a393c889fcf20778e9d24523

reviewer: independent internal agent /root/r4_policy_review

decision: REQUEST_CHANGES

open_P0: 0

open_P1: 1

failure_classification: VERIFIED_PREEXECUTION_ID_ENCODING_CHECK_DEFECT

ordinary_Phase_A_software_correction_permitted_by_owner_section_5: true

Phase_A_PASS: false

scientific_stage_consumed: false

real_scientific_execution_permitted_by_this_review: false

## Decision and authorization interpretation

The observed rejection is caused by comparing equal source identities with different JSON encodings, not demonstrated loss of source provenance or reconstructed mask disagreement. It is an ordinary software correction allowed before the new scientific stage under the explicit owner exception. The current failed candidate and all unsuccessful receipts must remain preserved; this decision neither clears the receipt nor asserts compatible representations exist.

Owner section 5, OWNER_REQUEST.txt:318, explicitly states: “Ordinary pre-execution software corrections may be made only before the new real scientific stage, with independent re-review and preserved unsuccessful evidence.” Line 320 distinguishes consumption once real execution has begun. Sections 2.1/2.2 still require STOP for genuinely unresolved label provenance or disagreement with frozen intervals/masks (lines 135/137), and line 178 requires archiving an actual Phase A incompatibility. These rules do not require treating a demonstrated comparison-code error as proof that authoritative source labels are missing. All Phase A/B/scientific acceptance gates remain closed until actual compatible representations and independent reviews pass.

No new owner intent, mask interpretation, numerical policy or scientific exception is needed for the narrow ID-encoding correction. No scientific clock, neural feature/scaler construction, fitting or B/E/Final operation has occurred. A later genuine provenance or frozen-contract disagreement must stop; the ID fix cannot waive it or justify using a fallback.

## Read-only review activity

Read the complete owner request, all 11 frozen implementation payloads, Phase A registration, schema audit, attempt/STOP and execution/synthetic logs, the original invalid_rows/evaluate implementation, the frozen native-header producer and applicable original observation definitions. Independently checked all 11 payload sizes/hashes and their manifest. Independently checked all 388 SOURCE_PINS current files and all 146 historical R2 files against expected digests/sizes. R2 source, its consumed real stage, bug1/warn1 and previous review records remain unchanged.

Read the already saved 27 native-header JSON files and existing SCHEMA_AUDIT records, checking the header hashes against stored provenance. Every header has a string session_id identical to the canonical decimal representation of its integer source-account ID. All 27 have no error, decoded_neural_values=false, a list-valued complete interval-name inventory and consistent invalid_times table presence. Twenty-two inventories omit invalid_times and their table maps omit it; five include it and have its saved table. The actual first header is session_id='750749662' (str), while the source account is 750749662 (int).

The saved schema audit records 27 actual inputs, 24 missing stimulus-invalid members and 3 present members, with float64 start/stop/invalid-interval arrays; the present stimulus-invalid arrays are also float64. No compatibility outputs or PHASE_A_RESULTS exist. The preserved PHASE_A_STOP and actual traceback show rejection at metadata_compat.py:22 before interval reconstruction/equality checks and before additive output publication.

No derive/labeled-invalidity operation, reconstruction, synthetic test or new experiment was executed by this reviewer. No original metadata array was decoded by this reviewer; source/header JSON and existing array-identity records were inspected, plus files were hashed. The parent's 10/10 synthetic test log was read and hash-verified, not rerun. It uses integer IDs on both fixture sides, so it does not cover the demonstrated real string/integer encoding boundary. Only this review file is written. No source transport, neural worker, scientific clock or Git mutation is performed.

## P1-01 — Strict JSON type comparison rejects an exact source ID

Location: paper16_development_r3/metadata_compat.py:21–22; fixtures in test_metadata.py.

The compound condition rejects `header.get('session_id') != item['session_id']`. The native-header producer, paper12_native_support1/native_headers.py:49, copies the upstream item session_id directly; its original main driver uses string IDs as filename components. The later R4 source account stores the same IDs as integers. Neither frozen source identity nor header hash is wrong: all 27 original header string values equal the expected account decimal text, independently inspected here. The producer's encoding is therefore demonstrated source evidence, not an ad hoc relaxation inferred merely from a traceback.

The generic receipt STOP_METADATA_PROVENANCE_UNRESOLVED correctly preserves that the current checker refused, but it does not establish a root-cause finding of unresolved source semantics. No invalid table, interval, label, mask or selected-probe contradiction was reached. It must remain immutable, with this independent root-cause interpretation recorded additively.

Minimal correction: compare canonical exact decimal source identities. Accept only a positive ordinary JSON integer (`type(value) is int`, excluding bool) or a canonical ASCII decimal string with no sign, whitespace, leading zero, exponent or decimal point; derive a canonical decimal representation and require exact equality to the already registered session ID. Do not use a permissive int()/float() coercion, stripping, bool acceptance or rounding. Preserve the source-account registration and all header bytes. Preserve raw encoding/type in provenance instead of overwriting it.

Add accepted integer/string exact-ID cases, plus rejected bool, float, leading-zero, whitespace/signed/nondecimal/malformed and wrong-ID cases. Check all 27 actual metadata/header ID types and canonical values before labeling this engineering defect repaired. Keep the original scope/label parser strict; the normalizer does not change probe/global tag semantics or admit an unregistered source.

Preserve the current 11-payload candidate, original 10-test evidence, SCHEMA_AUDIT, PHASE_A_ATTEMPT, PHASE_A_STOP and traceback. A corrected metadata-only attempt must use separately identified append-only evidence paths; do not delete or overwrite the current attempt/STOP merely to satisfy run()'s exclusive publication. Freeze the corrected candidate and obtain independent review. No current failure may be silently changed to PASS.

## Other load-bearing checks

**Trusted absence.** The implementation does not infer that a missing stimulus_invalid_intervals member means no stimulus-invalid intervals. It requires a complete, hash-bound native directory inventory, no partial-header error, and agreement between inventory and tables. Only then can absence of the entire native invalid_times table establish an empty invalidity source. The 22 observed table-absent headers satisfy the static inventory/absence preconditions; this is source-directory evidence, distinct from a missing NPZ field. The remaining five tables are explicit; their scope/label semantics must be parsed and checked, not erased. No unconditional empty fallback is permitted.

**Labels and original mathematical contract.** The pinned original invalid_rows(..., return_labels=True) independently distinguishes session stimulus labels, session all_probes/optotagging and selected/other-probe invalidity, checking ragged indices, interval finiteness/order, source IDs and probe-label membership. Reconstructed applicable and stimulus intervals are compared in original order with saved evidence. For the three explicit-field schemas both fields must agree. For every source the literal original evaluate formula must reproduce main_valid and retain the already admitted common mask/role coverage, while stimulus_valid remains separate. Static implementation follows that contract. These actual equality checks have not yet run successfully and are not claimed verified by this review.

The original five stored invalid tables contain two EcephysProbe-tagged tables and three EcephysSession-tagged tables, including an explicit stimulus table. The 24/3 schema count therefore cannot be used to decide invalidity or label absence. The existing implementation's requirement to reconstruct from the native table/inventory and compare saved evidence is necessary and must remain.

**Precision evidence.** Native start/stop timestamp arrays in saved flash NPZs are recorded as float64, and the original M1 read/evaluate path required float64 flash timing rather than silently promoting it. For native invalid-times values the old header producer validated numeric f/i/u and serialized values into JSON; exact original HDF5 width is not recorded. The current report explicitly discloses that limitation and describes the float64 conversion as the original frozen invalid_rows conversion, not newly recovered native precision. It must never claim a verified native float64 invalid-times dataset from JSON alone. This limitation alone does not demonstrate a new scientific-contract mismatch: Phase A reconstructs the original registered labeled values, with mandatory exact applicable/explicit-stimulus/validity comparisons before acceptance. If those comparisons or trustworthy numeric/tag provenance fail, stop rather than altering precision, masks or obtaining an alternative source. No new source read or precision amendment is justified by this review.

**Identity and boundaries.** The adapter verifies the exact admitted record, source/account/header/probe/metadata hashes, original timing admission and NPZ schema/dtypes before use. Full source identities and all 27 actual schema variants are already recorded. Pinning includes the reused parser and native-header producer; metadata hashes do not substitute for actual contract equality. The code imports no mathematical/neural worker and denies network in its metadata-only entry point. No Phase B or new 48-hour stage is made accessible by a partial metadata success.

No second distinct P0/P1 is established in the reviewed implementation/static saved metadata. This is not evidence that all post-fix comparisons will pass. The actual 27-source compatible-representation gate remains unverified; any new real source/metadata contradiction must be reported on its own evidence and handled by the owner's STOP rules.

## Required next action and non-authorization

Complete the ordinary pre-execution ID validation repair, preserve unsuccessful evidence and certify its positive/negative cases and actual 27 metadata encodings. Freeze/re-review the revised Phase A candidate before advancing. After that, successful actual all-27 interval/explicit-field/mask comparisons and independently accepted Phase A results are still mandatory; Phase B recertification and a separate exact production prefit review must then pass before any Phase C clock, neural feature/scaler or fit. None of those gates is accepted here.

The current engineering rejection does not consume the prospectively authorized R3 scientific stage, because no such stage has begun. The closed R2 real scientific attempt remains permanently untouched. No Final C/D, M6 or P17 is authorized.

## Actual saved header encoding/inventory audit

No interval derivation is represented by this table. Each row is a saved JSON/header/hash observation, paired with the existing schema audit.

| Session | Header ID type | Account ID type | Canonical decimal equal | Header error | invalid_times inventory/table | NPZ stimulus-invalid member |
|---|---|---|---|---|---|---|
| 750749662 | str | int | true | NONE | absent/absent | absent |
| 757216464 | str | int | true | NONE | present/present | absent |
| 760345702 | str | int | true | NONE | absent/absent | absent |
| 763673393 | str | int | true | NONE | absent/absent | absent |
| 766640955 | str | int | true | NONE | absent/absent | absent |
| 762602078 | str | int | true | NONE | absent/absent | absent |
| 767871931 | str | int | true | NONE | absent/absent | absent |
| 768515987 | str | int | true | NONE | absent/absent | absent |
| 771160300 | str | int | true | NONE | absent/absent | absent |
| 771990200 | str | int | true | NONE | present/present | absent |
| 778998620 | str | int | true | NONE | absent/absent | absent |
| 774875821 | str | int | true | NONE | absent/absent | absent |
| 778240327 | str | int | true | NONE | absent/absent | absent |
| 781842082 | str | int | true | NONE | absent/absent | absent |
| 779839471 | str | int | true | NONE | absent/absent | absent |
| 787025148 | str | int | true | NONE | absent/absent | absent |
| 786091066 | str | int | true | NONE | absent/absent | absent |
| 793224716 | str | int | true | NONE | present/present | present |
| 794812542 | str | int | true | NONE | absent/absent | absent |
| 816200189 | str | int | true | NONE | absent/absent | absent |
| 821695405 | str | int | true | NONE | absent/absent | absent |
| 831882777 | str | int | true | NONE | absent/absent | absent |
| 829720705 | str | int | true | NONE | absent/absent | absent |
| 835479236 | str | int | true | NONE | absent/absent | absent |
| 839068429 | str | int | true | NONE | absent/absent | absent |
| 840012044 | str | int | true | NONE | present/present | present |
| 847657808 | str | int | true | NONE | present/present | present |

## Exact identity binding

All paths are repository-relative. The 11 original candidate payloads remain unchanged. Actual audit and unsuccessful execution receipts are additionally bound. This review is hashed separately after publication.

| Path | Bytes | SHA256 |
|---|---:|---|
| paper16_development_r3/identity.py | 1545 | 329cf9defe01a7eb2e21f734723dcc5d3ecbc292be251584dccf572524d65195 |
| paper16_development_r3/metadata_compat.py | 12906 | fc8a50c76d9e56735af56ee446f1388e331e297d86ed6366201bf5e0539e3ef6 |
| paper16_development_r3/test_metadata.py | 6899 | 402d71c405b015d6135f526f14a2cbd381bf1c9cfc0fea65e62066832162dd2b |
| paper16_development_r3/SOURCE_PINS.json | 55305 | 6ccf4455e847bc8a83e42e229a2863d17ef32fe593121fb20778870250a77d9b |
| paper16_development_r3/PHASE_A_REGISTRATION.json | 49175 | 4d6f027cad89da1bb05b305c8d4f957005db9e75c08385286cc825ded13e0f36 |
| paper16_development_r3/HISTORICAL_R2_MANIFEST.json | 45541 | ba64b0237f08a96b2e8c9191648a2cedd706a88ecfa5124f2770ef80cd35d4cb |
| paper16_development_r3/MISSION_SPEC.json | 983 | f020125c11db7211ae60b3c523256f596968c8b412a2662f0175c7ddd3312346 |
| ops/evidence/2026-10-19/p16-m3-m5-metadata-compat-and-development-r3/OWNER_REQUEST.txt | 13181 | e47c8ca61366ba0ab65f19fce49c8122ce3f75476b095ad10fb5e95b0035fa35 |
| ops/evidence/2026-10-19/p16-m3-m5-metadata-compat-and-development-r3/REQUIREMENT_BASELINE.json | 42167 | b6900e21df30da677f4ee0f0e8f500d0c10150a400f28083b0a6b70102ae42ad |
| ops/evidence/2026-10-19/p16-m3-m5-metadata-compat-and-development-r3/goldenstandards.md | 2205 | 48408ed17bafac881e66d8c394a27575b930985348c69ef33cb7b00da6e8726d |
| ops/evidence/2026-10-19/p16-m3-m5-metadata-compat-and-development-r3/PHASE_A_SYNTHETIC_TESTS.log | 1850 | feab0c9ad5fd075fa0c835f17bb7972d0481e8b34ba10bc43a6c5b2d0ed7c74d |
| paper16_development_r3/PHASE_A_IMPLEMENTATION_MANIFEST.json | 2232 | f5193de27f67687ea6c84d3586ca78c13c55d478f11610e6cf292caae84380f4 |
| paper16_development_r3/SCHEMA_AUDIT.json | 194320 | c68fab1f29cfd34cab20c3747735abd4829ff2104eb05c997f559417077d9ebe |
| paper16_development_r3/results/PHASE_A_ATTEMPT.json | 130 | 43b8c0880c0906782ce9148a0659d993e373e21e1c77473e9979962501da2f50 |
| paper16_development_r3/results/PHASE_A_STOP.json | 223 | d0fd2d75fed5befd03219bf7f9f489c4fd3bf9583a12427437b14fdd92fffbb9 |
| ops/evidence/2026-10-19/p16-m3-m5-metadata-compat-and-development-r3/PHASE_A_ACTUAL_PREFLIGHT.log | 1651 | a621469c33a3f5bcc2439d5bc779fc79a599e7ed11f93413d76eefeb7d3ff1e4 |
| paper16_m1/code/roster_metadata.py | 10845 | c50c3b913761f3e827415cc6528a0ade17ff14ae889b964cef4d9d08647c93a1 |
| paper12_native_support1/native_headers.py | 5554 | 57a57314b693f4156445c7c9f21cc3e1843534e9fa94a9d3d6b476524befd577 |

review_scope = independent read-only pre-scientific Phase A engineering diagnosis; no compatibility or production acceptance

new_scientific_execution_authorized_by_review = false

Final_access_authorized = false
