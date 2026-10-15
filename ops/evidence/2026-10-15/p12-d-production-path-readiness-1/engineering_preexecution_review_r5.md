# Independent engineering preexecution addendum — revision 5

Mission: `P12-D-PRODUCTION-PATH-READINESS-1`.

Decision: **APPROVE_SYNTHETIC_REHEARSAL_ONLY** in a new append-only `synthetic_2` namespace under the unchanged registered full scientific budget. P0 = 0; P1 blocking this synthetic execution = 0. No REAL authority, signature, data access, consumption or evaluation is approved.

Reviewed exact on-disk revision-5 freeze SHA256 `c586b016071c0e4c15e81e46323fd510ff096ad3a2b7046c1c48acebe5b59d07`; all 19 file hashes match. Comparing the preserved revision-4 freeze shows only `run_synthetic.py` and `test_engineering.py` changed. The fixture now obtains a UUID hexadecimal property through `synthetic_authorization_id()` rather than calling that string. A focused regression checks identifier type, hexadecimal format and uniqueness. `focused_r5.log` SHA256 `83c3c3ca90e67a5d3b96e90e1dd9d8cbba5fb69faa0d52bbd489ee4a77616875` reports 20 tests, all PASS.

The first failed synthetic attempt is retained. Public reconciliation SHA256 `12b8018283510b2ebaff52b95d4aa629bc7b05ca5fcd83114a3054895c3a7e08` reports zero approval files, consumed files, assessment starts and new fits; the referenced failure and native receipts match their recorded hashes. Both native receipts record profile cleanup `0x00000000`. Their process exit fields are null, so this review does not represent the interrupted preparation as a successful normal native execution.

The revision-4 security/entrypoint review remains applicable to unchanged files. Final readiness still requires matching fresh actual-role, full cohort/null analysis, failure, durable consumption/delivery and exit/cleanup evidence. This review is a prospective SYNTHETIC_D engineering artifact, not completed runtime proof, independent human authority or scientific validation.

Review actions were public-source/hash/evidence reads only. No protected REAL data, arrays, ciphertext or keys were opened; no experiments or release operations were executed by the reviewer.
