# A9. Limitations and Failed Analyses

Final limitation:

```text
Paper 7 completed the 100-connectome generation target and the final 99-subject primary structural prediction test, but the tested high-fidelity structural interface did not support subject-specific structural grounding.
```

Completed failed or negative analyses:

```text
100307 20k streamline-count sensitivity: completed; sparse/warning-positive outlier persisted.
preliminary structural-model interface smoke: completed; true-subject superiority not supported.
final 99-subject M1/M2/M3/swap/rewire/distance structural test: completed; all final gates failed.
Gate A true G_i > no structure: failed.
Gate B true G_i > group mean: failed.
Gate C true G_i > swapped/rewired: failed.
Gate C true G_i > distance-only: failed.
```

Important constraints:

```text
The final route used 5,000-streamline engineering tractograms.
The final route used FreeSurfer-5TT because FSL was unavailable.
The connectome was compressed from fs_default84 to the P5 aparc cortical state space.
The tested prediction interface was ridge-regression over macroscopic HCP WM fMRI states.
The negative result is limited to this dataset, representation, tractography density, atlas mapping, lag, and model class.
```

Claims not supported:

```text
subject-specific structural connectivity constrains macroscopic transition prediction
structural mechanism is established
NAP is structurally grounded
CWP is validated
```

Claims still allowed:

```text
100 fs_default84 ACT/iFOD2/SIFT2 connectomes were generated.
The final 99-subject primary structural prediction test was run.
The strong P7 structural-grounding hypothesis was not supported under the tested interface.
```
