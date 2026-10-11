# A3. Full Pipeline

Planned path:

```text
Dataset audit
-> event semantic validation
-> transition-window construction
-> electrophysiology preprocessing
-> fast-dynamics feature extraction
-> existence / specificity tests
-> null and falsification tests
-> cross-subject / cross-dataset replication
-> claim audit
```

Implemented now:

```text
E0 protocol freeze
E1 dataset audit
E2 event-semantics audit
E2 ds004117 transition-window manifest
E3 one-run ds004117 EEG signal extraction smoke
E3-E6 full available ds004117 cohort analysis
E7 ds004752 external convergent stage-specificity analysis
E8 claim audit with within-dataset-positive but no NAP/cross-dataset claims allowed
```

Current implemented E3-E6 path:

```text
ds004117 transition windows
-> EEG .set/.fdt download
-> EEG channel selection
-> 1-55 Hz filtering
-> 1-second pre/post transition windows
-> theta/alpha/beta/low-gamma log bandpower deltas
-> subject-batched full available cohort feature extraction
-> batch feature aggregation
-> same-transition odd/even reproducibility
-> leave-one-run-out transition specificity
-> subject-level accuracy bootstrap
-> label-shuffle null
-> random-window null
-> time-shift null
-> phase-randomized bandpower control
-> ds004752 external encoding-vs-maintenance LCMV derivative analysis
-> claim audit
```

Current full available ds004117 output:

```text
paper6/results/e3_e6_ds004117_full_cohort_batched_results.json
paper6/results/e7_ds004752_external_convergent_results.json
```

Remaining planned path:

```text
external dataset replication
-> genuinely phase-sensitive feature/null family
-> held-out subject split if required
-> final figures
-> submission-ready manuscript package
```
