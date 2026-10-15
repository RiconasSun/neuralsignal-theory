# Owner-controlled REAL_D authority: AUTHORITY_PENDING

The human P12 project owner is the designated REAL_D Approval Authority. No independent external data custodian exists or is claimed. The desktop custodian/SYSTEM administrator is trusted in this architecture; hostile-administrator protection is not established.

1. The owner creates and retains an Ed25519 signing key in an environment separately controlled by the owner. No private key, seed, backup, passphrase or signing service credential may be submitted to Codex, analysis/controller workers or Git. This repository has no REAL key generator or signer.
2. Export only the raw 32-byte Ed25519 public key, represented as exactly64 hexadecimal characters. Compute SHA256 of the decoded32 bytes in the owner's environment. Hashing the hex text or PEM file produces a different fingerprint and is not accepted.
3. A separately identified human verifier obtains that same public key/fingerprint through a second trusted channel and independently calculates SHA256 of the decoded32 bytes. Record verifier identity, method/channel, time and provisioning ID. An assistant assertion does not constitute an independent key ceremony.
4. Run the public-only candidate checker, supplying both independently obtained fingerprints: `python -B -m paper12_production1.public_key --public-key-file <public.hex> --owner-fingerprint <sha256> --independent-fingerprint <sha256> --output <new-candidate.json>`. It cannot activate an authority or issue an entitlement.
5. A separately reviewed trusted-host provisioning records `owner_confirmation.json`, `independent_check.json` and `provisioning_receipt.json` under an access-protected authority directory. Receipt exact fields are enforced by authority.require_real_authority. The receipt binds owner designation SHA256 `3bf5ec38e3aa7938183452421f93134fa6763f4262400af8c551581ff32603ba`, approver identity, public key/fingerprint, both confirmation-file hashes and a unique provisioning ID. Owner and verifier confirmations must share this ID; verifier must name the out-of-band method. Protect directory and files with the reviewed host/SYSTEM-only ACL; pin receipt SHA256 in a separately reviewed, protected deployment. No worker-supplied trust root is accepted.
6. Before any future REAL signature, separately authorize that mission. Prepare suspended, zero-capability target/controller processes and freeze exact target SID/PID/process-creation identity, original13mouse/D masks, complete realC manifest and every artifact, original protocol/plan, production host+target+controller code, runtime, source receipt/AAD/root mapping, one-assessment specification, both independent reviews, human scope record and a unique32-hex authorization ID. Approval body uses the unchanged release_control.FIELDS and canonical JSON. All additional identities are in the signed exact artifact roster. SHA256 of the complete body is the consumed binding. Never reuse a SYN key/root or authorization.
7. The owner reviews the exact canonical body and signs it offline using the separately retained private key. Return the body and64-byte Ed25519 signature, never the private key. The trust-root pin comes from protected deployment, not the returned request. Separate human authorization for one final assessment is mandatory. This engineering mission does not grant that authorization and provides no signing command.
8. A reviewed future activation rechecks everything before controller resume, durably consumes once, stages all13 selected-unit outputs privately, verifies integrity, grants only the exact held target, then signals evaluation once. Crash after consumption or delivery start permanently denies replay; do not regenerate/reset entitlement. A failed scientific gate does not permit retuning or a second assessment.

Current state: owner designated; no owner public key, fingerprint or independent verification supplied; no REAL provisioning receipt, signature or entitlement created. All REAL entrypoints deny with AUTHORITY_PENDING before any D source access or consumption. Completing the candidate checker alone does not establish READY or authorize final validation.

Public fingerprint calculation in PowerShell7 (owner and independent verifier each run it on their separately obtained public file):

```powershell
$publicHex=(Get-Content -LiteralPath ./public.hex -Raw).Trim()
if ($publicHex -notmatch '^[0-9a-fA-F]{64}$') {throw 'Expected only the raw32-byte Ed25519 PUBLIC key in hex'}
$publicBytes=[Convert]::FromHexString($publicHex)
[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($publicBytes)).ToLowerInvariant()
```

This operates only on the public key; it neither creates nor reads a private signing key. Record both independently obtained outputs, verifier identity/channel/time and the common provisioning ID. A second calculation by the same assistant is not a substitute for the designated human verification procedure.
