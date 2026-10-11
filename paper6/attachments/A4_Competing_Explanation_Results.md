# A4. Competing Explanation Results

Status:

```text
FULL AVAILABLE ds004117 E3-E6 RUN COMPLETE
```

Implemented competing explanations:

```text
transition-label shuffle
duration-matched random windows
random-window specificity baseline
time-shift transition-window baseline
phase-randomized bandpower control
```

Full available ds004117 result:

```text
subjects: 23
runs/event files: 85
transition windows: 4190
duration-matched random windows: 3386
time-shift transition windows: 4131
phase-randomized transition windows: 4190
real leave-one-run-out transition specificity accuracy: 0.6806682577565633
label-shuffle null mean accuracy: 0.5009307875894987
label-shuffle null 95% CI: [0.48591885441527444, 0.5164677804295943]
one-sided permutation p: 0.004975124378109453
random-window specificity accuracy: 0.5053160070880095
time-shift specificity accuracy: 0.5100459937061245
phase-randomized bandpower specificity accuracy: 0.7047732696897375
```

Interpretation:

```text
The full available ds004117 result is not explained by transition-label shuffle, duration-matched random-window specificity, or a fixed time-shift control. However, phase-randomized bandpower specificity remains high. Because the current feature family is log bandpower delta, this phase-control result means the current evidence supports transition-aligned amplitude/bandpower structure, not phase-specific fast dynamics.
```

Remaining competing explanations:

```text
event-timing-only baseline
trial-position baseline
subject/session identity baseline
condition-label baseline without transition windows
genuinely phase-sensitive feature families
external-dataset replication
```
