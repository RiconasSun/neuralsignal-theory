# Do Reproducible Macroscopic Brain-State Transitions Contain Reproducible Subsecond Neural Dynamics?

Authors: [TO BE FILLED]  
Affiliations: [TO BE FILLED]  
Correspondence: [TO BE FILLED]

## Abstract

Paper 6 tests whether reproducible macroscopic brain-state transitions contain reproducible subsecond electrophysiological dynamics. The study begins from the current program state: macroscopic dynamics survived earlier tests, but cognitive ontology and structural grounding remain unproven. We therefore do not assume that neural activity patterns exist as discrete NAPs. Instead, we test whether transition-aligned EEG/MEG/iEEG windows contain fast neural structure that is reproducible, transition-specific, and stronger than matched null explanations. The current implementation has completed E0 protocol freeze, E1 public dataset audit, E2 event-semantics audit, a ds004117 transition-window manifest, one-run E3 EEG signal extraction smoke, full available ds004117 E3-E6 analysis across 23 subjects, 85 runs/event files, and 4190 transition windows, plus an E7 external convergent ds004752 analysis across 15 subjects and 3448 LCMV derivative trials. In ds004117, same-transition odd/even centroid similarity exceeded matched random-window similarity, and leave-one-run-out transition specificity reached 0.6807 accuracy versus a label-shuffle null mean of 0.5009. Subject-level mean accuracy was 0.7116 with bootstrap 95% CI [0.6780, 0.7447], and 23/23 subjects were above chance. Random-window and time-shift controls were near chance, but phase-randomized bandpower controls remained high. In ds004752, leave-one-subject-out encoding-vs-maintenance stage specificity reached 0.6276 accuracy versus a label-shuffle null mean of 0.4987. These results support within-dataset transition-aligned bandpower-delta structure in ds004117 and external convergent stage-specific electrophysiological structure in ds004752. They do not establish phase-specific neural dynamics, direct cross-dataset transition-boundary replication, or NAP validation.

## 1. Introduction

### 1.1 Phenomenon

Papers 3 and 4 suggest that macroscopic brain-state transitions can be reproducible and partially survive falsification. Paper 5 did not support a subject-specific structural-proxy explanation. The remaining question is whether these macroscopic transitions have subsecond electrophysiological structure beneath them.

### 1.2 Scientific Gap

The current evidence supports transition dynamics more strongly than it supports either CWP ontology or structural mechanism. Paper 6 therefore asks whether fast neural dynamics provide a better mechanistic grounding.

### 1.3 Proposed Explanation

The cautious proposed explanation is:

```text
Macro transitions may correspond to reproducible fast neural-dynamics signatures.
```

This is not yet a claim that NAPs exist.

### 1.4 Falsifiable Hypotheses

H1 Existence:

```text
Same-transition fast dynamics are more similar than duration-matched random windows.
```

H2 Specificity:

```text
Different macro transitions have distinguishable fast-dynamics signatures.
```

H3 Generalization:

```text
The direction of the effect survives subject/session holdout and at least one external dataset.
```

## 2. Methods

### 2.1 Dataset Audit

The E1 audit inspected three public candidate datasets:

| Dataset | Modality | Participants | Initial status |
| --- | --- | ---: | --- |
| ds004752 | iEEG + scalp EEG + beamforming | 15 | PASS_INITIAL_E1 |
| ds002550 / on002550 | MEG | 22 | PASS_INITIAL_E1 |
| ds004117 | EEG | 23 | PASS_INITIAL_E1 |

### 2.2 Event-Semantics Audit

The E2 audit found:

| Dataset | E2 status | Use |
| --- | --- | --- |
| ds004117 | PASS_E2_INITIAL_TRANSITION_AUDIT | first executable dataset |
| ds004752 | PARTIAL_EVENTS_NEED_MANUAL_STAGE_MAPPING | later iEEG extension |
| ds002550 / on002550 | PARTIAL_EVENTS_NEED_MANUAL_STAGE_MAPPING | later MEG extension |

`ds004117` contains event columns:

```text
onset, duration, sample, event_type, task_role, letter, trial, memory_cond, value
```

and task roles that support transition-window construction:

```text
to_remember, to_ignore, work_memory, probe_target
```

### 2.3 Transition Windows

Primary:

```text
encoding / presentation -> work_memory maintenance
```

Secondary:

```text
work_memory maintenance -> probe target
```

The ds004117 transition-window manifest contains:

```text
event files processed: 85
subjects with windows: 23
total transition windows: 4190
encoding_to_maintenance windows: 2095
maintenance_to_probe windows: 2095
window size: 1.0 s before and 1.0 s after transition boundary
```

### 2.4 Fast-Dynamics Features

The current implemented feature family is:

```text
per-channel 1-second pre/post transition log bandpower deltas
```

Bands:

```text
theta
alpha
beta
low gamma
```

Planned but not yet implemented feature families include phase consistency, phase-amplitude coupling where sampling rate permits, channel-space population trajectory, transition sharpness, and state-space distance.

### 2.5 Nulls and Competing Explanations

Implemented:

```text
transition-label shuffle
duration-matched random windows
random-window specificity baseline
time-shift specificity baseline
phase-randomized bandpower control
```

Not yet implemented:

```text
event-timing-only baseline
electrode/channel identity baseline
external-dataset null replication
genuinely phase-sensitive null family
```

## 3. Results

E0-E6 implementation has been run through the full available ds004117 cohort.

```text
E0: protocol frozen
E1: public dataset audit passed for three candidates
E2: ds004117 selected as first executable dataset
E2 transition windows: 4190 windows across 23 subjects and 85 event files
E3 signal smoke: sub-001 run-1, 69 EEG channels, 250 Hz, 50/50 windows extracted
E3-E6 full available ds004117: 23 subjects, 85 runs/event files, 4190 transition windows
```

### 3.1 Same-Transition Reproducibility

The full available ds004117 analysis found:

```text
same-transition odd/even centroid similarity: 0.994146078824997
random-window odd/even centroid similarity: -0.029297083616256714
delta similarity: 1.0234431624412537
```

### 3.2 Transition Specificity

Leave-one-run-out transition specificity was:

```text
accuracy: 0.6806682577565633
folds: 85
predictions: 4190
```

Subject-level inference:

```text
subject mean accuracy: 0.7116372328567145
subject median accuracy: 0.7191780821917808
subject bootstrap 95% CI: [0.6779915892328661, 0.7447466470064257]
subjects above chance: 23 / 23
binomial p for subjects above chance: 1.1920928955078125e-07
```

### 3.3 Null and Falsification Results

The label-shuffle null was near chance:

```text
label-shuffle null mean accuracy: 0.5009307875894987
label-shuffle null 95% CI: [0.48591885441527444, 0.5164677804295943]
one-sided permutation p: 0.004975124378109453
```

Random-window and time-shift controls were also near chance:

```text
random-window specificity accuracy: 0.5053160070880095
time-shift specificity accuracy: 0.5100459937061245
```

The phase-randomized bandpower control remained high:

```text
phase-randomized bandpower specificity accuracy: 0.7047732696897375
```

This is a boundary condition. Phase randomization preserves Fourier amplitude spectra, and the current feature family is log bandpower delta. Therefore this result does not refute the bandpower-delta finding, but it prevents phase-specific interpretation.

### 3.4 Gate Results

```text
E4 real same-transition similarity > random-window similarity: PASS
E5 specificity accuracy > label-shuffle 95% CI upper bound: PASS
E6 specificity accuracy > random-window specificity: PASS
E6 specificity accuracy > time-shift specificity: PASS
```

### 3.5 External Convergent Test

E7 used public ds004752 LCMV source derivatives. The derivative MAT files contain separated `LCMV_encoding` and `LCMV_maintenance` trials. Because these are stage-specific derivative windows rather than event-derived transition-boundary windows, this analysis is an external convergent test rather than a direct replication of the ds004117 transition-boundary analysis.

```text
subjects: 15
trials: 3448
encoding trials: 1724
maintenance trials: 1724
feature columns: 104
leave-one-subject-out accuracy: 0.6276102088167054
subject mean accuracy: 0.6288650530091637
subject bootstrap 95% CI: [0.5773691737749553, 0.6830378459547412]
label-shuffle null mean accuracy: 0.49868184454756376
label-shuffle null 95% CI: [0.47998839907192575, 0.5183077146171694]
one-sided permutation p: 0.004975124378109453
```

### 3.6 Figure Inventory

Current generated figures:

```text
Figure 1: paper6/figures/figure1_pipeline.png
Figure 2: paper6/figures/figure2_window_inventory.png
Figure 3: paper6/figures/figure3_e4_reproducibility.png
Figure 4: paper6/figures/figure4_e5_e6_specificity_nulls.png
Figure 5: paper6/figures/figure5_subject_accuracy.png
Figure 6: paper6/figures/figure6_claim_audit.png
Figure 7: paper6/figures/figure7_e7_external_convergent.png
```

## 4. Discussion

The current Paper 6 result is stronger than the earlier one-run and 12-run smoke results. Across the full available ds004117 cohort, transition-aligned EEG bandpower-delta features are reproducible within transition class and distinguish encoding-to-maintenance from maintenance-to-probe transitions under leave-one-run-out evaluation. The result survives label-shuffle, random-window, and time-shift controls.

The ds004752 E7 result adds external convergent support that encoding and maintenance stages contain separable electrophysiological bandpower structure. The result remains deliberately claim-limited. It supports a within-dataset amplitude/bandpower-family signature aligned to macro transition boundaries in ds004117 and external convergent stage specificity in ds004752. It does not show that the signal is phase-specific. It does not establish direct cross-dataset transition-boundary replication or an externally reproducible NAP family. It does not prove that CWP maps onto NAP.

### 4.1 What the Evidence Supports

```text
Within ds004117, transition-aligned EEG bandpower-delta structure is reproducible and transition-specific.
In ds004752, encoding and maintenance LCMV derivative trials are separable above label-shuffle null under leave-one-subject-out evaluation.
```

### 4.2 What the Evidence Does Not Support

```text
NAP is validated.
CWP maps to NAP.
Fast neural dynamics are universal primitives.
Macro transitions are mechanistically explained.
P6 is complete.
```

### 4.3 Next Tests

The next decisive tests are:

```text
external dataset replication
genuinely phase-sensitive feature/null families
held-out subject split
direct external transition-boundary replication
event-timing-only baseline
electrode/channel identity confound audit
```

## 5. Conclusion

Paper 6 has progressed to a positive within-dataset ds004117 E3-E6 result and a positive ds004752 external convergent stage-specificity result. The current evidence supports transition-aligned EEG bandpower-delta reproducibility and specificity in ds004117, plus external encoding-vs-maintenance electrophysiological separability in ds004752. It does not validate NAPs, does not establish direct cross-dataset transition-boundary replication, and does not complete the mechanistic grounding claim.

## Data Availability

Publication supplement: [P6 data sources, sample manifests, access conditions, and figure provenance](../DATA_AVAILABILITY.md). Code, papers, and derived results are published at [neuralsignal-theory/test](https://github.com/RiconasSun/neuralsignal-theory/tree/test). Raw participant imaging/signals and tractography remain with the original data providers and are not redistributed. The supplement records dataset identifiers and versions available in existing evidence, links to cohort/pipeline records, and distinguishes unrecorded historical metadata from verified information. Exact local withheld filenames and SHA256 values are recorded in [the raw file inventory](../../publication/raw_file_inventory.csv); derived artifacts and figures have [SHA256 checksums](../../publication/artifact_checksums.csv).

All candidate datasets are public OpenNeuro/NEMAR datasets. No large data files are redistributed here.

## Code Availability

Current scripts:

```text
paper6/scripts/audit_p6_electrophysiology_datasets.py
paper6/scripts/audit_p6_event_semantics.py
paper6/scripts/build_p6_ds004117_transition_windows.py
paper6/scripts/run_p6_e3_ds004117_signal_smoke.py
paper6/scripts/run_p6_e3_e6_ds004117_multi_run.py
paper6/scripts/aggregate_p6_e3_e6_ds004117_batches.py
paper6/scripts/run_p6_e7_ds004752_external_convergent.py
paper6/scripts/make_p6_figures.py
paper6/scripts/reproduce-paper6.ps1
```

## Reproducibility Statement

Current reproduction:

```powershell
.\paper6\scripts\reproduce-paper6.ps1
```

The full available ds004117 result was produced by subject-batched feature extraction followed by aggregation. The exact batch commands are recorded in `paper6/attachments/A10_One_Command_Reproduction.md`.

## Ethics Statement

The current implementation audits public dataset metadata and event semantics, downloads public ds004117 EEG files, and runs within-dataset transition-window analysis. No participant-identifying data are redistributed. External replication analyses have not yet been run.

## Conflicts of Interest

[TO BE FILLED]
