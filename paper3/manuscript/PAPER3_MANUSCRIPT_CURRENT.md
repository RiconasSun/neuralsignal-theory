# Reproducibility of Stage-Conditioned Brain-State Transitions Across Runs, Subjects, and Datasets

Authors: [TO BE FILLED]  
Affiliations: [TO BE FILLED]  
Correspondence: [TO BE FILLED]

## Abstract

Paper 1 and Paper 2 constrained the CWP strong hypothesis by showing local compositional signal but no CWP-specific cross-dataset superiority. Paper 3 therefore asks a more basic question: are the extracted macroscopic stage-transition vectors themselves reproducible empirical objects? Using frozen state files from OpenNeuro ds001635, ds001634, and ds004469, we estimate ENCODE-to-MAINTAIN and MAINTAIN-to-PROBE transition vectors and test within-run split-half reliability, cross-run same-subject reliability where repeated runs exist, same-transition versus different-transition contrasts, cross-dataset transition similarity, and label-shuffle nulls. The current claim-audit status is `P3_REPRODUCIBILITY_SUPPORTED`. These results support only the bounded claim reported in the audit and do not validate CWP as a general neural primitive.

## 1. Introduction

The prior papers showed that local out-of-distribution gains do not imply a universal CWP representation. The next defensible step is reproducibility: before asking whether a cognitive ontology is correct, the transition objects produced by the extraction pipeline must show stability.

## 2. Methods

The analysis uses three frozen state tables: ds001635, ds001634, and ds004469. For each trial, transition vectors were defined as `T = S_target - S_source` for `ENCODE -> MAINTAIN` and `MAINTAIN -> PROBE`. E1 audited state availability and stage completeness. E2 measured within-run split-half reliability. E3 measured cross-run same-subject reliability where run labels were available. E4 compared same-transition reliability against a different-transition null. E5 summarized dataset-specific reproducibility. E6 compared same versus different transition vectors across datasets. E7 used within-dataset transition-label shuffling as a falsification test. E8 aggregated statistics and enforced the claim audit.

## 3. Results

### 3.1 Dataset Inventory

| dataset | state_file | status | n_states | n_transitions | n_subjects | n_subject_runs | n_roi_features | stage_counts | transition_counts | run_counts | has_repeated_runs_for_cross_run_reliability | subjects_missing_any_primary_stage | primary_stage_completeness |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ds001635 | paper1\state_extraction\stage_states.csv | AUDITED | 2291 | 1523 | 16 | 48 | 216 | {'ENCODE': 768, 'MAINTAIN': 768, 'PROBE': 755} | {'ENCODE_TO_MAINTAIN': 768, 'MAINTAIN_TO_PROBE': 755} | {'run-01': 764, 'run-02': 765, 'run-03': 762} | True | 0 | True |
| ds001634 | paper1\external_validation\stage_states_external.csv | AUDITED | 3066 | 2040 | 19 | 57 | 216 | {'ENCODE': 1026, 'MAINTAIN': 1026, 'PROBE': 1014} | {'ENCODE_TO_MAINTAIN': 1026, 'MAINTAIN_TO_PROBE': 1014} | {'run-01': 1021, 'run-02': 1022, 'run-03': 1023} | True | 0 | True |
| ds004469 | paper2\external_holdout\stage_states_dataset_c.csv | AUDITED | 2268 | 1512 | 63 | 63 | 216 | {'ENCODE': 756, 'MAINTAIN': 756, 'PROBE': 756} | {'ENCODE_TO_MAINTAIN': 756, 'MAINTAIN_TO_PROBE': 756} | {'run-unknown': 2268} | False | 0 | True |

### 3.2 Within-run Reliability and Same-vs-Different Contrast

| dataset | same_transition_mean_cosine | different_transition_null_mean_cosine | same_minus_different | supports_within_run_reproducibility |
| --- | --- | --- | --- | --- |
| ds001634 | 0.7765306274806373 | -0.6692277776863865 | 1.4457584051670238 | True |
| ds001635 | 0.6674587699598806 | -0.4712997771762725 | 1.1387585471361532 | True |
| ds004469 | 0.4939706236331221 | -0.3166544002510807 | 0.8106250238842029 | True |

### 3.3 Cross-run Reproducibility

| dataset | comparison | n | mean_cosine | median_cosine | std_cosine | bootstrap_ci_low | bootstrap_ci_high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ds001634 | cross_run_same_subject_same_transition | 114 | 0.8175730445349313 | 0.91384466287683 | 0.2205070123709803 | 0.7743524285784247 | 0.8575041860226378 |
| ds001635 | cross_run_same_subject_same_transition | 96 | 0.7773176084018759 | 0.8406259140053818 | 0.2170500371444774 | 0.7346125457654672 | 0.816098335299832 |

### 3.4 Cross-dataset Reproducibility

| comparison | n | mean_cosine | median_cosine | std_cosine | bootstrap_ci_low | bootstrap_ci_high |
| --- | --- | --- | --- | --- | --- | --- |
| different_transition_cross_dataset_null | 6 | -0.4546305487288635 | -0.3296462387584628 | 0.2963866295933524 | -0.6765994677759571 | -0.258450724450705 |
| same_transition_cross_dataset | 6 | 0.4917027087021893 | 0.3251981380945946 | 0.3677070431101814 | 0.2495248346905871 | 0.7489385858344405 |

### 3.5 Null Tests

| null_test | dataset | observed_same_minus_different | n_permutations | null_mean | null_99th_percentile | observed_percentile_vs_null | upper_tail_p | survives_99_percent_null |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| within_dataset_label_shuffle | ds001634 | 1.4457584051670238 | 500 | -0.2335545030716123 | -0.0742840244928331 | 1.0 | 0.0019960079840319 | True |
| within_dataset_label_shuffle | ds001635 | 1.1387585471361532 | 500 | -0.2163100000112396 | -0.0531863944680163 | 1.0 | 0.0019960079840319 | True |
| within_dataset_label_shuffle | ds004469 | 0.8106250238842029 | 500 | -0.1766451734613774 | -0.0445604306706864 | 1.0 | 0.0019960079840319 | True |

## 4. Discussion

The paper should be read as a reproducibility and boundary study, not as a CWP validation paper. A positive same-transition contrast would support repeatability of the extracted transition vectors under the current state representation. Failure in any gate limits the claim to dataset- or pipeline-specific reproducibility.

Critical limitation: The study tests repeatability of extracted macroscopic stage-transition vectors. It does not establish CWP as a natural neural primitive and ds004469 lacks repeated run labels.

Unsupported claims remain explicitly disallowed: CWP is validated; CWP is a natural neural primitive; CWP-specific cross-dataset superiority is established.

## 5. Conclusion

Current claim-audit status: `P3_REPRODUCIBILITY_SUPPORTED`.

## Data Availability

Publication supplement: [P3 data sources, sample manifests, access conditions, and figure provenance](../DATA_AVAILABILITY.md). Code, papers, and derived results are published at [neuralsignal-theory/test](https://github.com/RiconasSun/neuralsignal-theory/tree/test). Raw participant imaging/signals and tractography remain with the original data providers and are not redistributed. The supplement records dataset identifiers and versions available in existing evidence, links to cohort/pipeline records, and distinguishes unrecorded historical metadata from verified information. Exact local withheld filenames and SHA256 values are recorded in [the raw file inventory](../../publication/raw_file_inventory.csv); derived artifacts and figures have [SHA256 checksums](../../publication/artifact_checksums.csv).

OpenNeuro ds001635, ds001634, and ds004469 were used through previously generated state tables in this workspace.

## Code Availability

Code: [neuralsignal-theory/test](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper3/scripts). See [the data and figure guide](../DATA_AVAILABILITY.md) for reproduction prerequisites.

## Ethics Statement

This analysis uses public de-identified datasets. Dataset-specific ethics approvals are reported by the original dataset providers.

## Conflicts of Interest

[TO BE FILLED]

## Claim Audit

```json
{
  "experiment": "P3-E8",
  "status": "P3_REPRODUCIBILITY_SUPPORTED",
  "claim_allowed_transition_reproducibility": true,
  "claim_allowed_cwp_validated": false,
  "claim_allowed_cwp_general_primitive": false,
  "claim_allowed_cross_dataset_cwp_superiority": false,
  "within_run_reproducibility_supported_all_datasets": true,
  "cross_run_reproducibility_supported_available_datasets": true,
  "cross_dataset_same_greater_than_different": true,
  "label_shuffle_null_survival_all_datasets": true,
  "critical_limitation": "The study tests repeatability of extracted macroscopic stage-transition vectors. It does not establish CWP as a natural neural primitive and ds004469 lacks repeated run labels.",
  "no_invented_results": true
}
```
