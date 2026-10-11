# CWP-NAP Foundation Program v2: Six-Paper Architecture

Status: updated Backbone architecture after Paper 1 real E0-E8 results  
Date: 2026-09-01  
Scope: Layer I - CWP Foundations  
Evidence policy: this document distinguishes completed Paper 1 results from planned Papers 2-6. It does not invent sample sizes, p-values, effect sizes, successful replications, or unrun results.

Unknown or unrun items are marked as `[TO BE FILLED]`, `[NOT YET RUN]`, or `[DECISION REQUIRED]`.

## Why v2 Exists

The original five-paper foundation chain was:

```text
CWP Exists
-> CWP Repeats
-> Not Noise
-> Structure Constrains It
-> CWP Has Finer Neural Dynamics
```

Paper 1 has now produced a real constrained result:

```text
Gate A incremental: INCONCLUSIVE
Gate B OOD: PASSED
Gate C external: FAILED
claim_allowed_cwp_foundation_holds: false
claim_allowed_cwp_clearly_outperforms_task_labels: false
```

Therefore Paper 1 no longer supports the strong framing:

```text
CWP Foundation validation
```

The current supported framing is:

```text
CWP-style compositional representations improve within-dataset out-of-distribution brain-state prediction, but do not yet generalize across independent datasets.
```

This failure is scientifically productive because it creates a new independent question:

```text
Why does cross-dataset generalization fail?
```

That question is large enough to become a new Paper 2 rather than a footnote inside Paper 1.

## Updated Six-Paper Chain

```text
P1 Discovery / Boundary Test
-> P2 Failure Mechanism
-> P3 Reproducibility
-> P4 Noise & Falsification
-> P5 Structural Constraint
-> P6 CWP -> NAP Bridge
```

In plain terms:

1. Does a CWP-style compositional representation show any empirical value?
2. Why does the current representation fail across datasets?
3. Are any CWP/state-transition patterns repeatable within sessions, subjects, or datasets?
4. Are the observed transitions real neural signal rather than nuisance structure?
5. Are transitions constrained by individual structural connectomes?
6. Does a seconds-level CWP contain finer NAP-like neural dynamics?

## Shared Paper Contract

Each paper must eventually satisfy the NSI reproducibility chain:

```text
Hypothesis
-> Dataset
-> Frozen Pipeline
-> Baselines / Competing Explanations
-> Holdout
-> Statistics
-> Null/Falsification Tests
-> QC/Leakage Audit
-> Limitations / Failed Analyses
-> One-command Reproduction
```

## P1 - CWP Compositionality / Boundary Test

**Current status**  
Completed through E8 in the current local run.

**Paper type**  
Method Paper.

**Current title**  

```text
CWP-style Compositional Representations Improve Within-dataset Out-of-distribution Brain-state Prediction but Do Not Yet Generalize Across Independent Datasets
```

**Backbone**

```text
Same data + same model capacity + different label representation
```

**Central question**  
Are reusable CWP-style labels more useful than dataset-specific flat task labels for predicting out-of-distribution brain-state transitions?

**Completed result boundary**

```text
Local compositional advantage != general cognitive primitive
```

**Frozen results**

```text
E0 Data/QC Audit: PASS
E1 State Extraction: 2,291 ds001635 states; 3,066 ds001634 states
E2 Stage Sanity: weak under current raw native-grid pipeline
E3 Task vs CWP: Gate A INCONCLUSIVE
E4 Unseen Combination: PASSED
E5 Unseen Domain: PASSED
E6 Available Nulls: true CWP survived sampled pseudo-ontology nulls
E7 External Dataset: Gate C FAILED
E8 Claim Audit: strong CWP foundation claim not allowed
```

**Allowed claim**

```text
CWP-style compositional labels improved within-dataset OOD prediction in ds001635.
```

**Disallowed claims**

```text
CWP is validated.
CWP clearly outperforms task labels overall.
CWP externally replicates.
The 216-ROI grid is a neuroanatomical atlas.
```

**Current manuscript package**

```text
paper1/manuscript/PAPER1_MANUSCRIPT_CURRENT.md
paper1/submission/PAPER1_BIORXIV_DRAFT_CURRENT.pdf
paper1/submission/SUPPLEMENTARY_MATERIAL_CURRENT.pdf
paper1/submission/SUBMISSION_CLAIM_AUDIT.json
```

## P2 - Cross-Dataset Failure / Generalization Mechanism

**Current status**  
New paper inserted after P1. Planned, not yet run.

**Paper type**  
Explanation Paper, with method-style diagnostic ablations.

**Backbone**

```text
External failure
-> shift decomposition
-> failure mechanism
-> revised generalization boundary
```

**Core question**

```text
Why does CWP v1 fail to generalize across independent datasets?
```

**Candidate failure mechanisms**

```text
ontology mismatch
task-design mismatch
stage-timing mismatch
HRF/state-extraction mismatch
native-grid representation mismatch
scanner/preprocessing shift
domain/load distribution shift
subject/cohort shift
true non-generalization of CWP v1
```

**Primary endpoint**  
Contribution of each shift source to the ds001635 -> ds001634 generalization drop: `[TO BE FILLED]`.

**Frozen constraint**

```text
P2 may diagnose why P1 failed externally.
P2 must not tune P1 v1 and then rewrite P1 as externally successful.
```

**Minimum analyses**

```text
1. Ontology alignment audit
2. Stage timing and HRF sensitivity
3. Native-grid vs template/anatomical atlas sensitivity
4. Within-dataset vs cross-dataset performance decomposition
5. Dataset-label prediction / domain-shift classifier
6. Covariate shift and label-distribution shift analysis
7. Failure attribution model
8. New untouched holdout if a CWP v2 redesign is attempted
```

**Baselines / competing explanations**

```text
H0: external failure is caused by implementation artifact
H1: external failure is caused by state-extraction mismatch
H2: external failure is caused by task-design mismatch
H3: external failure is caused by ontology mismatch
H4: external failure is caused by generic dataset/scanner shift
H5: external failure reflects genuine non-generalization of CWP v1
```

**Success criterion**  
The paper succeeds if it identifies and quantifies plausible failure mechanisms, even if CWP v1 remains unsupported.

**Failure criterion**  
The paper fails if it turns into post-hoc tuning without a clean new holdout.

## P3 - Reproducibility

**Current status**  
Planned, not yet run.

**Paper type**  
Method Paper.

**Backbone**

```text
CWP
-> Repeatability
```

**Core question**  
Are CWP-conditioned transitions stable across runs, sessions, subjects, and datasets when the ontology and state extraction are fixed?

**Hypothesis**

```text
Similarity(Transition_same_CWP) > Similarity(Transition_different_CWP)
```

**Dataset candidates**

```text
NSD 7T repeated-measures
HCP retest participants
ds001635 run-level repeats
additional repeated-task OpenNeuro datasets: [TO BE FILLED]
```

**Primary endpoint**  
Within-person and cross-session transition reliability: `[TO BE FILLED]`.

**Critical distinction from P2**  
P2 asks why cross-dataset transfer failed. P3 asks whether any transition structure repeats under better-controlled repeated-measures conditions.

## P4 - Noise & Falsification

**Current status**  
Planned, not yet run.

**Paper type**  
Explanation Paper / falsification-heavy method audit.

**Backbone**

```text
Observed Signal
-> Latent Brain State
```

**Core model**

```text
Y_t = H(S_t) + M_t + epsilon_t
```

Where:

```text
Y_t = observed fMRI
S_t = latent brain state
M_t = motion / physiological / scanner nuisance
epsilon_t = random noise
```

**Core question**  
Are observed CWP/state transitions neural state structure, or are they explainable by motion, physiological signal, scanner drift, timing, or preprocessing artifacts?

**Required nulls**

```text
motion-only model
time-only model
phase / temporal shuffle
label shuffle
spatial rotation
synthetic motion
timing jitter
subject shuffle
boundary perturbation
```

**Connection to P1**  
P1 E6 left motion-only and boundary-jitter nulls incomplete. P4 exists to close that falsification gap in a dedicated study.

## P5 - Structural Constraint

**Current status**  
Planned, not yet run.

**Paper type**  
Method Paper.

**Backbone**

```text
G_i + S_t + CWP
-> S_t+1
```

Where:

```text
G_i = individual structural connectome
```

**Core question**  
Does individual structural connectivity constrain which CWP-conditioned brain-state transitions are likely?

**Hypothesis**

```text
P(S_t+1 | S_t, CWP, G_i) > P(S_t+1 | S_t, CWP)
```

**Dataset candidates**

```text
HCP structural MRI + diffusion MRI + task-fMRI
other multimodal datasets: [TO BE FILLED]
```

**Baselines**

```text
functional-only
group-average connectome
randomized connectome
distance-only network
degree-preserving random network
subject-connectome swap
```

## P6 - CWP -> NAP Bridge

**Current status**  
Planned, not yet run.

**Paper type**  
Explanation Paper.

**Backbone**

```text
CWP
-> NAP_1
-> NAP_2
-> ...
-> NAP_n
```

**Core question**  
Does a seconds-level CWP contain reproducible finer-grained NAP-like neural dynamics?

**Important constraint**

```text
Do not claim CWP = NAP.
Test whether CWP corresponds to a sequence or distribution of NAP-like dynamics.
```

**Dataset candidates**

```text
public EEG datasets
public MEG datasets
public iEEG datasets
human single-unit memory datasets
specific accessions: [TO BE FILLED]
```

**Primary endpoint**  
Whether CWP timing constrains microstate, oscillatory, population-state, or spike-timing transitions beyond static band-power or ERP baselines: `[TO BE FILLED]`.

## Program-Level Claim Discipline

The six-paper program should not be framed as six guaranteed successes. It should be framed as:

```text
A falsifiable research program on whether reusable cognitive work descriptions can explain, predict, constrain, and decompose human brain-state dynamics.
```

Current strongest supported claim:

```text
P1 found within-dataset CWP-style OOD signal but did not validate dataset-invariant CWP.
```

Current strongest open question:

```text
What breaks between ds001635 and ds001634?
```

## Updated Relationship to the 15-Paper Architecture

Layer I should now be treated as six papers rather than five:

```text
Layer I - CWP Foundations: 6 papers
Layer II - CWP-NAP Multiscale Science: 4 papers
Layer III - CNSOS / AI4S: 6 papers
```

This changes the total if Layer II and Layer III remain unchanged:

```text
6 + 4 + 6 = 16 papers
```

Decision required:

```text
Either accept NSI as a 16-paper program,
or merge/drop one downstream paper if the external-facing architecture must remain exactly 15 papers.
```

No automatic deletion is made here.
