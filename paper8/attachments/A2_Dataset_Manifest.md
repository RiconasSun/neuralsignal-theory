# A2. Dataset Manifest

Current outputs:

```text
paper8/dataset_audit/p8_e0_dataset_candidates.csv
paper8/dataset_audit/p8_e0_local_hcp_physio_motion_audit.csv
paper8/dataset_audit/p8_e0_remote_hcp_physio_key_audit.csv
paper8/dataset_audit/p8_final_extension_ds005795_selected_files.csv
paper8/results/p8_e0_public_dataset_physio_audit.json
paper8/results/p8_e1_hcp_wm_physio_download.json
paper8/results/p8_final_extension_ds005795_manifest_audit.json
paper8/results/p8_final_extension_ds005795_streaming_nuisance_ladder.json
```

Primary candidate:

```text
HCP-YA 2025
```

Current local measured-physiology subset:

```text
18 subjects
36 WM runs
36 tfMRI_WM_*_Physio_log.txt files downloaded or confirmed present
36 Movement_Regressors.txt files available for the same runs
288 block-start transition rows
```

External/convergent measured-physiology extension:

```text
OpenNeuro ds005795 / MULTI-CLARID was audited by manifest and used only as a convergent measured-physiology extension.
The extension does not directly replicate HCP working-memory transitions.
```

ds005795 manifest boundary:

```text
Complete task-learning BOLD/physio/events/bold-json bundle available for:
sub-01
sub-02
sub-03
sub-04
sub-05

The audited manifest did not contain the required task-learning four-file bundle for sub-06 through sub-10. The final extension therefore freezes at 5/5 complete available task-learning subjects.
```
