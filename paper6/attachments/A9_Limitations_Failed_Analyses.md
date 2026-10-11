# A9. Limitations And Failed Analyses

Current limitations:

```text
Full available ds004117 E3-E6 analysis has been completed, and ds004752 external convergent stage specificity has been run.
No direct cross-dataset transition-boundary replication has been attempted.
The current feature family is log bandpower delta only.
Phase-randomized bandpower specificity remains high, so the current result is not phase-specific.
No iEEG or MEG mechanistic extension has been run.
No spike timing analysis has been run.
No held-out-subject-only split has been run.
Event-timing-only and electrode/channel identity baselines remain unrun.
```

Current positive evidence:

```text
The full available ds004117 analysis found same-transition reproducibility above matched random windows and transition specificity above label-shuffle, random-window, and time-shift nulls.
The ds004752 external convergent analysis found encoding-vs-maintenance stage specificity above label-shuffle null under leave-one-subject-out evaluation.
```

Failed or cautionary result:

```text
The phase-randomized bandpower control remained high at 0.7047732696897375 accuracy. This prevents interpreting the current result as evidence for phase-specific neural dynamics.
```

Forbidden current claims:

```text
NAP exists under macro transitions.
CWP maps to NAP.
Fast neural dynamics are universal primitives.
P6 is complete.
```
