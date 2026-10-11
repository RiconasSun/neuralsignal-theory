# A5 Holdout Audit

## Holdouts Implemented

E3:

```text
leave-one-subject-out
```

E4:

```text
leave-one Domain x Load x CWP cell out
```

E5:

```text
leave-one-domain-out
```

E7:

```text
train on ds001635 states, test on ds001634 external states
```

## Current Holdout Status

Real holdout evaluation has been completed for E3, E4, E5, and E7.

## Holdout Results

E3 Gate A:

```text
INCONCLUSIVE
```

E4 unseen combination:

```text
PASSED
```

E5 unseen domain:

```text
PASSED
```

E7 external validation:

```text
FAILED
```

## Access Log

Initial failed run:

```text
date: 2026-09-01
result: failed before E1 completion
error: no events files matched data_manifest\**\*events.tsv
```

Resolution:

```text
Downloaded ds001635 and ds001634 events/BOLD from OpenNeuro.
```

Final run:

```text
date: 2026-09-01
result: E0-E8 completed through claim audit
claim_allowed_cwp_foundation_holds: false
```

## Holdout Caveats

- E7 is a hard failure for the strong claim in the current run.
- E2 sanity check was weak, which makes downstream positive OOD results less interpretable.
- Motion confounds were not available, so the holdout audit is not yet motion-robust.
