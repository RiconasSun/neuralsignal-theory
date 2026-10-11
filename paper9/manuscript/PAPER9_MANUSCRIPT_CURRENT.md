# Dynamics-First Ontology Reconstruction for Claim-Safe CWP/NAP Theory Revision

## Abstract

The first eight papers in the NeuralSignal Institute CWP/NAP Layer I program produced a mixed evidence boundary rather than a validated primitive theory. Local compositional signals and reproducible macroscopic dynamics were observed, but CWP-specific external superiority, NAP validation, subject-specific structural grounding, and full measured-physiology exclusion remain unsupported or unresolved. We therefore introduce a dynamics-first Ontology v2 framework that begins with observables, neural states, and transition families before allowing candidate motifs, candidate NAPs, candidate CWPs, semantics, or grammar. The contribution of this paper is a claim-safe ontology and evidence-status system that encodes positive, negative, confounded, blocked, and untested P1-P8 results without claim inflation. No new neural mechanism is asserted by P9.

## 1. Introduction

### 1.1 Problem

The original CWP/NAP framing risked treating semantic primitives as if they were already validated neural objects. P1-P8 showed that this is too strong. The surviving object is better described as reproducible computational cognitive neurodynamics, while ontology, physiological robustness, and mechanistic grounding remain under active testing.

### 1.2 Literature Context

P9 sits at the intersection of cognitive ontology, reproducible neuroimaging, and dynamic brain-state modeling. The Cognitive Atlas formalized a key distinction between mental tasks and latent mental processes, which is central to the CWP problem because a task label is not the same thing as the cognitive operation it is assumed to evoke [Poldrack2011CognitiveAtlas]. RDoC provides a separate precedent for evidence-linked constructs whose status depends on behavioral and neural support rather than naming alone [Insel2010RDoC]. BIDS and OpenNeuro provide the data-organization and sharing context for reproducible neuroimaging analyses [Gorgolewski2016BIDS; OpenNeuro2026], while HCP supplies a major multimodal reference point for linking task-fMRI, structural imaging, and behavior [VanEssen2013HCP].

Dynamic brain-state work further motivates the ontology problem. Prior work has shown that large-scale neural activity can be described with transient or switching states, including HMM-based electrophysiological states and hidden brain-state dynamics during cognition [Vidaurre2018HMM; Taghia2018BSDS]. At the same time, dynamic functional connectivity work emphasizes interpretive caution: time-varying states can be meaningful, but they can also be shaped by methodological choices and competing explanations [Hutchison2013DynamicFC].

### 1.3 Scientific Gap

A research program with negative and boundary results needs a representation language that can carry failures without hiding them. A flat success/failure narrative is not enough because some findings are local, some are reproducible, some are confounded, and some are blocked by missing data or incomplete toolchains.

### 1.4 Proposed Method

We replace the old direction:

```text
CWP -> Dynamics
```

with:

```text
Observable -> State -> Transition -> Motif -> Candidate Primitive -> Semantics
```

This makes neural and behavioral evidence primary, and treats CWP/NAP labels as candidate interpretations that require explicit upgrade evidence.

Post-P10 addendum: P10 did not support the discrete dynamic-motif hypothesis under the tested feature regime and favored continuous low-dimensional latent dynamics over discrete motif reconstruction. Therefore the downstream P11/P12 route is updated from motif-sequence semantics and neural grammar to continuous latent semantics and neural dynamical syntax / flow rules:

```text
Observable -> State -> Transition -> Continuous Latent Trajectory -> Candidate Semantics -> Flow Rules
```

### 1.5 Contributions

1. A P1-P8 evidence matrix with allowed and disallowed claims.
2. A status taxonomy for observed, reproducible, OOD-supported, externally replicated, candidate, unsupported, confounded, blocked, and untested objects.
3. A CWP/NAP Ontology v2 schema.
4. Claim upgrade and downgrade rules.
5. A claim audit that prevents P9 from asserting unrun P10-P12 results.

## 2. Methods

### 2.1 Inputs

The inputs are the local P1-P8 paper packages, including results summaries, claim audits, manuscripts, and Layer I boundary documents. P9 does not download new data or re-run neural analyses.

### 2.2 Evidence Matrix

Each P1-P8 row records the paper title, source paths, allowed claim, primary evidence, primary gate, holdout status, null status, evidence status, disallowed claim, and ontology use.

### 2.3 Ontology Objects

Ontology v2 defines Observable, NeuralState, TransitionFamily, DynamicMotif, CandidateNAP, CandidateCWP, CognitiveProgram, ContextModifier, CompetingExplanation, and ClaimBoundary.

### 2.4 Evidence Statuses

The status labels are OBSERVED, REPRODUCIBLE, OOD_SUPPORTED, EXTERNALLY_REPLICATED, CANDIDATE, NOT_SUPPORTED, FAILED_PRIMARY_GATE, CONFOUNDED, DATA_BLOCKED, TOOLCHAIN_BLOCKED, and UNTESTED.

### 2.5 Claim Audit

The audit checks that P9 permits only ontology-level conclusions. Dynamic motifs, discrete NAPs, CWP v2 semantics, neural grammar, external replication, and universal theory remain disallowed unless later papers supply frozen evidence.

## 3. Results

### 3.1 Encoded Evidence

All eight P1-P8 rows are encoded in `results/encoded_p1_p8_evidence.json`.

### 3.2 Status Distribution

The evidence matrix intentionally contains mixed statuses: OOD-supported, reproducible, candidate, confounded, not-supported, and toolchain-blocked. This is the point of P9: the ontology must preserve boundary results instead of turning them into a success-only narrative.

### 3.3 Claim Audit

`results/claim_audit.json` passes with zero violations. The audit allows only the claim that Ontology v2 encodes P1-P8 without contradiction. It does not allow validated CWP, validated NAP, CWP-specific external superiority, structural grounding, measured-physiology elimination, or neural grammar.

## 4. Discussion

### 4.1 What P9 Supports

P9 supports a claim-safe ontology architecture for the next phase of the program. It makes the surviving evidence object explicit: reproducible computational cognitive neurodynamics.

### 4.2 What P9 Does Not Support

P9 does not show that dynamic motifs exist, that motifs are NAPs, that motifs carry cognitive semantics, or that motif sequences form grammar. After P10, discrete motif-token semantics and motif grammar are no longer the active downstream route. P11 should test cognitive semantics of continuous latent dynamics, and P12 should test continuous dynamical syntax / flow rules.

### 4.3 Why This Matters

The framework prevents theory repair by relabeling. A failed external holdout stays failed. A confound stays visible. A blocked structural test is not treated as support or refutation. A candidate primitive remains candidate-level until it passes a frozen upgrade path.

### 4.4 Limitations

P9 is a framework and audit paper. It depends on the fidelity of the local P1-P8 packages and does not add independent empirical evidence. Literature review, author metadata, and external repository citation remain `[TO BE FILLED]`.

## 5. Conclusion

P9 converts the P1-P8 evidence boundary into a dynamics-first CWP/NAP Ontology v2 framework. The paper's legitimate conclusion is methodological: a structured ontology can encode surviving, failed, confounded, blocked, and untested claims without inflating them. P10 has now constrained the downstream route: P11/P12 should proceed through continuous latent semantics and flow-rule tests rather than discrete motif-token grammar.

## Data Availability

Publication supplement: [P9 data sources, sample manifests, access conditions, and figure provenance](../DATA_AVAILABILITY.md). Code, papers, and derived results are published at [neuralsignal-theory/test](https://github.com/RiconasSun/neuralsignal-theory/tree/test). Raw participant imaging/signals and tractography remain with the original data providers and are not redistributed. The supplement records dataset identifiers and versions available in existing evidence, links to cohort/pipeline records, and distinguishes unrecorded historical metadata from verified information. Exact local withheld filenames and SHA256 values are recorded in [the raw file inventory](../../publication/raw_file_inventory.csv); derived artifacts and figures have [SHA256 checksums](../../publication/artifact_checksums.csv).

No new dataset is introduced. P9 consumes local P1-P8 evidence artifacts. Repository: [neuralsignal-theory/test](https://github.com/RiconasSun/neuralsignal-theory/tree/test); archival DOI is not assigned.

## Code Availability

Reproduction script: `paper9/scripts/run_paper9.py`. Public code: [neuralsignal-theory/test](https://github.com/RiconasSun/neuralsignal-theory/tree/test).

## Reproducibility Statement

Run:

```bash
make reproduce-paper9
```

This regenerates the evidence matrix, ontology schema, encoded evidence, claim audit, manuscript, and A1-A10 attachments.

## Ethics Statement

P9 analyzes existing paper-level evidence artifacts and does not introduce new human-subject data processing.

## Author Contributions

`[TO BE FILLED]`

## Conflicts of Interest

`[TO BE FILLED]`

## References

See `paper9/references/references.md` and `paper9/references/references.bib`.
