# Bounded conditioning and optimizer study

Mission P12-M4-CONDITIONING-OPTIMIZER-1. BASE `36a4099d0d7473fd21e592f3f2f321a493c46e44`.

**Scientific outcome: OPTIMIZATION_INCONCLUSIVE**. Feasible endpoint candidates: []. Single CA1 Continuous dimension4/ridge.001/seed11/384-parameter Training-A configuration only. Original objective,offset,bounds[-8,8] and PG<=.001 unchanged. All historical M4 failures remain immutable.

## Prospective stages and identities

Stage1 baseline42 frozen before implementation/experiments. Stage1 source and independent admission precede1536 Hessian gradient probes,3base objectives,3independentAD checks and3saturation passes with0 optimization fits. Stage2 completeaudit/initial/S/source/options/budgets and15+3synthetic support frozen before any realtrial. Two pretrial evidence-integrity P1 issues were corrected with17+3+8regressions and renewed independent admission; original snapshots/failed review remain. Algorithms/options/initial/S/budgets stayed identical to registrationv1. No outcome-driven amendment or retries.

Data/runtime/original model/original finite-difference oracle/frozen offset state hashes are bound in each execution_registration and native/input_binding. All four phase inputs agree exactly. Original offset loader applies saved all-seed weights; no M2,M3 or offset refit. Same original failing endpoint hash2d61b04db53dfdcc1dd49c1131fa810b84a0b8725d8db87105cc3d8095e3876f initializes all3 candidates. S hash43b6d95bdbedbd685f1606b3b46a59f5f516e60a498d6a27b5e87282e1e3ce46. Each native phase records capabilities0, denied source/key/DACL/network/custodian-memory probes, process exit and cleanup. No validation/final scores or arrays.

Saved original2230 objective calls and2000 accepted states show monotone accepted objective but0 PG<=.001; minimumPG0.025069166. Complete scalar trajectories retained. Full coordinate gradients available only at3 audited saved vectors; no claim of every original coordinate trajectory.

## Conditioning diagnosis

| Block | Original endpoint PG | Max-PG coordinate | Gradient RMS |
|---|---:|---:|---:|
| recurrent | 0.223440064264 | 5 | 0.115219773941 |
| past_count | 0.692604771057 | 61 | 0.0987663644748 |
| context | 0.479575322097 | 179 | 0.116849351559 |
| readout | 0.00368368856564 | 301 | 0.00122233844287 |

Past-count input coordinate61 dominates original endpoint PG; context has larger RMS, so PG dominance is not exclusive causation. Local Hessian scales1e-7 and1e-8 estimate all384 columns. Relative infinity-norm disagreement7.60781970061e-07; chosen1e-7 Hessian minimum-2.0320584279,maximum630434.189399,20 negative and33 near-zero modes at cutoff0.00630434189399. Resolved absolute-spectrum condition estimate97490373.6053 excludes near-zero modes and is not a positive-definite condition number. Both spectra,diagonals,asymmetry and resolution cutoffs retained; finite precision/step sensitivity remains a limitation.

Endpoint hidden saturation: |h|>.95 fraction0.256180555556, |h|>.99 fraction0.0944791666667; minimum tanh derivative2.98556200007e-06,mean0.446802218239. Saturation is heterogeneous; these local observations do not prove a sole causal mechanism or global landscape property.

## Frozen coordinate map and policies

Scale formula prospectively fixed: S_i=clip(1/sqrt(max(abs(H_ii at1e-7),1e-6)),1e-4,1e4). theta=S*z, z=theta/S, gradient_z=S*gradient_theta; z bounds[-8/S,8/S]. Ridge remains.001*sum(physical theta^2)/2 and Poisson loss remains normalized by7200 trial-bins. No coordinate-specific penalty or objective normalization change. Synthetic chain-rule/box/inverse oracles plus real endpoint objective/gradient/roundtrip checks verify the map. Exact transformed boundary values are canonicalized to physical +/-8 to avoid outward one-ulp multiplication rounding; interior map remains affine. Floating roundtrip is checked<=1e-12,objective<=1e-10,transform gradient<=1e-5.

A: transformed L-BFGS-B, maxiter5000,maxfun10000,maxcor20,maxls40,ftol1e-14,gtol1e-10; hard10000 objective-gradient calls. B:300 projected Adam steps,beta1.9/beta2.999/eps1e-8, rates.01 for1..100,.003 for101..200,.001 for201..300, then same L-BFGS-B options withmaxfun9400; warm600 calls and totalhard10000. C:bound-constrainedtrust-constr with BFGS skip_update,min_curvature1e-8,init_scaleauto; maxiter1500,gtol1e-9,xtol1e-12,barrier_tol1e-10,initialradius1,penalty1,barrier.1/tolerance.1,sparseJacobian,AugmentedSystem,keep_feasible; hard4500 calls. Native wall cap43200sec perphase inherited; method call/iteration caps tighter. Totalhard24500calls. Exact settings in candidate_protocol.json. No replacement, restart or budget increase.

Official API references: [L-BFGS-B](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-lbfgsb.html), [trust-constr](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-trustconstr.html). Frozen locally installed SciPy1.17.1/NumPy2.4.6 and source/runtime hashes determine execution; no dependency upgrade. Trust-constr solver optimality is distinct from original physical PG, and solver success alone never passes.

## All three outcomes and independent verification

| Candidate | Objective | Original PG | AD PG | AD scaled error | Iterations / callback states | Calls | Feasible |
|---|---:|---:|---:|---:|---:|---:|---|
| A | 19.851813776031 | 0.199668366545 | 0.199668366617 | 1.06756353757e-10 | 5000 / 5000 | 5405 | False |
| B | 19.8504583399732 | 0.0561309919767 | 0.0561309919778 | 7.44101872133e-12 | 5000 / 5300 | 6074 | False |
| C | 19.8527112179799 | 0.0242056458474 | 0.0242056458356 | 4.7839200483e-11 | 1500 / 1500 | 1518 | False |

Totalactual optimization objective-gradient calls12997<=24500. Native endpoint checks separately perform3 production objectives,1 independentAD and29 historical-checker forward losses per candidate, as registered. Warm and callback re-evaluations are included in method call ledgers. Each candidate has complete termination_history.json,endpoint.json,progress checkpoints andnative receipts. L-BFGS-B callback states are accepted iterates; C records every trust-constr callback state and may repeat an unchanged point, so callback count is not a claim of successful trust proposals.

- A: solver_success=False, status=1, message=STOP: TOTAL NO. OF ITERATIONS REACHED LIMIT; finite=True, bounds=True, bound_hits=0, objectiveADerror=3.5527136788e-15, transformgradienterror=0, roundtrip=0; old14-coordinatefixed-FDerror=0.0122580872702,checkerpassed=False.
- B: solver_success=False, status=1, message=STOP: TOTAL NO. OF ITERATIONS REACHED LIMIT; finite=True, bounds=True, bound_hits=0, objectiveADerror=0, transformgradienterror=0, roundtrip=0; old14-coordinatefixed-FDerror=0.0630949096987,checkerpassed=False.
- C: solver_success=False, status=0, message=The maximum number of function evaluations is exceeded.; finite=True, bounds=True, bound_hits=0, objectiveADerror=7.1054273576e-15, transformgradienterror=0, roundtrip=0; old14-coordinatefixed-FDerror=0.0106045702326,checkerpassed=False.

Independent forward-mode AD reuses the separately reviewed dual-number objective, not production backpropagation. All384 endpoint coordinates are retained with analytical and AD derivatives. Same physical endpoint/objective for all comparisons. Feasibility requires full original physical PG AND AD PG<=.001, finite scores/parameters/derivatives, strict bounds, ADscaled<=1e-5,objectiveerror<=1e-10 andtransform checks. No favorable intermediate or best-objective state is substituted. Raised objective/solver errors retain attempted calls,actual exception andlastaccepted state,without retry.

Historical finite-difference checker is run unchanged at each new endpoint and reported separately. It may remain step-unstable and is not the standalone acceptance checker for this newly registered feasibility study. No M4 replacement checker is adopted. Original .0002067630627 checkerFAIL,PG.692604771056502 and all older M4 FAIL/INCONCLUSIVE evidence stayimmutable. Passing a new endpoint or optimizer success cannot retrospectively clear them.

## Limits and next boundary

One configuration/one original seed/one common continuation endpoint/three fixed methods, finite precision and local Hessian estimates. No validation,holdout,between-mouse,regime-selection or predictive claim. No proof that the most difficult global optimum was reached or that all future gradients are valid. No full216fit smoke or13mouse competition; no M2/M3/offset rerun,M5,nulls,M6,M7. Every failed candidate and unsuccessful admission remains; scientific failures are not disguised as engineering success.

**OPTIMIZATION_INCONCLUSIVE**: none of the three fixed endpoints satisfies the unchanged feasibility gate. No winning uniform optimizer policy is justified. All three budgets are closed; no fourth candidate, replacement or budget expansion was executed. Further optimization work requires separate authorization.

## Reproduction, evidence and closure

`powershell -NoProfile -ExecutionPolicy Bypass -File .\paper12_condition1\reproduce.ps1` (Python+NumPy/SciPy) verifies sealedpublic hashes,same inputs/initial/S,budgets,full endpointgradient vectors and saved PG/AD/domain/decision arithmetic,then17structural+3exactpolicysynthetic+8saved tests. It runs no new real fit,reads no neural/protected state arrays anddoes notrepeatliveisolation; fresh nativeproofs belong to the recorded phases. Full outcome CSV,conditioning diagnostics,call/callback/warm histories and staticfigures included.42-item baselineacceptance andindependent review/Gitreadback are separate gates. STOP after this study and archival closure.
