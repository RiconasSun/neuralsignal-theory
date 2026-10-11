# Paper 4 Frozen Protocol v1

Title: Falsifying Noise Explanations for Reproducible Brain-State Transitions

Paper type: Method Paper / falsification and robustness study

## Core Question

Do the reproducible stage-transition vectors from Paper 3 survive plausible nuisance, timing, synthetic noise, and label-shuffle explanations?

## Experiment Chain

```text
E1 Input + measured-confound audit
E1b Online OpenNeuro derivatives/confound recovery audit, when recovery manifests are present
E2 Reproduce Paper 3 transition contrast
E3 Proxy nuisance-only prediction
E4 Nuisance residualization sensitivity
E5 Synthetic noise injection
E6 Timing / trial-position alternatives
E7 Label-shuffle falsification null
E8 Claim audit + paper package
```

## Primary Claim Boundary

Allowed only if supported:

```text
The transition contrast is not fully explained by the tested proxy nuisance and timing alternatives.
```

Disallowed:

```text
Noise has been eliminated.
Measured motion and physiology are fully excluded when confounds.tsv files are absent.
CWP is validated.
```
