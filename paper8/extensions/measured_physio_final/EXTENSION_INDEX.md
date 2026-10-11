# Paper 8 Measured-Physiology Final Extension Index

Status:

```text
P8_FINAL_EXTENSION_THREE_SUBJECT_INTERFACE_SMOKE_READY_NOT_FINAL
```

## What Is Frozen

The prior Paper 8 v2 result is preserved:

```text
PRIMARY TRANSITION FAILED
METADATA CONFOUND IDENTIFIED
```

This extension is a new measured-physiology study. It does not revise, rescue,
or overwrite that result.

## Dataset Candidate

```text
OpenNeuro ds005795 / NEMAR on005795 / MULTI-CLARID
```

Role:

```text
convergent measured-physiology validation
```

Not allowed:

```text
direct HCP working-memory Encode/Maintain/Probe replication
```

## Generated Audit Artifacts

```text
paper8/extensions/measured_physio_final/P8_FINAL_EXTENSION_PROTOCOL_v0_1.md
paper8/results/p8_final_extension_ds005795_manifest_audit.json
paper8/results/p8_final_extension_ds005795_smoke_download.json
paper8/results/p8_final_extension_ds005795_physio_parse_smoke.json
paper8/results/p8_final_extension_ds005795_physio_feature_smoke.json
paper8/results/p8_final_extension_ds005795_nuisance_ladder_smoke.json
paper8/dataset_audit/p8_final_extension_ds005795_selected_files.csv
paper8/state_extraction/ds005795_physio_extension/p8_ds005795_sub01_learning_physio_tr_features.csv
paper8/state_extraction/ds005795_physio_extension/p8_ds005795_sub02_learning_physio_tr_features.csv
paper8/state_extraction/ds005795_physio_extension/p8_ds005795_sub03_learning_physio_tr_features.csv
```

## Current Audit Result

```text
status = PASS_DS005795_MULTI_SUBJECT_NUISANCE_LADDER_INTERFACE_SMOKE
subjects = 34
tasks = learning, rest
total files = 670
bold files = 80
physio files = 72
eeg files = 302
events files = 78
channels files = 39
smoke subjects = sub-01, sub-02, sub-03
smoke task = learning
smoke BOLD shape = 112 x 112 x 58 x 816
TR-aligned transition rows = 815
physio columns = time, cardiac, respiratory
physio sampling frequency = 496 Hz
mean MSE, state only = 258.3504
mean MSE, state + cardiac/resp = 235.0614
mean MSE, state + metadata = 254.9492
mean MSE, state + physiology + metadata = 234.1164
mean R2, state only = 0.4623
mean R2, state + physiology + metadata = 0.5112
```

The NEMAR direct manifest path returned HTTP 403, but the OpenNeuro GraphQL
fallback returned the file tree.

## Next Required Step

Expand from the three-subject global-signal interface smoke to a locked
multi-subject cohort and run the full nuisance ladder:

```text
Raw
-> Motion
-> Respiration
-> Cardiac / pulse / ECG
-> WM / CSF
-> RETROICOR-style Fourier terms
-> HR / RVT
-> matched timing / metadata controls
```

Metadata-only remains a formal baseline.

## Claim Boundary

No measured-physiology robustness claim is allowed until the nuisance ladder is
run across the locked cohort with planned null and metadata controls.
