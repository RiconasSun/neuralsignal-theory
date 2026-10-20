# A1-A10 claim-to-evidence audit

All rows concern the stopped R3 Development mission. Independent final review remains a separate receipt.

| ID | Topic | Evidence in R3 unless specified | Claim boundary |
|---|---|---|---|
| A1 | Frozen scientific question and scope | paper16_m1/M1_SCIENTIFIC_PROTOCOL.md; SOURCE_PINS.json | Exploratory Development only; no E result |
| A2 | Exact models, feature/scaler and causal equations | PREFIT_FREEZE_MANIFEST.json; PHASE_B_REUSE_DIFF_1.json | No mathematical amendment |
| A3 | 27-mouse source and provenance | SCHEMA_AUDIT_2.json; metadata_compat/; PHASE_A_REVIEW_2.md | 27/28 admitted,5 BO22 FC; excluded source unreplaced |
| A4 | Original units, masks, role partitions | PHASE_A_RESULTS.json; results/PANEL_PREFIT_PLAN.json; results/ACCESS.jsonl | Original masks retained; A/B only |
| A5 | Initialization, seeds, grid and selection | results/TASK_PLAN.json; results/B_SELECTION.json | 648 B1 A passes; global lambda1; no E tuning |
| A6 | Numerical reliability | PRODUCTION_NUMERICAL_CERTIFICATION.json; NUMERICAL_FAILURE_SUMMARY.json; FAILED_COORDINATE_EVIDENCE.csv | Engineering pass is not real convergence; required PG failure |
| A7 | Mouse-level uncertainty and multiplicity | E_EFFECTS.csv; SENSITIVITY_CONTROL_STATUS.csv | All E statistical results NOT_EXECUTED; no equivalence/absence claim |
| A8 | Sensitivities and controls | results/PANEL_PREFIT_PLAN.json; TASK_OUTCOMES.json | Partial A panel fits only; no completed E sensitivity/null suite |
| A9 | Saved and executable reproduction separated | REPRODUCE_R3_ARCHIVE.ps1; archive_check.py; PREFIT_FREEZE_MANIFEST.json | Saved-only verification; do not rerun consumed scientific stage |
| A10 | Claims, history and limitations | SCIENTIFIC_LIMITATIONS.md; HISTORICAL_R2_MANIFEST.json; SCIENTIFIC_CLOSEOUT.md | No causal, physical-state,CWP/NAP,replication or Final validation claim |
