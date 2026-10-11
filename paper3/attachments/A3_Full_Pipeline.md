# A3 Full Pipeline

Raw state inputs from Paper 1 and Paper 2 are reused:

```text
paper1/state_extraction/stage_states.csv
paper1/external_validation/stage_states_external.csv
paper2/external_holdout/stage_states_dataset_c.csv
```

Pipeline:

```text
state files -> transition vectors T = S_target - S_source
-> E2 within-run split-half reliability
-> E3 cross-run same-subject reliability
-> E4 same-transition vs different-transition contrast
-> E5 dataset-specific reproducibility summary
-> E6 cross-dataset same-vs-different transition similarity
-> E7 label-shuffle null tests
-> E8 statistics and claim audit
```
