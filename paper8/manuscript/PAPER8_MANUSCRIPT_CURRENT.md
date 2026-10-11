# Measured-Physiology Boundary Test of Reproducible Cognitive Brain-State Transitions

Authors: [SUBMISSION METADATA REQUIRED]

Affiliations: [SUBMISSION METADATA REQUIRED]

Correspondence: [SUBMISSION METADATA REQUIRED]

## Abstract

Paper 8 tests whether reproducible macroscopic brain-state transitions survive aggressive measured nuisance control using real motion, respiration, cardiac/pulse, tissue, and timing regressors. We identified HCP-YA WM runs with measured Physio_log files, downloaded or confirmed 36 WM physiology logs, and ran an 18-subject / 36-run measured-physiology nuisance ladder smoke test. The preregistered primary raw transition-reproducibility gate, SameTransition similarity greater than DifferentTransition similarity, was not reproduced. We then added a convergent ds005795 streaming extension over all manifest-available task-learning subjects with complete BOLD/physio/event files. The extension showed that measured physiology improves global BOLD signal prediction, but it does not rescue the failed HCP primary gate. Therefore no claim that measured physiology has been eliminated, or that the transitions have a proven neural origin, is allowed in the current Paper 8 package.

## 1. Introduction

Papers 3 and 4 support reproducible macroscopic transition structure under proxy nuisance and timing controls, but measured respiration and cardiac signals were not fully tested. This is a serious limitation because fMRI studies have long documented structured respiratory, cardiac, and motion-related artifacts that can mimic or distort neural signal structure [1-5]. Paper 8 directly attacks that limitation.

## 2. Methods

The primary candidate is HCP-YA because the WU-Minn Human Connectome Project provides a large multimodal young-adult neuroimaging resource with task-fMRI, including a working-memory task battery, and associated processing/documentation for motion and physiological monitoring files [6-8]. The current smoke test used HCP WM runs with available `tfMRI_WM_*_Physio_log.txt`, `Movement_Regressors.txt`, WM EV timing files, CIFTI dtseries files, and the matching aparc dlabel file.

For each 0-back or 2-back block start, the analysis extracted an aparc68 cortical transition vector as the post-onset state window minus a pre-onset baseline window. The nuisance ladder residualized progressively richer measured nuisance sets:

```text
N0 raw/basic
N1 motion
N2 respiration
N3 cardiac/pulse
N4 motion + respiration + cardiac/pulse
```

The primary gate was same-transition reproducibility:

```text
SameTransition similarity > DifferentTransition similarity
```

Leave-one-run-out 0-back vs 2-back classification was retained as a secondary diagnostic only.

As a convergent measured-physiology extension, OpenNeuro ds005795 / NEMAR on005795 was audited by public manifest and then processed with a streaming pipeline. This dataset contains simultaneous fMRI/EEG recordings with ECG and physiological respiration/finger-pulse recordings during an auditory category-learning task [9]. Each available `task-learning` BOLD file was downloaded, modeled, and deleted after subject-level feature extraction. The extension used global BOLD signal transition prediction with four models:

```text
N0 state only
N1 state + cardiac/respiration
N2 state + metadata
N3 state + physiology + metadata
```

This extension was not treated as a direct replication of HCP working-memory transition reproducibility because the task design and state endpoint differ.

## 3. Current Results

Status:

```text
P8_E1_E6_HCP_PHYSIO_SMOKE_RAW_GATE_FAILED
```

The smoke test included 18 subjects, 36 WM runs, and 288 block-start transition rows. E0 found remote HCP WM physiology logs, E1 downloaded or confirmed 36 physiology logs, and E1-E6 completed the nuisance ladder.

Primary N0 raw result:

```text
SameTransition similarity = 0.926106
DifferentTransition similarity = 0.959254
Same-Different contrast = -0.033148
Subject mean contrast = -0.073271
Bootstrap 95% CI = [-0.161751, 0.018574]
Subject sign-flip p = 0.934607
Gate A = FAILED
```

Across all nuisance rungs, the same-transition contrast stayed negative:

| Rung | Same-Different Contrast | Leave-One-Run-Out Accuracy |
|---|---:|---:|
| N0 raw/basic | -0.033148 | 0.715278 |
| N1 motion | -0.015995 | 0.753472 |
| N2 respiration | -0.040132 | 0.732639 |
| N3 cardiac/pulse | -0.037937 | 0.729167 |
| N4 combined | -0.018814 | 0.756944 |

A P8-v2 signal-separation audit tested whether the secondary classification signal should be treated separately from the failed transition-reproducibility endpoint. With 100 permutations per tested rung, the ROI transition-feature classifier exceeded simple label-shuffle nulls, while the primary same-transition contrast did not:

| Rung | True Contrast | Contrast p vs Label Shuffle | ROI Accuracy | Label-Shuffle Accuracy Mean | Metadata-Only Accuracy |
|---|---:|---:|---:|---:|---:|
| N0 raw/basic | -0.033148 | 0.881188 | 0.715278 | 0.494028 | 0.625000 |
| N4 combined | -0.018814 | 0.405941 | 0.756944 | 0.488646 | 0.625000 |

The ds005795 streaming extension completed all manifest-available `task-learning` subjects with the required four-file bundle:

```text
sub-01, sub-02, sub-03, sub-04, sub-05
```

Aggregate global-signal prediction results were:

| Model | Mean MSE | Mean R2 | Subjects |
|---|---:|---:|---:|
| N0 state only | 308.008097 | 0.480632 | 5 |
| N1 state + cardiac/respiration | 288.628925 | 0.516281 | 5 |
| N2 state + metadata | 304.121571 | 0.485793 | 5 |
| N3 state + physiology + metadata | 286.173932 | 0.519003 | 5 |

Relative to state-only prediction, physiology plus metadata improved mean MSE by 21.834165 and mean R2 by 0.038371. This result establishes nuisance relevance in a convergent measured-physiology dataset, not physiology-robust transition reproducibility.

## 4. Discussion

The current result does not support the Paper 8 strong survival claim. The above-chance 0-back vs 2-back block-start classification signal indicates that task-condition information remains available in the extracted transition features, but this is not the preregistered same-transition reproducibility endpoint. Because the raw gate failed before measured nuisance controls were decisive, the result should be treated as a constrained negative/diagnostic smoke test rather than a completed physiological validation.

P8-v2 sharpens the interpretation: condition decodability and transition reproducibility are different scientific endpoints. The former survived simple label-shuffle tests in this smoke set; the latter did not. The ds005795 extension adds a second boundary: measured physiology can carry substantial predictive information for fMRI signal dynamics without proving the cognitive transition-reproducibility claim.

The current claim boundary is:

```text
HCP measured physiology can be acquired and inserted into the nuisance ladder, but the preregistered raw transition reproducibility contrast was not reproduced in the current 18-subject smoke test.
```

## Data Availability

Publication supplement: [P8 data sources, sample manifests, access conditions, and figure provenance](../DATA_AVAILABILITY.md). Code, papers, and derived results are published at [neuralsignal-theory/test](https://github.com/RiconasSun/neuralsignal-theory/tree/test). Raw participant imaging/signals and tractography remain with the original data providers and are not redistributed. The supplement records dataset identifiers and versions available in existing evidence, links to cohort/pipeline records, and distinguishes unrecorded historical metadata from verified information. Exact local withheld filenames and SHA256 values are recorded in [the raw file inventory](../../publication/raw_file_inventory.csv); derived artifacts and figures have [SHA256 checksums](../../publication/artifact_checksums.csv).

HCP-YA data require HCP/BALSA access and compliance with the applicable data-use terms. OpenNeuro ds005795 is publicly indexed as version 1.0.0 with DOI `10.18112/openneuro.ds005795.v1.0.0`; NEMAR indexes the corresponding copy as on005795 with DOI `10.82901/nemar.on005795`.

## Code Availability

Current scripts are under:

```text
paper8/scripts/
```

## Reproducibility Statement

Run:

```powershell
.\paper8\scripts\reproduce-paper8.ps1
```

## Ethics Statement

[SUBMISSION METADATA REQUIRED: state whether this is secondary analysis of de-identified public/restricted-access datasets and identify the applicable institutional review / exemption status for the submitting authors.]

## Author Contributions

[SUBMISSION METADATA REQUIRED]

## Conflicts of Interest

[SUBMISSION METADATA REQUIRED]

## Funding

[SUBMISSION METADATA REQUIRED]

## References

1. Glover GH, Li TQ, Ress D. Image-based method for retrospective correction of physiological motion effects in fMRI: RETROICOR. Magnetic Resonance in Medicine. 2000;44(1):162-167. doi:10.1002/1522-2594(200007)44:1<162::AID-MRM23>3.0.CO;2-E

2. Power JD, Barnes KA, Snyder AZ, Schlaggar BL, Petersen SE. Spurious but systematic correlations in functional connectivity MRI networks arise from subject motion. NeuroImage. 2012;59(3):2142-2154. doi:10.1016/j.neuroimage.2011.10.018

3. Behzadi Y, Restom K, Liau J, Liu TT. A component based noise correction method (CompCor) for BOLD and perfusion based fMRI. NeuroImage. 2007;37(1):90-101. doi:10.1016/j.neuroimage.2007.04.042

4. Ciric R, Wolf DH, Power JD, et al. Benchmarking of participant-level confound regression strategies for the control of motion artifact in studies of functional connectivity. NeuroImage. 2017;154:174-187. doi:10.1016/j.neuroimage.2017.03.020

5. Birn RM, Smith MA, Jones TB, Bandettini PA. The respiration response function: the temporal dynamics of fMRI signal fluctuations related to changes in respiration. NeuroImage. 2008;40(2):644-654. doi:10.1016/j.neuroimage.2007.11.059

6. Van Essen DC, Smith SM, Barch DM, Behrens TEJ, Yacoub E, Ugurbil K; WU-Minn HCP Consortium. The WU-Minn Human Connectome Project: an overview. NeuroImage. 2013;80:62-79. doi:10.1016/j.neuroimage.2013.05.041

7. Barch DM, Burgess GC, Harms MP, et al. Function in the human connectome: task-fMRI and individual differences in behavior. NeuroImage. 2013;80:169-189. doi:10.1016/j.neuroimage.2013.05.033

8. Human Connectome Project. 1200 Subjects Data Release and HCP-Young Adult release documentation. HumanConnectome.org.

9. OpenNeuro / NEMAR. MULTI-CLARID: Multimodal Category Learning and Resting-state Imaging Data. OpenNeuro ds005795 v1.0.0. doi:10.18112/openneuro.ds005795.v1.0.0; NEMAR on005795 doi:10.82901/nemar.on005795.
