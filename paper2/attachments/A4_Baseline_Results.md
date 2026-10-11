# A4 Baseline and Competing-Explanation Results

Status: A/B diagnostic run completed; Dataset C final holdout run completed.

## Required Baselines

```text
Raw transfer
dataset-specific task model
simple z-score alignment
CORAL / simple domain adaptation
Procrustes alignment
shared PCA/CCA latent space
task-label model
CWP v1
random ontology
task-context-only model
```

## Competing Explanations

```text
H0 implementation artifact
H1 measurement shift
H2 state representation shift
H3 task/context shift
H4 ontology mismatch
H5 genuine CWP non-invariance
```

## Current Results

```text
E9.0 reproduced the Paper 1 A -> B failure:
M2_strong_task MSE: 528.5845188041816
M3_cwp MSE: 531.7837157074374
status: REPRODUCED_FAILURE

E9.4 ontology stress:
coarse M3_cwp MSE: 531.7837157074374
medium M3_cwp MSE: 528.5292060700046
fine M3_cwp MSE: 528.5845188042871
random M3_cwp MSE: 528.7611714301368

E9.5 attribution warning:
random ontology produced the largest CWP-vs-task gap reduction, so semantic CWP specificity is not claim-allowed from A/B.

E9.7 Dataset C final holdout:
M2_strong_task MSE: 15411126.594459493
M3_cwp v1 MSE: 16937784.139945235
CWP_v2_medium MSE: 16921457.350479256
RandomOntology MSE: 20533230.666308556

E9.7 gate:
CWP_v2_medium beat RandomOntology but did not beat M2_strong_task.
Status: DATASET_C_CWP_SPECIFIC_NOT_SUPPORTED.
```

Full output:

```text
paper2/results/paper2_primary_metrics.csv
paper2/results/e9_5_failure_attribution.csv
paper2/results/e9_7_dataset_c_model_comparison.csv
paper2/results/e9_7_dataset_c_subject_effects.csv
```
