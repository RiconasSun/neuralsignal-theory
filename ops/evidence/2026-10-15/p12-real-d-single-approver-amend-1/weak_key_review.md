# Independent P1 finding — weak Ed25519 authority keys

Mission: `P12-REAL-D-SINGLE-APPROVER-AMEND-1`.

Decision: **P1 / HOLD AMENDED AUTHORITY READINESS AND FURTHER SYNTHETIC EXECUTION** until a corrected frozen candidate and affected regression evidence are independently reviewed. Revision-2 preexecution approval is withdrawn for subsequent execution/final readiness. Preserve that approval, its original scope, source bytes and failed/interrupted attempt as history. This finding does not authorize any REAL operation.

## Evidence and impact

Affected freeze SHA256: `b9d5b5f6e6ed99e14ff189307dec0f16c0cde46f474e91b31bd22d9f8def4e9d`. `paper12_singleowner1/owner_protocol.py:18-22` accepts any 64-hex representation that `Ed25519PublicKey.from_public_bytes` constructs. It establishes encoding length and computes a fingerprint, but does not enforce a canonical, nonidentity, prime-order curve point.

The parent's preserved synthetic-only `weak_key_reproduction.json`, SHA256 `ce821e85f465cf8d13262538f40fa6680f50a990269fa7fff8a8194dde239d15`, reports that the frozen cryptography verifier accepts public key `01` followed by 31 zero bytes and signature `01` followed by 63 zero bytes for its arbitrary public message. No private key is used. This reviewer inspected that source and receipt without re-executing the probe. The prior 33 passing tests and review did not establish algebraic public-key validity and are insufficient for this security requirement.

The identity point can satisfy a degenerate verification equation without possession of a secret signing key. Consequently a syntactically valid key, derived SHA256 and accepted signature do not establish the claimed owner key possession. Local confirmation/attestation does not repair the cryptographic defect. A weak authority anchor could also undermine future approval verification. No REAL authority or release was established in this mission; that boundary must remain false.

## Minimal complete repair

Centralize fail-closed public-key validation before creating a challenge, accepting a proof/candidate, importing a trust root or returning an authority key. Require canonical compressed encoding, successful on-curve decoding, nonidentity, and membership in the prime-order subgroup. For Ed25519, the public point must satisfy `[L]P = identity` and `P != identity`, with canonical decoding; merely rejecting the single demonstrated byte string or only checking curve membership/cofactor multiplication is insufficient. Retain original Ed25519 release-signature/schema and all scientific code/thresholds.

A vetted point-validation implementation is preferable to adding unreviewed arithmetic. The [official libsodium point-arithmetic documentation](https://doc.libsodium.org/advanced/point-arithmetic) describes `crypto_core_ed25519_is_valid_point` as checking canonical curve points, main-subgroup membership and exclusion of small order, but also documents mixed-order acceptance in affected older implementations and a subgroup-check workaround. The [official PyNaCl changelog](https://github.com/pyca/pynacl/blob/main/CHANGELOG.rst) records a patched 1.0.20-stable build in PyNaCl 1.6.2. Thus an unversioned API call or a coarse `1.0.20` string comparison alone does not establish safety: pin a known patched build/binary with mixed-order regressions, or add the independently checked complete subgroup condition. Ristretto is not a substitute here because changing the registered Ed25519 authority scheme is outside this minimal repair.

If a dependency is used, bind the exact code/native library identity and public-kit dependency requirements; refuse missing/unsupported validation instead of falling back to length-only validation. If explicit public arithmetic is necessary, independently review canonical point decoding and complete group operations and compare against a vetted oracle. This public-data check requires no signing secrets.

## Required affected evidence

- Preserve the demonstrated universal-forgery vector and verify rejection before challenge/proof/receipt/trust-root acceptance.
- Reject identity, all applicable small-order points, noncanonical field encodings/sign encodings, off-curve points and mixed-order points. Include positive valid generated-key and published-vector checks, wrong-key/altered-message checks and independent oracle comparison where feasible.
- Ensure the new onboarding, protected import, REAL/SYN authority integration, public toolkit and independent saved binding verifier apply the corrected validity rule. Update the exported toolkit/manifest and freeze identities rather than silently replacing historical files.
- Record the interrupted SYN attempt's actual stage, bound termination and cleanup receipts without fabricating normal exits or completed scientific/null counts. Preserve any synthetic consumed entitlement and poison state; never reset its namespace or reuse its approval.
- Freeze the repaired source before affected tests and the fresh registered rehearsal. Do not tune models, relax gates, amend scientific mathematics, access protected real data or use this repair to clear historical failures.

The user's single-owner authorization remains applicable; no second human or manual fingerprint requirement should be reintroduced. Genuine owner readiness, REAL signature/release/evaluation and scientific validation remain false pending their original required evidence and separate authorization.
