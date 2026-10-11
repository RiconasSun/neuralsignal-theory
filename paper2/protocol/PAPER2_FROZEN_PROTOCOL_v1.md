# Paper 2 Frozen Protocol v1

Title: Cross-Dataset Failure and Generalization of CWP-style Brain-State Models

Status: frozen protocol draft  
Date: 2026-09-01  
Paper type: Explanation Paper with diagnostic method ablations  
Evidence policy: this protocol contains planned analyses only. No Paper 2 results have been run yet. Do not infer success.

## Core Question

Why did Paper 1 show within-dataset CWP-style OOD signal in ds001635, but fail external validation on ds001634?

```text
Local CWP Signal
-> External Failure
-> Failure Decomposition
-> Generalization Test
```

This paper is not a rescue attempt for Paper 1. It studies the source of the cross-dataset failure.

The sharpened Paper 2 question is:

```text
Does semantic ontology matter beyond generic compositional structure?
```

If a random or pseudo ontology performs as well as the semantic CWP ontology, then the result cannot be interpreted as CWP-specific generalization. It may instead reflect label compression, parameterization, regularization, or representation geometry.

## Non-Negotiable Boundary

```text
P2 may explain P1 external failure.
P2 must not tune P1 v1 and then rewrite P1 as externally successful.
```

Dataset B, ds001634, has already been used as a failed external validation dataset in Paper 1. Therefore it becomes a failure-analysis dataset in Paper 2, not a final independent holdout.

## Starting Fact from Paper 1

Paper 1 completed E0-E8 locally.

```text
Gate A incremental: INCONCLUSIVE
Gate B OOD: PASSED
Gate C external: FAILED
claim_allowed_cwp_foundation_holds: false
claim_allowed_cwp_clearly_outperforms_task_labels: false
```

Supported Paper 1 conclusion:

```text
CWP-style compositional representations improve within-dataset out-of-distribution brain-state prediction,
but do not yet generalize across independent datasets.
```

## Hypothesis

External failure can be decomposed into candidate sources:

```text
F_external = F_measurement + F_state + F_task + F_ontology
```

### H1 - Measurement Shift

Scanner, preprocessing, SNR, temporal filtering, HRF, or nuisance differences make the extracted state spaces non-comparable:

```text
S^A not approximately S^B
```

### H2 - Representation Shift

The Paper 1 native image-space 216-ROI grid does not provide cross-dataset invariant brain-state features.

### H3 - Task / Context Shift

The datasets share coarse labels such as ENCODE, MAINTAIN, and PROBE, but the underlying task contexts differ enough that transfer degrades.

### H4 - CWP Non-Invariance

The strongest counter-hypothesis:

```text
Encode_A != Encode_B
```

The CWP label itself may not correspond to a stable cross-dataset neural operation.

## Datasets

### Dataset A - ds001635

Role:

```text
Source domain / Paper 1 development dataset
```

Known from Paper 1 local audit:

```text
48 events files
48 BOLD files
16 subjects x 3 runs
2,291 extracted ENCODE/MAINTAIN/PROBE states
```

### Dataset B - ds001634

Role:

```text
Failure-analysis dataset
```

Known from Paper 1 local audit:

```text
57 events files
57 BOLD files
3,066 extracted ENCODE/MAINTAIN/PROBE states
```

Important:

```text
Dataset B is no longer a clean final holdout because Paper 1 already observed its failure.
```

### Dataset C - Never-Seen Final External Holdout

Role:

```text
Final external holdout
```

Requirements:

```text
public working-memory or memory fMRI dataset
explicit Encoding / Maintenance / Retrieval-or-Probe phases
available event timing
available BOLD data
usable subject/run structure
not inspected for final CWP performance before P2 v2 pipeline is frozen
```

Dataset C identifier:

```text
OpenNeuro ds004469 v1.1.3
Dataset DOI: doi:10.18112/openneuro.ds004469.v1.1.3
Dataset name: Temporal Lobe Epilepsy - UNAM
```

Dataset C lock status:

```text
LOCKED_AND_EVALUATED_ONCE
```

Frozen Dataset C stage mapping:

```text
Coding -> ENCODE
Retention -> MAINTAIN
Test -> PROBE
```

Boundary:

```text
Dataset C can test stage-level cross-dataset transfer.
Dataset C cannot test TRANSFORM because no manipulation phase is exposed in the audited event files.
Dataset C final performance has not been inspected.
```

## Frozen Pipeline

```text
E9.0 Reproduce Failure
-> E9.1 Measurement Shift
-> E9.2 State Representation Shift
-> E9.3 Task-Context Shift
-> E9.4 Ontology Stress Test
-> E9.5 Failure Attribution
-> E9.6 Frozen v2 Representation
-> E9.7 Dataset C Final Holdout
-> E9.8 Statistics + Claim Audit
```

## Experiment E9.0 - Reproduce Failure

Goal:

```text
Reproduce Train(ds001635) -> Test(ds001634) failure from Paper 1.
```

Stop rule:

```text
If P1 external failure cannot be reproduced, pause P2 scientific inference and repair reproduction first.
```

Expected input:

```text
paper1/state_extraction/stage_states.csv
paper1/external_validation/stage_states_external.csv
paper1/results/claim_audit.json
```

Output:

```text
paper2/results/e9_0_failure_reproduction_summary.json
```

## Experiment E9.1 - Measurement Shift

Goal:

```text
Test whether measurement alignment alone improves A -> B transfer without changing CWP ontology.
```

Interventions:

```text
spatial normalization
ROI atlas harmonization
intensity scaling
nuisance strategy
temporal filtering
HRF modeling
state normalization
```

Comparison:

```text
Raw Transfer
vs
MeasurementAligned Transfer
```

Interpretation rule:

```text
If transfer substantially recovers without ontology changes, external failure is at least partly measurement/domain shift.
```

## Experiment E9.2 - State Representation Shift

Goal:

```text
Identify which brain-state representation is most stable across datasets.
```

Representations:

```text
R0 native-grid / current 216 ROI
R1 unified atlas
R2 network-level representation
R3 subject-normalized latent state
R4 dataset-adversarial or invariant latent state
```

Constraint:

```text
Model capacity must be controlled across representations.
```

## Experiment E9.3 - Task-Context Shift

Goal:

```text
Test whether transfer depends on task-context similarity.
```

Task descriptor:

```text
C = {
  stimulus,
  load,
  duration,
  instruction,
  response,
  memory_demand,
  sensory_modality
}
```

Primary relation:

```text
TransferPerformance ~ TaskSimilarity
```

Interpretation rule:

```text
If more similar contexts transfer better, CWP is not context-free and should be modeled as CWP(C).
```

## Experiment E9.4 - Ontology Stress Test

Goal:

```text
Quantify the generalization/complexity trade-off across CWP ontology granularity.
```

Ontologies:

```text
Too coarse: ENCODE / MAINTAIN / PROBE
Medium: VISUAL_ENCODE / WM_MAINTAIN / TRANSFORM / RETRIEVE_COMPARE
Fine: more task-specific primitives
Random: matched pseudo-ontology
```

Candidate revised form:

```text
CWP = CoreOperation + ContextModifier
```

## Experiment E9.5 - Failure Attribution

Goal:

```text
Estimate each shift source's contribution to the external performance drop.
```

Attribution model:

```text
Delta ExternalPerformance
= Delta Measurement
+ Delta StateRepresentation
+ Delta Context
+ Delta Ontology
```

Ablation ladder:

```text
all closed
+ Measurement
+ State Alignment
+ Context
+ Ontology
```

This is the main Paper 2 figure.

## Experiment E9.6 - Frozen v2 Representation

Goal:

```text
Freeze a revised representation before evaluating Dataset C.
```

Allowed:

```text
Use Dataset A and Dataset B for failure diagnosis and v2 design.
```

Forbidden:

```text
Inspect final Dataset C performance before v2 is frozen.
```

## Experiment E9.7 - Dataset C Final Holdout

Goal:

```text
Test frozen v2 on a never-seen external dataset.
```

Comparison:

```text
CWP_v1
vs
CWP_v2
vs
Strong Task Baseline
vs
Random/Pseudo Ontology
```

This is the only clean external replication test for Paper 2.

Observed result from current run:

```text
Dataset C: OpenNeuro ds004469 v1.1.3
Dataset C states extracted: 2,268
Dataset C transitions evaluated: 1,512
M2_strong_task MSE: 15411126.594459493
M3_cwp v1 MSE: 16937784.139945235
CWP_v2_medium MSE: 16921457.350479256
RandomOntology MSE: 20533230.666308556
CWP_v2_medium beat RandomOntology: yes
CWP_v2_medium beat M2_strong_task: no
Status: DATASET_C_CWP_SPECIFIC_NOT_SUPPORTED
```

Interpretation boundary:

```text
This result does not allow the claim that CWP was rescued or that CWP-specific cross-dataset generalization is supported.
```

## Experiment E9.8 - Statistics + Claim Audit

Goal:

```text
Aggregate results, compute subject-level statistics, run claim audit, and generate paper-ready outputs.
```

## Baselines

Required baselines:

```text
Raw transfer
dataset-specific task model
simple z-score alignment
CORAL / simple domain adaptation
Procrustes alignment
shared PCA/CCA latent space
task-label model
CWP v1
random ontology
task-context-only model
```

## Primary Metric

Primary:

```text
external predictive performance
```

Candidate metrics:

```text
predictive log likelihood
MSE
R2
cosine similarity
```

Primary metric final choice:

```text
MSE for the current implemented run; R2 and cosine similarity are reported as secondary metrics.
```

## Statistics

Required:

```text
subject-level paired comparison
bootstrap 95% CI
permutation / sign-flip tests
effect size
FDR correction
```

Do not treat trials or TRs as independent people.

## Null Tests

Required nulls:

```text
dataset label shuffle
CWP shuffle
pseudo ontology
random alignment
random ROI correspondence
task-context shuffle
subject permutation
alignment improves everything null
```

Important null:

```text
If alignment improves Task model, random ontology, and CWP equally, the result is not CWP-specific.
```

## Success Gates

### Gate A - Failure Explained

At least one preregistered factor explains the A -> B performance drop.

### Gate B - v2 Improvement

Frozen v2 improves over v1 on Dataset B.

Important:

```text
This is post-failure reconstruction, not independent replication.
```

### Gate C - New External Holdout

Frozen v2 succeeds on Dataset C.

This is the true external test.

Required comparison:

```text
CWP_v2 > StrongTask
AND
CWP_v2 > Random/PseudoOntology
```

If CWP_v2 improves over CWP_v1 but does not beat Random/PseudoOntology, the allowed conclusion is about generic compositional structure, not CWP-semantic specificity.

## Possible Conclusions

### Strong Success

Measurement/context/ontology shift explains P1 failure, and CWP_v2 succeeds on Dataset C.

Allowed conclusion:

```text
Cross-dataset CWP generalization requires explicit alignment of neural-state and task-context representations.
```

Additional requirement:

```text
CWP_v2 must outperform both StrongTask and Random/PseudoOntology on Dataset C.
```

### Moderate Result

A -> B failure is partly explained, but Dataset C fails.

Allowed conclusion:

```text
Paper 1 external failure can be partly attributed to dataset shift, but dataset-invariant CWP remains unsupported.
```

Alternative moderate result:

```text
CWP_v2 improves over CWP_v1, but CWP_v2 is approximately equal to Random/PseudoOntology.
```

Allowed conclusion:

```text
Compositional structure may help transfer, but current evidence does not support CWP-semantic specificity.
```

### Strong Refutation

Alignment and ontology revision fail on both B and C.

Allowed conclusion:

```text
CWP v1/v2 lacks cross-dataset neural invariance.
```

## One-Sentence Backbone

```text
Reproduce Failure
-> Decompose Shift
-> Ablate Causes
-> Revise Representation
-> Freeze
-> New External Holdout
```

## Reproducibility Target

Target command:

```bash
make reproduce-paper2
```

Current status:

```text
Implemented for Dataset A/B diagnostics and Dataset C final holdout.
```
