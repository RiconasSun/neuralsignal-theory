# Paper 9 Final Handoff

## Final Status

P9 is complete as a claim-safe framework/audit paper package.

## Core Deliverables

- `manuscript/PAPER9_MANUSCRIPT_CURRENT.md`
- `submission/PAPER9_BIORXIV_DRAFT_CURRENT.pdf`
- `references/references.md`
- `references/references.bib`
- `figures/figure1_ontology_flow.png`
- `figures/figure2_evidence_status_map.png`
- `figures/figure3_claim_gates.png`
- `figures/figure4_dependency_graph.png`
- `evidence_matrix/p1_p8_claim_matrix.csv`
- `ontology/ontology_v2_schema.json`
- `ontology/status_taxonomy.json`
- `rules/claim_upgrade_rules.md`
- `results/claim_audit.json`
- `attachments/A1_Frozen_Protocol.md` through `attachments/A10_One_Command_Reproduction.md`

## Scientific Claim Boundary

Allowed:

```text
A dynamics-first ontology can encode P1-P8 evidence boundaries without claim inflation.
```

Not allowed:

```text
CWP v2 is validated.
NAP is validated.
Dynamic motifs exist.
Motifs carry cognitive semantics.
Neural grammar exists.
External replication is established.
Universal primitive theory is established.
```

## Reproduction

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File "paper9/scripts/reproduce-paper9.ps1"
```

Make target when `make` is available:

```bash
make reproduce-paper9
```

## Remaining Administrative Inputs

- Author names.
- Affiliations.
- Conflicts of interest.
- Funding statement.
- Public repository URL or archive DOI.
