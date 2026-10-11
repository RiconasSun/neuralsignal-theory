# A6. Statistics

Primary estimand:

```text
same-transition fast-dynamics similarity
-
matched-null fast-dynamics similarity
```

Implemented inference:

```text
leave-one-run-out transition specificity
held-out prediction label-shuffle permutation null with 200 permutations
duration-matched random-window specificity baseline
time-shift transition-window specificity baseline
subject-level accuracy bootstrap
binomial test for subjects above chance
```

Status:

```text
FULL AVAILABLE ds004117 SUBJECT-LEVEL STATISTICS COMPLETE
EXTERNAL REPLICATION NOT YET RUN
```

Full available ds004117 result:

```text
subjects: 23
runs/event files: 85
transition windows: 4190
random windows: 3386
time-shift windows: 4131
phase-randomized windows: 4190
same-transition odd/even centroid similarity: 0.994146078824997
random-window odd/even centroid similarity: -0.029297083616256714
delta similarity: 1.0234431624412537
leave-one-run-out accuracy: 0.6806682577565633
label-shuffle null mean accuracy: 0.5009307875894987
label-shuffle null 95% CI: [0.48591885441527444, 0.5164677804295943]
one-sided permutation p: 0.004975124378109453
subject mean accuracy: 0.7116372328567145
subject bootstrap 95% CI: [0.6779915892328661, 0.7447466470064257]
subjects above chance: 23 / 23
binomial p for subjects above chance: 1.1920928955078125e-07
```

Remaining final inference:

```text
direct external transition-boundary replication statistics
FDR correction for secondary feature families after they are run
sensitivity analysis for alternative windows and feature families
```

External convergent E7 statistics:

```text
dataset: ds004752
subjects: 15
trials: 3448
encoding trials: 1724
maintenance trials: 1724
leave-one-subject-out accuracy: 0.6276102088167054
subject mean accuracy: 0.6288650530091637
subject bootstrap 95% CI: [0.5773691737749553, 0.6830378459547412]
label-shuffle null mean accuracy: 0.49868184454756376
label-shuffle null 95% CI: [0.47998839907192575, 0.5183077146171694]
one-sided permutation p: 0.004975124378109453
```

E7 interpretation:

```text
This is external convergent evidence for stage-specific fast electrophysiological structure. It is not direct transition-boundary replication because ds004752 derivative files provide separated encoding and maintenance trial data rather than transition-boundary windows matching ds004117.
```
