# A4. Full Baseline Results

Status:

```text
COMPLETED_FINAL
```

Final analysis cohort:

```text
100 fs_default84 ACT/iFOD2/SIFT2 connectomes generated
99 subjects included in primary model test
100307 excluded by frozen pre-modeling QC v0.2
```

Final baselines:

```text
M1 no structure
M2 group-mean connectome
M3 true subject connectome
Mswap swapped-subject connectome
Mrewire node-permuted connectome
Mdistance anatomical distance-only graph
```

Final subject-level delta MSE:

```text
M1 - M3 true vs no-structure: mean -0.000032, 95% CI [-0.001609, 0.001723]
M2 - M3 true vs group-mean:   mean -0.000494, 95% CI [-0.000800, -0.000109]
Mswap - M3 true vs swapped:   mean -0.000681, 95% CI [-0.001699, 0.000006]
Mrewire - M3 true vs rewired: mean -0.000822, 95% CI [-0.001854, -0.000040]
Mdistance - M3 true:          mean -0.000116, 95% CI [-0.001730, 0.001633]
```

Interpretation:

```text
Positive delta would support true-subject structural advantage.
The final deltas do not support true-subject structural advantage.
```

Evidence:

```text
paper7/results/p7_e7_final_structural_hypothesis_test.json
paper7/data_manifest/p7_e7_final_structural_hypothesis_subject_metrics.csv
```
