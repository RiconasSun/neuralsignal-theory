# Falsifying Noise Explanations for Reproducible Brain-State Transitions

Authors: [TO BE FILLED]  
Affiliations: [TO BE FILLED]  
Correspondence: [TO BE FILLED]

## Abstract

Paper 3 found reproducible macroscopic stage-transition vectors for ENCODE-to-MAINTAIN and MAINTAIN-to-PROBE transitions. Here we test whether that transition contrast is plausibly explained by nuisance structure, timing position, synthetic noise sensitivity, or label artifacts. We audited available raw/event/state inputs, attempted online recovery of OpenNeuro derivatives/confound files, reproduced the Paper 3 transition contrast, residualized transition vectors against proxy nuisance variables, compared nuisance-only and transition-aware prediction models, injected synthetic Gaussian corruption, evaluated timing-position alternatives, and ran frequency-preserving transition-label shuffles. The current claim-audit status is `P4_PROXY_FALSIFICATION_SUPPORTED_BUT_SYNTHETIC_NOISE_ROBUSTNESS_LIMITED`. The evidence supports only the bounded claim that the transition contrast is not fully explained by the tested proxy nuisance and timing alternatives. Because measured motion and physiological confound files were not found locally or in the targeted OpenNeuro recovery, the study does not fully exclude measured motion or physiology.

## 1. Introduction

Reproducibility alone is not enough. A repeated transition pattern may reflect neural state dynamics, but it may also reflect motion, trial timing, run structure, HRF smoothing, scanner drift, or preprocessing artifacts. Paper 4 treats these alternatives as the object of study.

## 2. Methods

The analysis used the same frozen state tables used by Paper 3: ds001635, ds001634, and ds004469. Transition vectors were defined as `T = S_target - S_source`. E1 audited local measured confound availability and incorporated targeted OpenNeuro online recovery manifests when present. E2 reproduced the Paper 3 same-transition versus different-transition contrast. E3/E4 tested proxy nuisance alternatives using residualization and nuisance-only prediction. E5 injected synthetic noise. E6 tested timing-position alternatives. E7 ran transition-label shuffle nulls. E8 enforced claim boundaries.

## 3. Results

### 3.1 Confound Audit

| dataset | state_file | state_file_exists | raw_root | raw_root_exists | events_tsv_count | bold_json_count | bold_nii_gz_count | measured_confound_file_count | measured_confounds_available | confound_files | online_recovery_manifest_available | online_recovery_status | online_recovered_candidate_confound_file_count | online_measured_confounds_recovered | online_recovery_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ds001635 | paper1\state_extraction\stage_states.csv | True | paper1\data_raw\ds001635 | True | 48 | 48 | 48 | 0 | False | nan | True | NO_MEASURED_CONFOUNDS_FOUND_ON_OPENNEURO | 0 | False | RuntimeError: Could not find path in the dataset: - derivatives/** There were no similar filenames found in the metadata. Please check your includes.; Runtim... |
| ds001634 | paper1\external_validation\stage_states_external.csv | True | paper1\data_raw\ds001634 | True | 57 | 57 | 57 | 0 | False | nan | True | NO_MEASURED_CONFOUNDS_FOUND_ON_OPENNEURO | 0 | False | RuntimeError: Could not find path in the dataset: - derivatives/** There were no similar filenames found in the metadata. Please check your includes.; Runtim... |
| ds004469 | paper2\external_holdout\stage_states_dataset_c.csv | True | paper2\external_holdout\ds004469_final_input | True | 63 | 63 | 63 | 0 | False | nan | True | NO_MEASURED_CONFOUNDS_FOUND_ON_OPENNEURO | 0 | False | RuntimeError: Could not find path in the dataset: - derivatives/** There were no similar filenames found in the metadata. Please check your includes.; Runtim... |

### 3.2 Transition Contrast Reproduction

| dataset | label_field | same_mean_cosine | different_null_mean_cosine | same_minus_different | n_same | n_different | supports_signal |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ds001634 | transition_type | 0.7765306274806373 | -0.6692277776863865 | 1.4457584051670238 | 114 | 57 | True |
| ds001635 | transition_type | 0.6674587699598806 | -0.4712997771762725 | 1.1387585471361532 | 96 | 48 | True |
| ds004469 | transition_type | 0.4939706236331221 | -0.3166544002510807 | 0.8106250238842029 | 126 | 63 | True |

### 3.3 Proxy Nuisance Residualization

| dataset | label_field | same_mean_cosine | different_null_mean_cosine | same_minus_different | n_same | n_different | supports_signal | residualization_variant | nuisance_fields |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ds001634 | transition_type | 0.6340416141086701 | -0.5441023395570231 | 1.1781439536656932 | 114 | 57 | True | time_only | time_bin |
| ds001635 | transition_type | 0.5073765720278773 | -0.2962899890330473 | 0.8036665610609246 | 96 | 48 | True | time_only | time_bin |
| ds004469 | transition_type | 0.7582223318009584 | -0.3806249040274082 | 1.1388472358283668 | 126 | 63 | True | time_only | time_bin |
| ds001634 | transition_type | 0.7741820688650334 | -0.750132145267457 | 1.5243142141324904 | 114 | 57 | True | domain_load_context | domain+load+context |
| ds001635 | transition_type | 0.6614999591171907 | -0.5494461330608457 | 1.2109460921780364 | 96 | 48 | True | domain_load_context | domain+load+context |
| ds004469 | transition_type | 0.9380131033620716 | 0.8373274514233975 | 0.1006856519386741 | 126 | 63 | True | domain_load_context | domain+load+context |
| ds001634 | transition_type | 0.6355998029042705 | -0.5572159314230517 | 1.1928157343273222 | 114 | 57 | True | run_time_context | run+time_bin+domain+load+context |
| ds001635 | transition_type | 0.507309682839488 | -0.3016320791653386 | 0.8089417620048265 | 96 | 48 | True | run_time_context | run+time_bin+domain+load+context |
| ds004469 | transition_type | 0.7582223318009584 | -0.3806249040274082 | 1.1388472358283666 | 126 | 63 | True | run_time_context | run+time_bin+domain+load+context |
| ds001634 | transition_type | 0.5961254940208494 | -0.7976254154777639 | 1.3937509094986131 | 114 | 57 | True | subject_run_time_context | subject+run+time_bin+domain+load+context |
| ds001635 | transition_type | 0.4142989875526956 | -0.6947780004492086 | 1.1090769880019042 | 96 | 48 | True | subject_run_time_context | subject+run+time_bin+domain+load+context |
| ds004469 | transition_type | 0.6785748718249974 | -0.9999996425701928 | 1.6785745143951902 | 126 | 63 | True | subject_run_time_context | subject+run+time_bin+domain+load+context |

### 3.4 Synthetic Noise

| dataset | noise_sigma_multiplier | n_repeats | mean_same_minus_different | min_same_minus_different | survival_rate_positive | survives_synthetic_noise |
| --- | --- | --- | --- | --- | --- | --- |
| ds001634 | 0.25 | 100 | 0.0241606175256049 | -0.0010335285637067 | 0.98 | True |
| ds001635 | 0.25 | 100 | 0.0148935636945761 | -0.0117566166992293 | 0.88 | False |
| ds004469 | 0.25 | 100 | 0.1018887460922906 | 0.0766737369752745 | 1.0 | True |
| ds001634 | 0.5 | 100 | 0.0060250838178819 | -0.0272643793690153 | 0.7 | False |
| ds001635 | 0.5 | 100 | 0.0029779219278882 | -0.0223358378279149 | 0.6 | False |
| ds004469 | 0.5 | 100 | 0.0951802586476669 | 0.0734292915604024 | 1.0 | True |
| ds001634 | 1.0 | 100 | 0.0025925816669255 | -0.0255285100230348 | 0.55 | False |
| ds001635 | 1.0 | 100 | -0.0013367492896809 | -0.0328325281152923 | 0.45 | False |
| ds004469 | 1.0 | 100 | 0.0925356640316873 | 0.0692538699109151 | 1.0 | True |
| ds001634 | 2.0 | 100 | 0.0018548836465265 | -0.0327295812580163 | 0.58 | False |
| ds001635 | 2.0 | 100 | 0.0005884128074812 | -0.0290157376254446 | 0.52 | False |
| ds004469 | 2.0 | 100 | 0.0865606109908813 | 0.0661411645659979 | 1.0 | True |

### 3.5 Timing Tests

| dataset | test | transition_same_minus_different | time_bin_same_minus_different | time_baseline_status | transition_exceeds_time_baseline | n_time_same | n_time_different |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ds001634 | time_bin_same_vs_different | 1.4457584051670238 | nan | INCONCLUSIVE_NO_SPLIT_HALF_TIME_BIN_GROUPS | nan | 0 | 0 |
| ds001635 | time_bin_same_vs_different | 1.1387585471361532 | nan | INCONCLUSIVE_NO_SPLIT_HALF_TIME_BIN_GROUPS | nan | 0 | 0 |
| ds004469 | time_bin_same_vs_different | 0.8106250238842029 | nan | INCONCLUSIVE_NO_SPLIT_HALF_TIME_BIN_GROUPS | nan | 0 | 378 |
| ds001634 | transition_after_time_bin_residualization | 1.1781439536656932 | nan | RESIDUALIZATION_TEST | True | 114 | 57 |
| ds001635 | transition_after_time_bin_residualization | 0.8036665610609246 | nan | RESIDUALIZATION_TEST | True | 96 | 48 |
| ds004469 | transition_after_time_bin_residualization | 1.1388472358283668 | nan | RESIDUALIZATION_TEST | True | 126 | 63 |

### 3.6 Label-shuffle Null

| dataset | null_test | observed_same_minus_different | n_permutations | null_mean | null_99th_percentile | observed_percentile_vs_null | upper_tail_p | survives_99_percent_null |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ds001634 | frequency_preserving_transition_label_shuffle | 1.4457584051670238 | 500 | -0.2309452072495131 | -0.078055431122446 | 1.0 | 0.0019960079840319 | True |
| ds001635 | frequency_preserving_transition_label_shuffle | 1.1387585471361532 | 500 | -0.2119220246084444 | -0.0645128474127131 | 1.0 | 0.0019960079840319 | True |
| ds004469 | frequency_preserving_transition_label_shuffle | 0.8106250238842029 | 500 | -0.1768136830244614 | -0.0435188081710145 | 1.0 | 0.0019960079840319 | True |

## 4. Discussion

The completed tests strengthen the transition object from Paper 3 against several proxy nuisance and timing explanations, but they do not eliminate noise. The most important limitation is that local measured head-motion and physiological confounds were not available. Therefore the paper cannot honestly claim that motion or physiology has been fully excluded.

Critical limitation: No local measured head-motion or physiological confounds.tsv files were found. The completed tests address proxy nuisance structure, timing-position alternatives, synthetic noise, and label-shuffle nulls, but do not fully exclude measured motion or physiology.

## 5. Conclusion

Current claim-audit status: `P4_PROXY_FALSIFICATION_SUPPORTED_BUT_SYNTHETIC_NOISE_ROBUSTNESS_LIMITED`.

## Data Availability

Publication supplement: [P4 data sources, sample manifests, access conditions, and figure provenance](../DATA_AVAILABILITY.md). Code, papers, and derived results are published at [neuralsignal-theory/test](https://github.com/RiconasSun/neuralsignal-theory/tree/test). Raw participant imaging/signals and tractography remain with the original data providers and are not redistributed. The supplement records dataset identifiers and versions available in existing evidence, links to cohort/pipeline records, and distinguishes unrecorded historical metadata from verified information. Exact local withheld filenames and SHA256 values are recorded in [the raw file inventory](../../publication/raw_file_inventory.csv); derived artifacts and figures have [SHA256 checksums](../../publication/artifact_checksums.csv).

OpenNeuro-derived local state tables from Papers 1-3 were used. Raw local dataset copies were audited for events, BOLD metadata, and measured confound files. Targeted OpenNeuro online recovery was attempted for derivatives/confound/motion/regressor/DVARS/FD file patterns and recorded in `paper4/online_confound_recovery/online_confound_recovery_summary.json`.

## Code Availability

Code: [neuralsignal-theory/test](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper4/scripts). See [the data and figure guide](../DATA_AVAILABILITY.md) for reproduction prerequisites.

## Ethics Statement

This analysis uses public de-identified datasets. Dataset-specific ethics approvals are reported by the original data providers.

## Conflicts of Interest

[TO BE FILLED]

## Claim Audit

```json
{
  "experiment": "P4-E8",
  "status": "P4_PROXY_FALSIFICATION_SUPPORTED_BUT_SYNTHETIC_NOISE_ROBUSTNESS_LIMITED",
  "measured_motion_or_physiology_confounds_available": false,
  "claim_allowed_transition_not_fully_explained_by_tested_proxy_nuisance": true,
  "claim_allowed_measured_motion_fully_excluded": false,
  "claim_allowed_noise_eliminated": false,
  "claim_allowed_cwp_validated": false,
  "gate_e2_p3_reproduction": true,
  "gate_e3_e4_strict_proxy_residualized_signal_positive": true,
  "gate_e5_one_sigma_synthetic_noise_survival": false,
  "gate_e6_time_residualized_signal_positive": true,
  "gate_e6_transition_exceeds_time_bin_baseline": false,
  "gate_e6_time_bin_baseline_valid_dataset_count": 0,
  "gate_e7_label_shuffle_null_survival": true,
  "critical_limitation": "No local measured head-motion or physiological confounds.tsv files were found. The completed tests address proxy nuisance structure, timing-position alternatives, synthetic noise, and label-shuffle nulls, but do not fully exclude measured motion or physiology.",
  "no_invented_results": true
}
```
