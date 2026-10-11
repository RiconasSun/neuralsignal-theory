# Paper 8 Final Current Conclusion

Status:

```text
P8_E1_E6_HCP_PHYSIO_SMOKE_RAW_GATE_FAILED
```

Paper 8 asked whether previously observed macroscopic transition structure survives measured nuisance controls using real motion, respiration, and cardiac/pulse recordings.

The current executable package found and used HCP-YA WM measured physiology files:

```text
18 subjects
36 WM runs
36 downloaded or existing Physio_log files
288 block-start transition rows
aparc68 cortical transition vectors
```

The primary preregistered smoke gate was:

```text
SameTransition similarity > DifferentTransition similarity
```

That gate failed at the raw/basic rung:

```text
SameTransition similarity = 0.926106
DifferentTransition similarity = 0.959254
Same-Different contrast = -0.033148
Subject mean contrast = -0.073271
Bootstrap 95% CI = [-0.161751, 0.018574]
Subject sign-flip p = 0.934607
```

The measured-nuisance ladder did not rescue the gate:

| Rung | Same-Different Contrast | Leave-One-Run-Out Accuracy | Subject p |
|---|---:|---:|---:|
| N0_raw_basic | -0.033148 | 0.715278 | 0.934607 |
| N1_motion | -0.015995 | 0.753472 | 0.942706 |
| N2_respiration | -0.040132 | 0.732639 | 0.982002 |
| N3_cardiac_pulse | -0.037937 | 0.729167 | 0.949205 |
| N4_motion_respiration_cardiac | -0.018814 | 0.756944 | 0.829317 |

Allowed current conclusion:

```text
HCP measured physiology can be acquired and inserted into the Paper 8 nuisance ladder, but the preregistered raw transition-reproducibility contrast was not reproduced in the current 18-subject smoke test.
```

Important secondary observation:

```text
0-back vs 2-back block-start classification was above chance across rungs, but this is a diagnostic condition-label signal, not the preregistered same-transition reproducibility endpoint.
```

P8-v2 signal-separation result:

```text
N0 ROI classification accuracy = 0.715278; label-shuffle mean = 0.494028; p = 0.009901.
N4 ROI classification accuracy = 0.756944; label-shuffle mean = 0.488646; p = 0.009901.
N0 primary contrast p vs label shuffle = 0.881188.
N4 primary contrast p vs label shuffle = 0.405941.
```

Interpretation:

```text
Condition classification signal is present, but it does not rescue the failed same-transition reproducibility endpoint.
```

Measured-physiology extension:

```text
P8 also ran a ds005795 streaming nuisance-ladder extension over every task-learning subject with a complete audited BOLD/physio/events/bold-json bundle: sub-01 through sub-05.
```

The ds005795 extension was deliberately treated as convergent validation rather than direct replication:

```text
It uses a different task design and a global BOLD signal transition endpoint. It cannot rescue or reverse the failed HCP WM SameTransition > DifferentTransition gate.
```

Streaming ds005795 aggregate result:

| Model | Mean MSE | Mean R2 | Subjects |
|---|---:|---:|---:|
| N0 state only | 308.008097 | 0.480632 | 5 |
| N1 state + cardiac/respiration | 288.628925 | 0.516281 | 5 |
| N2 state + metadata | 304.121571 | 0.485793 | 5 |
| N3 state + physiology + metadata | 286.173932 | 0.519003 | 5 |

Allowed ds005795 conclusion:

```text
Measured physiology improves global-signal prediction in the ds005795 convergent extension, but this establishes nuisance relevance rather than physiology-robust CWP/NAP transition reproducibility.
```

Forbidden claims:

```text
physiology eliminated
motion fully excluded
neural origin proven
CWP validated
NAP validated
P8 ds005795 extension directly replicates HCP working-memory transitions
```

Final boundary:

```text
Do not tune the current analysis to rescue the failed gate. Paper 8 closes as a constrained negative primary-gate result with a convergent measured-physiology extension showing that physiological regressors matter for global BOLD prediction.
```
