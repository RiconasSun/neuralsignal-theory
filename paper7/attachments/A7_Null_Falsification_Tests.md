# A7. Null and Falsification Tests

Status:

```text
COMPLETED_FINAL
```

Final structural nulls and competing explanations:

```text
group-mean connectome
swapped-subject connectome
node-permuted rewired connectome
anatomical distance-only graph
no-structure baseline
```

Final null results:

```text
true vs group-mean: mean -0.000494, 95% CI [-0.000800, -0.000109]
true vs swapped:    mean -0.000681, 95% CI [-0.001699, 0.000006]
true vs rewired:    mean -0.000822, 95% CI [-0.001854, -0.000040]
true vs distance:   mean -0.000116, 95% CI [-0.001730, 0.001633]
```

Interpretation:

```text
The true-subject connectome did not beat the graph nulls or competing structural explanations.
The final anatomical-specificity gate failed.
Subject-specific structural grounding is not supported under the tested interface.
```

Evidence:

```text
paper7/results/p7_e7_final_structural_hypothesis_test.json
paper7/data_manifest/p7_e7_final_structural_hypothesis_subject_metrics.csv
```
