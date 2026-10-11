# A9 Limitations and Failed Analyses

Status: limitations record updated after Dataset C final holdout.

## Known Starting Limitation from Paper 1

Paper 1 did not validate dataset-invariant CWP. It found local within-dataset OOD signal but failed external validation.

## Current Limitations

- Dataset B is contaminated as a final holdout by prior observation.
- Dataset C ds004469 can test ENCODE/MAINTAIN/PROBE transfer only.
- Dataset C cannot test TRANSFORM because the audited event files expose Coding, Retention, and Test, but no manipulation phase.
- CWP ontology revision may overfit A/B if interpreted beyond its diagnostic role.
- Measurement alignment may improve all models non-specifically.
- Task-context similarity metrics may be subjective unless operationalized more deeply.
- Failure attribution may be non-identifiable if shift factors are correlated.
- Dataset C has strong subject-level scale heterogeneity; aggregate and subject-level summaries disagree in direction.
- R_shared_cca_16 emitted a convergence warning and should be treated as exploratory until stabilized.

## Current Failed / Negative Analyses

```text
Dataset C final holdout did not support CWP-specific generalization.
CWP_v2_medium beat RandomOntology but did not beat M2_strong_task.
Failure explanation is not claim-allowed.
CWP-specific fix is not claim-allowed.
Cross-dataset CWP generalization is not claim-allowed.
The A/B v2 candidate has null risk because random ontology produced the largest apparent gap reduction in the A/B diagnostic screen.
```
