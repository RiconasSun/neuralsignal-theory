# A5. Holdout Audit

Status:

```text
SMOKE HOLDOUT COMPLETE
```

Primary rule:

```text
statistics are subject-level; nuisance construction and thresholds must be frozen before any final subject or external holdout evaluation.
```

Current holdout:

```text
Leave-one-run-out across 36 HCP WM runs.
Each held-out group is one subject-run with 8 block-start samples.
```

Current limitation:

```text
This is not a final locked external holdout. It is an internal HCP measured-physiology smoke run.
```

Convergent extension holdout boundary:

```text
ds005795 was used as an external/convergent measured-physiology dataset, but not as direct replication of the HCP WM transition endpoint.
The manifest-audited complete task-learning subset contains five usable subjects: sub-01 through sub-05.
The streaming ladder was run over all five complete available learning subjects.
```

Claim consequence:

```text
The ds005795 extension supports a measured-physiology nuisance-relevance claim for global BOLD prediction. It does not provide a locked external replication of the HCP SameTransition > DifferentTransition result, because that HCP result failed at the raw gate.
```
