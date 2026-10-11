# A9. HCP Structural Proxy Final Results

## Scope

This attachment records the completed Paper 5 HCP-YA 2025 structural proxy analysis.

```text
Dataset: HCP-YA 2025 / HCP_1200
Cohort: 100 Unrelated Subjects
Task: Working Memory tfMRI LR/RL
State representation: cortical aparc68 parcel states
Structural representation: subject-level BedpostX dyad1 endpoint-propagation proxy
Primary transition lag: 4 TR = 2.88 s
```

This is not an ACT/SIFT2 gold-standard connectome analysis. It is a real subject-level diffusion-derived proxy analysis designed to test whether adding person-specific structural information improves held-out prediction of macroscopic brain-state transitions.

## Generated Artifacts

```text
paper5/results/hcp_smoke_validate.json
paper5/results/hcp_e2_e3_smoke_states.json
paper5/results/paper5_e4_e8_structural_proxy_results.json
paper5/results/paper5_e4_connectome_proxy_qc.csv
paper5/results/paper5_e4_e7_structural_proxy_subject_metrics.csv
paper5/results/figures/paper5_e4_e7_structural_proxy_comparisons.png
paper5/results/figures/paper5_e4_e7_model_mse_boxplot.png
paper5/hcp_connectomes/bedpostx_dyad_proxy/
```

## E2-E3 Summary

The fMRI state extraction and no-structure baseline completed successfully.

```text
n_subjects_processed: 100
n_errors: 0
mean held-out R2: 0.1145682687
median held-out R2: 0.1085043946
mean MSE improvement vs mean-state null: 0.0714343156
```

## E4 Connectome Proxy QC

```text
connectome files generated: 100
mean path success rate: 0.7198786765
median path success rate: 0.7208333333
mean matrix density: 0.1427589991
median matrix density: 0.1427787533
```

## E4-E7 Model Comparison

Positive delta MSE means true subject `G_i` improved prediction relative to the comparator.

| Comparison | Mean delta MSE | 95% CI | Positive subjects | Sign-flip p |
| --- | ---: | --- | ---: | ---: |
| M3 true vs M1 no structure | -0.0000119337 | [-0.0012328103, 0.0014825392] | 19 / 100 | 0.5090490951 |
| M3 true vs M2 group mean | 0.0006467056 | [-0.0001641625, 0.0017230160] | 31 / 100 | 0.1247875212 |
| M3 true vs Mswap | -0.0000151163 | [-0.0001028483, 0.0000722391] | 53 / 100 | 0.6303369663 |
| M3 true vs Mrewire | -0.0010285813 | [-0.0020635382, -0.0002784207] | 40 / 100 | 0.9986001400 |

## Gate Decision

| Gate | Decision |
| --- | --- |
| Gate A: `M3 > M1` | FAIL |
| Gate B: `M3 > M2` | FAIL |
| Gate C: `M3 > swapped / rewired nulls` | FAIL |
| Gate D: locked replication | FAIL / not claimable |

## Conclusion

The current Paper 5 structural proxy analysis does **not** support the strong subject-specific structural-constraint hypothesis.

The correct paper framing is:

```text
HCP-YA data access, state extraction, and subject-level diffusion-derived structural proxy modeling were completed, but true subject structural proxies did not provide reliable additional prediction of macroscopic WM brain-state transitions.
```

The result should be treated as a constrained negative test of the current representation, not as proof that anatomical structure never constrains cognition. A gold-standard ACT/SIFT2 connectome analysis remains a separate stronger test.
