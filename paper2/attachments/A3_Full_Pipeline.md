# A3 Full Pipeline

Status: implemented for A/B diagnostics and Dataset C final holdout.

## Computational Path

```text
raw data
-> QC
-> measurement alignment variants
-> state representation variants
-> task-context descriptors
-> ontology variants
-> cross-dataset transfer models
-> failure attribution
-> frozen v2 representation
-> Dataset C final holdout
-> statistics
-> figures/tables
-> claim audit
```

## Required Experiments

- E9.0 Failure reproduction.
- E9.1 Measurement shift.
- E9.2 State representation shift.
- E9.3 Task-context shift.
- E9.4 Ontology stress test.
- E9.5 Failure attribution.
- E9.6 Frozen v2 representation.
- E9.7 Dataset C final holdout.
- E9.8 Statistics and claim audit.

## Current Implementation Status

```text
Implemented:
E9.0-E9.8 A/B diagnostics
Dataset C metadata audit
Dataset C event standardization
Dataset C E1 state extraction
Dataset C E9.7 final holdout comparison
Dataset C E9.8 claim audit
```

## Reproduction Target

```bash
make reproduce-paper2
```

Dataset C final holdout command:

```powershell
paper1\.venv\Scripts\python.exe paper2\scripts\run_paper2.py --dataset-c-states paper2\external_holdout\stage_states_dataset_c.csv
```
