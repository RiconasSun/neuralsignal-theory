# Independent internal prereconstruction native-repair review 1

Mission P15-DEV-EXACT-NATIVE-REPAIR-R1; exact owner BASE b0b692bd9b7e42f767117a51d0119644327a97f0. Scope: new versioned serializer, metadata/source adapters and downstream input consumers, before corrected real source reconstruction. Read-only review except this new artifact. No real neural arrays, source caches, B/E/Final values, network, fitting, Git mutation or historical coefficients were accessed. This is not a complete input/production certification or external peer review.

**Decision: NOT ACCEPTED FOR RECONSTRUCTION YET; zero P0, two P1.** Ordinary implementation corrections are within the new owner's authorization, but require affected regressions and fresh review before use. Historical paper15_dev and its failed source/fit evidence remain immutable.

## P1-1: the compatibility view collapses infinite source values into missing values

`native_table.decode_cell(cell, compatibility=True)` returns None for every nonfinite binary64 cell. The authoritative table retains NaN/+Inf/-Inf classifications and bits, but downstream reader, training, sensitivities, selection and evaluation consume only `state['trials']`, so they do not use those retained distinctions. `verify_native` explicitly accepts that collapse and returns `bitwise_pass=True`.

An independent in-memory20-row source fixture, with ordinary valid trial fields and trial5 contrastLeft=+Inf, contrastRight=.25, demonstrates:

- Exact table records positive_infinity, bits7ff0000000000000.
- Compatibility trial5 contrastLeft becomes None.
- task_masks(native) excludes trial5; task_masks(DataFrame(compatibility)) admits trial5, because missing contrast can represent an absent side.
- verify_native reports120 finite bit patterns verified and bitwise_pass=true despite the scientific mask disagreement.

Thus lossless storage of a sidecar alone does not preserve nonfinite scientific handling. The owner explicitly requires both original missingness classification and its scientific handling. This is a prospective implementation defect independently of whether the actual source currently contains infinities. Do not infer that any real animal is affected from this synthetic witness.

Required narrow correction: ensure nonfinite/nullable distinctions reach consumers with the frozen scientific meaning, or explicitly fail closed on unsupported nonfinite source states before any compatibility conversion. Infinity must not become an allowed absent-side value. Preserve legitimate NaN-as-absent-contrast behavior and the original missing event exclusions; do not add a new scientific cutoff or reinterpret source infinities as valid observations. Add regressions for both infinity signs, NaN/None/pd.NA, essential versus optional event fields and contrast handling, verifying serialized reload through the actual consumer path.

Positive evidence: the current implementation successfully round-trips the tested eight finite binary64 examples bit-for-bit, including +0/-0, values adjacent to1, smallest subnormal, smallest normal and maximum finite. Source row ordinals, field names/dtypes and native index are recorded. This narrower success does not resolve nonfinite semantics.

## P1-2: cached metadata bodies are decoded without a current source-body integrity check

`metadata_access.local_path` resolves historical cache paths. `metadata_qc.run` obtains those paths then directly reads native trial metadata, wheel arrays, sync, AP metadata, anatomy/mapping, saturation and selected metrics. No current SHA256/size/receipt check is performed by this resolver or on the run path before decoding. `metadata_access.fetch` contains historical reuse checks, but it is not invoked by metadata_qc.run and is a separate network-capable entry point; no separately enforced all-body verification gate exists in the reviewed candidate. The owner's exact-original-native requirement and current goldenstandards require verified cache reuse before reconstruction.

Consequently altered, truncated or mismatched local metadata may be treated as the frozen original despite an unchanged source inventory. An old successful receipt is not a current body readback. This is especially important when the timestamp repair's central claim is equivalence to the exact pinned native task source.

Required narrow correction: verify every reused metadata object's current size/hash against its original frozen source/body receipt before its first decoder/read. Bind the relevant original receipt/source identities; missing, ambiguous, altered or inconsistent evidence must stop before decoding. Apply the same verified resolver to downstream wheel/contact metadata consumers, or bind a complete current pre-read integrity gate that they enforce. Reuse existing original SHA/ETag evidence and files; no dataset/source rediscovery, new infrastructure or neural download is required. Add synthetic missing-receipt, changed-body and wrong-identity denial tests without reading real caches.

## Additional reviewed boundaries and remaining gates

The new root is paper15_r1; `source.P` points there. metadata_qc.run explicitly skips Final rows, reevaluates all Development candidates and uses the exact native table for its first masks. Reader denies non-Development and non-A roles before neural loading. `cached_neural` checks allocation/role, uses the historical source-object receipt by key, verifies size and streams SHA256 before returning a read-only original-cache path. This review did not call it or inspect a raw source body. Its SHA check is stronger than the current metadata path.

Static inspection found no historical fit-coefficient initialization/reuse: training prepares new features/scalers under the new namespace, initializes models via the frozen initialization routine, and selection/evaluation resolve versioned artifacts. Historical original_path references in neural receipts intentionally identify the original native source cache, not scientific fitted states. Exact production gate bindings, full actual source revalidation, no-retry/new-budget enforcement and independent numerical certification still require later completed gates; they are not certified by this early review.

All inspected future event consumers use the compatibility records. Therefore correcting their semantics at a verified serialization/load boundary is essential; it is not sufficient to keep an unused exact sidecar. Actual PL033/native-boundary integration, all37-column independent source audit, complete A/source ordinal reconciliation and fresh production numerical tests were not yet complete and are outside this review's acceptance.

## Synthetic execution evidence

Executed an in-memory Python diagnostic with the existing paper15_dev runtime and `-W error::ResourceWarning`; exit0. Imported only new serializer/task-mask code, numpy/pandas and standard libraries. It constructed20 synthetic rows, ran both native/compatibility masks, inspected all five missing/nonfinite classes and tested the finite binary64 edge cases described above. No real source body was opened. The exact observed output included `native_trial5_admitted=false`, `compatibility_trial5_admitted=true`, `changed_mask_rows=1`, while the verification certificate reported `bitwise_pass=true`.

## Reviewed candidate identities

| File | SHA256 |
|---|---|
| OWNER_MISSION.txt |baa9c09cb522b0736df3f6fe9dcee67eb9a1c127307c7b01d47c872dcd2c9c11|
| paper15_r1/native_table.py |b409c7ad1273c4e9dbec69ca6b7e5394ecd515f2196cccb0c237b79d414782e8|
| paper15_r1/metadata_qc.py |d8b813edfd7a795286776ba65dd2dcb027ee3397367992158d2e8e3bc0829933|
| paper15_r1/metadata_access.py |fd4dc71230fe822a05ac4781446bef9c19c3e331fc32f077d6f7cdbd7ca1f399|
| paper15_r1/cached_source.py |fe969df49d6d4a48ab68dcffbaa70524797a8ed7e08bb5bcc92afd9b8280828a|
| paper15_r1/reader.py |49cb124c8b035e912f80a1b7bb8fbb26ece06d28f401ce9519e086f17b47d856|
| paper15_r1/training.py |1c11098672df8d24c54770375c6c0c8db351622d533badf30bc11170dba0212d|
| paper15_r1/sensitivities.py |a2768c20b36cc81904ff89d9c64ca25a497b97ffd24ee3fd1dc1324513fd674b|
| paper15_r1/selection.py |e21ea51bbc5377e4bb9b6d70ed357a7ced9c91fea3605cc4f11e1c0874328317|
| paper15_r1/evaluation_support.py |e3b17ddf9cae5cd42c7630bca4a5fef2fa0c4f0b83b99c1d031241f559dbba61|
| paper15_r1/SOURCE_FILE_FREEZE.json |bd5bf03ca164066dad7e3a070d333e1a69c595108f9d7f8639ec43132c31ad87|

No full-mission PASS, M2 admission, fitting authorization, B/E release, Final access or downstream promotion is issued by this review. Preserve this unsuccessful revision after repair.
