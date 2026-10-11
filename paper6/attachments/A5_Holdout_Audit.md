# A5. Holdout Audit

Status:

```text
FULL AVAILABLE ds004117 RUN-LEVEL HOLDOUT COMPLETE
```

Implemented holdout:

```text
leave-one-run-out transition specificity
```

Full available ds004117 holdout result:

```text
subjects: 23
runs/event files: 85
total held-out predictions: 4190
accuracy: 0.6806682577565633
```

Subject-level summary:

```text
subject mean accuracy: 0.7116372328567145
subject median accuracy: 0.7191780821917808
subject bootstrap 95% CI: [0.6779915892328661, 0.7447466470064257]
subjects above chance: 23 / 23
binomial p for subjects above chance: 1.1920928955078125e-07
```

Isolation mechanism:

```text
Each fold held out one full EEG run/event file.
Training standardization was fit inside the training fold.
Held-out samples from the same run were excluded from fitting.
```

Remaining holdouts:

```text
held-out subject split
external dataset holdout
```

External convergent holdout:

```text
dataset: ds004752
analysis type: external derivative-level encoding-vs-maintenance stage specificity
holdout: leave-one-subject-out
subjects: 15
trials: 3448
accuracy: 0.6276102088167054
subject mean accuracy: 0.6288650530091637
subject bootstrap 95% CI: [0.5773691737749553, 0.6830378459547412]
label-shuffle null 95% CI: [0.47998839907192575, 0.5183077146171694]
one-sided permutation p: 0.004975124378109453
```

Claim boundary:

```text
The current ds004117 holdout supports within-dataset run-level generalization. The ds004752 result supports external convergent stage specificity. It does not establish direct cross-dataset transition-boundary replication.
```
