# Paper 6 Package Index

Status:

```text
P6_E0_E7_FULL_DS004117_EXTERNAL_CONVERGENT_COMPLETE
```

Paper 6 is an Explanation Paper. It asks whether reproducible macroscopic brain-state transitions contain reproducible subsecond electrophysiological structure. The current package contains the frozen protocol, public dataset audit, event-semantics audit, ds004117 transition-window analysis, ds004752 external convergent analysis, generated figures, A1-A10 attachments, manuscript draft, and final claim audit.

## Current Scientific Conclusion

Supported:

```text
Within ds004117, transition-aligned EEG bandpower-delta features show reproducible and transition-specific structure across the full available cohort.
```

```text
In ds004752, encoding and maintenance stages show externally convergent electrophysiological bandpower separability.
```

Not supported:

```text
NAP is validated.
CWP maps to NAP.
Fast neural dynamics are universal primitives.
Direct cross-dataset transition-boundary replication has been established.
P6 mechanistic grounding is complete.
```

## Primary Results

ds004117 full available cohort:

```text
subjects: 23
runs/event files: 85
transition windows: 4190
leave-one-run-out transition accuracy: 0.6806682577565633
subject mean accuracy: 0.7116372328567145
subject bootstrap 95% CI: [0.6779915892328661, 0.7447466470064257]
label-shuffle null mean accuracy: 0.5009307875894987
label-shuffle null 95% CI: [0.48591885441527444, 0.5164677804295943]
random-window specificity accuracy: 0.5053160070880095
time-shift specificity accuracy: 0.5100459937061245
phase-randomized bandpower specificity accuracy: 0.7047732696897375
```

ds004752 external convergent stage specificity:

```text
subjects: 15
trials: 3448
leave-one-subject-out accuracy: 0.6276102088167054
subject mean accuracy: 0.6288650530091637
subject bootstrap 95% CI: [0.5773691737749553, 0.6830378459547412]
label-shuffle null mean accuracy: 0.49868184454756376
label-shuffle null 95% CI: [0.47998839907192575, 0.5183077146171694]
```

## Main Files

```text
paper6/manuscript/PAPER6_MANUSCRIPT_CURRENT.md
paper6/results/CURRENT_RESULTS.md
paper6/results/e3_e6_ds004117_full_cohort_batched_results.json
paper6/results/e7_ds004752_external_convergent_results.json
paper6/results/e8_claim_audit.json
```

## Attachments

```text
paper6/attachments/A1_Frozen_Protocol.md
paper6/attachments/A2_Dataset_Manifest.md
paper6/attachments/A3_Full_Pipeline.md
paper6/attachments/A4_Competing_Explanation_Results.md
paper6/attachments/A5_Holdout_Audit.md
paper6/attachments/A6_Statistics.md
paper6/attachments/A7_Null_Falsification_Tests.md
paper6/attachments/A8_QC_Leakage_Audit.md
paper6/attachments/A9_Limitations_Failed_Analyses.md
paper6/attachments/A10_One_Command_Reproduction.md
```

## Figures

```text
paper6/figures/figure1_pipeline.png
paper6/figures/figure2_window_inventory.png
paper6/figures/figure3_e4_reproducibility.png
paper6/figures/figure4_e5_e6_specificity_nulls.png
paper6/figures/figure5_subject_accuracy.png
paper6/figures/figure6_claim_audit.png
paper6/figures/figure7_e7_external_convergent.png
```

## Reproduction

Run:

```powershell
.\paper6\scripts\reproduce-paper6.ps1
```

Latest strict reproduction completed on 2026-09-03 23:38 local time and regenerated E7, all figures, and the final claim audit without command failure.

## Remaining High-Value Work

```text
direct external transition-boundary replication
phase-sensitive feature family with appropriate phase nulls
submission-ready PDF/Word manuscript with filled author, affiliation, ethics, data, code, funding, and conflict-of-interest fields
```
