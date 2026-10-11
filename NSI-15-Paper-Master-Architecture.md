# NSI 15-Paper Master Architecture

Status: architecture draft from provided research-program outline  
Evidence policy: no unprovided data, results, sample sizes, p-values, effect sizes, baseline scores, holdout scores, repository URLs, accession numbers, or experimental outcomes are asserted here.  
Unknown fields are marked as `[TO BE FILLED]`, `[NOT YET RUN]`, or `[DECISION REQUIRED]`.

## Program Thesis

A three-layer computational cognitive neuroscience and AI-for-Science research program comprising 15 independent, falsifiable, reproducible studies.

The program is organized as:

```text
15 Papers = 5 + 4 + 6
```

```text
Layer I: Build the Representation
Layer II: Use it to Understand the Brain
Layer III: Build AI to Discover and Attack the Science
```

In expanded form:

```text
Layer I: Define and validate CWP as a scientific object.
Layer II: Use CWP-NAP multiscale dynamics to explain cognitive phenomena.
Layer III: Use the first two layers as a testbed for AI-assisted scientific discovery.
```

## Layer Map

| Layer | Papers | Core Task |
| --- | ---: | --- |
| Layer I - CWP Foundations | 5 | Test whether CWP is a real and useful representation of brain-state dynamics. |
| Layer II - CWP-NAP Multiscale Science | 4 | Build the CWP-to-NAP bridge and test whether it explains specific neural/cognitive phenomena. |
| Layer III - CNSOS / AI4S | 6 | Turn the first two layers into a testbed for automated scientific discovery. |

## Global Known Inputs

- The program contains 15 papers.
- The architecture is three-layered: 5 + 4 + 6.
- Layer I focuses on CWP Foundations.
- Layer II focuses on CWP-NAP Multiscale Science.
- Layer III focuses on CNSOS / AI4S.
- Layer II is organized as Framework + 3 Phenomena.
- The three Layer II phenomenon papers are Insight, Flow, and Alexithymia.
- Layer III studies scientific discovery itself.

## Global Missing Inputs

- Dataset names: `[TO BE FILLED]`
- Dataset sources: `[TO BE FILLED]`
- Dataset versions or accession IDs: `[TO BE FILLED]`
- Subject/sample counts: `[TO BE FILLED]`
- Inclusion/exclusion criteria: `[TO BE FILLED]`
- Modality definitions: `[TO BE FILLED]`
- Exact CWP operational definition: `[TO BE FILLED]`
- Exact NAP operational definition: `[TO BE FILLED]`
- Structural connectome source and construction method: `[TO BE FILLED]`
- CNSOS system definition: `[TO BE FILLED]`
- AI agent roles and implementation boundaries: `[TO BE FILLED]`
- Frozen preprocessing pipelines: `[TO BE FILLED]`
- Train/validation/holdout split logic: `[TO BE FILLED]`
- Statistical models and tests: `[TO BE FILLED]`
- Baselines or competing explanations per paper: `[TO BE FILLED]`
- Null/falsification tests per paper: `[TO BE FILLED]`
- Known results: `[NOT YET RUN]`
- Failed analyses: `[NOT YET RUN]`
- Reproduction command: `[TO BE FILLED]`

## Layer I - CWP Foundations

Layer question:

```text
Is CWP a real and useful scientific object?
```

### Paper 1 - CWP Framework

**Paper type:** Method Paper

**Research question:**  
Do reusable CWP labels generalize better than dataset-specific, flat task labels for predicting brain-state transitions across conditions, tasks, subjects, and datasets?

**Central claim to test:**  
CWP can serve as a reusable cognitive intermediate representation for out-of-task prediction of human brain-state transitions.

**Falsifiable hypothesis:**  
If CWP is a useful intermediate representation, then CWP/context models should improve held-out prediction over strong dataset-specific TaskID baselines, especially under OOD condition, task, subject, and dataset holdouts.

**Primary endpoint:**  
`[TO BE FILLED]`

**Known comparison:**  
CWP/context model vs dataset-specific flat TaskID model and strong TaskID transition-operator baseline.

**Dataset plan:**  
OpenNeuro ds001635 for primary discovery, OpenNeuro ds001634 for external holdout, and MDTB ds002105 for final leave-one-entire-task-out testing. Exact dataset metadata remains `[TO BE FILLED]`.

**Frozen pipeline plan:**  
`download + checksum -> preprocessing -> fixed-atlas ROI state extraction -> HRF/deconvolution or delay-aware stage estimation -> frozen CWP/context/task labels -> frozen splits -> M0-M4 training -> OOD holdouts -> null tests -> subject-level statistics -> external replication -> figures/tables -> claim audit`

Core experimental contrast:

```text
same data + same model capacity + same prediction target + same holdout
-> change only label representation
```

**Baselines / competing methods:**  
- M0 State-only.
- M1 Flat Task Label.
- M2 Strong Task Baseline with TaskID-specific transition operator and hierarchical shrinkage.
- M3 CWP Model.
- M4 Task + CWP residual model.

**Holdout plan:**  
Unseen combination, unseen domain, unseen task/dataset, leave-one-subject-out, leave-one-run-out, ds001634 external dataset holdout, and MDTB leave-one-entire-task-out.

Evidence strength:

```text
Unseen Combination < Unseen Domain < Unseen Task / Dataset
```

**Statistics:**  
Held-out predictive log-likelihood / ELPD as primary metric; subject-level paired differences, 10,000 sign-flip permutation, bootstrap 95% CI, FDR, and effect-size reporting. Exact implementation remains `[TO BE FILLED]`.

**Null / falsification tests:**  
Delay-position-preserving shuffle, pseudo-CWP ontology, time-only baseline, domain/load-preserving label shuffle, boundary jitter, confounds-only model, and subject/task swap.

**Known results:**  
`[NOT YET RUN]`

**Missing fields:**  
Exact dataset metadata, final CWP/context/task label schema, atlas, ROI extraction method, HRF/deconvolution method, model hyperparameter rules, claim-audit schema, results, limitations, reproduction command.

### Paper 2 - CWP Reproducibility

**Paper type:** Explanation Paper

**Research question:**  
Do CWP-conditioned transitions reproduce across sessions and individuals?

**Central claim to test:**  
CWP-conditioned transition structure is reproducible across session-level and individual-level variation.

**Falsifiable hypothesis:**  
If CWP-conditioned transitions are reproducible, transition patterns estimated in one session or individual grouping should predict or match corresponding patterns in an independent session or individual grouping above a predefined reproducibility threshold.

**Primary endpoint:**  
`[TO BE FILLED]`

**Known comparison:**  
Across session / individual reproducibility.

**Dataset plan:**  
`[TO BE FILLED]`

**Frozen pipeline plan:**  
`[TO BE FILLED]`

**Baselines / competing explanations:**  
- Session-specific artifact explanation: `[TO BE FILLED]`
- Individual-specific idiosyncrasy explanation: `[TO BE FILLED]`
- Additional competing explanations: `[TO BE FILLED]`

**Holdout plan:**  
`[TO BE FILLED]`

**Statistics:**  
`[TO BE FILLED]`

**Null / falsification tests:**  
`[TO BE FILLED]`

**Known results:**  
`[NOT YET RUN]`

**Missing fields:**  
Dataset, repeated-session design, individual grouping design, reproducibility metric, thresholds, confound controls, holdout, statistics, results, limitations, reproduction command.

### Paper 3 - Noise Robustness

**Paper type:** Explanation Paper

**Research question:**  
Are observed CWP transitions robust to noise, motion, drift, and artifact explanations?

**Central claim to test:**  
Observed transitions are not reducible to noise, motion, drift, or artifact.

**Falsifiable hypothesis:**  
If CWP transitions reflect meaningful dynamics rather than artifacts, transition structure should remain detectable after predefined artifact controls and should fail under appropriate null or artifact-destroying controls.

**Primary endpoint:**  
`[TO BE FILLED]`

**Known competing explanations:**  
- Noise.
- Motion.
- Drift.
- Artifact.

**Dataset plan:**  
`[TO BE FILLED]`

**Frozen pipeline plan:**  
`[TO BE FILLED]`

**Baselines / competing explanations:**  
Noise, motion, drift, artifact models or controls: `[TO BE FILLED]`

**Holdout plan:**  
`[TO BE FILLED]`

**Statistics:**  
`[TO BE FILLED]`

**Null / falsification tests:**  
`[TO BE FILLED]`

**Known results:**  
`[NOT YET RUN]`

**Missing fields:**  
Noise model, motion metrics, drift definition, artifact detection method, robustness endpoint, control pipeline, holdout, statistics, results, limitations, reproduction command.

### Paper 4 - Structural Constraint

**Paper type:** Explanation Paper

**Research question:**  
Does the structural connectome constrain the transition from state S_t to state S_t+1?

**Central claim to test:**  
Structural connectivity constrains brain-state transitions.

**Falsifiable hypothesis:**  
If structural connectivity constrains transitions, structural-connectome-derived constraints should predict or explain S_t to S_t+1 transitions better than predefined null structural controls.

**Primary endpoint:**  
`[TO BE FILLED]`

**Known phenomenon:**  
S_t -> S_t+1 transition under structural constraint.

**Dataset plan:**  
`[TO BE FILLED]`

**Frozen pipeline plan:**  
`[TO BE FILLED]`

**Baselines / competing explanations:**  
- Null structural connectome controls: `[TO BE FILLED]`
- Non-structural transition models: `[TO BE FILLED]`
- Additional competing explanations: `[TO BE FILLED]`

**Holdout plan:**  
`[TO BE FILLED]`

**Statistics:**  
`[TO BE FILLED]`

**Null / falsification tests:**  
`[TO BE FILLED]`

**Known results:**  
`[NOT YET RUN]`

**Missing fields:**  
Structural connectome source, state definition, transition model, null controls, endpoint, holdout, statistics, results, limitations, reproduction command.

### Paper 5 - CWP to NAP Empirical Bridge

**Paper type:** Explanation Paper

**Research question:**  
Does a specific CWP contain finer-grained, reproducible NAP-like dynamics?

**Central claim to test:**  
Within a specific CWP, there are finer-grained, repeatable NAP-like dynamics.

**Falsifiable hypothesis:**  
If a CWP contains NAP-like dynamics, a predefined within-CWP analysis should reveal finer-grained dynamic patterns that reproduce under independent validation.

**Primary endpoint:**  
`[TO BE FILLED]`

**Known bridge:**  
Specific CWP -> finer-grained NAP-like dynamics.

**Dataset plan:**  
`[TO BE FILLED]`

**Frozen pipeline plan:**  
`[TO BE FILLED]`

**Baselines / competing explanations:**  
- Within-CWP noise explanation: `[TO BE FILLED]`
- Non-reproducible substructure explanation: `[TO BE FILLED]`
- Additional competing explanations: `[TO BE FILLED]`

**Holdout plan:**  
`[TO BE FILLED]`

**Statistics:**  
`[TO BE FILLED]`

**Null / falsification tests:**  
`[TO BE FILLED]`

**Known results:**  
`[NOT YET RUN]`

**Missing fields:**  
Specific CWP, NAP-like operational definition, within-CWP analysis, reproducibility endpoint, dataset, holdout, statistics, results, limitations, reproduction command.

## Layer II - CWP-NAP Multiscale Science

Layer question:

```text
Can CWP-NAP explain real cognitive phenomena?
```

Layer structure:

```text
Framework + 3 Phenomena
```

Phenomenon set:

```text
Transition + Stability + Alteration
```

### Paper 6 - CWP-NAP Framework

**Paper type:** Method Paper

**Research question:**  
Can a generalized CWP-NAP multiscale formal architecture connect CWP-level dynamics with NAP-level dynamics?

**Central claim to test:**  
A CWP-NAP framework can formally relate coarse brain-state dynamics to finer-grained neural activity patterns.

**Falsifiable hypothesis:**  
If the framework is useful, it should generate predefined measurable predictions or analyses that can be evaluated on held-out data.

**Primary endpoint:**  
`[TO BE FILLED]`

**Known framework role:**  
Generalized CWP <-> NAP multiscale architecture.

**Dataset plan:**  
`[TO BE FILLED]`

**Frozen pipeline plan:**  
`[TO BE FILLED]`

**Baselines / competing methods:**  
- CWP-only framework: `[TO BE FILLED]`
- NAP-only framework: `[TO BE FILLED]`
- Additional alternatives: `[TO BE FILLED]`

**Holdout plan:**  
`[TO BE FILLED]`

**Statistics:**  
`[TO BE FILLED]`

**Null / falsification tests:**  
`[TO BE FILLED]`

**Known results:**  
`[NOT YET RUN]`

**Missing fields:**  
Formal definitions, measurable predictions, endpoint, dataset, pipeline, baselines, holdout, statistics, results, limitations, reproduction command.

### Paper 7 - Insight

**Paper type:** Explanation Paper

**Research question:**  
Is insight associated with abrupt transition dynamics?

**Central claim to test:**  
Insight may be characterized by abrupt transition dynamics in the CWP-NAP framework.

**Falsifiable hypothesis:**  
If insight is associated with abrupt transition, insight events should show a predefined abrupt-transition signature relative to appropriate non-insight controls.

**Primary endpoint:**  
`[TO BE FILLED]`

**Known phenomenon mapping:**  
Insight -> abrupt transition.

**Dataset plan:**  
`[TO BE FILLED]`

**Frozen pipeline plan:**  
`[TO BE FILLED]`

**Competing explanations:**  
`[TO BE FILLED]`

**Holdout plan:**  
`[TO BE FILLED]`

**Statistics:**  
`[TO BE FILLED]`

**Null / falsification tests:**  
`[TO BE FILLED]`

**Known results:**  
`[NOT YET RUN]`

**Missing fields:**  
Insight task/data definition, event labeling, abrupt-transition metric, controls, dataset, holdout, statistics, results, limitations, reproduction command.

### Paper 8 - Flow

**Paper type:** Explanation Paper

**Research question:**  
Is flow associated with stability or persistence dynamics?

**Central claim to test:**  
Flow may be characterized by stability or persistence in CWP-NAP dynamics.

**Falsifiable hypothesis:**  
If flow is associated with stability or persistence, flow states should show a predefined stability/persistence signature relative to appropriate non-flow controls.

**Primary endpoint:**  
`[TO BE FILLED]`

**Known phenomenon mapping:**  
Flow -> stability / persistence.

**Dataset plan:**  
`[TO BE FILLED]`

**Frozen pipeline plan:**  
`[TO BE FILLED]`

**Competing explanations:**  
`[TO BE FILLED]`

**Holdout plan:**  
`[TO BE FILLED]`

**Statistics:**  
`[TO BE FILLED]`

**Null / falsification tests:**  
`[TO BE FILLED]`

**Known results:**  
`[NOT YET RUN]`

**Missing fields:**  
Flow operational definition, state labeling, stability/persistence metric, controls, dataset, holdout, statistics, results, limitations, reproduction command.

### Paper 9 - Alexithymia

**Paper type:** Explanation Paper

**Research question:**  
Is alexithymia associated with altered CWP-NAP dynamics?

**Central claim to test:**  
Alexithymia may be characterized by altered dynamics in the CWP-NAP framework.

**Falsifiable hypothesis:**  
If alexithymia is associated with altered dynamics, individuals or states meeting a predefined alexithymia definition should show a predefined alteration signature relative to appropriate controls.

**Primary endpoint:**  
`[TO BE FILLED]`

**Known phenomenon mapping:**  
Alexithymia -> altered dynamics.

**Dataset plan:**  
`[TO BE FILLED]`

**Frozen pipeline plan:**  
`[TO BE FILLED]`

**Competing explanations:**  
`[TO BE FILLED]`

**Holdout plan:**  
`[TO BE FILLED]`

**Statistics:**  
`[TO BE FILLED]`

**Null / falsification tests:**  
`[TO BE FILLED]`

**Known results:**  
`[NOT YET RUN]`

**Missing fields:**  
Alexithymia measure, group/state definition, alteration metric, controls, dataset, holdout, statistics, results, limitations, reproduction command.

## Layer III - CNSOS / AI4S

Layer question:

```text
Can AI partially automate real scientific discovery?
```

Closed-loop target:

```text
Data -> Discovery -> Hypothesis -> Experiment -> Falsification -> Theory Update -> Replication
```

### Paper 10 - CNSOS Framework

**Paper type:** Method Paper

**Research question:**  
Can CNSOS reliably execute a complete scientific workflow?

**Central claim to test:**  
CNSOS can execute a complete scientific workflow in a stable and auditable way.

**Falsifiable hypothesis:**  
If CNSOS can execute the workflow, it should complete predefined workflow stages with traceable outputs and without violating predefined scientific or reproducibility constraints.

**Primary endpoint:**  
`[TO BE FILLED]`

**Known workflow target:**  
Complete scientific workflow execution.

**Dataset / task plan:**  
`[TO BE FILLED]`

**Frozen pipeline plan:**  
`[TO BE FILLED]`

**Baselines / competing systems:**  
`[TO BE FILLED]`

**Holdout plan:**  
`[TO BE FILLED]`

**Statistics / evaluation:**  
`[TO BE FILLED]`

**Null / falsification tests:**  
`[TO BE FILLED]`

**Known results:**  
`[NOT YET RUN]`

**Missing fields:**  
CNSOS definition, workflow stages, success/failure criteria, audit trail, task set, baselines, holdout, evaluation metrics, results, limitations, reproduction command.

### Paper 11 - Automated Pattern Discovery

**Paper type:** Method Paper

**Research question:**  
Can AI discover human-missed structures that replicate?

**Central claim to test:**  
AI may discover structures that were not identified by human analysis and that replicate under validation.

**Falsifiable hypothesis:**  
If AI can discover valid missed structures, AI-generated pattern candidates should replicate on independent data at a rate exceeding a predefined baseline.

**Primary endpoint:**  
`[TO BE FILLED]`

**Known task:**  
Discover human-missed, replicable structure.

**Dataset / task plan:**  
`[TO BE FILLED]`

**Frozen pipeline plan:**  
`[TO BE FILLED]`

**Baselines / competing systems:**  
- Human-known pattern set: `[TO BE FILLED]`
- Non-AI or random discovery baseline: `[TO BE FILLED]`
- Additional baselines: `[TO BE FILLED]`

**Holdout plan:**  
`[TO BE FILLED]`

**Statistics / evaluation:**  
`[TO BE FILLED]`

**Null / falsification tests:**  
`[TO BE FILLED]`

**Known results:**  
`[NOT YET RUN]`

**Missing fields:**  
Definition of "human-missed", replication criterion, discovery agent design, baseline, dataset, holdout, statistics, results, limitations, reproduction command.

### Paper 12 - Automated Hypothesis Generation

**Paper type:** Method Paper

**Research question:**  
Do AI-generated hypotheses have higher empirical yield than random or template baselines?

**Central claim to test:**  
AI-generated hypotheses may produce greater empirical yield than random/template-generated hypotheses.

**Falsifiable hypothesis:**  
If AI hypothesis generation is useful, AI-generated hypotheses should exceed random or template baselines on a predefined empirical-yield endpoint.

**Primary endpoint:**  
`[TO BE FILLED]`

**Known comparison:**  
AI hypothesis generation vs random/template baseline.

**Dataset / task plan:**  
`[TO BE FILLED]`

**Frozen pipeline plan:**  
`[TO BE FILLED]`

**Baselines / competing systems:**  
- Random hypothesis baseline.
- Template hypothesis baseline.
- Additional baselines: `[TO BE FILLED]`

**Holdout plan:**  
`[TO BE FILLED]`

**Statistics / evaluation:**  
`[TO BE FILLED]`

**Null / falsification tests:**  
`[TO BE FILLED]`

**Known results:**  
`[NOT YET RUN]`

**Missing fields:**  
Hypothesis representation, empirical-yield endpoint, random baseline construction, template baseline construction, task set, holdout, statistics, results, limitations, reproduction command.

### Paper 13 - Automated Experiment Design

**Paper type:** Method Paper

**Research question:**  
Can AI generate executable, statistically valid, leakage-resistant experiments?

**Central claim to test:**  
AI can generate experiment designs that are executable, statistically valid, and leakage-resistant.

**Falsifiable hypothesis:**  
If AI experiment design is useful, AI-generated designs should pass predefined executability, statistical-validity, and leakage-resistance criteria at a rate exceeding predefined baselines.

**Primary endpoint:**  
`[TO BE FILLED]`

**Known task:**  
Executable, statistically valid, leakage-resistant experiment design.

**Dataset / task plan:**  
`[TO BE FILLED]`

**Frozen pipeline plan:**  
`[TO BE FILLED]`

**Baselines / competing systems:**  
`[TO BE FILLED]`

**Holdout plan:**  
`[TO BE FILLED]`

**Statistics / evaluation:**  
`[TO BE FILLED]`

**Null / falsification tests:**  
`[TO BE FILLED]`

**Known results:**  
`[NOT YET RUN]`

**Missing fields:**  
Experiment-design constraints, validity rubric, leakage rubric, execution environment, baselines, holdout, statistics, results, limitations, reproduction command.

### Paper 14 - Automated Falsification

**Paper type:** Method Paper

**Research question:**  
Can a red-team agent reduce false discovery without eliminating true positives?

**Central claim to test:**  
An automated falsification/red-team agent can reduce false discoveries while preserving true positives.

**Falsifiable hypothesis:**  
If automated falsification is useful, adding a red-team agent should reduce false discoveries relative to a no-red-team workflow without causing an unacceptable reduction in predefined true-positive retention.

**Primary endpoint:**  
`[TO BE FILLED]`

**Known comparison:**  
Workflow with red-team agent vs workflow without red-team agent.

**Dataset / task plan:**  
`[TO BE FILLED]`

**Frozen pipeline plan:**  
`[TO BE FILLED]`

**Baselines / competing systems:**  
- No-red-team baseline.
- Alternative falsification baselines: `[TO BE FILLED]`

**Holdout plan:**  
`[TO BE FILLED]`

**Statistics / evaluation:**  
`[TO BE FILLED]`

**Null / falsification tests:**  
`[TO BE FILLED]`

**Known results:**  
`[NOT YET RUN]`

**Missing fields:**  
False-discovery definition, true-positive definition, red-team protocol, retention threshold, task set, holdout, statistics, results, limitations, reproduction command.

### Paper 15 - Closed-Loop Autonomous Discovery

**Paper type:** Method Paper

**Research question:**  
Can an automated system close the loop from data to discovery, hypothesis, experiment, falsification, theory update, and replication?

**Central claim to test:**  
A closed-loop system can execute the full discovery cycle with traceable, reproducible outputs.

**Falsifiable hypothesis:**  
If closed-loop autonomous discovery is feasible, the system should complete the full predefined loop and produce reproducible outputs that pass predefined validation, falsification, and replication checks.

**Primary endpoint:**  
`[TO BE FILLED]`

**Known workflow:**  
Data -> Discovery -> Hypothesis -> Experiment -> Falsification -> Theory Update -> Replication.

**Dataset / task plan:**  
`[TO BE FILLED]`

**Frozen pipeline plan:**  
`[TO BE FILLED]`

**Baselines / competing systems:**  
`[TO BE FILLED]`

**Holdout plan:**  
`[TO BE FILLED]`

**Statistics / evaluation:**  
`[TO BE FILLED]`

**Null / falsification tests:**  
`[TO BE FILLED]`

**Known results:**  
`[NOT YET RUN]`

**Missing fields:**  
Loop implementation, stage gates, theory-update representation, replication criteria, task set, baselines, holdout, statistics, results, limitations, reproduction command.

## Program-Level A1-A10 Reproducibility Attachment Standard

Each paper should eventually receive its own A1-A10 packet. At the master-architecture level, the shared attachment template is:

### A1 - Frozen Protocol

- Research question: paper-specific.
- Falsifiable hypothesis: paper-specific.
- Primary endpoint: `[TO BE FILLED]`
- Secondary endpoints: `[TO BE FILLED]`
- Inclusion/exclusion rules: `[TO BE FILLED]`
- Preprocessing rules: `[TO BE FILLED]`
- Feature definitions: `[TO BE FILLED]`
- Model or analysis specification: `[TO BE FILLED]`
- Baselines / competing explanations: paper-specific.
- Data split logic: `[TO BE FILLED]`
- Holdout definition: `[TO BE FILLED]`
- Statistical tests: `[TO BE FILLED]`
- Null / falsification tests: `[TO BE FILLED]`
- Success criteria: `[TO BE FILLED]`
- Failure criteria: `[TO BE FILLED]`
- Deviations policy: `[TO BE FILLED]`
- Freeze version: `[TO BE FILLED]`
- Freeze timestamp or immutable version identifier: `[TO BE FILLED]`

### A2 - Dataset Manifest

- Dataset name: `[TO BE FILLED]`
- Source: `[TO BE FILLED]`
- Version / release: `[TO BE FILLED]`
- Accession / identifier: `[TO BE FILLED]`
- Modality: `[TO BE FILLED]`
- Sample / subject inventory: `[TO BE FILLED]`
- Inclusion / exclusion decisions: `[TO BE FILLED]`
- Train / validation / holdout membership: `[TO BE FILLED]`
- File checksums: `[TO BE FILLED]`
- Missing-data record: `[TO BE FILLED]`
- Licensing / access requirements: `[TO BE FILLED]`
- Dataset-specific caveats: `[TO BE FILLED]`

### A3 - Full Pipeline

- Raw data path: `[TO BE FILLED]`
- QC steps: `[TO BE FILLED]`
- Preprocessing: `[TO BE FILLED]`
- Representation / features: `[TO BE FILLED]`
- Model / analysis: `[TO BE FILLED]`
- Statistics: `[TO BE FILLED]`
- Figures / tables: `[TO BE FILLED]`
- Software versions: `[TO BE FILLED]`
- Seeds: `[TO BE FILLED]`
- Evaluation code path: `[TO BE FILLED]`

### A4 - Full Baseline or Competing-Explanation Results

- Planned baselines or competing explanations: paper-specific.
- Full result table: `[NOT YET RUN]`
- Negative or unfavorable results: `[NOT YET RUN]`
- Deviations from planned baselines: `[TO BE FILLED]`

### A5 - Holdout Audit

- Holdout definition: `[TO BE FILLED]`
- Isolation mechanism: `[TO BE FILLED]`
- Access policy: `[TO BE FILLED]`
- Access log: `[TO BE FILLED]`
- Date/version of first evaluation: `[TO BE FILLED]`
- Number of holdout evaluations: `[TO BE FILLED]`
- Post-holdout changes: `[TO BE FILLED]`
- Final immutable evaluation artifact: `[TO BE FILLED]`

### A6 - Statistics

- Estimand / target quantity: `[TO BE FILLED]`
- Statistical tests: `[TO BE FILLED]`
- Effect sizes: `[NOT YET RUN]`
- Uncertainty intervals: `[NOT YET RUN]`
- Multiple-comparison correction: `[TO BE FILLED]`
- Assumptions: `[TO BE FILLED]`
- Sensitivity analyses: `[TO BE FILLED]`
- Missing-data handling: `[TO BE FILLED]`
- Complete result tables: `[NOT YET RUN]`

### A7 - Null / Falsification Tests

- Paper-specific falsification tests: `[TO BE FILLED]`
- Negative controls: `[TO BE FILLED]`
- Permutation or shuffle controls: `[TO BE FILLED]`
- Synthetic null controls: `[TO BE FILLED]`
- Confound or adversarial tests: `[TO BE FILLED]`
- Results: `[NOT YET RUN]`

### A8 - QC and Leakage Audit

- Subject leakage: `[TO BE FILLED]`
- Session leakage: `[TO BE FILLED]`
- Temporal leakage: `[TO BE FILLED]`
- Preprocessing leakage: `[TO BE FILLED]`
- Normalization leakage: `[TO BE FILLED]`
- Feature leakage: `[TO BE FILLED]`
- Label leakage: `[TO BE FILLED]`
- Duplicate / near-duplicate contamination: `[TO BE FILLED]`
- Site / scanner confounding: `[TO BE FILLED]`
- Batch effects: `[TO BE FILLED]`
- Demographic confounding: `[TO BE FILLED]`
- Train/test contamination: `[TO BE FILLED]`
- Researcher-induced leakage: `[TO BE FILLED]`
- Post-hoc selection: `[TO BE FILLED]`

### A9 - Limitations and Failed Analyses

- Known limitations: `[TO BE FILLED]`
- Failed analyses: `[NOT YET RUN]`
- Negative results: `[NOT YET RUN]`
- Unsupported hypotheses: `[TO BE FILLED]`
- Unstable findings: `[NOT YET RUN]`
- Discarded methods and why: `[TO BE FILLED]`
- Protocol deviations: `[TO BE FILLED]`
- Unresolved confounds: `[TO BE FILLED]`
- Boundary conditions: `[TO BE FILLED]`
- Claims the data cannot support: `[TO BE FILLED]`

### A10 - One-Command Reproduction

Target command:

```bash
make reproduce
```

Current status:

```text
[TO BE FILLED]
```

The reproduction command should eventually:

1. Validate environment.
2. Obtain or locate authorized data.
3. Verify dataset manifest and checksums.
4. Run preprocessing.
5. Run the frozen analysis.
6. Run baselines or competing models.
7. Run statistics.
8. Run null/falsification tests.
9. Regenerate main tables.
10. Regenerate main figures.
11. Emit a reproducibility report.

## Quality Gate

This master architecture is not a completed paper package. It is a controlled scaffold.

Current quality-gate status:

| Gate | Status |
| --- | --- |
| Central claims are specific enough to begin protocol design | PARTIAL |
| Hypotheses are falsifiable at the architecture level | PARTIAL |
| Primary endpoints are explicit | MISSING |
| Dataset and cohort are reproducibly defined | MISSING |
| Pipeline is frozen before final holdout evaluation | MISSING |
| Baselines or competing explanations are fully specified | MISSING |
| Holdout is genuinely isolated | MISSING |
| Statistics match the data structure | MISSING |
| Null/falsification tests can challenge the claim | PARTIAL |
| QC and leakage risks are audited | MISSING |
| Limitations include claim boundaries | PARTIAL |
| Failed analyses are disclosed | MISSING |
| Main results can be reproduced from a locked environment | MISSING |
| Unsupported causal language is avoided | PASS |
| No result is invented | PASS |

## Highest-Risk Missing Decisions

1. CWP must receive an operational definition before any paper can claim representation validity.
2. NAP must receive an operational definition before the CWP-to-NAP bridge can be tested.
3. Each paper needs a primary endpoint before it can have a frozen protocol.
4. Each paper needs a dataset and cohort definition before statistical claims are possible.
5. Layer III needs an explicit CNSOS system boundary before AI4S claims can be tested.
6. Holdout and leakage controls must be defined before any discovery result can be treated as confirmatory.
7. No paper should be framed as having results until the relevant analysis has been run and recorded.
