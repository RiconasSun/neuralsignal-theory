# Paper 7 and Paper 8 Closing Routes Status

Date: 2026-09-04

## P7 Route

Status:

```text
P7_65_FSDEFAULT_CONNECTOMES_64_SUBJECT_PRELIMINARY_MODEL_SMOKE_COMPLETE_100_SUBJECT_HYPOTHESIS_NOT_TESTED
```

Paper 7 is not sealed. It has moved beyond readiness and has produced
10-subject final-route engineering `G_i` smoke matrices, a fifty-five-subject
streaming extension, and a preliminary 64-subject structural-model interface
smoke. The preliminary smoke did not support true-subject structural
superiority, but it does not replace the final 100-subject structural
prediction hypothesis test.

Completed now:

```text
HCP 100307/100408/101107/101309/101915/103111/103414/103818/105014/105115 FreeSurfer-5TT route inputs ready
WSL user-space MRtrix3 working
FreeSurferColorLUT fixed and frozen under paper7/resources/
mrconvert completed
dwi2response completed
initial workspace-path MSMT-CSD WM FOD was zero for 100307
ext4-regenerated MSMT-CSD WM FOD is nonzero
5ttgen freesurfer completed
5TT and aparc+aseg resampled to DWI/FOD grid
5tt2gmwmi completed
diagnostic single-tissue CSD + ACT/iFOD2 + SIFT2 + tck2connectome completed
100307/100408/101107 final-route ACT/iFOD2 + SIFT2 + tck2connectome smoke completed
10-subject final-route ACT/iFOD2 + SIFT2 + tck2connectome QC completed
10-subject fs_default84 label-conversion connectome QC completed
100307 20k streamline sensitivity completed; outlier warning persisted
106016/108828/110411/111312/111716/113619/113922/114419/115320/116524/117122/118528/118730/118932/120111/122317/122620/123117/123925/124422/125525/126325/127630/127933/128127 streaming-batch final-route and fs_default84 connectomes completed
streaming cleanup removed large generated intermediates and newly downloaded raw DWI where applicable
MSMT-FOD readiness validator passes for ext4 FOD and one-subject final-route smoke
preliminary 64-subject M1/M2/M3/swap/rewire/distance structural-model interface smoke completed after excluding 100307
```

Important boundary:

```text
The diagnostic single-tissue connectome proves the MRtrix back half can execute.
It is not the frozen P7 final-route MSMT-CSD connectome.
```

Current P7 blocker:

```text
Pre-100-subject QC freeze v0.2 now handles 100307 and cleanup policy.
Run a larger streaming batch QC or proceed under frozen batch-size/runtime policy.
The 64-subject preliminary structural prediction smoke has run and did not support true-subject structural superiority.
The final 100-subject structural prediction comparison has not been run.
```

Next P7 order:

```text
scale fs_default84 connectome generation under frozen QC/cleanup policy
-> 100 subject frozen structural hypothesis test with no-structure/group/true/swap/rewire/distance comparisons
```

## P8 Route

Status:

```text
P8_V2_FROZEN_NEGATIVE_RESULT_PLUS_P8_FINAL_EXTENSION_THREE_SUBJECT_INTERFACE_SMOKE_READY
```

The current P8 v2 result remains frozen:

```text
PRIMARY TRANSITION FAILED
METADATA CONFOUND IDENTIFIED
```

New measured-physiology extension:

```text
OpenNeuro ds005795 / NEMAR on005795 selected as convergent physiological validation.
```

Generated now:

```text
paper8/extensions/measured_physio_final/P8_FINAL_EXTENSION_PROTOCOL_v0_1.md
paper8/extensions/measured_physio_final/EXTENSION_INDEX.md
paper8/results/p8_final_extension_ds005795_manifest_audit.json
paper8/results/p8_final_extension_ds005795_smoke_download.json
paper8/results/p8_final_extension_ds005795_physio_parse_smoke.json
paper8/results/p8_final_extension_ds005795_physio_feature_smoke.json
paper8/results/p8_final_extension_ds005795_nuisance_ladder_smoke.json
paper8/dataset_audit/p8_final_extension_ds005795_selected_files.csv
paper8/state_extraction/ds005795_physio_extension/p8_ds005795_sub01_learning_physio_tr_features.csv
paper8/state_extraction/ds005795_physio_extension/p8_ds005795_sub02_learning_physio_tr_features.csv
paper8/state_extraction/ds005795_physio_extension/p8_ds005795_sub03_learning_physio_tr_features.csv
```

Audit result:

```text
34 subjects
learning/rest tasks
80 BOLD files
72 physiology files
302 EEG files
78 events files
39 channel files
three-subject interface smoke PASS
sub-01/sub-02/sub-03 learning BOLD shape 112 x 112 x 58 x 816
TR-aligned transition rows 815
physio columns time, cardiac, respiratory
mean MSE state only 258.3504
mean MSE state + cardiac/resp 235.0614
mean MSE state + metadata 254.9492
mean MSE state + physiology + metadata 234.1164
```

Important boundary:

```text
ds005795 is not a direct Encode/Maintain/Probe replication dataset.
It is only a convergent physiological-control extension.
```

Next P8 order:

```text
expand ds005795 from three-subject smoke to a locked multi-subject subset
-> implement full nuisance ladder beyond global-signal smoke
-> include metadata-only as formal baseline
-> test whether same-transition structure survives measured physiology
```
