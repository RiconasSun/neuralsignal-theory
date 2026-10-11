# Paper 8 Final Extension Protocol v0.1

Title:

```text
Measured Physiological Controls for Candidate Brain-State Transition Dynamics
```

## Status

```text
EXTENSION_PROTOCOL_CREATED_NOT_RUN
```

This extension does not replace the frozen Paper 8 v2 result. The existing HCP
analysis remains:

```text
PRIMARY TRANSITION FAILED
METADATA CONFOUND IDENTIFIED
```

## Scientific Role

This is a convergent physiological validation study, not a direct replication
of the HCP working-memory transition protocol.

Primary candidate:

```text
OpenNeuro ds005795 / NEMAR on005795 / MULTI-CLARID
```

Rationale: the public dataset description reports simultaneous fMRI/EEG,
63-channel EEG with ECG and other peripheral channels, respiration and
finger-pulse physiological recording, plus structural MRI. The task is auditory
category learning and rest, so it must not be presented as Encode/Maintain/Probe
replication.

## Frozen Question

After measured motion, respiration, cardiac/pulse, WM/CSF, RETROICOR-style,
heart-rate, respiratory-volume-per-time, and matched timing/metadata controls,
does any candidate same-transition structure remain above competing
explanations?

## Nuisance Ladder

```text
N0 Raw
N1 + Motion
N2 + Respiration
N3 + Cardiac / finger pulse / ECG
N4 + WM / CSF nuisance
N5 + RETROICOR-style Fourier terms
N6 + HR / RVT derived regressors
N7 + Matched timing and metadata controls
```

Metadata-only is a formal baseline, not an appendix-only diagnostic.

## Primary Endpoint

```text
SameTransition similarity - DifferentTransition similarity
```

evaluated after the full nuisance ladder and matched timing/metadata controls.

## Competing Explanations

```text
motion-only
respiration-only
cardiac-only
physiology-only
metadata-only
event-timing-only
phase-shuffled physiology
random-window controls
```

## Claim Boundary

Allowed if run succeeds:

```text
Measured physiological controls leave residual candidate transition structure under the tested dataset and pipeline.
```

Forbidden:

```text
P8 v2 is rescued.
HCP Encode/Maintain/Probe replicated in ds005795.
Physiology confounds are universally resolved.
NAP is validated.
CWP is validated.
```
