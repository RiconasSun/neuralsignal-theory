# Independent security preexecution review — revision 2

Mission: `P12-REAL-D-SINGLE-APPROVER-AMEND-1`; base `6e952aeb0bc19abead5b208327b56298f25dc290`.

Decision: **APPROVE_REGISTERED_SYNTHETIC_ATTEMPT_1_ONLY** for exact revision 2 and the unchanged registered full rehearsal/budget. P0 = 0; P1 blocking this synthetic execution = 0. No REAL authority provisioning, signing, entitlement, protected data access or scientific validation is approved.

Reviewed exact on-disk source-freeze SHA256 `b9d5b5f6e6ed99e14ff189307dec0f16c0cde46f474e91b31bd22d9f8def4e9d`; all 23 candidate file hashes match. All 56 registered original hashes still match. `focused_r2.log` SHA256 `a339c573e57bf34359fdba598f25a4c663a3cbea2b96ada76d0707255e5082c3` reports 33 tests, all PASS. Review was read-only; no tests/experiments/releases were executed by this reviewer and no protected REAL data or keys were opened.

Only `owner_onboarding.py` and `test_owner.py` differ from revision 1. Both prior source files under `source_r1_changed` independently match their preserved r1 freeze hashes; prior reviews/logs remain historical evidence. The r1 review does not certify altered r2 code; this fresh review does.

The owner now returns only an ASCII detached signature file. Software wraps the exact saved challenge body, validates the unchanged strict 128-lowercase-hex signature rule and verifies its signature against the exact setup/owner/mission/base/amendment/ceremony binding before writing proof, confirmation or receipt. The owner still performs one local interactive confirmation; there is no manual fingerprint or second-verifier input. This removes manual proof-JSON composition without changing authorization semantics. No private-key reader, generator, signing interface or REAL release signature path was added.

The full unchanged-source security findings and mandatory downstream conditions from `engineering_preexecution_review_r1.md` remain applicable: synthetic-only onboarding identity/receipts; protected deployment pins and REAL-pending early denial; actual production entrypoint and restricted roles; all 29 controller oracles, eight producer negatives, 13-mouse/208-case/104 x 999 controls and 10,000-bootstrap procedures; preserve failed attempts, all scientific/controller bytes and original budgets. The signature/statement confirms possession and an owner attestation, not remotely proven physical isolation. REAL-shaped unit-test fixtures cannot establish genuine owner readiness.

Final engineering acceptance requires completed matching native exit/cleanup and source/runtime/principal/binding evidence, full output and saved-only reproduction, and independent final reviews. Owner authority readiness and unqualified production readiness remain false while genuine owner setup is absent. Any pending request dossier must remain NOT_SIGNABLE without protected owner provisioning and held live identities. Stop before any REAL approval, release or evaluation.
