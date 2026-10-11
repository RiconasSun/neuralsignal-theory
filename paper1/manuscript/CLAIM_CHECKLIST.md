# Claim Checklist

Date: 2026-09-01

## Allowed Claims

Claim:

```text
The E0-E8 pipeline ran through E8 on downloaded OpenNeuro data.
```

Evidence:

```text
paper1/results/claim_audit.json
paper1/attachments/RESULTS_CURRENT.md
```

Status: ALLOWED

Claim:

```text
Within ds001635, CWP-style labels improved OOD prediction in E4 and E5.
```

Evidence:

```text
paper1/results/primary_metrics.csv
paper1/attachments/RESULTS_CURRENT.md
```

Status: ALLOWED

Claim:

```text
The strong CWP foundation claim is not supported by the current run.
```

Evidence:

```text
paper1/results/claim_audit.json
```

Status: ALLOWED

## Disallowed Claims

Claim:

```text
CWP is validated.
```

Status: DISALLOWED

Reason:

```text
Gate A is inconclusive and Gate C failed.
```

Claim:

```text
CWP clearly outperforms task labels overall.
```

Status: DISALLOWED

Reason:

```text
claim_allowed_cwp_clearly_outperforms_task_labels is false.
```

Claim:

```text
CWP externally replicates.
```

Status: DISALLOWED

Reason:

```text
Gate C external validation failed.
```

Claim:

```text
The 216-ROI grid is a neuroanatomical atlas.
```

Status: DISALLOWED

Reason:

```text
The current representation is a native image-space grid.
```
