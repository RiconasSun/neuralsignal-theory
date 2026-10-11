# A4 Full Baseline Results

## Result Status

Real-data baseline results have been generated.

## Output Files

```text
paper1/results/e3_m0_m4_metrics.csv
paper1/results/e4_unseen_combination_metrics.csv
paper1/results/e5_unseen_domain_metrics.csv
paper1/external_validation/e7_external_dataset_metrics.csv
paper1/results/primary_metrics.csv
```

## E3 Subject Holdout Mean MSE

```text
M0_state: 739.9842107977023
M1_flat_task: 651.1084620470139
M2_strong_task: 651.1084916855937
M3_cwp: 673.3670453189366
M4_task_plus_cwp: 651.1084167356842
```

Gate A is inconclusive because the M4 improvement over M2 is tiny and its subject-level CI crosses 0.

## E4 Unseen Combination Mean MSE

```text
M2_strong_task: 1.2930225316211859
M3_cwp: 1.1905904151828643
M4_task_plus_cwp: 1.2001512696937149
```

E4 supports the OOD component of the CWP claim in this run.

## E5 Unseen Domain Mean MSE

```text
M2_strong_task: 1.549553729346369
M3_cwp: 1.5035537034522544
M4_task_plus_cwp: 1.5084872262939564
```

E5 supports the OOD component of the CWP claim in this run.

## E7 External Validation Mean MSE

```text
M0_state: 528.9595753463202
M1_flat_task: 529.0050987946481
M2_strong_task: 529.0031639473207
M3_cwp: 532.1089214151368
M4_task_plus_cwp: 528.9681855141137
```

Gate C failed because M3_cwp did not outperform M2_strong_task on ds001634.

## Claim Boundary

The strong "CWP clearly outperforms task labels" claim is not allowed by the current E8 audit.
