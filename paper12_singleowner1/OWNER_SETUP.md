# One-owner public-key setup

Only the P12 project owner approves REAL_D. No second verifier or manual SHA256 calculation is required. The owner must establish a physically separate offline signing device inaccessible to Codex and scientific workers. Keep the Ed25519 private key, seed, passphrase and signing credentials there. Do not put them in this repository, chat, the public toolkit or an analysis process. No private-key generator or signer is supplied by this toolkit.

Software automatically validates the raw32-byte Ed25519 public key, canonical encoding, curve membership, nonidentity and prime-subgroup membership and computes its decoded-byte SHA256 fingerprint. A detached signature over a domain-separated onboarding challenge proves possession and binds the owner statement. It does not technically prove physical isolation; the owner must actually establish and confirm that separation. The trusted desktop Host/admin is not an independent external custodian. No protection against a malicious trusted administrator is claimed.

Use Python 3.11 with `cryptography` already available on your separate device, or the public toolkit supplied with this handoff. Only the following public ceremony is exposed:

1. Export the PUBLIC key as 64 hexadecimal characters to `PUBLIC.hex`. Prepare the public challenge:

```powershell
python -B -m paper12_singleowner1.public_key prepare --public-key-file ./PUBLIC.hex --environment-reference "My separate offline owner signing device" --output ./owner-public-ceremony
```

The software displays the fingerprint automatically. You do not calculate or transcribe it. The generated setup is a proposed owner statement, not completed proof or READY.

2. In your separately controlled existing Ed25519 signing tool, sign exactly the bytes of `owner-public-ceremony/key-possession-message.bin`. Save ONLY the detached public signature as 128 lowercase hexadecimal characters in `owner-signature.hex`. Do not sign a reserialized JSON file, a hash string or a REAL_D approval body. This challenge has purpose `OWNER_KEY_ONBOARDING_ONLY`; the release Controller rejects it as a release approval.

3. Complete the local workflow with one explicit confirmation:

```powershell
python -B -m paper12_singleowner1.public_key confirm --ceremony-directory ./owner-public-ceremony --signature-file ./owner-signature.hex
```

Type the displayed `CONFIRM OWNER <ceremony-id>` once. The software wraps the exact challenge automatically, verifies the signature, owner designation, amendment, isolation statement, key and fingerprint, and writes an append-only public candidate receipt. A rejected or interrupted ceremony remains incomplete; do not replace its original files.

Return only these public files: `owner_challenge.json`, `owner_proof.json`, `owner_setup.json`, `owner_confirmation.json`, `provisioning_receipt.json`. The private key and signing device stay under your control. No second human or independently calculated fingerprint is needed. A software-created test key or fabricated isolation assertion cannot satisfy genuine owner setup.

The trusted Host subsequently verifies the exact candidate receipt/hash, imports only public records to a new protected directory, checks worker-denying ACLs and pins the receipt SHA256 in a reviewed protected deployment. Hash calculation is automatic. Owner-key readiness remains pending until that genuine setup and protected pin are verified. No release entitlement is created by preparation, confirmation or public import.

Even after owner readiness, separate explicit final approval and an offline REAL_D signature are required for the exact reviewed canonical release body, live restricted principal and artifact roster. The body must include the unchanged protocol, full C seal, original 13 final mice/D masks, code/runtime hashes, one-shot specification and unique authorization ID. Durable consumption occurs before decryption and cannot be restored after interruption. This mission stops before that boundary.

Current status: no genuine owner public key, possession proof or offline setup confirmation has been provided. `AUTHORITY_PENDING`; `OWNER_AUTHORITY_READY=FALSE`; `PRODUCTION_PATH_READY=FALSE`; REAL_D signature/release/evaluation/scientific validation remain FALSE.
