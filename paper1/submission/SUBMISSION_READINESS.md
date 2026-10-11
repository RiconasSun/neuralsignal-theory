# Paper 1 Submission Readiness

Date: 2026-09-01

## Current Status

Status: PARTIAL bioRxiv-ready package.

The manuscript, seven figures, supplementary materials, and submission claim audit have been generated from the completed E0-E8 run.

## Generated Files

- Main manuscript source: `paper1/manuscript/PAPER1_MANUSCRIPT_CURRENT.md`
- Main PDF draft: `paper1/submission/PAPER1_BIORXIV_DRAFT_CURRENT.pdf`
- Figure captions: `paper1/submission/FIGURE_CAPTIONS.md`
- Figures: `paper1/manuscript/figures/`
- Supplement source: `paper1/submission/SUPPLEMENTARY_MATERIAL_CURRENT.md`
- Supplement PDF: `paper1/submission/SUPPLEMENTARY_MATERIAL_CURRENT.pdf`
- Claim audit: `paper1/submission/SUBMISSION_CLAIM_AUDIT.json`

## Scientific Positioning

Allowed positioning:

```text
CWP-style compositional representations improve within-dataset out-of-distribution brain-state prediction, but do not yet generalize across independent datasets.
```

Forbidden positioning:

```text
CWP is validated.
CWP clearly outperforms task labels overall.
CWP externally replicates.
The 216-ROI grid is a neuroanatomical atlas.
```

## Frozen Result Summary

```text
Gate A incremental: INCONCLUSIVE
Gate B OOD: PASSED
Gate C external: FAILED
claim_allowed_cwp_foundation_holds: false
claim_allowed_cwp_clearly_outperforms_task_labels: false
```

## Remaining Human Fields

These cannot be filled without user-provided identity and release decisions:

- Author names
- Affiliations
- Corresponding author email
- Funding statement
- Author contributions
- Conflicts of interest
- Public repository or archive URL for code
- bioRxiv license/reuse choice

## Submission Recommendation

Do not submit until the remaining human fields are filled and the PDF is visually inspected.

Recommended bioRxiv category: `New Results`, if the paper is framed as a new method/representation boundary test with mixed results.

Use `Contradictory Results` only if the submission explicitly frames the result as contradicting a prior claim.
