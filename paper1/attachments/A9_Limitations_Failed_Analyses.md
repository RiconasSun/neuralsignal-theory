# A9 Limitations & Failed Analyses

## Current Limitations

- Motion-only null requires confounds input.
- Boundary-jitter null requires event perturbation and E1 rerun.
- TRANSFORM is exploratory only and cannot support the primary claim.
- The current run uses a native image-space 216-ROI grid, not a neuroanatomical atlas.
- E2 stage separability was weak under subject holdout.
- E7 external validation failed for the CWP-only model against the strong task baseline.

## Earlier Failed Attempt

An earlier one-command run failed before data download:

```text
ERROR: no events files matched data_manifest\**\*events.tsv
```

Interpretation:

```text
This missing-data blocker was resolved by downloading real OpenNeuro data.
```

## Unsupported Claims

The current workspace does not support:

- CWP is validated.
- CWP clearly outperforms task labels.
- CWP replicates externally.
- TRANSFORM is a valid primary primitive.

## Supported Narrower Observation

The current workspace supports:

- Within ds001635, CWP-style labels outperformed the strong task baseline in E4 unseen-combination and E5 unseen-domain MSE.
