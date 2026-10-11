# Paper 2 Figure Captions

## Figure 1. A-to-B failure reproduction

Reproduction of the Paper 1 external transfer failure from ds001635 to ds001634. M3 CWP v1 has higher MSE than M2 StrongTask, preserving the original external failure.

## Figure 2. Failure-attribution diagnostics

Top gap-reduction candidates from A/B diagnostic analyses. Positive values indicate reduction of the CWP-vs-StrongTask MSE gap within the same metric space. These are diagnostic candidates, not independent replication.

## Figure 3. Dataset C final holdout

Final comparison on OpenNeuro ds004469 v1.1.3. CWP_v2_medium improves over RandomOntology but does not improve over M2 StrongTask, so the CWP-specific Dataset C gate fails.

## Figure 4. Dataset C subject-level heterogeneity

Distribution of subject-level CWP_v2_medium minus StrongTask MSE on Dataset C. Negative values favor CWP_v2_medium. The subject-level direction is heterogeneous and does not override the aggregate primary MSE failure.
