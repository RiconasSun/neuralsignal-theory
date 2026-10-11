# A7. Null / Falsification Tests

Planned:

```text
label shuffle
matched random windows
fixed trial-position baseline
motion-only model
respiration-only model
cardiac-only model
physiology circular shift
phase-shifted physiology null
boundary jitter
time-bin residualization
```

Current result:

```text
PARTIAL MEASURED-NUISANCE FALSIFICATION RUN
```

Completed:

```text
motion residualization
respiration residualization
cardiac/pulse residualization
combined motion + respiration + cardiac/pulse residualization
label-shuffle null for primary contrast
label-shuffle null for secondary classification
domain-preserving label-shuffle null for secondary classification
pseudo-ontology contrast null
metadata-only classifier diagnostic
ds005795 measured-physiology/metadata nuisance ladder over all complete task-learning subjects
```

Not completed in current smoke:

```text
matched random windows
fixed trial-position baseline
physiology circular shift
phase-shifted physiology null
boundary jitter
time-bin residualization
```

Claim consequence:

```text
Because the N0 raw/basic gate failed, P8 cannot claim survival against measured nuisance or full falsification success.
```

ds005795 extension consequence:

```text
The extension reinforces that measured physiology is a meaningful competing explanatory signal for fMRI prediction. It does not establish that the preregistered transition-reproducibility endpoint survives physiology controls.
```
