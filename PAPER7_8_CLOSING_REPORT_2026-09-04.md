# Paper 7-8 Closing Report

Date: 2026-09-04

## Paper 7

Status:

```text
P7_10_SUBJECT_CONNECTOME_QC_READY_STRUCTURAL_HYPOTHESIS_NOT_TESTED
```

Completed in this run:

```text
HCP 10-subject smoke cohort inputs audited and ready
WSL MRtrix3 ext4-first MSMT-CSD route implemented
100307 initial zero-FOD issue diagnosed as route/path-sensitive, not dataset-impossible
100307/100408/101107 FreeSurfer-5TT route completed
100307/100408/101107 ACT+iFOD2+SIFT2+tck2connectome smoke completed
10-subject ACT+iFOD2+SIFT2+tck2connectome QC smoke completed
10-subject fs_default84 label-conversion QC completed
100307 20k streamline sensitivity completed; outlier warning persisted
P7 claim audit updated
P7 reproduction script updated
P7 results, manuscript, package index, package audit, and Layer I claim boundary updated
```

Key outputs:

```text
paper7/results/p7_e3_three_subject_final_route_smoke.json
paper7/results/p7_e4_ten_subject_connectome_qc.json
paper7/results/p7_e4_ten_subject_connectome_qc_summary.json
paper7/results/p7_e5_labelconvert_connectome_qc.json
paper7/results/p7_e5_100307_streamline_20000_sensitivity.json
paper7/results/p7_final_route_single_subject_smoke.json
paper7/results/p7_msmt_fod_readiness_validator.json
paper7/results/p7_e8_claim_audit.json
paper7/data_manifest/p7_e4_ten_subject_connectome_qc_summary.csv
paper7/data_manifest/p7_e5_labelconvert_connectome_qc_summary.csv
paper7/protocol/PAPER7_PRE_100_SUBJECT_QC_FREEZE_DRAFT.md
paper7/structural_connectomes/mrtrix_act_sift2_smoke/100307/connectome_sift2_ext4_msmt_smoke.csv
paper7/structural_connectomes/mrtrix_act_sift2_smoke/*/connectome_sift2_ext4_msmt_fsdefault84_smoke.csv
```

Claim boundary:

```text
This is a 10-subject engineering QC smoke. It does not test whether subject-specific structural connectivity improves macroscopic brain-state transition prediction.
```

Remaining P7 requirements:

```text
resolve or preregister handling for the 100307 fs_default84 outlier
freeze final atlas/label-conversion/streamline-count/QC thresholds
run 100-subject frozen structural prediction
compare no-structure, group-mean, true-subject, swapped, rewired, and distance baselines
```

## Paper 8

Status:

```text
P8_V2_FROZEN_NEGATIVE_RESULT_PLUS_P8_FINAL_EXTENSION_THREE_SUBJECT_INTERFACE_SMOKE_READY
```

Completed in this run:

```text
P8 ds005795 downloader parameterized for multiple subjects
P8 TR-aligned physiology feature builder parameterized for multiple subjects
P8 nuisance-ladder interface smoke parameterized for multiple subjects
sub-01/sub-02/sub-03 learning BOLD, events, and cardiac/respiratory physiology files downloaded
TR physiology feature tables generated for sub-01/sub-02/sub-03
3-subject global-signal physiology/metadata nuisance-ladder interface smoke completed
P8 claim audit, extension index, package audit, execution summary, and Layer I claim boundary updated
```

Key outputs:

```text
paper8/results/p8_final_extension_ds005795_smoke_download.json
paper8/results/p8_final_extension_ds005795_physio_feature_smoke.json
paper8/results/p8_final_extension_ds005795_nuisance_ladder_smoke.json
paper8/results/p8_e8_claim_audit.json
paper8/state_extraction/ds005795_physio_extension/p8_ds005795_sub01_learning_physio_tr_features.csv
paper8/state_extraction/ds005795_physio_extension/p8_ds005795_sub02_learning_physio_tr_features.csv
paper8/state_extraction/ds005795_physio_extension/p8_ds005795_sub03_learning_physio_tr_features.csv
```

Observed smoke metrics:

```text
mean MSE state only = 258.3504
mean MSE state + cardiac/resp = 235.0614
mean MSE state + metadata = 254.9492
mean MSE state + physiology + metadata = 234.1164
mean R2 state only = 0.4623
mean R2 state + physiology + metadata = 0.5112
```

Claim boundary:

```text
This is a convergent measured-physiology interface smoke only. It does not establish physiology-robust transition dynamics and does not rescue the frozen P8-v2 primary transition failure.
```

## Verification

```text
P7/P8 updated Python scripts py_compile = PASS
P7/P8 key JSON validation = PASS
P7 10-subject smoke connectome QC = PASS
P7 fs_default84 label-conversion QC = PASS, with 100307 outlier
P8 3 smoke physiology feature files exist = PASS
WSL MRtrix residual process check = PASS, no active MRtrix process found
git status = not a git repository in this workspace
```

## Layer I Boundary

```text
Dynamics survived as the most defensible target.
CWP ontology, NAP primitive status, measured-physiology robustness, and structural mechanism remain unproven.
P7 advanced from readiness to 10-subject engineering QC smoke.
P8 advanced from one-subject ds005795 interface smoke to 3-subject interface smoke.
```
