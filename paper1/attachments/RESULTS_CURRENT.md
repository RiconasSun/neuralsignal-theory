# Current Results

Date: 2026-09-01

## Execution Status

Real OpenNeuro data were downloaded and processed for:

- ds001635 primary dataset
- ds001634 external validation dataset

The E0-E8 chain has run through E8.

## Data and State Extraction

E0 ds001635 audit:

```text
status: PASS
n_events: 48
n_bold: 48
n_roi_timeseries: 48
n_confounds: 0
external_stage_states_present: true
```

E1 primary ds001635:

```text
states_extracted: 2291
roi_count: 216
hrf_lag: 4.0
baseline_seconds: 4.0
```

E1 external ds001634:

```text
states_extracted: 3066
roi_count: 216
hrf_lag: 4.0
baseline_seconds: 4.0
```

Atlas note:

```text
Native image-space 216-ROI grid; not a neuroanatomical atlas claim.
```

## E2 CWP Existence Sanity Check

Subject-held-out stage decoding:

```text
accuracy: 0.3356612832824094
macro_f1: 0.3153017767921555
label_counts: ENCODE 768, MAINTAIN 768, PROBE 755
```

Interpretation:

```text
This raw native-grid pipeline does not reproduce a strong ENCODE/MAINTAIN/PROBE stage-separability sanity check.
```

## E3 Task vs CWP

Mean MSE:

```text
M0_state: 739.9842107977023
M1_flat_task: 651.1084620470139
M2_strong_task: 651.1084916855937
M3_cwp: 673.3670453189366
M4_task_plus_cwp: 651.1084167356842
```

Gate A:

```text
INCONCLUSIVE
```

## E4 Unseen Combination

Mean MSE:

```text
M2_strong_task: 1.2930225316211859
M3_cwp: 1.1905904151828643
M4_task_plus_cwp: 1.2001512696937149
```

Gate component:

```text
PASSED
```

## E5 Unseen Domain

Mean MSE:

```text
M2_strong_task: 1.549553729346369
M3_cwp: 1.5035537034522544
M4_task_plus_cwp: 1.5084872262939564
```

Gate component:

```text
PASSED
```

## E6 Null/Falsification

```text
true_cwp_mse: 1.1905904151828643
pseudo_cwp_survival_percentile: 1.0
required_survival_percentile: 0.99
```

Blocked nulls:

```text
motion_only_model
boundary_jitter
```

## E7 External Validation

Mean MSE:

```text
M0_state: 528.9595753463202
M1_flat_task: 529.0050987946481
M2_strong_task: 529.0031639473207
M3_cwp: 532.1089214151368
M4_task_plus_cwp: 528.9681855141137
```

Gate C:

```text
FAILED
```

## E8 Claim Audit

```text
Gate A incremental: INCONCLUSIVE
Gate B OOD: PASSED
Gate C external: FAILED
claim_allowed_cwp_foundation_holds: false
claim_allowed_cwp_clearly_outperforms_task_labels: false
```

## Final Current Conclusion

The strong Paper 1 claim is not supported by the current run.

Paper 1 should be repositioned as:

```text
CWP-style compositional representations improve within-dataset out-of-distribution brain-state prediction, but do not yet generalize across independent datasets.
```

Supported narrower finding:

```text
Within ds001635, CWP-style compositional labels improved OOD prediction in leave-one-combination and unseen-domain tests.
```

Unsupported:

```text
CWP clearly outperforms task labels overall.
CWP passes the primary incremental gate.
CWP externally replicates on ds001634.
CWP foundation paper holds as a strong positive result.
```
