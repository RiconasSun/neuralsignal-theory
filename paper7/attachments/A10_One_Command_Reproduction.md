# A10. One-command Reproduction

Command:

```powershell
.\paper7\scripts\reproduce-paper7.ps1
```

Implemented scope:

```text
E0 HCP-YA dataset/toolchain audit
E1 MRtrix ACT/SIFT2 command-plan generation
E1b HCP structural input audit/download
E2 checkpointed WSL MRtrix ACT/iFOD2/SIFT2 smoke
E3 three-subject final-route ACT/iFOD2/SIFT2 smoke
E4 ten-subject final-route ACT/iFOD2/SIFT2 connectome QC smoke
E4 ten-subject connectome QC summary
E5 fs_default84 label-conversion connectome QC
E5 100307 20k streamline-count sensitivity
E6 streaming connectome batches through 100 available connectomes
E6 streaming cleanup audit
E6 available fs_default84 connectome summary
E7 preliminary structural-model interface smoke
E7 final 99-subject structural hypothesis test
P7 final figure generation
P7 manuscript PDF preview generation
E8 claim audit
```

Expected behavior:

```text
If MRtrix3 or required HCP files are unavailable, the command records the exact blocker and continues to write the E1 command plan and E8 claim audit.
If prior smoke or final outputs already exist, the command reuses them through explicit skipped-existing-output records.
The command must not silently substitute the Paper 5 BedpostX proxy for the high-fidelity P7 G_i.
The final E7 step writes paper7/results/p7_e7_final_structural_hypothesis_test.json and paper7/data_manifest/p7_e7_final_structural_hypothesis_subject_metrics.csv.
```

Final reproducibility artifacts:

```text
paper7/results/p7_e6_available_fsdefault_connectome_summary.json
paper7/results/p7_e6_streaming_cleanup_audit.json
paper7/results/p7_e7_final_structural_hypothesis_test.json
paper7/results/p7_final_figures.json
paper7/results/p7_manuscript_pdf.json
paper7/results/p7_e8_claim_audit.json
paper7/data_manifest/p7_e7_final_structural_hypothesis_subject_metrics.csv
paper7/figures/paper7_final_structural_hypothesis_delta_mse.png
paper7/figures/paper7_final_structural_hypothesis_delta_mse.svg
paper7/output/pdf/paper7_manuscript_preview.pdf
```
