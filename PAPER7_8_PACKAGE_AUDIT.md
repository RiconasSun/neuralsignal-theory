# Paper 7-8 Package Audit

Date: 2026-09-04

Audit standard:

```text
NSI Paper Builder A1-A10 reproducibility package:
Hypothesis -> Dataset -> Frozen Pipeline -> Baselines/Competing Explanations -> Holdout -> Statistics -> Null/Falsification -> QC/Leakage -> Limitations -> One-command Reproduction
```

## Paper 7

Package status:

```text
AUDITABLE_35_CONNECTOME_ENGINEERING_QC_COMPLETE
```

Audit:

| Component | Status | Evidence |
|---|---|---|
| Hypothesis | PASS | `paper7/protocol/PAPER7_FROZEN_PROTOCOL_v0_1.md` |
| Dataset manifest | PASS_FOR_SMOKE | `paper7/data_manifest/p7_hcp_structural_input_audit.csv`; 10 complete smoke subjects ready plus 40 streaming-batch subjects |
| Frozen pipeline | PASS | `paper7/protocol/PAPER7_FROZEN_PROTOCOL_v0_1.md`; `paper7/results/p7_e1_mrtrix_command_plan.json` |
| Baselines / competing models | PRELIMINARY_SMOKE_NOT_FINAL | 64-subject no-structure, group-mean, true-subject, swapped, rewired, and distance-only interface smoke has run; final 100-subject comparison not run |
| Holdout | PLANNED_NOT_RUN | 100-subject frozen holdout not run |
| Statistics | PRELIMINARY_SMOKE_NOT_FINAL | 64-subject paired delta MSE summaries exist; final 100-subject structural statistics not run |
| Null / falsification | PRELIMINARY_SMOKE_NOT_FINAL | swapped, rewired, group-mean, and distance-only preliminary smoke comparisons exist; final 100-subject nulls not run |
| QC / leakage | PASS_FOR_READINESS | `paper7/results/p7_e0_dataset_toolchain_audit.json`; `paper7/results/P7_ENVIRONMENT_RECOVERY_AUDIT.md`; `paper7/results/p7_e4_ten_subject_connectome_qc_summary.json`; `paper7/results/p7_e5_labelconvert_connectome_qc.json`; `paper7/results/p7_e6_streaming_batch_10_2.json`; `paper7/results/p7_e6_streaming_batch_12_3.json`; `paper7/results/p7_e6_streaming_batch_15_5.json`; `paper7/results/p7_e6_streaming_batch_20_5.json`; `paper7/results/p7_e6_streaming_batch_25_5.json`; `paper7/results/p7_e6_streaming_batch_30_5.json`; `paper7/results/p7_e6_streaming_cleanup_audit.json`; `paper7/protocol/PAPER7_PRE_100_SUBJECT_QC_FREEZE_v0_2.md` |
| Engineering diagnostic | PASS_FOR_SMOKE | `paper7/results/p7_final_route_single_subject_smoke.json`; `paper7/results/p7_e3_three_subject_final_route_smoke.json`; `paper7/results/p7_e4_ten_subject_connectome_qc.json`; `paper7/results/p7_e6_streaming_batch_10_2.json`; `paper7/results/p7_e6_streaming_batch_12_3.json`; `paper7/results/p7_e6_streaming_batch_15_5.json`; `paper7/results/p7_e6_streaming_batch_20_5.json`; `paper7/results/p7_e6_streaming_batch_25_5.json`; `paper7/results/p7_e6_streaming_batch_30_5.json`; 10-subject final-route ACT/iFOD2/SIFT2 QC plus 25-subject streaming extension completed |
| Limitations / failed analyses | PASS | `paper7/attachments/A9_Limitations_Failed_Analyses.md`; `paper7/results/PAPER7_FINAL_CONCLUSION.md` |
| One-command reproduction | PASS_FOR_SMOKE | `paper7/scripts/reproduce-paper7.ps1` includes 3-subject smoke, 10-subject QC, label-conversion QC, 100307 sensitivity, streaming-batch script, and claim audit |

Allowed conclusion:

```text
Paper 7 is a complete auditable 65-connectome engineering QC package when counting the 10-subject smoke cohort plus the 55-subject streaming-batch extension. WSL MRtrix3 was recovered and final-route ACT/iFOD2/SIFT2 connectomes can be generated without retaining every raw DWI locally, but this is not a completed structural hypothesis paper. The 100307 label-conversion outlier is now handled by a frozen pre-modeling exclusion rule before 100-subject modeling, and the 64-subject preliminary model-interface smoke did not support true-subject structural superiority.
```

## Paper 8

Package status:

```text
AUDITABLE_SMOKE_RESULT_PACKAGE_COMPLETE
```

Audit:

| Component | Status | Evidence |
|---|---|---|
| Hypothesis | PASS | `paper8/protocol/PAPER8_FROZEN_PROTOCOL_v0_1.md` |
| Dataset manifest | PASS | `paper8/results/p8_e0_public_dataset_physio_audit.json`; `paper8/results/p8_e1_hcp_wm_physio_download.json` |
| Frozen pipeline | PASS | `paper8/scripts/paper8_e1_e6_hcp_physio_ladder.py`; `paper8/attachments/A3_Full_Pipeline.md` |
| Competing explanations | PARTIAL_RUN | motion, respiration, cardiac/pulse, combined nuisance ladder completed in HCP smoke; ds005795 3-subject global-signal physiology/metadata interface smoke completed |
| Holdout | PASS_FOR_SMOKE | leave-one-run-out across 36 HCP WM runs |
| Statistics | PASS_FOR_SMOKE | subject-level bootstrap CI and sign-flip p reported |
| Null / falsification | PARTIAL_RUN | measured nuisance ladder plus P8-v2 label-shuffle/domain-preserving/pseudo-ontology/metadata diagnostics completed; random-window/phase/timing nulls not completed |
| QC / leakage | PASS_FOR_SMOKE | matched run files required; credentials not printed |
| Limitations / failed analyses | PASS | raw gate failure and forbidden claims documented |
| One-command reproduction | PASS | `paper8/scripts/reproduce-paper8.ps1` covers E0/E1/E1-E6/figures/E8 and ds005795 3-subject extension smoke |

Allowed conclusion:

```text
Paper 8 is a complete auditable measured-physiology smoke-result package. It does not support physiological-survival or neural-origin claims.
```

P8-v2 addendum:

```text
Signal-separation audit added label-shuffle, domain-preserving shuffle, pseudo-ontology contrast, and metadata-only diagnostics for N0 and N4. It supports secondary condition-classification signal but not primary transition reproducibility.
```

P8-final measured-physiology extension:

```text
OpenNeuro ds005795 / NEMAR on005795 was audited through OpenNeuro GraphQL after the NEMAR direct manifest returned HTTP 403.
sub-01/sub-02/sub-03 learning BOLD, events, and cardiac/respiratory physio files were downloaded.
TR-aligned physiology feature tables were generated for all three smoke subjects.
The 3-subject global-signal nuisance-ladder interface smoke passed.
Mean MSE improved from 258.3504 for state-only to 235.0614 with cardiac/respiratory terms and 234.1164 with physiology plus metadata.
This remains an interface smoke only; it is not physiology-robust transition evidence.
```

## Global Claim Boundary

Forbidden across P7/P8:

```text
CWP validated
NAP validated
structural mechanism established
physiology eliminated
neural origin proven
```

Current Layer I program claim:

```text
Reproducible computational cognitive neurodynamics remain. CWP ontology, NAP primitive status, structural grounding, and measured-physiology robustness remain unproven.
```
