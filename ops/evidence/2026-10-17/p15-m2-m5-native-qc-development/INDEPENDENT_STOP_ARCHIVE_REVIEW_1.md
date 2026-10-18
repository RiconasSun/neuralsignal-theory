# Independent stopped-evidence archive review 1

Mission P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Decision: REPAIR_REQUIRED. Open P0=0; open P1=3. This preliminary review precedes final STOP_ARCHIVE_FREEZE and actual saved reproduction. Prior accepted component reviews do not certify the native-input pipeline or scientific execution.

Exact SHA256 identities:
- `STOP_REPORT.md`: `f38d2273121db7af2e665d2bfd8925bc2126d687cd4a6ff63bd3a2a7aea8547d`
- `STOP_CLAIM_AUDIT.md`: `2d870db91dd1a352bbaa9af37fd61d66f3199c5c6818c132c3660bae64aa3201`
- `README.md`: `29e582f794684f577c5949e551a31ee0773175bddb227cba873af5b0bb231ce4`
- `stop_verify.py`: `6906b42fb38bb4e8b1d2587fdbd0a736f7dd2a2fd0ef88ec4f6e9fafd51d2dcf`
- `reproduce_stop.ps1`: `67898b61d928374dfe088f0637558719bb7b03f47f5a0ea042345d041507b7f4`
- `test_time_serialization.py`: `1fd25e32c6ef1621c097b5fdb30fe7f28badc4e3524dd7debbb4e02bf6ff40b9`

## P1-1 — Attempt reconciliation can silently verify a duplicated row instead of every fit

stop_verify.audit requires359files and359seal rows and checks each row key belongs to the610plan, but does not require unique sealed subject/configuration keys or exact equality with actual fit-file paths. A synthetic seal containing358unique keys in359rows (one duplicated numerical PASS, one real fit omitted) passes the present length/key/status-count checks and still reports358completed arithmetic checks. Require unique plan subjects/configurations and seal keys; exact actual-fit-path versus sealed-key equality; all attempt states from actual records; compute251unattempted directly from610expected−359actual unique keys and compare sealed values. Require baseline attempt-hash keys to equal the exact130 registered baseline keys, not just iterate whichever map entries exist.

## P1-2 — Required historical A QC journal completeness is not checked

The stopped verifier globs *_A_QC.json and audits only those present, without requiring the exact historical neural-access subject set in M2_PHYSIOLOGY_GATE. An omitted A QC journal is therefore not independently rejected by the arithmetic validator. Restore exact expected filename/content subject binding, uniqueness and cohort agreement (as in the complete-run saved verifier). Preserve historical admission as a computation under defective inputs; never turn this completeness check into source/QC scientific PASS.

## P1-3 — Stopped archive manifest lacks explicit required-file coverage

paths excludes every file named STOP_ARCHIVE_FREEZE.json at any depth, whereas only its root self-reference should be excluded. The package manifest has exact currently-enumerated paths but no mandatory stop report/status/claim-audit/verifier/source/fit-plan/timing-evidence key set, and evidence hashes verify only whatever entries are listed. Add explicit mandatory package/evidence keys, exact root-only self exclusion and an explicit evidence manifest policy for immutable source/failed reviews/time audits/interruption/historical evidence while excluding only known review/self-readback receipts. Validate paths remain relative/in-scope. Complete final freeze/evidence hashes must then receive actual independent saved-only reproduction; a subset of hash matches is not complete evidence coverage.

## Reports and scientific boundary

STOP_REPORT and STOP_CLAIM_AUDIT correctly identify the serializer/strict-held-index issue as a native-input implementation failure, not biology or optimizer failure. They correctly limit358numerical PASS results to the rounded-input objective, retain the1STARTED interruption and251unattempted, declare all B selection/E/sensitivity/reference/scientific effects unavailable, preserve historical M2 receipts without retroactive PASS, and withhold Prompt4/Final. Exact source-witness/time-index claims remain subject to the separate source reviewer; this review did not independently inspect raw source arrays.

The saved path statically invokes no production fit/extract/predictor. It denies sockets and np.load; synthetic model tests may exercise synthetic optimization, so README should say no **real-data/scientific refitting**, rather than an unqualified promise that no fitting occurs. The exact-time test reproduces the defect and a proposed binary64-roundtrip option without modifying the production serializer or scientific data. No fresh repair/re-QC/re-export/refit or budget reset is authorized by the archive.

No actual stopped reproduction was run, no raw/neural/A-cache/B/E/Final values were accessed, no network or real fit occurred and no source was edited. Synthetic in-memory duplicate-row counterexample is saved in INDEPENDENT_STOP_ARCHIVE_SYNTHETIC_1.json. Repair verifier integrity only, freeze the complete negative archive, obtain timing-source review and request final stopped-evidence review/reproduction.
