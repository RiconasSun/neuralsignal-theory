# Paper 8 Frozen Protocol v0.1

Title:

```text
Measured Physiological Validation of Reproducible Cognitive Brain-State Transitions
```

## Research Question

Paper 8 tests whether the reproducible macroscopic stage-transition contrast from Papers 3 and 4 survives measured nuisance control using real motion, respiration, cardiac/pulse, tissue, and timing regressors.

## Primary Aim

The goal is to try to destroy the P3/P4 transition contrast with measured nuisance controls. If aggressive measured nuisance control eliminates the transition contrast, that negative result must be accepted.

## Candidate Dataset Criteria

Primary dataset candidates must provide as many of the following as possible:

```text
task-fMRI
subject-level event timing
measured head motion
measured respiration
measured pulse/cardiac signal
repeated trials or blocks
public or authorized download path
WM/CSF nuisance or anatomical masks
```

## Primary Dataset Candidate

```text
HCP-YA 2025 / HCP_1200
```

Reason:

```text
HCP documentation describes fMRI physiological monitoring logs and HCP-YA 2025 task-fMRI movement regressors. Local Paper 5 work already established authorized HCP/BALSA access and a 100-subject WM task-fMRI cache.
```

## Analysis Ladder

```text
N0 raw/basic transition
N1 + measured motion
N2 + respiration
N3 + cardiac/pulse
N4 + motion + respiration + cardiac
N5 + WM/CSF
N6 aggressive combined nuisance
N7 aggressive + high-motion censoring
N8 low-motion / physiology-matched subset
```

## Gates

Gate A:

```text
raw transition reproduced
```

Gate B:

```text
transition remains positive after measured motion control
```

Gate C:

```text
transition remains positive after respiration + cardiac control
```

Gate D:

```text
transition remains positive after aggressive combined nuisance/censoring or matched-subset control
```

Gate E:

```text
external or convergent physiological replication has same direction if P8-B is available
```

## Claim Boundary

Strongest allowed claim if gates pass:

```text
The reproducible macroscopic transition contrast survived the measured motion and physiological nuisance models tested here.
```

Forbidden claims:

```text
physiology eliminated
motion fully excluded
neural origin proven
CWP validated
NAP validated
```
