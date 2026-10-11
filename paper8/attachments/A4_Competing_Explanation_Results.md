# A4. Competing Explanation Results

Status:

```text
MEASURED-PHYSIOLOGY LADDER SMOKE RUN
```

Executed nuisance rungs:

```text
N0_raw_basic
N1_motion
N2_respiration
N3_cardiac_pulse
N4_motion_respiration_cardiac
```

Primary result:

```text
The preregistered SameTransition > DifferentTransition contrast failed at N0 raw/basic and remained negative at every measured-nuisance rung.
```

Secondary diagnostic:

```text
Leave-one-run-out 0-back vs 2-back classification accuracy ranged from 0.715278 to 0.756944 across rungs. This is not the primary transition-reproducibility endpoint.
```

P8-v2 signal separation:

| Rung | ROI Accuracy | Label-Shuffle Mean | Domain-Preserving Shuffle Mean | Metadata-Only Accuracy |
|---|---:|---:|---:|---:|
| N0_raw_basic | 0.715278 | 0.494028 | 0.501458 | 0.625000 |
| N4_motion_respiration_cardiac | 0.756944 | 0.488646 | 0.497743 | 0.625000 |

Interpretation:

```text
The secondary classifier is above simple shuffle nulls, but this does not imply same-transition reproducibility or physiological robustness.
```

ds005795 measured-physiology extension:

```text
Status = PASS_DS005795_STREAMING_NUISANCE_LADDER
Scope = all complete manifest-available task-learning subjects: sub-01 through sub-05
Endpoint = global BOLD signal transition prediction
```

| Model | Mean MSE | Mean R2 | Subjects |
|---|---:|---:|---:|
| N0 state only | 308.008097 | 0.480632 | 5 |
| N1 state + cardiac/respiration | 288.628925 | 0.516281 | 5 |
| N2 state + metadata | 304.121571 | 0.485793 | 5 |
| N3 state + physiology + metadata | 286.173932 | 0.519003 | 5 |

Extension interpretation:

```text
Physiology regressors improve global BOLD signal prediction in ds005795, showing that measured physiology is a real competing explanatory signal. This does not rescue the failed HCP primary transition-reproducibility gate.
```
