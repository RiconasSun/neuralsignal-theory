# P11 M1 Verdict

mission_id: paper11-m1
final_status: PASS
milestone_gate: M1 PASS (acquisition/anatomy/alignment/QC only)
scientific_verdict: NOT_EVALUATED
bug_count: 0
warn_count: 0
baseline_requirement_count: 8
verified_baseline_count: 8
required_items_omitted: 0
required_behaviors_silently_reduced: 0
unapproved_existing_behaviors_removed: 0
required_tests_silently_removed: 0
unresolved_shrink_risk: 0
temporary_substitutes_remaining: 0
coverage_reductions_without_approval: 0

## Fresh Evidence

Prechange identity: d30170810a8498137b6d84b66a5b1ea7694496ae; clean tree.
M0 gate/source identity: verified PASS, all 16 inputs unchanged and no output rewrite.
Pinned real acquisition: 221 files, 39259790 bytes, expected Git blob plus SHA256.
9 subjects, 37 sessions, 23 qualifying sessions, 613 primary eligible
hippocampal session-local units. 630 units pass unit-level QC including units in
small populations. Paired sessions: 36. Unpaired: sub-08/ses-05.
Actual frozen split SHA256:
d66ff7cc5dcadf3e0b7f18bfddcb50f3baa8fe59fc28b999910b3b66bd3e1eaa.

Commands:
powershell -NoProfile -ExecutionPolicy Bypass -File paper11/scripts/reproduce-m1.ps1 -Acquire
powershell -NoProfile -ExecutionPolicy Bypass -File paper11/scripts/reproduce-m1.ps1
Final offline replay exit 0; 22 tests passed, zero skips. The temporary CSV-reader
regression FAIL was preserved and corrected with stronger regression coverage.

Load-bearing artifacts:
paper11/results/M1/gate_result.json (source SHA256 identity and timestamps)
paper11/results/M1/tests.txt and execution.log
paper11/results/M1/qc_report.json and QC_REPORT.md
paper11/results/M1/unit_qc.csv, session_qc.csv, subject_coverage.csv
paper11/results/M1/trial_alignment_qc.json and claim_audit.json
paper11/data_manifest/M1/trial_splits.json, split_lock.json and acquisition_receipts.json
paper11/MILESTONE_STATUS.md and REPRODUCE_M1.md

Raw experimental bytes stay ignored/local. Derived data license preserved.
No heldout timestamp evaluation, model fitting, M2 features or external test.
No NAP/CWP or discrete/continuous/hybrid preference claim.
Final post-commit verification binds the gate to the candidate; subsequent
evidence-only commits preserve the same source/split/protocol SHA256 identity.
Review: M1-only upload approved. Push: origin/test, final remote match verified.
Remaining blockers: none for M1. Next required action: stop after M1.
