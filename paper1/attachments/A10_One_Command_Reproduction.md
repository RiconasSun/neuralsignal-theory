# A10 One-command Reproduction

## Command

For a complete rerun from downloaded raw data:

```powershell
cd "C:\Users\85993\Desktop\codebase\neuralsignal institute"
cd paper1
.\.venv\Scripts\python.exe scripts\run_e1_e8.py
```

Equivalent explicit commands are:

```powershell
.\.venv\Scripts\python.exe scripts\e1_extract_states.py --events-glob "data_raw\ds001635\**\*events.tsv" --bold-glob "data_raw\ds001635\**\*_bold.nii.gz" --native-grid --grid-bins 6,6,6 --tr 2.0 --hrf-lag 4.0
.\.venv\Scripts\python.exe scripts\e2_cwp_existence.py --states state_extraction\stage_states.csv --split subject
.\.venv\Scripts\python.exe scripts\e3_task_vs_cwp.py --states state_extraction\stage_states.csv
.\.venv\Scripts\python.exe scripts\e4_unseen_combination.py --states state_extraction\stage_states.csv
.\.venv\Scripts\python.exe scripts\e5_unseen_domain.py --states state_extraction\stage_states.csv
.\.venv\Scripts\python.exe scripts\e6_null_falsification.py --states state_extraction\stage_states.csv --permutations 100
.\.venv\Scripts\python.exe scripts\e1_extract_states.py --events-glob "data_raw\ds001634\**\*events.tsv" --bold-glob "data_raw\ds001634\**\*_bold.nii.gz" --native-grid --grid-bins 6,6,6 --tr 2.0 --hrf-lag 4.0 --timeseries-out-dir "external_validation\input_timeseries" --out "external_validation\stage_states_external.csv"
.\.venv\Scripts\python.exe scripts\e7_external_dataset.py --train-states state_extraction\stage_states.csv --external-states external_validation\stage_states_external.csv
.\.venv\Scripts\python.exe scripts\e8_statistics_reproduction.py
```

## Current Reproduction Result

```text
status: completed_audit_not_claim_validated
Gate A incremental: INCONCLUSIVE
Gate B OOD: PASSED
Gate C external: FAILED
```

## Final Outputs

```text
paper1/state_extraction/stage_states.csv
paper1/external_validation/stage_states_external.csv
paper1/results/e2_cwp_existence_metrics.csv
paper1/results/e3_m0_m4_metrics.csv
paper1/results/e4_unseen_combination_metrics.csv
paper1/results/e5_unseen_domain_metrics.csv
paper1/results/e6_null_falsification_metrics.csv
paper1/external_validation/e7_external_dataset_metrics.csv
paper1/results/primary_metrics.csv
paper1/results/subject_level_effects.csv
paper1/results/claim_audit.json
```

## Claim Boundary

The current one-command-equivalent run does not support the strong Paper 1 claim.
