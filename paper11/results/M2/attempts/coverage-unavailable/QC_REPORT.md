# M2 QC and Scientific Stop

Execution status: NEED_ENV. Scientific gate: FAIL (observation coverage unverified).
No model-family verdict is assigned. This is not demonstrated missing neural
data and is not DATA_INSUFFICIENT: exact observation provenance is unavailable.

M0/M1 gates, source hashes, raw receipts, metadata lock and trial splits verified.
All 37 metadata trial rosters have exactly consecutive IDs 1..n. Smoke, two-subject
and full training-cohort extraction executed in order. Conditional training
features include 9 subjects, 23 sessions, 613 session-local units and 622 trials.
There are 1,005,120 conditional unit-bins and 292,615 training spikes, with
80.764386% zero-count bins. Counts exactly conserve M1 training preprobe spikes.
100ms retained without selecting a new sparsity threshold. No convergence claim.

Pinned converter blob 6b622721897ed40d61c89ed0d972621496a01eee records array
existence before reading spike content. Thus empty arrays can mean observed zeros.
It exports only a cardinality, however, and does not prove exactly one array for
every required unit/trial or exclude extraneous/duplicate arrays. The scientific
gate therefore cannot accept full exposure as independently verified.

The initial extraction-only PASS is preserved in
count_extraction_gate_before_coverage_review.json. It was not used to advance.
The coverage audit found 23 required original files absent; three original GIN
endpoints returned HTTP 403. Storage metadata and annex pointers do not supply an
equivalent inventory. Missing coverage cannot be replaced by assumed zeros.

Tests verify decimal boundaries, complete zeros in fixtures, opaque malformed
heldout rows, causal set-size availability, reset history, trial-ID gaps, hashes,
real shapes/count conservation and coverage inventory duplicate/missing/schema
rejection. Fixture arrays are tests only, not experimental observations.

No validation/test timestamps decoded. No iEEG pooling, model selection, model
fits, heldout statistics, null outcomes or external tests. SU/MU unresolved;
unit identities remain session-local; published sorting was session-wide.
Exposure follows the released trial convention; independent dropout masks absent.

Restore original checksum-matching NIX files in paper11/raw/NIX, run metadata-only
array-name/schema audit, then rerun M2. Do not modify frozen partitions. An
authoritative equivalent coverage inventory is a valid prospective alternative;
weakening exposure requirements or changing primary datasets is not.
