# A2 Dataset Manifest

Status: audited for datasets A/B/C used in the current Paper 2 run.

## Dataset A - ds001635

Role: source domain / Paper 1 development dataset.

Known from Paper 1:

```text
OpenNeuro ds001635
DOI: 10.18112/openneuro.ds001635.v1.0.1
License: CC-BY 4.0
48 events files
48 BOLD files
16 subjects x 3 runs
2,291 extracted ENCODE/MAINTAIN/PROBE states
1,523 extracted transitions
```

## Dataset B - ds001634

Role: failure-analysis dataset.

Known from Paper 1:

```text
OpenNeuro ds001634
DOI: 10.18112/openneuro.ds001634.v1.0.1
License: CC-BY 4.0
57 events files
57 BOLD files
3,066 extracted ENCODE/MAINTAIN/PROBE states
2,040 extracted transitions
```

Important:

```text
Dataset B is no longer a final independent holdout.
```

## Dataset C - Final External Holdout

Identifier:

```text
OpenNeuro ds004469 v1.1.3
Dataset DOI: doi:10.18112/openneuro.ds004469.v1.1.3
Dataset name: Temporal Lobe Epilepsy - UNAM
License: CC0
```

Current metadata audit:

```text
metadata-only OpenNeuro download completed
participants.tsv rows: 74
task_fmri_vw included subjects: 62
Sternberg events files: 63
Sternberg BOLD sidecar JSON files: 63
event columns: onset, duration, trial_type
observed trial types: Coding, Retention, Test
Coding events: 756, duration 4.0 s
Retention events: 756, duration 10.0 s
Test events: 756, duration 4.0 s
```

Final input and state extraction:

```text
task-sternberg BOLD NIfTI downloaded after Dataset C lock
standardized events: paper2/external_holdout/ds004469_standardized_events
stage states: paper2/external_holdout/stage_states_dataset_c.csv
states extracted: 2,268
transitions evaluated: 1,512
subjects with transitions: 63
ROI features: 216
```

Frozen stage mapping:

```text
Coding -> ENCODE
Retention -> MAINTAIN
Test -> PROBE
```

Scope boundary:

```text
Dataset C can test ENCODE/MAINTAIN/PROBE transfer.
Dataset C cannot test TRANSFORM because the audited task has no manipulation phase.
```
