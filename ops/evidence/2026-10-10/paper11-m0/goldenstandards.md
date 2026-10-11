# P11 M0 Requirement Baseline

Mission: paper11-m0. Mode: ENGINEER_MODE after protocol planning.
Approved source: user's P11 Hippocampal Dynamical Regime directive; M0 only.
Baseline frozen before implementation: 2026-10-10, revision 1.
Prechange HEAD: d1ff39d028815b15bbad84b9ed6fd6d896eab0cf.
Prechange working tree: clean. No paper11 directory or prior gates exist.
Prior gates required: none. Next milestone: M0, never M1 in this execution.
Remote preflight: origin/test equals prechange HEAD; origin/main ref absent.
No main integration applicable. Repo ops foundation/engineer/review templates
are absent; user directive and this explicit contract govern this mission.

## Product Decision

Actor: scientific reader and future milestone runner.
Outcome: immutable, testable P11 scientific contract without experimental claims.
Flow: fetch pinned metadata -> freeze protocol/environment/source digests ->
verify exact frozen artifacts -> run automated tests -> QC -> M0 gate -> stop.
Preserve: all P1-P10 bytes and existing published artifacts; no raw data acquired.
Boundary: metadata retrieval belongs to M0; anatomy/trial/unit eligibility is M1.
Missing experimental eligibility is unassessed, not evidence of insufficiency.
No heldout trials are assigned until M1 metadata inventory; the algorithm and
primary dataset participant roster are frozen now, never tuned from spike data.
Open material decisions: 0.

| ID | Requirement | Verification | Status |
| --- | --- | --- | --- |
| REQ-001 | Execute only M0 and preserve Papers 1-10 | Git tree/blob comparison and milestone sequence audit | VERIFIED |
| REQ-002 | Freeze protocol, metric, splits, model budgets, nulls and claim boundaries | Protocol validator and regression tests | VERIFIED |
| REQ-003 | Pin primary and external versions and capture real metadata provenance | Metadata receipts, immutable refs, SHA256 | VERIFIED |
| REQ-004 | Freeze repository and actual M0 environment | Environment and source lock verification | VERIFIED |
| REQ-005 | Supply executable code and verified PowerShell reproduction | Real runner and unittest invocation | VERIFIED |
| REQ-006 | Emit real output, automated tests, QC and gate_result.json | Report files tied to current source digests | VERIFIED |
| REQ-007 | Create milestone status and claim audit without scientific success | M0-only status, no fitted models, no regime verdict | VERIFIED |
| REQ-008 | Review and push exact mission files to origin/test | Review, exact staging and final remote hash | VERIFIED |

Test level: focused stdlib contract/integrity tests plus real metadata execution.
Oracle: pinned source metadata verifies; immutable source/protocol locks match;
P1-P10 unchanged; tests succeed; only M0 executed; no fabricated observations.
baseline_requirement_count: 8
No clinical channels, UI or model fitting applicable. Parser fixtures are labeled
as test fixtures and cannot become scientific results. No new dependencies.
