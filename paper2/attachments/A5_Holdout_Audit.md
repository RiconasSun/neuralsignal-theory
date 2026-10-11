# A5 Holdout Audit

Status: Dataset C final holdout evaluated once under current v2 candidate rules.

## Holdout Roles

Dataset A ds001635:

```text
source / development domain
```

Dataset B ds001634:

```text
failure-analysis dataset
not a clean final holdout
```

Dataset C:

```text
OpenNeuro ds004469 v1.1.3
locked never-seen final external holdout
metadata/events audited first
final BOLD/state extraction completed after v2 candidate freeze
final performance evaluated once in the current run
```

## Isolation Policy

Dataset C final performance must not be inspected before:

```text
v2 ontology frozen
v2 preprocessing frozen
v2 state representation frozen
model family frozen
metrics frozen
success/failure gates frozen
```

## Access Log

```text
2026-09-01: Web/source audit identified ds004469 v1.1.3 as a Sternberg working-memory fMRI dataset with encoding, retention, and retrieval/test phases.
2026-09-01: Metadata-only OpenNeuro download completed for README, dataset_description.json, participants.tsv/json, events.tsv, and BOLD JSON sidecars.
2026-09-01: Local metadata audit generated paper2/external_holdout/dataset_c_metadata_audit.json and paper2/external_holdout/dataset_c_event_inventory.csv.
2026-09-01: Dataset C task-sternberg BOLD NIfTI files were downloaded after Dataset C lock.
2026-09-01: Dataset C standardized event files were generated with Coding -> ENCODE, Retention -> MAINTAIN, Test -> PROBE.
2026-09-01: Dataset C E1 extracted 2,268 stage states and 1,512 transitions.
2026-09-01: E9.7 final Dataset C comparison was run once with M2_strong_task, CWP v1, CWP_v2_medium, and RandomOntology.
```

## Current Holdout Risk

Dataset B cannot be used as clean external replication evidence because its failure was already observed in Paper 1.

Dataset C can test stage-level transfer only:

```text
ENCODE / MAINTAIN / PROBE
```

It cannot test:

```text
TRANSFORM
```

## Dataset C Final Comparison

The final Dataset C comparison included:

```text
M2 StrongTask
CWP v1
CWP v2
Random/PseudoOntology
```

Current result:

```text
CWP_v2_medium beat RandomOntology but did not beat M2_strong_task.
CWP-specific Dataset C success criterion failed.
```

The CWP-specific claim is allowed only if CWP v2 beats both StrongTask and Random/PseudoOntology. That condition was not met.
