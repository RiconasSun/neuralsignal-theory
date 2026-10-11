# P9-P12 Ontology v2 Reconstruction Program

Status: active SSOT, updated after P9 completion and P10 negative/boundary result  
Date: 2026-09-06  
Scope: NeuralSignal Institute / CWP-NAP Layer I continuation after P1-P8  
Evidence policy: this document freezes the research architecture only. It does not assert unrun results, dataset performance, p-values, effect sizes, successful replications, or publication readiness.

Unknown or unrun items must remain marked as `[TO BE FILLED]`, `[NOT YET RUN]`, or `[DECISION REQUIRED]`.

## Program Position

P1-P8 narrowed the strongest defensible Layer I claim:

```text
Reproducible computational cognitive neurodynamics remain.
```

They do not currently justify stronger claims such as:

```text
CWP is validated.
NAP is validated.
CWP is a general neural primitive.
CWP-specific cross-dataset superiority is established.
Subject-specific structural connectivity constrains transitions.
Measured physiology has been eliminated as an explanation.
```

Therefore P9-P12 should not "repair" the old ontology by relabeling failures. They should rebuild the ontology from surviving dynamics first.

The original P9-P12 plan was:

```text
Factorization
-> Motif Discovery
-> Semantic Grounding
-> Grammar
```

P10 has now produced a boundary result: the current global discrete-motif model is not supported under the tested P6-derived bandpower feature regime, and a continuous low-dimensional global representation is preferred over global discrete motif reconstruction. This does not decide whether individual regions or networks contain local motif-like dynamics, local continuous manifolds, hybrid regional structure, or hierarchical local-to-global composition.

Therefore P11 and P12 must not use failed global motif identities as semantic atoms, but the downstream route should first add a regional/hierarchical discriminator before freezing any final P11/P12 semantic object.

The updated P9-P12 plan is:

```text
Evidence-bound ontology reset
-> Discrete motif hypothesis test
-> Continuous latent semantic test
-> Continuous dynamical syntax / flow rules
```

The governing shift is:

```text
Old direction:
CWP -> Dynamics

Intermediate direction before P10:
Observable -> State -> Transition -> Motif -> Candidate Primitive -> Semantics

Updated direction after P10:
Observable -> State -> Transition -> Global/Regional/Hierarchical Dynamics Test -> Candidate Latent Object -> Candidate Semantics -> Flow Rules
```

## P9-P12 Route Map

| Paper | Title / Backbone | Primary Role |
| --- | --- | --- |
| P9 | Dynamics-First Ontology Reconstruction | Define a claim-safe ontology and evidence-status system that can encode P1-P8 without contradiction. |
| P10 | Data-Driven Primitive / Dynamic Motif Discovery | Test whether neural dynamics naturally form recurring motif families or are better treated as continuous manifolds. Current result: the global discrete-motif model is not supported under the tested feature regime; global continuous latent dynamics are preferred; regional/hierarchical alternatives remain untested. |
| P10R | Global vs Regional vs Hierarchical Neural Dynamics | Test whether the P10 boundary result reflects global continuity, heterogeneous regional dynamics, local motifs composing into a continuous whole-brain trajectory, or region-specific continuous manifolds with cross-region coupling. |
| P11 | Cognitive Semantics of Continuous or Region-Conditioned Neural Latent Dynamics | Test whether the frozen post-P10/P10R latent objects carry reusable cognitive semantics beyond task labels, metadata, and generic factorization. |
| P12 | Neural Dynamical Syntax / Flow Rules | Test whether continuous latent neural trajectories obey reusable flow rules beyond timing, metadata, and simple dynamical baselines. |

Execution order is fixed:

```text
P9 -> P10 -> P10R -> P11 -> P12
```

P10 requires P9 ontology objects and status rules.  
P10R requires the P10 frozen feature interface and claim audit; it may define region/network partitions before its own final holdout, but may not tune them on final outcomes.  
P11 now requires P10/P10R frozen latent objects and the P10/P10R claim audits, not failed global motif sequences.  
P12 now requires frozen P10/P10R latent trajectories and P11 candidate semantic assignments, not motif-token sequences unless P10R independently supports local motif objects under a frozen claim boundary.

## Shared Paper Contract

Each paper must follow the NSI paper contract:

```text
Hypothesis
-> Dataset
-> Frozen Pipeline
-> Baselines / Competing Explanations
-> Holdout
-> Statistics
-> Null / Falsification Tests
-> QC / Leakage Audit
-> Limitations / Failed Analyses
-> One-command Reproduction
```

Every final paper package should include:

```text
manuscript/
protocol/
attachments/A1_frozen_protocol/
attachments/A2_dataset_manifest/
attachments/A3_full_pipeline/
attachments/A4_baselines_or_competing_explanations/
attachments/A5_holdout_audit/
attachments/A6_statistics/
attachments/A7_null_falsification/
attachments/A8_qc_leakage/
attachments/A9_limitations_failed_analyses/
attachments/A10_one_command_reproduction/
results/
figures/
claim_audit/
```

## P9 - Dynamics-First Ontology Reconstruction

**Paper type:** Method Paper / Framework Paper

**Core question**

```text
How should a new CWP/NAP ontology be defined so that hypotheses, observations, failures, and candidate primitives are not confused?
```

**Core hypothesis**

```text
P1-P8 evidence can be encoded in a dynamics-first ontology without converting unsupported claims into facts.
```

**Backbone**

```text
P1-P8 evidence
-> extract surviving claims
-> extract failed or unsupported claims
-> define ontology objects
-> define evidence-status system
-> define upgrade/downgrade rules
-> build CWP-NAP Ontology v2
```

**Ontology objects**

```text
Observable
Neural State
Transition Family
Dynamic Motif
Candidate NAP
Candidate CWP
Cognitive Program
Context Modifier
Dataset Context
Measurement Regime
Competing Explanation
Claim Boundary
```

**Required evidence-status labels**

```text
OBSERVED
REPRODUCIBLE
OOD_SUPPORTED
EXTERNALLY_REPLICATED
CANDIDATE
NOT_SUPPORTED
UNTESTED
FAILED_PRIMARY_GATE
CONFOUNDED
DATA_BLOCKED
TOOLCHAIN_BLOCKED
```

**Upgrade / downgrade principle**

```text
Objects move upward only by passing preregistered tests.
Objects move downward when primary gates fail, nulls survive, leakage is found, or external holdout fails.
```

**Primary endpoint**

```text
Ontology v2 can represent every major P1-P8 positive result, negative result, blocked test, and limitation without contradiction.
```

**Baselines / competing frameworks**

```text
Old CWP v1 string-label ontology
Flat task-label ontology
Pure continuous dynamics model with no primitives
Generic latent-factor ontology
Task-timing ontology
Dataset-specific ontology
```

**Holdout**

```text
Historical evidence holdout: reserve a subset of P1-P8 claim-audit statements before writing rules, then test whether Ontology v2 can encode them without rule changes.
```

**Null / falsification tests**

```text
Can a random status system encode the evidence as compactly?
Does the ontology accidentally allow disallowed claims?
Does any object receive a stronger status than its evidence permits?
Does the schema force P1-P8 failures into success categories?
```

**Success condition**

```text
Ontology v2 provides a coherent, auditable, non-contradictory language for surviving, failed, and untested P1-P8 claims.
```

**Failure condition**

```text
Ontology v2 cannot encode the evidence without hiding failures, collapsing distinct claims, or granting unsupported statuses.
```

**Allowed conclusion**

```text
A dynamics-first ontology can organize the current evidence boundary and prevent unsupported CWP/NAP claim escalation.
```

**Disallowed conclusion**

```text
CWP/NAP v2 is validated.
Dynamic motifs exist.
Motifs have cognitive semantics.
Neural grammar exists.
```

**Planned artifacts**

```text
paper9/protocol.yaml
paper9/ontology_v2_schema.json
paper9/evidence_matrix.csv
paper9/claim_upgrade_rules.md
paper9/manuscript/manuscript.md
paper9/attachments/A1-A10/
paper9/results/claim_audit.json
```

## P10 - Data-Driven Primitive / Dynamic Motif Discovery

**Paper type:** Method Paper

**Core question**

```text
Do neural dynamics naturally form a small set of recurring motif families, or are they better modeled as a continuous manifold?
```

**Core hypothesis**

```text
Neural dynamics contain recurring motif families that can be discovered without imposing CWP semantics.
```

**Required anti-hypothesis**

```text
Dynamics may be better explained as a continuous manifold with no discrete motif atoms.
```

**Backbone**

```text
EEG / MEG / iEEG / fMRI dynamics
-> latent representation
-> unsupervised segmentation
-> motif discovery
-> recurrence analysis
-> clustering stability
-> cross-subject holdout
-> cross-dataset holdout
```

**Candidate datasets**

```text
EEG: [TO BE FILLED]
MEG: [TO BE FILLED]
iEEG: [TO BE FILLED]
fMRI dynamics: [TO BE FILLED]
```

Dataset choice must be made before any final claim. If only one dataset is available, conclusions must be labeled dataset-specific.

**Models / baselines**

```text
Discrete motif model
Soft mixture model
HMM / switching state-space model
Continuous manifold model
Generic low-rank model
Random segmentation
Task-timing model
Metadata-only model
```

**Holdout**

```text
Train subjects -> held-out subjects
Dataset A -> Dataset B
```

**Primary endpoint**

```text
Held-out recurrence and predictive value of discovered motifs compared with continuous and random baselines.
```

**Null / falsification tests**

```text
phase shuffle
time shuffle
random windows
duration-matched fake motifs
subject shuffle
metadata-only segmentation
task-timing-only segmentation
```

**Success condition**

```text
Small motif families recur in held-out subjects and at least one independent dataset more than null and continuous/generic alternatives.
```

**Boundary-success condition**

```text
Continuous manifold models outperform discrete motif models.
```

This is still a valid scientific result, but it weakens the discrete NAP atom hypothesis.

**Current completed result**

```text
Discrete motif hypothesis: NOT SUPPORTED under the tested feature regime.
Continuous latent dynamics: preferred over discrete motif reconstruction.
Real features beat only 1/3 matched nulls.
External evidence is convergent only, not direct motif replication.
```

**Current allowed conclusion**

```text
Under the tested P6-derived bandpower feature regime, the current global discrete dynamic motif model is not supported; continuous low-dimensional global neural latent dynamics are the better-supported global representation. This does not adjudicate region-specific motif, region-specific continuous-manifold, hybrid, or hierarchical dynamics.
```

**Current disallowed conclusion**

```text
Dynamic motifs exist as validated neural primitives.
Discrete NAP tokens are supported.
P11 can use frozen P10 motif sequences as validated semantic atoms.
P12 can build a motif-token grammar.
P10 proves that no region-specific motifs exist.
P10 proves that every brain region is continuous.
```

**Allowed conclusion if successful**

```text
Candidate neural dynamic motif families exist under the tested measurement regime.
```

**Disallowed conclusion**

```text
Motifs are NAPs.
Motifs have cognitive semantics.
Motifs form grammar.
```

**Planned artifacts**

```text
paper10/protocol.yaml
paper10/dataset_manifest/
paper10/motif_models/
paper10/null_tests/
paper10/results/
paper10/figures/
paper10/manuscript/manuscript.md
paper10/attachments/A1-A10/
paper10/results/claim_audit.json
```

## P10R - Global vs Regional vs Hierarchical Neural Dynamics

**Paper type:** Method Paper

**Core question**

```text
Does the P10 boundary result reflect genuinely continuous whole-brain dynamics, or does global averaging hide heterogeneous regional or hierarchical dynamics?
```

**Core hypothesis**

```text
Different brain regions or networks may have distinct dynamical structure; local motifs or local manifolds may compose asynchronously into an apparently continuous global trajectory.
```

**Required anti-hypotheses**

```text
All tested regions are better modeled as continuous manifolds.
The apparent regional differences are explained by noise, dimensionality, subject/session imbalance, task timing, or metadata.
Local discrete structure does not improve held-out reconstruction, recurrence, or prediction beyond regional continuous and null baselines.
```

**Model classes**

```text
M1: Global continuous model
M2: Region-specific dynamics
    - Regional discrete motif model
    - Regional continuous manifold model
    - Regional soft/switching state-space model
M3: Hierarchical dynamics
    - region latent state -> network latent state -> whole-brain latent state
    - local asynchronous dynamics with global coupling
```

**Region / network partitions**

```text
EEG sensor regions: frontal, central, temporal, parietal, occipital, frontocentral, centroparietal
Alternative atlas/source-space regions: [TO BE FILLED]
Network mapping: [TO BE FILLED]
```

**Primary endpoint**

```text
Held-out reconstruction, recurrence, predictive value, and stability of regional/hierarchical models compared with global continuous, regional continuous, regional discrete, switching-state, task-timing, metadata-only, and matched-null baselines.
```

**Outcome taxonomy**

```text
A: all tested regions continuous
B: some regions discrete and some continuous
C: local discrete dynamics compose into a continuous global trajectory
D: different regions have different continuous manifolds with cross-region coupling
```

**Claim boundary**

```text
P10R may update the downstream object for P11/P12 only after frozen regional/hierarchical holdout and null gates pass.
P10R may not relabel failed P10 global motifs as NAPs.
P10R may not claim region-specific NAPs unless local motif/manifold objects pass independent recurrence, prediction, leakage, and null tests.
```

## P11 - Cognitive Semantics of Continuous or Region-Conditioned Neural Latent Dynamics

**Paper type:** Method Paper with explanation-paper constraints

**Core question**

```text
Do frozen post-P10/P10R neural latent trajectories carry reusable cognitive semantics beyond task labels, metadata, and generic factorization?
```

**Core hypothesis**

```text
Frozen continuous, region-conditioned, or hierarchical latent state, velocity, and trajectory geometry predict cognitive function, behavior, or future neural state in a way that exceeds strong task-label baselines and generic latent-factor controls, especially under OOD evaluation.
```

**Backbone**

```text
P10 frozen continuous latent representation
-> construct z_t, dz/dt, and trajectory-geometry features
-> align latent trajectory segments to task episodes without using labels during representation discovery
-> test semantic prediction for cognitive operations, context, behavior, and neural state
-> OOD cognitive prediction against strong baselines and nulls
```

**New CWP v2 object**

```text
CWP_k_v2 = (
  LatentFactor,
  LatentTrajectoryFeature,
  TrajectoryGeometry,
  ContextModifier,
  SemanticInterpretation,
  EvidenceStatus
)
```

The semantic interpretation is an output of the analysis and annotation process, not a training label used to discover the latent representation.

**Primary latent-dynamics objects**

```text
z_t in R^d
dz_t/dt
curvature / path length / dwell geometry
trajectory direction
transition corridor occupancy
latent-distance-to-context manifolds
```

**Candidate semantic targets**

```text
Maintain
Retrieve
Update
Compare
task context
behavioral response / reaction time when available
future neural state
```

**Baselines / competing explanations**

```text
FlatTask
StrongTask
RandomOntology
Generic matrix factorization
Task embedding
Metadata-only
Old CWP v1
Continuous PCA without semantic grouping
Random latent rotation
Random trajectory segmentation
Time-position baseline
```

**Holdout**

```text
Unseen task
Unseen subject
Unseen dataset when available
```

**Primary endpoint**

```text
OOD prediction of cognitive function, neural state, or behavior by continuous latent-dynamics semantics compared with StrongTask, metadata-only, and Random/GenericFactorization.
```

**Null / falsification tests**

```text
random semantic labels
latent-trajectory shuffle
context shuffle
subject shuffle
task-timing baseline
metadata-only baseline
old-CWP-v1 comparison
random latent rotation
velocity sign/permutation controls
```

**Success condition**

```text
NEW CWP v2 > StrongTask
and
NEW CWP v2 > RandomOntology / GenericFactorization
on OOD tests.
```

**Failure condition**

```text
Continuous latent trajectories do not support cognitive semantics beyond task labels, timing, metadata, or generic factorization.
```

**Allowed conclusion if successful**

```text
Continuous neural latent dynamics support candidate cognitive semantic structure under the tested tasks and datasets.
```

**Disallowed conclusion**

```text
CWP v2 is universal.
Semantics are causal.
Discrete motif semantics exist.
Semantics externally replicate unless explicitly tested.
```

**Planned artifacts**

```text
paper11/protocol.yaml
paper11/semantic_mapping_schema.json
paper11/latent_semantics_schema.json
paper11/baselines/
paper11/holdouts/
paper11/null_tests/
paper11/results/
paper11/figures/
paper11/manuscript/manuscript.md
paper11/attachments/A1-A10/
paper11/results/claim_audit.json
```

## P12 - Neural Dynamical Syntax / Flow Rules

**Paper type:** Method Paper

**Core question**

```text
Do continuous latent neural trajectories obey reusable flow rules, or are their paths explained by simpler timing, metadata, and generic dynamical baselines?
```

**Core hypothesis**

```text
dz_t/dt = F(z_t, Context, Input) improves held-out latent trajectory prediction beyond task labels, timing, metadata, and simple linear/state-space baselines.
```

**Backbone**

```text
Frozen P10 continuous latent trajectories
+ frozen P11 candidate latent semantic assignments
-> trajectory corpus
-> vector-field / flow-rule modeling
-> attractor, branch, loop, and corridor discovery
-> held-out trajectory and OOD flow prediction
```

**Flow-rule targets**

```text
vector field
attractors
branching trajectories
recurrent loops
transition corridors
context-dependent flow
forbidden / low-probability regions
trajectory composition
long-range path dependence
```

**Baselines / competing explanations**

```text
linear autoregression
state-only vector field
task-timing model
metadata-only flow model
context-free continuous SSM
generic Transformer / SSM
random vector field with matched smoothness
shuffled trajectory
time-reversed trajectory
task-timing model
no-semantics trajectory model
```

**Holdout**

```text
Train on Tasks A, B, C -> predict Task D trajectory flow
Held-out subjects
Held-out dataset when available
```

**Primary endpoint**

```text
Held-out latent trajectory prediction, vector-field prediction, and OOD task-flow prediction.
```

**Null / falsification tests**

```text
trajectory-order shuffle
within-task time shuffle
duration-preserving shuffle
context shuffle
subject shuffle
random vector field with matched complexity
metadata-only flow null
```

**Success condition**

```text
Flow-rule model predicts held-out latent trajectories better than timing, task-label, metadata, generic SSM/Transformer, and matched random-flow baselines.
```

**Boundary-success condition**

```text
If linear/state-only, metadata-only, or task-timing models explain the trajectory corpus, the strong flow-rule claim contracts to ordinary transition dynamics.
```

**Allowed conclusion if successful**

```text
Candidate neural dynamical syntax / flow rules exist under the tested measurement regime and task family.
```

**Disallowed conclusion**

```text
Universal neural grammar.
Discrete token grammar.
Causal cognitive grammar.
Human cognition is governed by the discovered flow rules unless separately tested.
```

**Planned artifacts**

```text
paper12/protocol.yaml
paper12/trajectory_corpus_manifest.csv
paper12/flow_models/
paper12/baselines/
paper12/null_tests/
paper12/results/
paper12/figures/
paper12/manuscript/manuscript.md
paper12/attachments/A1-A10/
paper12/results/claim_audit.json
```

## Dependency Graph

```text
P1-P8 evidence boundary
        |
        v
P9 dynamics-first ontology schema
        |
        v
P10 continuous-manifold result; discrete motif claim not supported
        |
        v
P11 candidate continuous-latent semantic mapping
        |
        v
P12 candidate neural dynamical syntax / flow rules
```

Hard dependency rules:

```text
P10 cannot use P11 semantic labels during motif discovery.
P11 cannot reinterpret P10's failed discrete motifs as validated semantic atoms.
P11 cannot change P10 latent representation after OOD evaluation.
P12 cannot change P10 latent representation or P11 semantics to improve flow-rule results.
Any post-holdout changes require a new freeze version and a new final holdout.
```

## Claim Audit Rules

All P9-P12 manuscripts must include a claim audit with these checks:

```text
claim_allowed_dynamic_motifs_exist
claim_allowed_continuous_latent_dynamics_preferred
claim_allowed_discrete_NAP_supported
claim_allowed_CWP_v2_semantics_supported
claim_allowed_neural_grammar_supported
claim_allowed_neural_dynamical_syntax_supported
claim_allowed_external_replication
claim_allowed_universal_theory
```

Default before execution:

```text
claim_allowed_dynamic_motifs_exist: false
claim_allowed_continuous_latent_dynamics_preferred: true after P10 under the tested feature regime
claim_allowed_discrete_NAP_supported: false
claim_allowed_CWP_v2_semantics_supported: false
claim_allowed_neural_grammar_supported: false
claim_allowed_neural_dynamical_syntax_supported: false
claim_allowed_external_replication: false
claim_allowed_universal_theory: false
```

No manuscript may upgrade these fields without a corresponding frozen endpoint, result table, holdout audit, null-test result, and limitations entry.

## Directory Plan

Do not create these directories until implementation begins. When implementation starts, use:

```text
paper9/
paper10/
paper11/
paper12/
```

Each paper should contain:

```text
protocol/
data_manifest/
preprocessing/
models_or_analysis/
holdouts/
null_tests/
statistics/
results/
figures/
manuscript/
attachments/
claim_audit/
```

## One-Command Reproduction Targets

Final target for each paper:

```bash
make reproduce-paper9
make reproduce-paper10
make reproduce-paper11
make reproduce-paper12
```

Optional aggregate target after all four are implemented:

```bash
make reproduce-ontology-v2
```

If restricted datasets cannot be downloaded automatically, the command must fail clearly with authorized data placement instructions. It must not silently substitute toy data for real evidence.

## Program-Level Outcomes

**Best-case outcome after P10**

```text
Continuous Latent Dynamics
-> Candidate Cognitive Semantics
-> Neural Dynamical Syntax / Flow Rules
-> Cognitive Programs
```

**Conservative positive outcome**

```text
Continuous latent dynamics carry reusable cognitive semantics, but flow-rule claims remain candidate-level.
```

**Boundary outcome**

```text
Continuous dynamics outperform discrete motifs; CWP/NAP atom language contracts into computational cognitive neurodynamics.
```

**Failure outcome**

```text
P9 succeeds as a claim-safe ontology, P10 rejects discrete motifs under the tested regime, and P11-P12 fail to support continuous latent semantics or flow rules beyond strong baselines and nulls.
```

All outcomes are scientifically acceptable if reported without claim inflation.
