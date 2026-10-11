# A5. Holdout Audit

Status:

```text
COMPLETED_FINAL_PRIMARY_ANALYSIS
```

Frozen rule:

```text
Development and smoke subjects were used to tune feasibility, atlas alignment, and QC mechanics.
Before final model interpretation, PAPER7_PRE_100_SUBJECT_QC_FREEZE_v0_2.md fixed the exclusion rule for warning-positive or sparse connectomes.
100307 was excluded by that pre-modeling rule.
The final primary model test used the remaining 99 subjects.
```

Final evaluation:

```text
n_available_connectomes_before_qc_exclusion = 100
n_final_primary_subjects = 99
excluded_primary_subjects = 100307
final_result = FINAL_STRUCTURAL_HYPOTHESIS_NOT_SUPPORTED
```

Access/deviation note:

```text
The 99-subject final analysis is the frozen primary analysis for this package.
It is not a separate new external dataset holdout.
No post-result ontology or model change is used to rescue the structural hypothesis.
```

Evidence:

```text
paper7/protocol/PAPER7_PRE_100_SUBJECT_QC_FREEZE_v0_2.md
paper7/results/p7_e7_final_structural_hypothesis_test.json
paper7/results/p7_e8_claim_audit.json
```
