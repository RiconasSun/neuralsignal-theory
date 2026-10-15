# Independent scientific source review — revision 2

Mission `P12-C-SEAL-HOST-IMPORT-REPAIR-1`; BASE `6cb50aaaffc1a89b4a6dddadb73e991d37c02448`.

Reviewer: independent agent `/root/final_plan_review`. Read-only source/design inspection; no real saved model bundle, raw C/D input, compartment key, fit, derivative experiment, sealing or release operation. The reviewer authored only this review file. Decision: **HOLD pending the test-harness repair and complete passing synthetic evidence**. No real saved-state access is approved here.

Revision-2 host snapshot SHA256 is `72570fa006b50972cf4515f6263f4db382620bf8ee6630f0da94422afe816cf2`; all six listed source hashes match. The populated frozen baseline contains 59 unique requirements. Original selection source retains SHA256 `9a36e1c29ca9acc2e6b4e8534489c8730f68d3db313ab8b2fc2b40a1930d9d4e`.

## P1 test-oracle defect

`paper12_cseal1/test_saved.py::isolated_cmd` places its receipt at the copied repository root (`isolated_repo/receipt.json`, line117). `paper12_cseal1/host.py` requires synthetic receipts beneath that copied repository's `paper12_cseal1/jobs` namespace (line190). Missing/corrupt source mutations can fail earlier, masking the mismatch. Authenticated dependency-hash/import-failure cases instead reach `RECEIPT_PATH` before the intended dependency failure. Those cases therefore cannot substantiate their registered import oracle with this candidate. Use a fresh receipt in the copied jobs namespace, preserve the failed attempt evidence, freeze the corrected revision and rerun the affected synthetic verification before seeking real-state approval. No assertion or expected dependency error should be weakened.

## Scientific preservation findings

No P0/P1 mathematical or scientific-policy alteration was found. The existing controller diff is confined to the package dependency block; native top-level import behavior is retained. The explicit helper verifies the literal original source hash and compiles those exact bytes, without inserting a path or populating a selection module cache. Hash/import failures do not fall back to an ambient module. Selection, calibration, optimizer, ridge, seeds, bounds and original numerical thresholds remain unchanged.

The saved-only assembler copies the inventoried partial artifacts into an exclusive new namespace, binds original model/scaler/unit/trial/certificate/provenance records, builds the same schema-v2 manifest and invokes the complete original validator. Its real-count cross-check retains 13 mice,26 subfields,290 cases,21,716 GLM fits,78 N seed fits,26 N means and40,104 endpoint certificates. It verifies preserved original worker, runtime, scientific source and old sealer identities separately from the new repair attestation. It does not reconstruct a missing fitted state or call the original calibration/sealer pipeline.

The synthetic prospective-roster fixture remains marked synthetic with an explicit test-only notice; it makes no prospective claim about historical fits. Genuine historical retrospective artifacts are preserved and rechecked. Negative cases cover missing/corrupt state, certificates/roster, exclusive destination reuse, concurrency/interruption and prohibited input/key/source/ledger/fitting accesses. These are registered tests; their passing execution remains necessary evidence, not established by source review alone.

Final gate approval requires the corrected frozen source identity, successful fresh-process synthetic results and matching independent security review. Any later real saved-only attempt must remain separately recorded and must preserve the failed partial directory. No new fitting, raw neural input/key loading, model substitution or D authority follows from this source review.
