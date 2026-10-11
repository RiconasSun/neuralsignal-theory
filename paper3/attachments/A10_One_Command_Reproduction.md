# A10 One-command Reproduction

Run on this Windows workspace:

```powershell
powershell -ExecutionPolicy Bypass -File paper3\scripts\reproduce-paper3.ps1
```

If GNU Make is available, this equivalent target is also defined:

```powershell
make reproduce-paper3
```

Equivalent explicit commands:

```powershell
paper1\.venv\Scripts\python.exe paper3\scripts\run_paper3_e1.py
paper1\.venv\Scripts\python.exe paper3\scripts\run_paper3_e2_e8.py
```

Expected primary outputs:

```text
paper3/results/e1_input_audit.json
paper3/results/e2_transition_reliability_rows.csv
paper3/results/e3_cross_run_summary.csv
paper3/results/e4_same_vs_different_summary.csv
paper3/results/e5_dataset_specific_reproducibility.csv
paper3/results/e6_cross_dataset_reproducibility_summary.csv
paper3/results/e7_null_tests_summary.csv
paper3/results/e8_claim_audit.json
paper3/manuscript/PAPER3_MANUSCRIPT_CURRENT.md
paper3/submission/PAPER3_BIORXIV_DRAFT_CURRENT.pdf
```
