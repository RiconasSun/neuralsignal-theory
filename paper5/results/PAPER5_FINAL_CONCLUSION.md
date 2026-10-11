# Paper 5 Final Conclusion

## Status

```text
P5_HCP_YA_2025_STRUCTURAL_PROXY_TEST_COMPLETE
```

Paper 5 has been completed as a constrained HCP-YA 2025 structural-proxy test.

## What Was Actually Done

```text
1. HCP-YA / BALSA access was completed.
2. 100 Unrelated Subjects were locked for the current analysis.
3. WM LR/RL task-fMRI states were extracted for 100 subjects.
4. Measured movement regressors were residualized.
5. Subject-level aparc68 structural proxy matrices were generated from HCP BedpostX dyads.
6. M1/M2/M3/swap/rewire predictive models were run.
7. Subject-level bootstrap and sign-flip statistics were generated.
8. Claim audit was updated to block unsupported structural/CWP claims.
```

## Core Result

The strong Paper 5 hypothesis was **not supported**:

```text
P(S_(t+tau) | S_t, G_i) > P(S_(t+tau) | S_t)
```

was not observed under the current cortical aparc68 / BedpostX dyad proxy pipeline.

## Gate Results

| Gate | Result |
| --- | --- |
| Gate A: true `G_i` beats no-structure | FAIL |
| Gate B: true `G_i` beats group mean | FAIL |
| Gate C: true `G_i` beats swapped / rewired nulls | FAIL |
| Gate D: locked replication | FAIL / not claimable |

## Key Numbers

Positive delta MSE means true subject `G_i` improved prediction.

| Comparison | Mean delta MSE | 95% CI | p |
| --- | ---: | --- | ---: |
| True `G_i` vs no structure | -0.0000119337 | [-0.0012328103, 0.0014825392] | 0.5090490951 |
| True `G_i` vs group mean | 0.0006467056 | [-0.0001641625, 0.0017230160] | 0.1247875212 |
| True `G_i` vs swapped subject | -0.0000151163 | [-0.0001028483, 0.0000722391] | 0.6303369663 |
| True `G_i` vs rewired | -0.0010285813 | [-0.0020635382, -0.0002784207] | 0.9986001400 |

## Allowed Interpretation

```text
In a 100-subject HCP-YA 2025 WM analysis using cortical aparc68 states and a BedpostX dyad structural proxy, true subject structural proxies did not provide reliable additional prediction of macroscopic brain-state transitions.
```

## Forbidden Interpretation

```text
Subject-specific structural connectivity constrains brain-state dynamics.
CWP/NAP structural grounding is established.
All Paper 5 gates passed.
This is a gold-standard ACT/SIFT2 tractography result.
```

## Main Evidence Files

```text
paper5/results/CURRENT_RESULTS.md
paper5/manuscript/PAPER5_MANUSCRIPT_CURRENT.md
paper5/attachments/A9_HCP_Structural_Proxy_Final_Results.md
paper5/results/e8_claim_audit.json
paper5/results/paper5_e4_e8_structural_proxy_results.json
paper5/results/paper5_e4_connectome_proxy_qc.csv
paper5/results/paper5_e4_e7_structural_proxy_subject_metrics.csv
paper5/results/figures/paper5_e4_e7_structural_proxy_comparisons.png
paper5/results/figures/paper5_e4_e7_model_mse_boxplot.png
```

## Reproduction

```powershell
.\paper5\scripts\reproduce-paper5.ps1
```

This requires authorized HCP/BALSA credentials already configured locally.
