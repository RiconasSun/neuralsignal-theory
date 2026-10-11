# A7. Null / Falsification Tests

Planned tests:

```text
phase shuffle
circular time shift
random segmentation
transition-label shuffle
duration-matched random windows
spike-time jitter if spike data exist
electrode/channel shuffle
event-timing-only baseline
simple band-power-only baseline
```

Status:

```text
FULL AVAILABLE ds004117 NULL TESTS RUN
```

Implemented null tests:

```text
transition-label shuffle
duration-matched random segmentation / random windows
random-window specificity baseline
time-shift specificity baseline
phase-randomized bandpower control
```

Full available ds004117 null results:

```text
real leave-one-run-out transition specificity accuracy: 0.6806682577565633
label-shuffle null mean accuracy: 0.5009307875894987
label-shuffle null 95% CI: [0.48591885441527444, 0.5164677804295943]
one-sided permutation p: 0.004975124378109453
random-window specificity accuracy: 0.5053160070880095
time-shift specificity accuracy: 0.5100459937061245
phase-randomized bandpower specificity accuracy: 0.7047732696897375
```

Gate result:

```text
real specificity > label-shuffle 95% CI upper bound: PASS
real specificity > random-window specificity: PASS
real specificity > time-shift specificity: PASS
```

Important limitation:

```text
Phase randomization does not destroy Fourier amplitude spectra. Because the implemented feature family is log bandpower delta, strong phase-randomized performance is expected to preserve much of the same information. This prevents phase-specific or NAP-specific claims from the current result.
```

Planned but not yet run:

```text
genuinely phase-sensitive nulls
spike-time jitter if spike data exist
electrode/channel shuffle
event-timing-only baseline
direct external-dataset transition-boundary null replication
```

Claim boundary:

```text
The current nulls support a transition-aligned EEG bandpower-delta signal in ds004117. They do not validate NAPs or complete P6.
```

E7 external convergent null:

```text
dataset: ds004752
analysis: encoding-vs-maintenance LCMV derivative stage specificity
observed accuracy: 0.6276102088167054
label-shuffle null mean accuracy: 0.49868184454756376
label-shuffle null 95% CI: [0.47998839907192575, 0.5183077146171694]
one-sided permutation p: 0.004975124378109453
```
