# Paper 5 HCP-YA 2025 Frozen Protocol v1

Title: Individual Structural Connectomes as Predictive Constraints on Macroscopic Task-State Transitions

## Central Model

```text
G_i + S_t + X_t -> S_(t+tau)
```

`G_i` is a diffusion-derived subject-level structural connectome. `S_t` and `S_(t+tau)` are macroscopic brain states extracted from HCP-YA 2025 Working Memory task-fMRI. `X_t` contains 0/2-back, stimulus category, block position, run, measured motion, and time covariates.

## Dataset Lock

Use HCP-Young Adult 2025 only. Do not mix HCP-YA 2025 processing with the 2017 S1200 release.

Official release page: https://www.humanconnectome.org/study/hcp-young-adult/document/hcp-young-adult-2025-release

Target cohort:

```text
N = 200 eligible subjects
100 development subjects
100 locked final holdout subjects
```

Eligibility requires T1w/T2w anatomy, preprocessed dMRI with bvals/bvecs, WM LR/RL task-fMRI, movement files, and WM event timing.

## E0-E8

E0 - Dataset / cohort lock.
E1 - Build subject structural connectome G_i using Schaefer-200 + subcortex, MSMT-CSD, ACT, iFOD2, SIFT2.
E2 - Extract WM task-fMRI brain states in the same atlas and residualize measured motion, run drift, and nuisance terms.
E3 - Strong no-structure baseline: S_(t+tau) = F(S_t, X_t).
E4 - Structural models using group mean and true G_i S_t.
E5 - Structural falsification: swapped, randomized, and distance-only graphs.
E6 - Subject-specificity rank test.
E7 - Locked holdout statistics.
E8 - Claim audit and one-command reproduction.

## Lags

Primary: 4TR_2.88s

Secondary: 1TR_0.72s, 2TR_1.44s, 7TR_5.04s

## Gates

Gate A: M3 > M1, structure matters.
Gate B: M3 > M2, individual structure matters.
Gate C: M3 > swapped/random/distance, anatomical specificity.
Gate D: gates replicate in locked final holdout.
