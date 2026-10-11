# A1 Frozen Protocol

Paper: Reusable Cognitive Work Primitives Improve Out-of-Task Prediction of Human Brain-State Transitions

Status: frozen protocol implemented and run on downloaded OpenNeuro data.

## Research Question

Do reusable Cognitive Work Primitives (CWP) predict human brain-state transitions better than dataset-specific flat task labels, especially under out-of-distribution holdouts?

## Falsifiable Hypothesis

Primary:

```text
P(S_t+1 | S_t, CWP, Context) > P(S_t+1 | S_t, TaskLabel)
```

Operational gates:

```text
Gate A: M4_task_plus_cwp > M2_strong_task
Gate B: M3_cwp > M2_strong_task on unseen combination/domain
Gate C: external dataset direction is consistent
```

## Frozen Ontology

Primary CWP labels:

- ENCODE
- MAINTAIN
- PROBE

TRANSFORM remains exploratory and is not allowed to support the primary Paper 1 claim.

## Frozen Experiments

- E0 Data/QC Audit
- E1 Brain-State Extraction
- E2 CWP Existence
- E3 Task vs CWP
- E4 Unseen Combination
- E5 Unseen Domain
- E6 Null/Falsification
- E7 External Dataset
- E8 Statistics + Reproduction

## Frozen Models

- M0_state: `S_t+1 = F(S_t)`
- M1_flat_task: `S_t+1 = F(S_t, TaskID)`
- M2_strong_task: `S_t+1 = F(S_t, TaskID, Domain, Load)`
- M3_cwp: `S_t+1 = F(S_t, CWP, Domain, Load)`
- M4_task_plus_cwp: `S_t+1 = F(S_t, TaskID, CWP, Domain, Load)`

## Primary Endpoint

Held-out prediction error / predictive performance on brain-state transitions.

## Secondary Endpoints

- R2
- MSE
- cosine similarity
- subject-level effect size
- bootstrap 95% CI
- sign-flip permutation p-value
- FDR-adjusted q-value

## Current Execution State

Current real-data run:

```text
status: completed through E8 claim audit
Gate A incremental: INCONCLUSIVE
Gate B OOD: PASSED
Gate C external: FAILED
claim_allowed_cwp_foundation_holds: false
```

The strong Paper 1 claim is not supported by the current workspace state.
