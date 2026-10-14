# Continuous recurrent Poisson gradient diagnosis

Mission `P12-M4-CONTINUOUS-GRADIENT-DIAG-1`. Independently reviewed Stage A BASE: `0e7ac4d816d2f006f7e394cfaa37a1d362679e5f` (parent `e635724f2aae45b7fdf30edb5902beaab425b8e2`).

**D4: FINITE_DIFFERENCE_INSTABILITY.** The analytical derivative is validated at all three registered vectors. The old fixed-step numerical check is unreliable at the endpoint. The optimizer also remains nonconvergent: explaining its numerical checker failure does not clear its projected-gradient failure.

## Exact reproduction and custody

One real fit only: Development Training A, mouse 744912849, session 766640955, CA1 / Continuous / dimension 4 / ridge 0.001 / seed 11. Native zero-capability AppContainer role proof passes source/key read denial, DACL regrant denial, network denial and custodian-memory denial. No validation scores or final values were supplied. Synthetic oracle executions are separately labeled.

The frozen L-BFGS-B options remain maxiter=2000, maxfun=80000, ftol=1e-10, gtol=1e-5; all 384 bounds remain [-8,8]. Architecture, seeds, ridge grid, shared frozen offset, allocation and downstream selection rules are unchanged. `execution_registration.json` binds the original mathematical sources, cached original checker, frozen offset states, A manifest and runtime before the single replay. `frozen_offset.fit_offset` loads and applies saved all-seed mean weights; its historical name does not imply a refit.

`results/diagnostic/native/reproduction.json` records exact equality for all ten scalar/checker fields, all objective-call history and all accepted-iteration history. Endpoint: 2000 iterations, 2230 objective calls, objective 19.87905908627809, PG 0.692604771056502, zero bound hits, solver iteration-limit failure. The original 14-coordinate check is reproduced unchanged: scaled error 0.00020676306270142608 > 1e-5. PG also exceeds the frozen 0.001 threshold. Both original gates remain FAIL.

Old early-stop evidence did not save theta. This replay recovered the endpoint vector; it is not described as an originally saved vector. Initial, intermediate (accepted array index 1000, iteration 1001) and endpoint vectors were prospectively defined, hashed and used identically by every derivative comparison. Complete 2000 accepted vectors stay in protected storage; public coordinate evidence contains only the three audited vectors and derivatives.

| Identity | SHA256 |
|---|---|
| A manifest | da90b8d8596c81721bc8aa91d40f7b8ee4a32e55064b9f649f1202055c272d2f |
| Target A file | 334c99b2ee66695c95315b7527328d01fc823d7727193bc8b59f25de847a5a5b |
| CA1 training array | aec99aeaf912cc8068b9d1ab34ac0bbd44c1861fc27e75ae1f09774ff983d852 |
| Context | 7800f597bb67bb5dcd808458ea7f0caf508f6b3263c62571eb2bccff1d541fce |
| Frozen offset | 6b458e5b18f241f3e2ce888fce06dab349ccca08f45c2b390b1e704cfc504225 |
| Recovered state bundle | c7533350096bb9d8c9a3faa7ee02dff22dba0f93c77b193a3db9dc703403208a |
| Complete 8064-row CSV | 7136f2fd6954ac1e0bc7209e410ef88892edb18c65632d684233e6546ce3a2c6 |

## Independent derivative examination

The independent implementation uses operator-level forward-mode dual numbers (matmul, tanh, exp, arithmetic and sums) in a separately written recurrent Poisson objective. It neither imports nor calls production backpropagation. Primitives, exact one-bin identities, dimensions 1/2/4, recurrence stress, ridge and projection have synthetic regression coverage. This is independent AD, not a finite-difference estimator. No external AD package was required.

All comparisons use the same full Poisson PMF objective plus ridge: negative log-likelihood divided by trials*bins = 7200, plus 0.001*sum(theta^2)/2. Unit count is not an extra normalization divisor. All fitted coefficients are penalized; independent ridge gradient is 0.001*theta and its measured decomposition error is zero. Blocks are recurrent 0:16, past counts 16:144, context 144:256, readout 256:384. There is no free dynamic intercept. The fixed task offset includes its frozen intercept contribution and the dynamic context excludes its first/intercept column. No intercept or offset parameter is introduced or refit. `block_summary.json` retains separate block errors; the full CSV retains every coordinate and ridge/likelihood decomposition.

The unconstrained derivative and projected gradient are separately reported. All three real audited vectors have zero bound hits. Registered symmetric probes use the smooth objective extension with bound-crossing flags; synthetic checks cover outward/inward bound projection. Every objective discrepancy is <=3.56e-15. Float64 and Windows longdouble both report 52 stored mantissa bits, so no extra-precision validation is claimed.

| Vector | Maximum analytic vs AD absolute/scaled error | Analytic PG | Independent AD PG |
|---|---:|---:|---:|
| Initial | 3.2959746043559335e-17 | 0.05885804464681279 | 0.058858044646812796 |
| Intermediate | 2.02546313055052e-12 | 0.34946971765395507 | 0.3494697176538317 |
| Endpoint | 7.259443046692127e-12 | 0.692604771056502 | 0.6926047710553235 |

`gradient_scan.csv` includes 3 vectors x 384 coordinates x 7 scales = 8064 rows and 48384 independent forward objective evaluations. Step multipliers were registered as 1e-2 through 1e-8, h_i = s*max(1,abs(theta_i)). Fourth-order central differences use +/-h and +/-2h; Richardson uses central h and h/2. Raw probe values, absolute/scaled errors, roundoff indicators and extrapolation stability flags are retained for every coordinate, including unfavorable values. Scaled relative error divides by max(1,abs(reference),abs(estimate)); absolute errors are separately available.

| Endpoint scale s | Central maximum scaled error | Fourth order | Richardson | Stable coordinates |
|---:|---:|---:|---:|---:|
| 1e-2 | 0.720730080 | 0.674817427 | 1.100834169 | 138/384 |
| 1e-3 | 1.286207393 | 1.424741126 | 1.343523272 | 150/384 |
| 1e-4 | 1.518333665 | 0.900970399 | 0.867719324 | 187/384 |
| 1e-5 | 0.0429420694 | 0.000986618309 | 0.000182515539 | 284/384 |
| 1e-6 | 0.000421803130 | 3.72053802e-7 | 2.00390881e-8 | 368/384 |
| 1e-7 | 4.19051874e-6 | 9.56214092e-8 | 1.55693822e-7 | 384/384 |
| 1e-8 | 6.71616956e-7 | 9.67676429e-7 | 2.22205311e-6 | 384/384 |

The all-coordinate maximum at s=1e-5 differs from the old 14-coordinate maximum. Both are preserved. Central error contracts by about 100x from 1e-5 to 1e-6 and again to 1e-7; higher-order values agree at the two adjacent preregistered smallest scales. Richardson begins losing accuracy at 1e-8. This supports finite-difference truncation/step sensitivity in the evolved recurrent objective, followed by roundoff sensitivity. It does not prove one universal best step or certify higher precision. No favorable step substitutes the frozen original gate. See `figures/step_scan.png` and `figures/endpoint_coordinates.png`.

## Separate A / B / C conclusions

A. Analytical gradient: no defect demonstrated. Independent AD matches all coordinates at initialization, the registered intermediate state and the exact-reproduction endpoint by much more than the frozen tolerance. This is numerical validation at these vectors plus synthetic oracle coverage, not a theorem for all parameters.

B. Original numerical estimate: unreliable for this endpoint at the frozen central-difference scale. The complete predefined scan and independent AD establish finite-difference instability. The original checker FAIL is preserved, rather than retrospectively passed.

C. Optimizer: genuinely nonconvergent under the frozen policy. It consumes maxiter=2000 and has independently verified endpoint PG approximately 0.693. Correctness at the three audited vectors does not certify every gradient evaluation, but the independent endpoint PG directly rules out convergence here. No corrected-gradient optimizer rerun or optimizer amendment was performed.

Exactly one D4 verdict is returned: **FINITE_DIFFERENCE_INSTABILITY**, with optimizer nonconvergence separately retained. `decision.json` and the independent saved-CSV reconstruction enforce these separate conclusions. The numerical gate PASS means the registered diagnostic completed; it does not restore M4 eligibility or any scientific model-comparison gate.

## Execution metadata failure and certification

The original numerical worker completed and produced all primary results. Its trusted controller exited 1 while publishing the completion receipt because `study.save` accepted two arguments and the archived launcher supplied a third exclusive-write argument. `native_attempt1.log` and original source snapshots are retained. The original native process exit and profile cleanup HRESULT were not published and remain UNPUBLISHED; they are not inferred or replaced.

Only this serialization interface was fixed, retaining exclusive append-only writes. A separately registered, independently reviewed native saved-only certificate hashed the completed payload, verified row arithmetic/coverage/statistics/D4 and role boundaries, and performed zero fits, zero derivative evaluations and no neural-array decoding. That fresh certificate has exit 0, no timeout, zero capabilities and cleanup HRESULT 0x00000000. These values certify the saved-only process alone. `results/receipt_recovery_launch_receipt.json`, `results/receipt_recovery/native/` and both unsuccessful and successful admission reviews preserve the distinction. The original missing process metadata is a disclosed historical limitation, not a numerical result fabricated by recovery.

## Recommended separately authorized next study

No mathematical source repair is justified by this audit. A future numerical-checker study may assess an independently preregistered stability/error estimator against AD while retaining all historical FAIL evidence and thresholds. It cannot retroactively pass this gate.

If separately authorized, a conditioning/optimizer study should be bounded to this one Training-A configuration and synthetic oracles, at most three predefined candidate runs, original architecture/offset/ridge/seed/bounds/PG threshold fixed, a prospective exact initialization/vector and solver-policy registration, independent endpoint AD/PG verification, and a hard stop without cohort competition. The options and budget must be approved before execution. This mission does not execute that study or choose a replacement optimizer policy.

## Reproduction and claim limits

From repository root: `powershell -NoProfile -ExecutionPolicy Bypass -File .\paper12_contgrad1\reproduce.ps1` (Python with NumPy/SciPy). It verifies the sealed manifest, all saved probe arithmetic, vector hashes, statistics and decision, then runs synthetic and saved-audit regressions. It never accesses neural data or protected state files, reruns a real fit, or repeats live isolation proof. Actual live native role proof belongs to the separately recorded executions. Failed review/test/controller attempts remain in the archive. Final review, scoped commit and remote closure certify the final relevant public candidate. Stop after diagnosis; M3/full M4/M5/nulls/M6/final evaluation remain prohibited.
