# Paper 8 Current Results

Status:

```text
P8_E1_E6_HCP_PHYSIO_SMOKE_RAW_GATE_FAILED
```

Paper 8 asks whether P3/P4 reproducible macro transitions survive real measured motion, respiration, cardiac/pulse, tissue, and timing nuisance controls.

Current implementation and run:

```text
E0 public dataset and measured-physiology availability audit
E1 HCP WM Physio_log download
E1-E6 HCP WM measured-physiology nuisance ladder smoke
P8-v2 signal-separation audit
P8-final ds005795 all-manifest-available learning-subject streaming nuisance ladder
E8 claim audit
```

Current claim:

```text
Paper 8 found HCP WM measured physiology files and ran an 18-subject / 36-run measured-physiology ladder smoke, but the preregistered raw SameTransition > DifferentTransition gate was not reproduced. No physiological-survival claim is allowed.
```

Data actually used:

```text
HCP-YA WM: 18 subjects, 2 WM runs per subject, 36 runs, 288 block-start transition rows.
Downloaded or confirmed present: 36 HCP WM Physio_log files.
State representation: aparc68 cortical parcel block-start transition vectors.
```

Primary transition-reproducibility gate:

```text
Gate A = SameTransition similarity > DifferentTransition similarity at N0 raw.
Observed N0 contrast = -0.033148.
Subject-level mean contrast = -0.073271.
Bootstrap 95% CI = [-0.161751, 0.018574].
Subject sign-flip p = 0.934607.
Gate A = FAILED.
```

Nuisance ladder summary:

| Rung | Controls | Same-Different Contrast | LORO Accuracy | Subject p |
|---|---|---:|---:|---:|
| N0_raw_basic | none | -0.033148 | 0.715278 | 0.934607 |
| N1_motion | motion | -0.015995 | 0.753472 | 0.942706 |
| N2_respiration | respiration | -0.040132 | 0.732639 | 0.982002 |
| N3_cardiac_pulse | cardiac/pulse | -0.037937 | 0.729167 | 0.949205 |
| N4_motion_respiration_cardiac | motion + respiration + cardiac/pulse | -0.018814 | 0.756944 | 0.829317 |

Interpretation:

```text
There is above-chance 0-back vs 2-back block-start classification signal, but the preregistered same-transition reproducibility contrast is negative at every rung. The classification result is secondary and cannot rescue the primary gate.
```

Claim boundary:

```text
P8 is a constrained negative measured-physiology falsification result with a completed ds005795 convergent measured-physiology extension. It is not a positive physiological-survival validation paper.
```

P8-v2 signal-separation audit:

```text
Purpose: separate the failed same-transition reproducibility endpoint from the secondary 0/2-back condition-classification signal.
Permutation count: 100 per rung.
Rungs tested: N0_raw_basic and N4_motion_respiration_cardiac.
```

P8-v2 key result:

| Rung | True Contrast | Contrast vs Label-Shuffle p | ROI Classifier Accuracy | Label-Shuffle Accuracy Mean | Metadata-Only Accuracy |
|---|---:|---:|---:|---:|---:|
| N0_raw_basic | -0.033148 | 0.881188 | 0.715278 | 0.494028 | 0.625000 |
| N4_combined | -0.018814 | 0.405941 | 0.756944 | 0.488646 | 0.625000 |

Interpretation:

```text
The secondary condition-classification signal exceeds simple label-shuffle nulls, but the primary transition-reproducibility endpoint remains unsupported. Classification cannot rescue the failed primary gate.
```

## ds005795 Measured-Physiology Streaming Extension

Role:

```text
Convergent measured-physiology nuisance-ladder validation, not direct Encode/Maintain/Probe replication and not a rescue of the HCP primary gate.
```

Manifest boundary:

```text
The ds005795 manifest contains complete task-learning BOLD/physio/events/bold-json files for sub-01 through sub-05. Requested sub-06 through sub-10 do not have the required task-learning four-file bundle in the audited manifest. The final streaming analysis therefore freezes at 5/5 available learning subjects.
```

Streaming result:

```text
Status = PASS_DS005795_STREAMING_NUISANCE_LADDER
Subjects = sub-01, sub-02, sub-03, sub-04, sub-05
Each BOLD file was downloaded, processed, and deleted after subject-level feature extraction/modeling.
State endpoint = global BOLD signal transition prediction.
```

Aggregate results:

| Model | Mean MSE | Mean R2 | Subjects |
|---|---:|---:|---:|
| N0 state only | 308.008097 | 0.480632 | 5 |
| N1 state + cardiac/respiration | 288.628925 | 0.516281 | 5 |
| N2 state + metadata | 304.121571 | 0.485793 | 5 |
| N3 state + physiology + metadata | 286.173932 | 0.519003 | 5 |

Delta relative to state-only:

| Model | Delta MSE vs N0 | Delta R2 vs N0 |
|---|---:|---:|
| N1 state + cardiac/respiration | 19.379172 | 0.035649 |
| N2 state + metadata | 3.886527 | 0.005161 |
| N3 state + physiology + metadata | 21.834165 | 0.038371 |

Interpretation:

```text
Measured physiology carries predictive information for global BOLD signal dynamics in ds005795. This is a convergent nuisance-modeling result only. It does not show that HCP WM transition reproducibility survives measured physiology, because the HCP preregistered raw SameTransition > DifferentTransition gate already failed.
```
