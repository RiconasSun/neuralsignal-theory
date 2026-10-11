# A8 QC & Leakage Audit

Paper 3 reuses frozen state files generated before this reproducibility paper. E1 confirms state-file availability, subject/run inventory, primary stage completeness, and transition counts.

Main leakage controls:

```text
No model fitting is used for the primary reliability estimand.
Transition labels are challenged by label-shuffle nulls.
Cross-run estimates exclude run-unknown entries.
Dataset-level estimates are reported separately before cross-dataset aggregation.
```
