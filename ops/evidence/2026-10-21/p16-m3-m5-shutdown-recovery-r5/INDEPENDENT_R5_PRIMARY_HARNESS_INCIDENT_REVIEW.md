# Independent source-only primary harness incident review

Mission: P16-M3-M5-SHUTDOWN-RECOVERY-R5.
Reviewer: /root/r4_interruption_review, 2026-10-21.

Decision: VERIFIED_PRIMARY_AUDIT_HARNESS_SCHEMA_DEFECT; narrowly corrected pre-real preflight execution is permitted under the same original Phase A claim. This is not acceptance or rejection of any fitted state and does not grant Phase A PASS or real fitting permission.

Static evidence:

- Frozen R3 optimizer.py SHA256 `0219392eec78fdba8aadc6f6fc1497abe55bad02e12ba0ab25e7d0a2df62b89b`. Its lines 69–71 record FG reservation event/call/iterations and completion event/call/objective/gradient_inf. Per-call x and full gradient fields were never written by that producer. Accepted vectors and three full coordinate certificates are separate original artifacts.
- Frozen R4 optimizer.py SHA256 `17f96fba6720aad1a8ae65d90f04c645dd047de5fb033064ed9f02e0750d0114`. Its FG writer adds x/full-gradient fields, and its certificate writer adds DIAGNOSTIC_CALLS reservations.
- Preserved PRIMARY_SAVED_AUDIT_ATTEMPT1.py SHA256 `4d5f76c7c4366c538376802ba514f882e996140c585056b1f9d5938490912c95`. Its journal helper unconditionally invokes the later feasibility helper call_prefix and indexes pre['x']/post gradient semantics before considering the origin. That helper requires fields absent from the original R3 schema. The first R3 target therefore encounters an invalid harness assertion; the traceback alone is not the basis for this classification.

The correction must branch on the registered producer origin. R3 retains complete original scalar FG accounting, finite objective/norm history, accepted-vector sequence, original initializer/bounds, endpoint and all three coordinate certificates. R4 additionally requires its original per-call vectors and full diagnostic reservation journal. No missing historical field may be synthesized, no coordinate certificate or endpoint may be recalculated, and no newly relaxed numerical threshold is permitted. The protocol's preservation of distinct historical producer policies requires this distinction; imposing R4 serialization retroactively on R3 would invent a requirement.

The independent script registration preceded private state checking and explicitly documented this producer difference. Its original audit source remains SHA256 `7f2903621b3cd88dd6282b024cf9bd476b348f04e336010db552f2ce4f8ff14f` and does not impose the invalid R4 fields on R3. The independent audit is conducting its own complete qualification; it has not adopted the primary matrix or any new primary PASS result.

All primary failed source, launch attempts, registration, stop/classification receipts and ledger fragments must remain append-only evidence. A revised primary harness must be prospectively registered with old/new exact hashes and this limited correction, and remain inside the original 24-hour claim. This pre-real implementation repair is authorized by the frozen protocol. It is not a new scientific fit, a resumed R4 clock, an optimizer retry, a replacement state, a certificate recomputation or an automatic admission. If the corrected audit encounters an actual mandatory state identity/certificate failure, it must immediately stop without auditing later targets or substituting a state.

This record is based on static frozen producer/helper source and the preserved failed harness source only. It does not certify private states, the complete primary matrix, the new production implementation, synthetic tests, M4, E or Final. Those gates remain separate. No numerical or scientific operation was performed to produce this incident classification.
