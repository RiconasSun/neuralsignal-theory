# Independent internal pre-neural review 2

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Base: `30cb925f505d63ae52bb1461d9ab153a52f1888e`. Review date: 2026-10-18 UTC.

Decision: **ACCEPTED_FOR_EXACT_FROZEN_DEVELOPMENT_A_QC_READER_ONLY**. Open P0: 0. Open P1: 0. This is an independent internal implementation review under the owner's existing Prompt3 authorization, not external peer review or a new scientific authorization. The unsuccessful r1 remains preserved (SHA256 `da397c16e7be0aac6ca96ffa9fc9e42d377aee35683b90a8b572774f55648fa0`).

## Closure of r1 P1-01

`reader.neural_file` now routes new payloads through `source_integrity.conditional_download`. The actual GET carries the prospectively frozen `IfMatch` ETag, plus `VersionId` when present. Its response ETag, content length, version presence/value and modification time must match the pin before the first body read or file write. A mismatched response is closed and rejected. New data are written exclusively to a separate partial file; truncation is rejected and retains that partial file. Existing complete/partial files are not overwritten by this downloader. Only a complete, identity-matching body is renamed for subsequent source checks/extraction. The prior HEAD/GET source-identity gap is repaired without changing any scientific model, source revision, cohort, role, numerical threshold or fit budget.

This relies on the existing trusted S3/HTTPS source and local operator environment. It does not claim protection against malicious administrators or introduce a new custody system. The newly recorded SHA256 is a reproducibility identity, not falsely presented as an independently known pre-download checksum.

The source-integrity helper also provides explicit single-part and known 8 MiB multipart ETag verification. The saved metadata audit records 184/184 previously acquired metadata bodies matching their frozen ETags. I inspected that recorded audit and its denominator; I did not reread raw caches or independently rerun those 184 body calculations. Unknown multipart layouts cannot pass that verifier by assumption.

## Independent focused verification

- Ran `paper15_m0/work/runtime/Scripts/python.exe -W error::ResourceWarning -m unittest paper15_dev.test_source paper15_dev.test_reader paper15_dev.test_integrity -v`: **31 tests PASS**, exit 0, no warnings. All original 25 tests remain, with six source-integrity regressions added.
- Independently injected response length, last-modified and unexpected-version mismatches: all three rejected before any body read or partial/complete file creation, and closed the response body. Independently checked a successful versioned response sends the frozen VersionId and yields exactly the expected synthetic bytes.
- Checked the installed botocore S3 GetObject service model offline: both `IfMatch` and `VersionId` are supported. No live source request was made by this review.
- Checked the prospective header freeze's 20 keys exactly equal the two neural objects for each of the ten currently metadata-eligible original Development mice; no Final neural object is included.
- Source/role/physiology interpretation from r1 remains unchanged: CSHL059 and NYU-37 are retained per-mouse coverage exclusions; 10 Development mice / 8 labs is only a prephysiology upper bound; all ten currently have verified wheel support. Final 8 are metadata possibilities, with no neural or physiological admission.

## Reviewed candidate identities (SHA256)

| File | SHA256 |
|---|---|
| paper15_dev/source_integrity.py | 453e7041a5954627ec41b195a9ce7fbbeb74e04f656f1a1aa9e57b732931aff0 |
| paper15_dev/reader.py | fc3f4df8d29a2bd26dafa083fecf66e99892ec3d9fa28926bf66796dda9be613 |
| paper15_dev/test_integrity.py | ab8a7c1471c3a79e099335da363300b14b77f8b12c9070f1496f080a609b077c |
| paper15_dev/READER_PROTOCOL.md | 725c0f68b2ae1fa4086e362e7b8485490023eed41b9b9c849c867c975dca055e |
| paper15_dev/NEURAL_HEADER_FREEZE.json | 1457587b5042993d5890aa9f5f2feb8780db3b65154eda77e9f520e82a773961 |
| paper15_dev/results/METADATA_BODY_ETAG_AUDIT.json | dd6bcd1acb0686e3681d2f3cb136c37626c82d4f15b599f2737dd9dafacbcbae |

The unchanged source, metadata, physiology, original tests, annotation scope and saved metadata result identities are recorded in r1. This focused review found no remaining actionable P0/P1 in the repaired path.

## Exact scope of acceptance

Before execution, freeze this reviewed implementation, source/header pins, M1 identities and the exact saved task/QC input states in the reader execution gate. The reader's existing before-read gate must verify these identities. Within that exact state, the next permitted scientific action is the already authorized single Development A-only extraction/physiological QC run on the ten fixed eligible candidates, reusing the two verified M0 payloads and preserving each source/QC outcome. Any required source integrity failure stops downstream use; no automatic retry or substitution is approved.

This review does **not** certify actual M2 physiological admission or M2_SOURCE_QC_PASS before the run. It does not approve M3 production mathematics, real fitting, B/E neural exports, Final C/D neural access, model selection, mission closure, or Git promotion. At least eight physiologically admitted Development mice across four laboratories, with all other frozen gates intact, remain required before considering M3.

No real neural payload, Final neural values, model fit, download or remote request was performed by this reviewer. Only this new review artifact was added.
