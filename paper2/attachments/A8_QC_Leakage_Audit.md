# A8 QC and Leakage Audit

Status: current audit generated for A/B diagnostics and Dataset C final holdout.

## Required Checks

```text
subject leakage
run/session leakage
dataset leakage
feature normalization leakage
state-alignment leakage
ontology-selection leakage
Dataset C pre-freeze exposure
task-context descriptor leakage
label leakage
scanner/site confounding
batch effects
post-hoc metric selection
```

## Critical Rule

Dataset C performance must not influence v2 design.

## Current Findings

```text
Dataset B is explicitly marked failure-analysis, not final holdout.
Dataset C metadata/events were audited before final evaluation to verify eligibility and stage mapping.
Dataset C performance was inspected only after v2 candidate status was written.
Dataset C final result does not rescue CWP.
Any post-hoc v3 changes require a new clean holdout or must be labeled exploratory.
```
