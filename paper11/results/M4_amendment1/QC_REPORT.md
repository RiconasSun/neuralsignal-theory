# M4-NUM-1: Numerical Gate Still Fails

Original results/M4 evidence preserved byte-for-byte, with exact registered
hash readback in numerical_audit.json. M0-M3 scientific gates/splits unchanged.
Amendment registered2026-10-11T05:49:07.575337+00:00 before revised evaluation;
development exposure disclosed. PowerShell real replay exit1, correct STOP.
Focused eight numerical tests and full84-test regression PASS, zero skips.

Smoke sub-01/ses-01:48 converged training seeds, including40 checksum-matched
original corrected-run seeds reused and8 fresh continuous d2 fits. All eight
required seeds considered for each reached configuration. Four exact HMM
configurations retained. Best training-objective seeds chosen under original
policy, not validation-favorable seeds. No grids or candidate seeds removed.

| Continuous configuration | Particles | Discrepancy nats/unit-bin | Outcome |
| --- | --- | --- | --- |
| d1 seed71 | 2048 | 0.0011293628177796713 | FAIL |
| d1 seed71 | 4096 | 0.0007312952775541941 | PASS |
| d1 seed71 | 8192 | 0.0004892881078053064 | PASS |
| d2 seed53 | 2048 | 0.004253642098821145 | FAIL |
| d2 seed53 | 4096 | 0.0034519195488160316 | FAIL |
| d2 seed53 | 8192 | 0.0016818397769194165 | FAIL |

Reference uncertainty:d1=0.00012125197950379633,d2=0.0003261110384436511.
Threshold0.001 unchanged. All budgets evaluated with8 independent runs;
reference16384/32768 with8 each. Single first-seed endpoint, not replicate mean.

Proposal quality: d2 at8192 minimum ESS/N0.00037743696386359786 (about3.09
effective particles at its worst observed bin), maximum weight0.5260625097699546.
At2048 its maximum weight0.9903073819410834. These indicate severe concentration,
not a neural-regime finding. No rate overflow recorded in tested candidate runs.
Single-run SD maximum at8192:0.0004121327243726155. Maximum absolute
replicate-mean/reference shift:0.0000975944144415708; this is not known absolute bias.
Likelihood log transformation has Jensen bias; larger-budget agreement cannot
prove its absence. Reference uncertainty is empirical, not simultaneous coverage.
Coupled seeds across budgets aid comparison; within-budget repetitions independent.

Instrumentation matches original scoring in numerical fixtures, including a
hybrid fixture independently reviewed. Observation-aware proposal would require
prior/proposal importance correction; not implemented or claimed effective.
Systematic resampling retained; no unverified antithetics/control variates.
Exact HMM and identical PLDS/Hybrid numerical policy preserve comparable target.
Hybrid real fitting not reached because mandatory d2 accuracy FAIL stopped it.

No full cohort, d3, Hybrid, M5-M7, null/statistics or holdout result. Final
holdout and external test not accessed. M4 remains INCONCLUSIVE. Do not infer
continuous rejection, discrete preference, NAP/CWP or neural primitives.
Future observation-guided importance proposals or stronger references would
need another registered amendment and oracle validation, not relaxed thresholds.

Outputs: numerical_diagnostics.csv/png/pdf, numerical_audit.json, accuracy/*,
sessions/*, cache_receipts.json, gate_result.json, claim_audit.json, tests.txt.
Cost: per-reference/per-budget wall times inside accuracy JSON; cached receipt
records historical training times separately from current cache-loading cost.
These historic times are not independently proven original CPU measurements.
