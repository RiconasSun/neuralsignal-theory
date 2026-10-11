# Paper 6 Frozen Protocol v0.1

## Title

Do Reproducible Macroscopic Brain-State Transitions Contain Reproducible Subsecond Neural Dynamics?

## Paper Type

Explanation Paper.

## Program State Entering Paper 6

```text
Dynamics survived; ontology and structural mechanism remain unproven.
```

Paper 6 must not assume that NAP exists. It tests whether reproducible macroscopic transitions have reproducible fast neural-dynamics structure beneath them.

## Research Question

Do macro-scale cognitive/task transitions correspond to reproducible subsecond neural dynamics in electrophysiology?

## Falsifiable Hypothesis

For a fixed macro transition class `T`, the fast neural dynamics observed in a transition-aligned electrophysiological window are more reproducible than matched null windows, and different transition classes have distinguishable fast-dynamics signatures.

## Primary Candidate Transition

```text
Encode -> Maintain
```

Secondary transitions:

```text
Maintain -> Recall / Probe
Trial baseline -> Encode
```

## Primary Dataset Candidate

```text
OpenNeuro ds004117
```

Rationale: public EEG Sternberg working-memory dataset whose events expose onset/sample timing and task-role fields that support direct transition-window construction.

## External Dataset Candidates

```text
OpenNeuro ds004752: iEEG + scalp EEG verbal working-memory dataset, high-value but requires manual stage mapping because initial events preview is trial-level rather than explicit stage-level.
OpenNeuro / NEMAR ds002550 / on002550: MEG working-memory selection and maintenance, requires sequence-derived maintenance mapping.
```

External datasets are candidates only until E1 confirms event semantics and usable files.

## E0-E8

| Experiment | Purpose | Status |
| --- | --- | --- |
| E0 Protocol Freeze | Freeze claim, transitions, datasets, metrics, nulls | FROZEN_v0.1 |
| E1 Dataset Audit | Verify public electrophysiology datasets and event semantics | PASS_INITIAL_E1 |
| E2 Macro Transition Definition | Map events to transition windows | PASS_INITIAL_E2_FOR_ds004117 |
| E3 Fast Feature Extraction | Extract oscillation / phase / population-state features | NOT YET RUN |
| E4 Existence Test | Same-transition fast dynamics reproducibility | NOT YET RUN |
| E5 Specificity Test | Transition A vs B separability | NOT YET RUN |
| E6 Null / Falsification | Phase shuffle, time shift, random segmentation, event-only, band-power-only | NOT YET RUN |
| E7 Cross-subject / Cross-dataset Replication | Test whether findings generalize | NOT YET RUN |
| E8 Claim Audit / Reproduction | Decide allowed claims | NOT YET RUN |

## Primary Endpoint

Subject-level mean difference:

```text
Similarity(fast dynamics | same transition)
-
Similarity(fast dynamics | matched null windows)
```

The primary endpoint is positive only if the 95% confidence interval is above zero and null distributions are exceeded under the frozen test.

## Secondary Endpoints

```text
Transition-class decoding above event-timing-only baseline
Cross-session transfer within subject
Cross-subject transfer
Cross-dataset direction consistency
Feature-family robustness across time-frequency, phase, and trajectory representations
```

## Fast-Dynamics Feature Families

```text
Time-frequency power: theta, alpha, beta, low gamma, high gamma
Phase-locking / phase consistency
Phase-amplitude coupling when sampling rate permits
Population state trajectory in channel/electrode space
Temporal sharpness / transition distance
Spike timing only if single-unit data are available
```

## Competing Explanations / Baselines

```text
Event-timing-only baseline
Simple band-power baseline
Random transition windows with matched duration
Trial-position baseline
Condition-label baseline without transition windows
Subject/session identity baseline
```

## Null / Falsification Tests

```text
Phase shuffle
Circular time shift
Random segmentation
Transition-label shuffle
Duration-matched random windows
Spike-time jitter if spike data are present
Electrode/channel shuffle
```

## Success Criteria

Strong success requires all three:

```text
Existence: same-transition fast dynamics exceed matched nulls.
Specificity: different macro transitions have distinguishable fast dynamics.
Generalization: direction survives cross-subject and at least one external dataset.
```

Moderate success:

```text
Existence and specificity hold in the primary dataset, but cross-dataset generalization is not established.
```

Failure:

```text
Fast dynamics fail against matched nulls or event-timing-only baselines.
```

## Claim Boundaries

Allowed only after supporting results:

```text
candidate NAP-like dynamics
dataset-specific electrophysiological transition signature
```

Forbidden before E4-E7 pass:

```text
NAP is validated
CWP maps to NAP
macro transitions are mechanistically explained
fast neural dynamics are universal primitives
```

## E2 Data-Driven Dataset Decision

Initial public metadata and event audits found:

```text
ds004117: PASS_INITIAL_E2; event files include onset, sample, event_type, task_role, memory_cond.
ds004752: PARTIAL; events include trial onset/sample but require manual stage mapping.
ds002550: PARTIAL; events include cue/stimulus/probe sequence but require derived maintenance windows.
```

Therefore P6 v0.1 uses `ds004117` as the first executable analysis dataset. `ds004752` remains the preferred iEEG mechanistic extension only after a separate manual event-stage mapping audit.

## Reproduction Target

```powershell
.\paper6\scripts\reproduce-paper6.ps1
```

The first implemented reproduction stage performs E1 public dataset audit and writes the claim audit as `NOT_YET_RUN` for neural results.
