# A10. One-command Reproduction

Current command:

```powershell
.\paper6\scripts\reproduce-paper6.ps1
```

Current implemented scope:

```text
E1 public dataset audit
E2 event-semantics audit
E2 transition-window manifest
E3 one-run signal extraction smoke
E3-E6 default multi-run signal analysis
E3-E6 full available ds004117 aggregation if batch feature files exist
E7 ds004752 external convergent analysis
current figure generation if full-cohort result exists
E8 claim audit
```

Latest verified run:

```text
2026-09-03 23:38 local time: reproduce-paper6.ps1 completed E1 cache checks, E2 cache checks, E3 smoke, default E3-E6, full ds004117 batch aggregation, E7 ds004752 external convergent analysis, figure generation, and E8 claim audit without command failure.
```

Current reproduction scripts:

```text
paper6/scripts/audit_p6_electrophysiology_datasets.py
paper6/scripts/audit_p6_event_semantics.py
paper6/scripts/build_p6_ds004117_transition_windows.py
paper6/scripts/run_p6_e3_ds004117_signal_smoke.py
paper6/scripts/run_p6_e3_e6_ds004117_multi_run.py
paper6/scripts/aggregate_p6_e3_e6_ds004117_batches.py
paper6/scripts/make_p6_figures.py
paper6/scripts/write_p6_final_claim_audit.py
paper6/scripts/run_p6_e7_ds004752_external_convergent.py
paper6/scripts/reproduce-paper6.ps1
```

Full available ds004117 output:

```text
paper6/results/e3_e6_ds004117_full_cohort_batched_results.json
paper6/features/ds004117_multi_run/ds004117_batch01_bandpower_delta_features.csv
paper6/features/ds004117_multi_run/ds004117_batch02_bandpower_delta_features.csv
paper6/features/ds004117_multi_run/ds004117_batch03_bandpower_delta_features.csv
paper6/features/ds004117_multi_run/ds004117_batch04_bandpower_delta_features.csv
paper6/features/ds004117_multi_run/ds004117_batch05_bandpower_delta_features.csv
paper6/features/ds004117_multi_run/ds004117_batch06_bandpower_delta_features.csv
```

External convergent E7 output:

```text
paper6/results/e7_ds004752_external_convergent_results.json
paper6/features/ds004752_external/ds004752_lcmv_encoding_maintenance_bandpower_features.csv
```

Current generated figures:

```text
paper6/figures/figure1_pipeline.png
paper6/figures/figure2_window_inventory.png
paper6/figures/figure3_e4_reproducibility.png
paper6/figures/figure4_e5_e6_specificity_nulls.png
paper6/figures/figure5_subject_accuracy.png
paper6/figures/figure6_claim_audit.png
paper6/figures/figure7_e7_external_convergent.png
```

Manual full-cohort batch extraction commands used:

```powershell
python paper6/scripts/run_p6_e3_e6_ds004117_multi_run.py --max-runs 0 --subjects sub-001 sub-002 sub-003 sub-004 --analysis-label batch01 --n-perm 20
python paper6/scripts/run_p6_e3_e6_ds004117_multi_run.py --max-runs 0 --subjects sub-005 sub-006 sub-007 sub-008 --analysis-label batch02 --n-perm 20
python paper6/scripts/run_p6_e3_e6_ds004117_multi_run.py --max-runs 0 --subjects sub-009 sub-010 sub-011 sub-012 --analysis-label batch03 --n-perm 20
python paper6/scripts/run_p6_e3_e6_ds004117_multi_run.py --max-runs 0 --subjects sub-014 sub-015 sub-016 sub-017 --analysis-label batch04 --n-perm 20
python paper6/scripts/run_p6_e3_e6_ds004117_multi_run.py --max-runs 0 --subjects sub-018 sub-019 sub-020 sub-021 --analysis-label batch05 --n-perm 20
python paper6/scripts/run_p6_e3_e6_ds004117_multi_run.py --max-runs 0 --subjects sub-022 sub-023 sub-024 --analysis-label batch06 --n-perm 20
python paper6/scripts/aggregate_p6_e3_e6_ds004117_batches.py --label-prefix batch --analysis-label full_cohort_batched --n-perm 200
```

Future full scope will add:

```text
direct external transition-boundary replication
genuinely phase-sensitive feature/null family
submission-ready manuscript package
```
