# A8. QC and Leakage Audit

Implemented:

```text
local HCP motion/physio file audit
remote HCP physio key-pattern audit
HCP WM Physio_log download / existing-file verification
run-level motion/physio/dtseries/EV matching
ds005795 public manifest audit
ds005795 complete task-learning four-file bundle check
ds005795 streaming BOLD deletion after each subject
secret-redaction guarantee
claim-boundary audit
```

Planned:

```text
physiology timing alignment QC
motion censoring QC
WM/CSF extraction QC
subject leakage audit
normalization leakage audit
final holdout access log
```

Current QC notes:

```text
No credential value is written to outputs.
The E0 audit records that credentials were used without exposing secret fields.
The measured-physiology ladder requires all matched run files before including a run.
The current ladder has 18 subjects, 36 runs, 288 block-start transition rows.
The ds005795 extension requires BOLD, physio.tsv.gz, events.tsv, and bold.json before including a subject.
The complete ds005795 task-learning subset has five subjects: sub-01 through sub-05.
No BOLD file is retained after streaming subject processing.
```
