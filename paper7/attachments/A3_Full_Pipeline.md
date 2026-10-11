# A3. Full Pipeline

Final computational path:

```text
HCP-YA 2025 dMRI/T1w/FreeSurfer/tfMRI
-> E0 dataset/toolchain audit
-> E1 MRtrix ACT/SIFT2 command-plan generation
-> E1b HCP structural input audit/download
-> E2 WSL MRtrix recovery and one-subject diagnostic
-> E3 three-subject final-route ACT/iFOD2/SIFT2 smoke
-> E4 ten-subject final-route connectome QC smoke
-> E5 fs_default84 label-conversion QC
-> E5 100307 20k streamline-count sensitivity
-> E6 streaming connectome generation through 100 available fs_default84 connectomes
-> E6 cleanup and available-connectome inventory
-> E7 final 99-subject structural hypothesis test
-> E8 claim audit
```

Connectome construction path:

```text
HCP dMRI data.nii.gz + bvals/bvecs
-> mrconvert dwi.mif
-> copy DWI/mask to WSL ext4
-> dwi2response dhollander
-> dwi2fod msmt_csd on WSL ext4
-> 5ttgen freesurfer from aparc+aseg
-> mrtransform 5TT and nodes to DWI/FOD grid
-> 5tt2gmwmi
-> tckgen iFOD2 ACT 5k
-> tcksift2
-> tck2connectome
-> fs_default84 label-converted connectome QC
-> cleanup of raw DWI and large generated intermediates after final connectome preservation
```

Final model path:

```text
load P5 aparc cortical WM fMRI states
load P7 fs_default84 connectomes
exclude 100307 by frozen pre-modeling QC v0.2
map fs_default84 cortical labels to P5 aparc68 cortical state space
normalize connectome rows after log1p weighting
construct graph-projected features G_i S_t
fit no-structure, group-mean, true-subject, swapped, rewired, and distance-only ridge models
evaluate 4TR future-state prediction
compute subject-level delta MSE, bootstrap CI, and sign-flip p-values
write final result JSON, subject metrics CSV, and claim audit
```

Final outputs:

```text
paper7/results/p7_e7_final_structural_hypothesis_test.json
paper7/data_manifest/p7_e7_final_structural_hypothesis_subject_metrics.csv
paper7/results/p7_e8_claim_audit.json
```
