# A7 Null / Falsification Tests

## Implemented Nulls

E6 currently implements:

- label shuffle
- pseudo-CWP ontology
- domain/load-preserving label shuffle
- subject shuffle
- time-only baseline

## Current Result

E6 has been run on real ds001635 stage states.

```text
true_cwp_mse: 1.1905904151828643
pseudo_cwp_survival_percentile: 1.0
required_survival_percentile: 0.99
```

## Explicitly Blocked Nulls

Motion-only model:

```text
status: requires confounds.tsv or motion columns
```

Boundary jitter:

```text
status: requires event-level perturbation followed by E1 rerun
```

These are intentionally not faked and cannot be counted as completed robustness evidence.
