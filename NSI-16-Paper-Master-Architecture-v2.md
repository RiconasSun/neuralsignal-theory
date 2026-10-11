# NSI 16-Paper Master Architecture v2

Status: updated master architecture after Paper 1 real E0-E8 results  
Date: 2026-09-01  
Evidence policy: completed Paper 1 results are recorded from the local claim audit. Planned papers do not assert unrun results, sample sizes, p-values, effect sizes, successful replications, or repository/publication status.

Unknown or unrun items are marked as `[TO BE FILLED]`, `[NOT YET RUN]`, or `[DECISION REQUIRED]`.

## Program Thesis

A three-layer computational cognitive neuroscience and AI-for-Science research program comprising 16 independent, falsifiable, reproducible studies.

The program is organized as:

```text
16 Papers = 6 + 4 + 6
```

```text
Layer I: Build, stress-test, and revise the representation
Layer II: Use it to understand brain and cognition
Layer III: Build AI systems to discover and attack the science
```

The key update from the 15-paper architecture is that Paper 1 produced a real boundary result:

```text
CWP-style compositional representations improve within-dataset out-of-distribution brain-state prediction,
but do not yet generalize across independent datasets.
```

That external failure creates a new scientific paper:

```text
Paper 2: Why does cross-dataset generalization fail?
```

Therefore Layer I becomes six papers rather than five.

## Layer Map

| Layer | Papers | Core Task |
| --- | ---: | --- |
| Layer I - CWP Foundations | 6 | Build, test, falsify, explain failure modes, and ground CWP-style brain-state dynamics. |
| Layer II - CWP-NAP Multiscale Science | 4 | Build the CWP-to-NAP bridge and test whether it explains specific neural/cognitive phenomena. |
| Layer III - CNSOS / AI4S | 6 | Turn the first two layers into a testbed for automated scientific discovery. |

## Program-Level Story

```text
Layer I: Define a representation, test it, discover its boundary, and explain that boundary.
-> Layer II: Use the surviving/revised representation to explain cognitive phenomena.
-> Layer III: Build AI systems that generate, test, falsify, and revise the science.
```

This is no longer a clean success-only architecture. The program explicitly allows:

```text
hypothesis
-> holdout
-> falsification
-> failure mechanism
-> revised hypothesis
```

That is the reason the 16-paper architecture is stronger than the original 15-paper version.

## Global Known Inputs

- The updated program contains 16 papers.
- The architecture is three-layered: 6 + 4 + 6.
- Layer I focuses on CWP Foundations and now includes an explicit cross-dataset failure/generalization paper.
- Layer II remains the four-paper CWP-NAP Multiscale Science program.
- Layer III remains the six-paper CNSOS / AI4S program.
- Paper 1 has completed E0-E8 locally and supports only a constrained claim.

## Global Missing Inputs

- Final public repository URL: `[TO BE FILLED]`
- Author list and affiliations: `[TO BE FILLED]`
- Dataset choices for Papers 2-16: `[TO BE FILLED]`
- Dataset versions or accession IDs for Papers 2-16: `[TO BE FILLED]`
- Subject/sample counts for Papers 2-16: `[NOT YET RUN]`
- Inclusion/exclusion criteria for Papers 2-16: `[TO BE FILLED]`
- Exact CWP v2 operational definition: `[TO BE FILLED]`
- Exact NAP operational definition: `[TO BE FILLED]`
- Structural connectome source and construction method: `[TO BE FILLED]`
- CNSOS system definition: `[TO BE FILLED]`
- AI agent roles and implementation boundaries: `[TO BE FILLED]`
- Frozen preprocessing pipelines for Papers 2-16: `[TO BE FILLED]`
- Train/validation/holdout split logic for Papers 2-16: `[TO BE FILLED]`
- Statistical models and tests for Papers 2-16: `[TO BE FILLED]`
- Baselines or competing explanations per planned paper: `[TO BE FILLED]`
- Null/falsification tests per planned paper: `[TO BE FILLED]`
- Known results for Papers 2-16: `[NOT YET RUN]`
- Failed analyses for Papers 2-16: `[NOT YET RUN]`
- Reproduction command per planned paper: `[TO BE FILLED]`

## Layer I - CWP Foundations: 6 Papers

Layer I question:

```text
Can reusable cognitive work descriptions predict, generalize, survive falsification, and connect to neural/structural mechanisms?
```

### Paper 1 - CWP Compositionality / Boundary Test

**Paper type:** Method Paper

**Current status:** Completed local E0-E8 run.

**Current title:**

```text
CWP-style Compositional Representations Improve Within-dataset Out-of-distribution Brain-state Prediction but Do Not Yet Generalize Across Independent Datasets
```

**Backbone**

```text
same data + same model capacity + same prediction target
-> change only label representation
```

**Core finding**

```text
Local compositional advantage != general cognitive primitive
```

**Completed gate status**

```text
Gate A incremental: INCONCLUSIVE
Gate B OOD: PASSED
Gate C external: FAILED
claim_allowed_cwp_foundation_holds: false
claim_allowed_cwp_clearly_outperforms_task_labels: false
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

**Current artifacts**

```text
paper1/manuscript/PAPER1_MANUSCRIPT_CURRENT.md
paper1/submission/PAPER1_BIORXIV_DRAFT_CURRENT.pdf
paper1/submission/SUPPLEMENTARY_MATERIAL_CURRENT.pdf
paper1/submission/SUBMISSION_CLAIM_AUDIT.json
```

### Paper 2 - Cross-Dataset Failure / Generalization Mechanism

**Paper type:** Explanation Paper with diagnostic method ablations

**Current status:** Planned, not yet run.

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

**Candidate mechanisms**

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

**Frozen constraint**

```text
P2 may explain P1's external failure.
P2 must not tune P1 v1 and then rewrite P1 as externally successful.
```

**Primary endpoint:** `[TO BE FILLED]`

**Known results:** `[NOT YET RUN]`

**Current protocol package**

```text
paper2/protocol/PAPER2_FROZEN_PROTOCOL_v1.md
paper2/attachments/ATTACHMENT_INDEX.md
```

### Paper 3 - Reproducibility

**Paper type:** Method Paper

**Current status:** Planned, not yet run.

**Backbone**

```text
CWP
-> Repeatability
```

**Core question**  
Are CWP-conditioned transitions stable across sessions, subjects, runs, and repeated measurements?

**Hypothesis**

```text
Similarity(Transition_same_CWP) > Similarity(Transition_different_CWP)
```

**Dataset candidates**

```text
NSD repeated-measures
HCP retest participants
ds001635 run-level repeats
additional repeated-task OpenNeuro datasets: [TO BE FILLED]
```

**Known results:** `[NOT YET RUN]`

### Paper 4 - Noise & Falsification

**Paper type:** Explanation Paper / falsification-heavy method audit

**Current status:** Planned, not yet run.

**Backbone**

```text
Observed Signal
-> Latent Brain State
```

**Core model**

```text
Y_t = H(S_t) + M_t + epsilon_t
```

**Core question**  
Are observed CWP/state transitions real neural state structure, or are they explainable by motion, physiology, scanner drift, timing, or preprocessing artifacts?

**Connection to P1**  
P1 E6 left motion-only and boundary-jitter nulls incomplete. P4 exists to close that falsification gap.

**Known results:** `[NOT YET RUN]`

### Paper 5 - Structural Constraint

**Paper type:** Method Paper

**Current status:** Planned, not yet run.

**Backbone**

```text
G_i + S_t + CWP
-> S_t+1
```

**Core question**  
Does individual structural connectivity constrain CWP-conditioned brain-state transitions?

**Hypothesis**

```text
P(S_t+1 | S_t, CWP, G_i) > P(S_t+1 | S_t, CWP)
```

**Dataset candidates**

```text
HCP structural MRI + diffusion MRI + task-fMRI
other multimodal datasets: [TO BE FILLED]
```

**Known results:** `[NOT YET RUN]`

### Paper 6 - CWP -> NAP Bridge

**Paper type:** Explanation Paper

**Current status:** Planned, not yet run.

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

**Constraint**

```text
Do not claim CWP = NAP.
Test whether CWP corresponds to a sequence or distribution of NAP-like dynamics.
```

**Known results:** `[NOT YET RUN]`

## Layer II - CWP-NAP Multiscale Science: 4 Papers

Layer II question:

```text
Can cognitive phenomena be explained as regimes of CWP-conditioned neural dynamics?
```

Layer II structure:

```text
Framework
-> Transition
-> Stability
-> Impairment
```

### Paper 7 - CWP-NAP Framework

**Paper type:** Method Paper

**Backbone**

```text
CWP_t
-> NAP_t
-> BrainState_t+1
```

**Core question**  
Can cognitive work state CWP systematically constrain subsequent neural activity pattern NAP and brain-state transition?

**Known results:** `[NOT YET RUN]`

### Paper 8 - Insight

**Paper type:** Explanation Paper

**Backbone**

```text
Search
-> Precursor NAP
-> Abrupt Transition
-> Insight
```

**Core question**  
Is insight a predictable abrupt CWP-NAP state transition rather than a random instant?

**Known results:** `[NOT YET RUN]`

### Paper 9 - Flow

**Paper type:** Explanation Paper

**Backbone**

```text
Task CWP
-> Stable NAP Manifold
-> Low Switching
-> Flow
```

**Core question**  
Does flow correspond to an unusually stable, low-switching-cost task-conditioned neural trajectory?

**Known results:** `[NOT YET RUN]`

### Paper 10 - Alexithymia

**Paper type:** Explanation Paper

**Backbone**

```text
Affective Signal
-> Identification
-> Representation
-> Labeling
```

**Core question**

```text
Where does the CWP-NAP transformation weaken?
```

**Known results:** `[NOT YET RUN]`

## Layer III - CNSOS / AI4S: 6 Papers

Layer III question:

```text
Can AI systems partially automate real scientific discovery while preserving falsification, leakage control, and theory revision?
```

Layer III structure:

```text
Framework
-> Discover
-> Hypothesize
-> Design
-> Falsify
-> Closed Loop
```

### Paper 11 - CNSOS Framework

**Paper type:** Method Paper

**Core question**  
Can CNSOS reliably execute a complete scientific workflow?

**Known results:** `[NOT YET RUN]`

### Paper 12 - Automated Pattern Discovery

**Paper type:** Method Paper

**Core question**  
Can AI discover replicable structures that human analysts missed?

**Known results:** `[NOT YET RUN]`

### Paper 13 - Automated Hypothesis Generation

**Paper type:** Method Paper

**Core question**  
Do AI-generated hypotheses have higher empirical yield than random or template baselines?

**Known results:** `[NOT YET RUN]`

### Paper 14 - Automated Experiment Design

**Paper type:** Method Paper

**Core question**  
Can AI generate executable, statistically valid, leakage-resistant experiments?

**Known results:** `[NOT YET RUN]`

### Paper 15 - Automated Falsification

**Paper type:** Method Paper

**Core question**  
Can a red-team agent reduce false discovery without eliminating true positives?

**Known results:** `[NOT YET RUN]`

### Paper 16 - Closed-Loop Autonomous Discovery

**Paper type:** Method Paper

**Backbone**

```text
Data
-> Discovery
-> Hypothesis
-> Experiment
-> Falsification
-> Theory Update
-> Replication
```

**Core question**  
Can an AI system complete a full scientific discovery loop under constrained, auditable conditions?

**Known results:** `[NOT YET RUN]`

## Current Highest-Priority Next Step

P1 is now a manuscript/submission package. The next scientific paper should be P2:

```text
Cross-Dataset Failure / Generalization Mechanism
```

Before running P2, freeze:

```text
P2 research question
failure mechanisms
shift-decomposition endpoints
datasets
preprocessing alternatives
holdout policy
claim boundaries
one-command reproduction target
```

P2's core rule:

```text
Explain failure. Do not rescue P1 post hoc.
```
