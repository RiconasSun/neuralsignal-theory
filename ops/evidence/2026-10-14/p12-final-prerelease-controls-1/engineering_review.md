# Independent engineering and custody E0-E3 review

Mission: `P12-FINAL-PRERELEASE-CONTROLS-1`.
Reviewer: independent agent `/root/final_custody_review`; no implementation authorship. This review inspected source, metadata, synthetic public receipts and hashes only. It did not open real C/D neural payloads, compartment or issuer key contents, or run scientific experiments.

Decision: **E0_E3_PASS_ALLOW_CONDITIONAL_C**.

No unresolved P0/P1 engineering or custody defect was identified for the registered C-only scope. This approves the existing authorization's conditional, one-attempt frozen C calibration after the separate scientific review also passes. It does not certify successful real C calibration, a complete real C state manifest, real D release readiness, scientific validation or permission to issue/consume/evaluate D.

## Exact reviewed candidate and fresh evidence

- Final v2 implementation snapshot: `paper12_controls1/implementation_snapshot_v2.json`; SHA256 `dc48694e8c42843bc8923660d38dc5cc816eff9b2ebefe9bd2f6b36c33ef13d7`. Independently verified all 92 source hashes, with zero mismatches.
- Final selected security result: `paper12_controls1/results/security_9546086888504515998.json`; SHA256 `7ff0ecdf9a1cf4a189bf48567b1e408f84e363b36f7462ff2291c11380440e90`.
- Final selected saved-synthetic state certificate: `paper12_controls1/results/saved_v2_9546086888504515998.json`; SHA256 `70735a06504cf6ccf89f7d1c1395c82a23160cbdaef4b9f91e63e402e2a3cb8f`.
- `E3_evidence_selection.json` selects those exact results. `results/native_reproduction_final.json` records the successful one-command PowerShell `SavedSynthetic` run and the same snapshot/result hashes. Independently verified the security execution registration's current source hashes without mismatch.

The fresh controller and state-certificate suites each passed 29 oracles, with zero skips, errors or failures. Certificate, controller and target launches each report exit 0, no timeout, actual role proof PASS and profile cleanup `0x00000000`. Saved synthetic evidence contains 208 cases and 104 N certificates. Its fixed state hash is `abb9f7537ff1b03210487227d3b23e6b44200d19f4d2bf56d73bfe67b241135a`. This verification reused saved cohort fits; the numerical oracle suite separately performed six small synthetic fits. It is not a fresh refit of that saved synthetic cohort or a real calibration.

## Enforcement and completeness findings

The controller validates signed, artifact-bound approvals under a distinct zero-capability AppContainer. Issuer private material is excluded from controller/worker grants. The host broker holds the target process handle and verifies actual package/token/creation identity, including denial of a host principal and a substituted target identity. The protected ledger uses an exclusive native lock, flushed hash-chained intent/consumption records and an independent exclusive write fence before capability delivery. Replay, concurrency, interruption and malformed/missing record cases are tested; injected failures count as zero valid releases. One synthetic capability was granted, and duplicate broker delivery was denied.

Actual controller/target/certificate receipts establish zero capabilities plus source/key read denial, DACL regrant denial, network denial and custodian-memory denial. Controller issuer-key denial and target issuer-key/ledger read/write denial passed; the latter also passed after capability delivery. These are actual native-principal tests, not mock substitutes.

The v2 completeness checks bind input manifests, QC/metadata, prefit roster, ordered units/trials/views, exact per-unit numerical certificates and original solver evidence, saved attempt journals, source/runtime identity and actual launch provenance. A real C run requires a prospectively emitted roster; retrospective roster reconstruction is confined to explicitly synthetic saved evidence. Empty certificate lists and incomplete case rosters are rejected.

The custody P1 concerning mixed REAL_D/synthetic C states is repaired: `verify_approval` calls `check_C_realm`, requiring strictly false synthetic mode for REAL_D and strictly true mode for SYNTHETIC_D. Both mismatch directions have regression coverage in the final passing controller suite. The prior HOLD findings remain in `review_history.md`; this approval does not erase them.

`arm_C.py` requires exact artifact-bound engineering/scientific reviews before issuing its separate C-only signature. `real_C.py` rechecks that signature, reviewed source/evidence hashes and original custody integrity, derives C only, and supplies no D payload or key. D access probes request an OS open-denial check without reading D bytes. Exclusive creation of the fixed real C job prevents a silent second attempt. Any required real C security/source/coverage/numerical failure must STOP without retry or D consumption.

## Limits and continuing prohibitions

The trusted immutable controller and Windows DACL/token boundary enforce against restricted scientific workers. The same desktop administrator, custodian and approval issuer remain trusted. This is not OS WORM storage, independent human approval/custody, hostile-administrator protection, a hardware rollback counter or a power-loss durability guarantee. Signed synthetic review fixtures exercise binding and do not substitute for the separate real C review gates.

Only synthetic D approvals/capabilities were exercised. Real D approval issuance, entitlement consumption, decryption, release and evaluation remain prohibited in this mission. The dormant future bridge contains no D decoder/key, and a future actual D producer/complete evaluation implementation would require separate authorization and fresh independent review. Historical failed final prerelease and M4 scientific/numerical evidence remain unchanged.
