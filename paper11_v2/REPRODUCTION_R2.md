# R2 Reproduction and Access Boundaries

The prospective registration is `results/R2/registration.json`. It binds the
new evaluator, independent oracles, statistical/null helpers, tests and policy
before testing or real fitting. All earlier sources/evidence and P1-P11-v1
are protected by hashes. Current status/claim/operations files are explicitly
excluded from the historical-file lock so they can report this execution.

Default one-command PowerShell replay from the repository root:

```powershell
& ./paper11_v2/scripts/reproduce-r2-audit.ps1
```

Use `-Python <absolute-python.exe>` for an equivalent environment matching the
recorded Python/NumPy/SciPy versions. Default replay verifies every source and
saved artifact, reconstructs saved successful development and partial-null scores/objectives,
runs independent controlled tests, and never refits or opens an external holdout.
A zero replay exit is engineering reproducibility, NOT a scientific R2 PASS.
Read `results/R2/gate_result.json` for the actual scientific gate/verdict.

The original execution used `run_r2.py register` followed by `run_r2.py execute`.
The execution entrypoint rejects an existing execution-start marker or gate.
Do not delete these markers, overwrite results, or rerun failed candidates to
replace the original evidence. Any permitted future study/method amendment
needs a separately registered output namespace and must retain this attempt.

Input: only the 23 admitted R0 train/development count features and known task
event metadata, with frozen old-test ID exclusion. Counts are hippocampus-only;
unit identities are session-local. All transforms use training metadata only.
Every initialization result is saved before the next candidate. The first
required nonconverged/nonfinite candidate stops scientific evaluation globally.
No successful seed can replace a failed required initialization.

External data are not accessible through this runner. If development and all
registered nulls pass, independent recording-support/eligibility auditing and a
prospectively registered sealed accessor are required before external spikes.
The source-frozen 60/40 calibration/final split must remain unchanged. No final
metrics may select configurations, masks, seeds, hyperparameters or claims.

The registered primary metric is the full causal joint count log probability,
including count factorials, divided by unit bins. Patients are averaged equally
after equal-session aggregation. Development is previously exposed/exploratory.
Neither passing tests nor a predictive ranking proves physical neural regimes,
NAP, CWP or hippocampal primitives. R3 is outside this execution authorization.

This attempt is now STOPPED: scientific FAIL / DATA_INSUFFICIENT from external
observation-support auditing. Do not rerun scientific execution or extend nulls.
The saved-only audit has its own prospective source registration and receipt in
results/R2_saved_audit; it does not replace the original runner or failed gate.
Metadata support retries and their registration/transport failures are preserved
in separate result namespaces. The development report can be verified with
`python -B paper11_v2/scripts/r2_development_report.py verify`; verification
does not regenerate figures, select models or open external neural data.

Verified receipt:actual PowerShell exit0;59R2 tests PASS;6,783saved fit records
reconstructed, maximum score/objective discrepancy0;6,997original output hashes
checked. Prior51unique R0/R1 tests passed in separate new logs. Never interpret
this engineering receipt as clearing the six scientific/evidence warnings.
