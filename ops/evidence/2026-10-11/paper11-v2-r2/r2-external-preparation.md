# R2-C External Preparation - Read-Only Assessment

Date: 2026-10-11. This is a preparation note, not an executed scientific gate.
No network, external neural timestamps/counts, old protected test values or
real-neural fits were accessed. Frozen fitting code was not changed.

## Evidence and Current Boundary

- Sources: `paper11_v2/protocol/protocol.json`, `protocol/r2_execution.json`,
  `results/R0_schema1/registration.json`, `results/R0_schema1/final_validation_lock.json`,
  `scripts/run_r0.py`, `scripts/run_r0_schema.py`, and `results/R0_final/LIMITATIONS.md`.
- Pinned external source: DANDI:000004 version 0.220126.1852; recognition only.
- Final split lock SHA-256:
  `27fad80c753cfdef00977d056b379da5210f1e0247efba803a4e098e593e93e3`.
- Local lock contains 52 candidate sessions/36 canonical patients; minimum five
  explicit hippocampal unit labels/session. All locked partitions are disjoint
  and calibration size is floor(0.6 * valid recognition trials).
- All 52 candidate sessions have `observation_support_metadata_present=false`
  and `observation_support_verified=false`. These are metadata candidates,
  not a demonstrated training-spike-adequate or observation-supported cohort.
- Nature source: https://www.nature.com/articles/s41597-020-0415-9.
  Local LIMITATIONS.md reports continuous acquisition and stable units. The
  parent also reports continuous raw acquisition/stability criteria from its
  browse. The article body/precise criteria were not independently reread here:
  no network was authorized, and no local article capture was located in the
  inspected study/evidence text. Do not invent exact thresholds or quotations.
  The historical limitation note predates the approved development amendment;
  its old development-stop statement is not the current R2 status.

## Earliest Obstacles and Their Classification

| Order | Requirement | Present evidence / gap | Classification |
| --- | --- | --- | --- |
| 1 | Valid completed development/statistics/null gates and frozen selection before any external spikes | Parent owns execution and final manifest; this note does not certify their completion | PREREQUISITE_NOT_CERTIFIED_HERE |
| 2 | Independent observation support for every scored bin, without spike-derived support | No unit obs_intervals; general continuous acquisition/stability statements are not an asset/unit/time mapping or independent dropout audit | COVERAGE_UNRESOLVED, not established failure |
| 3 | Calibration-only access under the pinned split | Existing R0 accessor only permits anatomy/trial metadata and explicitly forbids spike_times/spike_times_index; it cannot serve as a calibration accessor unchanged | SOFTWARE_TO_IMPLEMENT |
| 4 | Prevent premature final values during continuous/ragged-unit decoding | Local metadata does not establish a safe partial timestamp retrieval method; decoding an entire unit spike vector then filtering to calibration would already expose final timestamps | ACCESS_FEASIBILITY_UNRESOLVED; enforce before physiological decoding |
| 5 | One-shot final accessor with durable ledger and frozen masks/parameters | Dedicated accessor/transition enforcement must be prospectively registered and tested | SOFTWARE_TO_IMPLEMENT, not scientifically failed gate |

Coverage can be supported by explicit independently documented recording
intervals, gaps and unit observation support mapped to each pinned asset and
its frozen trial epochs, or by sufficiently specific source documentation
establishing continuous support for those exact epochs/units. An absence of
obs_intervals alone does not prove inadequate data. Conversely, first/last
spikes, apparent firing, trial stimulus stop, upstream stability selection,
and zero-filled unknown intervals cannot establish support. Keep coverage
unresolved until the independent mapping is available. If a completed audit
cannot establish mandatory support, apply DATA_INSUFFICIENT and preserve all
remaining requirements as not executed; do not predeclare that result now.

## Prospective Access Contract for the Parent

1. Verify original source/artifact/split hashes and complete development gates.
   Freeze selected family/ridge/size/lags, strongest baseline, shared combined
   offset configuration, context rules, scoring, null rules and seeds before
   any external physiological access. Never substitute a weaker comparator.
2. Bind a metadata-only support manifest to asset ID, published digest, site,
   canonical patient, session, unit IDs/hemisphere, recording-clock basis and
   every locked [stimulus onset, onset+1s) epoch. Do not read acquisition signal
   values or use final activity to decide coverage or eligibility.
3. Register a calibration accessor with an explicit permitted decode/transport
   boundary. Whole-unit decode followed by time filtering is insufficient.
   Establish whether bounded per-epoch retrieval is possible or a genuinely
   sealed export service is needed. Buffered undecoded neighboring bytes and
   decoded final timestamps are distinct exposures; log both accurately.
   Published whole-file SHA-256 is provenance, not a verified local checksum
   unless independently checked against the complete file.
4. Use only frozen calibration rows for the >=20-spikes/unit mask, context
   transforms, constant-column mask, trial-position endpoints and session-local
   fitting. Require >=5 hippocampal units/session and >=8 independent patients.
   Preserve repeated-session grouping; no score/rate-driven final pruning or
   adjustment of floor60/40. Unit/cohort failure is retained, not silently pruned
   to find a passing cohort; the parent must apply the frozen STOP policy.
5. External context is recognition elapsed/event context, not verbal-WM load or
   maintenance. Retain T=10, 100ms half-open bins, score-before-assimilate and
   trial resets. Fit local parameters under all frozen seeds/budgets; resolve
   seeds by training objective only. Recompute causal history after nulls;
   external circular offsets are 5..9 and streams remain partition-local.
6. Before final access, persist all masks, parameters/seeds, feature schemas,
   support/split hashes and transition receipts. Reject missing prerequisites,
   wrong identities, changed masks and repeated final calls. Record an attempted
   access before decoding, including crashes; recover from sealed saved outputs
   without a second final-data access. Apply subject-only paired statistics and
   separate external Holm-six correction, without final selection or tuning.

Implement and prospectively register synthetic guard tests for denial before
unlock, calibration/final separation, no full-vector decode/filter shortcut,
identity/mask mismatch, duplicate final access, crash recovery, train-only QC
and exact frozen split preservation. They establish software safeguards;
independent support and later real external execution establish different facts.

## Regression Receipt

`prior-regression.log`: 33 unique R0 cases, including four audit-repair cases,
and 17 non-optimizer R1 cases passed; exit0. 3023 registered paths checked
before/after with zero mismatches; 12 archive manifests unchanged.
`prior-regression-supplement.log`: the separately authorized existing synthetic
GLM optimizer regression passed (one unique case, exit0); five historical
source/test hashes unchanged. Together: R0 33/33 and R1-CODE-1 18/18 unique
controlled cases across the two receipts. This is not a real-neural fit or
scientific R2-C success. The completed original log was not overwritten.

Parent retains current fit monitoring and saved replay. This sidecar does not
run those actions, replace frozen fitting code, implement an accessor or claim
that an unimplemented accessor is a failed scientific gate.
