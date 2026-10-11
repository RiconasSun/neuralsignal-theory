# A10 One-Command Reproduction

Status: implemented for current A/B diagnostics and Dataset C final holdout when Dataset C states are supplied.

## Target Command

```bash
make reproduce-paper2
```

Windows/PowerShell equivalent for A/B diagnostics:

```powershell
.\paper2\scripts\reproduce-paper2.ps1
```

Dataset C final holdout command:

```powershell
paper1\.venv\Scripts\python.exe paper2\scripts\run_paper2.py --dataset-c-states paper2\external_holdout\stage_states_dataset_c.csv
```

## Required Behavior

The command should:

```text
validate environment
locate datasets A, B, and C
verify manifests
reproduce Paper 1 A -> B failure
run measurement shift analyses
run state representation analyses
run task-context shift analyses
run ontology stress tests
run failure attribution
freeze v2
evaluate Dataset C once under frozen rules
run statistics
generate tables
emit claim audit
```

## Current Status

```text
Implemented:
E9.0 Failure reproduction
E9.1 Measurement shift
E9.2 State representation shift
E9.3 Task-context shift
E9.4 Ontology stress test
E9.5 Failure attribution
E9.6 Frozen v2 diagnostic candidate
E9.7 Dataset C final holdout
E9.8 Claim audit

Not bundled into make:
Dataset C 3.3 GB BOLD download
Dataset C E1 extraction command
```

Dataset C state artifact:

```text
paper2/external_holdout/stage_states_dataset_c.csv
```
