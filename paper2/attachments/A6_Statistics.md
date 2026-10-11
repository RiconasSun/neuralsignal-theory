# A6 Statistics

Status: A/B diagnostic statistics generated; Dataset C aggregate and subject-level effects generated.

## Primary Estimand

Change in external predictive performance attributable to each shift-alignment intervention.

## Metrics

```text
Primary current metric: MSE
Secondary metrics: R2, cosine similarity
```

## Required Statistical Tests

```text
subject-level paired comparison
bootstrap 95% CI
permutation / sign-flip tests
effect size
FDR correction
```

## Unit of Analysis

Subject or dataset-defined independent evaluation unit.

Forbidden:

```text
treating trials or TRs as independent participants
```

## Dataset C Subject-Level Outputs

```text
paper2/results/e9_7_dataset_c_subject_effects.csv
```

Fields:

```text
subject
n_transitions
M2_strong_task_mse
M3_cwp_mse
CWP_v2_medium_mse
RandomOntology_mse
cwp_v2_minus_strong_task_mse
cwp_v2_minus_random_ontology_mse
```

Current summary:

```text
subjects with transitions: 63
CWP_v2 better than StrongTask: 41/63
CWP_v2 better than RandomOntology: 37/63
mean CWP_v2 - StrongTask MSE: 1510330.756019763
median CWP_v2 - StrongTask MSE: -7.347499898579429
```

Interpretation:

```text
The primary aggregate MSE gate failed because CWP_v2_medium did not beat StrongTask.
The subject-level distribution is heterogeneous and requires explicit reporting.
```
