# Individual Structural Connectome Proxies Do Not Reliably Improve Prediction of Macroscopic Working-Memory Brain-State Transitions

Authors: [TO BE FILLED]  
Affiliations: [TO BE FILLED]  
Correspondence: [TO BE FILLED]

## Abstract

This study tested whether individual structural connectivity provides additional predictive constraint on macroscopic task-fMRI brain-state transitions. We analyzed 100 unrelated HCP-YA subjects with Working Memory task-fMRI, measured movement regressors, anatomical labels, and diffusion BedpostX outputs. Cortical brain states were extracted as aparc68 CIFTI parcel time series, motion-residualized, and modeled at a primary 4TR lag. Subject-level structural matrices were constructed as a frozen BedpostX dyad1 endpoint-propagation proxy aligned to the same 68 cortical parcels. The core test compared a no-structure transition model, a group-mean structural model, a true subject-structure model, swapped-subject structural nulls, and node-permuted rewiring nulls. The strong structural-constraint hypothesis was not supported: true subject `G_i` did not reliably outperform no-structure, group-mean, swapped, or rewired alternatives. These results do not rule out anatomical constraints on neural dynamics, but they reject the current strong claim under this cortical aparc68 / BedpostX proxy implementation.

## 1. Introduction

Papers 3 and 4 established reproducible macroscopic stage-transition signals and tested several falsification routes. Paper 5 asks a narrower biological question: whether anatomical wiring adds predictive information about which future macroscopic state follows a current task-state.

The planned strong hypothesis was:

```text
P(S_(t+tau) | S_t, X_t, G_i) > P(S_(t+tau) | S_t, X_t)
```

and, more stringently, whether the true subject `G_i` outperforms group-average, swapped-subject, and randomized structural alternatives.

## 2. Methods

### 2.1 Dataset

The primary dataset was HCP-YA 2025 / HCP_1200 public S3 distribution accessed through authorized BALSA/ConnectomeDB credentials. The current analysis used the 100 Unrelated Subjects cohort captured from BALSA.

No HCP data are redistributed in this repository. Local credentials are excluded from version control.

### 2.2 fMRI Brain States

Working Memory LR/RL task-fMRI CIFTI files were parcellated with each subject's aparc fs_LR32k dlabel. The current state representation is cortical-only aparc68 parcel means. Measured HCP `Movement_Regressors.txt` files were residualized before prediction.

Primary transition:

```text
S_t -> S_(t+4TR)
```

with HCP TR = 0.72 s, so the primary lag is 2.88 s.

### 2.3 Structural Connectome Proxy

The local environment did not include a full MRtrix ACT/SIFT2 tractography stack. Therefore the completed analysis used a frozen, explicitly limited proxy:

```text
HCP BedpostX dyads1
-> endpoint propagation from aparc68 cortical parcel seeds
-> 68 x 68 subject-level structural proxy matrix
-> row-normalized log-count graph operator
```

Frozen proxy parameters:

```text
seeds per parcel: 60
maximum steps: 96 voxels
minimum steps before endpoint acceptance: 2
step size: 1 voxel
```

This proxy uses real subject-specific HCP diffusion orientation fields, but it is not gold-standard probabilistic tractography and must not be reported as ACT/SIFT2.

### 2.4 Models

All models predicted held-out future cortical state from current state.

```text
M1: S_t -> S_(t+4TR)
M2: S_t + group_mean_G S_t -> S_(t+4TR)
M3: S_t + true subject G_i S_t -> S_(t+4TR)
Mswap: S_t + other subject G_j S_t -> S_(t+4TR)
Mrewire: S_t + node-permuted G_i S_t -> S_(t+4TR)
```

Each model used ridge regression with cross-validated regularization. Statistics were computed at the subject level.

### 2.5 Statistics

The primary metric was held-out MSE. Positive delta MSE means the true-subject structural model reduced error relative to the comparator.

Subject-level inference used bootstrap 95% confidence intervals and 10,000 sign-flip permutations.

## 3. Results

### 3.1 Data And State Pipeline

The 100-subject HCP-YA WM state pipeline completed without subject-level failures.

```text
n_subjects_processed: 100
n_errors: 0
mean held-out R2 for no-structure state prediction: 0.1145682687
median held-out R2: 0.1085043946
mean MSE improvement vs mean-state null: 0.0714343156
```

This confirms that macroscopic WM state transitions were measurable in the current state representation.

### 3.2 Structural Proxy QC

The structural proxy generated one aparc68 matrix per subject.

```text
connectome files generated: 100
mean path success rate: 0.7198786765
median path success rate: 0.7208333333
mean matrix density: 0.1427589991
median matrix density: 0.1427787533
```

### 3.3 Structural Prediction Gates

| Comparison | Mean delta MSE | 95% bootstrap CI | Positive subjects | Sign-flip p |
| --- | ---: | --- | ---: | ---: |
| M3 true vs M1 no structure | -0.0000119337 | [-0.0012328103, 0.0014825392] | 19 / 100 | 0.5090490951 |
| M3 true vs M2 group mean | 0.0006467056 | [-0.0001641625, 0.0017230160] | 31 / 100 | 0.1247875212 |
| M3 true vs Mswap | -0.0000151163 | [-0.0001028483, 0.0000722391] | 53 / 100 | 0.6303369663 |
| M3 true vs Mrewire | -0.0010285813 | [-0.0020635382, -0.0002784207] | 40 / 100 | 0.9986001400 |

The true subject structural proxy did not pass any of the planned gates.

```text
Gate A: M3 > M1 = FAIL
Gate B: M3 > M2 = FAIL
Gate C: M3 > swap / rewire = FAIL
Gate D: locked replication = FAIL / not claimable
```

## 4. Discussion

The current Paper 5 analysis does not support the strong subject-specific structural-constraint hypothesis. The key failure is not merely a lack of effect over the group mean. The true `G_i` also failed to outperform swapped-subject connectomes and performed worse than the node-permuted rewiring null in the current feature construction.

The most conservative interpretation is:

```text
Under cortical aparc68 state extraction and a BedpostX dyad endpoint-propagation structural proxy, subject-specific structural information does not reliably improve prediction of macroscopic HCP working-memory brain-state transitions.
```

This does not show that structure is irrelevant to neural dynamics. It shows that the current structural representation, state representation, and predictive interface are insufficient to support the strong Paper 5 claim.

## 5. Limitations

First, this analysis used cortical aparc68 states rather than the originally targeted Schaefer-200 plus subcortex representation.

Second, the structural matrix was a BedpostX dyad propagation proxy, not ACT/SIFT2 tractography.

Third, only the 100 Unrelated Subjects cohort was used, so the 100-development / 100-locked-holdout split originally proposed for a 200-subject design was not completed.

Fourth, task context terms such as detailed block labels were not yet included in the structural proxy comparison; the current result is best interpreted as a state-plus-graph prediction test.

## 6. Conclusion

Paper 5 is complete as a constrained negative structural-proxy study:

```text
HCP-YA data access, state extraction, and subject-level diffusion-derived structural proxy modeling were completed, but true subject structural proxies did not provide reliable additional prediction of macroscopic WM brain-state transitions.
```

The strong claim that subject-specific anatomical wiring constrains these macroscopic task-state transitions is not supported by the current implementation.

## Data Availability

Publication supplement: [P5 data sources, sample manifests, access conditions, and figure provenance](../DATA_AVAILABILITY.md). Code, papers, and derived results are published at [neuralsignal-theory/test](https://github.com/RiconasSun/neuralsignal-theory/tree/test). Raw participant imaging/signals and tractography remain with the original data providers and are not redistributed. The supplement records dataset identifiers and versions available in existing evidence, links to cohort/pipeline records, and distinguishes unrecorded historical metadata from verified information. Exact local withheld filenames and SHA256 values are recorded in [the raw file inventory](../../publication/raw_file_inventory.csv); derived artifacts and figures have [SHA256 checksums](../../publication/artifact_checksums.csv).

HCP-YA data require authorized access through the HCP/ConnectomeDB/BALSA distribution path. No HCP data are redistributed here.

## Code Availability

Reproduction scripts are provided under `paper5/scripts/`. The current structural proxy results are under `paper5/results/`. Credential files are intentionally excluded from version control.

## Ethics Statement

This analysis uses controlled-access/de-identified HCP data under the applicable HCP data-use terms.

## Conflicts of Interest

[TO BE FILLED]

## Claim Audit

Allowed claim:

```text
The current HCP-YA 2025 BedpostX dyad structural proxy analysis does not support the strong subject-specific structural-constraint hypothesis.
```

Forbidden claims:

```text
Subject-specific structural connectivity constrains brain-state dynamics.
All Paper 5 gates passed.
CWP/NAP structural grounding is established.
This is a gold-standard ACT/SIFT2 tractography result.
```
