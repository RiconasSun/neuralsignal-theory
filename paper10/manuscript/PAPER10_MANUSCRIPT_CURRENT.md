# Data-Driven Dynamic Motif Discovery in Fast Neural Signals

## Abstract

P9 rebuilt the CWP/NAP ontology around a dynamics-first evidence ladder. P10 tests the first empirical step after that reconstruction: whether fast neural dynamics form recurring motif families without using cognitive semantics as training labels. Using P6-derived electrophysiological bandpower-delta features from ds004117, we fit train-only PCA representations and unsupervised KMeans motif models, freeze K by train-subject silhouette, and evaluate held-out subjects against phase-randomized, time-shift, random-window, and continuous PCA competing explanations. The result is claim-bounded: the available motif evidence remains insufficient against the available nulls. P10 does not validate NAPs, CWP v2 semantics, neural grammar, or universal neural primitives.

## 1. Introduction

### 1.1 Problem

The original CWP/NAP program could not assume that semantic cognitive labels correspond to neural primitives. P10 therefore starts from neural dynamics rather than semantic labels.

### 1.2 Proposed Test

The primary question is whether fast neural feature trajectories contain recurring motif families that generalize to held-out subjects. The anti-hypothesis is that continuous low-dimensional dynamics or matched null structures explain the data as well or better.

## 2. Methods

### 2.1 Inputs

Primary input was `paper6/features/ds004117_multi_run/ds004117_multi_run_bandpower_delta_features.csv`. Matched null inputs were phase-randomized, time-shift, and random-window feature tables from the same P6 feature interface. External convergent input was ds004752 LCMV encoding/maintenance bandpower features.

### 2.2 Frozen Analysis

All scaling, PCA fitting, K selection, and KMeans centroid fitting used train subjects only. Held-out subjects were never used for latent representation fitting or motif discovery. Transition or stage labels were not used during motif discovery; they were used only for post-hoc metadata association audit.

### 2.3 Baselines and Competing Explanations

The main competing explanations were continuous PCA manifold reconstruction, phase-randomized features, time-shifted windows, random windows, and metadata association.

## 3. Results

### 3.1 Primary Motif Discovery

The train-only selected K was 2. The held-out discrete reconstruction MSE for real ds004117 features was 0.825623. Held-out assignment entropy was 0.893173. The post-hoc transition-label NMI was 0.017570822682773875. The latent-space quantization MSE was 129.495441, but model comparison uses reconstruction MSE so discrete and continuous models are evaluated on the same standardized feature scale.

### 3.2 Null Comparisons

Real held-out quantization MSE was compared with 3 matched null tables.

- ds004117_phase_randomized: held-out discrete reconstruction MSE = 0.914732
- ds004117_time_shift: held-out discrete reconstruction MSE = 0.680388
- ds004117_random_window: held-out discrete reconstruction MSE = 0.686338

The real model beat 1 of 3 available nulls.

### 3.3 Continuous Manifold Baseline

The continuous PCA reconstruction MSE was 0.663943. Continuous-preferred status: True.

### 3.4 External Convergent Check

The ds004752 feature space is not identical to ds004117, so this is not a direct cross-dataset replication. It is recorded only as an external convergent check.

## 4. Discussion

### 4.1 What the Evidence Supports

P10 supports only the claim flags recorded in `results/p10_claim_audit.json`. Candidate motif structure may be discussed only within the tested bandpower-delta feature regime and null set.

### 4.2 What the Evidence Does Not Support

P10 does not support validated NAPs, CWP v2 semantics, motif grammar, external direct replication, or universal neural primitives. It also does not rule out region-specific motifs, region-specific continuous manifolds, hybrid regional dynamics, or hierarchical local-to-global composition; those remain untested follow-up hypotheses.

### 4.3 Limitations

The analysis inherits P6 feature constraints: it uses bandpower/amplitude-family features, not raw iEEG spikes, source-localized phase coupling, or direct cross-dataset feature alignment. The external dataset has a different feature space and can only serve as convergent validation. The current comparison is global; regional and hierarchical alternatives require a separate frozen analysis.

## 5. Conclusion

P10 implements a dynamics-first motif-discovery test after P9. The strongest allowed conclusion is bounded by the claim audit: P10 may report a negative/boundary result for the current global discrete-motif model under the tested P6-derived bandpower feature regime: discrete motif discovery is not supported and a continuous low-dimensional global representation is preferred. This does not test whether individual regions or networks have local motif-like, local continuous-manifold, or hierarchical dynamics. NAP, semantic, grammar, and universal claims remain disallowed.

## Data Availability

Publication supplement: [P10 data sources, sample manifests, access conditions, and figure provenance](../DATA_AVAILABILITY.md). Code, papers, and derived results are published at [neuralsignal-theory/test](https://github.com/RiconasSun/neuralsignal-theory/tree/test). Raw participant imaging/signals and tractography remain with the original data providers and are not redistributed. The supplement records dataset identifiers and versions available in existing evidence, links to cohort/pipeline records, and distinguishes unrecorded historical metadata from verified information. Exact local withheld filenames and SHA256 values are recorded in [the raw file inventory](../../publication/raw_file_inventory.csv); derived artifacts and figures have [SHA256 checksums](../../publication/artifact_checksums.csv).

No new raw data are distributed in P10. The analysis consumes local P6 feature artifacts generated from public datasets.

## Code Availability

Reproduction script: `paper10/scripts/run_paper10.py`. Public repository: [neuralsignal-theory/test](https://github.com/RiconasSun/neuralsignal-theory/tree/test).

## Reproducibility Statement

Run:

```powershell
powershell -ExecutionPolicy Bypass -File paper10/scripts/reproduce-paper10.ps1
```

## Ethics Statement

P10 reuses de-identified public feature artifacts from prior local analyses.

## Author Contributions

`[TO BE FILLED]`

## Conflicts of Interest

`[TO BE FILLED]`
