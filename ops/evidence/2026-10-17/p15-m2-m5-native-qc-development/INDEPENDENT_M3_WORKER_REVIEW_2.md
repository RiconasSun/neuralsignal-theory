# Independent internal M3 worker review 2

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Base: `30cb925f505d63ae52bb1461d9ab153a52f1888e`. Review date: 2026-10-18 UTC.

Decision: **ACCEPTED_WORKER_COMPONENT_FOR_PRODUCTION_GATE_CONSOLIDATION_ONLY**. Open worker P0: 0. Open worker P1: 0. Both r1 worker findings are resolved before any real fitting. R1 remains unchanged unsuccessful evidence. This report alone does not approve real fitting or certify mathematical sources, B/E release, model selection or Final access.

## R1 finding closure

P1-01: dynamic execution now reads every expected baseline journal, requires completed statuses and exact registered configuration/current production-gate identity, and verifies each journal against the baseline marker's recorded hash. `baseline_availability` requires the complete full-cohort record set and establishes global B0/B1/B4 numerical availability. The required baseline gate is checked before any dynamic model construction or optimizer invocation. Missing/STARTED/stale/failed required full-cohort evidence cannot be replaced by mere marker existence or a favorable mouse subset.

P1-02: `claim_attempt` creates the STARTED journal with exclusive `open('x')`, flushes it and fsyncs it before optimization. A competing invocation or preserved crash residue cannot claim that attempt again. Existing STARTED journals are rejected; completed receipts can be skipped only with identical configuration/gate identity. No retry, stale-lock recovery or extra start is introduced.

## Fresh independent checks

- Executed all **8 test_worker tests** using `paper15_dev/work/runtime/Scripts/python.exe -W error::ResourceWarning -m unittest paper15_dev.test_worker -v`: PASS, exit 0. These cover exact 61-start grid counts, complete-cohort availability, incomplete/STARTED baseline denial, concurrent/existing claims, STARTED replay refusal, configuration/gate mismatch, frozen A-derived C active coordinates and B0 zero/positive-target constrained MLE PG.
- Independently exercised the actual `execute('dynamic')` entry point against isolated synthetic files for five denied cases: no globally valid B1, no globally valid B4, missing baseline journal, STARTED baseline journal and stale attempt hash. Every case failed before feature loading/optimization; the substituted optimizer invocation counter stayed zero in every case. Synthetic fixtures used project-local disposable directories and did not alter real journals or gates.
- Verified unchanged A_FIT_PLAN.json SHA256 and its 610 fixed starts (61 each for the same ten admitted mice), maximum732 and max_retries0. Real fit journal count remained zero at review.
- Verified all ten preserved old preprocessing states and tensors against A_FEATURE_PREPARATION_ATTEMPT_1.json. Its SHA256 exactly equals the original preparation manifest hash recorded in worker r1. Also verified all ten new state/tensor hashes against the new preparation manifest, each state's current feature/training implementation hashes, and equality of old/new A-export/QC/task/cohort-freeze identities, selected units/UUIDs and trial IDs. No original state/tensor was overwritten. Hashing preserved/current derived A feature files did not decode real neural arrays.
- The new preparation explicitly records feature and preparation code identities. The accepted mathematical review's `training.build_model` function source hash remains exactly `a40e8e29dda5df3e365d37fe3270dc0c8793c81f08b1541b3cbd9839f28bf0b6`; worker-only changes did not modify that helper.

The separate canonical-edge implementation repair and feature regeneration are documented prospectively before fitting. Historical feature states remain invalid for fitting and retained as evidence. This is implementation correction under the frozen half-open mathematics, not a new fit, neural-source reread, model substitution or scientific-policy amendment.

## Exact worker/preservation identities

| File | SHA256 |
|---|---|
| paper15_dev/training.py | 1c11098672df8d24c54770375c6c0c8db351622d533badf30bc11170dba0212d |
| paper15_dev/test_worker.py | 75aa02a9a07713208ae52b610e227ae7d2e1f166ff4999bb4ab02e2420012ca1 |
| paper15_dev/A_FIT_PLAN.json (unchanged) | 2a6af8f763950ef4136b291010d43e29e5360ebb6e6a628032ba75410c15e868 |
| paper15_dev/features.py | 30d17b3a902429537e8b83fc9ac5a483933bdb8080ff890c5f43c6fc5f4dd3fd |
| paper15_dev/results/A_FEATURE_PREPARATION_ATTEMPT_1.json | ca1f165bcb75369bc55db8bb89c2ae3efbc6d9053567b7aac7f48e554a196908 |
| paper15_dev/results/A_FEATURE_PREPARATION.json | cc28272cbd4adc5686fc2fc590e8d8ad9e1b71df86f5c757a834f1de460ebe05 |

## Separate consolidation dependency: numerical source identity

At this review point, INDEPENDENT_M3_NUMERICAL_REVIEW_2.md lists models.py `30c46a98...` and independent_ad.py `919e8a82...`, while current actual bytes are respectively `e13d12d3986b42ba1691075804df7b2ec6a033dcfe20fac36e5b6ed8e359ba90` and `8c69998bd1d03004325fb24d39c4d33fb4be15966b8e30321248d13480521ec0`. These current byte hashes also appear in my worker r1. This is not newline normalization. I notified the parent to have the separately assigned numerical reviewer reconcile its reviewed surface/hashes before consolidation. Worker acceptance does not waive this identity gap or establish that the numerical review applies to different source bytes. Any subsequent resolution must be a separately preserved review/addendum; this report must not be retrospectively edited to conceal the observation.

The parent's full64-test result is additional evidence; this review directly ran the eight focused worker tests and five additional entry-point denial cases identified above, not all64. A complete source-bound production gate, accepted mathematical review for the exact current sources, and final-candidate hashes remain prerequisites before real fitting. No PRODUCTION_NUMERICAL_PASS is issued by this worker report alone.

No real fit, B/E neural export, Final access, raw neural cache read or source/network request was performed by this reviewer. Only this new review artifact was written.
