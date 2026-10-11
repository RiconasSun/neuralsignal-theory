# Cross-Dataset Failure and Generalization of CWP-style Brain-State Models

Authors: [TO BE FILLED]  
Affiliations: [TO BE FILLED]  
Correspondence: [TO BE FILLED]

## Abstract

Paper 1 found within-dataset out-of-distribution signal for CWP-style compositional representations, but failed external validation from OpenNeuro ds001635 to ds001634. Here we treat that failure as the object of study. We reproduced the A-to-B failure, decomposed candidate sources across measurement scaling, state representation, task context, and ontology granularity, froze an A/B-derived v2 candidate, and evaluated it once on a newly selected Dataset C, OpenNeuro ds004469 v1.1.3. The A/B diagnostics identified plausible measurement, state-representation, and ontology candidates, but also revealed null risk because random ontology structure could reduce the CWP-vs-task gap. On Dataset C, CWP_v2_medium beat RandomOntology but did not beat the StrongTask baseline. The current evidence therefore does not support CWP-specific cross-dataset generalization or a rescue of the CWP strong hypothesis.

## 1. Introduction

The central question is why a CWP-style representation can show local compositional advantage but fail across independent datasets. This manuscript does not reinterpret Paper 1 as successful. Dataset B is treated as a failure-analysis dataset, while Dataset C is the final external holdout.

The sharpened question is whether semantic ontology matters beyond generic compositional structure. If a pseudo ontology performs similarly, any improvement may reflect compression, regularization, or representation geometry rather than CWP-specific cognitive semantics.

## 2. Methods

Dataset A was OpenNeuro ds001635. Dataset B was OpenNeuro ds001634 and was used only for failure analysis because its external failure was already observed in Paper 1. Dataset C was locked as OpenNeuro ds004469 v1.1.3 after metadata/event audit. Its Sternberg task events were mapped as Coding to ENCODE, Retention to MAINTAIN, and Test to PROBE. Dataset C does not test TRANSFORM.

All models predicted next brain state from current brain state and categorical descriptors. The main comparison included M2 StrongTask, M3 CWP v1, CWP_v2_medium, and RandomOntology. The CWP-specific success rule required CWP_v2_medium to beat both StrongTask and RandomOntology on Dataset C.

## 3. Results

### 3.1 Failure Reproduction

Paper 1 external failure was reproduced:

```text
M2_strong_task MSE: 528.5845188041816
M3_cwp MSE: 531.7837157074374
status: REPRODUCED_FAILURE
```

### 3.2 A/B Diagnostic Candidate

The frozen v2 candidate was:

```text
selected_factor_family: ontology
selected_variant: ontology_medium
status: FROZEN_V2_CANDIDATE_WITH_NULL_RISK
null_risk: random ontology produced the largest apparent gap reduction
```

This is diagnostic only, not independent replication.

### 3.3 Dataset C Final Holdout

Dataset C produced 2,268 stage states and 1512 transitions. Final comparison:

```text
M2_strong_task MSE: 15411126.594459493
M3_cwp v1 MSE: 16937784.139945235
CWP_v2_medium MSE: 16921457.350479256
RandomOntology MSE: 20533230.666308556
```

CWP_v2_medium beat RandomOntology: True.  
CWP_v2_medium beat M2_strong_task: False.  
Final status: DATASET_C_CWP_SPECIFIC_NOT_SUPPORTED.

Subject-level effects were heterogeneous: CWP_v2_medium beat StrongTask for 41/63 subjects, but aggregate MSE was worse than StrongTask.

## 4. Discussion

The evidence supports a constrained failure-analysis story. Measurement scaling, state representation, and ontology granularity can reduce the A/B CWP-vs-task gap, but the Dataset C final holdout does not support a CWP-specific rescue. The strongest allowed interpretation is that compositional structure may sometimes help transfer, but the current semantic CWP ontology is not validated as a dataset-invariant neural primitive.

The negative result is scientifically useful because it prevents conflating local OOD advantage with general cognitive primitives. Future work should treat v3 ontology or alignment changes as exploratory until tested on a new clean holdout.

## 5. Conclusion

Paper 2 reproduces the Paper 1 external failure, identifies plausible diagnostic mechanisms, and rejects the current CWP-specific cross-dataset generalization claim on Dataset C.

## Data Availability

Publication supplement: [P2 data sources, sample manifests, access conditions, and figure provenance](../DATA_AVAILABILITY.md). Code, papers, and derived results are published at [neuralsignal-theory/test](https://github.com/RiconasSun/neuralsignal-theory/tree/test). Raw participant imaging/signals and tractography remain with the original data providers and are not redistributed. The supplement records dataset identifiers and versions available in existing evidence, links to cohort/pipeline records, and distinguishes unrecorded historical metadata from verified information. Exact local withheld filenames and SHA256 values are recorded in [the raw file inventory](../../publication/raw_file_inventory.csv); derived artifacts and figures have [SHA256 checksums](../../publication/artifact_checksums.csv).

OpenNeuro ds001635, ds001634, and ds004469 were used. Dataset C DOI: doi:10.18112/openneuro.ds004469.v1.1.3.

## Code Availability

Code: [neuralsignal-theory/test](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper2/scripts). See [the data and figure guide](../DATA_AVAILABILITY.md) for reproduction prerequisites.

## Ethics Statement

This study uses public de-identified datasets. Dataset-specific ethics statements are reported by the original data providers.

## Conflicts of Interest

[TO BE FILLED]

## Claim Audit

```json
{
  "claim_allowed_cross_dataset_generalization": false,
  "claim_allowed_cwp_rescued": false,
  "claim_allowed_cwp_specific_fix": false,
  "claim_allowed_failure_diagnostic_candidate_identified": true,
  "claim_allowed_failure_explained": false,
  "claim_allowed_generic_composition_possible": true,
  "dataset_b_role": "failure-analysis dataset, not final holdout",
  "dataset_c_status": "DATASET_C_CWP_SPECIFIC_NOT_SUPPORTED",
  "e9_0_failure_reproduction": "REPRODUCED_FAILURE",
  "experiment": "E9.8",
  "no_invented_results": true,
  "remaining_blockers": [],
  "semantic_specificity_rule": "CWP-specific generalization requires CWP_v2 to beat both StrongTask and Random/PseudoOntology on Dataset C.",
  "status": "completed_with_dataset_c",
  "v2_candidate_status": "FROZEN_V2_CANDIDATE_WITH_NULL_RISK"
}
```
