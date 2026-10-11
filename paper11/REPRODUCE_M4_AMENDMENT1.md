# Controlled M4 Numerical Remediation

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File paper11/scripts/reproduce-m4-amendment1.ps1
```

Registers numerical_amendment1_lock.json before revised evaluation. Source,
spec and original M4 evidence hashes cannot change silently. Requires unchanged
M0-M3 PASS, selection/fitting contracts and frozen split. Final holdout stays
opaque. Original results/M4 remains unchanged; output in results/M4_amendment1.
Existing forty corrected-run smoke training seeds are reused only with exact
checksums and all seeds included; original training times retained in receipts.
Remaining grid/session seeds fit original unchanged code. No neuron identity
transfer across sessions. Same original progressive stages and mandatory grid.

Candidates2048/4096/8192, eight independent runs per budget; references16384/32768,
eight independent runs per budget. All budgets evaluated; select least passing
budget, first frozen run as endpoint. Do not choose favorable replica or report
replicate-mean error as single-run accuracy. Threshold unchanged0.001 nats/unit-bin.
Exact HMM needs no MC approximation; identical policy for all PLDS/Hybrid.
Record ESS, largest particle weight, overflows, resampling roundoff boundaries,
replicate variance, signed budget/reference shifts and computational wall times.
Empirical agreement is not a proof of absolute integration error/unbiased log score.

Proposal audit: bootstrap does not use current counts to guide latent proposals,
so sharp joint likelihoods may cause degeneracy. An observation-guided Gaussian
proposal would require exact prior/proposal importance correction for each
switching state; using a fitted posterior reconstruction would be invalid.
Antithetics/control variates require additional validation. Keep proven target
and systematic resampling, test larger budgets first rather than introducing
unverified likelihood bias. Observation-aware proposals are investigated as
alternatives, not claimed implemented or effective.

Any required training/accuracy failure produces FAIL/INCONCLUSIVE and exit1;
STOP before downstream execution. All results retained. No preferred neural
regime, null/holdout advantage, NAP/CWP or primitives claim follows from this gate.
Joint B2 requested previously is not added: authorization only amends M4 numerics.
