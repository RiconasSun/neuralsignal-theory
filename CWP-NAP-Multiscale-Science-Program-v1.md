# CWP-NAP Multiscale Science Program v1

Status: frozen Backbone architecture for four CWP-NAP first-batch papers  
Scope: Layer II - CWP-NAP Multiscale Science  
Program goal: test whether cognitive phenomena can be explained as regimes of CWP-conditioned neural dynamics  
Evidence policy: this document uses only the provided Backbone content. It does not invent datasets, sample sizes, p-values, effect sizes, holdout scores, baseline scores, exact thresholds, completed results, repository URLs, accession numbers, or experimental outcomes.

Unknown or unrun items are marked as `[TO BE FILLED]`, `[NOT YET RUN]`, or `[DECISION REQUIRED]`.

## Program Question

```text
Can cognitive phenomena be explained as regimes of CWP-conditioned neural dynamics?
```

## Program Structure

```text
Framework
-> Transition
-> Stability
-> Impairment
```

| Paper | Measures |
| --- | --- |
| CWP-NAP Framework | Whether CWP constrains NAP dynamics. |
| Insight | How state suddenly transitions. |
| Flow | How state becomes unusually stable. |
| Alexithymia | How state transformation becomes impaired. |

## Shared Paper Contract

Each paper must eventually satisfy:

```text
Hypothesis
-> Dataset
-> Frozen Pipeline
-> Baselines / Competing Explanations
-> Holdout
-> Statistics
-> Null Tests
-> Limitations
-> One-command Reproduction
```

## Shared Missing Decisions

- Exact CWP operational definition: `[TO BE FILLED]`
- Exact NAP operational definition: `[TO BE FILLED]`
- Exact BrainState / S_t representation: `[TO BE FILLED]`
- CWP-to-NAP alignment method: `[TO BE FILLED]`
- Time indexing and sampling-resolution policy: `[TO BE FILLED]`
- Dataset choices per paper: `[TO BE FILLED]`
- Subject/sample counts: `[TO BE FILLED]`
- Inclusion/exclusion criteria: `[TO BE FILLED]`
- Holdout split logic: `[TO BE FILLED]`
- Statistical tests and correction plan: `[TO BE FILLED]`
- Null/falsification tests per paper: `[TO BE FILLED]`
- One-command reproduction: `[TO BE FILLED]`

## Paper 1 - CWP-NAP Framework

**Backbone**

```text
CWP_t -> NAP_t -> BrainState_t+1
```

**Core question**  
Can cognitive work state CWP systematically constrain subsequent neural activity pattern NAP and brain-state transition?

**Paper type**  
Method Paper

**Core model**

```text
P(S_t+1 | S_t, CWP_t)
```

**Comparison model**

```text
P(S_t+1 | S_t)
```

**Core hypothesis**  
Adding CWP_t should improve holdout prediction of S_t+1 relative to a model that conditions only on S_t.

**Failure condition**  
If adding CWP does not improve holdout prediction, the framework's core claim is weakened. The exact improvement threshold is `[DECISION REQUIRED]`.

**One-sentence contribution**  
Establish and validate CWP-conditioned neural dynamics as a unified mid-level neural dynamics framework.

**Known results**  
`[NOT YET RUN]`

**Missing fields**

- Dataset: `[TO BE FILLED]`
- CWP_t definition: `[TO BE FILLED]`
- NAP_t definition: `[TO BE FILLED]`
- BrainState_t+1 definition: `[TO BE FILLED]`
- Holdout prediction metric: `[TO BE FILLED]`
- Baselines beyond P(S_t+1 | S_t): `[TO BE FILLED]`
- Statistical test for prediction improvement: `[TO BE FILLED]`
- Null tests: `[TO BE FILLED]`
- Limitations: `[TO BE FILLED]`
- One-command reproduction: `[TO BE FILLED]`

## Paper 2 - Insight

**Backbone**

```text
Search
-> Precursor NAP
-> Abrupt Transition
-> Insight
```

**Core question**  
Is "Aha!" not a random instant, but a predictable neural-state transition?

**Paper type**  
Explanation Paper

**Core prediction**

```text
P(Insight_t+Delta | NAP_t-k:t) > P(Insight)
```

**Core hypothesis**  
Pre-insight NAP dynamics should predict later insight above base-rate insight prediction.

**Primary analysis focus**

- Pre-insight precursor.
- Transition sharpness.
- State-space distance.
- Insight vs non-insight trials.

**Failure condition**  
If pre-insight NAP dynamics do not predict later insight above base rate or appropriate non-insight controls, the abrupt-transition explanation is weakened. The exact threshold is `[DECISION REQUIRED]`.

**One-sentence contribution**  
Explain insight as a predictable abrupt CWP-NAP state transition.

**Known results**  
`[NOT YET RUN]`

**Missing fields**

- Dataset: `[TO BE FILLED]`
- Insight event definition: `[TO BE FILLED]`
- Search phase definition: `[TO BE FILLED]`
- Precursor NAP feature definition: `[TO BE FILLED]`
- Delta and k time windows: `[DECISION REQUIRED]`
- Transition sharpness metric: `[TO BE FILLED]`
- State-space distance metric: `[TO BE FILLED]`
- Non-insight control construction: `[TO BE FILLED]`
- Holdout split: `[TO BE FILLED]`
- Statistical test: `[TO BE FILLED]`
- Null/falsification tests: `[TO BE FILLED]`
- One-command reproduction: `[TO BE FILLED]`

## Paper 3 - Flow

**Backbone**

```text
Task CWP
-> Stable NAP Manifold
-> Low Switching
-> Flow
```

**Core question**  
Does flow correspond to an unusually stable, low-switching-cost task-conditioned neural trajectory?

**Paper type**  
Explanation Paper

**Core prediction 1**

```text
Entropy_transition^Flow < Entropy_transition^Control
```

**Core prediction 2**

```text
P(S_t+1 in TaskManifold | S_t, Flow) increases
```

**Core hypothesis**  
Flow should show reduced transition entropy and increased persistence within a task-relevant manifold relative to control states.

**Primary analysis focus**

- State dwell time increases.
- Transition entropy decreases.
- Irrelevant switching decreases.
- Trajectory consistency increases.

**Failure condition**  
If flow states do not show lower transition entropy, greater task-manifold persistence, or reduced irrelevant switching relative to control, the stabilization explanation is weakened. Exact thresholds are `[DECISION REQUIRED]`.

**One-sentence contribution**  
Explain flow as CWP-conditioned neural dynamical stabilization.

**Known results**  
`[NOT YET RUN]`

**Missing fields**

- Dataset: `[TO BE FILLED]`
- Flow operational definition: `[TO BE FILLED]`
- Control-state definition: `[TO BE FILLED]`
- Task CWP definition: `[TO BE FILLED]`
- Stable NAP manifold definition: `[TO BE FILLED]`
- Transition entropy metric: `[TO BE FILLED]`
- Dwell-time metric: `[TO BE FILLED]`
- Irrelevant switching definition: `[TO BE FILLED]`
- Trajectory consistency metric: `[TO BE FILLED]`
- Holdout split: `[TO BE FILLED]`
- Statistical test: `[TO BE FILLED]`
- Null/falsification tests: `[TO BE FILLED]`
- One-command reproduction: `[TO BE FILLED]`

## Paper 4 - Alexithymia

**Backbone**

```text
Affective Signal
-> Identification
-> Representation
-> Labeling
```

**Core diagnostic question**

```text
Where does the CWP-NAP transformation weaken?
```

**Core question**  
Is alexithymia not simply a weak brain region, but an altered neural-state transition architecture in the emotion-information transformation chain?

**Paper type**  
Explanation Paper

**Example transformation chain**

```text
S_affective
-> S_identified
-> S_symbolic
```

**Candidate altered transition**

```text
P(S_identified | S_affective) decreases
```

or:

```text
transition geometry changes
```

**Core hypothesis**  
High-alexithymia individuals may show altered affect-to-identification or affect-to-symbolic transition architecture relative to lower-alexithymia controls.

**Primary analysis focus**

- TAS score.
- State occupancy.
- Transition probability.
- Network integration.
- Dynamic connectivity / state geometry.

**Failure condition**  
If alexithymia does not alter transition probabilities, state occupancy, network integration, dynamic connectivity, or state geometry under the frozen analysis, the altered-transformation explanation is weakened. Exact thresholds are `[DECISION REQUIRED]`.

**One-sentence contribution**  
Describe alexithymia as altered affect-to-representation CWP-NAP transformation architecture.

**Known results**  
`[NOT YET RUN]`

**Missing fields**

- Dataset: `[TO BE FILLED]`
- TAS score source and thresholding strategy: `[TO BE FILLED]`
- Affective signal definition: `[TO BE FILLED]`
- Identification-state definition: `[TO BE FILLED]`
- Symbolic/labeling-state definition: `[TO BE FILLED]`
- CWP-NAP transformation metric: `[TO BE FILLED]`
- Transition-geometry metric: `[TO BE FILLED]`
- Control/group definition: `[TO BE FILLED]`
- Holdout split: `[TO BE FILLED]`
- Statistical test: `[TO BE FILLED]`
- Null/falsification tests: `[TO BE FILLED]`
- One-command reproduction: `[TO BE FILLED]`

## Program-Level Quality Gate

| Gate | Status |
| --- | --- |
| Four Backbones are defined | PASS |
| Shared program question is defined | PASS |
| Framework / Transition / Stability / Impairment structure is defined | PASS |
| Each paper has one core question | PASS |
| Each paper has one Backbone | PASS |
| Each paper has a core hypothesis or prediction | PASS |
| Each paper has a failure condition | PARTIAL |
| Exact datasets are specified | MISSING |
| Exact primary endpoints are specified | PARTIAL |
| Exact statistical tests are specified | MISSING |
| Holdout plans are specified | MISSING |
| Null/falsification tests are specified | MISSING |
| Results are available | NOT YET RUN |
| One-command reproduction is defined | MISSING |
| Unsupported results are invented | PASS - no invented results |

## A1-A10 Packet Status

Each CWP-NAP Multiscale Science paper now has enough structure to begin a paper-specific A1-A10 package, but none is complete.

| Attachment | Current Status |
| --- | --- |
| A1 Frozen Protocol | PARTIAL |
| A2 Dataset Manifest | MISSING |
| A3 Full Pipeline | PARTIAL |
| A4 Full Baseline / Competing-Explanation Results | NOT YET RUN |
| A5 Holdout Audit | MISSING |
| A6 Statistics | MISSING |
| A7 Null / Falsification Tests | MISSING |
| A8 QC & Leakage Audit | MISSING |
| A9 Limitations & Failed Analyses | MISSING |
| A10 One-command Reproduction | MISSING |

## Immediate Next Step

The next protocol decision should be Paper 1's exact framework definitions:

```text
CWP_t
NAP_t
BrainState_t+1 / S_t+1
holdout prediction metric
prediction-improvement threshold
baseline model set
```

Paper 1 should be frozen first because its CWP-NAP definitions and prediction target become dependencies for Insight, Flow, and Alexithymia.
