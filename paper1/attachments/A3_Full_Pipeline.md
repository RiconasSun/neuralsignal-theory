# A3 Full Pipeline

## Implemented Code Path

Common utilities:

```text
paper1/scripts/common.py
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
```

One-command runner:

```text
paper1/scripts/run_e1_e8.py
```

## Computational Path

```text
OpenNeuro download
-> E0 data/QC audit
-> events.tsv + ROI time-series or BOLD/native grid
-> E1 stage-state extraction
-> stage_states.csv
-> E2 stage sanity check
-> E3 M0-M4 subject holdout
-> E4 leave-one-combination-out
-> E5 unseen-domain holdout
-> E6 available null/falsification tests
-> E7 external dataset test when external states exist
-> E8 statistics and claim audit
```

## Environment

Virtual environment:

```text
paper1/.venv
```

Frozen package list:

```text
paper1/results/environment.lock
```

## Verification Already Performed

Static compile:

```text
paper1\.venv\Scripts\python.exe -m compileall paper1\scripts
status: PASS
```

Synthetic smoke:

```text
paper1\.venv\Scripts\python.exe paper1\scripts\smoke_test_e1_e8.py
status: PASS
```

Synthetic outputs were removed after verification and are not evidence for the scientific claim.

Real-data run:

```text
ds001635 E1 states_extracted: 2291
ds001634 E1 states_extracted: 3066
E8 claim audit: completed_audit_not_claim_validated
```
