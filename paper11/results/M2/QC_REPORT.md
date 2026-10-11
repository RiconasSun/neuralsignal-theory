# M2 QC and Scientific Stop

Execution/scientific gate: PASS after public annex resolution and full coverage
replay. Earlier NEED_ENV/FAIL records remain in attempts/coverage-unavailable.
No model-family verdict is assigned. No DATA_INSUFFICIENT claim is made.

M0/M1 gates, source hashes, raw receipts, metadata lock and trial splits verified.
All 37 metadata trial rosters have exactly consecutive IDs 1..n. Smoke, two-subject
and full training-cohort extraction executed in order. Conditional training
features include 9 subjects, 23 sessions, 613 session-local units and 622 trials.
There are 1,005,120 conditional unit-bins and 292,615 training spikes, with
80.764386% zero-count bins. Counts exactly conserve M1 training preprobe spikes.
100ms retained without selecting a new sparsity threshold. No convergence claim.

Pinned converter blob 6b622721897ed40d61c89ed0d972621496a01eee records array
existence before reading spike content. Thus empty arrays can mean observed zeros.
Its cardinality alone does not prove exact coverage. Therefore all 23 selected
NEMAR NIX objects were progressively acquired (11,387,335,686 bytes) and verified
against their pinned annex SHA256. The metadata-only consumer verified exact
unit/trial membership, uniqueness, microwire identity and numeric seconds schema.
Pinned publisher provenance attests timestamp-attribute masking only, with no
data-array changes; original/masked identities are retained separately. There
was no independent comparison of original-versus-masked signal values.

The initial extraction-only PASS is preserved in
count_extraction_gate_before_coverage_review.json. It was not used to advance.
Initial coverage audit found 23 sources absent; both HEAD and bounded GET to
three original GIN endpoints returned HTTP 403. Annex remote logs subsequently
identified accessible public S3 objects. Initial failure was not used to advance.
Fresh complete coverage audit and count-extraction replay passed before M3.

Tests verify decimal boundaries, complete zeros in fixtures, opaque malformed
heldout rows, causal set-size availability, reset history, trial-ID gaps, hashes,
real shapes/count conservation and coverage inventory duplicate/missing/schema
rejection. Fixture arrays are tests only, not experimental observations.

At M2, no validation/test timestamps decoded, no iEEG pooling or model fitting.
Later M3 validation access is distinct from this training-only feasibility stage.
SU/MU unresolved;
unit identities remain session-local; published sorting was session-wide.
Exposure follows the released trial convention; independent dropout masks absent.

One-command reproduction supports -AcquireNix for checksum-bound public sources.
Full array coverage follows the released trial-window convention, not independent
proof of physiological dropout-free recording. Frozen partitions stay unchanged.
