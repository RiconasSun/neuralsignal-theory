# Paper 2 Attachment Index

Paper: Cross-Dataset Failure and Generalization  
Status: protocol package plus A/B diagnostics and Dataset C final holdout  
Date: 2026-09-01

## Attachments

- A1 Frozen Protocol: `paper2/attachments/A1_Frozen_Protocol.md`
- A2 Dataset Manifest: `paper2/attachments/A2_Dataset_Manifest.md`
- A3 Full Pipeline: `paper2/attachments/A3_Full_Pipeline.md`
- A4 Baseline and Competing-Explanation Results: `paper2/attachments/A4_Baseline_Results.md`
- A5 Holdout Audit: `paper2/attachments/A5_Holdout_Audit.md`
- A6 Statistics: `paper2/attachments/A6_Statistics.md`
- A7 Null and Falsification Tests: `paper2/attachments/A7_Null_Falsification.md`
- A8 QC and Leakage Audit: `paper2/attachments/A8_QC_Leakage_Audit.md`
- A9 Limitations and Failed Analyses: `paper2/attachments/A9_Limitations_Failed_Analyses.md`
- A10 One-Command Reproduction: `paper2/attachments/A10_One_Command_Reproduction.md`

## Current Scientific Status

```text
P2 is frozen as a failure-mechanism study.
E9.0-E9.8 are implemented for Dataset A/B diagnostics.
E9.7 Dataset C final holdout is locked to OpenNeuro ds004469 v1.1.3 and has been evaluated once under the current v2 candidate rules.
Dataset C result: DATASET_C_CWP_SPECIFIC_NOT_SUPPORTED.
```

## Claim Boundary

Allowed:

```text
P2 will test why P1's cross-dataset generalization failed.
P2 reproduced the Paper 1 A -> B external failure.
P2 identified A/B diagnostic candidates for measurement, state-representation, and ontology shift.
P2 tested the frozen v2 candidate on Dataset C and did not obtain CWP-specific support.
```

Disallowed:

```text
P2 has explained the failure.
P2 has rescued CWP.
P2 proves CWP generalizes.
Dataset B is a clean independent holdout.
```

Current results summary:

```text
paper2/results/CURRENT_RESULTS.md
paper2/results/e9_8_claim_audit.json
```
