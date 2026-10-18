# Independent internal prereconstruction native-repair review 2

Mission P15-DEV-EXACT-NATIVE-REPAIR-R1; owner BASE b0b692bd9b7e42f767117a51d0119644327a97f0. Focused review after the two P1 findings in NATIVE_REPAIR_REVIEW_1.md. That unsuccessful review and NATIVE_REPAIR_COUNTEREXAMPLE_1.json remain preserved.

**Decision: ACCEPTED_FOR_CORRECTED_INPUT_RECONSTRUCTION_ONLY; open P0=0, open P1=0 on the reviewed serializer/cache/consumer integration surface.** This is an engineering/source-component review under existing owner authorization, not a complete M2/production/scientific PASS. It does not authorize actual fitting, B/E scientific access, Final access or a change to any scientific criterion.

## P1 repairs and independent evidence

1. **Nonfinite scientific handling now reaches consumers.** Native binary64 columns retain their bits, hex strings and NaN/+Inf/-Inf classifications. The compatibility view maps NaN and nullable missing values to None for existing missing-event/absent-contrast semantics, while retaining positive and negative infinity. source.dump writes nonfinite compatibility numbers as explicit binary64-tag objects within standard JSON; source.load_json restores their numeric values. verify_native checks the complete serialized/reloaded compatibility representation as well as the original finite bits and exact classified sidecar. Infinity is no longer converted into an allowed absent contrast.

   I repeated the original synthetic trial5 counterexample through **actual source.dump -> evaluation_support.read_json -> task_masks** for both infinity signs. The native and loaded masks agree, both exclude trial5, and the loaded compatibility value retains its infinity sign. Five additional synthetic cases place infinity in each essential timestamp field (stimulus, go cue, feedback, trial start and trial end); every loaded case remains excluded. No changed physiological or source threshold was used.

2. **Metadata cache bodies are now checked before decoders.** local_path calls verify_cache before returning a path. The verifier requires a matching complete original body receipt by exact object key, rejects conflicting body hashes, checks current byte length against the frozen source and verifies SHA256. Missing receipts, files and mismatches fail before native metadata loaders receive the path. The same resolver is used by metadata reconstruction and later wheel/contact consumers. The existing neural cache adapter separately checks Development allocation, original receipt, size and SHA before returning an original native source path.

   Independent temporary-file faults demonstrated denial for a FAILED-only receipt, wrong object key, conflicting complete receipts, truncation and same-size corruption; the exact original synthetic body was accepted. These were synthetic bytes, not reads of actual metadata/neural caches. The existing focused test also verifies missing-receipt denial.

## Exactness and strict-past checks

I independently ran `python -W error::ResourceWarning -m unittest paper15_r1.test_native_table -v` using the existing project runtime: **six tests passed**, exit0. These cover finite binary64 edges/signed zero, nullable and nonfinite classification, the repaired contrast case, contradictory bits/hex denial, PL033's exact native boundary constant, missing predecessor support and cache integrity failures.

I additionally executed **19 independent synthetic integration/fault checks**, exit0 with ResourceWarning treated as error: the seven actual-loader nonfinite cases, six cache decisions and six strict-past query groups. The latter derive `bin-lag` for lag0/.05/.1/.25/.5 from preserved bin/lag values, test neighboring representable query values and compare to an independent scalar `wheel_time < query` predecessor oracle; the epoch equality case is also excluded. This supplements the test file's repeated held-boundary labels with actual query arithmetic. No numerical magnitude tolerance or changed scientific acceptance oracle was introduced.

The finite view uses Python's float JSON serialization and verifies binary64 roundtrip; it does not rely on pandas decimal precision. Field order, dtypes, native index and original row ordinals remain represented. NaN/None/pd.NA distinctions remain available in the authoritative table even when their frozen scientific missing-value handling is shared by the numeric compatibility view. Bit patterns of source finite numbers, including negative zero, remain verified.

## Consumer paths and preservation

Static inspection confirms that reader, A preparation, sensitivities, selection, evaluation support, reports and saved-result auditing now use load_json on their persisted state paths; evaluation.read_json delegates to that loader. Remaining direct json.loads calls in source.py load original source inventories, not corrected event/feature records. Source dump emits standard JSON with explicit nonfinite tags; this finding does not assert a new adversarial security system or malicious-administrator protection.

metadata_qc retains the original mathematical/source screens and explicitly processes Development rows only. It uses native data for masks, encodes the native table and verifies the compatibility view before storing it. reader remains A-only; the new source namespace is paper15_r1. Original-source references intentionally reuse verified source files, not historical scientific fitted coefficients. Model initialization and versioned fit paths do not import rounded-input fitted endpoints. No real source cache or neural arrays were opened in this review.

The mathematical feature, model and AD files have their prior hashes unchanged. The JSON-reader/cache import amendments change orchestration identities and must be bound by the new actual reader/input/production gates. This review does not substitute for those gates or for later complete source verification.

## Required downstream gates still pending

- Actual12-candidate native metadata reconstruction and source identity/coverage reconciliation.
- Original PL033 trial224 witness verified against the actual native source and all registered query/feature values, not only the synthetic constant.
- Full independent source-level37-column construction, A counts/history/role ordinal/QC/ranking/scaler reconciliation and exact differences versus historical exports.
- Complete corrected admission and independent production/numerical integration certification before any real fitting; original equations/thresholds/initialization/no-retry policy and the owner's new bounded budget remain binding.
- All B/E and Final access gates remain separate; no Final neural access is granted.

These pending substantive deliverables are scope limits, not waived requirements or a claim that actual input reconstruction has already passed. No historical failure is reclassified and no original evidence is overwritten.

## Reviewed candidate hashes

| File | SHA256 |
|---|---|
| source.py |ad8d0f786690d414f07568556d017e0bdb14edd0137fb246789e7ffb7cedddbb|
| native_table.py |fb7ca090776f2096a9ec3fd102afd0cc115d0bca3d01b57a8c6defabbc637aaf|
| metadata_qc.py |3a7de81fdd26cc433fb23c200a59344f0023c951e8fe159173ae25d123fdd5b3|
| metadata_access.py |bd32678410e38a262150a015df1f6b896ac6f9fa62da1aaf169153ab37f2dfb9|
| cached_source.py |cbc1a8cefdc2743cc96587f65c2dc9201a876cd843e3f0eee055f638268aa800|
| reader.py |54754e8690541e148ff04e5f84a8b9a384dc0dd1c96f6cc5c0e22a795a74d4e5|
| training.py |1b3f112b53b6a3b046056266f3b6f1252f0a749691d888345fad351436a6a093|
| selection.py |d76b29e945e4666ce554979ccddd6bab404d63e8ceb5721313b5f390d6c5891d|
| sensitivities.py |2eb61be757dd508e8f8e02dea19ec26770772d174d879d01ebc246760fa52b70|
| evaluation_support.py |ae51af203734ad82451b01b91816a7e6e2ebd23b71bcea49504e0e47d0c7e189|
| test_native_table.py |1c546fa9b741f3f4f9063a0af2c5891977c126a865415bf0a1615d895ad05410|
| features.py |30d17b3a902429537e8b83fc9ac5a483933bdb8080ff890c5f43c6fc5f4dd3fd|
| models.py |e13d12d3986b42ba1691075804df7b2ec6a033dcfe20fac36e5b6ed8e359ba90|
| independent_ad.py |8c69998bd1d03004325fb24d39c4d33fb4be15966b8e30321248d13480521ec0|

All paths in this table are relative to paper15_r1. This review wrote only this artifact; independent temporary synthetic files were automatically removed. No implementation, scientific definitions, original review, source artifact or fit state was edited.
