# Static implementation audit

Diagnostic verdict: SOLVER_TERMINATION_POLICY_LIMITATION. No demonstrated implementation defect in the audited failure path. This is not a proof that all unexecuted paths are defect free.

Every source below is frozen in SOURCE_PINS.json. The installed SciPy wrapper is additionally bound in RUNTIME_SOURCE_PIN.json. Inspection is textual; no optimizer or mathematical function was invoked.

| Component | Frozen behavior | Evidence and assessment |
|---|---|---|
| M1 NUMERICAL_POLICY.json | float64; L-BFGS-B maxiter1500,maxfun6000,maxls40,maxcor10,ftol1e-12,gtol2e-6 | Exact policy unchanged. Mandatory scientific outward PG<=1e-5 is a separate endpoint gate. |
| optim_child.py:run | Passes NUMERIC.options unchanged to minimize, jac=True, bounds; FG requests and callback ITER; preserves DONE success/message/nit/nfev | SciPy can terminate on either its objective or gradient condition. success=True does not imply scientific PG acceptance. |
| optimizer.py:Counter / fit | Reserve/count before FG; deny call6001 and iteration1501; counter/client nfev/nit identity; preserve accepted x and every completed FG objective/gradient-inf | Failed attempt has275 complete pairs and254 accepted vectors, no interrupted pair. No budget exhaustion. FG journal lacks x/full g, limiting independent identity at uncheckpointed steps. |
| optimizer.py:certificate | Initial, accepted127, endpoint; same x for analytic, independent AD, four fixed central FD scales | All111 saved coordinate comparisons verified arithmetically. Fixed acceptance FDh1e-5 was not selected after results. Central smooth extension outside bounds is explicitly permitted for derivative oracles. No new derivatives evaluated. |
| optimizer.py:fit endpoint | Compare saved endpoint analytic with DONE jac; objective checkpoint with DONE fun; independently evaluate outward PG; numerical_pass=PG<=1e-5 AND all checkpoints pass | Endpoint arrays/result/diagnostics agree. Writes RESULT, then NumericalStop/FAILURE on mandatory failure. The STOP is correct enforcement, not an implementation bug. |
| models.py:Objective | A-only scaler, model C columns0..37, drop inactive features, ascending packed order, PSTH bounds[-10,10], others[-1,1] | Saved A S02 active metadata recovers37 names. Original23 running_missing inactive; all12 PSTH retained. Packed26 is original27 color*order. No model/scaler or mathematics modification. |
| models.py + spec.py:glm | Mean scored-row Poisson NLL with exposure plus lambda/2 squared non-PSTH coefficients; analytic derivative includes matching ridge | C is a fixed causal history-feature GLM, not a fitted recurrent state model. Convex objective, but no uniform strong-convexity guarantee for unpenalized PSTH coordinates. No objective normalization/bound/penalty inconsistency demonstrated. |
| core.py | Verifies normative/reused source pins before scientific imports; supplies unchanged NUMERIC | New forensic driver does not import core/models/spec/dynamics or access their data. Reads static files and saved numerical certificates only. |
| spec.py:projected_gradient | Zero g only at lower with g>0 or upper with g<0, epsilon1e-12 | Independently implemented in audit.outward, sign/interior/epsilon/invalid-input regression tests. Endpoint has2 lower-active coordinates and35 interior; largest3 residuals interior. |
| installed SciPy1.16.3 _lbfgsb_py.py | ftol->factr=ftol/float64eps; gtol->pgtol; callback after NEW_X; task402 reports relative reduction and success | Source lines127-139,319-325,375-376,464-487 and saved message support the documented termination route. Native compiled internals were not instrumented or replayed. |

The relative-objective rule is (f_old-f_new)/max(1,abs(f_old),abs(f_new))<=ftol. The protocol-associated last accepted reduction is5.4511950509095186e-14, below1e-12, while endpoint PG is1.9827644454692775e-5. This demonstrates the mismatch between solver termination and scientific convergence. It does not establish why the quasi-Newton direction and line search reached this small reduction.

FG trial274 increased f relative to accepted253; trial275 was accepted. Treating every FG trial as accepted would be incorrect. Association of last FG per accepted-count group follows pinned SciPy callback/broker ordering and is cross-checked against saved initial/midpoint/endpoint objective and vector certificates. Other FG/vector identities remain protocol-derived because FG x is absent.

Accepted250 had saved raw gradient-inf8.880019404928358e-6, already below the scientific threshold but above solver gtol2e-6. The frozen policy certifies the termination endpoint plus three checkpoints; it did not permit retrospective selection of an earlier vector. No full independent certificate exists for250. It cannot replace the failed endpoint.

No source repair or numerical-policy amendment was made. The original no-retry STOP and all prior P12-P16 failures remain unchanged.
