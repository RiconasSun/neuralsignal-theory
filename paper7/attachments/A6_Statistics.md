# A6. Statistics

Primary statistical unit:

```text
subject
```

Primary estimand:

```text
Delta MSE = MSE(comparator) - MSE(true-subject structural model)
```

Positive delta means the true-subject structural model predicts better than the comparator.

Final analysis:

```text
n_available_connectomes_before_qc_exclusion = 100
n_subjects_primary_analysis = 99
excluded_primary_subjects = 100307
primary_lag = 4 TR = 2.88 seconds
```

Statistical procedures:

```text
subject-level paired contrasts
bootstrap 95% confidence intervals
one-sided sign-flip permutation test for delta > 0
```

Final statistics:

```text
true vs no-structure: mean -0.000032, 95% CI [-0.001609, 0.001723], p_one_sided=0.514
true vs group-mean:   mean -0.000494, 95% CI [-0.000800, -0.000109], p_one_sided=1.000
true vs swapped:      mean -0.000681, 95% CI [-0.001699, 0.000006], p_one_sided=0.956
true vs rewired:      mean -0.000822, 95% CI [-0.001854, -0.000040], p_one_sided=0.975
true vs distance:     mean -0.000116, 95% CI [-0.001730, 0.001633], p_one_sided=0.565
```

Gate result:

```text
Gate A true G_i > no structure: false
Gate B true G_i > group mean: false
Gate C true G_i > swapped/rewired: false
Gate C true G_i > distance-only: false
```

Conclusion:

```text
The final statistics do not support subject-specific structural grounding under the tested interface.
```
