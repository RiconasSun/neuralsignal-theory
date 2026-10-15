# Human-controlled authority boundary

Mission: `P12-D-PRODUCTION-PATH-READINESS-1`.

Candidate exit after all other engineering and archival checks: `WAIT_FOR_HUMAN_INPUT`. This is a human-only public-key ceremony, not permission to sign or release REAL_D. The human owner explicitly designated themself; designation is preserved in `owner_human_reply.txt` and hash-bound in `owner_designation.json`.

Observed missing evidence: an owner-controlled Ed25519 public key, SHA256 of its decoded 32 bytes, independently obtained and checked fingerprint, identified verifier/channel/time, and a matching unique provisioning ID. There is no valid protected authority provisioning receipt or externally pinned deployment trust root. Consequently `AUTHORITY_PENDING`, `PRODUCTION_PATH_READY=FALSE`, and `REAL_D_AUTHORITY_PROVISIONED=FALSE` remain required.

Autonomous alternatives completed: implemented a public-only key/fingerprint checker, exact receipt/schema/hash/realm verifier, protected deployment pinning, missing-authority early denial, synthetic trust-root and negative tests, and a complete documented onboarding procedure. A synthetic authority cannot provision REAL_D. An assistant-generated key, assistant self-designation, repeated assistant fingerprint calculation or worker-supplied trust root cannot substitute for the required separately controlled owner key and independent human verification. Existing repository evidence contains no verified owner public-key bundle. Creating one autonomously would cross the user's explicit private-key custody and approval boundary.

Minimal next human action: follow `paper12_production1/AUTHORITY_ONBOARDING.md` in the separately controlled signing environment and provide only the public-key verification bundle (raw public key as 64 hexadecimal characters, both independently obtained decoded-byte SHA256 fingerprints, verifier identity/channel/time and common provisioning ID). Never provide a private key, seed, passphrase or signing-service credential. A trusted-host provisioning operation then needs its own reviewed protected receipt and deployment hash pin. No REAL signature is requested by this handoff.

After public onboarding is verified, stop again for separate explicit human authorization of the exact REAL_D canonical approval and one-shot final validation. Neither designation nor public-key onboarding authorizes signing, consuming an entitlement or evaluating D. No release entitlement may be created or reset in this mission.

The machine administrator and trusted custodian Host remain trusted. These controls do not establish protection against a malicious administrator or independent external custodianship. Public mathematical/source review and full synthetic execution establish engineering evidence only; real-source operational compatibility and scientific validation remain unexecuted.
