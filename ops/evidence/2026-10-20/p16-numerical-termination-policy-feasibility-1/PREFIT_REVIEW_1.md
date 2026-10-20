# Independent pre-execution review, candidate1

MISSION: P16-NUMERICAL-TERMINATION-POLICY-FEASIBILITY-1

BASE: 682b0ac37fc6a0bc211acc388134058ec3c071aa

Decision: **REQUEST_CHANGES**. open_P0=0; open_P1=1. No prefit approval is issued and no real A attempt is authorized by this review. Owner authorization remains conditional on all required preceding gates.

## P1-01: incomplete consumed attempts cannot be reproduced

`paper16_termination_feasibility1/reproduce.py:73–76` unconditionally invokes `check_fit(work/real/fit)` whenever REAL_A_DIAGNOSTIC_ATTEMPTS is nonzero. `check_fit:14` immediately requires RESULT.json and DIAGNOSTICS.json; lines43 and58 demand a complete24P/3/3 diagnostic set. A permitted genuine STOP from access/implementation failure before endpoint, interrupted FG, external deadline or incomplete diagnostics therefore reaches FileNotFoundError or a complete-certificate assertion rather than verifying the saved STOP. The supervisor correctly consumes the one entitlement before launch, so recording zero attempts or trying again would violate the contract.

This affects owner requirements R-099 (no extensions/retries), R-121–123 (INCONCLUSIVE/STOP with exact reason), R-136–139 (attempt, certificates as available, resource/access/preservation evidence) and R-142 (saved-only reproduction). Complete negative numerical results and incomplete consumed attempts must remain distinct. A genuine incomplete result cannot acquire a numerical PASS, fabricated endpoint, zero attempt count or replacement run.

Minimal correction: add a saved-only incomplete-STOP branch that validates the consumed claim/stage identity, actual existing stop/supervision/failure and partial journals, reservations/caps, absence of a successful completion and explicit unavailable endpoint/certificate fields. Verify complete results with the existing strict routine. Missing mandatory failure evidence must fail closed. Add pure saved-evidence regression coverage for a consumed pre-endpoint STOP and partial certificate/journal interruption, while retaining complete positive/negative validation and rejection of fabricated PASS/zero-count or missing STOP evidence. This requires no new scientific fit, policy change, fixture optimization or A neural read. Preserve candidate1 and this unsuccessful review, then independently review the revised finite candidate before the one real trial.

## Otherwise verified prefit surfaces

Reviewed the complete189-statement baseline against the owner request and candidate execution plan. No additional P0/P1 was found in the reviewed neighborhood. Independently verified34 prefit payloads,19 code-freeze entries,626 inherited source/evidence pins and10717 protected file hashes. This was byte hashing, not protected neural decoding. REAL_CLAIM.json is absent; no protected A neural values or new real optimization were accessed by this review.

Candidate policy differs from frozen M1 only in ftol=0.0; original gtol2e-6, PG1e-5, AD1e-8, fixed FD1e-5/error2e-5,1500iterations,6000FG,888FD,3AD,3analytic,one worker and7200s/no-retry limits remain. Official SciPy v1.16.3 C source lines691/933–945 independently confirms tol=factr*epsilon, PG checked first and relative-F branch retained at zero tolerance. Source: https://raw.githubusercontent.com/scipy/scipy/v1.16.3/scipy/optimize/__lbfgsb.c . Installed wrapper/binary/runtime hashes are pinned; no independent binary rebuild is claimed.

Static review checked the unchanged imported R3 feature/scaler/Objective mathematics, exact saved A input member hashes, original initializer/bounds comparison, frozen unit951800892/S02/C/lambda1, external FG/accepted-iteration accounting, all three diagnostic checkpoints, fixed four-scale FD and reservations, fresh exclusive claim before launch, native assign-before-resume/7200s Job tree guard, ordinary-process access hook, and absence of source/controller/scoring paths. Historical lambda is fixed, not reselected. No warm-start or accepted250 substitution exists. Access-hook protection is limited to reviewed ordinary processes; no hostile-administrator custody claim is introduced.

Native certificate reports15/15 tests, zero skips/errors/failures, the exact19-file code freeze and a normally completed synthetic Job. Reviewer did not rerun optimization. Reviewer independently ran only saved-state check_fit arithmetic for all four fixtures: poisson PG8.323608169380492e-8 (11FG/8iterations), slow_quadratic PG6.448810935255622e-8 (9/3), bound_quadratic PG0 (2/1), rounded_plateau PG0.1 (2/1). The three positive certificates pass; the negative rounded plateau remains numerical_pass=false despite successful relative-F termination. No tuning or alternate candidate is inferred or authorized.

Historical M1/R3/forensic files and original R3 STOP are unchanged. Single-unit feasibility could never establish all6471 planned tasks or retrospective R3 PASS. Remaining future outcome documents, independent final review and actual Git/clean closure are not prefit-complete scientific claims. Do not start A until P1-01 is resolved and the exact revised candidate receives ACCEPTED_SINGLE_A_DIAGNOSTIC.

## Frozen identity

All34 payload identities are transitively covered by PREFIT_MANIFEST.json. This report and its binding are separate review evidence; preserve them without changing the frozen candidate.

| Path | Bytes | SHA256 |
|---|---:|---|
| paper16_termination_feasibility1/PREFIT_MANIFEST.json | 7348 | 3239c506735518d57169c1b9e89b1bea2a0863e392f95b8781f75406ad09d103 |
| paper16_termination_feasibility1/CODE_FREEZE.json | 3816 | 9f43af1408f83f7f888159857b59c9acbe11e25b084b0cc8ac0f6ed6ec51d006 |
| paper16_termination_feasibility1/reproduce.py | 7573 | fd3a5f79d60340cab102cd774089df8919e35cb1007c4cad088a28af993ab355 |
| paper16_termination_feasibility1/SYNTHETIC_CERTIFICATION.json | 821 | 0ce0695099f641732c57cbfbd5b95f195953eee5188e879a2ee01ed68c40c6a4 |
| paper16_termination_feasibility1/SYNTHETIC_OUTCOMES.json | 43174 | 89edb37d30bddad7b50b3af1b60333c92918cdc48c08e62e79b5b06dcbfbc3f6 |
| ops/evidence/2026-10-20/p16-numerical-termination-policy-feasibility-1/SYNTHETIC_TESTS_1.log | 1911 | bf053ce920661ab623851a1b1265714c254ce3cf86e70b5638d6d52e31a99b23 |
| ops/evidence/2026-10-20/p16-numerical-termination-policy-feasibility-1/SYNTHETIC_SUPERVISION.json | 253 | cd62d6f1364201560bb185e19909d9a0175b582597c668d37c14a376a00d739a |
| ops/evidence/2026-10-20/p16-numerical-termination-policy-feasibility-1/PRE_A_ACCESS_ACCOUNT.json | 171 | e01c634efb3767dd87cf57e2cdf16e3483567da01f71292a1aeb0729d99fcf30 |
| ops/evidence/2026-10-20/p16-numerical-termination-policy-feasibility-1/REQUIREMENT_BASELINE.json | 38603 | 9b408cf2cfec14682680dcb8360b6e41b6ae56f3a819211d3acf4b37069d3555 |
