---
name: nsi-paper-builder
description: Create, structure, audit, and standardize NSI research papers using one of two paper skeletons—Method Paper or Explanation Paper—plus the shared A1–A10 reproducibility attachment standard. Use when turning a research question, hypothesis, analysis plan, or completed study into an NSI-style paper package.
---

# NSI Paper Builder

## Purpose

Create one complete NSI scientific research unit:

**Paper + A1–A10 Reproducibility Attachments**

There are exactly two default paper types:

1. **Method Paper** — asks whether a method, framework, model, representation, pipeline, or system works.
2. **Explanation Paper** — asks whether a framework or model explains a scientific phenomenon.

Use the same reproducibility discipline for both. Do not force identical experiments onto both paper types.

---

# Core Rule

Every paper should form this evidence chain when applicable:

**Hypothesis → Dataset → Frozen Pipeline → Baselines / Competing Explanations → Holdout → Statistics → Null/Falsification Tests → QC/Leakage Audit → Limitations → One-command Reproduction**

The paper tells the scientific story.

The attachments prove how the result was obtained, audited, falsified, and reproduced.

---

# Step 1 — Classify the Paper

Choose **Method Paper** when the primary claim is similar to:

- "This method works."
- "This representation predicts better."
- "This architecture improves performance."
- "This pipeline generalizes."
- "This system is more reliable / efficient / robust."
- "Component X contributes to the result."

Method papers emphasize:

**Method → Baselines → Ablations → Holdout → Robustness**

Choose **Explanation Paper** when the primary claim is similar to:

- "Framework X explains phenomenon Y."
- "Phenomenon Y follows prediction Z."
- "Observed neural/behavioral pattern supports mechanism X."
- "One scientific explanation fits better than alternatives."

Explanation papers emphasize:

**Hypothesis → Prediction → Observation → Competing Explanations → Falsification**

If both are present, classify by the **main claim of the paper**, not by the tools used.

Do not create a third category unless the user explicitly requests one.

---

# Step 2 — Never Fabricate Evidence

Never invent:

- dataset sizes
- subject counts
- p-values
- effect sizes
- confidence intervals
- baseline scores
- holdout scores
- failed analyses
- preregistration timestamps
- repository URLs
- accession numbers
- statistical significance
- experimental outcomes

If information is missing, mark it clearly as:

**[TO BE FILLED]**, **[NOT YET RUN]**, or **[DECISION REQUIRED]**

Separate:

- planned analysis
- completed analysis
- observed result
- interpretation

---

# Step 3 — Method Paper Skeleton

Use this structure by default.

## Title

## Abstract
Include:
- problem
- proposed method
- dataset
- evaluation design
- primary holdout result
- main conclusion

## 1. Introduction
### 1.1 Problem
### 1.2 Existing Methods and Gap
### 1.3 Proposed Method
### 1.4 Evaluation Questions / Falsifiable Hypotheses
### 1.5 Contributions

## 2. Methods
### 2.1 Dataset
### 2.2 Cohort / Inclusion Criteria
### 2.3 Preprocessing
### 2.4 Frozen Protocol
### 2.5 Proposed Method / Architecture
### 2.6 Baselines
### 2.7 Ablation Design
Use only when meaningful.
### 2.8 Holdout Design
### 2.9 Metrics
### 2.10 Statistical Analysis
### 2.11 Null / Robustness Tests
### 2.12 QC and Leakage Controls

## 3. Results
### 3.1 Primary Performance
### 3.2 Baseline Comparison
### 3.3 Ablation Results
Use only when meaningful.
### 3.4 Holdout Performance
### 3.5 Statistical Evidence
### 3.6 Null / Robustness Results
### 3.7 Failure Cases

## 4. Discussion
### 4.1 What Worked
### 4.2 Why It May Have Worked
Do not claim mechanism unless the experiment supports it.
### 4.3 Generalization
### 4.4 Failure Cases
### 4.5 Limitations
### 4.6 Future Work

## 5. Conclusion

## Data Availability
## Code Availability
## Reproducibility Statement
## Ethics Statement
## Author Contributions
## Conflicts of Interest

---

# Step 4 — Explanation Paper Skeleton

Use this structure by default.

## Title

## Abstract
Include:
- phenomenon
- scientific gap
- proposed explanation
- dataset
- falsifiable prediction
- primary evidence
- conclusion with appropriate causal restraint

## 1. Introduction
### 1.1 Phenomenon
### 1.2 Existing Explanations
### 1.3 Scientific Gap
### 1.4 Proposed Explanation
### 1.5 Falsifiable Hypotheses
### 1.6 Predictions
### 1.7 Contributions

## 2. Methods
### 2.1 Dataset
### 2.2 Cohort / Inclusion Criteria
### 2.3 Operational Definitions
### 2.4 Preprocessing
### 2.5 Frozen Analysis Protocol
### 2.6 Measurements / Representations
### 2.7 Competing Explanations / Models
### 2.8 Holdout Design
### 2.9 Statistical Analysis
### 2.10 Confound Controls
### 2.11 Null / Falsification Tests
### 2.12 QC and Leakage Controls

## 3. Results
### 3.1 Primary Hypothesis Test
### 3.2 Predicted Pattern
### 3.3 Competing Explanation Tests
### 3.4 Holdout Result
### 3.5 Statistical Evidence
### 3.6 Null / Falsification Results
### 3.7 Unexpected / Negative Results

## 4. Discussion
### 4.1 Interpretation
### 4.2 What the Evidence Supports
### 4.3 What the Evidence Does NOT Support
### 4.4 Alternative Explanations
### 4.5 Limitations
### 4.6 Future Falsification Tests

## 5. Conclusion

## Data Availability
## Code Availability
## Reproducibility Statement
## Ethics Statement
## Author Contributions
## Conflicts of Interest

---

# Step 5 — Shared A1–A10 Attachment Standard

Every complete paper package should contain the following attachments.

## A1 Frozen Protocol

Record what was fixed before final holdout evaluation:

- research question
- falsifiable hypothesis
- primary endpoint
- secondary endpoints
- inclusion / exclusion rules
- preprocessing rules
- feature definitions
- model specification
- hyperparameters or tuning space
- baselines / competing explanations
- data split logic
- holdout definition
- statistical tests
- null / falsification tests
- success criteria
- failure criteria
- deviations policy
- freeze version
- freeze timestamp or immutable version identifier

Core principle:

**Freeze → final holdout evaluation**

If the holdout influences model or analysis changes, it is no longer a clean holdout.

## A2 Dataset Manifest

Include:

- dataset name
- source
- version / release
- accession / identifier
- modality
- sample / subject inventory
- inclusion / exclusion decisions
- train / validation / holdout membership
- file checksums when practical
- missing-data record
- licensing / access requirements
- dataset-specific caveats

## A3 Full Pipeline

Document the complete computational path:

**Raw Data → QC → Preprocessing → Representation / Features → Model / Analysis → Statistics → Figures / Tables**

Include:

- software versions
- environment
- parameters
- seeds
- transformations
- normalization
- feature construction
- model configuration
- evaluation code path

## A4 Full Baseline Results

For Method Papers:

**Full Baseline & Ablation Results**

Include all planned baselines, not only favorable ones.

For Explanation Papers:

**Full Baseline & Competing-Explanation Results**

Include plausible alternative models / explanations and their tests.

## A5 Holdout Audit

Include:

- holdout definition
- isolation mechanism
- access policy
- access log when available
- date / version of first evaluation
- number of holdout evaluations
- whether any post-holdout changes occurred
- if changes occurred, what data became the new final holdout
- final immutable evaluation artifact

## A6 Statistics

Include the full statistical plan and outputs:

- estimand / target quantity
- statistical tests
- effect sizes
- uncertainty intervals
- multiple-comparison correction
- assumptions
- sensitivity analyses
- missing-data handling
- hierarchical / repeated-measure handling when relevant
- power / precision analysis when appropriate
- complete result tables

Never equate "p < 0.05" with scientific importance.

## A7 Null / Falsification Tests

Possible tests include:

- permutation tests
- label shuffle
- temporal shuffle
- phase randomization
- subject shuffle
- negative controls
- random-feature controls
- synthetic null data
- adversarial confound tests
- alternative-hypothesis tests
- destructive / perturbation tests

Choose tests that could genuinely make the central claim fail.

## A8 QC & Leakage Audit

Check for:

- subject leakage
- session leakage
- temporal leakage
- preprocessing leakage
- normalization leakage
- feature leakage
- label leakage
- duplicate / near-duplicate contamination
- site / scanner confounding
- batch effects
- demographic confounding when relevant
- train/test contamination
- researcher-induced leakage
- post-hoc selection

Document both tests performed and findings.

## A9 Limitations & Failed Analyses

Include:

- known limitations
- failed analyses
- negative results
- unsupported hypotheses
- unstable findings
- discarded methods and why
- protocol deviations
- unresolved confounds
- boundary conditions
- claims the data cannot support

Do not hide failures merely because they weaken the narrative.

## A10 One-command Reproduction

Target:

```bash
make reproduce
```

or an equivalent single command.

It should, as far as licensing and compute allow:

1. validate environment
2. obtain or locate data
3. verify dataset manifest / checksums
4. run preprocessing
5. run the frozen analysis
6. run baselines / competing models
7. run statistics
8. run null tests
9. regenerate main tables
10. regenerate main figures
11. emit a reproducibility report

If full data cannot be redistributed, the command should fail clearly with instructions for authorized data placement rather than silently substituting data.

---

# Step 6 — Match Tests to Paper Type

Do not mechanically require every test.

## Method Paper

Usually prioritize:

- strong baselines
- ablations
- holdout generalization
- robustness
- sensitivity analysis
- compute / complexity where relevant

Ablation is required only if the method contains separable components whose contribution is part of the claim.

## Explanation Paper

Usually prioritize:

- operational definitions
- competing explanations
- confound controls
- falsification tests
- negative controls
- effect sizes
- replication / holdout
- causal restraint

Do not add meaningless ablations merely to imitate ML papers.

---

# Step 7 — Output Modes

Infer the mode from the user's request.

## SKELETON MODE

Use when the user asks for:
- structure
- outline
- skeleton
- sections

Return:
1. selected paper type
2. main paper skeleton
3. A1–A10 skeleton

## PACKAGE MODE

Use when the user provides a research idea and wants a paper package.

Return:
1. paper classification
2. proposed title
3. central claim
4. falsifiable hypothesis
5. primary endpoint
6. dataset plan
7. frozen pipeline plan
8. baseline / competing-explanation plan
9. holdout plan
10. statistics
11. null / falsification plan
12. main paper skeleton populated with known information
13. A1–A10 populated with known information and placeholders

## DRAFT MODE

Use when enough evidence/results are provided to draft manuscript text.

Draft the paper, but:
- distinguish facts from interpretation
- do not manufacture missing results
- preserve uncertainty
- leave explicit placeholders where evidence is missing

## AUDIT MODE

Use when the user supplies an existing paper or protocol.

Return:
- PASS
- PARTIAL
- MISSING
- RISK

for each of:

1. Hypothesis
2. Dataset
3. Frozen Pipeline
4. Baselines / Competing Explanations
5. Holdout
6. Statistics
7. Null / Falsification
8. QC / Leakage
9. Limitations / Failed Analyses
10. One-command Reproduction

Then list the highest-risk scientific weaknesses first.

---

# Step 8 — Minimum Intake

When possible, extract these fields from the user's input:

```yaml
paper_type: auto | method | explanation
research_question:
central_claim:
hypothesis:
dataset:
primary_endpoint:
pipeline:
baselines:
competing_explanations:
holdout:
statistics:
null_tests:
known_results:
known_limitations:
reproduction_target:
```

Do not block progress if fields are missing. Generate the best available structure and mark missing fields.

---

# Step 9 — Quality Gate

Before calling a package "complete", verify:

- [ ] Central claim is specific.
- [ ] Hypothesis is falsifiable.
- [ ] Primary endpoint is explicit.
- [ ] Dataset and cohort are reproducibly defined.
- [ ] Pipeline is frozen before final holdout evaluation.
- [ ] Baselines or competing explanations are appropriate.
- [ ] Holdout is genuinely isolated.
- [ ] Statistics match the data structure.
- [ ] Null / falsification tests can actually challenge the claim.
- [ ] QC and leakage risks are audited.
- [ ] Limitations include claim boundaries.
- [ ] Failed analyses are disclosed.
- [ ] Main results can be reproduced from a locked environment.
- [ ] No unsupported causal language is used.
- [ ] No result is invented.

If one of these fails, state the failure explicitly rather than hiding it.

---

# Default Output Style

Be concise and structured.

Prefer:

**Classification → Core Claim → Paper Skeleton → A1–A10 → Missing Evidence / Risks**

For early-stage research ideas, focus on the scientific design rather than producing decorative prose.

The goal is not to make a study look publishable.

The goal is to make the scientific claim **testable, auditable, falsifiable, and reproducible**.
