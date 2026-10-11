# Paper 7 Current Results

Status:

```text
FINAL_STRUCTURAL_HYPOTHESIS_NOT_SUPPORTED
```

Paper 7 asks whether the negative Paper 5 structural-proxy result persists when `G_i` is built from high-fidelity ACT/SIFT2 subject-specific connectomes.

Completed implementation:

```text
E0 dataset/toolchain audit
E1 MRtrix ACT/SIFT2 command-plan generation
E2 WSL MRtrix recovery and one-subject route diagnostic
E3 three-subject final-route ACT/iFOD2/SIFT2 smoke
E4 ten-subject final-route connectome QC smoke
E5 fs_default84 label-conversion QC
E5 100307 20k streamline-count sensitivity
E6 100-subject fs_default84 connectome generation via streaming batches
E6 streaming cleanup audit
E6 available-connectome inventory
E7 final 99-subject structural hypothesis test
E8 claim audit
```

Final data state:

```text
100 fs_default84 ACT/iFOD2/SIFT2 connectomes generated
99 subjects entered the primary final model test
100307 excluded by frozen pre-modeling QC v0.2
available nonzero edge counts: min 282, mean 1088.64, max 1180
```

Final model result:

```text
true vs no-structure: mean -0.000032, 95% CI [-0.001609, 0.001723], p_one_sided=0.514
true vs group-mean:   mean -0.000494, 95% CI [-0.000800, -0.000109], p_one_sided=1.000
true vs swapped:      mean -0.000681, 95% CI [-0.001699, 0.000006], p_one_sided=0.956
true vs rewired:      mean -0.000822, 95% CI [-0.001854, -0.000040], p_one_sided=0.975
true vs distance:     mean -0.000116, 95% CI [-0.001730, 0.001633], p_one_sided=0.565
```

Final gates:

```text
Gate A true G_i > no structure: false
Gate B true G_i > group mean: false
Gate C true G_i > swapped/rewired: false
Gate C true G_i > distance-only: false
```

Allowed claim:

```text
Paper 7 generated 100 fs_default84 ACT/iFOD2/SIFT2 connectomes, excluded 100307 by the frozen pre-modeling QC rule, and ran the final 99-subject primary structural prediction analysis. The final gates did not support subject-specific structural grounding under the tested state-prediction interface.
```

Forbidden claims:

```text
Subject-specific structural connectivity constrains brain-state dynamics.
Structural mechanism is established.
NAP is structurally grounded.
CWP is validated.
```
