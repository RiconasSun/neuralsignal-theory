# A8. QC and Leakage Audit

Status:

```text
COMPLETED_FINAL
```

Implemented checks:

```text
local HCP subject inventory
required DWI/T1w/tfMRI/motion file presence
MRtrix3 command availability
FSL command availability
FreeSurferColorLUT availability
one-subject WSL MRtrix recovery
three-subject final-route ACT/iFOD2/SIFT2 smoke
ten-subject ACT/iFOD2/SIFT2 smoke connectome QC
ten-subject fs_default84 label-conversion QC
100307 20k streamline-count sensitivity
100-subject streaming connectome generation and cleanup
100-subject available fs_default84 connectome inventory
99-subject final structural-model test after frozen QC exclusion
claim-boundary audit
```

Final QC outputs:

```text
paper7/protocol/PAPER7_PRE_100_SUBJECT_QC_FREEZE_v0_2.md
paper7/results/p7_e6_available_fsdefault_connectome_summary.json
paper7/results/p7_e6_streaming_cleanup_audit.json
paper7/results/p7_e7_final_structural_hypothesis_test.json
paper7/results/p7_e8_claim_audit.json
paper7/data_manifest/p7_e7_final_structural_hypothesis_subject_metrics.csv
```

Final QC findings:

```text
100 fs_default84 ACT/iFOD2/SIFT2 connectomes were generated.
The available-connectome inventory passed.
Streaming cleanup preserved final connectome outputs and removed large intermediates.
100307 remained a warning-positive sparse outlier after fs_default84 conversion and 20k streamline sensitivity.
100307 was excluded by the frozen pre-modeling QC v0.2 rule before final model interpretation.
99 subjects entered the final primary structural prediction model test.
```

Leakage controls:

```text
subject is the statistical unit
frozen QC exclusion applied before final model interpretation
group-mean connectome built only from the analysis connectome set
swapped-subject and rewired baselines explicitly test subject identity and graph-specific explanations
distance-only baseline tests whether anatomical geometry alone explains any apparent structure advantage
claim audit blocks CWP validation, NAP structural grounding, and subject-specific structural-grounding claims after failed gates
```

Residual risks:

```text
5,000-streamline engineering connectomes are not dense production-scale tractograms.
FreeSurfer-5TT route was used because FSL was unavailable.
fs_default84-to-aparc68 mapping compresses structural information into the P5 state space.
The fMRI state representation and ridge interface may be insensitive to structural effects that require different temporal, nonlinear, or biophysical models.
```
