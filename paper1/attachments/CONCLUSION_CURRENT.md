# Current Conclusion

Date: 2026-09-01

## Conclusion Status

```text
COMPLETED_STRONG_CLAIM_NOT_SUPPORTED
```

## What Is Complete

The Paper 1 execution package is implemented and run for E0-E8:

- E0 Data/QC Audit
- E1 Brain-State Extraction
- E2 CWP Existence
- E3 Task vs CWP
- E4 Unseen Combination
- E5 Unseen Domain
- E6 Null/Falsification
- E7 External Dataset
- E8 Statistics + Reproduction

The Python environment is installed and frozen in `paper1/results/environment.lock`.

The code passed:

```text
compileall: PASS
synthetic E1-E8 smoke: PASS
```

The real local audit produced:

```text
paper1/data_manifest/dataset_manifest.csv
paper1/data_manifest/trial_counts.csv
paper1/data_manifest/qc_subjects.csv
paper1/data_manifest/e0_summary.json
```

E0 result:

```text
n_events = 48
n_roi_timeseries = 48
n_bold = 48
n_confounds = 0
external_stage_states_present = true
```

## Primary Run

E1 primary ds001635:

```text
states_extracted = 2291
roi_count = 216
```

E1 external ds001634:

```text
states_extracted = 3066
roi_count = 216
```

## Gate Result

```text
Gate A incremental: INCONCLUSIVE
Gate B OOD: PASSED
Gate C external: FAILED
claim_allowed_cwp_foundation_holds: false
claim_allowed_cwp_clearly_outperforms_task_labels: false
```

## Scientific Claim Allowed Now

Allowed:

```text
Within ds001635, CWP-style compositional labels improved OOD prediction in leave-one-combination and unseen-domain tests.
```

Not allowed:

```text
CWP has been validated.
CWP clearly outperforms task labels overall.
CWP externally replicates.
```

## Current Scientific Conclusion

The strong Paper 1 claim is not supported by the current run. The result is mixed: CWP-style representations helped on ds001635 OOD tests, but the primary incremental gate was inconclusive and external validation failed.

Paper 1 should therefore be positioned as:

```text
CWP-style compositional representations improve within-dataset out-of-distribution brain-state prediction, but do not yet generalize across independent datasets.
```

Core boundary:

```text
Local compositional advantage != general cognitive primitive
```

## Next Required Action

The next required scientific action is not to tune v1 against ds001634. It is to freeze a separate CWP v2 hypothesis before using the external failure to redesign ontology, alignment, preprocessing, or model structure.
