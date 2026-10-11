# M4 Scientific Stop

Command: powershell -NoProfile -ExecutionPolicy Bypass -File paper11/scripts/reproduce-m4.ps1
Real run finished 2026-10-11T05:33:12.758954+00:00; exit 1.
Preceding scientific gates M0-M3 PASS. M4 FAIL / INCONCLUSIVE.

Smoke session sub-01/ses-01: all 32 required HMM seeds/configurations and eight
continuous d=1 seeds converged in the corrected run. Continuous d=1 training-best
seed71 could not satisfy the frozen marginal-likelihood numerical diagnostic.
Conservative single-run discrepancy: 64=0.009484312522032967,
256=0.0027676139728540633, 1024=0.0014080063396446991 nats/unit-bin.
Frozen threshold: 0.001. Reference uncertainty: 0.00010224930758077136.
Empirical repetition/reference checks are not an absolute-error proof.

Evidence: gate_result.json, qc_report.json, claim_audit.json, execution.log,
accuracy/sub-01_ses-01/continuous_k1_d1_seed71.json. Earlier failed serializer,
incorrect mean-estimator diagnostic and interrupted partial fits are retained
under attempts; none establishes the corrected single-run gate PASS. The 43
retained model artifacts include interrupted prior-run artifacts, not 43
completed corrected-run candidates. Hybrid fitting and full cohort unexecuted.

The run captured eight tests before two additional regression cases were added.
The gate test hash predates the final fixture revision. Historical tests.txt
does not certify the current ten-test file. Fresh final regression-tests.txt
in ops evidence runs all ten M4 and 60 M0-M3 tests: 70/70 PASS, zero skips.
Model/runner/reproduction hashes unchanged; current tests separately identified.
The nonzero-loading quadrature fixture was increased from 100000 to 1000000
particles after deterministic Monte Carlo discrepancy 0.004903973517237592
exceeded its unchanged 0.004 assertion. This increases test-fixture precision,
not real-data budgets, and is not experimental evidence.

No final test timestamps decoded. Frozen protocol, splits, grids and tolerance
unchanged. M5-M7 blocked. No preferred regime, null result or NAP/CWP validation.

Valid next options: retain this inconclusive technical-stop report, or register
a prospective numerical-method amendment (e.g. better proposal or larger audited
budget), record development-data exposure, and rerun all required candidates
and accuracy checks with matched policy before unlocking any final holdout.
Do not relax the threshold or select only successful seeds to claim success.
