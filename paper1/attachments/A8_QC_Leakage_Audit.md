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
