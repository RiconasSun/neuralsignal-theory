# Independent security preexecution review — repaired revision 3

Mission: `P12-REAL-D-SINGLE-APPROVER-AMEND-1`; base `6e952aeb0bc19abead5b208327b56298f25dc290`.

Decision: **APPROVE_REGISTERED_FRESH_SYNTHETIC_ATTEMPT_2_ONLY**. No unresolved P0/P1 preventing that bounded synthetic execution was found in the repaired candidate. The earlier P1 and withdrawn r1/r2 approvals remain historical evidence. This review is not final security acceptance, owner readiness, protected REAL provisioning, REAL signing/release/evaluation permission or scientific PASS.

## Exact state and evidence

- Revision-3 source freeze SHA256: `d3c21d9dd7b2dc48350310bec580b5c0cbecb1eb294d3d71d2b6631aa76bf922`; all 25 candidate file hashes independently match.
- Current registration SHA256: `77644c642ffd9bed4e9ae68e0ad40987b32f72d70ddb86bede5d7bafaf82144b`; all 60 registered hash guards independently match. The original 56 remain preserved; four additional public security-document/authorization guards are explicitly recorded, and the prior registration remains archived.
- `focused_r3.log` SHA256: `6e170f111508a6f1e9159031cb5155fb51bed688aa6854ad6baa2954a9bc158f`; saved evidence reports 39 tests, all PASS.
- `public_key_vectors_r3.json` SHA256: `e969313f089fafb3df990b0505ac998c7ec7cef7564180476a751271646f78db`; 234 public vectors, zero disagreement with the separately represented affine oracle.
- Current public toolkit SHA256: `10dfbbcef74d668885bcef7a80509fa5f5e0ad3e8ea80ac968ff04836753eb1f`; the reviewer read only this public archive and independently checked all manifested payload hashes, with 12 entries and no mismatches.

The reviewer inspected source, public metadata/receipts and hashes only. No experiments, tests, releases or signing were executed by the reviewer. No protected REAL neural/model states, ciphertext or keys were opened.

## P1 repair assessment

`ed25519_public.validate_public_point` now enforces exactly 32 bytes, canonical field encoding, recoverable on-curve coordinates, the canonical zero-x sign rule, exact re-encoding, explicit nonidentity and `[L]P = identity` with nonzero projective denominator. Its extended Edwards addition/multiplication formulas and decoding were reviewed against [RFC 8032 sections 5.1.3–5.1.4](https://www.rfc-editor.org/rfc/rfc8032.html#section-5.1.3). The added nonidentity/prime-subgroup admission rule implements the registered stronger authority-key requirement; it is not attributed to mere signature-constructor acceptance. Arithmetic branches operate on public input only and introduce no secret-scalar or signing implementation.

The centralized `public_identity` applies this guard before challenge/proof/candidate receipt acceptance. Both REAL and SYN authority trust-root paths reach that validation through the exact receipt/candidate verifier; protected import likewise validates before acceptance. The unused length-only legacy comparator was removed only from the new version. Its old test is explicitly replaced by automatic fingerprinting of a valid RFC public key plus malformed/weak-key rejection; historical originals remain unchanged. This is strengthened admission coverage, not weakening a scientific test or assertion.

The saved vector matrix includes three RFC public keys, 16 strong generated keys, all eight torsion points, seven mixed-order points, 128 encodings for y=0..63 with both signs, 38 noncanonical y encodings, two forbidden zero-x signs and 32 seeded encodings. Separate regressions reject the identity-point forged possession proof and a self-consistent forged candidate despite updated hashes. The affine oracle uses separate coordinates/addition and left-to-right scalar multiplication, rather than the production extended/right-to-left helpers. This finite matrix supports the source reasoning; it is not a claim of exhaustive cryptographic verification.

New challenges/receipts bind `ED25519_CANONICAL_PRIME_SUBGROUP_V1` and amendment SHA256 `cdffd327632ceac9dcb25c96ab26f0686ac742ff944c4c72c20b34d295ce46b6`. The independent saved-binding audit uses the affine admission oracle and checks signed security-document hashes. The current toolkit contains the repaired guard and policy; old unsafe kit bytes are preserved with an explicit supersession notice, not silently replaced. No new numerical runtime dependency, Ed25519 release-format change or scientific amendment is introduced.

## Interrupted history and downstream gate

Attempt 1 reconciliation truthfully retains nine synthetic consumption receipts, successful synthetic delivery and assessment start, controller exit 0, target controlled termination 97 and cleanup 0 for both roles. It records zero completed null cases/mice and no complete scientific statistics. It must not be reported as no consumption, a normal target exit or a full successful rehearsal, and its namespace/entitlements must not be reset.

Proceed only with a fresh synthetic attempt-2 namespace and the unchanged full 13-mouse/208-case/104 x 999 controls, 10,000 bootstrap, original 29 native oracles/eight producer negatives and original phase limits. Final acceptance still requires matching actual restricted-role/source/runtime/principal/receipt evidence, completed full results, saved reproduction, native exits/cleanup and independent final reviews. The new validator fixes authority admission; it neither proves physical signing-device isolation nor authorizes the missing genuine owner setup.

Retain one owner confirmation and automatic fingerprinting, without a second human. Genuine owner authority and unqualified production readiness remain false while setup is absent; pending dossiers remain NOT_SIGNABLE without protected trust-root provisioning and held live identities. All REAL signature/release/evaluation/scientific fields remain false throughout this engineering mission.
