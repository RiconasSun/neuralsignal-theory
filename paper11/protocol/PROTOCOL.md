# P11 M0 Frozen Protocol

P11 - Hippocampal Dynamical Regime. Explanation Paper.
Question: do human hippocampal population dynamics favor discrete, continuous,
or hybrid state-space models? P10's global comparison does not answer this.

The authoritative machine-readable specification is [protocol.json](protocol.json).
Its frozen digest and all M0 source/environment digests are in
[freeze.json](freeze.json). This text explains that unchanged specification;
it is not an amendment. No experimental results are reported at M0.

## Data and Provenance

- Primary sorted spikes: nm000363 v1.0.0, commit b054fbef57f9c4fb93477ecc5c88c6114dbc5662.
- Separate companion iEEG: ds004752 v1.0.1, commit 234fd4c04dea66ab9b0fd5ddbf4ec51f56b6ad02.
- Conditional external convergent test: DANDI 000004 release 0.220126.1852.
- [Real source receipts](../data_manifest/source_receipts.json) record URLs,
  retrieval timestamps, HTTP status, byte sizes and SHA256 of pinned metadata.

The metadata roster contains nine spike-dataset participants and fifteen
companion-dataset participants. These are not eligible hippocampal counts.
NEMAR's pinned README describes hippocampus, entorhinal cortex and amygdala;
unit type is not consistently distinguished as SU versus MU. It also documents
unpaired sub-08/ses-05 and sessions without units. M1 must independently audit
anatomy, trial alignment, spike quality and eligible coverage before proceeding.
Do not merge non-hippocampal labels into the primary cohort. Record hemisphere.
Do not assume persistent neuron identity across sessions.

## Eligibility and Features

Confirmatory comparison requires six eligible subjects. An eligible session
requires at least forty metadata-valid trials and five explicitly hippocampal
units passing training-only QC, including twenty training-window spikes each.
These are prospectively chosen design thresholds, not observations or a power
calculation. A failure leads to DATA_INSUFFICIENT, not a forced comparison.

Primary bins: 100 ms, left closed/right open, in [-6, 0) seconds relative to
probe. Trial resets prevent cross-trial history/filter leakage. Training-only
feasibility review precedes M2; 50/200 ms are sensitivity analyses. Any amendment
must be versioned before affected test access, never selected from test scores.
Upstream session-wide spike sorting limits claims of entirely blind processing;
downstream train-only filtering does not remove this limitation.

## Evaluation and Scoring

Whole trials in chronological order: floor(60%) train, floor(20%) validation,
remainder test, separately per subject-session. M1 creates the real eligible
trial manifest from metadata; M0 freezes the algorithm, not fabricated trials.
No overlapping windows or history/filter carryover across trial partitions.

Primary endpoint: heldout one-step count predictive log-likelihood, nats per
observed unit-bin, predicting before assimilating the scored count. Integrate
latent uncertainty; neither smoothed reconstructions nor ELBOs are comparable
primary scores. All models use the same unit/bin/trial mask and causal covariates.
Session means are equally weighted within subject; subjects are equally weighted.

Outer leave-one-subject-out assesses transfer of regime/hyperparameter policy.
The target subject's emission parameters may be adapted using only its training
trials under that policy. This is neither neuron-identity transfer nor zero-shot
spike prediction. External anatomy/task audit must pass and its own independent
split must freeze before external spike inspection. Different tasks support
convergent evidence, not direct replication.

## Models, Controls and Statistics

Baseline ladder: stationary rates, causal history, task events, within-trial
timing, trial-position/session drift, and their combined Poisson GLM.
Discrete: Poisson HMM K=2/3/4/6. Continuous: Poisson latent dynamics d=1/2/3.
Hybrid: switching Poisson dynamics K=2/3 and d=1/2. Eight fixed initialization
seeds; max 500 iterations, tolerance 1e-5. Validation-only one-standard-error
selection prefers fewer free parameters. Report complexity frontiers, matched
complexity sensitivity, convergence and compute. Never silently drop a failed
family. Lock likelihood integration precision and seeds on validation.

Frozen nulls: firing-rate-preserving bin permutation, bounded 25/50/100/200 ms
spike jitter, within-trial circular time shifts, trial-position controls, and
duration-matched random segmentation. All operations stay within partitions;
refit the complete frozen pipeline. 1000 null replicates. No post-hoc jitter
scale selection. All negative results and failed fits remain visible.

Subject-level paired differences; 10000 paired subject bootstrap resamples,
95% intervals; paired sign-flip tests with disclosed symmetry assumptions;
Holm correction across three family comparisons plus three baseline comparisons,
and separate correction across null contrasts. Independent unit is subject,
never bin, unit or trial. Alpha 0.05. Minimum practical gain 0.01 nats/unit-bin.
The prospective winner must beat both alternatives and the strongest baseline,
with positive corrected statistical evidence and the locked reproducibility/
falsification criteria in protocol.json. Otherwise INCONCLUSIVE; insufficient
coverage yields DATA_INSUFFICIENT. External evidence is reported separately.

## Claim and Execution Boundaries

M0 PASS certifies metadata/protocol/environment engineering only. It does not
establish hippocampal eligibility, fit any model, validate NAP/CWP, or select a
scientific regime. Allowed eventual scientific verdicts: DISCRETE_PREFERRED,
CONTINUOUS_PREFERRED, HYBRID_PREFERRED, INCONCLUSIVE, DATA_INSUFFICIENT.
M1-M7 remain NOT_STARTED. See [M0 reproduction](../REPRODUCE_M0.md).
