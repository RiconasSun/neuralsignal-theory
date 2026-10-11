# A1 Frozen Protocol

Paper: Paper 2 - Cross-Dataset Failure and Generalization  
Status: protocol frozen; current run completed through Dataset C final holdout  
Date: 2026-09-01

## Research Question

Why did Paper 1 show within-dataset CWP-style OOD signal in ds001635, but fail external validation on ds001634?

## Falsifiable Hypothesis

External failure can be decomposed into:

```text
F_external = F_measurement + F_state + F_task + F_ontology
```

At least one preregistered component should explain a measurable portion of the A -> B generalization drop.

## Primary Endpoint

External predictive performance under shift-decomposition interventions.

Final primary metric:

```text
MSE for current implemented run; R2 and cosine similarity are secondary metrics.
```

## Secondary Endpoints

- Dataset-shift classifier performance.
- Task-context similarity vs transfer performance.
- Ontology complexity vs external generalization.
- Semantic CWP ontology vs random/pseudo compositional ontology.
- Dataset C final external holdout result.

## Frozen Pipeline

```text
E9.0 Reproduce Failure
-> E9.1 Measurement Shift
-> E9.2 State Representation Shift
-> E9.3 Task-Context Shift
-> E9.4 Ontology Stress Test
-> E9.5 Failure Attribution
-> E9.6 Frozen v2 Representation
-> E9.7 Dataset C Final Holdout
-> E9.8 Statistics + Claim Audit
```

## Success Criteria

Gate A: at least one preregistered factor explains A -> B failure.  
Gate B: frozen v2 improves over v1 on Dataset B.  
Gate C: frozen v2 succeeds on a never-seen Dataset C and beats both StrongTask and Random/PseudoOntology.

Current Gate C result:

```text
FAILED
CWP_v2_medium beat RandomOntology but did not beat M2_strong_task on Dataset C.
```

## Failure Criteria

- Paper 1 external failure cannot be reproduced.
- Dataset B is used as if it were still a clean independent final holdout.
- Dataset C performance is inspected before v2 is frozen.
- Results are used to retroactively rewrite Paper 1 as externally successful.
- CWP-specific generalization is claimed without beating random/pseudo ontology.

## Freeze Rule

P2 may diagnose and revise after P1, but it must not rescue P1 post hoc.
