# Independent M3 current-byte numerical review 3

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. BASE: 30cb925f505d63ae52bb1461d9ab153a52f1888e. Independent reviewer: `/root/gradient_review`. Date: 2026-10-17 America/Los_Angeles.

**P0=0; P1=0 for the exact mathematical/feature/helper components identified below.** Accept these current components for the consolidated production-worker gate. This report supersedes reliance on review 2 for the changed `models.py` and `independent_ad.py` byte identities; reviews 1 and 2 remain unchanged historical evidence. It does not independently certify the complete fitting/attempt/selection/access worker or create real-fit permission without the separately required worker review and source-bound consolidated gate.

## Current value-only implementation

The changed production files were read in full. `Model.value` computes the same negative score log likelihood divided by T plus ridge on the same non-intercept free coordinates. Baselines/C use the same Poisson exposure, factorial and score slice. S sums IID pre-bin log masses over the score interval. D sums its causal pre-bin normalizers and subtracts the warm-prefix normalizers, preserving the conditional full-minus-warm objective. This removes unnecessary posterior/backward-gradient computation for scalar finite differences; it does not change the target, penalty, normalization, bounds or warm-up derivatives in the analytical objective.

The independent raw-equation autograd objective is unchanged. Its finite-difference caller now uses `model.value` at the same plus/minus parameter vectors. All three absolute steps {1e-4,1e-5,1e-6}, scaled coordinate error definition, all-step requirement, synthetic AD<=1e-8 and real AD<=1e-5 remain unchanged. Mathematical extension outside a box is still evaluated for the derivative comparison; no clipping or favorable-step selection was introduced.

The causal prediction optimization `fe=e` applies only when the assimilation counts are the original target counts. The separate `filter_y` branch still computes emissions from the supplied assimilation counts, and prediction still occurs before assimilation. Reusing an already identical emission array does not replace filtering with smoothing or current-bin posterior prediction.

## Fresh independent evidence on these exact bytes

Using `paper15_dev/work/runtime/Scripts/python.exe`, single BLAS/OMP threads, bytecode writes disabled and ResourceWarning as error:

1. **All 25 current production model/feature tests PASS**: 14 model methods plus 11 feature methods. These include exact Poisson/exposure/normalization, parameter counts and nonzero nesting/reductions, analytical versus raw AD and every fixed FD step, conditional HMM enumeration, IID/static distinction, larger-K/boundary derivatives, PG signs, invalid inputs, seed/ridge behavior, the new scalar-value identity, all 37 nuisance values, causal perturbations, canonical history edges and DCT reset/scaling.
2. The 24 initialization/intermediate/synthetic-endpoint coordinate comparisons were captured without overwriting the existing diagnostic certificate. Only the test's persistence callback was intercepted; no model, derivative, numerical step or assertion was changed. A subsequent focused execution of that coordinate test also PASSed on these current files. Max analytic/raw-AD scaled error: **1.6653345369377348e-16**. Max finite-difference scaled error over **every** fixed step at these 24 points: **1.1584238013284676e-09**.
3. Additional independent value-identity checks covered **30 synthetic vectors**: initialization, fixed intermediate and bounded-coordinate fixture for B0/B1/B2/B3/B4/C/D2/D3/S3/S4. `value(theta)` versus `objective(theta)[0]` maximum absolute difference was **0.0**. For D2/D3 at all these points, default filtering and explicit `filter_y=model.y` produced exactly equal pre-bin masses.
4. The first supplemental reviewer-written boundary probe incorrectly indexed a nonexistent B0 non-intercept coordinate after the 25 production tests had already passed. This was a reviewer-fixture IndexError, not a product failure. Guarding that synthetic index resolved it; the corrected 30-point probe above passed with no production code change. This unsuccessful auxiliary attempt is explicitly retained here.

The parent's reported full 64-test suite and consolidated M3 receipt are additional evidence, not represented here as an independent rerun of all 64. This reviewer executed only synthetic fixtures; no real neural arrays, A-role exports, B/E/Final values, network calls or real fitting attempts were read or executed.

## Unchanged feature and active-coordinate surface

The fixed canonical shared microbin-edge implementation and its tests retain the exact review-2 identities. The review-1 history-window defect remains resolved. The complete nuisance table, strict event/wheel availability, A-score-only scaling and DCT finite observed-history construction have current independent feature test PASS evidence.

`training.build_model` has the same function-source hash as review 2. It supplies the shared design/target/ridge and active mask to B/D/S and appends the selected C rank/tau state plus its active flags for C. Review-2 synthetic active-count/zero-coordinate evidence therefore certifies an unchanged helper surface. The training file as a whole changed independently; this report does not promote those other worker changes through an unchanged helper review.

No scientific equation, tolerance, FD step, solver, seed, start count, parameter box or fit budget amendment is needed or approved. No remaining component P0/P1 is identified. Full production fitting remains conditional on the other independent review, exact gate/source binding and all authoritative prerequisites.

## Exact current SHA256 identities

| Source | SHA256 |
|---|---|
| paper15_dev/models.py | e13d12d3986b42ba1691075804df7b2ec6a033dcfe20fac36e5b6ed8e359ba90 |
| paper15_dev/independent_ad.py | 8c69998bd1d03004325fb24d39c4d33fb4be15966b8e30321248d13480521ec0 |
| paper15_dev/features.py | 30d17b3a902429537e8b83fc9ac5a483933bdb8080ff890c5f43c6fc5f4dd3fd |
| paper15_dev/test_models.py | 3010b2979c9ca98bc6aee4c02992b9e657f5163c450c243a9aaf9dc1bbdac8af |
| paper15_dev/test_features.py | 751fd03f1e084a9c7d1d35f5e001f43f028a18f2afc23a68a482b1ac6eb0b122 |
| paper15_dev/training.py at this component review | 1c11098672df8d24c54770375c6c0c8db351622d533badf30bc11170dba0212d |
| training.build_model function source, UTF-8 via inspect.getsource | a40e8e29dda5df3e365d37fe3270dc0c8793c81f08b1541b3cbd9839f28bf0b6 |
| paper15_m1/FEATURE_MODELS.md | 37ef100353913eb2a99d92ffb9404093b2d850ce326fd6b497dec31ec2453b4e |
| paper15_m1/NUMERICAL_POLICY.json | cc0c926b04540f1787e0a005f6566bf42225cb2bca159fd9accdd3e74ab0358e |
| paper15_m1/NUMERICAL_SELECTION.md | 6580c55effc5ce13f07649279a39a009a66734407312413681d40e941a16bbef |

Only this new report was written by the reviewer. Any further relevant source change invalidates the corresponding current-byte review and requires affected fresh evidence; the earlier review files must remain preserved.
