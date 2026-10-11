# Paper 9 Frozen Protocol v1

Status: frozen framework protocol  
Generated: 2026-09-06T04:46:38+00:00

## Title

Dynamics-First Ontology Reconstruction for Claim-Safe CWP/NAP Theory Revision

## Research Question

Can the P1-P8 evidence chain be encoded into a CWP/NAP Ontology v2 without converting candidate, failed, blocked, or confounded claims into validated primitives?

## Primary Hypothesis

A dynamics-first ontology with explicit evidence-status labels can encode all major P1-P8 positive, negative, blocked, and untested claims without contradiction or claim inflation.

## Primary Endpoint

All P1-P8 claim rows in `paper9/evidence_matrix/p1_p8_claim_matrix.csv` are mapped into Ontology v2 objects with an evidence status, allowed claim, disallowed claim, and competing-explanation record.

## Success Criteria

- Every P1-P8 row is encoded.
- No disallowed universal CWP/NAP claim is allowed by `claim_audit.json`.
- Negative and blocked results retain negative or blocked statuses.
- P10-P12 dependencies are explicit and cannot be bypassed.

## Failure Criteria

- Any P1-P8 result requires an unsupported success label.
- The schema cannot represent confounded, blocked, or failed primary-gate results.
- Claim audit permits CWP/NAP validation before P10-P12 evidence exists.

## Frozen Pipeline

```text
P1-P8 local evidence packages
-> p1_p8_claim_matrix.csv
-> status_taxonomy.json
-> ontology_v2_schema.json
-> encoded_p1_p8_evidence.json
-> claim_audit.json
-> manuscript and A1-A10 attachments
```

## Baselines / Competing Ontologies

```text
Old CWP v1 string-label ontology
Flat task-label ontology
Pure continuous dynamics account
Generic latent-factor ontology
Dataset-specific ontology
Timing/metadata ontology
```

## Holdout Audit

No new neural-data holdout is used in P9. The holdout logic is conceptual and document-level: P9 does not upgrade any empirical claim beyond the status already carried by P1-P8. Future P10-P12 final holdouts remain separate.

## Null / Falsification Tests

```text
claim inflation audit
unsupported status audit
dependency bypass audit
confound erasure audit
failure relabeling audit
```

## One-Command Reproduction

```bash
make reproduce-paper9
```
