# P11 M1 Requirement Baseline

Mission: paper11-m1. Baseline revision 1 frozen before implementation, 2026-10-10.
User source: Continue Paper 11; execute ONLY next incomplete milestone.
Prechange HEAD: d30170810a8498137b6d84b66a5b1ea7694496ae. Clean working tree.
M0 gate PASS independently verified with all 16 frozen SHA256 inputs unchanged.
Remote preflight: origin/test matches HEAD; origin/main absent. No branch repair.
Repository foundation/engineer/review templates absent; explicit user governs.

## Product Decision

Actor: researcher performing the next auditable dataset eligibility step.
Outcome: real progressively acquired primary spike data with anatomical/QC
eligibility, companion alignment, provenance and immutable metadata trial splits.
Flow: fixed repository trees -> pilot session metadata -> all session metadata
-> immutable 60/20/20 manifests -> session-by-session spike acquisition ->
training-only unit QC -> subject/session coverage -> tests -> M1 gate -> stop.
No binning, feature extraction, baseline fitting, model fitting, or external
scientific testing. No change to M0 protocol/lock or Papers 1-10.

Metadata validity: unique positive trial identity; artifact=0; set size 4/6/8;
finite nonnegative response time; fixation/encoding/maintenance/probe events
verify [-6,-5,-3,0] s with [1,2,3] s preprobe coverage. Correctness is retained,
not used to exclude incorrect trials. Match codes 1/2 mean IN/OUT. Validate
every present companion trial for set size, probe, response time, match,
correctness and artifact. Missing companion is explicitly UNPAIRED, not a
fabricated successful alignment and not alone an exclusion from spike analysis.
Unknown or conflicting anatomical labels stay outside the hippocampal primary.
Unit IDs scoped to subject/session. Unit eligibility uses training epoch spikes
>=20, full source trial-array coverage, finite coordinates and explicit label.
No total session spike-count field or validation/test counts influence selection.
Raw downloaded bytes include heldout rows but heldout timestamps are not parsed
or scored. The metadata trial identity column may be read only to exclude them.
Source's SU/MU uncertainty remains explicit; sorted units are not all called SUA.
No open material decisions. Frozen M0 thresholds apply without alteration.

| ID | Requirement | Verification | Status |
| --- | --- | --- | --- |
| REQ-001 | M0 PASS prerequisite; M1 only; preserve frozen inputs and P1-P10 | M0 verify and Git diff | VERIFIED |
| REQ-002 | Progressive real acquisition from pinned source commits | Per-file Git blob/SHA256 checks and progress receipts | VERIFIED |
| REQ-003 | Audit explicit hippocampus vs other MTL and session-local unit IDs | Real unit/electrode records and parser tests | VERIFIED |
| REQ-004 | Verify trial alignment and metadata QC without pooling iEEG | Session/trial audits and negative tests | VERIFIED |
| REQ-005 | Freeze real split manifests before train-only spike QC | Immutable locks, checksums and heldout-isolation tests | VERIFIED |
| REQ-006 | Report eligible coverage and DATA_INSUFFICIENT if thresholds fail | Subject/session/unit QC and gate tests | VERIFIED |
| REQ-007 | Executable code, real outputs, tests, QC, gate, claims, status and PowerShell reproduction | Real complete M1 run | VERIFIED |
| REQ-008 | Scoped review, closure evidence and origin/test upload | Exact staging, final source identity and remote match | IMPLEMENTED_UNVERIFIED |

baseline_requirement_count: 8
Test level: focused parser, provenance, split immutability and heldout-isolation
regressions plus real offline replay of complete acquired data. No UI/channels.
Gate: all required source/parse/alignment/integrity checks and tests pass AND
>=6 subjects each with >=1 eligible session (>=40 valid trials, >=5 eligible
hippocampal units). Otherwise FAIL or DATA_INSUFFICIENT; do not enter M2.
No scientific regime preference or NAP/CWP validation can follow from M1 PASS.
