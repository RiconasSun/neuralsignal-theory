# High-fidelity ACT/SIFT2 Structural Grounding of Reproducible Macroscopic Brain-State Transitions

Authors: [TO BE FILLED]

Affiliations: [TO BE FILLED]

Correspondence: [TO BE FILLED]

## Abstract

Paper 7 tests whether subject-specific structural connectivity provides incremental constraints on macroscopic brain-state transition prediction when `G_i` is rebuilt with a higher-fidelity ACT/iFOD2/SIFT2 tractography route rather than the earlier Paper 5 BedpostX-dyad proxy. Using HCP-YA 2025 structural inputs, we generated 100 fs_default84 ACT/iFOD2/SIFT2 connectomes through an MRtrix3 FreeSurfer-5TT route. A frozen pre-modeling QC rule excluded one warning-positive sparse outlier, leaving 99 subjects for the final primary analysis. The final comparison tested no-structure, group-mean, true-subject, swapped-subject, rewired, and anatomical distance-only models using the same macroscopic state-prediction interface. The final gates did not support subject-specific structural grounding: true-subject `G_i` did not outperform no-structure, group-mean, swapped, rewired, or distance-only baselines. Under this pipeline, high-fidelity structural connectomes were generated successfully, but the strong structural-constraint hypothesis was not supported.

## 1. Introduction

Paper 5 did not support subject-specific structural-proxy grounding. That result could have reflected a weak structural proxy rather than a genuine absence of structural constraint. Paper 7 therefore asks whether rebuilding `G_i` with an ACT/iFOD2/SIFT2 route changes the conclusion.

## 2. Methods

The dataset was HCP-YA 2025 structural and WM-task material available in the local authorized cache. The structural route was:

```text
dMRI -> response estimation -> MSMT-CSD -> FreeSurfer 5TT -> ACT -> iFOD2 -> SIFT2 -> fs_default84 connectome
```

The final model comparison used a primary lag of 4 TR, or 2.88 seconds. Models compared:

```text
M1 no structure
M2 group-mean connectome
M3 true subject connectome
Mswap swapped-subject connectome
Mrewire node-permuted connectome
Mdistance anatomical distance-only graph
```

The primary endpoint was subject-level delta MSE. Positive delta means the true-subject structural model improved prediction relative to the comparator.

## 3. Results

Status:

```text
FINAL_STRUCTURAL_HYPOTHESIS_NOT_SUPPORTED
```

P7 generated 100 fs_default84 ACT/iFOD2/SIFT2 connectomes. Subject 100307 was excluded before final modeling by the frozen QC v0.2 rule because it remained warning-positive and sparse after 20k streamline sensitivity. The final primary analysis therefore included 99 subjects.

Final gates:

```text
Gate A true G_i > no structure: false
Gate B true G_i > group mean: false
Gate C true G_i > swapped/rewired: false
Gate C true G_i > distance-only: false
```

Final subject-level delta MSE summaries:

```text
true vs no-structure: mean -0.000032, 95% CI [-0.001609, 0.001723], p_one_sided=0.514
true vs group-mean:   mean -0.000494, 95% CI [-0.000800, -0.000109], p_one_sided=1.000
true vs swapped:      mean -0.000681, 95% CI [-0.001699, 0.000006], p_one_sided=0.956
true vs rewired:      mean -0.000822, 95% CI [-0.001854, -0.000040], p_one_sided=0.975
true vs distance:     mean -0.000116, 95% CI [-0.001730, 0.001633], p_one_sided=0.565
```

These results do not support the claim that subject-specific high-fidelity structural connectivity adds stable predictive information for macroscopic brain-state transitions under the tested interface.

## 4. Discussion

Paper 7 closes a major ambiguity left by Paper 5. The earlier negative result can no longer be dismissed only because `G_i` was a weak BedpostX-dyad proxy: this paper generated a 100-subject ACT/iFOD2/SIFT2 connectome cohort and still did not find subject-specific structural superiority in the frozen prediction test.

This is a constrained negative finding, not a universal claim that anatomical connectivity never constrains brain dynamics. It applies to the current HCP-YA 2025 sample, FreeSurfer-5TT ACT/iFOD2/SIFT2 route, 5,000-streamline engineering tractograms, fs_default84-to-aparc68 mapping, macroscopic fMRI state representation, and ridge-regression prediction interface.

## 5. Conclusion

High-fidelity structural connectomes were generated and tested, but the Paper 7 strong structural-grounding hypothesis was not supported. The strongest allowed conclusion is:

```text
Under the tested high-fidelity ACT/iFOD2/SIFT2 connectome and macroscopic fMRI state-prediction interface, subject-specific structural connectivity did not provide robust incremental constraints on brain-state transition prediction.
```

## Data Availability

Publication supplement: [P7 data sources, sample manifests, access conditions, and figure provenance](../DATA_AVAILABILITY.md). Code, papers, and derived results are published at [neuralsignal-theory/test](https://github.com/RiconasSun/neuralsignal-theory/tree/test). Raw participant imaging/signals and tractography remain with the original data providers and are not redistributed. The supplement records dataset identifiers and versions available in existing evidence, links to cohort/pipeline records, and distinguishes unrecorded historical metadata from verified information. Exact local withheld filenames and SHA256 values are recorded in [the raw file inventory](../../publication/raw_file_inventory.csv); derived artifacts and figures have [SHA256 checksums](../../publication/artifact_checksums.csv).

HCP-YA data require HCP/BALSA access and compliance with the applicable data-use terms.

## Code Availability

Scripts are under:

```text
paper7/scripts/
```

## Reproducibility Statement

Run:

```powershell
.\paper7\scripts\reproduce-paper7.ps1
```

## Ethics Statement

[TO BE FILLED]

## Author Contributions

[TO BE FILLED]

## Conflicts of Interest

[TO BE FILLED]
