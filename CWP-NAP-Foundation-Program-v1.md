# CWP-NAP Foundation Program v1

Status: frozen Backbone architecture for the first five CWP/NAP papers  
Scope: Layer I - CWP Foundations  
Program goal: establish verifiable CWP-conditioned brain-state dynamics  
Evidence policy: this document uses only the provided Backbone content. It does not invent sample sizes, effect sizes, p-values, significance, exact metrics, accession numbers, completed results, or implementation details.

Unknown or unrun items are marked as `[TO BE FILLED]`, `[NOT YET RUN]`, or `[DECISION REQUIRED]`.

## Shared Goal

```text
Establish verifiable CWP-conditioned Brain-State Dynamics
```

The five Backbone papers form one evidence chain:

```text
CWP Exists
-> CWP Repeats
-> Not Noise
-> Structure Constrains It
-> CWP Has Finer Neural Dynamics
```

In plain terms:

1. Does the object exist?
2. Does it repeat?
3. Is it fake/noise/artifact?
4. Why does it move this way?
5. What finer dynamics exist underneath it?

## Shared Paper Contract

Each Backbone paper must eventually satisfy the same scientific contract:

```text
Hypothesis
-> Dataset
-> Frozen Pipeline
-> Baselines
-> Holdout
-> Statistics
-> Null Tests
-> Limitations
-> One-command Reproduction
```

## Shared Missing Decisions

- Exact operational definition of CWP: `[TO BE FILLED]`
- Exact operational definition of brain state S_t: `[TO BE FILLED]`
- Exact state-transition metric or model family: `[TO BE FILLED]`
- CWP annotation procedure: `[TO BE FILLED]`
- Criteria for valid CWP boundaries: `[TO BE FILLED]`
- Primary endpoint per paper: `[TO BE FILLED]`
- Statistical tests per paper: `[TO BE FILLED]`
- Multiple-comparison correction plan: `[TO BE FILLED]`
- Dataset access/version details: `[TO BE FILLED]`
- Cohort inclusion/exclusion rules: `[TO BE FILLED]`
- Reproducibility command: `[TO BE FILLED]`

## Backbone 1 - CWP Foundation

**Question**  
Is CWP a useful cognitive modeling unit?

**Core mapping**

```text
CWP -> Brain State Transition
```

**Paper type**  
Method Paper

**Research question**  
Do reusable CWP labels generalize better than dataset-specific, flat task labels for predicting human brain-state transitions across conditions, tasks, subjects, and datasets?

**Hypothesis**  
Reusable CWP structure predicts S_t+1 beyond strong flat TaskID models and survives OOD, null, and external-replication tests.

**Dataset Backbone**  
OpenNeuro ds001635 for primary CWP discovery, OpenNeuro ds001634 for external holdout, and MDTB ds002105 for final leave-one-entire-task-out generalization. HCP Working Memory and NSD remain context or later validation options. Specific release/version/access details remain citation-pending.

**Frozen pipeline**

```text
same data + same model capacity + same preprocessing + same prediction target
-> change only label representation
-> predict S_t+1
-> test unseen combinations/domains/tasks/datasets
```

**Model comparison**

```text
M0: S_hat_t+1 = A S_t
M1 Flat Task Label: S_hat_t+1 = F(S_t, TaskID)
M2 Strong Task Baseline: S_hat_t+1 = F(S_t, TaskID, Domain, Load)
M3 CWP Model: S_hat_t+1 = F(S_t, CWP, Domain, Load)
M4 Task + CWP: S_hat_t+1 = M2 + CWP residual
```

Primary comparison:

```text
M4 > M2
```

This tests whether CWP adds predictive information beyond the strongest task-label baseline, not only beyond weak one-hot labels.

**Baselines**

- Static activation.
- Task-label model.
- History-only model.
- Simple linear/state-space model.
- Fixed trial-position baseline.
- Random/time boundary baselines.

**Holdout**

- Unseen combination.
- Unseen domain.
- Unseen task / dataset.
- Cross-run holdout.
- Cross-subject holdout.
- ds001634 external dataset holdout.
- MDTB leave-one-entire-task-out test.

Evidence strength:

```text
Unseen Combination < Unseen Domain < Unseen Task / Dataset
```

**Core result target**

```text
P(S_t+1 | S_t, CWP, Context) > P(S_t+1 | S_t, TaskLabel)
```

and:

```text
Similarity(Delta S | Same CWP, Different Task)
>
Similarity(Delta S | Different CWP)
```

**Null tests**

- CWP label shuffle.
- Random boundaries with matched durations.
- Circular time shift.
- Operation-label shuffle.
- Subject shuffle.
- Motion/confound-only prediction.
- Fixed trial-position baseline.

**Meaning**  
Tests whether CWP's value is better generalization rather than better memorization of dataset-specific task labels.

**Known results**  
`[NOT YET RUN]`

**Missing fields**

- Exact OpenNeuro ds001635 release/version/access details: `[TO BE FILLED]`
- Exact OpenNeuro ds001634 release/version/access details: `[TO BE FILLED]`
- Exact MDTB ds002105 release/version/access details: `[TO BE FILLED]`
- CWP annotation protocol: `[TO BE FILLED]`
- Brain-state representation S_t: `[TO BE FILLED]`
- Model family for P(S_t+1 | ...): `[TO BE FILLED]`
- Primary metric, preferably held-out predictive log-likelihood / ELPD: `[TO BE FILLED]`
- Statistical test for the core result target: `[TO BE FILLED]`
- Effect size and CI: `[NOT YET RUN]`
- HRF/time-delay modeling policy: `[TO BE FILLED]`
- One-command reproduction: `[TO BE FILLED]`

## Backbone 2 - CWP Reproducibility

**Question**  
Is the transition real, or just a one-scan coincidence?

**Core mapping**

```text
CWP -> Repeatability
```

**Paper type**  
Explanation Paper

**Research question**  
Do CWP-conditioned transitions repeat across sessions and individuals?

**Hypothesis**

```text
Similarity(Transition_same CWP) > Similarity(Transition_different CWP)
```

The same relation should also hold across different sessions within the same individual.

**Dataset**  
NSD 7T deep repeated-measures.

**Frozen pipeline**

```text
Repeated CWP
-> Individual State Models
-> Session Alignment
-> Reproducibility
```

**Baselines**

- Random trial matching.
- Generic task-average.
- Subject-independent model.

**Holdout**  
Entire held-out session.

**Statistics**

- Within-person reliability.
- Between-person generalization.
- Effect size + CI.

**Null tests**

- Session shuffle.
- Stimulus shuffle.
- Subject shuffle.

**Meaning**  
Tests whether CWP transition is a stable phenomenon rather than an attractive one-off pattern.

**Known results**  
`[NOT YET RUN]`

**Missing fields**

- NSD release/version/access details: `[TO BE FILLED]`
- CWP repetition definition: `[TO BE FILLED]`
- Session alignment method: `[TO BE FILLED]`
- Transition similarity metric: `[TO BE FILLED]`
- Reliability statistic: `[TO BE FILLED]`
- Generalization endpoint: `[TO BE FILLED]`
- Effect size and CI values: `[NOT YET RUN]`
- One-command reproduction: `[TO BE FILLED]`

## Backbone 3 - Noise / Falsification

**Question**  
Could the observed state transition actually be noise?

**Core mapping**

```text
Observed Signal -> Latent Brain State
```

**Observation model**

```text
Y_t = H(S_t) + M_t + epsilon_t
```

where:

- `Y_t`: observed fMRI.
- `S_t`: true latent state.
- `M_t`: motion / physiological / scanner nuisance.
- `epsilon_t`: random noise.

**Paper type**  
Explanation Paper

**Research question**  
Do CWP-conditioned transitions remain detectable after controlling for, modeling, and injecting noise/artifact sources?

**Hypothesis**  
After controlling for or injecting noise, true CWP transitions remain significantly above null.

**Dataset**  
NSD + HCP.

**Frozen pipeline**

```text
Raw
-> QC
-> Nuisance Modeling
-> Latent State
-> Transition
```

**Baselines**

- Standard denoising.
- No-denoising.
- Naive dynamic connectivity.
- Simple autoregression.

**Holdout**  
Unseen subjects + unseen corruption levels.

**Null tests**

- Time shuffle.
- Phase shuffle.
- Label shuffle.
- Spatial rotation.
- Synthetic motion.
- Timing jitter.
- Subject shuffle.

**Meaning**  
Tests whether the first two Backbone findings are produced by motion, respiration, scanner drift, or other artifacts.

**Known results**  
`[NOT YET RUN]`

**Missing fields**

- Exact NSD/HCP versions: `[TO BE FILLED]`
- QC thresholds: `[TO BE FILLED]`
- Nuisance model specification: `[TO BE FILLED]`
- Latent-state model: `[TO BE FILLED]`
- Synthetic corruption protocol: `[TO BE FILLED]`
- Definition of "significantly above null": `[TO BE FILLED]`
- Statistical test and correction plan: `[TO BE FILLED]`
- One-command reproduction: `[TO BE FILLED]`

## Backbone 4 - Structural Constraint

**Question**  
Why does the state move from S_t to one specific S_t+1 rather than anywhere?

**Core mapping**

```text
G_i + S_t + CWP -> S_t+1
```

where:

```text
G_i = individual structural connectome
```

**Paper type**  
Explanation Paper

**Research question**  
Does the individual structural connectome constrain CWP-conditioned brain-state transitions?

**Hypothesis**

```text
P(S_t+1 | S_t, CWP, G_i) > P(S_t+1 | S_t, CWP)
```

**Dataset**  
HCP structural MRI + diffusion MRI + task-fMRI.

**Frozen pipeline**

```text
dMRI -> G_i
fMRI -> S_t

(G_i, S_t, CWP) -> S_t+1
```

**Baselines**

- Functional-only.
- Group-average connectome.
- Randomized connectome.
- Distance-only network.

**Holdout**  
Held-out subjects.

**Null tests**

- Edge shuffle.
- Degree-preserving random networks.
- Subject-connectome swap.

**Meaning**  
Tests whether CWP dynamics can be linked to individual structural brain constraints.

**Known results**  
`[NOT YET RUN]`

**Missing fields**

- HCP structural/dMRI/task-fMRI versions: `[TO BE FILLED]`
- Structural connectome construction method: `[TO BE FILLED]`
- Parcellation: `[TO BE FILLED]`
- Transition model using G_i: `[TO BE FILLED]`
- Evaluation metric for improvement over no-G_i model: `[TO BE FILLED]`
- Statistical test and CI plan: `[TO BE FILLED]`
- One-command reproduction: `[TO BE FILLED]`

## Backbone 5 - CWP to NAP Bridge

**Question**  
Inside a seconds-scale CWP, is there finer-grained neural dynamics?

**Core mapping**

```text
CWP -> NAP_1 -> NAP_2 -> ... -> NAP_n
```

This paper does not assert:

```text
CWP = NAP
```

It tests whether:

```text
CWP ?= Sequence/Distribution of NAP-like Dynamics
```

**Paper type**  
Explanation Paper

**Research question**  
Can a seconds-scale CWP be empirically linked to a sequence or distribution of finer-grained NAP-like neural dynamics?

**Hypothesis**  
Within a CWP timing window, electrophysiological data should show reproducible oscillation, population-state, or microstate-transition structure consistent with NAP-like dynamics.

**Dataset**  
Public EEG / MEG / iEEG / human single-unit memory datasets.

**Frozen pipeline**

```text
CWP timing
-> Electrophysiology
-> Oscillation/Population State
-> Microstate Transition
```

**Baselines**

- Band-power only.
- Event-related potential.
- Static decoding.
- Random segmentation.

**Holdout**

- Trials.
- Sessions.
- Subjects.
- Dataset-level external holdout, preferably.

**Null tests**

- Phase randomization.
- Spike-time jitter.
- Temporal permutation.
- Fake CWP boundaries.

**Meaning**  
Builds the first empirical bridge between CWP and NAP.

**Known results**  
`[NOT YET RUN]`

**Missing fields**

- Exact EEG/MEG/iEEG/single-unit datasets: `[TO BE FILLED]`
- CWP timing source and alignment method: `[TO BE FILLED]`
- NAP-like operational definition: `[TO BE FILLED]`
- Oscillation/population-state/microstate features: `[TO BE FILLED]`
- External holdout dataset choice: `[DECISION REQUIRED]`
- Statistical test and correction plan: `[TO BE FILLED]`
- One-command reproduction: `[TO BE FILLED]`

## Program-Level Quality Gate

| Gate | Status |
| --- | --- |
| Five Backbones are defined | PASS |
| Shared program goal is defined | PASS |
| Shared paper contract is defined | PASS |
| Each Backbone has a research question | PASS |
| Each Backbone has a hypothesis | PASS |
| Each Backbone has a dataset family | PASS |
| Each Backbone has a frozen-pipeline outline | PASS |
| Each Backbone has baselines | PASS |
| Each Backbone has holdout logic | PASS |
| Each Backbone has null tests | PASS |
| Exact primary endpoints are specified | MISSING |
| Exact datasets/releases/accession IDs are specified | MISSING |
| Sample/subject counts are specified | MISSING |
| Statistical tests are fully specified | PARTIAL |
| Effect sizes and CIs are available | NOT YET RUN |
| Results are available | NOT YET RUN |
| One-command reproduction is defined | MISSING |
| Unsupported results are invented | PASS - no invented results |

## A1-A10 Packet Status

Each Backbone now has enough structure to begin a paper-specific A1-A10 package, but none is complete.

| Attachment | Current Status |
| --- | --- |
| A1 Frozen Protocol | PARTIAL |
| A2 Dataset Manifest | MISSING |
| A3 Full Pipeline | PARTIAL |
| A4 Full Baseline Results | NOT YET RUN |
| A5 Holdout Audit | PARTIAL |
| A6 Statistics | PARTIAL |
| A7 Null / Falsification Tests | PARTIAL |
| A8 QC & Leakage Audit | PARTIAL |
| A9 Limitations & Failed Analyses | MISSING |
| A10 One-command Reproduction | MISSING |

## Immediate Next Step

The next protocol decision should be Backbone 1's exact operational definition:

```text
CWP Annotation
S_t representation
S_t+1 prediction target
primary endpoint
held-out subject/session split
```

Backbone 1 should be frozen first because its CWP definition and transition target become dependencies for Backbones 2-5.
