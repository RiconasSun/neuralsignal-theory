# A6 Statistics

## Implemented Statistical Outputs

E8 writes:

```text
paper1/results/primary_metrics.csv
paper1/results/subject_level_effects.csv
paper1/results/claim_audit.json
```

## Implemented Methods

- subject-level paired comparison where subject-level rows exist
- bootstrap 95% CI
- sign-flip permutation test
- Benjamini-Hochberg FDR correction

## Current Statistical Result

E8 has been run on real downloaded OpenNeuro data.

```text
Gate A incremental: INCONCLUSIVE
Gate B OOD: PASSED
Gate C external: FAILED
claim_allowed_cwp_foundation_holds: false
claim_allowed_cwp_clearly_outperforms_task_labels: false
```

## Interpretation Rule

E8 is the only local script allowed to write the claim audit. Any manuscript conclusion must follow `claim_audit.json`, not isolated metric files.
