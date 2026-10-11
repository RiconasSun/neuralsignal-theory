# Paper 2 Current Results

Date: 2026-09-01

Status:

```text
E9.0-E9.8 implemented and run for Dataset A/B diagnostics.
E9.7 Dataset C final holdout has been run on ds004469 v1.1.3.
Final status: DATASET_C_CWP_SPECIFIC_NOT_SUPPORTED.
```

## Inputs

```text
Dataset A states: paper1/state_extraction/stage_states.csv
Dataset B states: paper1/external_validation/stage_states_external.csv
Dataset C states: paper2/external_holdout/stage_states_dataset_c.csv
Dataset A transitions: 1,523
Dataset B transitions: 2,040
Dataset C transitions: 1,512
ROI features: 216
```

## E9.0 Failure Reproduction

Paper 1 external failure was reproduced:

```text
M2_strong_task MSE: 528.5845188041816
M3_cwp MSE: 531.7837157074374
status: REPRODUCED_FAILURE
```

This preserves the Paper 1 conclusion that CWP v1 did not externally generalize from ds001635 to ds001634.

## E9.1 Measurement Shift

```text
target_to_source_moment_aligned reduced the CWP-vs-task MSE gap from 3.1992 to -0.00465.
```

Measurement/state scaling is a plausible contributor to the external failure. This is diagnostic, not independent replication.

## E9.2 State Representation Shift

```text
R2_network_12_mean reduced the CWP-vs-task MSE gap from 3.1992 to -0.03805.
R_shared_cca_16 reduced the gap to -0.01630, but emitted a convergence warning.
R_shared_pca_32 worsened the gap to 4.02433.
```

The current 216 native-grid representation is likely part of the cross-dataset failure.

## E9.3 Task-Context Shift

```text
correlation(nearest_train_context_similarity, M3 row MSE): -0.027426
```

This first-pass descriptor does not show a strong context-similarity/error relationship.

## E9.4 Ontology Stress Test

```text
coarse M3_cwp MSE: 531.7837157074374
medium M3_cwp MSE: 528.5292060700046
fine M3_cwp MSE: 528.5845188042871
random M3_cwp MSE: 528.7611714301368
```

Medium ontology is a plausible A/B diagnostic candidate by raw M3 MSE. However, random ontology produced the largest CWP-vs-task gap reduction in E9.5, so semantic CWP specificity is not claim-allowed from A/B.

## E9.5 Failure Attribution

```text
ontology_medium: gap reduction 3.25451
R2_network_12_mean: gap reduction 3.23725
R_shared_cca_16: gap reduction 3.21550
target_to_source_moment_aligned: gap reduction 3.20384
```

P2 has diagnostic candidates for why P1 failed externally, but this is not yet a validated explanation.

## E9.6 Frozen v2 Candidate

```text
selected_factor_family: ontology
selected_variant: ontology_medium
status: FROZEN_V2_CANDIDATE_WITH_NULL_RISK
null_risk: random ontology produced the largest apparent gap reduction
```

This is a Dataset A/B diagnostic candidate only.

## E9.7 Dataset C Final Holdout

Locked Dataset C:

```text
OpenNeuro ds004469 v1.1.3
Dataset DOI: doi:10.18112/openneuro.ds004469.v1.1.3
Dataset name: Temporal Lobe Epilepsy - UNAM
```

Dataset C state extraction:

```text
states extracted: 2,268
transitions evaluated: 1,512
subjects with transitions: 63
stage mapping: Coding -> ENCODE, Retention -> MAINTAIN, Test -> PROBE
```

Final model comparison:

```text
M2_strong_task MSE: 15,411,126.594459493
M3_cwp v1 MSE: 16,937,784.139945235
CWP_v2_medium MSE: 16,921,457.350479256
RandomOntology MSE: 20,533,230.666308556
```

Gate result:

```text
CWP_v2_medium > RandomOntology: yes
CWP_v2_medium > M2_strong_task: no
status: DATASET_C_CWP_SPECIFIC_NOT_SUPPORTED
```

Subject-level note:

```text
CWP_v2 better than StrongTask by subject count: 41/63
CWP_v2 better than RandomOntology by subject count: 37/63
subject mean CWP_v2 - StrongTask MSE: 1,510,330.756019763
subject median CWP_v2 - StrongTask MSE: -7.347499898579429
```

The primary aggregate metric does not support CWP-specific generalization. The subject-level distribution is heterogeneous and should be reported as instability/scale sensitivity, not as a rescue.

## E9.8 Claim Audit

Current allowed claims:

```text
Paper 1 external failure was reproduced.
A/B diagnostics identified plausible measurement, state-representation, and ontology candidates.
CWP_v2_medium beat RandomOntology on Dataset C but failed against StrongTask.
```

Current disallowed claims:

```text
Failure is explained.
CWP is rescued.
CWP-specific fix is proven.
Cross-dataset CWP generalization is proven.
Dataset B is a final clean holdout.
```

Current claim audit:

```text
claim_allowed_failure_explained: false
claim_allowed_failure_diagnostic_candidate_identified: true
claim_allowed_cwp_specific_fix: false
claim_allowed_generic_composition_possible: true
claim_allowed_cross_dataset_generalization: false
claim_allowed_cwp_rescued: false
```
