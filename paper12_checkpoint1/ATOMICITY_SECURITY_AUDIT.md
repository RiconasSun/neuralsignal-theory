# Atomicity, Recovery and Isolation

Candidate3 retains the registered200 noninjected operations,100 each in the main
trusted host and a fresh trusted child process. They are two native process
contexts on one Windows machine/volume, not independent OS replications.

All200 committed envelopes pass full source/body SHA256, length and custody-DACL
checks. A repeated identical request returns a verified idempotent result without
publication. No native denial/retry event occurred in these200 operations.
Eight separately registered size boundaries passed: six complete commits through
4MiB and two oversized expected stops; expected stops are not successful commits.

All18 named injections retain separate results. Persistent locked-target denial
exhausts exactly3 calls, retains the old artifact and persists STOP. Releasing the
lock does not reset the budget. A saved nonretryable result stops without a STOP
file. Shared-delete reader retains a complete old snapshot while a complete new
artifact appears. Conflicting separate-process writer receives native33.

Mid-write process termination leaves a partial staging envelope, preserves the
complete old artifact, and fails closed on resume. Termination before publication
resumes a verified stage; termination after publication reconstructs success by
verifying the complete target rather than trusting a missing receipt. Missing,
partial, corrupt, identity/hash-mismatched, readonly, traversal and reparse inputs
are never accepted as committed. Scope rejection is not an actual cross-volume
movement test. Full journal identities remain256-bit despite compact names.

Fresh zero-capability native AppContainer was denied the actual repaired
synthetic checkpoint and synthetic key, DACL regrant, direct network access
(10013), and custodian memory access. Host-positive checkpoint oracle verifies
the envelope/source/digest/length independently of the32-byte key. Copied runtime
imports and synthetic AEAD roundtrip passed. Only new-study runtime ACLs change;
historical runtime and all real custody artifacts remain untouched.

No unrestricted neural vector, final count, experimental key or unit statistic
was read/exported. No neural source request, source extraction, final unlock,
model fitting or M3-M7 execution occurred. No malicious-host/admin defense or
power-failure consistency guarantee is claimed.
