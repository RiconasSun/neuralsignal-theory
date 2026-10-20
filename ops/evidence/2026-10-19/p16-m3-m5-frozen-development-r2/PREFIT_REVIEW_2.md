# Independent R2 production prefit re-review — revision 2

mission: P16-M3-M5-FROZEN-DEVELOPMENT-R2

reviewer: independent internal agent /root/r4_policy_review

BASE/current HEAD: 4aef2810885b6167ef909eb8ccc9e8c5c967871a

candidate_revision: 2

decision: REQUEST_CHANGES

open_P0: 0

open_P1: 1

resolved_attempt_1_P1: 4

The four original implementation findings are resolved in this candidate. One newly identified saved-results reproduction gap remains. This is not M3 production prefit acceptance, an authorization to start the scientific stage, or scientific evidence from real Development/Final data. No approval is written. The prior failed review is preserved at its original path and hash.

## Review activity and bound evidence

Read REPAIR_REGISTRATION.md, the revised manifest and every changed source/test/policy neighborhood against the exact attempt-1 snapshots. The revision changes controller, controls, core, features, source, SOURCE_PINS, tests, implementation-policy explanation and the synthetic certification; model objectives, numerical optimizer/client, panel planning, mathematical scoring and saved reproducer are byte-identical to attempt 1. Owner authorization, scientific definitions, models, units, masks, ridge grid, seeds and numerical thresholds are unchanged.

Independently checked all 31/31 manifest payloads, plus the manifest; all sizes/digests match. Independently checked all 28/28 attempt-1 payload snapshots against the original frozen manifest, and the original failed review at both original and snapshot paths. The old manifest remains a5bdcdac32b3cc8f291eec1e1b792d420e811158bb47fae9c5cce57349aa280e; the old failed review remains 7ea6a413dadaff2fcc3928dd30ab6af2f8e64ff83aa7349220e8a33cb09b8fe0. Original 26-test evidence is preserved rather than overwritten.

Independently checked all 238/238 SOURCE_PINS files against both current bytes and exact BASE Git blobs, totaling 49,139,731 pinned bytes, without decoding arrays. All 13/13 current normative files match BOOTSTRAP. This confirms that the enlarged expectations came from the approved BASE rather than newly calculated scientific identities. Import-time verify_pins runs before NUMERIC parsing and scientific module imports; source.metadata also rechecks it before reading adapter data.

Reviewed the actual revised native synthetic evidence: 30 tests, zero failures/errors/skips, 38.703 seconds; source hashes unchanged before/after tests; exact pinned runtime; native Job assigned before resume, full descendant-tree enforcement, return 0 before deadline, no clock failure or deadline kill. These are fresh parent-executed native tests, not 30 tests independently rerun by this reviewer and not real numerical-convergence evidence.

Independently reran 16 existing stateless synthetic tests, exit 0, 0.803 seconds, with socket connections denied and bytecode disabled. The 13 prior independent math/causal/packing/AD/fixed-FD/S07/N4/control/budget/role tests passed again, together with the new previous-stimulus distinction, all-live-normative/fresh-import fail-closed test and S04 complementary-panel test. The norm regression injects missing/mismatched identities for each of the 13 files and verifies refusal at both core and prefit, including a fresh subprocess before numerical-policy parse. The file-creating metadata corruption/native integration regressions were inspected in the bound 30-test run; this reviewer did not rerun those file-creating tests under a second synthetic root.

No current R2 scientific results/stage artifacts exist. The revised manifest/certification still record real fits 0, B/E access false and Final access false. No HTTP, real neural array decode, new A feature/scaler construction, real fitting, B/E or Final access occurred during this review. Only PREFIT_REVIEW_2.md is written.

## Attempt-1 findings

| Finding | Re-review result | Evidence |
|---|---|---|
| P1-01 previous stimulus versus neural/support validity | RESOLVED | source.metadata constructs a distinct stimulus_valid from the frozen stimulus-invalid intervals, finite source timing/color and original flash duration. build requires and uses it for original j−1. main_valid/common masks/units/target rows remain unchanged. Repetition features retain original scheduled rows. Corrected oracle and added original-index, support-only, invalid/unknown, repetition and target-mask regressions are explicit in REPAIR_REGISTRATION. |
| P1-02 normative identities before policy use and prefit | RESOLVED | core.verify_pins follows all 13 normative expected paths before NUMERIC parsing/imports, and controller.verify_prefit invokes it before reading approval. Independent 13-file missing/mismatch and fresh-import tests pass. BOOTSTRAP is itself part of the reviewed manifest. |
| P1-03 S04 missing panel | RESOLVED | controller now calls running_panels using the same frozen scores, primary support and running-missing flag. available/missing masks are complementary, each has explicit valid-bin/unit-bin/presentation/exposure denominators and effects or EMPTY_NO_SCORABLE_BINS with no invented effect. Existing available-case coverage and causal filtering remain unchanged. All-available/all-missing/mixed synthetic cases and denominator reconciliation pass. |
| P1-04 source metadata/certificates/dependency identities | RESOLVED | Before adapter decode, source.metadata validates the registered source, all pinned dependencies, QC/result references, frozen metadata JSON/NPZ and running derived bundle. Returned pins, flash arrays and running array set/shape/dtype/raw hashes must match frozen receipts. native_role rechecks QC/result before parsing and uses the checked native-object certificate. The 238 BASE-bound pins include running RESULT/bundle, source QC/result, roster metadata/index, headers, probes and concrete imported helpers. Missing/corrupt/fabricated-identity regressions are preserved in the actual native synthetic run. |

The review_path adjustment is a bounded closure change: approval binds a report path resolving inside the current evidence directory and its exact hash, as well as the current manifest. It permits this second independent review without overwriting the first rejection. It does not itself create approval, a new release entitlement or scientific retry.

S05 remains a prefit lack-of-verified-pupil-timing certificate, not a claim of absent arousal or an optional label applied after numerical failure. S07 rate ranking and canonical parameter order remain distinct. N4 still maps raw covariates before the frozen scaler. The unchanged A→all648 B1→B selection→all remaining/panel/three-seed fits→full M4 seal→one E sequence, 7506 Development ceiling, 7722 Final reserve, 16178 study ceiling, original external 6000/1500 limits and single 48-hour Job are retained. Earlier substantive math/source limitations in the first review still apply and are not erased by resolving its defects.

## New P1-05 — Saved-only reproduction does not reproduce registered descriptive intervals/group outputs

Locations: paper16_development_r2/reproduce.py:100–112; controller.py:260–263; controls.py:66–80. Owner requirements: OWNER_REQUEST.txt:279–283 require registered descriptive intervals and separate BO/FC reporting; :379–392 require scientific/reproducibility deliverables and one-command saved-state reproduction.

facts() verifies per-mouse main absolute scores, six effects and pooled equal-mouse means from saved scores, then reference aggregates. It does not inspect or recompute exploratory_whole_mouse_CI95, bootstrap_seed, bootstrap_replicates, or any BO_FC group fields. Hash-binding source/results establishes identity, but does not reproduce those reported statistics. Setting E_results_recomputed_from_saved_scores_only cannot establish interval/group reproduction under this implementation.

Independent in-memory witness used 27 synthetic mouse score dictionaries, with five BO and 22 FC, valid per-mouse scores/effects and correct equal-mouse means. Replacing the pooled CI and BO_FC with malformed strings, seed with −123 and replicate count with 0 still allowed facts() to return E_results_recomputed_from_saved_scores_only=True. No actual results were modified, no source or saved real E array was read, and no forecast was generated. The first witness setup failed with TypeError because its in-memory np.load stand-in did not accept allow_pickle; the stand-in signature was corrected and the same isolated witness then demonstrated the unchecked fields. This was a reviewer synthetic tooling error, not a scientific attempt, and is not counted as passed production evidence.

Required minimal repair: from already verified saved mouse score/effect summaries, reproduce the exact registered pooled bootstrap (PCG64 16042, 10,000 whole-mouse resamples, linear quantile 0.025/0.975) and the separate BO/FC outputs (numeric mouse order, seeds 16043/16044, 10,000 resamples, original group floors, equal-mouse means, intervals, absolute-model means and descriptive denominators). Compare the required fields, including seed/replicate declarations, identity/order and scope flags, and fail closed on missing/malformed/mismatched fields. Reuse of the version-bound deterministic statistics routine is acceptable; no new source, neural decoding, model prediction, fit, derivative call or second E is needed. Add synthetic correct-data, modified-CI, changed-seed/replicate, missing-group/wrong-membership and group-mean/denominator regressions. Keep the statistical definitions and thresholds unchanged. An early scientific STOP with no E must retain the explicit unexecuted path and must not fabricate intervals.

## Required continuation

Keep the scientific stage unstarted. Preserve this revision-2 candidate, 31-payload manifest, 30-test evidence and this rejection as immutable attempt evidence. Repair only the saved-statistics reproduction gap and its regressions, freeze revised identities, rerun sufficient affected checks and the complete native synthetic certification required by this mission, then obtain independent prefit acceptance. The four resolved findings remain recorded as resolved for revision 2; later evidence must bind any subsequent code state. No human scientific decision is needed for this implementation completion.

## Exact reviewed identities

All paths are repository-relative. Every manifest payload below was independently checked against its actual current bytes; separate preservation records/reviews follow. This report is separately hash-bound after writing.

| Path | Bytes | SHA256 |
|---|---:|---|
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/goldenstandards.md | 2519 | 35a37c6106d45c6bdef85422a32005598189bc599ac7589f8db7e9130298ed3e |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/M3_REVISED_SYNTHETIC/CODE_HASHES.json | 1302 | 0b7e908341c6352519ef0b35b869b5e30fd6d8ca6db61540ec9577e640ec4e10 |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/M3_REVISED_SYNTHETIC/RESULT.json | 1762 | 35c13a2cf5132068be1e0defa05e8fdcc4aa9e88e2781c33be82f941ca2246be |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/M3_REVISED_SYNTHETIC/STAGE.json | 255 | 684ee7334463dc2f4a887a0335df6b911ab389a144ef21c2f9b024194e59ee68 |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/M3_REVISED_SYNTHETIC/SUPERVISION.json | 245 | 5b9313f2a8b22b2bc496da8474e23675b4e739c5842ee9f6841aa75f340df939 |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/M3_REVISED_SYNTHETIC/TESTS.log | 5710 | a3aa900e42e1b814939626296586b35715169bd6dff30efcab521537b6abea37 |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/OWNER_REQUEST.txt | 17134 | 671b169ea0e5c0d2533ae95026736143b429c0548a6748a7466021f55c3373bd |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/PREFIT_ATTEMPT_1/PRESERVATION.json | 325 | 918c975abeaa24664e3c8bc92735cef88256a1189aff54e54e66ddbb34bc0dbf |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/PREFIT_REVIEW.md | 21433 | 7ea6a413dadaff2fcc3928dd30ab6af2f8e64ff83aa7349220e8a33cb09b8fe0 |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/REPAIR_REGISTRATION.md | 2142 | b325b9b067092ff83b0042c525d150d36f9faa66fd4ca4d32189f75aa98b2c9d |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/REQUIREMENT_BASELINE.json | 52111 | 2b88affd2bf27366d2aa41c4fd91563790b5a12f6b78c1961dd04abe1a5b2ab4 |
| paper16_development_r2/.gitignore | 25 | 16efb1aafab2d99d1dfee53e728010380484ce4c3ef3e5980bb1ba5f4aaa3533 |
| paper16_development_r2/ACCESS_REGISTRATION.json | 51742 | 2ce10636604311e55063fa32bda48df0a1cec7b6904cae31cb71d7858a846a1e |
| paper16_development_r2/BOOTSTRAP.json | 3747 | 7fe3f161a61ac4d42a4b51313e4a5a0a6434a97b743c9e35282efe7057f140ac |
| paper16_development_r2/certify.py | 3239 | 11084a909993b04e7eb322e44baab0bfe7272a9ed24bf6f7c5409e311c3af62c |
| paper16_development_r2/controller.py | 25787 | 9a77471f8242d51eeec1300518234f82d4c95128f7a9492b1af818fbc4c085f2 |
| paper16_development_r2/controls.py | 7504 | 982a21b69d0c6f5dbfdc6028b82e90556e2579f8d3ec58b5e89eae0c7351406b |
| paper16_development_r2/core.py | 2618 | 172be1154dab513259f8a51cb7fb65a9c070529a203051fad3cc0d6373e262e9 |
| paper16_development_r2/features.py | 6263 | da7d655dc5a2c00f95ed1da1566153277334bd7f403e033ae0265b498c5c016b |
| paper16_development_r2/IMPLEMENTATION_POLICY.md | 5771 | 7f2b918f52b727cdce34dcc53258c1ae56ceaf463901c01849d2f5ea66e3f80a |
| paper16_development_r2/MISSION_SPEC.json | 937 | 6fe5cd53478ae7a5c905ae1f40ff652e6a078add0dfcebef0388728973f76a70 |
| paper16_development_r2/models.py | 4752 | e13e5feff0b4101ddc27cb5dd0177760b8a6b787a8abf6f026b2bacfc9dd7869 |
| paper16_development_r2/optim_child.py | 1117 | e6993643323d224391b54fda3a686068ba160457ad651ecb05e25cea74e0ba24 |
| paper16_development_r2/optimizer.py | 7817 | 5441398d633159d613c608d5d8656267ce6b43e3fe5983a4cd4ca61e1fd3228c |
| paper16_development_r2/panels.py | 5173 | dc91d666f18435a751d6a3d4ce7a8a9719c5d90e52bf59b3a105e2062883dada |
| paper16_development_r2/PRODUCTION_NUMERICAL_CERTIFICATION.json | 2587 | 9bcab14b6a8f6003da7380b59251a2bd445e0d4a9715a7db50c9fc94e0dd1372 |
| paper16_development_r2/reproduce.py | 9189 | 678e8f017101d06f135c049bb0b860a0d40d2a37d25b6c5d407bd9c38e0ff8ce |
| paper16_development_r2/REPRODUCE_SAVED.ps1 | 515 | 2e57cca7323005b9ec57c6ac385d31c358e55060b2db01d9e5014585bc73347c |
| paper16_development_r2/source.py | 15349 | e1a24d21b3862158c049b337d6521e55c47a708f985bbdc1513c5db618548f91 |
| paper16_development_r2/SOURCE_PINS.json | 30236 | e5a9d1fd1662d04dc9271289b0d1b588f8a6ae051496ec1eb00760af9b07a292 |
| paper16_development_r2/test_production.py | 31967 | fcd833ea0e240b0b702604f8e3142e2880dc9f623d4e8935748bf4d218f78514 |
| paper16_development_r2/PREFIT_FREEZE_MANIFEST.json | 6067 | 1273d132d2c5af3df23271db68c0ea55251f15b26791b19f3623a7ce45c202e0 |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/PREFIT_REVIEW.md | 21433 | 7ea6a413dadaff2fcc3928dd30ab6af2f8e64ff83aa7349220e8a33cb09b8fe0 |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/PREFIT_ATTEMPT_1/PREFIT_FREEZE_MANIFEST.json | 5384 | a5bdcdac32b3cc8f291eec1e1b792d420e811158bb47fae9c5cce57349aa280e |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/PREFIT_ATTEMPT_1/PRESERVATION.json | 325 | 918c975abeaa24664e3c8bc92735cef88256a1189aff54e54e66ddbb34bc0dbf |

real_scientific_execution_started = false

Final_access_authorized = false

review_scope = independent production prefit revision-2 audit; REQUEST_CHANGES only
