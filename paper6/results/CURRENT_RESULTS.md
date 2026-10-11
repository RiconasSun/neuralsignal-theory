# Paper 6 Current Results

Status:

```text
P6_E0_E7_FULL_DS004117_EXTERNAL_CONVERGENT_COMPLETE
```

Paper 6 is an Explanation Paper. It asks whether reproducible macroscopic brain-state transitions contain reproducible subsecond electrophysiological structure. The implementation now includes a frozen protocol, public electrophysiology dataset audit, event-semantics audit, ds004117 transition-window manifest, one-run EEG signal extraction smoke, and full available ds004117 E3-E6 analysis assembled from batched subject-level extraction.

This is a positive within-dataset result for transition-aligned EEG bandpower-delta structure. E7 also now includes an external ds004752 derivative-level convergent test of encoding-vs-maintenance stage specificity. The E7 result is not a direct cross-dataset transition-boundary replication, not a NAP validation claim, and not a completed P6 mechanistic claim.

## Program State

```text
Dynamics survived; ontology and structural mechanism remain unproven.
```

Paper 6 directly tests fast neural-dynamics signatures under macro transitions, without assuming that NAPs already exist.

## E1 Dataset Audit

E1 passed for three public candidate datasets.

| Dataset | Role | Modality | Participants | E1 status |
| --- | --- | --- | ---: | --- |
| ds004752 | primary mechanistic candidate | iEEG + scalp EEG + beamforming | 15 | PASS_INITIAL_E1 |
| ds002550 / on002550 | external MEG candidate | MEG | 22 | PASS_INITIAL_E1 |
| ds004117 | first executable dataset | EEG | 23 | PASS_INITIAL_E1 |

Evidence:

```text
paper6/results/e1_dataset_audit.json
paper6/results/e1_dataset_audit.csv
```

## E2 Event-Semantics Audit

E2 found that `ds004117` is the cleanest first dataset because its events expose transition-relevant task roles.

| Dataset | E2 status | Interpretation |
| --- | --- | --- |
| ds004117 | PASS_E2_INITIAL_TRANSITION_AUDIT | First executable P6 dataset |
| ds004752 | PARTIAL_EVENTS_NEED_MANUAL_STAGE_MAPPING | High-value iEEG candidate, but stage windows are not explicit in initial event preview |
| ds002550 / on002550 | PARTIAL_EVENTS_NEED_MANUAL_STAGE_MAPPING | MEG candidate, but maintenance windows must be sequence-derived |

`ds004117` event files include:

```text
onset
duration
sample
event_type
task_role
letter
trial
memory_cond
value
```

Observed task roles include:

```text
to_remember
to_ignore
work_memory
probe_target
fixate
feedback_correct
feedback_incorrect
```

This supports the first P6 transition-window plan:

```text
Letter presentation / encoding -> work_memory maintenance
work_memory maintenance -> probe target
```

Evidence:

```text
paper6/results/e2_event_semantics_audit.json
paper6/results/e2_event_semantics_audit.csv
paper6/results/e2_ds004117_transition_windows.json
paper6/results/e2_ds004117_transition_windows.csv
```

## E2 Transition Window Manifest

The first executable transition-window manifest has been generated for `ds004117`.

```text
event files processed: 85
subjects with windows: 23
total transition windows: 4190
encoding_to_maintenance windows: 2095
maintenance_to_probe windows: 2095
window size: 1.0 s before and 1.0 s after transition boundary
file errors: 0
```

## E3 Signal Extraction Smoke

E3 signal extraction passed for one public ds004117 EEG run.

```text
dataset: ds004117
subject/run: sub-001 ses-01 run-1
signal files downloaded: events.tsv, eeg.set, eeg.fdt, eeg.json, channels.tsv
sampling rate: 250 Hz
channels: 69
duration: 652.952 s
transition windows requested: 50
transition windows extracted: 50
windows skipped: 0
feature family: 1-second pre/post transition log bandpower deltas
```

Evidence:

```text
paper6/results/e3_ds004117_signal_smoke.json
paper6/features/ds004117_signal_smoke/sub-001_run-1_bandpower_transition_smoke.csv
```

## E3-E6 Full Available ds004117 Cohort

The requested expansion from one-run smoke to multi-subject/run E3-E6 was completed across the full available ds004117 event-file cohort. :codex-annotation{index="1"}

Scope:

```text
dataset: ds004117
subjects: 23
runs/event files: 85
transition windows: 4190
duration-matched random windows: 3386
phase-randomized transition windows: 4190
time-shift transition windows: 4131
feature columns: 276
feature family: per-channel 1-second pre/post transition log bandpower deltas
bands: theta, alpha, beta, low gamma
```

E4 same-transition reproducibility:

```text
same-transition odd/even centroid similarity: 0.994146078824997
random-window odd/even centroid similarity: -0.029297083616256714
delta similarity: 1.0234431624412537
```

E5 transition specificity:

```text
leave-one-run-out transition classification accuracy: 0.6806682577565633
folds: 85
predictions: 4190
```

Subject-level inference:

```text
subject mean accuracy: 0.7116372328567145
subject bootstrap 95% CI: [0.6779915892328661, 0.7447466470064257]
subjects above chance: 23 / 23
binomial p for subjects above chance: 1.1920928955078125e-07
```

E6 null/falsification:

```text
label-shuffle null mean accuracy: 0.5009307875894987
label-shuffle null 95% CI: [0.48591885441527444, 0.5164677804295943]
one-sided permutation p: 0.004975124378109453
random-window specificity accuracy: 0.5053160070880095
time-shift specificity accuracy: 0.5100459937061245
phase-randomized bandpower specificity accuracy: 0.7047732696897375
```

Full-cohort gates:

```text
E4 real same-transition similarity > random-window similarity: PASS
E5 specificity accuracy > label-shuffle 95% CI upper bound: PASS
E6 specificity accuracy > random-window specificity: PASS
E6 specificity accuracy > time-shift specificity: PASS
```

Evidence:

```text
paper6/results/e3_e6_ds004117_full_cohort_batched_results.json
paper6/features/ds004117_multi_run/ds004117_batch01_bandpower_delta_features.csv
paper6/features/ds004117_multi_run/ds004117_batch02_bandpower_delta_features.csv
paper6/features/ds004117_multi_run/ds004117_batch03_bandpower_delta_features.csv
paper6/features/ds004117_multi_run/ds004117_batch04_bandpower_delta_features.csv
paper6/features/ds004117_multi_run/ds004117_batch05_bandpower_delta_features.csv
paper6/features/ds004117_multi_run/ds004117_batch06_bandpower_delta_features.csv
```

Interpretation:

```text
Full available ds004117 EEG analysis supports transition-aligned bandpower-delta structure and transition specificity within this dataset. Because phase-randomized bandpower controls remain high, the current result should be interpreted as amplitude/bandpower-family evidence, not phase-specific dynamics. It does not validate NAPs and does not establish cross-dataset reproducibility.
```

## E7 External Convergent Test

E7 was implemented on public ds004752 LCMV source derivatives. Because ds004752 event files expose trial-level windows while the derivative MAT files expose separated `LCMV_encoding` and `LCMV_maintenance` trials, this is an external convergent stage-specificity test rather than a direct transition-boundary replication.

Scope:

```text
dataset: ds004752
subjects: 15
trials: 3448
encoding trials: 1724
maintenance trials: 1724
feature columns: 104
feature family: per-virtual-sensor log bandpower features from LCMV_encoding and LCMV_maintenance trials
holdout: leave-one-subject-out
```

E7 result:

```text
leave-one-subject-out accuracy: 0.6276102088167054
subject mean accuracy: 0.6288650530091637
subject bootstrap 95% CI: [0.5773691737749553, 0.6830378459547412]
label-shuffle null mean accuracy: 0.49868184454756376
label-shuffle null 95% CI: [0.47998839907192575, 0.5183077146171694]
one-sided permutation p: 0.004975124378109453
```

Interpretation:

```text
ds004752 provides external convergent evidence that encoding and maintenance stages carry separable electrophysiological bandpower structure. This supports the broad fast-dynamics direction but does not replicate the ds004117 transition-boundary result.
```

Evidence:

```text
paper6/results/e7_ds004752_external_convergent_results.json
paper6/features/ds004752_external/ds004752_lcmv_encoding_maintenance_bandpower_features.csv
```

## Claim Audit

Allowed current claim:

```text
P6 has a frozen protocol, public dataset/event-semantics audit, ds004117 transition-window manifest, one-run real EEG signal extraction smoke, full available ds004117 E3-E6 positive within-dataset result, and ds004752 external convergent encoding-vs-maintenance evidence. No direct cross-dataset transition-boundary replication has been run.
```

Forbidden current claims:

```text
NAP is validated.
CWP maps to NAP.
Macro transitions are mechanistically explained.
Fast neural dynamics are universal primitives.
P6 is complete.
```

## Next Implementation Step

Scale P6 beyond the positive within-dataset ds004117 result:

```text
run direct external transition-boundary replication
add genuinely phase-sensitive feature/null families
add held-out subject split if needed
produce submission-ready manuscript package
```
