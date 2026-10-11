# Paper 1 Workspace

This directory is the frozen execution workspace for Paper 1:

```text
Does CWP generalize better and reuse better than dataset-specific flat Task Label?
```

`protocol.yaml` is the local execution SSOT. The first recommended run order is:

```text
E0 -> E1 -> E2 -> E4
```

No result should be treated as a Paper 1 claim until the relevant protocol gate is run and recorded.

## Environment

Use the local virtual environment:

```powershell
paper1\.venv\Scripts\python.exe
```

Installed dependencies are frozen in:

```text
paper1/results/environment.lock
```

## Run E1-E4 From ROI Time-Series CSV

Expected inputs:

- `paper1/data_manifest/**/*events.tsv`
- `paper1/state_extraction/input_timeseries/**/*.csv`

Time-series CSV files must include:

```text
time, roi_001, roi_002, ...
```

Then run:

```powershell
cd paper1
.\.venv\Scripts\python.exe scripts\run_e1_e4.py
```

## Run E1 From Raw NIfTI + Atlas

If ROI time-series files do not exist yet, provide preprocessed BOLD files and a fixed atlas image:

```powershell
cd paper1
.\.venv\Scripts\python.exe scripts\e1_extract_states.py `
  --events-glob "data_manifest\**\*events.tsv" `
  --bold-glob "preprocessing\**\*bold*.nii.gz" `
  --atlas-img "preprocessing\atlas.nii.gz" `
  --tr 2.0
```

This writes ROI time-series into `state_extraction/input_timeseries/` and stage states into `state_extraction/stage_states.csv`.

## Run E5-E8

After E1 has produced `state_extraction/stage_states.csv`, run:

```powershell
cd paper1
.\.venv\Scripts\python.exe scripts\e5_unseen_domain.py --states state_extraction\stage_states.csv
.\.venv\Scripts\python.exe scripts\e6_null_falsification.py --states state_extraction\stage_states.csv
.\.venv\Scripts\python.exe scripts\e7_external_dataset.py --train-states state_extraction\stage_states.csv --external-states external_validation\stage_states_external.csv
.\.venv\Scripts\python.exe scripts\e8_statistics_reproduction.py
```

E7 requires a second dataset converted into the same stage-state schema with identical `roi_*` columns:

```text
paper1/external_validation/stage_states_external.csv
```

If that file is missing, `make reproduce` skips E7 and E8 records external validation as not evaluated.

## One-command Run

```powershell
cd paper1
.\.venv\Scripts\python.exe scripts\run_e1_e8.py
```

or, if `make` is available:

```powershell
cd paper1
make reproduce PYTHON=.\.venv\Scripts\python.exe
```

## E5-E8 Outputs

- E5: `results/e5_unseen_domain_metrics.csv`
- E6: `results/e6_null_falsification_metrics.csv`
- E6 summary: `results/e6_null_falsification_summary.json`
- E7: `external_validation/e7_external_dataset_metrics.csv`
- E8 primary metrics: `results/primary_metrics.csv`
- E8 subject-level effects: `results/subject_level_effects.csv`
- E8 claim audit: `results/claim_audit.json`

The E8 claim audit is conservative by design: unrun experiments remain `NOT_EVALUATED`, unavailable nulls remain explicit blockers, and no CWP success claim is allowed unless the protocol gates pass.

E0 can be run alone to audit local input availability:

```powershell
.\.venv\Scripts\python.exe scripts\e0_data_qc_audit.py
```

E0 writes:

```text
data_manifest/dataset_manifest.csv
data_manifest/trial_counts.csv
data_manifest/qc_subjects.csv
data_manifest/e0_summary.json
```

## Paper Attachments

The current reproducibility attachment pack is in:

```text
paper1/attachments/
```

Current conclusion:

```text
paper1/attachments/CONCLUSION_CURRENT.md
```
