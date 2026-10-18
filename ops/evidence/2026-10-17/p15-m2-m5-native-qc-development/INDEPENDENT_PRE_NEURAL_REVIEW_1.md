# Independent internal pre-neural review 1

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Base: `30cb925f505d63ae52bb1461d9ab153a52f1888e`.

Review date: 2026-10-18 UTC. Reviewer: independent internal source/scientific review agent. This is not external peer review or M2 scientific admission.

Decision: **REPAIR_REQUIRED_BEFORE_NEURAL_ACCESS**. Open P0: 0. Open P1: 1. No real neural payload was accessed by this reviewer; no source HTTP, fits, Final access, or implementation edits were performed. This unsuccessful review is retained and must not be overwritten by a later acceptance.

## P1-01: the pinned unversioned multipart object is not bound to the actual download

In `paper15_dev/reader.py::neural_file`, new payload access verifies a separate HEAD against the prospective key/size/ETag/last-modified/version pin, then calls `s3_download_file` without a version or conditional ETag constraint. For multipart ETags, the later MD5 check is deliberately skipped. The newly computed SHA256 is logged, but there is no previously frozen expected SHA256 for a newly downloaded file. Consequently the implementation does not establish that the body actually consumed is the object certified by the earlier HEAD if the unversioned key changes between those operations. The present header freeze contains unversioned multipart objects, so this is a relevant source-identity path, not an invented Final security architecture.

Required narrow repair: bind the actual GET to the frozen identity (for example pinned If-Match, and version when present), validate response identity/length before a payload is made usable, and fail closed on mismatched response or interruption. Preserve partial/failure evidence. Add synthetic response/ETag/version/length mismatch regressions that demonstrate no extraction/use on failure. An unconditional GET followed only by recording a new SHA256 is insufficient. No scientific model, threshold, budget or source revision change is requested.

The 25 existing synthetic tests pass but do not exercise this download binding. They do not negate this P1. Do not create an executable approved reader gate or request a real payload until the repair and focused independent re-review complete.

## Reviewed scientific and access interpretation

The owner Prompt3 expressly allows a narrow trusted full-record Development decoder that exports only the authorized role. The reader rejects Final allocations and B/E/C/D roles before neural object loading; only A is implemented. Internal nonfinite timestamps cannot be partitioned and fail closed. A ordering/cluster/range checks are limited to A; no B/E values or summaries are exported. A export intentionally retains A rows outside retained epochs, preserving future registered role-local thinning ordinals, while physiology uses valid A epochs only.

The physiology implementation uses half-open epochs, genuine zero observations, per-epoch ISI pairs without cross-gap pairs, original A trial quartiles before exclusion, frozen rate/spike/pair/refractory/exposure thresholds, and refractory/rate/UUID ranking. Strict QC is a separate preserved indicator. These computations and tests do not establish actual physiological admission before execution.

CSHL059's `[[0,0],[1,1]]` sync is well-formed monotone identity metadata, not demonstrated clock corruption. The frozen no-extrapolation policy limits usable support to [0,1], producing zero eligible epochs. This is a per-mouse registered sync-domain coverage exclusion. NYU-37's B count 31 below 40 is likewise per-mouse coverage attrition. Frozen M1 explicitly stops that mouse's source admission; the owner gives M1 precedence. Neither result alone establishes a global essential-clock failure or permits extending the sync domain/replacing either mouse. Remaining fixed candidates may be considered only through the complete required gates.

The current saved metadata supports an upper bound of 10 Development mice across 8 labs, all ten with verified wheel support; physiological admission is still unknown. Final 8 task/anatomy possibilities are metadata-only, with wheel/physiology unverified and no Final neural authorization. A whole-source/cohort PASS is not inferred. All 11 additional catalog annotations are saturation on the other probe; the explicit scope table excludes these appropriately, while selected-probe saturation is used. Unannotated artifacts remain unknown.

## Independent checks

- Read the exact owner mission, frozen M1 source/QC and relevant sensitivity definitions, current source/metadata/reader/physiology code, registration/header pin, annotation scope, saved task results and preserved repair log.
- Independently recomputed all 20 saved task masks and A/B/E or C/D structural counts from saved small task JSONs using a separate stdlib implementation: exact agreement. All finite stimulus sequences were chronological; no hidden nonadjacent epoch overlap across missing-stimulus rows occurred in these saved inputs.
- Ran `paper15_m0/work/runtime/Scripts/python.exe -W error::ResourceWarning -m unittest paper15_dev.test_source paper15_dev.test_reader -v`: **25 tests, PASS**, exit 0, no neural access. Repeated after the header-pin reader addition; same 25 tests pass. This remains synthetic source/role/QC verification only.
- Source identity/name mismatch and metadata cap failure remain implementation history, not biological exclusions or erased attempts. Source-only recovery and completed wheel receipts are distinct evidence.

## Exact principal reviewed SHA256 identities

| File | SHA256 |
|---|---|
| paper15_dev/source.py | d8eae9f300f1d4fcd0655e3a20c81d8099e229187d937bde37aa047bcaa291dc |
| paper15_dev/metadata_access.py | ad17ec2a349e34795f06d135f848de2eb9ff0ad5647106db9a98f17a2b13164f |
| paper15_dev/metadata_qc.py | 14068246912971fea75eacc510afd088230d1b1e174d14c175d9e17319008ecf |
| paper15_dev/reader.py | f09ec3cd6086236987661f93172a99c37fd98230d853472f04cf5c80a6506fe0 |
| paper15_dev/physiology.py | 1e85584d4f779df9b063941b153715def105ad9cf006046fa7694eb1a12176fd |
| paper15_dev/test_source.py | c9a2796495a1d2fe5afec766ed8842d1f9455d6161940b6928dd4599c6991c62 |
| paper15_dev/test_reader.py | d00194145e8e5004bfc62a118bb3927883598cad245a616ac17c9f046f70a843 |
| paper15_dev/SOURCE_FILE_FREEZE.json | bd5bf03ca164066dad7e3a070d333e1a69c595108f9d7f8639ec43132c31ad87 |
| paper15_dev/READER_PROTOCOL.md | 725c0f68b2ae1fa4086e362e7b8485490023eed41b9b9c849c867c975dca055e |
| paper15_dev/NEURAL_HEADER_FREEZE.json | 1457587b5042993d5890aa9f5f2feb8780db3b65154eda77e9f520e82a773961 |
| paper15_dev/results/ANNOTATION_SCOPE.json | f53297c43fb04e9620829d3f3a7bb6d800a0b51e421be362e633d47d52b7126f |
| paper15_dev/results/METADATA_QC.json | 16115e2f39d9fc3b19c9bd58295dc951efbc8536a41fa981971e146fc86459de |
| paper15_dev/results/M2_METADATA_GATE.json | 4078d29fe02c241398b7efae1b73f342850c1272e829045fa80cc6ca7121e6fb |

After this repair, the exact reviewed reader/source/input-state identities must be frozen in the execution gate before the one authorized A-only run. This review does not approve M3 production mathematics, any real fit, B/E release, Final C/D access, mission closure or Git promotion.
