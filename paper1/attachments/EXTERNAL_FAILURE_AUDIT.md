# External Failure Audit

Date: 2026-09-01

## Frozen Rule

The ds001634 external validation failure is a frozen v1 result.

Do not tune any of the following against ds001634 to rescue Gate C:

- CWP v1 ontology
- HRF lag
- native-grid ROI construction
- preprocessing/alignment
- model structure
- success thresholds
- metric choice

Any revised analysis must be registered as CWP v2 before using ds001634 failure information as development feedback.

## Observed Failure

E7 external validation mean MSE:

```text
M0_state: 528.9595753463202
M1_flat_task: 529.0050987946481
M2_strong_task: 529.0031639473207
M3_cwp: 532.1089214151368
M4_task_plus_cwp: 528.9681855141137
```

Gate C:

```text
FAILED
```

Operational interpretation:

```text
M3_cwp did not outperform M2_strong_task on the independent ds001634 external dataset.
```

## Possible Explanations To Audit

These are hypotheses for failure analysis, not conclusions.

1. CWP ontology mismatch

The ENCODE / MAINTAIN / PROBE labels may not map cleanly across ds001635 and ds001634.

2. Task-design mismatch

The two datasets may share surface stage names but differ in cognitive demands, timing, stimulus operations, or response structure.

3. Brain-state extraction mismatch

The current native image-space grid may be too crude or unstable across datasets.

4. Dataset/scanner/preprocessing shift

Differences in scanner, acquisition, preprocessing state, subject population, or image geometry may dominate the learned transition structure.

5. Genuine non-generalization

The CWP v1 representation may not describe a reusable cross-dataset brain-state transition primitive.

## Current Evidence Boundary

Supported:

```text
Within ds001635, CWP-style compositional labels improved E4/E5 OOD prediction.
```

Not supported:

```text
CWP v1 is a dataset-invariant cognitive primitive representation.
```

## Required v2 Audit Before Any New Positive Claim

A CWP v2 study must be separately frozen before reusing ds001634 information.

Minimum v2 changes to preregister:

- explicit cross-dataset ontology alignment rules
- neuroanatomical or template-space atlas decision
- confound/motion handling
- stage timing/HRF sensitivity plan
- dataset harmonization plan
- external validation dataset policy
- new final untouched holdout

## Manuscript Use

This failure should be reported as a result, not hidden as a limitation only.

Recommended framing:

```text
Local compositional advantage does not imply an externally reusable cognitive primitive.
```
