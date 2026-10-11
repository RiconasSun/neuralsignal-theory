# A8. QC / Leakage Audit

Planned checks:

```text
subject leakage
session leakage
trial leakage
temporal-window leakage
event-label leakage
preprocessing leakage
normalization leakage
electrode/channel identity confounding
site/dataset confounding
post-hoc transition selection
```

Status:

```text
FULL AVAILABLE ds004117 QC / LEAKAGE CONTROLS PARTIALLY RUN
```

Implemented controls:

```text
full available ds004117 feature extraction was batched by subject and aggregated after extraction
leave-one-run-out split prevents identical run reuse between train and test
standardization is fit inside each training fold
random-window null uses duration-matched windows within the same run
time-shift null tests whether displaced transition timing retains the effect
claim audit forbids external-replication and NAP claims
```

Observed leakage-relevant results:

```text
real specificity accuracy: 0.6806682577565633
random-window specificity accuracy: 0.5053160070880095
time-shift specificity accuracy: 0.5100459937061245
label-shuffle null 95% CI upper bound: 0.5164677804295943
```

Not yet complete:

```text
held-out subject split
direct external transition-boundary leakage audit
event-timing-only baseline
channel/electrode identity confound audit
genuinely phase-sensitive checks
```

Claim boundary:

```text
The current controls reduce several obvious leakage explanations for the ds004117 within-dataset result. They do not close all leakage/confound risks required for a final P6 mechanistic claim.
```

E7 external convergent leakage controls:

```text
dataset: ds004752
holdout: leave-one-subject-out
normalization/imputation: fit inside training fold
null: label-shuffle with same fold structure
limitation: derivative stage labels are pre-separated encoding/maintenance fields, so this tests stage specificity rather than transition-boundary specificity
```
