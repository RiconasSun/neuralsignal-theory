# P11 M0 Verdict

mission_id: paper11-m0
final_status: PASS
milestone_gate: M0 PASS (engineering/protocol only)
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

## Evidence

- paper11/protocol/protocol.json and freeze.json: prospective protocol and immutable input digests.
- paper11/environment/environment.json: actual Python 3.11.15 and installed version inventory; M0 uses stdlib only.
- paper11/data_manifest/source_receipts.json: nine real HTTP 200 metadata receipts, pinned commits/releases and SHA256.
- paper11/results/M0/tests.txt: 16 tests, all passed, zero skips.
- paper11/results/M0/qc_report.json: source/environment/protocol integrity and P1-P10 preservation.
- paper11/results/M0/gate_result.json: PASS with exact 16 frozen input hashes, freeze digest and execution timestamps.
- paper11/results/M0/claim_audit.json: no scientific verdict, model comparison NOT_RUN, no NAP/CWP validation.
- paper11/MILESTONE_STATUS.md: M0 PASS, M1-M7 NOT_STARTED.

Real verified command:
powershell -NoProfile -ExecutionPolicy Bypass -File paper11/scripts/reproduce-m0.ps1
Exit: 0. Original sandbox Temp failure is preserved; successful execution used
normal local permissions without source/test/protocol edits after freeze.

## Scientific Boundary

Nine primary metadata participants and fifteen companion metadata participants
are not a hippocampal eligible cohort. Anatomy, unit quality, trial alignment and
external task compatibility await M1/M6. No spikes or models were analyzed. No
heldout data were accessed, no scientific winner determined. Protocol thresholds
are prespecified design choices, not empirical findings or power calculations.

Prechange identity: d1ff39d028815b15bbad84b9ed6fd6d896eab0cf, clean tree.
Candidate identity: frozen SHA256 24938ea54f0766af41f5989946b9b722c42ca49b7f4f59a2358a20bfdae10e73 plus per-input hashes in gate_result.json.
Final gate rerun after commit binds outputs to that commit; evidence-only closure
changes do not change the frozen relevant scientific/tooling input identity.
Review: scoped M0 upload allowed; no main promotion.
Push destination: origin/test; final remote hash verified before terminal report.
Remaining blockers: none for M0; M1 eligibility NOT_ASSESSED, not an M0 defect.
Next required action: stop; a separate request is required to execute M1.
