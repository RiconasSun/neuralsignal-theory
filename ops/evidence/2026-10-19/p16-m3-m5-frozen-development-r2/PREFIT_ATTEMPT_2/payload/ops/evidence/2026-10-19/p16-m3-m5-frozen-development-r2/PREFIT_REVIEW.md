# Independent R2 production prefit review — attempt 1

mission: P16-M3-M5-FROZEN-DEVELOPMENT-R2

reviewer: independent internal agent /root/r4_policy_review

BASE and current HEAD: 4aef2810885b6167ef909eb8ccc9e8c5c967871a

decision: REQUEST_CHANGES

open_P0: 0

open_P1: 4

Production M3 acceptance is withheld. This review does not authorize real A feature/scaler construction or fitting, B/E neural access, any Final access, or advancement to M4/M5. It does not waive the historical R1 STOP or retrospectively change source/physiology evidence. No PREFIT_APPROVAL is produced.

## Scope and actual activity

Read the complete current OWNER_REQUEST, requirement baseline, all 28 frozen prefit payloads, all new production Python modules/tests, the bound implementation/access/numerical policies, the 13 BOOTSTRAP normative scientific files and the additive precision definitions. Reviewed causal scoring, fit packing/objectives, derivative certificates, source and phase gates, panel/control definitions, external call/iteration/deadline accounting, state completeness and saved-only reproduction. Earlier R1 archive-only acceptance was not used as production evidence.

Independently rehashed 28/28 current manifest payloads plus the manifest itself; all match. Independently rehashed all 13/13 BOOTSTRAP normative files; all currently match. Separately verified 135/135 existing file hashes across the 27 admitted sources: each source's frozen QC and result references, metadata JSON, flash NPZ, and derived-running NPZ. No arrays were decoded in that 135-file verification. These checks establish current identities, not that the production gates enforce them on subsequent reads.

The exact candidate's bound native-Windows certification reports 26 tests, zero failures/errors/skips; native Job assigned before resume, full tree enforcement and timely return 0; real fits 0. Reviewed its bound RESULT, CODE_HASHES, STAGE, SUPERVISION and TESTS log. This is parent-executed fresh synthetic evidence, not an independently rerun 26-test native certification or real convergence evidence.

Independently ran 13 existing stateless synthetic tests with the exact pinned Python, no bytecode writes, no source transport and no real neural arrays. All 13 passed (0.364 seconds). Tests covered primary feature boundaries; strict-past/role reset; A-only scaling; GLM AD/fixed FD; full D/S packing, AD and forward score; B4 nesting/no scoring smoother; S07; all 11 N4 maps; refit-panel/pupil synthetic geometry; N1 joint donors; N2/N3 invariants; external call/iteration boundary logic; role splitting/full-row integrity/original cuts. Their PASS does not cure a wrong oracle in the previous-stimulus case below. Also ran the three isolated synthetic counterexamples described in P1-01, P1-02 and P1-04. None started a scientific stage or wrote an approval.

Current production results/stage artifacts remain absent, and the frozen manifest/certification declare real fits 0, B/E access false and Final access false. This review performed no HTTP, native-source decode, new real A features/scalers/fits, B/E access, or Final operation. Only this review file is written.

## P1-01 — Previous-stimulus features use neural/support validity instead of stimulus validity

Locations: paper16_development_r2/features.py:48; paper16_development_r2/test_production.py:105–106; reused paper16_dev_r3/run_m2.py:76–95; paper16_m1/code/roster_metadata.py:24–43,58,96.

Normative requirement: paper16_m1/FEATURE_AND_MODEL_EQUATIONS.md:23 defines previous presentation as original j−1, never a post-exclusion replacement. Its missingness is determined by invalid/unknown source stimulus metadata; neural/support QC exclusions must not redefine adaptation features. The source roster explicitly distinguishes stimulus-invalid intervals from broader probe/neural invalid intervals; main_valid combines them. The original flash NPZ preserves both interval sets.

Observed: build() makes `known` conditional on `flashes['main_valid'][previous]`. The adapter exports main_valid but no separate stimulus validity. A previous presentation with valid stimulus metadata and a neural/support-only exclusion is incorrectly represented as unknown, setting previous color/gap to zero and previous-missing to one. The existing test asserts precisely this conflation.

Independent synthetic witness: with a valid original previous color −1, all stimulus metadata valid, and only previous main_valid false, build produced previous color 0 and missing 1 instead of color −1 and missing 0. No real input was used. The error changes frozen nuisance predictors, potentially affecting every B1-derived family and its contrasts.

Required minimal repair: expose a distinct stimulus-metadata validity indicator from the already frozen stimulus-invalid metadata, after the identity checks in P1-04. Keep original main_valid, common masks, selected units, target rows and all neural/support QC unchanged. Use the original j−1 and already-observed timing exactly as registered. Correct the test oracle under an explicitly recorded TEST_BUG explanation; retain the old test/log evidence. Add synthetic distinctions for neural/support-only exclusion, stimulus-invalid/unknown previous rows, original-row versus replacement indexing, and unchanged repetition counts and target masks. No scientific amendment or new source acquisition is needed.

## P1-02 — Live normative hashes are not enforced before policy use or prefit acceptance

Locations: paper16_development_r2/core.py:33–46; paper16_development_r2/controller.py:11–23; paper16_development_r2/BOOTSTRAP.json normative_files.

Observed: verify_pins() checks the 22 SOURCE_PINS entries. verify_prefit() checks the 28 payloads, including BOOTSTRAP's bytes, but does not compare the 13 normative file paths against BOOTSTRAP's expected digests. In particular NUMERICAL_POLICY.json is parsed into NUMERIC after the incomplete import-time pin check. Its solver and derivative policy can therefore be consumed before any actual normative hash check; the same absent check persists at the real prefit gate.

All 13 current normative files match; no actual alteration is alleged. Independent no-write sentinel test made the hash function return a mismatch for the numerical-policy path while preserving the real candidate/manifest and providing only a synthetic accepted review object. verify_prefit still returned acceptance, and the numerical-policy path was never queried. The synthetic review object was never persisted.

Required minimal repair: verify the actual normative files against their prospectively frozen expected identities before parsing/importing scientific policy or making a scientific stage accessible, and recheck at the production prefit gate. Do not merely hash BOOTSTRAP without following its entries. Add mismatch/missing-file regressions for the normative files, including a fresh-process check that refusal occurs before policy parsing or A construction/optimization/source access. Preserve every original scientific value and threshold; this is identity enforcement, not a new authority system.

## P1-03 — S04 omits the required missing-running panel

Locations: paper16_development_r2/controller.py:251–255; paper16_m1/controls.json:54–62.

Normative S04 operator explicitly requires reporting missing/available panels using fixed fitted states and identical within-pair targets, with D/S filtering limited to observed past counts. The current code saves only effects for `~batch.running_missing`, plus available-case coverage. It never saves the complementary missing-only panel. The overall primary mixture is not a substitute for the missing subgroup.

Required minimal repair: within the same one-shot E batch, derive both complementary masks from the frozen running-missing indicator and primary score support; report fixed-model scores/effects and bin/unit-bin/exposure denominators for both. Preserve existing available-case coverage gates and causal filtering; no refit, new model or second E is allowed. If the missing mask is empty, emit explicit empty/no-missing status and zero denominator rather than an invented effect. Add all-available, mixed and all-missing synthetic cases and verify that the two panel denominators reconcile to primary support. This restores the registered output rather than adding a hypothesis or changing a coverage threshold.

## P1-04 — Source metadata and integrity certificates are loaded without their expected identity checks

Locations: paper16_development_r2/source.py:32–34,134–145; paper16_dev_r3/run_m2.py:76–95; paper16_running_r2/run_sources.py:138–149; paper16_development_r2/SOURCE_PINS.json.

Observed: source.metadata validates the registered source object and returns source_inputs unchanged. The reused utility calculates current metadata hashes and returns them, but the new adapter does not compare them with the frozen result's source_metadata_pins. It loads DERIVED_RUNNING.npz before comparing it with the frozen running result's derived_bundle. native_role parses QC and result JSON directly without first checking their bytes against record['QC'] and record['result']. The 22 global pins bind the account containing those expected references but do not transitively verify the referenced files. Further metadata inputs used by the adapter—roster index, native headers/probes and imported roster invalid-time logic—also need their existing frozen identities verified before use. A changed expected certificate could otherwise redefine native geometry/full-row hashes rather than being refused.

Independent synthetic witness: patched only the adapter's source_inputs return to fabricated metadata path and zero digests, while retaining an actual registered Development source record. source.metadata accepted that return unchanged. No actual metadata or record was modified and no arrays or sources were opened. Separately, all 135 checked current saved file hashes match, so this is an enforcement defect rather than evidence of corruption.

Required minimal repair: before reading/using record-linked certificates or arrays, verify the referenced QC/result bytes against the frozen account; verify metadata JSON/NPZ against that result's source_metadata_pins; bind the running RESULT to its frozen expected identity and verify its derived bundle before decoding; close the concrete metadata/import dependency chain used by this adapter against existing BASE/frozen manifests. Compare actual current values with frozen expected digests rather than accepting newly calculated digests as evidence. Keep existing source allowlists, native decoding scope and role masks unchanged. Add synthetic missing/corrupted QC/result/metadata/running/dependency tests that stop before decode, features or HTTP; preserve valid saved-input and native synthetic paths. No historical source file or scientific definition must change.

## Other requested checks and limits

The implementation correctly separates A physiology from the scored-window rates used by S07. S07 ranks the original common-A 100–220 ms count/exposure rates by ascending rate then numeric Unit ID, takes ranks 2–5, and records that ranking separately from canonical ascending Unit-ID parameter/RNG packing. It does not replace the main eight units. N4 implements the registered 11 raw-column maps before applying the same frozen scaler; color flip changes PSTH and raw color×running interaction, time rotation changes only the six PSTH positions, and previous-color/repetition/raw-running/targets/masks/coefficients remain fixed.

S05 prefit UNAVAILABLE is supported by the lack of a frozen verified pupil exposure-end certificate in the authorized input contract. The source evidence establishes no verified timing certificate, not absence of pupil signals or arousal. The positive feature branch is tested synthetically. This is an original optional timing/availability condition, not an exception manufactured after a numerical failure, and does not justify replacing any mandatory fit. No new pupil source or Final inspection is required for this review.

Reviewed the production math against the bound equations: identical objective/vector for analytic, independent AD and all fixed FD scales; h=1e−5 alone controls frozen FD acceptance; initialization/mid-accepted/endpoint checkpoints; outward-bound projected gradient; bound-aware packing; original regularization/normalization. D/S scoring is a separate forward-only joint predictive likelihood, conditioned on permitted observed past targets, not a backward smoother. Independent synthetic oracle tests pass for these surfaces, subject to the feature and identity defects above. This does not predict real numerical convergence.

The intended sequencing is explicit: approved M3 then all A features/panel availability and exact task plan before scaling/fits; all 648 main B1 grid fits certified before B access; B1-only B selection and the frozen global lambda/tie rule; every remaining mandatory main/panel fit and all three D/S seeds before full M4 state sealing; unique E claim before its first neural access. Full-state completeness includes coefficients, all seeds, scaler/active/unit/mask states, endpoints, coordinate certificates and external journals. Refit panels use only registered B1/B4/C/D/S and applicable contrasts; adding panel B2/B3 fits would exceed the frozen model definition. Fixed panels retain all required applicable main scores. No mandatory model may be removed or relabeled UNAVAILABLE on numerical failure.

External broker checks are before pair 6001 / accepted iteration 1501; full native Job supervision binds the original boot/UTC/monotonic 48-hour stage and descendants, with no restart entitlement. The task plan caps current Development optimizer attempts at 7506, retains Final reserve 7722 and full-study cap 16178; actual available-panel allocation is frozen before fitting. No unused Final budget is borrowed. Transport is cache-first, registered Development only, bounded new-range reservations, exact ETag/206/range, no retry/redirect fallback. Source/raw and Final restrictions remain substantive; the metadata identity defect must be repaired before relying on those later source checks.

N1–N4 preserve their frozen operators and descriptive/reference interpretation; no unstable P13 conditional Poisson generator is imported. N2's primary-bin invariance is distinguished from possible C changes, N3 preserves full-flash per-unit counts, and N4 is a wrong-context reference without manufactured p-values. Development exploratory intervals are not a Final sign-flip/Holm/leave-one-mouse-out PASS; Final-specific positive-claim and coverage gates remain unexecuted. Saved-only reproduction is separate from fresh numerical execution and cannot clear any fit that failed its original gates.

## Required next action

Preserve this failed review, the 28-payload candidate and its 26-test certificate as immutable attempt-1 evidence. Repair only the four demonstrated implementation/identity/output defects; freeze a revised candidate, rerun the affected regressions and full native production synthetic certification for that candidate, and obtain independent production prefit re-review. Keep real A features/scalers/fits, B/E neural access and Final stopped until actual new acceptance. No owner clarification or scientific threshold amendment is required by these four findings.

## Exact reviewed identities

All paths below are repository-relative. Sizes and SHA256 values were independently checked against current bytes immediately before writing this report. The manifest covers all 28 payloads; this review is separately hash-bound after writing and is not recursively included.

| Path | Bytes | SHA256 |
|---|---:|---|
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/goldenstandards.md | 2519 | 35a37c6106d45c6bdef85422a32005598189bc599ac7589f8db7e9130298ed3e |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/M3_FINAL_SYNTHETIC/CODE_HASHES.json | 1302 | 3c6568f9fe798212fd8c57b62a8a44ce861bfe05c2668df698c6e64740ea1ca4 |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/M3_FINAL_SYNTHETIC/RESULT.json | 1762 | 237cda46aca13a8322f350f56049bad249be4e79ce5f029759d114d345f577b0 |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/M3_FINAL_SYNTHETIC/STAGE.json | 255 | 9202a2f1cc8775ea76702f6e9d29ab0855c5eb818e16ad52c0eb2e7115e7f494 |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/M3_FINAL_SYNTHETIC/SUPERVISION.json | 244 | 1337586bf9fe39bb1a0baef1e64adbc766ce4d2a76686267943b7dbd30f6e1c0 |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/M3_FINAL_SYNTHETIC/TESTS.log | 4892 | 707fdb88269c7eb86889b3ca0393d9335c024abbd4916714768a7204f513c822 |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/OWNER_REQUEST.txt | 17134 | 671b169ea0e5c0d2533ae95026736143b429c0548a6748a7466021f55c3373bd |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2/REQUIREMENT_BASELINE.json | 52111 | 2b88affd2bf27366d2aa41c4fd91563790b5a12f6b78c1961dd04abe1a5b2ab4 |
| paper16_development_r2/.gitignore | 25 | 16efb1aafab2d99d1dfee53e728010380484ce4c3ef3e5980bb1ba5f4aaa3533 |
| paper16_development_r2/ACCESS_REGISTRATION.json | 51742 | 2ce10636604311e55063fa32bda48df0a1cec7b6904cae31cb71d7858a846a1e |
| paper16_development_r2/BOOTSTRAP.json | 3747 | 7fe3f161a61ac4d42a4b51313e4a5a0a6434a97b743c9e35282efe7057f140ac |
| paper16_development_r2/certify.py | 3239 | 11084a909993b04e7eb322e44baab0bfe7272a9ed24bf6f7c5409e311c3af62c |
| paper16_development_r2/controller.py | 25707 | 65551f7fb50b06ff10d9ce215240fdacee98c29a8f6adff6d0687f59ed358277 |
| paper16_development_r2/controls.py | 6779 | 7158115c35de82d5ba254a4002ccc08a839f2eff34acf9e7445a44d2b299be01 |
| paper16_development_r2/core.py | 2271 | 146732e7efb00c4731eb4847d0d188264f1add205cbad7f53dca858c89f98f2e |
| paper16_development_r2/features.py | 6066 | c8a178c104ddee6b14c1286aa4be4301a5088f309e88969c7cc8cb135c7137ff |
| paper16_development_r2/IMPLEMENTATION_POLICY.md | 4986 | 0b9588d1c3490cf7dea2420e43996986fd34b8c8660b7e5b59e80d0d8a215485 |
| paper16_development_r2/MISSION_SPEC.json | 937 | 6fe5cd53478ae7a5c905ae1f40ff652e6a078add0dfcebef0388728973f76a70 |
| paper16_development_r2/models.py | 4752 | e13e5feff0b4101ddc27cb5dd0177760b8a6b787a8abf6f026b2bacfc9dd7869 |
| paper16_development_r2/optim_child.py | 1117 | e6993643323d224391b54fda3a686068ba160457ad651ecb05e25cea74e0ba24 |
| paper16_development_r2/optimizer.py | 7817 | 5441398d633159d613c608d5d8656267ce6b43e3fe5983a4cd4ca61e1fd3228c |
| paper16_development_r2/panels.py | 5173 | dc91d666f18435a751d6a3d4ce7a8a9719c5d90e52bf59b3a105e2062883dada |
| paper16_development_r2/PRODUCTION_NUMERICAL_CERTIFICATION.json | 2453 | 0f6a4a6cecf90f6e91dddf4646427d0ee2ecaf7ce8e6715a8b71ad8758fcfe7f |
| paper16_development_r2/reproduce.py | 9189 | 678e8f017101d06f135c049bb0b860a0d40d2a37d25b6c5d407bd9c38e0ff8ce |
| paper16_development_r2/REPRODUCE_SAVED.ps1 | 515 | 2e57cca7323005b9ec57c6ac385d31c358e55060b2db01d9e5014585bc73347c |
| paper16_development_r2/source.py | 12928 | f0feb9cf9b9b4ad62029575cce9ffb0168e307b4a47d10fff1a3ddc525286b4d |
| paper16_development_r2/SOURCE_PINS.json | 2505 | d586710057ef59cd8a0742b4b8ae679b83470654dd3f31c34035ebecde9926ef |
| paper16_development_r2/test_production.py | 24334 | 89ccfc345eb9ea0af8c9aa112a216abb215430e367c992c3c92be549f804ff52 |
| paper16_development_r2/PREFIT_FREEZE_MANIFEST.json | 5384 | a5bdcdac32b3cc8f291eec1e1b792d420e811158bb47fae9c5cce57349aa280e |

The following 13 current normative identities were additionally independently checked; runtime enforcement is still absent as described in P1-02.

| Path | Bytes | SHA256 |
|---|---:|---|
| paper16_m1/M1_SCIENTIFIC_PROTOCOL.md | 4442 | 26e208f18bc68f970ea5ffc04e554419115cfd1456fb77a1ccd51c1dd5aff5f3 |
| paper16_m1/protocol.json | 20009 | 36d074bdf8af121346d444a1f3b2eaf0b235c1327e88701d33863ad6c7f85746 |
| paper16_m1/FEATURE_AND_MODEL_EQUATIONS.md | 7401 | c77bae6b9e221431c677633bb9502a85149dc977918eed01fd58b5c994d0fccc |
| paper16_m1/NUMERICAL_POLICY.json | 5591 | 9409657df46117ef20cfbde078898aa5346d448b974a5e86f3997238d07b49b8 |
| paper16_m1/SOURCE_OBSERVATION_QC.md | 4202 | 0fdb5e57a0b1e7de1559704b1926d42c1a099cab5534fb8dd6f43d6183f83214 |
| paper16_m1/STIMULUS_CONTRACT.md | 4247 | cc00f9cda6f9ef95a0b5c3e2a3c30817e031b54f0b0f6673dbcc85b0b0db0b99 |
| paper16_m1/STATISTICAL_ANALYSIS_PLAN.md | 5439 | 31172581801620e73ff7b34ed7fb2492ec53ee5aedb0d9c13a7e88f626ef6669 |
| paper16_m1/BO_FC_TRANSPORT_PLAN.md | 1990 | 9b28c54749013731496e40b1a69d7bf9761d9bfc377829d5125b6a5f0593f9c1 |
| paper16_m1/FALSIFICATION_AND_SENSITIVITY_PLAN.md | 3703 | 7ed3dee978efdc28e831d6e03557e44b4634771d4b52d78ef0148437e40ac42b |
| paper16_m1/controls.json | 13296 | 5ea6b238ad854e7cbff62985a2a79aa36cc7d9957056f4cd7c435df7ce5961a7 |
| paper16_m1/EVALUATION_BOUNDARY.md | 3244 | de51ccd7b88fbc5cf48404a637cfd3858dcdaf844440077d4367b1ce3c0a79c8 |
| paper16_m1/FROZEN_COHORT.csv | 14839 | b6c875e4eaae2392de0c1b4c1def04175dc16e45a0f128474966460c6380937c |
| paper16_m1/M1_FREEZE_MANIFEST.json | 63973 | a9e787ae990fda13eb0b1899b9dd2d7e57c039c7b33f6630f3729fd27c19cab6 |

review_scope = independent production prefit implementation/scientific audit only

real_scientific_execution_authorized_by_this_review = false

Final_access_authorized = false
