# Paper 8 Package Index

Status:

```text
P8_E1_E6_HCP_PHYSIO_SMOKE_RAW_GATE_FAILED
```

Core question:

```text
Do P3/P4 reproducible macro transitions survive true measured motion, respiration, cardiac/pulse, tissue, and timing nuisance controls?
```

Current package:

```text
paper8/protocol/PAPER8_FROZEN_PROTOCOL_v0_1.md
paper8/scripts/paper8_e0_public_dataset_physio_audit.py
paper8/scripts/paper8_e1_download_hcp_wm_physio.py
paper8/scripts/paper8_e1_e6_hcp_physio_ladder.py
paper8/scripts/make_paper8_figures.py
paper8/scripts/paper8_v2_signal_separation_audit.py
paper8/scripts/make_paper8_v2_figures.py
paper8/scripts/paper8_final_extension_ds005795_manifest_audit.py
paper8/scripts/paper8_final_extension_ds005795_streaming_ladder.py
paper8/scripts/make_paper8_ds005795_streaming_figure.py
paper8/scripts/paper8_make_manuscript_pdf.py
paper8/scripts/write_paper8_claim_audit.py
paper8/scripts/reproduce-paper8.ps1
paper8/results/CURRENT_RESULTS.md
paper8/results/PAPER8_SUBMISSION_READINESS.md
paper8/results/p8_e0_public_dataset_physio_audit.json
paper8/results/p8_e1_hcp_wm_physio_download.json
paper8/results/p8_e1_e6_hcp_physio_ladder_smoke.json
paper8/results/p8_v2_signal_separation_audit.json
paper8/results/p8_final_extension_ds005795_manifest_audit.json
paper8/results/p8_final_extension_ds005795_streaming_nuisance_ladder.json
paper8/results/p8_e8_claim_audit.json
paper8/figures/figure1_p8_nuisance_ladder_transition_contrast.png
paper8/figures/figure2_p8_nuisance_ladder_classification.png
paper8/figures/figure3_p8_v2_transition_nulls.png
paper8/figures/figure4_p8_v2_classification_nulls.png
paper8/figures/figure5_p8_ds005795_streaming_nuisance_ladder.png
paper8/output/pdf/paper8_manuscript_preview.pdf
paper8/manuscript/PAPER8_MANUSCRIPT_CURRENT.md
paper8/attachments/A1_Frozen_Protocol.md
paper8/attachments/A2_Dataset_Manifest.md
paper8/attachments/A3_Full_Pipeline.md
paper8/attachments/A4_Competing_Explanation_Results.md
paper8/attachments/A5_Holdout_Audit.md
paper8/attachments/A6_Statistics.md
paper8/attachments/A7_Null_Falsification_Tests.md
paper8/attachments/A8_QC_Leakage_Audit.md
paper8/attachments/A9_Limitations_Failed_Analyses.md
paper8/attachments/A10_One_Command_Reproduction.md
```

Current allowed claim:

```text
Paper 8 found HCP WM measured physiology files and ran an 18-subject / 36-run measured-physiology ladder smoke, but the preregistered raw SameTransition > DifferentTransition gate was not reproduced. No physiological-survival claim is allowed.
```

P8-v2 allowed claim:

```text
The secondary 0/2-back condition-classification signal exceeds simple label-shuffle nulls in this HCP smoke set, but the primary same-transition reproducibility endpoint remains unsupported.
```

P8-final ds005795 streaming extension:

```text
Status = PASS_DS005795_STREAMING_NUISANCE_LADDER
Scope = all manifest-available task-learning subjects with complete BOLD/physio/events/bold-json files: sub-01 through sub-05.
Result = physiology plus metadata improved global BOLD signal prediction relative to state-only prediction.
Boundary = convergent measured-physiology nuisance relevance only; not direct HCP WM transition replication and not a rescue of the failed primary gate.
```

Current forbidden claims:

```text
physiology eliminated
motion fully excluded
neural origin proven
CWP validated
NAP validated
P8 ds005795 extension directly replicates HCP working-memory transitions
```
