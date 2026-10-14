# Independent preliminary review — unsuccessful closeout candidate

Reviewer: independent stage_a_review agent. Read-only public files, no fits, gradient experiments, tests or protected exports.
Decision: NOT_READY, five P1 evidence/documentation defects; scientific failure itself is not a closeout defect.

1. Stale execution state: MILESTONE_STATUS.md still reports RUNNING. Saved smoke establishes completed STOP / FAIL / NUMERICAL_INCONCLUSIVE; archive original before correction.
2. Incomplete reconciliation: 61 attempted and completed, 59 converged, 2 nonconverged, 155 unexecuted, 0 evidenced interrupted fits. Continuous d2/.001/11: iteration1355, solver success, PG .0016052460119657442, terminal numerical check passed, convergence threshold failed. Continuous d4/.001/11: iteration2000, solver failure, PG .692604771056502, gradient error .00020676306270142608 >1e-5.
3. Original reproduction exceeds Stage A scope and cannot run as saved: missing final_manifest/root gate plus synthetic gradient experiments. Add separate saved-only audit runner; preserve original.
4. Endpoint vector limitation: worker.stop exits before fitted_states.npz is saved. Scalar diagnostics/history are preserved, endpoint parameter vector is not. Do not claim vector preservation; exact Stage B replay must verify identity.
5. Final closeout identity/review absent: require atomic disposition, claim audit, verified counts, immutable public hashes, saved-only replay, final independent review, exact staging, remote commit/readback and clean-tree proof.

Reviewer confirmed 61 per-fit JSON records exactly match summary rows, no duplicate identities, native exit2/no timeout/cleanup success/zero-capability proof. Source registration changes must be checked against preserved version snapshots rather than requiring all obsolete hashes to match current sources.
