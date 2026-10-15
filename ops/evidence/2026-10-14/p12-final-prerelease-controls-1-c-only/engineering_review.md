# Independent engineering and safe-STOP review

Mission: `P12-FINAL-PRERELEASE-CONTROLS-1`, explicitly authorized one-attempt C-only continuation.
Reviewer: independent agent `/root/final_custody_review`. The reviewer inspected frozen source, public saved numerical/custody receipts, hashes and artifact-existence metadata. No real C/D input arrays, private model arrays or key contents were opened; no import workaround, validation/sealing retry, repair, fit or release was performed.

Decision: **ARCHIVE_EVIDENCE_ONLY** for the stopped run, after final sealed saved reproduction and normal `origin/test` Git verification. A known P1 engineering defect remains unresolved. This is not MERGE_ALLOWED, engineering-control PASS, complete C sealing, overall real C calibration PASS or scientific validation. No D action is approved.

## Reviewed identity and scope

Continuation base: `2597bb8d71dd4c4454412181fe522727e7ed4c0d`; original mission base: `cbf3ef5b69c2fe8ba6720d32eb5a031194dcd74f`.

Candidate manifest SHA256: `6e63f4272fb0162b31cff22f8c00f9400e3227270786fb17b867d3e4f52a84f0`. Independently checked all 28 listed file hashes with zero mismatches. Listed paths contain no private directory, native job/export, compartment key/ciphertext, NPZ or NWB payload. The new D partition artifact is metadata only and creates no release entitlement.

All 92 source identities still match frozen snapshot `dc48694e8c42843bc8923660d38dc5cc816eff9b2ebefe9bd2f6b36c33ef13d7`. The prior E3 engineering review remains byte-identical at `40035736090b2f40f66d8730adda36943e0ab81b8961a453ca8a40426960d11e`. Earlier approvals, unsuccessful reviews and scientific failures remain historical evidence, not substitutes for the new required gate.

## Unresolved P1 and STOP correctness

The native C worker completed, but the mandatory host seal failed at `release_control.py:130`, `from selection import views`, reached through `real_C.py:120` and `state_manifest.create`. The fresh real/prospective-roster branch does not establish that host dependency. The earlier retrospective synthetic branch imported calibration and indirectly cached selection, masking the missing dependency; the native worker has its own copied selection module. This is a host packaging/import defect, not evidence of a gradient or optimizer failure.

The earlier engineering review missed that host branch distinction. Its prospective approval cannot override the observed failure. Current ENGINEERING_CONTROL_PASS=false, COMPLETE_C_SEAL_PASS=false and REAL_C_CALIBRATION_PASS=false are required; retaining HISTORICAL_E0_E3_PASS=true separately is accurate. bug_count=1 and warn_count=1 preserve the current defect and missing complete seal evidence.

The required error triggered STOP. Saved evidence records one native C worker invocation, zero fit retries, zero seal retries and no source repair. Independent existence checks confirm both the complete `C_state_manifest.json` and public `C_sealing_receipt.json` are absent. The 1,858-file partial inventory explicitly identifies an incomplete failed seal and is not a release-controller C manifest. No private partial array was loaded or validated by this review.

## Bounded positive evidence

Saved receipts support REAL_C_NUMERICAL_FITS_PASS=true: 13 mice, 26 subfields, 290 cases, 21,716 GLM unit fits, 78 joint N seed fits, 26 coefficient-mean certificates, and 40,104 model-unit endpoint certificates. Maximum original PG is 0.0002573605165640388 and AD scaled error 5.510782802309322e-15 under unchanged limits. Native exit/cleanup are zero and every mandatory view retains 13 paired mice. These facts do not clear the failed complete-state seal.

The public custody audit records 26 actual protected D open denials without byte reads, exact C masks/selections and denied issuer-key access. The legacy native fields `final_values_exposed_to_analysis=false` and `final_holdout_evaluated=false` must not be interpreted as no C access: the same receipt explicitly identifies authorized real C execution. D_AUTHORIZED, D_RELEASE_CONSUMED and D_EVALUATION_EXECUTED remain false. No final D inference, score, null or QC is claimed.

The attempt archive SHA256 matches its index. Its index contains 45,650 JSON receipt members, with no private-prefixed files, path traversal, arrays, keys, ciphertext or NWB member names. Full member-byte verification remains part of the final saved-only reproduction. The new reproducer imports no calibration, release controller or state validator, cannot retry sealing, and explicitly rejects a false complete/control PASS. It preserves the failure rather than correcting it.

## Traceability and permitted closure

All 67 baseline requirements remain traceable: 64 VERIFIED, two BLOCKED_HUMAN_INPUT (REQ-027 and REQ-057), and one IMPLEMENTED_UNVERIFIED Git predicate before commit. The prospective count of 65 after actual Git readback does not waive the two complete-seal requirements. No full-mission PASS is permitted.

Final closure must seal both independent reviews, complete saved-only reproduction and exact preservation of all 22,296 prior tracked bytes with the original daily file retained as an exact suffix, stage only mission artifacts, and verify normal `origin/test` push/readback, changed-file hashes and a clean working tree externally. These final checks remain pending in this review; no force/main/PR operation is approved.

The separately described bounded packaging repair and saved-state-only sealing study is a proposal only. It requires new direct authorization, prospective fresh-host regression and independent review; no additional C input loading, new fits, modifications of the failed partial directory or D authority follows from this archive decision.
