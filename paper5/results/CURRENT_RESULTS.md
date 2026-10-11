# Paper 5 Current Results

Status:

```text
P5_HCP_YA_2025_STRUCTURAL_PROXY_TEST_COMPLETE
```

Paper 5 has now moved beyond the earlier feasibility audit. HCP-YA data access was completed through BALSA/ConnectomeDB, AWS S3 access was configured locally, the 100 Unrelated Subjects package was downloaded in the minimal form required for the current pipeline, and E2-E8 were run on real HCP-YA 2025 subject data.

The central structural claim is **not supported** in the current analysis:

```text
True subject-specific structural proxy G_i did not outperform no-structure, group-mean, swapped-subject, or rewired structural alternatives.
```

This is a constrained negative result, not a data-access blocker.

## Data And Cohort

```text
Dataset: HCP-YA 2025 / HCP_1200 public S3 distribution
Subject group: 100 Unrelated Subjects
Subjects processed in E2-E8: 100
Task: Working Memory tfMRI LR/RL
State representation: cortical aparc68 CIFTI parcel means
Motion handling: measured HCP Movement_Regressors.txt residualized before state modeling
Primary lag: 4 TR = 2.88 s
```

Local data and access evidence:

```text
paper5/data_hcp_ya_2025/hcp_ya_2025_100_unrelated_subjects_browser_manifest.csv
paper5/data_hcp_ya_2025/hcp_ya_2025_100_unrelated_package_manifest.csv
paper5/results/balsa_hcp_browser_access_state.json
paper5/results/balsa_hcp_s3_access_redacted.json
paper5/results/hcp_s3_download_summary.json
paper5/results/hcp_smoke_validate.json
```

## E2-E3 State Extraction / No-Structure Baseline

E2/E3 passed on the 100-subject cohort.

```text
n_subjects_processed: 100
n_errors: 0
mean held-out R2: 0.1145682687
median held-out R2: 0.1085043946
mean MSE improvement vs mean-state null: 0.0714343156
```

Evidence:

```text
paper5/results/hcp_e2_e3_smoke_states.json
paper5/state_extraction/hcp_smoke/
```

Interpretation:

```text
Macroscopic WM brain-state transition prediction is measurable after motion residualization. This does not test the structural hypothesis by itself.
```

## E4 Structural Connectome Proxy

Because the local environment does not include a full MRtrix ACT/SIFT2 tractography stack, the completed E4-E8 analysis used a frozen structural proxy:

```text
Method: BedpostX dyad1 endpoint-propagation proxy
Atlas: cortical aparc68, aligned to the fMRI state order
Seeds: 60 per parcel
Max steps: 96 voxels
Step size: 1 voxel
Subjects: 100
```

QC:

```text
mean path success rate: 0.7198786765
median path success rate: 0.7208333333
mean matrix density: 0.1427589991
median matrix density: 0.1427787533
connectome files generated: 100
```

Evidence:

```text
paper5/hcp_connectomes/bedpostx_dyad_proxy/
paper5/results/paper5_e4_connectome_proxy_qc.csv
```

Limitation:

```text
This is a real subject-level structural proxy from HCP diffusion BedpostX outputs, but it is not gold-standard ACT/SIFT2 tractography.
```

## E4-E7 Model Results

Models:

```text
M1: S_t -> S_(t+4TR)
M2: S_t + group-mean G S_t -> S_(t+4TR)
M3: S_t + true subject G_i S_t -> S_(t+4TR)
Mswap: S_t + another subject's G_j S_t -> S_(t+4TR)
Mrewire: S_t + node-permuted G_i S_t -> S_(t+4TR)
```

Primary subject-level deltas use positive values to mean that true subject `G_i` reduced held-out MSE relative to the comparator.

| Comparison | Mean delta MSE | 95% bootstrap CI | Positive subjects | One-sided sign-flip p |
| --- | ---: | --- | ---: | ---: |
| M3 true vs M1 no structure | -0.0000119337 | [-0.0012328103, 0.0014825392] | 19 / 100 | 0.5090490951 |
| M3 true vs M2 group mean | 0.0006467056 | [-0.0001641625, 0.0017230160] | 31 / 100 | 0.1247875212 |
| M3 true vs Mswap | -0.0000151163 | [-0.0001028483, 0.0000722391] | 53 / 100 | 0.6303369663 |
| M3 true vs Mrewire | -0.0010285813 | [-0.0020635382, -0.0002784207] | 40 / 100 | 0.9986001400 |

Evidence:

```text
paper5/results/paper5_e4_e8_structural_proxy_results.json
paper5/results/paper5_e4_e7_structural_proxy_subject_metrics.csv
paper5/results/figures/paper5_e4_e7_structural_proxy_comparisons.png
paper5/results/figures/paper5_e4_e7_model_mse_boxplot.png
```

## Gate Audit

| Gate | Requirement | Current result |
| --- | --- | --- |
| Gate A | True `G_i` improves over no-structure M1 | FAIL |
| Gate B | True `G_i` improves over group-mean M2 | FAIL |
| Gate C | True `G_i` improves over swapped / rewired nulls | FAIL |
| Gate D | Prior gates replicate in locked final holdout | FAIL / not claimable |

## Scientific Conclusion

Allowed conclusion:

```text
In a 100-subject HCP-YA 2025 WM analysis using cortical aparc68 states and a BedpostX dyad structural proxy, the strong subject-specific structural-constraint hypothesis was not supported.
```

Forbidden claims:

```text
Subject-specific structural connectivity constrains brain-state dynamics.
All Paper 5 structural gates passed.
CWP/NAP structural grounding is established.
This is a gold-standard ACT/SIFT2 tractography result.
```

## Reproduction

Core commands:

```powershell
python paper5/scripts/hcp_s3_download.py --subjects 100 --fast-template --download --workers 8
python paper5/scripts/hcp_smoke_validate.py
python paper5/scripts/hcp_e2_e3_smoke_states.py
python paper5/scripts/hcp_e4_e8_structural_proxy.py --seeds-per-parcel 60 --n-perm 10000 --rebuild-connectomes
```

The commands require authorized HCP/BALSA access. Local secret material is excluded from git and must not be redistributed.
