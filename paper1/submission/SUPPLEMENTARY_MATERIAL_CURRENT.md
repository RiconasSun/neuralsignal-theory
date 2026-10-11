# Supplementary Materials for Paper 1

This supplement contains the A1-A10 reproducibility attachments generated from the frozen E0-E8 run.

# A1 Frozen Protocol

Paper: Reusable Cognitive Work Primitives Improve Out-of-Task Prediction of Human Brain-State Transitions

Status: frozen protocol implemented and run on downloaded OpenNeuro data.

## Research Question

Do reusable Cognitive Work Primitives (CWP) predict human brain-state transitions better than dataset-specific flat task labels, especially under out-of-distribution holdouts?

## Falsifiable Hypothesis

Primary:

```text
P(S_t+1 | S_t, CWP, Context) > P(S_t+1 | S_t, TaskLabel)
```

Operational gates:

```text
Gate A: M4_task_plus_cwp > M2_strong_task
Gate B: M3_cwp > M2_strong_task on unseen combination/domain
Gate C: external dataset direction is consistent
```

## Frozen Ontology

Primary CWP labels:

- ENCODE
- MAINTAIN
- PROBE

TRANSFORM remains exploratory and is not allowed to support the primary Paper 1 claim.

## Frozen Experiments

- E0 Data/QC Audit
- E1 Brain-State Extraction
- E2 CWP Existence
- E3 Task vs CWP
- E4 Unseen Combination
- E5 Unseen Domain
- E6 Null/Falsification
- E7 External Dataset
- E8 Statistics + Reproduction

## Frozen Models

- M0_state: `S_t+1 = F(S_t)`
- M1_flat_task: `S_t+1 = F(S_t, TaskID)`
- M2_strong_task: `S_t+1 = F(S_t, TaskID, Domain, Load)`
- M3_cwp: `S_t+1 = F(S_t, CWP, Domain, Load)`
- M4_task_plus_cwp: `S_t+1 = F(S_t, TaskID, CWP, Domain, Load)`

## Primary Endpoint

Held-out prediction error / predictive performance on brain-state transitions.

## Secondary Endpoints

- R2
- MSE
- cosine similarity
- subject-level effect size
- bootstrap 95% CI
- sign-flip permutation p-value
- FDR-adjusted q-value

## Current Execution State

Current real-data run:

```text
status: completed through E8 claim audit
Gate A incremental: INCONCLUSIVE
Gate B OOD: PASSED
Gate C external: FAILED
claim_allowed_cwp_foundation_holds: false
```

The strong Paper 1 claim is not supported by the current workspace state.



---

# A2 Dataset Manifest

## Primary Dataset

Dataset id: ds001635

Role: primary CWP discovery and validation against flat task labels.

Current local availability:

```text
events.tsv files: FOUND, 48
BOLD NIfTI files: FOUND, 48
ROI time-series CSV files: FOUND, 48
confounds.tsv files: NOT FOUND
```

Machine audit outputs:

```text
paper1/data_manifest/dataset_manifest.csv
paper1/data_manifest/trial_counts.csv
paper1/data_manifest/qc_subjects.csv
paper1/data_manifest/e0_summary.json
```

E0 observed:

```text
status = PASS
n_events = 48
n_roi_timeseries = 48
n_bold = 48
n_confounds = 0
external_stage_states_present = true
```

## External Holdout Dataset

Dataset id: ds001634

Role: zero-change external validation.

Current local availability:

```text
events.tsv files: FOUND, 57
BOLD NIfTI files: FOUND, 57
external_validation/stage_states_external.csv: FOUND
```

External E1 observed:

```text
states_extracted = 3066
roi_count = 216
```

## Dataset Metadata

ds001635 dataset description reports:

```text
Name: Visual working memory: Study two Task fMRI and Behavioural response
License: Creative Commons Attribution 4.0 International (CC-BY 4.0)
DatasetDOI: 10.18112/openneuro.ds001635.v1.0.1
```

## Local Raw Data Paths

```text
paper1/data_raw/ds001635
paper1/data_raw/ds001634
```

## Caveats

No confounds files were found in the current local pull, so motion-only falsification is not complete.



---

# A3 Full Pipeline

## Implemented Code Path

Common utilities:

```text
paper1/scripts/common.py
```

Experiment scripts:

```text
paper1/scripts/e0_data_qc_audit.py
paper1/scripts/e1_extract_states.py
paper1/scripts/e2_cwp_existence.py
paper1/scripts/e3_task_vs_cwp.py
paper1/scripts/e4_unseen_combination.py
paper1/scripts/e5_unseen_domain.py
paper1/scripts/e6_null_falsification.py
paper1/scripts/e7_external_dataset.py
paper1/scripts/e8_statistics_reproduction.py
```

One-command runner:

```text
paper1/scripts/run_e1_e8.py
```

## Computational Path

```text
OpenNeuro download
-> E0 data/QC audit
-> events.tsv + ROI time-series or BOLD/native grid
-> E1 stage-state extraction
-> stage_states.csv
-> E2 stage sanity check
-> E3 M0-M4 subject holdout
-> E4 leave-one-combination-out
-> E5 unseen-domain holdout
-> E6 available null/falsification tests
-> E7 external dataset test when external states exist
-> E8 statistics and claim audit
```

## Environment

Virtual environment:

```text
paper1/.venv
```

Frozen package list:

```text
paper1/results/environment.lock
```

## Verification Already Performed

Static compile:

```text
paper1\.venv\Scripts\python.exe -m compileall paper1\scripts
status: PASS
```

Synthetic smoke:

```text
paper1\.venv\Scripts\python.exe paper1\scripts\smoke_test_e1_e8.py
status: PASS
```

Synthetic outputs were removed after verification and are not evidence for the scientific claim.

Real-data run:

```text
ds001635 E1 states_extracted: 2291
ds001634 E1 states_extracted: 3066
E8 claim audit: completed_audit_not_claim_validated
```



---

# A4 Full Baseline Results

## Result Status

Real-data baseline results have been generated.

## Output Files

```text
paper1/results/e3_m0_m4_metrics.csv
paper1/results/e4_unseen_combination_metrics.csv
paper1/results/e5_unseen_domain_metrics.csv
paper1/external_validation/e7_external_dataset_metrics.csv
paper1/results/primary_metrics.csv
```

## E3 Subject Holdout Mean MSE

```text
M0_state: 739.9842107977023
M1_flat_task: 651.1084620470139
M2_strong_task: 651.1084916855937
M3_cwp: 673.3670453189366
M4_task_plus_cwp: 651.1084167356842
```

Gate A is inconclusive because the M4 improvement over M2 is tiny and its subject-level CI crosses 0.

## E4 Unseen Combination Mean MSE

```text
M2_strong_task: 1.2930225316211859
M3_cwp: 1.1905904151828643
M4_task_plus_cwp: 1.2001512696937149
```

E4 supports the OOD component of the CWP claim in this run.

## E5 Unseen Domain Mean MSE

```text
M2_strong_task: 1.549553729346369
M3_cwp: 1.5035537034522544
M4_task_plus_cwp: 1.5084872262939564
```

E5 supports the OOD component of the CWP claim in this run.

## E7 External Validation Mean MSE

```text
M0_state: 528.9595753463202
M1_flat_task: 529.0050987946481
M2_strong_task: 529.0031639473207
M3_cwp: 532.1089214151368
M4_task_plus_cwp: 528.9681855141137
```

Gate C failed because M3_cwp did not outperform M2_strong_task on ds001634.

## Claim Boundary

The strong "CWP clearly outperforms task labels" claim is not allowed by the current E8 audit.



---

# A5 Holdout Audit

## Holdouts Implemented

E3:

```text
leave-one-subject-out
```

E4:

```text
leave-one Domain x Load x CWP cell out
```

E5:

```text
leave-one-domain-out
```

E7:

```text
train on ds001635 states, test on ds001634 external states
```

## Current Holdout Status

Real holdout evaluation has been completed for E3, E4, E5, and E7.

## Holdout Results

E3 Gate A:

```text
INCONCLUSIVE
```

E4 unseen combination:

```text
PASSED
```

E5 unseen domain:

```text
PASSED
```

E7 external validation:

```text
FAILED
```

## Access Log

Initial failed run:

```text
date: 2026-09-01
result: failed before E1 completion
error: no events files matched data_manifest\**\*events.tsv
```

Resolution:

```text
Downloaded ds001635 and ds001634 events/BOLD from OpenNeuro.
```

Final run:

```text
date: 2026-09-01
result: E0-E8 completed through claim audit
claim_allowed_cwp_foundation_holds: false
```

## Holdout Caveats

- E7 is a hard failure for the strong claim in the current run.
- E2 sanity check was weak, which makes downstream positive OOD results less interpretable.
- Motion confounds were not available, so the holdout audit is not yet motion-robust.



---

# A6 Statistics

## Implemented Statistical Outputs

E8 writes:

```text
paper1/results/primary_metrics.csv
paper1/results/subject_level_effects.csv
paper1/results/claim_audit.json
```

## Implemented Methods

- subject-level paired comparison where subject-level rows exist
- bootstrap 95% CI
- sign-flip permutation test
- Benjamini-Hochberg FDR correction

## Current Statistical Result

E8 has been run on real downloaded OpenNeuro data.

```text
Gate A incremental: INCONCLUSIVE
Gate B OOD: PASSED
Gate C external: FAILED
claim_allowed_cwp_foundation_holds: false
claim_allowed_cwp_clearly_outperforms_task_labels: false
```

## Interpretation Rule

E8 is the only local script allowed to write the claim audit. Any manuscript conclusion must follow `claim_audit.json`, not isolated metric files.



---

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



---

# A8 QC & Leakage Audit

## Leakage Controls Implemented

- train/test standardization is fit on training rows only
- categorical levels are fit on training metadata only
- E3 holds out subjects
- E4 holds out full condition cells
- E5 holds out full domains
- E7 uses an external stage-state file with identical ROI columns

## Machine QC Evidence

E0 has been implemented and run.

Outputs:

```text
paper1/data_manifest/dataset_manifest.csv
paper1/data_manifest/trial_counts.csv
paper1/data_manifest/qc_subjects.csv
paper1/data_manifest/e0_summary.json
```

Current E0 result:

```text
status: PASS
n_events: 48
n_roi_timeseries: 48
n_bold: 48
n_confounds: 0
external_stage_states_present: true
```

## Remaining QC Gaps

- no confounds files were found, so motion-only null is not complete
- native image-space grid atlas is a reproducible engineering atlas, not a neuroanatomical parcellation
- no checksum inventory is currently written beyond OpenNeuro downloader verification



---

# A9 Limitations & Failed Analyses

## Current Limitations

- Motion-only null requires confounds input.
- Boundary-jitter null requires event perturbation and E1 rerun.
- TRANSFORM is exploratory only and cannot support the primary claim.
- The current run uses a native image-space 216-ROI grid, not a neuroanatomical atlas.
- E2 stage separability was weak under subject holdout.
- E7 external validation failed for the CWP-only model against the strong task baseline.

## Earlier Failed Attempt

An earlier one-command run failed before data download:

```text
ERROR: no events files matched data_manifest\**\*events.tsv
```

Interpretation:

```text
This missing-data blocker was resolved by downloading real OpenNeuro data.
```

## Unsupported Claims

The current workspace does not support:

- CWP is validated.
- CWP clearly outperforms task labels.
- CWP replicates externally.
- TRANSFORM is a valid primary primitive.

## Supported Narrower Observation

The current workspace supports:

- Within ds001635, CWP-style labels outperformed the strong task baseline in E4 unseen-combination and E5 unseen-domain MSE.



---

# A10 One-command Reproduction

## Command

For a complete rerun from downloaded raw data:

```powershell
cd "C:\Users\85993\Desktop\codebase\neuralsignal institute"
cd paper1
.\.venv\Scripts\python.exe scripts\run_e1_e8.py
```

Equivalent explicit commands are:

```powershell
.\.venv\Scripts\python.exe scripts\e1_extract_states.py --events-glob "data_raw\ds001635\**\*events.tsv" --bold-glob "data_raw\ds001635\**\*_bold.nii.gz" --native-grid --grid-bins 6,6,6 --tr 2.0 --hrf-lag 4.0
.\.venv\Scripts\python.exe scripts\e2_cwp_existence.py --states state_extraction\stage_states.csv --split subject
.\.venv\Scripts\python.exe scripts\e3_task_vs_cwp.py --states state_extraction\stage_states.csv
.\.venv\Scripts\python.exe scripts\e4_unseen_combination.py --states state_extraction\stage_states.csv
.\.venv\Scripts\python.exe scripts\e5_unseen_domain.py --states state_extraction\stage_states.csv
.\.venv\Scripts\python.exe scripts\e6_null_falsification.py --states state_extraction\stage_states.csv --permutations 100
.\.venv\Scripts\python.exe scripts\e1_extract_states.py --events-glob "data_raw\ds001634\**\*events.tsv" --bold-glob "data_raw\ds001634\**\*_bold.nii.gz" --native-grid --grid-bins 6,6,6 --tr 2.0 --hrf-lag 4.0 --timeseries-out-dir "external_validation\input_timeseries" --out "external_validation\stage_states_external.csv"
.\.venv\Scripts\python.exe scripts\e7_external_dataset.py --train-states state_extraction\stage_states.csv --external-states external_validation\stage_states_external.csv
.\.venv\Scripts\python.exe scripts\e8_statistics_reproduction.py
```

## Current Reproduction Result

```text
status: completed_audit_not_claim_validated
Gate A incremental: INCONCLUSIVE
Gate B OOD: PASSED
Gate C external: FAILED
```

## Final Outputs

```text
paper1/state_extraction/stage_states.csv
paper1/external_validation/stage_states_external.csv
paper1/results/e2_cwp_existence_metrics.csv
paper1/results/e3_m0_m4_metrics.csv
paper1/results/e4_unseen_combination_metrics.csv
paper1/results/e5_unseen_domain_metrics.csv
paper1/results/e6_null_falsification_metrics.csv
paper1/external_validation/e7_external_dataset_metrics.csv
paper1/results/primary_metrics.csv
paper1/results/subject_level_effects.csv
paper1/results/claim_audit.json
```

## Claim Boundary

The current one-command-equivalent run does not support the strong Paper 1 claim.



---
