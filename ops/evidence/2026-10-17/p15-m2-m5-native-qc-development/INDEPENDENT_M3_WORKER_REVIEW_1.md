# Independent internal M3 worker review 1

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Base: `30cb925f505d63ae52bb1461d9ab153a52f1888e`. Review date: 2026-10-18 UTC.

Decision: **REPAIR_REQUIRED_BEFORE_REAL_FITTING**. Open P0: 0. Open P1: 2. This unsuccessful review must remain preserved. No actual fit, real neural cache, source HTTP, B/E neural data or Final data was accessed by this reviewer. Only this review artifact was added.

Scope is the A-only preparation/execution worker, fixed attempt plan, access/ledger behavior, configuration/solver policy and saved-state serialization. Independent production mathematics/gradient review is assigned separately; this report does not certify its results.

## P1-01: dynamic execution accepts an attempts marker instead of the required baseline gate

`training.execute('dynamic')` at line 103 checks only that BASELINE_ATTEMPTS_COMPLETE.json exists. The baseline branch writes this file regardless of whether a required B1 or B4 ridge is numerically valid across every admitted mouse. Therefore the implementation can enter dynamic real fitting after all B1 or all B4 candidates have already become globally unavailable. Frozen M1 NUMERICAL_SELECTION.md requires a candidate to pass every required start/mouse and requires STOP primary activation when no valid B1 or B4 candidate remains; Prompt3 additionally orders M3 baselines before M4.

Minimal repair: validate the exact expected complete baseline journals against the frozen subject/configuration/gate identities, establish at least one full-cohort numerically valid B1 lambda and one full-cohort valid B4 lambda (plus any other required baseline prerequisite), and deny dynamic attempts before that gate. Do not substitute a favorable subset of mice or infer scientific convergence from a marker or optimizer success. A numerical failure in an unused candidate can remain preserved without preventing availability of a different registered full-cohort candidate.

Required synthetic tests: absent/incomplete/stale baseline records; all B1 candidates unavailable; all B4 candidates unavailable; a candidate failing one mouse; valid required full-cohort candidates with other failed attempts retained. In every denied case a fake optimizer invocation counter must remain zero.

## P1-02: the attempt claim is not exclusive

At lines 112-122, new-attempt admission is `path.exists()` followed later by ordinary `dump(path, STARTED)`. `dump` writes with overwrite semantics. Two concurrent worker processes can both observe absence, both overwrite the same STARTED journal, and both launch the same registered fit. The resulting single journal can hide an extra start and exceed the frozen one-start/no-retry attempt budget. Sequential STARTED rejection does not prevent this race.

Minimal repair: obtain an exclusive durable attempt claim or a simple exclusive worker execution lock before any optimization. A crash must retain an interrupted claim that cannot be silently reused. Preserve existing completed/failed/interrupted receipts; do not introduce an automatic retry or stale-lock entitlement reset. This is a local bounded-attempt ledger fix, not a new cryptographic/security architecture.

Required synthetic tests: simultaneous/double claim launches at most one fake fit; a STARTED/interrupted attempt is rejected without changing its bytes; an existing completed record is skipped only with identical configuration/gate identity; mismatched configuration/gate is rejected; unexpected execution failure is retained and stops the current execution. These tests must not consume real model attempts.

## Reviewed contract-consistent surfaces

- A_FIT_PLAN.json has the exact ten admitted mice, 61 distinct configurations per mouse and 610 total starts, below the unchanged 732 main-Development ceiling; max_retries=0. Counts are B0=1, B1/B2/B3/B4=3 each, D=18, C=12, S=18. No real fit journals existed at inspection.
- Fixed grids and seeds agree with frozen numerical policy: ridge .01/.1/1; D K2/3 and S K3/4 each three seeds; C rank1/2 and tau .1/.25; B/C one start. Registered solver options are L-BFGS-B, maxiter2000, maxfun80000, maxls40, ftol1e-12, gtol1e-6.
- Preparation reads the sealed A export and original selected units, valid A trial IDs, A-only feature transforms and serialized scalers/active coordinates. The worker contains no B/E loader or Final-fitting branch. The four C states and their active coordinates are derived from A and reused by build_model, rather than recomputed for a later scoring partition.
- Preprocessing serializes selected unit UUIDs, trial IDs, nuisance/history/C scalers, active coordinates, warm-up/bin policy, source-task/QC/A-export identities and nominal scoring denominators. Actual numerical feature correctness and final-candidate freshness still require the independent production gate.
- Constrained B0 uses its registered closed-form stationary MLE, then objective/bounds/gradient checks. Other families use the frozen solver. Endpoints preserve original parameters for independent AD and all three FD scales, full and projected gradients, coefficients, bounds, objective, iterations/calls and termination status. Optimizer success alone is not used as the convergence gate; an exhausted solver status is invalid. This review does not replace the independent derivative certification.
- Sequential execution already refuses a STARTED attempt, preserves unexpected exceptions and checks configuration/production-gate identity when skipping completed receipts. The requested changes retain these behaviors and add the missing stage/exclusive-claim enforcement.

No direct training-worker regression suite was present at inspection. Source, feature and likelihood tests do not themselves exercise the two worker gates above. The narrow synthetic tests identified here are necessary before a real fitting gate can be accepted; they do not require a real fit or scientific policy change.

## Exact principal reviewed identities

| File | SHA256 |
|---|---|
| paper15_dev/training.py | 0d2520f4796772f5aece3119443a140a040430569141cec181819257679c0739 |
| paper15_dev/A_FIT_PLAN.json | 2a6af8f763950ef4136b291010d43e29e5360ebb6e6a628032ba75410c15e868 |
| paper15_dev/features.py | 30d17b3a902429537e8b83fc9ac5a483933bdb8080ff890c5f43c6fc5f4dd3fd |
| paper15_dev/models.py (interface context only) | e13d12d3986b42ba1691075804df7b2ec6a033dcfe20fac36e5b6ed8e359ba90 |
| paper15_dev/independent_ad.py (endpoint interface context) | 8c69998bd1d03004325fb24d39c4d33fb4be15966b8e30321248d13480521ec0 |
| paper15_dev/results/A_FEATURE_PREPARATION.json (serialization manifest only) | ca1f165bcb75369bc55db8bb89c2ae3efbc6d9053567b7aac7f48e554a196908 |

Do not execute real A fits until these worker P1 findings are repaired and reviewed and the separate complete production mathematical/numerical gate passes for the final frozen candidate. No B/E or Final access, extra starts or model-policy amendment is approved by this review.
