# Independent bounded pilot access review 1

Decision: REPAIR_REQUIRED_PILOT_ACCESS. Open P0: 0. Open P1: 4. **Neither download nor neural decode is approved.** This is not a whole-M0 verdict.

## Verified metadata and frozen selection

I independently reconstructed the saved metadata inventory using the registered predicates and compared the entire inventory and role allocation with the saved artifacts. Source denominator is 58 mice/sessions, 332 probes and 135,275 units; 55 mice qualify at tier 8, with 28 Development and 27 Final candidates. All 26 historical roster entries resolve to the saved source specimen identity, with 13 prior Final mice protected across sessions. The selected cohort contains 23 historically exposed mice, all Development. No historical mouse enters the new Final reserve. The actual source has one session per specimen in this roster; the previously repaired cross-session protection remains required for the general case.

The deterministic pilot selector reproduces SID 760345702 (BO) and SID 829720705 (FC), both Development and outside prior protected Final. Their declared sizes total 3,640,631,888 bytes. Frozen roles/selection registration hashes, exact object ETags and sizes agree with the HEAD freeze and historical descriptors. HEAD is object-identity metadata, not a neural read or a generation-compatibility certificate. Metadata-audit attempt 1 failed on an encoding-name typo before roster processing; its log remains preserved. The later successful audit is explicit rather than a hidden retry.

## P1-01 — cookie-valued response headers retained in archive candidates

PILOT_OBJECT_FREEZE.json retains Set-Cookie values in both HEAD headers. The same sensitive header class occurs in metadata/allen_citation_current.json, allen_terms_current.json, sessions_sdk_definition.json and source_unit_qc.json (case insensitive). I examined header names and file identity without emitting any values. These public service cookies are not needed for object identity and must not enter Git/evidence. Redact cookie/authorization header values in a case-insensitive shared sanitizer, retain non-sensitive ETag/size/version fields and original scientific body hashes, record redaction provenance and pre-redaction file SHA without copying cookie values into replacement evidence. Rebind the reviewed file hashes and test that future acquisition/pinning also sanitizes them.

## P1-02 — invalid interval probe-name lookup spans unrelated sessions

pilot_reader.main constructs the probe ID/name map from all source probes. invalid_for_probe then resolves a tag such as ['EcephysProbe','probeC'] against that global map. Probe names repeat across sessions, so a normal current-session tag is rejected as ambiguous. An independent fictional two-session probeC counterexample reproduces ValueError('Invalid probe tag ambiguous'). The helper tests used globally unique names and did not cover the production caller scope. Restrict the map to probes in the current session, while continuing to reject unknown or genuinely ambiguous current-session tags. Add a cross-session repeated-name regression before risking a one-shot real pilot.

## P1-03 — unresolved/rejected or empty review receipt can reach transport

Both downloader and reader only inspect numeric zero counters and iterate the receipt's own reviewed_hashes. They do not require an accepted decision, explicit true GET/decode approval, strict integer counters, a complete required reviewed-file set, or the matching report hash. I supplied a fictional REJECTED receipt with explicit approval false and an empty map in an isolated temporary tree; the downloader reached the mocked transport call. There was no real request or data. Zero defects alone do not constitute access authorization. Use a shared small verifier with a fixed accepted decision, strict integer 0/0, literal true approval(s), exact required/nonempty source-and-artifact set and current hashes, report identity, and frozen role/object/selection binding before either entrypoint can proceed. This is a normal local admission check, not a request for a new cryptographic custody system. Reject false, malformed, stale, empty and altered receipts in regression tests.

## P1-04 — interruption/concurrency accounting is not enforced before transport

The durable per-chunk TransferBudget implementation has atomic replacement/fsync and rejects over-budget charges, and the downloader checks declared remaining size before GET. However, it calls res.read before budget.charge. A crash or read exception after receiving bytes but before charging loses those bytes from the durable ledger. Similarly, checking attempt/partial existence followed by ordinary replacing dump_json is not an atomic acquisition of the session attempt: two processes can both pass the precheck and start the same GET. The per-charge lock is not a whole-attempt lock. These are static lifecycle defects in the promised interrupted-byte/no-retry boundary; the original helper tests prove charge durability but not downloader transport ordering or duplicate-attempt exclusion. Use an exclusive durable attempt claim before any body request and conservative pre-reservation/outstanding-byte accounting so unobservable interrupted bytes cannot be silently discarded or an entitlement reused. Report actual versus conservatively reserved bytes distinctly. Add isolated mocked concurrency/interruption tests; preserve failed attempts. The current nominal 3.64-GB pair fits the 6-GB ceiling, but nominal capacity does not prove this lifecycle property.

## Source, scientific scope and test interpretation

Existing 15 synthetic tests independently pass with socket/network access denied. The new collision and rejected-receipt probes demonstrate material production-path gaps despite those passes. Before actual access I require an official-PyNWB-created fictional NWB integration run through main: exactly eight selected rows, an unselected nonfinite spike sentinel proving no eager full-unit decoding, same-name probes in other sessions, invalid intervals, missing behavior, original event IDs/native binary64 persistence and failure/denial paths. A modern synthetic writer schema is useful integration evidence but must not be presented as proof of compatibility with real source NWB 2.2.2. Preserve actual runtime versions and the guarded 2.2.2 header check; real object schema/namespace compatibility and native clock checks remain mandatory first-read gates, with failures retained and no pilot replacement.

The pre-existing non-neural source header receipts for both selected sessions report NWB 2.2.2 and equal session/timestamp reference strings, with decoded_neural_values false. This supports the planned guard, not successful real PyNWB decoding. The reader's lazy per-row spike access and no old-worker import are appropriate in design. The declared support is source-curated scheduled presentation intervals minus known invalid intervals; it explicitly does not establish raw/AP packet continuity or rule out unmarked dropout. Do not infer support from spike extrema or merely from file existence. Retain native missingness/IDs, strict-past exclusion of equality, finite/order checks and zero-versus-invalid distinction.

Final reservation is entirely BO (27/27), whereas Development has only 5 BO and 23 FC. The numerical 28/27 split is not evidence of an exchangeable same-protocol 8+8 design. The pilot may assess both source families as already registered; it cannot justify silently reallocating animals or claim session-family-independent predictive generalization. The eventual M0 decision and proposed M1 must disclose this asymmetry and establish a defensible common stimulus/estimand domain and adequate development support, or retain a narrower/inconclusive feasibility verdict. No future scientific model, inference or cohort alteration is authorized here.

I read only authorized metadata, frozen source/code and synthetic fixtures; no real NWB GET, neural arrays, fitting, predictions, likelihoods or Final access occurred. The first reviewer probe invocation failed on a local encoding-label typo before any data read; the corrected invocation produced the saved proof. No implementation files were edited. All reviewer-owned evidence is under this mission E directory. After the four repairs, freeze amended hashes and independently re-review before either real pilot. Full M0 evidence/report/review/Git gates remain open.

## Reviewed file identities

- `paper16_m0/code/pilot_reader.py`: `31d4d6fa657008593b25e2a1d31b83e4009394f2e7c229a2ba110fb541927fa4`
- `paper16_m0/code/pilot_transfer.py`: `7a7b5c9848ceed48e39e88aef6986b6f06901632c86aaa1fa7f7f517413738bd`
- `paper16_m0/code/core.py`: `935cfb8c7483b93d75dcbc01c7354e8f0d559d64ee181c744387d228076e80aa`
- `paper16_m0/code/test_core.py`: `0d6773435df82676a8494d728e3217058a3135c5f6787c79a339345d3f8ba60f`
- `paper16_m0/code/test_reader.py`: `a8fdf1077d4703a2256af0a848b5063b3ea7e4a5ffd10402027f330da3f81a2f`
- `paper16_m0/code/metadata_audit.py`: `161177e5117220a109248e3da40c9f6c54569fdfa570e05ff1d4134716689adc`
- `paper16_m0/code/acquire_metadata.py`: `e166b9085f26242cb928fa1f7bab864f18ad3791dc92b5843c760c84c0eeb177`
- `paper16_m0/FEASIBILITY_REGISTRATION.json`: `fc0475a5bdef84ac94b2ead49e5103f11cdae763885eaf3d91a2e1360c5b421d`
- `paper16_m0/FEASIBILITY_REGISTRATION.md`: `33c7f13e29e715740b998730ba3359ecdbe2a15d3c5530563ccca65fa94c6c7b`
- `paper16_m0/SOURCE_RIGHTS_REGISTRY.json`: `a7af653e49d81fc4bbfef52652b22d8fabf0076c32008ad3abbde80bac8bf55d`
- `paper16_m0/metadata/METADATA_ACTIVE_BINDING.json`: `62fe61d147b099efbfae6c91ceae3582762ae4310446adab617efc1101760c3a`
- `paper16_m0/metadata/METADATA_INPUTS.json`: `379604a5a567bfd8933f19ba1fff784b38f3cd98e829d69b430bb3d81add8232`
- `paper16_m0/results/METADATA_SUMMARY.json`: `185c770d627172d689a6405ad3af6371a1f764e6cbdc134fa092177fa330ef4a`
- `paper16_m0/results/POPULATION_INVENTORY.json`: `5cbf286d303e74ac20613dbdde2c2be91acb26a0f7b109fd2631bb8cc4e17d24`
- `paper16_m0/results/ROLE_ALLOCATION.json`: `463ed226d1f8c385934f1c7cda87481d5465702592c54d9e7e162fe14e50fb9a`
- `paper16_m0/results/PILOT_METADATA_SELECTION.json`: `c11e40b7ccff939ab7cdb2b911ed92247076670ece6d35de65a9885866b1a512`
- `paper16_m0/results/PILOT_OBJECT_FREEZE.json`: `86335a2be9eb43047a144bfb2deba6465b0a9ab22df7426562f5754a2ee354e1`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/REGISTRATION_RECEIPT_2.json`: `2e57e5ded1dc1995bbd4abd5c4ea31867725b33bab013f9fcad0f8db252f276b`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/PREACCESS_PROTOCOL_REVIEW_RECEIPT_2.json`: `235167e2bd70fa8cdedd6876c97115bf65c210516a056da3bbc2d45e8b4525a3`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/METADATA_AUDIT_1.log`: `9eea9b5533752c4e6080af8696c9820c7f8459b10a7f46c00f91784b1c93dfb2`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/METADATA_AUDIT_2.log`: `4899ad858bd2121b4d2c39bef3b6fbb697d8eab68fa9b7ea0373222c328d8253`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/SYNTHETIC_PREPILOT_1.log`: `816a6d364c3ecc0dfe608a533541033f90d0ddb1caf44181ab3b6ee1d1c7ad84`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/PILOT_ACCESS_INDEPENDENT_PROBES_1.json`: `6fcf53c30b5eae693d9dcd1209a5485437ad38e7553f6ff503fef0c06f4340d9`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/PILOT_ACCESS_INDEPENDENT_SYNTHETIC_1.log`: `673b64f0e1e82e6ae172653c7788ef657a7625999d96fc93a20a1ab9b9d9e7e4`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/baseline.json`: `8f6c751ac7c12476bfe2a2fdee946fc7bedc380707c117658d79291e8f285a05`
- `ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0/OWNER_REQUEST.txt`: `6c3e58e0ea5abd7028c4db0d85bfdef6feef5d273209bb23eeec99d139d07018`
- `paper12_curated_v1/replay/mouse_evidence.csv`: `f1a937d25fc9e5d78954292d596486cfb8a292abcc4f109fbb773a0404cb70cd`
- `paper12/metadata/allen_header_capability.json`: `429adcfa8c9201905766fdb7d4b56e8eba98438348ef776922b9e04798a779d3`
- `paper16_m0/metadata/sessions.body`: `c418fbcebac6c242b052e35cf5e282b4db7ebef9dc19bb678d4b27bb13872a27`
- `paper16_m0/metadata/sessions.json`: `6e265403c7f9714c7662c9882883fb8170d7a75c9b3a05764734f5b01c0a5e16`
- `paper16_m0/metadata/probes.body`: `f7ac8d3e2b3b630613a93ca73bf2b145723df08f25bf5e307214f6422591bde2`
- `paper16_m0/metadata/probes.json`: `597c937355fbffdb0f1a43ca9f5abf178d9bbcb161dada68cea86da24f556d95`
- `paper16_m0/metadata/channels.body`: `c15f34f73bfb7ffb3b9d6514e356a649bfd6aa3bc60fc169aecfd3abe21441b7`
- `paper16_m0/metadata/channels.json`: `d369a506a3b073b5baade057e33695d7f95a37cece2dd5dcd9603cc01dd41537`
- `paper16_m0/metadata/source_unit_qc.body`: `9d130ec5caf9c56b5964cb633dc79cbe182b4787917115dfb0e6f9b49fc11014`
- `paper16_m0/metadata/source_unit_qc.json`: `770e9b0c04a9e76e8bd2dde018da1e7486081bfe05f8a3bd2b9bfa3a61d5e798`
- `paper16_m0/metadata/sessions_sdk_definition.body`: `3709fdb545a95c72c31f3f3e07ec1ab1d6cdc948ef59ddd28c080445cf00c1a1`
- `paper16_m0/metadata/sessions_sdk_definition.json`: `4846959d3c1f8bd3796bf91aae15c5c1f1d5391b8c91aeed7378dd93c6aa094d`
- `paper16_m0/metadata/sdk_tag_2_16_2.json`: `08e7ca0d8ec4f146d570cd1f9b08148c18c1fababf0405d40315b00647c4c64a`
- `paper16_m0/work/source_documents/sdk_tag_2_16_2.body`: `78e18b8971d923a155a3f0dc955bd9d0d4e598e10ba7e5d05da3bb8c440db6be`
- `paper16_m0/metadata/sdk_nwb_api_2_16_2.json`: `8373c205e942df763b3a91bd7ffe080b6f73631053f9c9346a830465a1f2bad0`
- `paper16_m0/work/source_documents/sdk_nwb_api_2_16_2.body`: `428f03a8840d5dd0ca8c3ec5103a055be3315bb2d1b577d254c5ce2d6a840841`
- `paper16_m0/metadata/sdk_session_2_16_2.json`: `6428e9af646d1281c5a9b4b12ce7a6b302941c10367ca3f9275227b47cf12a8b`
- `paper16_m0/work/source_documents/sdk_session_2_16_2.body`: `403840767a08dc6194d55c604e9eebbac4512acd61ae3b17b536271302a5c6eb`
- `paper16_m0/metadata/sdk_unit_filters_2_16_2.json`: `d4ab7d127504cdd8b632971020cc33ced6f7f06fe9fcefdd89277adede43cfd6`
- `paper16_m0/work/source_documents/sdk_unit_filters_2_16_2.body`: `9ec581ff632db832a03ac1de20a23ff36e23b1aac0e75f6ff92fd0eb2721d9c1`
- `paper16_m0/metadata/sdk_cache_2_16_2.json`: `a905506b8169794c6479b1d3dd0267e6da47f00d05bbf19d44bd3c814bc7f9ea`
- `paper16_m0/work/source_documents/sdk_cache_2_16_2.body`: `56b28d367a42c629c86da7fcb4bd324b07f5ea931f3b6cc03cb68894d58df365`
- `paper16_m0/metadata/allen_terms_current.json`: `1a71832fd8e34a0cba4e4cb43701289dc3fde0931eb2f5ad1e3ae8670e23999f`
- `paper16_m0/work/source_documents/allen_terms_current.body`: `f737b6899f3040ee71413a1c02f3b1ef9d3962ea26b355cfb40c5e8e42dfecab`
- `paper16_m0/metadata/allen_citation_current.json`: `84022b465dbf16cd79d8d3ddfb35f300470fe313366761e75468cfd85a77feeb`
- `paper16_m0/work/source_documents/allen_citation_current.body`: `57f20e07526b0576e73f4de5ff5f5d6189413cc93a674924413556568c99d329`
- `paper12_native_support1/metadata/native_headers/760345702.json.gz`: `2aa65261db24ca3de2b04c8196c8136ca54e0ed59de9b183cae83a914e69dde0`
- `paper12_native_support1/metadata/native_headers/829720705.json.gz`: `c0c45e44e1849e8c0225e8dcf37b9c1715ae09250fc98aebc26d07bf4954b0d1`
