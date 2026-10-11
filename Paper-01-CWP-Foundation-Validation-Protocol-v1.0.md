# Paper 01 - CWP Foundation Validation Protocol v1.0

Status: frozen validation protocol  
Program: CWP-NAP Foundation Program v1  
Paper type: Method Paper  
Tentative title: Reusable Cognitive Work Primitives Improve Out-of-Task Prediction of Human Brain-State Transitions  
Evidence policy: this document uses only the user-provided Paper 1 validation content. Dataset details, author-result summaries, and public-result values are recorded as user-provided / citation-pending until independently verified. No new completed result, p-value, effect size, sample-size inference, or significance claim is introduced here.

Unknown or unrun items are marked as `[TO BE FILLED]`, `[NOT YET RUN]`, or `[DECISION REQUIRED]`.

## Logic Fix

If a "traditional Task Label" has already been decomposed into Encode / Maintain / Transform and uses shared cross-task state-transition operators, then it has effectively become CWP.

Therefore the real claim is not:

```text
CWP > any possible task representation
```

The real claim is:

```text
CWP generalizes better than dataset-specific, flat task labels across conditions, tasks, subjects, and datasets.
```

## Current Conclusion Boundary

Current status:

```text
CWP has not been falsified, but its definition must be narrowed.
```

Do not claim:

```text
CWP has been validated
```

The custom M0-M4 CWP-vs-Task model comparison has not been completed.

## Prior Evidence Boundary

User-provided public-result summary for ds001635:

- ds001635 has 16 participants and 3 runs.
- Each trial has approximately 10 seconds Encode, approximately 10 seconds Maintain/Manipulate, then Probe.
- Published/precomputed results indicate that cognitive stages Encode / Maintain / Probe are decodable from brain activity.
- Activation held-out F1 is approximately 75.9%-91.4%.
- Connectivity held-out F1 is approximately 76.1%-87.6%.
- Null is approximately 32%.
- Stage decoding empirical p = 0.001.

Interpretation allowed:

```text
Different cognitive processing stages -> stable different macroscopic neural states
```

Interpretation not allowed:

```text
CWP > Traditional Task Label
```

User-provided limitation:

- Manipulation-factor decoding is approximately F1 = 43.5%-49.4%.
- Null is approximately 47%-48%.
- p is approximately 0.42-0.69.

Implication:

```text
MAINTAIN != TRANSFORM is not currently supported as an easily detectable universal neural primitive.
```

## Core Hypothesis

```text
P(S_t+1 | S_t, CWP, Context)
>
P(S_t+1 | S_t, TaskLabel)
```

This must be tested on:

- unseen stimulus domain
- unseen task combination
- unseen subjects
- unseen dataset

## Core Experimental Design

The core design is:

```text
same data
+ same model capacity
+ same preprocessing
+ same prediction target
+ same holdout
+ only change label representation
```

Then deliberately test task combinations the model has never seen.

The paper must not use simple task classification as the primary claim. Every main model predicts:

```text
S_t+1
```

from:

```text
F(S_t, X)
```

where `S_t` is the current brain state and `X` is the label representation.

## Two Label Representations

### Flat Task-Label Representation

Each full condition is an independent category:

```text
Num-Low-Encode
Num-High-Encode
Pos-Low-Maintain
Rot-High-Maintain
...
```

The model receives:

```text
TaskID = 17
```

It is not told that TaskID 17 and TaskID 23 share cognitive structure.

### CWP Compositional Representation

Each condition is decomposed into:

```text
CWP + Domain + Load + Context
```

Example:

```text
Rot-High-Encode
```

becomes:

```text
Encode + Spatial + High + RotationContext
```

This gives the model reusable components. It may not have seen the full combination, but it has separately seen Encode, Spatial, and High.

## Shared Prediction Target

Flat model:

```text
S_hat_t+1 = F(S_t, TaskID)
```

CWP model:

```text
S_hat_t+1 = F(S_t, CWP, Domain, Load)
```

Model structure, hidden-layer size, training epochs, regularization search space, preprocessing, and train/test splits must remain identical unless a difference is explicitly required by the representation. The intended causal contrast is the label representation, not model capacity.

## Frozen Experiment Chain

Paper 1 is now frozen as:

```text
Paper 1 = Does CWP generalize better and reuse better than Task Label?
```

The execution chain is:

| Experiment | Name | Purpose |
| --- | --- | --- |
| E0 | Data/QC Audit | Confirm data, events, motion, missing values, and trial counts. |
| E1 | Brain-State Extraction | Convert each trial stage into S_t and Delta S. |
| E2 | CWP Existence | Test whether Encode / Maintain / Probe have distinct brain states. |
| E3 | Task vs CWP | Run the M0-M4 model faceoff. |
| E4 | Unseen Combination | Test compositionality. |
| E5 | Unseen Domain | Test cross-content/domain generalization. |
| E6 | Null/Falsification | Exclude time, label, motion, and related false explanations. |
| E7 | External Dataset | Replicate on a second dataset with zero protocol changes. |
| E8 | Statistics + Reproduction | Freeze conclusions and support one-command rerun. |

Recommended first execution sequence:

```text
E0 -> E1 -> E2 -> E4
```

E4 leave-one-combination-out is the fastest early test of whether CWP compositionality has signal.

### E0 - Data/QC Audit

Parse:

- subjects
- runs
- events.tsv
- BOLD
- confounds

Required outputs:

```text
dataset_manifest.csv
trial_counts.csv
qc_subjects.csv
```

Checks:

- each subject has 3 runs
- trial counts by condition
- high/low balance
- Num/Pos/Add/Rot balance when present in verified metadata
- motion anomalies
- missing responses
- event timing correctness
- event fields include trial_type / load_type / processing_stage

### E1 - Brain-State Extraction

Start without deep learning.

Use a fixed 200-400 ROI atlas. Exact atlas is `[DECISION REQUIRED]`.

Extract:

```text
S_Encode
S_Maintain
S_Probe
```

and:

```text
Delta S_Encode = S_Encode - S_Baseline
Delta S_Maintain = S_Maintain - S_Encode
Delta S_Probe = S_Probe - S_Maintain
```

HRF delay must be explicitly handled.

### E2 - CWP Existence

Sanity check:

```text
Encode != Maintain != Probe
```

Use held-out subject/run classification or representational similarity.

If this pipeline cannot reproduce the strong stage signal reported by prior/public analysis, stop downstream modeling and repair E0/E1 first.

Maintain vs Transform remains exploratory because current public-result summaries do not support it as an easily detectable universal primitive.

### E3 - Task vs CWP

Run M0-M4 under the same data, preprocessing, capacity, and holdout.

Primary comparison:

```text
M4 > M2
```

Secondary OOD comparison:

```text
M3 > M2 on OOD
```

First CWP ontology:

```text
ENCODE
MAINTAIN
PROBE
```

### E4 - Unseen Combination

Leave one full cell out from:

```text
Domain x Load x CWP
```

Example:

```text
Pos + High + Encode
```

Training may still include:

- Pos + Low + Encode
- Num + High + Encode
- Pos + High + Maintain

Test:

```text
Pos + High + Encode
```

Repeat for every valid cell.

Expected CWP evidence:

```text
Error_CWP < Error_Task
```

### E5 - Unseen Domain

Train:

```text
Number
```

Test:

```text
Spatial
```

Then reverse:

```text
Spatial -> Number
```

Core question:

```text
A_Encode^Number -> Encode^Spatial ?
```

If this holds, Encode may contain domain-reusable structure.

### E6 - Null/Falsification

Required nulls:

- Label shuffle.
- Pseudo-CWP ontology.
- Time baseline.
- Random boundary / boundary jitter.
- Domain-preserving shuffle.
- Motion-only model.
- Subject shuffle.

Required survival criterion:

```text
True CWP > 99% Pseudo CWP
```

### E7 - External Dataset

After E0-E6, ontology changes are forbidden.

External test:

```text
Train/Develop on ds001635
-> Test on ds001634
```

Use:

```text
ENCODE
MAINTAIN
PROBE
```

with the frozen Paper 1 pipeline.

Purpose:

Exclude the explanation that CWP was customized only for ds001635.

### E8 - Statistics + Reproduction

Primary metric:

```text
Held-out predictive error / log likelihood
```

Report:

- R^2
- MSE
- cosine similarity
- effect size
- 95% CI

Statistical unit:

```text
Subject
```

Methods:

- subject-level paired comparison
- bootstrap 95% CI
- permutation test
- FDR correction

### Final Three Gates

Gate A - Incremental:

```text
Task + CWP > Task
```

Gate B - OOD:

```text
CWP > Task
```

in unseen combination/domain.

Gate C - External:

```text
second dataset direction is consistent
```

Interpretation:

- If A+B+C all pass: CWP Foundation Paper holds.
- If only A passes: CWP has extra information, but generalization advantage is not proven.
- If A and B fail: strong CWP hypothesis fails.

## Dataset Division

### Primary Dataset - OpenNeuro ds001635

Primary role:

```text
CWP discovery and validation against flat task labels
```

User-provided structure:

- 16 participants.
- 3 fMRI runs.
- number / spatial domains.
- low / high loads.
- Maintain / Manipulate operations.
- Manipulate is number +3 or spatial rotation 90 degrees.
- Maintain and Manipulate occur at the same delay time position.
- Retro-cue appears after encoding, so encoding demands are intentionally matched between trial types.

Why it is central:

This can challenge the objection that CWP is merely time since trial start.

Metadata still required:

- Dataset version/accession verification: `[TO BE FILLED]`
- BIDS event schema verification: `[TO BE FILLED]`
- Subject/run inclusion list: `[TO BE FILLED]`
- Exact event durations from files: `[TO BE FILLED]`
- Preprocessing provenance: `[TO BE FILLED]`

### External Holdout - OpenNeuro ds001634

Primary role:

```text
External replication of frozen Encode / Maintain CWP
```

User-provided structure:

- 19 participants.
- number / fractal / spatial domains.
- 3 memory-load levels.
- Encode -> Maintain -> Probe.
- Each stage can be modeled separately.

Boundary:

The new paper must not merely repeat that stages can be classified. It must test reusable state-transition operators and OOD prediction advantage.

Metadata still required:

- Dataset version/accession verification: `[TO BE FILLED]`
- Compatibility with ds001635 preprocessing and atlas: `[TO BE FILLED]`
- External replication split: `[TO BE FILLED]`

### Final Cross-Task Test - MDTB ds002105

Primary role:

```text
Leave-One-Entire-Task-Out cross-task generalization
```

User-provided structure:

- 24 participants.
- 47 task conditions.
- 4 sessions.
- 32 runs.

Purpose:

The model never sees a held-out task during training and predicts brain states only from the task's CWP composition.

Metadata still required:

- Dataset version/accession verification: `[TO BE FILLED]`
- Task-to-CWP composition map: `[TO BE FILLED]`
- Leave-one-task-out split file: `[TO BE FILLED]`

## Frozen CWP Ontology

Primary analysis uses only three semantically cleaner primitives:

| CWP | Definition |
| --- | --- |
| ENCODE | Convert external stimulus into working-memory representation. |
| MAINTAIN | Preserve an existing representation without actively changing it. |
| TRANSFORM | Change an internal representation according to a rule. |

Probe is secondary only because it mixes:

```text
Retrieve + Compare + Decide + MotorReport
```

Strict distinction:

| Construct | Meaning |
| --- | --- |
| CWP | What cognitive operation is being performed. |
| Context | number / spatial / fractal, load, stimulus content, transformation rule. |
| Task Label | Dataset-specific name of the full experimental condition. |

Revised ontology status:

```text
CWP Level 1: ENCODE -> MAINTAIN -> PROBE/RETRIEVAL
CWP Level 2: MAINTAIN -> PassiveMaintain / Transform
```

Level 1 has stronger current support from stage decoding. Level 2 remains candidate and must be re-tested.

## Brain-State Representation

Public fMRI can test macroscopic CWP state, not instantaneous NAP.

For each trial stage:

```text
S_j,p in R^R
```

where `R` is the number of ROIs in a fixed brain atlas.

Main state transitions:

```text
Delta S_Encode = S_Encode - S_Baseline
Delta S_Maintain = S_Delay-Maintain - S_Encode
Delta S_Transform = S_Delay-Transform - S_Encode
```

All models must use:

- same preprocessing
- same fixed atlas
- same nuisance regressors
- same HRF/deconvolution method
- same training/testing data

Leakage rule:

```text
Do not generate ROIs using full data.
```

## Frozen Pipeline

```text
download + checksum
-> preprocessing
-> fixed-atlas ROI state extraction
-> HRF/deconvolution or delay-aware stage estimation
-> frozen CWP/context/task labels
-> frozen splits
-> M0-M4 training
-> OOD holdouts
-> null tests
-> subject-level statistics
-> external replication
-> figures/tables
-> claim audit
```

## Five-Model Faceoff

All models must use the same data, same preprocessing, same network capacity/model budget, same hyperparameter selection rules, and same holdout.

### M0 - State-only

```text
S_hat_t+1 = A S_t
```

Question:

```text
Is current state alone enough?
```

### M1 - Flat Task Label

```text
S_hat_t+1 = F(S_t, TaskID)
```

Examples:

```text
number-high-transform-delay
spatial-low-maintain-delay
```

Each condition combination is treated as an independent dataset-specific label.

### M2 - Strong Task Baseline

```text
S_hat_t+1 = F(S_t, TaskID, Domain, Load)
```

Equivalent linear/operator form:

```text
S_hat_t+1 =
A_TaskID S_t
+ B_domain
+ C_load
```

This is the strongest task-label opponent. Each task condition receives its own transition operator with hierarchical shrinkage, but it does not receive a shared CWP operator.

Examples:

```text
A_NumEncode != A_PosEncode != A_RotEncode
```

### M3 - CWP Model

```text
S_hat_t+1 = F(S_t, CWP, Domain, Load)
```

Equivalent linear/operator form:

```text
S_hat_t+1 =
A_CWP S_t
+ B_domain
+ C_load
```

Core reuse claim:

```text
A_Encode
```

can be shared across domains, and:

```text
A_TRANSFORM
```

can be tested for sharing across:

- number +3
- spatial rotation 90 degrees
- future transformation tasks

### M4 - Task + CWP

```text
S_hat_t+1 = M2 + CWP residual
```

True incremental validity:

```text
M4 > M2
```

If the only finding is:

```text
M3 > M1
```

then the evidence only shows CWP beats a weak one-hot baseline, not that CWP beats a strong task-label model.

## Key Holdouts

Evidence strength:

```text
Unseen Combination < Unseen Domain < Unseen Task / Dataset
```

### Test A - Cross-Domain Transform

Main test:

```text
Train: number + add 3
Test: spatial + rotate 90 degrees
```

and reverse direction.

Why it matters:

- stimulus differs
- transformation rule differs
- semantic operation is TRANSFORM
- time position and duration are matched

This is the core ds001635 test.

### Test B - Leave-One-Combination-Out / Leave-One-Cell-Out

Condition space:

```text
Domain x Load x Operation = 2 x 2 x 2 = 8
```

Each run removes one complete cell, for example:

```text
Spatial x High x Transform
```

The model cannot see any trial from that combination.

CWP model must compose known components:

```text
Spatial + High + Transform
```

Example from the general design:

```text
Rot + High + Encode
```

is completely removed from training.

Training may still contain:

```text
Rot-Low-Encode
Pos-High-Encode
Num-High-Encode
Rot-High-Maintain
```

So the CWP model has seen Rot, High, and Encode separately, but never the full combination.

Expected comparison:

```text
Error_CWP < Error_Flat
```

This is useful but insufficient alone, because a reviewer could object that a flat model is forced to handle an unseen label.

### Test C - Cross-Domain

Example:

```text
Train: Num Encode
Test: Spatial Encode
```

or:

```text
Train: Num Encode + Pos Encode
Test: Rot Encode
```

If `A_Encode` transfers, this supports:

```text
CWP_Encode has domain-invariant dynamics.
```

Exact domains and valid mappings depend on the dataset's verified event schema.

### Test D - Subject / Run Holdout

Outer split:

```text
Leave-One-Subject-Out
```

Inner split:

```text
Leave-One-Run-Out
```

Use inner split for regularization, operator rank, and other hyperparameters.

Rule:

```text
No data from the same subject may appear in both train and test.
```

### Test E - Dataset Holdout / Cross-Task Dataset Transfer

Freeze on ds001635:

- ontology
- preprocessing
- atlas
- model
- hyperparameter rules
- success thresholds

Then test unchanged on ds001634.

No ontology or model-structure changes are allowed after seeing ds001634 results.

General cross-dataset logic:

```text
Dataset_A: Encode -> Maintain -> Probe
Dataset_B: Encode -> Maintain -> Retrieve
```

Train on Dataset_A, test on Dataset_B.

Flat Task Model has not seen Dataset_B task IDs. CWP model can test:

```text
Encode_A -> Encode_B
```

This is the strongest test of reusable representation.

### Test F - Leave-One-Entire-Task-Out

Use MDTB ds002105.

Train:

```text
all but one task
```

Test:

```text
held-out entire task
```

The held-out task is predicted from CWP composition, not from a seen TaskID.

## Main Figure Design

The main Paper 1 figure should compare prediction performance across generalization regimes.

X-axis:

```text
Seen Combination
Unseen Combination
Unseen Domain
Unseen Task
```

Y-axis:

```text
Prediction Performance
```

Model lines/bars:

- Flat Task.
- Strong Task.
- CWP.
- Task + CWP.

Ideal pattern:

```text
Seen: Task approximately equals CWP
Unseen combination: CWP > Task
Unseen domain: CWP >> Task
Unseen task: CWP >>> Task
```

Interpretation:

```text
CWP's value is not better memorization. Its value is better generalization.
```

Conceptual contrast:

```text
Task Label = name the whole program.
CWP = describe which reusable cognitive operations compose the program.
```

## Primary Metric

Primary metric:

```text
Held-out Predictive Log-Likelihood / ELPD
```

Secondary metrics:

- multivariate R^2
- cosine similarity between predicted and observed Delta S
- MSE
- added prediction of accuracy / reaction time
- parameter count and description length

Statistical unit:

```text
subject
```

Do not treat thousands of trials as thousands of independent participants.

Statistical methods:

- subject-level paired differences
- 10,000 sign-flip permutations
- bootstrap 95% CI
- FDR for multiple comparisons
- report effect size, not only p-values

## Required Null Tests

Minimum null set:

1. Delay-position-preserving shuffle.
2. Pseudo-CWP ontology.
3. Time-only baseline.
4. Domain/load-preserving label shuffle.
5. Boundary jitter.
6. Confounds-only model.
7. Subject/task swap.

### Delay-Position-Preserving Shuffle

Shuffle Maintain / Transform only within the same delay time position.

Purpose:

```text
Destroy CWP semantics while preserving timing.
```

### Pseudo-CWP Ontology

Randomly generate the same number and frequency of fake primitives.

Required result:

```text
True CWP > 99% matched pseudo-ontologies
```

### Time-Only Baseline

```text
S_t+1 = F(S_t, time since trial start)
```

Purpose:

Test whether CWP is just a stopwatch.

### Domain/Load-Preserving Label Shuffle

Preserve low-level statistics while destroying CWP semantics.

### Boundary Jitter

Move CWP boundaries by 1-2 TR.

### Confounds-Only Model

Use only:

- head motion
- run
- drift
- other nuisance variables

### Subject/Task Swap

Attach another subject's CWP labels or task context.

## Four Gates For "Clearly Outperforms"

The paper may write:

```text
CWP clearly outperforms traditional task labels.
```

only if all four gates pass.

### Gate 1 - Incremental

```text
ELPD(M4) - ELPD(M2) > 0
```

and the 95% CI is fully above 0.

### Gate 2 - OOD Practical Gain

In cross-domain and leave-cell-out settings:

```text
MSE_CWP <= 0.95 x MSE_Task
```

Meaning:

```text
at least 5% OOD prediction error reduction
```

### Gate 3 - Null Survival

True CWP must exceed:

```text
99% frequency-matched pseudo-ontologies
```

### Gate 4 - External Replication

In the second dataset not used for development:

- effect direction is consistent
- corrected q < 0.05
- ontology and model structure are not changed

## Three Possible Conclusions

### Strong Success

Condition:

```text
CWP > M2
```

and success holds across:

- domain
- task
- dataset

Allowed conclusion:

```text
CWP is a reusable cognitive state-transition representation.
```

### Moderate Success

Condition:

```text
CWP approximately equals M2
```

but CWP has:

- fewer parameters
- stronger cross-task generalization
- reusable ontology across datasets

Allowed conclusion:

```text
CWP is a more compact and compositional representation language.
```

Not allowed:

```text
CWP is the only true neural primitive.
```

### Failure

Condition:

```text
CWP only beats flat one-hot labels but fails against strong task model, pseudo-ontology, or OOD tests.
```

Required conclusion:

```text
The strong CWP hypothesis fails.
```

Do not rescue the claim by switching metrics after the fact.

## One-Command Reproduction

Target:

```bash
make reproduce
```

The command should run:

```text
download + checksum
-> preprocessing
-> ROI state extraction
-> frozen splits
-> M0-M4 training
-> OOD holdouts
-> null tests
-> statistics
-> figures/tables
-> claim audit
```

Expected output structure:

```text
results/
|-- primary_metrics.csv
|-- subject_level_effects.csv
|-- null_distributions/
|-- external_replication/
|-- figures/
|-- claim_audit.json
`-- environment.lock
```

Frozen computer directory:

```text
paper1/
|-- protocol.yaml
|-- data_manifest/
|-- preprocessing/
|-- state_extraction/
|-- models/
|   |-- M0_state/
|   |-- M1_flat_task/
|   |-- M2_strong_task/
|   |-- M3_cwp/
|   `-- M4_task_plus_cwp/
|-- holdouts/
|-- null_tests/
|-- statistics/
|-- external_validation/
`-- results/
```

Expected figures:

- Figure 1 CWP framework.
- Figure 2 Stage sanity check.
- Figure 3 M0-M4 comparison.
- Figure 4 Unseen-combination.
- Figure 5 Unseen-domain.
- Figure 6 Null tests.
- Figure 7 External replication.

## Central Test

The most important single test is:

```text
Train: Number Add-3
Test: Spatial Rotate-90 degrees
```

Interpretation:

If this wins, CWP begins to look like a reusable cognitive intermediate representation.

If this fails, TRANSFORM may be a linguistic abstraction rather than a shared brain-state transition structure.

## A1-A10 Status

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
| A9 Limitations & Failed Analyses | PARTIAL |
| A10 One-command Reproduction | PARTIAL |

## Immediate Next Decisions

Before implementation, freeze:

1. Exact ds001635 and ds001634 metadata/version records.
2. Final CWP/context/task label schema.
3. Fixed atlas and ROI extraction method.
4. HRF/deconvolution or delay-aware estimation method.
5. M0-M4 model classes and equal-budget rule.
6. Subject-level statistical test implementation.
7. Claim audit JSON schema.
