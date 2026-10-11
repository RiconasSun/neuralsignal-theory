# CNSOS / AI4Biology Core Program v1

Status: frozen Backbone architecture for six CNSOS / AI4Biology core papers  
Scope: Layer III - CNSOS / AI4S / AI4Biology  
Program goal: test whether CNSOS can move from architecture to scientific capability to autonomous discovery  
Evidence policy: this document uses only the provided Backbone content. It does not invent sample sizes, p-values, effect sizes, benchmark scores, exact dataset identities, completed results, repository URLs, accession numbers, or experimental outcomes.

Unknown or unrun items are marked as `[TO BE FILLED]`, `[NOT YET RUN]`, or `[DECISION REQUIRED]`.

## Program Structure

```text
P1 Framework
-> P2 Discover
-> P3 Hypothesize
-> P4 Design
-> P5 Falsify
-> P6 Closed Loop
```

The six papers form a progressive falsifiable claim chain:

```text
P1: Can the system run?
P2: Can it discover?
P3: Can it generate good hypotheses?
P4: Can it design experiments?
P5: Can it prove itself wrong?
P6: Can it complete one scientific discovery independently?
```

Program narrative:

```text
Architecture -> Scientific Capability -> Autonomous Discovery
```

## Shared Paper Contract

Each paper must eventually satisfy the same publication/reproducibility contract:

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

## Shared Backbone Rule

Each paper is frozen around:

```text
one question
one key experiment
one clear failure condition
```

Specific numeric thresholds, dataset IDs, benchmark definitions, sample sizes, and final evaluation criteria remain `[TO BE FILLED]` or `[DECISION REQUIRED]`.

## Shared Missing Decisions

- Exact CNSOS system boundary: `[TO BE FILLED]`
- Agent roles and allowed tools: `[TO BE FILLED]`
- Biological benchmark/task list: `[TO BE FILLED]`
- Dataset names and versions: `[TO BE FILLED]`
- Secret holdout construction: `[TO BE FILLED]`
- Success/failure thresholds per metric: `[DECISION REQUIRED]`
- Human-review policy: `[TO BE FILLED]`
- Machine-readable protocol schema: `[TO BE FILLED]`
- Leakage audit rubric: `[TO BE FILLED]`
- Scientific-validity rubric: `[TO BE FILLED]`
- Reproduction command: `[TO BE FILLED]`

## Paper 1 - CNSOS Framework

**Backbone question**  
Can a multi-agent research system reliably execute a complete scientific workflow?

**Core hypothesis**

```text
Multi-Agent > Single Agent
```

For complex scientific workflows, specialized multi-agent division of labor should be more reliable than a single model or single agent.

**Paper type**  
Method Paper

**Core workflow**

```text
Biological Task
-> Agents
-> Workflow
-> Scientific Output
```

Expanded workflow:

```text
Data
-> Discover
-> Hypothesize
-> Design
-> Falsify
-> Replicate
```

**Dataset / benchmark plan**  
Multiple public biological datasets / benchmark tasks.

**Baselines**

- Single LLM.
- Single Agent.
- Ordinary multi-agent chat.
- CNSOS.

**Key metrics**

- Task completion.
- Factual correctness.
- Executable analyses.
- Leakage rate.
- Reproducibility.
- Scientific validity.

**Key experiment**  
Compare CNSOS against single-model, single-agent, and ordinary multi-agent-chat baselines on complex scientific workflow completion.

**Failure condition**  
If CNSOS performs approximately the same as Single Agent on the frozen workflow metrics, then:

```text
H_1 rejected
```

The exact equivalence/non-inferiority threshold is `[DECISION REQUIRED]`.

**Known results**  
`[NOT YET RUN]`

**Missing fields**

- Exact biological datasets/tasks: `[TO BE FILLED]`
- Agent role definitions: `[TO BE FILLED]`
- Workflow completion rubric: `[TO BE FILLED]`
- Factual correctness rubric: `[TO BE FILLED]`
- Leakage-rate definition: `[TO BE FILLED]`
- Statistical comparison plan: `[TO BE FILLED]`
- One-command reproduction: `[TO BE FILLED]`

## Paper 2 - Automated Pattern Discovery

**Backbone question**  
Can AI discover real, reproducible biological patterns?

**Core hypothesis**

```text
Data -> Reproducible Pattern
```

CNSOS should identify reproducible biological patterns rather than merely fitting noise.

**Paper type**  
Method Paper

**Core experiment structure**

```text
Dataset_train
-> Pattern Agent
-> Candidate Pattern
-> Independent Holdout
```

**Key experiment A - Known-pattern recovery**  
Use data with accepted known patterns and test whether CNSOS can rediscover them.

**Key experiment B - Synthetic planted pattern**  
Use synthetic data with:

```text
Signal + Noise
```

Then test whether CNSOS finds the signal rather than noise.

**Baselines**

- PCA / clustering / classical statistics.
- AutoML.
- Single-agent.
- CNSOS.

**Most important metric**

```text
Precision_discovery
```

The focus is precision, not raw number of generated patterns.

**Failure condition**  
If CNSOS does not produce reproducible candidate patterns on independent holdout, or if its discovery precision does not exceed frozen baselines by the predefined threshold, the discovery claim fails. The exact threshold is `[DECISION REQUIRED]`.

**Known results**  
`[NOT YET RUN]`

**Missing fields**

- Known-pattern datasets: `[TO BE FILLED]`
- Synthetic planted-pattern generator: `[TO BE FILLED]`
- Definition of "accepted known pattern": `[TO BE FILLED]`
- Independent holdout split: `[TO BE FILLED]`
- Discovery precision formula: `[TO BE FILLED]`
- Baseline configurations: `[TO BE FILLED]`
- Statistical test: `[TO BE FILLED]`
- One-command reproduction: `[TO BE FILLED]`

## Paper 3 - Automated Hypothesis Generation

**Backbone question**  
Can AI turn patterns into high-quality, falsifiable scientific hypotheses?

**Core mapping**

```text
Pattern -> Scientific Hypothesis
```

**Core hypothesis**  
CNSOS-generated hypotheses should outperform random hypotheses, template hypotheses, single-LLM hypotheses, and literature-only hypotheses on:

```text
Testability + Novelty + Future Evidence
```

**Paper type**  
Method Paper

**Key experiment**  
Temporal holdout.

Example structure:

```text
Literature/Data_<=2020
-> CNSOS hypothesis generation
-> Evidence_2021-2026 validation
```

The purpose is to prevent leakage from future evidence into hypothesis generation.

**Baselines**

- Random hypothesis.
- Template hypothesis.
- Single LLM.
- Literature-only hypothesis.

**Failure condition**  
If CNSOS hypotheses validate at approximately the same rate as SingleLLM hypotheses, then the multi-agent hypothesis architecture has no demonstrated value. The exact equivalence threshold is `[DECISION REQUIRED]`.

**Known results**  
`[NOT YET RUN]`

**Missing fields**

- Literature/data cutoff implementation: `[TO BE FILLED]`
- Exact 2020 cutoff date: `[DECISION REQUIRED]`
- Evidence validation window and sources: `[TO BE FILLED]`
- Testability rubric: `[TO BE FILLED]`
- Novelty rubric: `[TO BE FILLED]`
- Future-evidence validation metric: `[TO BE FILLED]`
- Leakage-prevention protocol: `[TO BE FILLED]`
- Statistical test: `[TO BE FILLED]`
- One-command reproduction: `[TO BE FILLED]`

## Paper 4 - Automated Experiment Design

**Backbone question**  
Can AI turn a hypothesis into a truly executable experiment?

**Core mapping**

```text
Hypothesis -> Executable Experiment
```

**Core hypothesis**  
CNSOS can automatically generate experiment designs that are executable, free of severe statistical errors, and free of severe leakage.

**Paper type**  
Method Paper

**Required experiment output**

```text
Dataset
+ Variables
+ Pipeline
+ Baseline
+ Statistics
+ Holdout
+ Null
```

**Benchmark**  
Give the system 100 biological hypotheses and require it to generate complete protocols.

**Key experiment**  
Generated protocols are actually executed, preferably by an independent execution agent.

The strongest version of the experiment asks whether the protocol can be handed to a fully independent execution agent without reinterpretation.

**Metrics**

- ExecutableRate.
- LeakageRate.
- StatisticalValidity.
- Power.
- Reproducibility.

**Failure condition**  
If CNSOS-generated protocols cannot be executed, contain severe statistical errors, contain severe leakage, or require substantial reinterpretation by the execution agent, the experiment-design claim fails. Exact thresholds are `[DECISION REQUIRED]`.

**Known results**  
`[NOT YET RUN]`

**Missing fields**

- The 100 biological hypotheses: `[TO BE FILLED]`
- Protocol schema: `[TO BE FILLED]`
- Execution-agent boundary: `[TO BE FILLED]`
- Executability rubric: `[TO BE FILLED]`
- Severe statistical error definition: `[TO BE FILLED]`
- Severe leakage definition: `[TO BE FILLED]`
- Power criterion: `[TO BE FILLED]`
- Statistical evaluation plan: `[TO BE FILLED]`
- One-command reproduction: `[TO BE FILLED]`

## Paper 5 - Automated Falsification / Red-Team Science

**Backbone question**  
Can a dedicated error-finding agent reduce false discoveries?

**Core mapping**

```text
Claim -> Attack
```

**Core hypothesis**  
Adding a dedicated Falsification Agent should reduce the false positive rate while preserving true discoveries.

Expected direction:

```text
False Positive Rate down
True Positive Rate approximately stable
```

**Paper type**  
Method Paper

**Attack set / poison set**

The system is deliberately exposed to cases involving:

- Label leakage.
- Batch effect.
- Confound.
- Duplicated subjects.
- Selection bias.
- P-hacking opportunity.
- Multiple-comparison trap.
- Spurious correlation.

**Backbone workflow**

```text
Candidate Finding
-> Alternative Explanations
-> Null Tests
-> Confound Tests
-> Survival
```

Final classification:

```text
Discovery survives
```

or:

```text
Discovery rejected
```

**Key experiment**  
Compare discovery workflows with and without a Falsification / Red-Team Agent under deliberately contaminated or confounded conditions.

**Failure condition**  
If the Falsification Agent does not reduce false positives, or if it reduces false positives only by eliminating true positives beyond the accepted retention threshold, the red-team science claim fails. The retention threshold is `[DECISION REQUIRED]`.

**Known results**  
`[NOT YET RUN]`

**Missing fields**

- Poisoned benchmark cases: `[TO BE FILLED]`
- False-positive definition: `[TO BE FILLED]`
- True-positive definition: `[TO BE FILLED]`
- Accepted true-positive retention threshold: `[DECISION REQUIRED]`
- Red-team agent protocol: `[TO BE FILLED]`
- Alternative-explanation inventory: `[TO BE FILLED]`
- Statistical test: `[TO BE FILLED]`
- One-command reproduction: `[TO BE FILLED]`

## Paper 6 - Closed-Loop Autonomous Discovery

**Backbone question**  
Can the full CNSOS system produce and validate a new candidate discovery end to end?

**Core hypothesis**  
CNSOS can start from raw public biological data and complete the full discovery loop.

**Paper type**  
Method Paper

**Closed-loop workflow**

```text
Data
-> Pattern
-> Hypothesis
-> Experiment
-> Falsification
-> Replication
-> Novel Candidate Finding
```

**Key design requirement**  
Freeze both:

```text
Discovery Dataset
```

and:

```text
Secret Holdout
```

CNSOS completes discovery before the holdout is opened.

If the finding still holds on the holdout:

```text
Discovery -> Independent Confirmation
```

**Key experiment**  
Run the full CNSOS loop from raw public biological data through discovery, hypothesis, experiment, falsification, and replication, then evaluate on a secret holdout.

**Failure condition**  
If CNSOS cannot complete the full loop, cannot produce a candidate finding, fails falsification, or fails independent holdout confirmation, the closed-loop autonomous discovery claim fails. Exact thresholds and allowed partial failures are `[DECISION REQUIRED]`.

**Known results**  
`[NOT YET RUN]`

**Missing fields**

- Discovery dataset: `[TO BE FILLED]`
- Secret holdout design: `[TO BE FILLED]`
- Definition of "novel candidate finding": `[TO BE FILLED]`
- Independent confirmation protocol: `[TO BE FILLED]`
- Replication criterion: `[TO BE FILLED]`
- Theory/update representation, if any: `[TO BE FILLED]`
- Human intervention boundary: `[TO BE FILLED]`
- Statistical test: `[TO BE FILLED]`
- One-command reproduction: `[TO BE FILLED]`

## Program-Level Quality Gate

| Gate | Status |
| --- | --- |
| Six Backbones are defined | PASS |
| Progressive architecture is defined | PASS |
| Shared paper contract is defined | PASS |
| Each paper has a Backbone question | PASS |
| Each paper has a core hypothesis | PASS |
| Each paper has a key experiment | PASS |
| Each paper has a failure condition | PARTIAL |
| Dataset families or benchmark types are named | PARTIAL |
| Exact datasets/releases/accession IDs are specified | MISSING |
| Sample/task counts are fully specified | PARTIAL |
| Baselines are named | PASS |
| Holdout logic is defined | PARTIAL |
| Statistical tests are fully specified | MISSING |
| Results are available | NOT YET RUN |
| One-command reproduction is defined | MISSING |
| Unsupported results are invented | PASS - no invented results |

## A1-A10 Packet Status

Each CNSOS / AI4Biology paper now has enough structure to begin a paper-specific A1-A10 package, but none is complete.

| Attachment | Current Status |
| --- | --- |
| A1 Frozen Protocol | PARTIAL |
| A2 Dataset Manifest | MISSING |
| A3 Full Pipeline | PARTIAL |
| A4 Full Baseline Results | NOT YET RUN |
| A5 Holdout Audit | PARTIAL |
| A6 Statistics | MISSING |
| A7 Null / Falsification Tests | PARTIAL |
| A8 QC & Leakage Audit | PARTIAL |
| A9 Limitations & Failed Analyses | MISSING |
| A10 One-command Reproduction | MISSING |

## Immediate Next Step

The next protocol decision should be Paper 1's exact CNSOS system boundary:

```text
agent roles
allowed tools
workflow stages
baseline systems
benchmark tasks
completion rubric
leakage rubric
reproducibility rubric
```

Paper 1 should be frozen first because its architecture, agent boundaries, and workflow metrics become dependencies for Papers 2-6.
