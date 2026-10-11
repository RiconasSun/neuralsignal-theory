# Autonomous P11 Execution Verdict

Mission: paper11-autonomous. Final status: WAIT_FOR_HUMAN_INPUT.
M0-M3 PASS; M4 FAIL / INCONCLUSIVE; M5-M7 NOT_STARTED.
Paper complete: NO. BioRxiv-ready: NO. No preferred regime or NAP/CWP validation.

bug_count: 0 remaining implementation/review defects.
warn_count: 5 incomplete full-contract requirements R05/R06/R07/R08/R13.
baseline_requirement_count: 13; verified_baseline_count: 8.
required_items_omitted: 0 (retained, five incomplete).
required_behaviors_silently_reduced: 0; unapproved_existing_behaviors_removed: 0.
required_tests_silently_removed: 0; unresolved_shrink_risk: 0.
temporary_substitutes_remaining: 0; coverage_reductions_without_approval: 0.
Full mission PASS and MERGE_ALLOWED forbidden.
No compensation of missing model/null/statistics results with QC/test successes.

Actual execution: smoke -> two-subject cohort -> 23-session/9-subject training
cohort, 613 session-local units, 622 trials, 292615 conserved preprobe spikes,
1005120 conditional unit-bins. 70 final regression tests passed without skips.
Coverage failure was resolved by public annex acquisition and full inventory.
M2/M3 PowerShell reproduction passed; 483 baseline candidates completed.
Training QC figures rendered and visually inspected. Full-paper reproduction
and full-cohort regime comparisons were NOT executed. M4 smoke PowerShell replay
exited1 at the frozen integration gate: 1024-particle discrepancy
0.0014080063396446991 > frozen0.001 nats/unit-bin. Final holdout unopened.

Source identities and timestamps: paper11/results/M2/gate_result.json.
Historical access attempts and resolution: blocker.md and
paper11/results/M2/coverage_access_evidence.json. Review: review.md.

Anti-shrink: all 13 requirements retained; downstream items remain open/blocked,
not marked N/A or verified. No removed tests, mocks replacing findings, altered
holdouts or Papers 1-10 changes. Count-only provisional PASS was superseded on
scientific review, retained as an attempted-run artifact, never used to advance.

Deliverables: executable training counts and metadata-only NIX validator, real
outputs/logs/QC/gate, progressive figures, explicit incomplete manuscript and
A1-A10 progress attachments. Missing paper outputs are identified, not invented.
Final candidate source identity: closing-audit.json. Scoped staging and remote
verification recorded by Git execution. Required next decision: STOP_DECISION.md.
