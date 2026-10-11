# Paper 5 Phase 1 HCP-YA 2025 Protocol v1

Title: Individual Structural Connectomes as Constraints on Cognitive Brain-State Transitions

## Status

```text
PENDING_HCP_YA_2025_DATA_ACCESS_AND_DOWNLOAD
```

## Rationale

The OpenNeuro datasets used in Papers 1-4 do not contain dMRI-derived subject-level structural connectomes. The proper continuation of Paper 5 is therefore a new HCP-YA 2025 analysis, not a post-hoc reinterpretation of T1w anatomy as `G_i`.

## Dataset Rule

Use HCP-Young Adult 2025 only. Do not mix HCP-YA 2025 processed outputs with the 2017 S1200 processing in the same analysis.

Official release page:

```text
https://www.humanconnectome.org/study/hcp-young-adult/document/hcp-young-adult-2025-release
```

Known release facts from the official documentation checked during setup:

```text
Release date: 2025-08-11
Processed participants without processing errors and with at least one rfMRI run for MSMAll: 1071
Retest participants: 45
Unprocessed imaging participants: 1113
Available modality target: 3T task-fMRI + diffusion MRI / connectivity-relevant structural data
```

## Primary Hypothesis

```text
P(S_next | S_t, CognitiveState, G_i) > P(S_next | S_t, CognitiveState)
```

## Required Inputs

```text
HCP-YA 2025 subject list
3T Working Memory task-fMRI runs
task event timing / E-Prime variables
dMRI-derived subject-level structural connectomes or reproducible dMRI-to-connectome pipeline
ROI atlas shared by fMRI state extraction and structural connectome matrices
```

## Model Chain

```text
HCP-YA 2025 task-fMRI
-> stage/event-aligned brain states S_t and S_next
-> HCP-YA 2025 dMRI/connectivity-derived G_i
-> state/context baseline
-> individual G_i model
-> structural nulls
-> subject-level statistics
```

## Baselines

```text
M0: S_next = f(S_t)
M1: S_next = f(S_t, CognitiveState)
M2: S_next = f(S_t, CognitiveState, group_mean_G)
M3: S_next = f(S_t, CognitiveState, G_i)
```

## Structural Nulls

```text
subject-connectome swap
group-mean connectome
edge-shuffled connectome
degree-preserving randomized graph
distance-only graph
```

## Success Gate

The structural claim is allowed only if individual `G_i` improves subject-held-out prediction over the state/context baseline and beats the structural nulls under subject-level statistics.

## Failure Gate

If individual `G_i` does not beat group/random/swapped connectomes, the conclusion is that current evidence does not support individual structural-connectome constraint on the extracted transitions.
