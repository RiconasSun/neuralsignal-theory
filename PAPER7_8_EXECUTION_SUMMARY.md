# Paper 7-8 Execution Summary

Date: 2026-09-04

Workspace:

```text
C:\Users\85993\Desktop\codebase\neuralsignal institute
```

## Paper 7

Status:

```text
P7_65_FSDEFAULT_CONNECTOMES_64_SUBJECT_PRELIMINARY_MODEL_SMOKE_COMPLETE_100_SUBJECT_HYPOTHESIS_NOT_TESTED
```

Completed:

```text
E0 dataset/toolchain audit
E1 MRtrix ACT/SIFT2 command-plan generation
E8 claim audit
environment recovery audit
HCP structural input audit/download script
checkpointed WSL MRtrix smoke script
ACT/SIFT2 engineering diagnostic
MSMT-FOD readiness validator
100307 ext4 MSMT-CSD diagnostic
100307 final-route ACT/iFOD2/SIFT2 smoke summary
100307/100408/101107 three-subject final-route ACT/iFOD2/SIFT2 smoke
10-subject final-route ACT/iFOD2/SIFT2 connectome QC smoke
10-subject fs_default84 label-conversion connectome QC
100307 20k streamline-count sensitivity
55-subject streaming-batch connectome generation and cleanup
pre-100-subject QC freeze draft
pre-100-subject QC freeze v0.2
64-subject preliminary structural-model interface smoke
final conclusion file
```

Current result:

```text
3-subject structural input audit ready subjects = 3
HCP 100307/100408/101107 FreeSurfer-5TT route inputs = ready
MRtrix3 via WSL micromamba = ready
FreeSurferColorLUT = installed under paper7/resources/
final-route connectome_sift2_ext4_msmt_smoke.csv = generated for 10 smoke subjects
fs_default84 label-converted 84 x 84 connectomes = generated for 10 smoke subjects
fs_default84 load-bearing tck2connectome warnings = cleared for 9/10 smoke subjects
100307 outlier = persists after 20k streamline sensitivity
streaming batch subjects 106016, 108828, 110411, 111312, and 111716 = PASS
streaming batch subjects 113619, 113922, 114419, 115320, and 116524 = PASS
streaming batch subjects 117122, 118528, 118730, 118932, and 120111 = PASS
streaming batch subjects 122317, 122620, 123117, 123925, and 124422 = PASS
streaming batch subjects 125525, 126325, 127630, 127933, and 128127 = PASS
streaming batch subjects 128632, 129028, 130013, 130316, and 131217 = PASS
streaming batch subjects 131722, 133019, 133928, 135225, and 135932 = PASS
streaming batch subjects 136833, 138534, 139637, 140925, and 144832 = PASS
streaming batch subjects 146432, 147737, 148335, 148840, and 149337 = PASS
streaming batch subjects 149539, 149741, 151223, 151526, 151627, 153025, 154734, 156637, 159340, and 160123 = PASS
streaming cleanup = removed large generated intermediates after preserving connectome outputs
available fs_default84 connectomes = 65 subjects
100307 = excluded from primary model analysis by frozen pre-100-subject QC rule
preliminary 64-subject structural-model interface smoke = PASS_PRELIMINARY_STRUCTURAL_MODEL_SMOKE
preliminary smoke gates for true-subject structural superiority = failed
diagnostic single-tissue connectome = generated
MSMT-FOD readiness gate = passed for ext4 FOD + one-subject final-route smoke
```

Environment recovery:

```text
WSL Ubuntu starts and apt lists an mrtrix3 candidate, but sudo installation requires a password.
User-space micromamba was installed and MRtrix3 3.0.8 was installed under WSL.
MRtrix read HCP subject 100307 DWI and generated dwi.mif.
FSL has no candidate in the current WSL apt source list.
Docker CLI is installed, but Docker Desktop did not provide a responsive daemon during autonomous execution.
FreeSurfer 5TT and DWI-grid 5TT were generated for the 10-subject smoke cohort.
MSMT-CSD WM FOD was zero under the original workspace-path smoke for 100307.
Regenerating MSMT-CSD on WSL ext4 produced nonzero FOD and enabled final-route ACT/iFOD2/SIFT2.
Single-tissue CSD was used only as a diagnostic fallback and successfully generated ACT/iFOD2/SIFT2/tck2connectome output.
```

Scientific conclusion:

```text
The Paper 7 high-fidelity ACT/iFOD2/SIFT2 structural hypothesis has not been finally tested. Current work produced a 10-subject engineering QC smoke, a fifty-five-subject streaming-batch extension, and a preliminary 64-subject model-interface smoke. The preliminary smoke did not support true-subject structural superiority, but it does not replace the final 100-subject structural hypothesis test.
```

Key outputs:

```text
paper7/results/CURRENT_RESULTS.md
paper7/results/PAPER7_FINAL_CONCLUSION.md
paper7/results/p7_e0_dataset_toolchain_audit.json
paper7/results/p7_e1_mrtrix_command_plan.json
paper7/results/p7_e1_mrtrix_command_plan.ps1
paper7/results/p7_e8_claim_audit.json
paper7/results/P7_ENVIRONMENT_RECOVERY_AUDIT.md
paper7/results/p7_environment_recovery_audit.json
paper7/results/P7_ACT_SIFT2_ENGINEERING_DIAGNOSTIC.md
paper7/results/p7_act_sift2_engineering_diagnostic.json
paper7/results/p7_final_route_single_subject_smoke.json
paper7/results/p7_e3_three_subject_final_route_smoke.json
paper7/results/p7_e4_ten_subject_connectome_qc.json
paper7/results/p7_e4_ten_subject_connectome_qc_summary.json
paper7/results/p7_e5_labelconvert_connectome_qc.json
paper7/results/p7_e5_100307_streamline_20000_sensitivity.json
paper7/results/p7_e6_streaming_batch_10_2.json
paper7/results/p7_e6_streaming_batch_12_3.json
paper7/results/p7_e6_streaming_batch_15_5.json
paper7/results/p7_e6_streaming_batch_20_5.json
paper7/results/p7_e6_streaming_batch_25_5.json
paper7/results/p7_e6_streaming_batch_30_5.json
paper7/results/p7_e6_streaming_batch_35_5.json
paper7/results/p7_e6_streaming_batch_40_5.json
paper7/results/p7_e6_streaming_batch_45_5.json
paper7/results/p7_e6_streaming_batch_50_5.json
paper7/results/p7_e6_streaming_batch_55_5.json
paper7/results/p7_e6_streaming_batch_60_5.json
paper7/results/p7_e6_streaming_batch_59_1.json
paper7/results/p7_e6_streaming_cleanup_audit.json
paper7/results/p7_e6_available_fsdefault_connectome_summary.json
paper7/results/p7_e7_preliminary_structural_model_smoke.json
paper7/data_manifest/p7_hcp_structural_input_audit.csv
paper7/data_manifest/p7_e4_ten_subject_connectome_qc_summary.csv
paper7/data_manifest/p7_e5_labelconvert_connectome_qc_summary.csv
paper7/data_manifest/p7_e6_streaming_batch_10_2.csv
paper7/data_manifest/p7_e6_streaming_batch_12_3.csv
paper7/data_manifest/p7_e6_streaming_batch_15_5.csv
paper7/data_manifest/p7_e6_streaming_batch_20_5.csv
paper7/data_manifest/p7_e6_streaming_batch_25_5.csv
paper7/data_manifest/p7_e6_streaming_batch_30_5.csv
paper7/data_manifest/p7_e6_streaming_batch_35_5.csv
paper7/data_manifest/p7_e6_streaming_batch_40_5.csv
paper7/data_manifest/p7_e6_streaming_batch_45_5.csv
paper7/data_manifest/p7_e6_available_fsdefault_connectome_summary.csv
paper7/data_manifest/p7_e7_preliminary_structural_model_subject_metrics.csv
paper7/protocol/PAPER7_PRE_100_SUBJECT_QC_FREEZE_DRAFT.md
paper7/protocol/PAPER7_PRE_100_SUBJECT_QC_FREEZE_v0_2.md
paper7/structural_connectomes/mrtrix_act_sift2_smoke/100307/connectome_sift2_ext4_msmt_smoke.csv
paper7/structural_connectomes/mrtrix_act_sift2_smoke/100408/connectome_sift2_ext4_msmt_smoke.csv
paper7/structural_connectomes/mrtrix_act_sift2_smoke/101107/connectome_sift2_ext4_msmt_smoke.csv
paper7/structural_connectomes/mrtrix_act_sift2_smoke/100307/connectome_sift2_ext4_msmt_fsdefault84_smoke.csv
paper7/structural_connectomes/mrtrix_act_sift2_smoke/100307/connectome_sift2_ext4_msmt_fsdefault84_20000_sensitivity.csv
paper7/structural_connectomes/mrtrix_act_sift2_smoke/100307/connectome_sift2_csd_diagnostic.csv
paper7/structural_connectomes/mrtrix_act_sift2_smoke/106016/connectome_sift2_ext4_msmt_fsdefault84_smoke.csv
paper7/structural_connectomes/mrtrix_act_sift2_smoke/108828/connectome_sift2_ext4_msmt_fsdefault84_smoke.csv
```

## Paper 8

Status:

```text
P8_E1_E6_HCP_PHYSIO_SMOKE_RAW_GATE_FAILED
```

Completed:

```text
E0 public dataset and measured-physiology availability audit
E1 HCP WM Physio_log download / existing-file confirmation
E1-E6 HCP WM measured-physiology nuisance ladder smoke
figure generation
P8-v2 signal-separation audit
P8-v2 figure generation
P8-final measured-physiology extension protocol
P8-final ds005795 manifest audit
P8-final ds005795 small physiology/BOLD smoke download
P8-final ds005795 physiology timing parse smoke
P8-final ds005795 TR-aligned physiology feature smoke
P8-final ds005795 three-subject nuisance-ladder interface smoke
E8 claim audit
final conclusion file
one-command reproduction
```

Current data:

```text
18 subjects
36 HCP WM runs
36 HCP WM Physio_log files
288 block-start transition rows
aparc68 cortical transition vectors
```

Primary gate:

```text
SameTransition similarity > DifferentTransition similarity
```

Primary result:

```text
N0 same-transition similarity = 0.926106
N0 different-transition similarity = 0.959254
N0 same-different contrast = -0.033148
subject mean contrast = -0.073271
bootstrap 95% CI = [-0.161751, 0.018574]
subject sign-flip p = 0.934607
Gate A = failed
```

Scientific conclusion:

```text
HCP measured physiology can be acquired and inserted into the Paper 8 nuisance ladder, but the preregistered raw transition-reproducibility contrast was not reproduced in the current 18-subject smoke test. No physiological-survival or neural-origin claim is allowed.
```

Secondary diagnostic:

```text
0-back vs 2-back block-start classification accuracy remained above chance across rungs, ranging from 0.715278 to 0.756944. This does not rescue the primary same-transition reproducibility gate.
```

P8-v2 signal-separation:

```text
N0 ROI classification accuracy = 0.715278 versus label-shuffle mean = 0.494028.
N4 ROI classification accuracy = 0.756944 versus label-shuffle mean = 0.488646.
Primary transition contrast remains unsupported at N0 and N4.
Metadata-only accuracy = 0.625, so timing/domain/run metadata remain a serious competing explanation.
```

Key outputs:

```text
paper8/results/CURRENT_RESULTS.md
paper8/results/PAPER8_FINAL_CONCLUSION.md
paper8/results/p8_e0_public_dataset_physio_audit.json
paper8/results/p8_e1_hcp_wm_physio_download.json
paper8/results/p8_e1_e6_hcp_physio_ladder_smoke.json
paper8/results/p8_v2_signal_separation_audit.json
paper8/results/p8_e8_claim_audit.json
paper8/figures/figure1_p8_nuisance_ladder_transition_contrast.png
paper8/figures/figure2_p8_nuisance_ladder_classification.png
paper8/figures/figure3_p8_v2_transition_nulls.png
paper8/figures/figure4_p8_v2_classification_nulls.png
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
paper8/manuscript/PAPER8_MANUSCRIPT_CURRENT.md
paper8/attachments/
```

P8-final extension current audit:

```text
OpenNeuro ds005795 / NEMAR on005795 selected only as convergent measured-physiology validation.
OpenNeuro GraphQL file-tree audit passed.
subjects = 34
tasks = learning, rest
BOLD files = 80
physio files = 72
EEG files = 302
events files = 78
channels files = 39
three-subject interface smoke = PASS
sub-01/sub-02/sub-03 learning BOLD shape = 112 x 112 x 58 x 816
TR-aligned transition rows = 815
physio columns = time, cardiac, respiratory
mean MSE state only = 258.3504
mean MSE state + cardiac/resp = 235.0614
mean MSE state + metadata = 254.9492
mean MSE state + physiology + metadata = 234.1164
mean R2 state only = 0.4623
mean R2 state + physiology + metadata = 0.5112
```

## Verification

Completed checks:

```text
P7 scripts py_compile: PASS
P8 scripts py_compile: PASS
P7 JSON validation: PASS
P8 JSON validation: PASS
P8 one-command reproduction: completed
P8 figures exist: PASS
```

Repository note:

```text
This workspace is not currently a Git repository, so no commit or push was performed.
```

Layer I current claim boundary:

```text
Reproducible computational cognitive neurodynamics remain the most stable surviving object of the current program. CWP ontology, NAP primitive status, structural grounding, and measured-physiology robustness remain unproven. P7 has an early negative 64-subject structural-model smoke but remains open until the 100-subject test; P8-final remains an open measured-physiology workstream.
```

Claim-boundary file:

```text
LAYER_I_CURRENT_CLAIM_BOUNDARY.md
```
