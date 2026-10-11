# A7 Null and Falsification Tests

Status: planned null suite plus current random-ontology Dataset C falsification result.

## Required Nulls

```text
dataset label shuffle
CWP shuffle
pseudo ontology
random alignment
random ROI correspondence
task-context shuffle
subject permutation
alignment improves everything null
```

## Key Falsification Logic

If alignment improves CWP, task-label, and random-ontology models equally, then the result is not CWP-specific.

Dataset C success requires:

```text
CWP_v2 > StrongTask
AND
CWP_v2 > Random/PseudoOntology
```

If CWP_v2 only beats CWP_v1 but not Random/PseudoOntology, the allowed conclusion is generic compositional transfer, not semantic CWP specificity.

## Results

```text
Dataset C:
CWP_v2_medium MSE: 16921457.350479256
RandomOntology MSE: 20533230.666308556
CWP_v2_medium beat RandomOntology: yes

However:
M2_strong_task MSE: 15411126.594459493
CWP_v2_medium did not beat StrongTask.

Therefore CWP-specific generalization remains unsupported.
```
