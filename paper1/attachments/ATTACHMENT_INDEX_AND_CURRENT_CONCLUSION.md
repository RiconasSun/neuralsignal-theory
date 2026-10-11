# Attachment Index and Current Conclusion

Date: 2026-09-01

## Files Produced

Protocol and execution:

```text
paper1/protocol.yaml
paper1/README.md
paper1/Makefile
paper1/results/environment.lock
```

Experiment scripts:

```text
paper1/scripts/e0_data_qc_audit.py
paper1/scripts/e1_extract_states.py
paper1/scripts/e2_cwp_existence.py
paper1/scripts/e3_task_vs_cwp.py
paper1/scripts/e4_unseen_combination.py
paper1/scripts/e5_unseen_domain.py
paper1/scripts/e6_null_falsification.py
paper1/scripts/e7_external_dataset.py
paper1/scripts/e8_statistics_reproduction.py
paper1/scripts/run_e1_e8.py
```

Attachments:

```text
paper1/attachments/A1_Frozen_Protocol.md
paper1/attachments/A2_Dataset_Manifest.md
paper1/attachments/A3_Full_Pipeline.md
paper1/attachments/A4_Baseline_Results.md
paper1/attachments/A5_Holdout_Audit.md
paper1/attachments/A6_Statistics.md
paper1/attachments/A7_Null_Falsification.md
paper1/attachments/A8_QC_Leakage_Audit.md
paper1/attachments/A9_Limitations_Failed_Analyses.md
paper1/attachments/A10_One_Command_Reproduction.md
paper1/attachments/CONCLUSION_CURRENT.md
paper1/attachments/RESULTS_CURRENT.md
paper1/attachments/PAPER1_REPOSITIONING.md
paper1/attachments/EXTERNAL_FAILURE_AUDIT.md
```

Machine audit/result outputs:

```text
paper1/data_manifest/dataset_manifest.csv
paper1/data_manifest/trial_counts.csv
paper1/data_manifest/qc_subjects.csv
paper1/data_manifest/e0_summary.json
paper1/state_extraction/e1_summary.json
paper1/external_validation/e1_summary.json
paper1/results/e2_cwp_existence_summary.json
paper1/results/e3_m0_m4_summary.json
paper1/results/e4_unseen_combination_summary.json
paper1/results/e5_unseen_domain_summary.json
paper1/results/e6_null_falsification_summary.json
paper1/external_validation/e7_external_dataset_summary.json
paper1/results/claim_audit.json
```

## Operations Performed

1. Installed `openneuro-py`.
2. Downloaded ds001635 events and BOLD from OpenNeuro.
3. Downloaded ds001634 events and BOLD from OpenNeuro.
4. Implemented E0-E8 local execution scripts.
5. Generated fixed native-grid 216-ROI state representations.
6. Ran E0-E8 through E8.
7. Updated A1-A10 attachments and current conclusion.

## Observed Real-data State

```text
E0 status: PASS
n_events: 48
n_roi_timeseries: 48
n_bold: 48
n_confounds: 0
external_stage_states_present: true
```

E1:

```text
ds001635 states_extracted: 2291
ds001634 states_extracted: 3066
roi_count: 216
```

E8 claim audit:

```text
Gate A incremental: INCONCLUSIVE
Gate B OOD: PASSED
Gate C external: FAILED
claim_allowed_cwp_foundation_holds: false
```

## Current Conclusion

The Paper 1 computational package is implemented and has been run on downloaded OpenNeuro data. The strong Paper 1 claim is not supported by the current run.

Repositioned title:

```text
CWP-style Compositional Representations Improve Within-dataset OOD Brain-state Prediction but Do Not Yet Generalize Across Independent Datasets
```

Allowed conclusion:

```text
Within ds001635, CWP-style compositional labels improved OOD prediction in leave-one-combination and unseen-domain tests.
```

Not allowed:

```text
CWP is validated.
CWP clearly outperforms task labels overall.
CWP has passed external replication.
```
