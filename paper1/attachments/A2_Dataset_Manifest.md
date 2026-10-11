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
