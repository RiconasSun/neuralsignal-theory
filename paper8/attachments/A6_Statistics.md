# A6. Statistics

Primary statistical unit:

```text
subject
```

Planned:

```text
subject-level paired contrasts
bootstrap 95% CI
sign-flip/permutation
effect size
FDR for secondary nuisance ladders
```

Current result:

```text
RUN
```

Primary N0 subject-level result:

```text
n_subjects_with_contrast = 18
subject_mean_transition_contrast = -0.073271
bootstrap 95% CI = [-0.161751, 0.018574]
subject sign-flip p = 0.934607
```

Nuisance ladder:

| Rung | Contrast | Bootstrap 95% CI | Subject p |
|---|---:|---:|---:|
| N0_raw_basic | -0.033148 | [-0.161751, 0.018574] | 0.934607 |
| N1_motion | -0.015995 | [-0.183655, 0.010641] | 0.942706 |
| N2_respiration | -0.040132 | [-0.184402, -0.015802] | 0.982002 |
| N3_cardiac_pulse | -0.037937 | [-0.179932, 0.011700] | 0.949205 |
| N4_motion_respiration_cardiac | -0.018814 | [-0.174041, 0.060984] | 0.829317 |

Interpretation:

```text
The primary same-transition contrast is not positive in the raw rung, so downstream nuisance-survival gates cannot be claimed.
```

P8-v2 permutation smoke:

```text
permutations per tested rung = 100
tested rungs = N0_raw_basic, N4_motion_respiration_cardiac
```

| Rung | True Contrast p vs Label Shuffle | Classification p vs Label Shuffle | Classification p vs Domain-Preserving Shuffle |
|---|---:|---:|---:|
| N0_raw_basic | 0.881188 | 0.009901 | 0.009901 |
| N4_motion_respiration_cardiac | 0.405941 | 0.009901 | 0.009901 |

ds005795 streaming extension:

```text
n_subjects_requested = 5
n_subjects_passed = 5
subjects = sub-01, sub-02, sub-03, sub-04, sub-05
```

| Model | Mean MSE | Mean R2 | Subjects |
|---|---:|---:|---:|
| N0 state only | 308.008097 | 0.480632 | 5 |
| N1 state + cardiac/respiration | 288.628925 | 0.516281 | 5 |
| N2 state + metadata | 304.121571 | 0.485793 | 5 |
| N3 state + physiology + metadata | 286.173932 | 0.519003 | 5 |

| Model | Delta MSE vs N0 | Delta R2 vs N0 |
|---|---:|---:|
| N1 state + cardiac/respiration | 19.379172 | 0.035649 |
| N2 state + metadata | 3.886527 | 0.005161 |
| N3 state + physiology + metadata | 21.834165 | 0.038371 |

Statistics boundary:

```text
The ds005795 extension is descriptive at five subjects and uses a global signal endpoint. It is not a subject-level inferential rescue of the failed HCP primary transition-reproducibility gate.
```
