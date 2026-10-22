# Independent prefit review 1 — candidate 3 requires repair

Mission: P16-M3-M5-SHUTDOWN-RECOVERY-R5. Reviewer: /root/r4_interruption_review, 2026-10-21.

Decision: CHANGES_REQUIRED_P1. Open P0=0; open P1=3 (two implementation/evidence-gate defects and one mandatory-negative coverage gap). No PREFIT_APPROVAL is issued. No new real A, E or Final execution is permitted by this review. The complete historical 3,992+216 independent reuse qualification remains valid and separately accepted; these findings concern the new execution wrapper and its certification coverage.

Scope is the immutable candidate-3 source archive, certification 3 and prefit freeze 1, not the evolving candidate-4 implementation. PREFIT_FREEZE_MANIFEST.json SHA256 is `b22c7ae6b5acab35306d4f71c11b8a6125c8a987c6261e5af85bc31385cf549e`. The five files in CANDIDATE_3_SOURCE were independently checked byte-for-byte against their original source hashes in that manifest. Certification 3 actually passed 50 methods with no failures/errors/skips under a native Windows Job; that fact remains preserved. Passing those methods does not demonstrate every registered requirement when a relevant semantic case was not exercised.

## P1-001 — actual clock/process failure classification

The original clock_bound.guard and verify_stage_environment raise paper16_dev_r3.core.ResourceStop. It is distinct from paper16_development_r4.core.BudgetStop. Candidate-3 worker exception handling recognizes only the latter as STOP_BUDGET_REQUIRED_GATE; actual deadline, stale-clock or changed-boot exceptions therefore fall into STOP_ACCESS_OR_IMPLEMENTATION_REQUIRED_GATE. This loses the registered budget/interruption distinction. Existing clock tests asserted an exception, not the resulting saved scientific category. Bootstrap and native-supervision outcomes also require preservation of actual exit/clock/Job evidence and nulls where unavailable, without manufacturing a process exit.

Required correction: a small, explicit wrapper classification using actual exception type and bounded stage evidence, with semantic deadline, boot/interruption, local budget and native missing/abnormal-receipt tests. Preserve original native outcomes, failed sources and tests. Do not change an objective, optimizer, scientific threshold, wall limit or original clock helper.

## P1-002 — incomplete coordinate state can appear complete at readiness

Candidate-3 verify_completed checks result numerical_pass/PG, counters, endpoint hash and DIAGNOSTICS all_checkpoints_pass/length. It does not check the coordinate_state file, its members or the actual three saved coordinate/checkpoint acceptance conditions. A missing/corrupt coordinate certificate with retained truthy summary fields is therefore not rejected by this completion-readiness check. Downstream independent M4 review still prevents scientific M4 PASS, but the registered incomplete-state-as-complete negative gate and complete-state readiness are insufficiently enforced here.

Required correction: saved-state-only integrity and member/coordinate validation under the unchanged original numerical rules. Distinguish R3's original journal schema. Add synthetic metadata/array cases where apparently completed results have missing/corrupt coordinate files or invalid required checkpoint evidence. Do not call a real objective/gradient/AD/FD function or regenerate historical certificates.

## P1-003 — registered negative cases not demonstrated by method count

The candidate-3 fixed-FD test checks constants, but does not present a case where the original h=1e-5 fails while a different scanned h passes; it therefore does not exercise rejection of favorable post-result step choice. The suite also lacks targeted tests for historical failed/diagnostic/partial state mixing at the new reuse gate, wrong-unit or scaler-member/hash failures at the new prepared-input gate, a D/S group missing exactly one seed, and actual Phase-A/Phase-B registered-span extension. Generic text-manifest tampering and the inherited source-adapter tests do not independently exercise these new branches. The existing clock test name includes extension, but its inputs cover unknown phase, no-reset, expired/backward clocks and boot mismatch rather than an extended phase span.

Required correction: bounded synthetic saved-metadata/array negative fixtures for these precise cases, under a prospectively frozen revised method inventory. Preserve all existing assertions and all previous attempts. A favorable finite-difference scale must not rescue the original failing h. No real fitted state, model, seed, animal allocation, scientific threshold, hypothesis or optimization budget changes are authorized by this request.

## Checks already supported by actual candidate-3 evidence

The native broker tests genuinely denied evaluation 6,001 and accepted-iteration 1,501 before the unauthorized operation; the inclusive 6,000/1,500 fixture completed its required certificate. The suite also exercised original-initializer substitution, outward-PG signs, diagnostic reservation interruption, atomic claim/consume, native wall-bound descendant termination and parent-loss Job behavior, and rejection of non-A entry roles before loading. Byte-copy proofs preserve the original mathematical feature/model/panel code and the optimizer/child with only namespace/Job substitutions. These proofs are retained, but affected source/test changes invalidate the corresponding final-candidate approval until fresh sufficient certification and a versioned exact freeze exist.

The owner-authorized protocol permits pre-real implementation/certification repair inside the same original 24-hour Phase A. Historical state qualification and scientific STOPs are not rewritten. Preserve candidate-3 source, registration/result/supervision, freeze 1 and this unsuccessful review. Re-review the exact revised candidate only after code changes and required tests are complete. No implementation change is implicitly approved by this record.
