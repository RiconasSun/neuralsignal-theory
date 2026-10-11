# Dataset C Lock

Status: locked for Paper 2 final external holdout; final performance not evaluated.

## Locked Dataset

```text
OpenNeuro ds004469 v1.1.3
Dataset DOI: doi:10.18112/openneuro.ds004469.v1.1.3
Dataset name: Temporal Lobe Epilepsy - UNAM
License: CC0
```

## Lock Rationale

This dataset was selected because its Sternberg working-memory task exposes explicit stage timing that can be mapped to the frozen stage-level CWP ontology:

```text
Coding -> ENCODE
Retention -> MAINTAIN
Test -> PROBE
```

The external source article describes the task as a three-phase working-memory design with encoding, retention, and retrieval phases. The local metadata audit confirms that the downloaded OpenNeuro events use `Coding`, `Retention`, and `Test` events with durations of 4 s, 10 s, and 4 s respectively.

## Metadata Audit

Generated files:

```text
paper2/external_holdout/dataset_c_metadata_audit.json
paper2/external_holdout/dataset_c_event_inventory.csv
```

Current audited counts:

```text
participants.tsv rows: 74
task_fmri_vw included subjects: 62
Sternberg events files: 63
Sternberg BOLD sidecar JSON files: 63
Coding events: 756
Retention events: 756
Test events: 756
domain mapping: digit Sternberg task -> NUMBER
```

## Holdout Boundary

The following have not been performed:

```text
Dataset C BOLD NIfTI download for final evaluation
Dataset C state extraction
Dataset C model prediction
Dataset C CWP-vs-task-vs-random performance comparison
Dataset C post-hoc tuning
```

Therefore Dataset C remains clean for the final E9.7 performance test under the frozen P2 v2 rules.

## Scope Boundary

This dataset can test cross-dataset transfer of the stage-level ontology:

```text
ENCODE / MAINTAIN / PROBE
```

It cannot test the `TRANSFORM` primitive because the local metadata audit does not expose a manipulation phase.
