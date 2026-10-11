# Paper 10 Frozen Protocol v1

Status: implemented local protocol  
Generated: 2026-09-07T05:16:16+00:00

## Title

Data-Driven Dynamic Motif Discovery in Fast Neural Signals

## Core Question

Do fast neural dynamics naturally form recurring motif families, or are they better treated as a continuous manifold?

## Primary Hypothesis

Unsupervised clustering of latent electrophysiological transition features will produce recurring dynamic motif families that generalize to held-out subjects and outperform matched null inputs.

## Required Anti-Hypothesis

The same data may be better described by continuous low-dimensional manifolds or by matched null/time/phase/random-window explanations. If those win, the discrete motif hypothesis contracts.

## Inputs

Primary input:

```text
paper6/features/ds004117_multi_run/ds004117_multi_run_bandpower_delta_features.csv
```

Null inputs:

```text
phase randomized bandpower deltas
time-shift bandpower deltas
random-window bandpower deltas
```

External convergent input:

```text
paper6/features/ds004752_external/ds004752_lcmv_encoding_maintenance_bandpower_features.csv
```

## Frozen Pipeline

```text
P9 ontology rules
-> P6 feature-table input audit
-> subject split
-> train-only standardization
-> train-only PCA latent representation
-> train-only K selection by silhouette
-> KMeans motif discovery
-> held-out subject quantization / recurrence
-> matched null comparison
-> continuous PCA baseline
-> external convergent check
-> claim audit
```

## Baselines

```text
continuous PCA manifold
phase-randomized null
time-shift null
random-window null
metadata association audit
```

## Holdout

Subjects are split deterministically by sorted subject ID into approximately 70 percent train and 30 percent held-out test subjects. K selection and scaling use train subjects only.

## Primary Endpoint

Held-out subject quantization error and motif recurrence for real ds004117 features compared with matched null feature tables.

## Secondary Endpoint

Continuous PCA reconstruction error compared with discrete motif quantization error. This endpoint determines whether the discrete motif language should contract toward continuous manifold dynamics.

## Claim Boundary

P10 may support candidate dynamic motifs only within the tested global feature regime. It may not validate NAPs, CWP semantics, motif grammar, universal neural primitives, or claims that region-specific motifs are absent.
