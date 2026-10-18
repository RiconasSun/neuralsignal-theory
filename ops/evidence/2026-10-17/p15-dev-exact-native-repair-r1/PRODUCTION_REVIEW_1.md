# Independent R1 production numerical and worker review 1

Mission: P15-DEV-EXACT-NATIVE-REPAIR-R1. Reviewer: `/root/gradient_review`. Date: 2026-10-17 America/Los_Angeles. Authority: OWNER_MISSION.txt, especially preservation, production certification, separate corrective budgets and execution-order requirements. Scope: versioned numerical components, source-level worker integration and independently executed synthetic production tests. **P0=0; P1=0 in this reviewed component scope.** This is conditional component acceptance, not permission to start real fits before the complete actual input gate and its independent review pass.

No real neural arrays, fit coefficients, A/B/E/Final scientific observations or network were read by this review. Synthetic optimizations/gradient checks were executed only on the test fixtures. Historical paper15_dev and M1 were not edited. New output consists of this report, its receipt and the existing synthetic test's generated gradient fixture in paper15_r1/work.

## Mathematical identity and fresh checks

The reviewer independently checked that `models.py`, `features.py`, `independent_ad.py` and `physiology.py` are byte-identical to the historical versions. Original mathematical/source reviews remain historical evidence; this R1 source identity check and fresh tests bind their mathematical conclusions to the new package. The exact61 configurations also equal the original generated configuration list, including B0-B4, D states2/3, C ranks1/2 and timescales.1/.25, S states3/4, original lambda grid and seeds11/23/37.

The reviewer independently ran33 tests:14 actual production model tests,11 feature tests and8 worker tests, with bundled runtime, BLAS/OMP/MKL threads1, bytecode disabled and ResourceWarning treated as error. Exit0; all33 passed. This is the independently executed denominator, not a claim to have rerun the parent's entire122-test suite.

The model test produces24 coordinate checks: each of B0,B1,B2,B3,B4,C,D,S at initialization,a fixed intermediate parameter vector and a synthetic optimizer endpoint. All analytical-versus-independent raw AD comparisons and all central FD steps1e-4,1e-5,1e-6 pass; no favorable-step selection occurs. Maximum AD scaled error is1.6653345369377348e-16; maximum fixed-FD scaled error is1.1584238013284676e-9. Additional tested points cover larger D/S state sizes and bound extensions. Bounds are not clipped during derivative evaluation; this checks the unchanged smooth objective extension, separately from feasible optimization/PG acceptance.

Other fresh checks cover exact Poisson factorial/exposure/T normalization, intercept ridge exemption, zeroed inactive coordinates, nominal parameter counts, nonzero baseline nesting, D/C/S reductions, brute-force conditional HMM likelihood, same-K IID identity, D past-only filtering, value-only objective equality, outward-gradient bound PG signs, full37 nuisance oracle, canonical four history windows, A-only scales, finite DCT history and future perturbation invariance. This is numerical/causal component proof, not real native-witness or all-source-input validation.

## Worker and corrective execution contract

`training.prepare` reads only versioned corrected A exports/task states and verified original metadata cache, constructs fresh A design/scales/C states and seals their hashes. It does not read old rounded task states or fitted coefficients. `source.P` is paper15_r1. The inspected cache adapters may read original source receipts/native source bytes after identity checks; their reference to historical QC receipts is source-custody reuse, not parameter transfer. Complete cache/native-content correctness belongs to the independent source review.

Fresh fits instantiate `build_model` from the current arrays and call `model.initialize(config['seed'])`. There is no old fit/coefficients loading path in the training module. Existing fit lookup is confined to the new paper15_r1 fit namespace; matching completed attempts are preserved, STARTED residues are rejected and exclusive `open('x')`/flush/fsync claims precede numerical execution. Concurrent/existing-claim and interrupted-claim denials passed fresh tests.

Registration prospectively separates359 historical starts (358 completed,1 interrupted) from the authorized new61-per-corrected-mouse main budget, absolute732. It records original solver/maxiter2000,maxfun80000,maxls40,ftol1e-12,gtol1e-6,zero retries and original PG/AD/all-FD thresholds, plus sensitivity absolute660 and55-per-corrected-mouse caps. The owner explicitly authorizes these separate corrective budgets; they do not retroactively validate historical scientific fits or reset the old accounting. Later summaries must still report historical/new/cumulative counts separately.

The worker uses original model bounds, callback diagnostics and saved endpoint arrays. Its numerical PASS requires bounds, PG<=.001, independent objective/AD/all-step FD checks and no exhausted-budget termination; optimizer_success alone is insufficient. B0 retains the original constrained stationary MLE. Dynamic progression requires all130 baselines for the actual ten-mouse example (13 per actual admitted mouse generally), complete matching hashes and global baseline availability. No failed mandatory baseline is replaced with another mouse or a favorable start. Relevant component tests passed; this review did not execute the actual full real worker.

## Mandatory actual-input/production gate before real execution

At review time the real input auditor is a separate ongoing task; its actual output and independent approval are **not certified here**. The production gate must not be inferred from these33 tests or from historical rounded-input numerical PASS labels.

Before a real fit, independently verify all required actual exact-native reconstruction, original witness, full-input comparison and corrected cohort/admission outputs. Seal an exact production gate binding that accepted input audit/review, A_FIT_PLAN, unchanged numerical sources, loader/cache sources, actual corrected A preprocessing/task/QC and feature identities. The worker checks every supplied gate hash and the feature-to-preprocessing hash, but does not itself require a complete schema of gate keys or independently assert every plan field against a hardcoded policy. Therefore the complete gate and exact plan bindings must be explicitly checked at actual admission; an empty or incomplete gate cannot be approved on this report. Relevant later source/plan/input edits invalidate affected evidence.

No B/E/Final access or real fitting is approved by this component report alone. Original STOP/source defect and358+1 historical records remain preserved. Full input-gate review is required before declaring the corrected source failure resolved. Sensitivity/E production admission and Final boundaries remain separately enforced and reviewed at their authorized stages.

## Exact identities and receipt

Receipt: `PRODUCTION_REVIEW_1_RECEIPT.json`, SHA256 `4406c7ccac1449d5cfaed85c011384da0e10ba1119e0a320e55b7e27105318eb`. It records the exact command,33 tests,24 points, fresh maxima, all inspected source hashes and exact AST source-segment hashes of training functions.

| Source | SHA256 |
|---|---|
| paper15_r1/models.py | e13d12d3986b42ba1691075804df7b2ec6a033dcfe20fac36e5b6ed8e359ba90 |
| paper15_r1/features.py | 30d17b3a902429537e8b83fc9ac5a483933bdb8080ff890c5f43c6fc5f4dd3fd |
| paper15_r1/independent_ad.py | 8c69998bd1d03004325fb24d39c4d33fb4be15966b8e30321248d13480521ec0 |
| paper15_r1/physiology.py | 1e85584d4f779df9b063941b153715def105ad9cf006046fa7694eb1a12176fd |
| paper15_r1/training.py | 9bedaaa5b3cb4d96c25471d86edd84ab3501bb6b312fee6b2e0ceda826c3eb8c |
| paper15_r1/source.py | ad8d0f786690d414f07568556d017e0bdb14edd0137fb246789e7ffb7cedddbb |
| paper15_r1/metadata_access.py | bd32678410e38a262150a015df1f6b896ac6f9fa62da1aaf169153ab37f2dfb9 |
| paper15_r1/cached_source.py | cbc1a8cefdc2743cc96587f65c2dc9201a876cd843e3f0eee055f638268aa800 |
| paper15_r1/test_models.py | 3010b2979c9ca98bc6aee4c02992b9e657f5163c450c243a9aaf9dc1bbdac8af |
| paper15_r1/test_features.py | 751fd03f1e084a9c7d1d35f5e001f43f028a18f2afc23a68a482b1ac6eb0b122 |
| paper15_r1/test_worker.py | 75aa02a9a07713208ae52b610e227ae7d2e1f166ff4999bb4ab02e2420012ca1 |

Reviewed `build_model` AST source-segment SHA256: `cd9074bc070d0e9dadefcad0e19a290221e31c031996daf27855fb78de3307f5`. Preserve this review and issue a new affected review after relevant changes; do not silently replace this conditional approval with whole-input/whole-mission PASS.
