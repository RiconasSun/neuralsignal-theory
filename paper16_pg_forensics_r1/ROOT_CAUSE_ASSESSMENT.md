# Root-cause assessment

Verdict: **SOLVER_TERMINATION_POLICY_LIMITATION**.

High confidence in the immediate stopping mechanism and unchanged PG failure; limited confidence about the deeper numerical geometry. No confirmed implementation defect. Conditioning is a plausible contributor, not a measured condition number or established cause.

The frozen S02/C unit951800892 mouse733457989, lambda1, stopped at254 iterations/275 FG calls with f0.35200449304009157. Independent arithmetic on saved x/g/bounds reconfirms PG1.9827644454692775e-5>1e-5. The endpoint's3 above-threshold residuals are packed26 color*order (1.9827644454692775e-5), packed23 color*repeat (1.7541683403006318e-5), and packed28 own20-60ms history (1.4934496350774151e-5). All are interior. Coordinates3/4 are at-10 and their outward gradients correctly vanish; coordinate6 is near-10 but interior and remains unzeroed.

| Explanation | Supporting evidence | Contrary evidence / limits | Unknown |
|---|---|---|---|
| Relative-objective termination before mandatory PG convergence | Exact saved message; successTrue with scientific passFalse; last protocol-associated relative decrease5.4511950509095186e-14<=ftol1e-12; endpoint PG above both scientific1e-5 and gtol2e-6 | Small decrease is not itself a gradient certificate. Association outside checkpoints relies on static callback order. | Internal line-search/correction-pair state absent; whether a different prospective policy would converge is untested. |
| Analytic gradient/vector/PG defect | None demonstrated. Audit explicitly checks signs, packing, bounds, identity, fixed scales and accounting. | All3 saved AD checks pass; max scaled AD8.673617379884035e-16; fixed FD max1.4926393454572917e-11. Endpoint independent AD error4.163336342344337e-17 and fixed FD1.4036320716413509e-11 are far smaller than PG excess. | Checkpoints do not prove every mathematical code path; no new evaluation permitted. |
| Poor scaling / weak curvature / plateau |2 PSTH coefficients at-10, another near-10; unpenalized PSTH vs lambda1-penalized nuisance/history; long trajectory with small final decrease; saved A active non-PSTH scales span0.25..0.993870101058377. Checkpoint long-chord Rayleigh-like statistics differ substantially. | Scale range alone is modest. Chords span different points/directions and cannot estimate a local spectrum or condition number. Largest endpoint residuals are penalized interior features. No design/Hessian inspected. | Hessian spectrum, predictor correlations and L-BFGS curvature quality. A saved-only audit cannot determine these. |
| FD instability causing false PG failure | No support in saved data: PG uses analytic g, agrees with AD and fixed FD. | FD errors are about1e-11, while PG excess is about9.83e-6. No favorable step selected and no new derivative scan. | Behavior outside saved checkpoints not examined. |
| Broad optimizer budget exhaustion | None:254<1500,275<6000. | Other passed endpoints required up to759iterations/789calls. Failure is a different termination mode, not the longest run. | Remaining5518 outcomes are unavailable. |

Among952 accepted optimizer endpoints, every one terminated on the projected-gradient solver condition; maxPG1.9997389862705384e-6, median1.4774231426179981e-6, none above half the scientific threshold. There are72 prior C passes,48 S02 passes,10 S02/C passes. The failure is exceptional in termination mode in the observed prefix, but is not the most costly run: approximately90.02% of accepted fits used no more iterations/calls. The prefix is censored by STOP and includes repeated units/seeds/lambdas; no independent animal-level hypothesis test or predictive interpretation is made.

Saved initial/midpoint/endpoint f:0.45345841631764516 /0.352079719662344 /0.35200449304009157. Their PG:0.11610677520970106 /0.0019603935950026166 /1.9827644454692775e-5. Gradient-inf is not monotone near the end. Earlier accepted250's small raw gradient cannot retrospectively clear the frozen endpoint gate.

Unavailable evidence: FG parameter vectors/full gradients for all275 trials; local Hessian/design audit; compiled solver internal state and correction pairs; unattempted outcomes. We do not reconstruct missing values, infer a coding defect from failure, or claim a validated conditioning diagnosis.

Original scientific verdict remains **STOP_NUMERICAL_REQUIRED_GATE**. A completed forensic mission is not M3-M5, M6 or Final PASS.
