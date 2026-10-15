# Independent security design review — single-owner amendment

Mission: `P12-REAL-D-SINGLE-APPROVER-AMEND-1`  
Exact base: `6e952aeb0bc19abead5b208327b56298f25dc290`.

Decision: **ACCEPT_DESIGN_FOR_BOUNDED_ENGINEERING_IMPLEMENTATION**. No P0/P1 design blocker identified. This is not a preexecution approval, completed security gate, owner-key provisioning, REAL signature, release permission or scientific PASS. Later source and fresh synthetic evidence require their registered reviews.

## Scope and source binding

Reviewed public `human_authorization.bin`, `SECURITY_AMENDMENT.md`, `registration.json`, `goldenstandards.md` and the frozen 56-item requirement baseline. Human authorization SHA256 is `01e40349e02d9a7327bb25cffef580394da216595b147d2ddd7a0f2ac18f82c6`; amendment SHA256 is `83d49d5aa2da9cbd0761421963322a898efe2ee0fccd1fd686c23bb4d529d2eb`, both matching registration. No protected REAL states, neural arrays, ciphertext or keys were accessed; no experiments or release operations were performed.

The human explicitly supersedes the second-human fingerprint ceremony prospectively. The new policy must require neither another person nor a manually calculated/transcribed fingerprint. Historical evidence remains governed by its original protocol and is not retrospectively passed. The separately versioned package and registered byte-preservation boundary are consistent with these instructions.

## Conditions for source review and verification

1. Strictly validate a raw 32-byte Ed25519 public key and derive SHA256 from those decoded bytes. Reject malformed/ambiguous encodings, duplicate or unknown schema fields and inconsistent identity, key, fingerprint, version, mission, base, amendment or provisioning ID. Automatic hashing establishes consistency, not the human identity or exclusive possession of a private key.
2. Keep onboarding proof and REAL release signatures in separate domains. The exact proof bytes must bind a fixed onboarding-only purpose/domain, policy/version, owner identity, public key, amendment/mission/base, provisioning ID and owner signing-environment statement. The unchanged release verifier must reject the onboarding proof as an approval. Test cross-domain/realm reuse and altered proof fields in both directions. Only synthetic proof fixtures may be generated in this mission.
3. Require one explicit owner local confirmation against the displayed public key/fingerprint and owner statement. Software may verify a valid signature, schema and confirmation consistency. It must not infer physical/offline key isolation from a signature, path, flag, assistant assertion or synthetic fixture. Under the stated trusted-owner model, the owner's explicit setup attestation supplies the human evidence; disclose its limits. Do not introduce a replacement second-person ceremony.
4. Preserve host-protected immutable receipt/deployment hash pins and the worker-denial boundary. Owner public-key setup is not entitlement issuance. Absence of genuine owner setup/confirmation/possession evidence must remain `AUTHORITY_PENDING` and deny REAL source resolution, role activation and consumption. A worker/request-supplied root or synthetic key cannot satisfy REAL provisioning.
5. Provide no REAL private-key generator, loader, signer or signing-credential interface. The owner uses their existing separately controlled offline tool. Codex/workers/Git receive only the public setup/proof artifacts. No REAL approval, source key, entitlement or ledger may be created/accessed in the engineering rehearsal.
6. Preserve producer/evaluator/broker/Controller and scientific bytes as registered; limit necessary differences to the new version's governance, mission/package and binding integration. No weakening of full artifact rosters, actual held principal checks, durable consume-before-decrypt, delivery fencing, crash poisoning, replay denial, model/scientific thresholds or holdout partitions is permitted.
7. Fresh acceptance must exercise the actual new-version production entrypoint on the complete registered synthetic fixture, including original 29 native oracles, eight producer negatives, owner-onboarding boundary cases, full statistics/controls, protected-principal denials, source/runtime/receipt bindings, saved reproduction and native cleanup. Historical successful runs establish precedent, not fresh proof for amended authority integration.
8. A future request dossier must retain exact public artifact identities and preparation ID, but remain `NOT_SIGNABLE` while genuine owner provisioning, complete staged runtime or a held live restricted principal is absent. Do not fabricate stale/live identities or present an incomplete object as an executable canonical REAL approval. Final explicit owner approval/offline release signature remains a separate irreversible boundary.

## Reporting boundary

`SECURITY_AMENDMENT_PASS` may become true only after implementation and required verification; `OWNER_AUTHORITY_READY` and unqualified `PRODUCTION_PATH_READY` must remain false while genuine owner setup is pending. REAL signature/release/evaluation/scientific flags remain false throughout this engineering mission. The owner is the sole approver, not an independent third-party custodian; the desktop Host/admin remains trusted. No protection against a malicious trusted administrator or remote proof of physical signing-device isolation is established.

Complete all safe authorized engineering and archival work before asking for the smallest necessary owner-controlled setup action. Neither this design review nor later engineering review may authorize REAL signing or evaluation.
