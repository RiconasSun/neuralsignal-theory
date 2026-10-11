# Paper 5 Phase 0 Frozen Protocol v1

Title: Structural Data Availability Gate for Reproducible Stage-Conditioned Brain-State Transitions

Paper type: Method Paper / feasibility gate

## Core Question

Do the datasets used in Papers 1-4 contain the subject-level structural connectomes required to test whether `G_i` constrains reproducible stage-conditioned transitions?

## Required Primary Input

```text
Subject-level structural connectome matrices aligned to the 216-ROI functional state representation.
```

T1w anatomy alone is not sufficient for the primary `G_i` test.

## Experiment Chain

```text
E1 Dataset / modality audit
E2 Structural connectome inventory
E3 Functional transition inventory
E4 State-only/context baseline
E5 Individual G_i model
E6 Group-average/random/distance nulls
E7 Subject-holdout statistics
E8 Claim audit + paper package
```
