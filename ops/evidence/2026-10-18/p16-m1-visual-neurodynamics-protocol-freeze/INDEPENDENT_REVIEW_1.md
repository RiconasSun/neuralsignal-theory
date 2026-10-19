# Independent internal P16 M1 review 1

Decision: **REPAIR_REQUIRED**. **open_P0 = 0; open_P1 = 5**.

Mission: P16-M1-VISUAL-NEURODYNAMICS-PROTOCOL-FREEZE. BASE: 2adb11a9fcd05cf1ea3cb4e120b5102400d6bb84. Candidate manifest SHA256: c86c7e97b1893322189dc64ab46be0a186d05e899f5ec6989622cec44387eb9b.

This complete internal review covers the exact owner request, all 469 frozen baseline rows, all 37 acceptance groups, every scientific document/JSON policy, the 55-row cohort, specification code/tests and saved reproduction. It is not external peer review or independent-laboratory replication. No candidate implementation or test was edited. Only this report was written. The five prospective specification/reproduction defects below must be corrected before M1 is called independently reviewed and frozen. They require no neural data or model-outcome access.

## P1-01 — the saved verifier accepts an empty manifest

**Location:** paper16_m1/code/verify.py:9–15; related test paper16_m1/code/extra_tests.py:19.

`validate_manifest` loops over supplied rows without enforcing a nonempty, unique, safe and complete expected set. `checks` therefore continues when the manifest file list is empty. I verified this against the entire checker with an in-memory substitution of only `files=[]`: it exited successfully and printed `saved_hashes: 0`, cohort55, native_metadata_pilots2, planning_scenarios100 and historical_paths_preserved36252. The checker can claim success after certifying no frozen payload. The existing regression checks a changed/missing file for a supplied row, which does not cover omission of the row or whole set.

**Required correction:** bind an explicit expected scientific payload/source-reference set to the trusted versioned candidate; require exact membership, uniqueness, normalized safe repository-relative paths and hashes/declared bytes as applicable, with narrowly defined self/work/closure exclusions. Do not let the manifest itself redefine the required denominator. Add regressions for empty, omitted, duplicate, unexpected and escaping entries. This is ordinary archive completeness, not a new cryptographic custody system. Preserve this unsuccessful review and the old candidate before repair.

## P1-02 — B0 fitting and B1 initialization have two plausible A/C rate domains

**Location:** paper16_m1/FEATURE_AND_MODEL_EQUATIONS.md:5,11; paper16_m1/NUMERICAL_POLICY.json:9,20; contrast with paper16_m1/SOURCE_OBSERVATION_QC.md:7.

The objective uses scored late-flash rows [100,220) ms, while physiological QC explicitly uses [0,220) ms. “analytic A/C MLE log(total count/total exposure)” and “log A/C mean rate” do not identify which domain provides B0's fit and all initial PSTH values. These yield different frozen parameters and initialization. A purely hypothetical ten-presentation example with 90 early and 10 scored spikes gives 100/2.2 =45.4545 Hz for the QC domain versus 10/1.2 =8.3333 Hz for scored rows. This is a specification ambiguity, not a measured P16 difference.

**Required correction:** state one exact role/unit/mask/count/exposure formula for B0 and initial PSTH values in both normative files. If the intended model-training domain is A/C valid registered scored rows, name that explicitly and distinguish it from physiological-QC rate windows. Freeze zero-count/bound treatment consistently. Add a synthetic fixture in which early and late rates differ so that the intended formula is verified before a future worker exists.

## P1-03 — valid-presentation coverage is not operationally defined for all PSTH cells

**Location:** paper16_m1/protocol.json:83–110; paper16_m1/STIMULUS_CONTRACT.md:11; paper16_m1/SOURCE_OBSERVATION_QC.md:3,7.

The per-role/per-color minima count “valid presentations”, but the support rule is defined per score bin using [onset,bin_end). It is not explicit whether a presentation must support all six scored bins and the shared history window, or whether one supported bin is sufficient. The latter interpretation can satisfy a presentation-count floor while leaving a mandatory unpenalized color×time PSTH column with no A/C observations. Preserving all12 PSTH slots and checking PG does not detect this: in a small synthetic X with an unobserved PSTH column5, moving that coefficient from0 to5 changes the objective by exactly0 and its gradient is exactly0.

**Required correction:** define main valid-presentation admission and role/color coverage using an unambiguous support condition. For example, all six bins plus the entire onset..220-ms shared selected-unit interval must be valid, or explicitly require each condition×time training/calibration cell to meet the registered coverage. Resolve the masks, history support, minimum denominators and relevant sensitivity differences consistently. Add a known-invalid late-bin counterexample that cannot pass via earlier bins. This prevents a weak/unidentified B1 and is not permission for outcome-driven threshold changes.

## P1-04 — positive classification is insufficiently fixed for secondary contrasts

**Location:** paper16_m1/STATISTICAL_ANALYSIS_PLAN.md:9; paper16_m1/protocol.json:207–210.

The primary positive category has exact meaningful-effect/interval-width/LOMO/robustness conditions. For B4−B3 and B4−B2, the text only requires their “own Holm/mean/CI/direction evidence” and calls primary guards “joint context”. It does not settle whether each secondary must also meet .002, .004, its own LOMO positivity, and whether the primary sensitivities/N1 are a prerequisite or merely reported context. The JSON uses a generic positive_category while naming a maximum_primary CI width. Both interpretations can change the labels after results.

**Required correction:** register a three-contrast classification table, with explicit per-contrast mean, adjusted-p, interval/precision, LOMO, coverage and joint-reference/sensitivity prerequisites, together with deterministic required-gate/fallback/negative/mixed classifications. Either scientifically justified secondary rule can be chosen prospectively now; no P16 outcome exists. Keep the secondary attribution observational and never infer connectivity/mechanism or call the results VALIDATED.

## P1-05 — the documented one-command PowerShell example is broken

**Location:** paper16_m1/README.md:9–12.

The code block contains a literal carriage return inside the path, producing `& .\paper16_m1` followed by `eproduce.ps1` on another rendered line. It cannot be copied and executed as the promised command. Inspection of raw bytes confirms the escape error. The actual file exists and executes correctly when its full path is supplied.

**Required correction:** preserve a literal backslash and present the runnable command `& .\paper16_m1\reproduce.ps1`. Check the rendered/raw code block and a minimal literal-command regression; do not change the actual PowerShell/runtime oracle merely to fix this documentation defect.

## Independent verification and scientific assessment

I independently executed `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\paper16_m1\reproduce.ps1`. Actual exit0; all23 synthetic tests passed. The command verified the current44 supplied hashes,55 cohort identities, two stimulus-only native bitwise tables,100 hypothetical scenarios and36252 historical paths. This successful run is real saved/specification evidence, but does not cure the empty-set counterexample or the scientific ambiguities above. No real NWB was reopened, no new neural array, actual model fit, prediction/likelihood, Final C/D or network data was accessed. The small synthetic optimizer is authorized specification evidence, not a real-data fit. The independent empty-manifest probe explicitly denied network and any NWB open, patched decoded data only in memory and did not modify real files.

Every currently listed manifest hash matches, and the stated manifest SHA matches this candidate. All464 original owner-line requirements match their exact source_line text and owner SHA; five explicit closure obligations account for469. The37 semantic acceptance groups correctly distinguish specification, pending source/production work and actual future transport. I independently compared every FROZEN_COHORT row's mouse/session/probe/role/protocol, sex/genotype, metadata unit count, historical flag, pilot/native-table flag and source-header digest with saved M0 identity/metadata; all55 agree. No reroll or replacement was found. The source header/metadata review is not neural access.

The nominal-flash primary is defensible within the disclosed scope. Both original Development pilots have150 flashes,75/category, compatible late-window timing and the same source scalar conditions; full native tables remain verified only2/55, despite family-name presence55/55. No new55-object source rescue is required for M1: a precise pending-native gate is legitimate. Grating phase/physical display equivalence is not invented. Contrast .8 and nominal±1 remain source categories, not equal radiometry. The two HDF5 metadata extractions have an explicit prospective dataset allowlist and sourcefile identity plan; the saved reader code targets only identifier and stimulus fields, not units/spikes. Reading raw container bytes for the preregistered source checksum is distinct from neural-array decoding. The review did not run that extraction.

The causal running choice addresses the independently identified source problem: processed velocity's whole-session median normalization is excluded; same-row net_rotation/actual parent duration is allowed only after the parent end, with frozen age/duration/invalidity and missingness rules. Missing source near-zero rows are not reconstructed as stationary behavior. Raw dx unit-label ambiguity is not silently converted to cm/s. Pupil is optional and fails unavailable if exposure availability cannot be established. Measured running/pupil never claims all movement/arousal control. Real native mapping, units, coverage and source generation must still be verified by a separately authorized worker.

The anchored20-ms grid,100-ms within-flash neural history, strict event<t, half-open targets and presentation resets are coherent. Three disjoint own/population lags exclude the target from population history. Poisson exposure/logfactorial, shared A/C scalers and active maps, zero-added-feature nesting, outward PG and independent dual AD/frozen FD scan are mathematically consistent in their synthetic scope. Bound-derived eta maxima150/182 are finite without prediction clipping. Registered maximum parameter counts and the9248 optimizer-attempt budget are arithmetically consistent. Actual production code must enforce all declared bounds/call/iteration/time certificates; scipy maxfun or a success flag alone is not a future worker certificate. Mandatory numerical failure must not be silently converted to an optional-panel coverage absence.

Development B-only global model selection uses the fixed BO/FC balanced weighting and B1 scores, not a favorable B4 increment; E is not a tuning source. All Final candidates are BO, Development5BO/23FC. The protocol-distribution shift and source/batch/genotype/sex dependence are disclosed. Equal-mouse inference, Holm3, explicit sign-symmetry/bootstrap assumptions, hypothetical rather than empirical power/precision planning, and a wholly descriptive/exploratory scientific track are appropriate. The100 scenarios are not actual sign-flip power or P16 variance. Twelve-mouse main and6–11 descriptive fallback retain their distinct coverage consequences and no positive fallback label. A significant result cannot become VALIDATED.

All12 sensitivity families and four finite operators have scientific purpose, preservation/destruction/assumption/coverage and failure language. N1 is explicitly an approximate descriptive donor reference, N3 destroys stimulus alignment and is not an exact conditional null, N2 is a count-resolution invariant, and N4 a deterministic nuisance stress test. No recursive Poisson generator or favorable redraw was found. Optional coverage cannot be called a successful control; finite arrays are not null validity. D/C/S are prospectively excluded from real fitting and their forward/IID/state examples do not establish production or temporal-state evidence.

The original VISp7-acronym allowlist is available in the manifest-bound M0 FEASIBILITY_REGISTRATION and no authorized anatomical expansion is present. For the repair clarification, explicitly name the inherited main candidate qualified_unit_ids and same allowlist for S11; a probe containing VISp does not make every unit on that probe VISp. This is an authoritative inherited-boundary clarification, not an extra independent scientific amendment or a sixth finding.

## Acceptance boundary and next action

The present M1_FROZEN_PENDING_NATIVE_STIMULUS_QC / Prompt3=false status is correct: M1 specification review is separate from unexecuted full-cohort native stimulus/running/support/physiological admissions and separately certified production code. No further neural data are needed to complete the five repairs. Retain the exact rejected candidate, this report and all previous failures, make the prospective definition/reproduction corrections, refreeze and run the focused/saved checks before independent rereview.

Actual origin/test commit, all-changed-blob remote readback, clean checks and literal STOP remain future executed gates. This review does not approve scientific execution, Final access, a main push, a future commit or claim M1/M2 production/scientific PASS. No external reviewer/lab is claimed. Reviewer writes are COMPLETE for this round; parent may now return to the bounded repair loop.

## Reviewed identity map

- `paper16_m1/.gitignore`: `16efb1aafab2d99d1dfee53e728010380484ce4c3ef3e5980bb1ba5f4aaa3533`
- `paper16_m1/A1_A10_PROSPECTIVE_CLAIM_AUDIT.md`: `0e48148279df8bfa1510cfc6fe7861a0044ed5d7abe6534870c16d40e576988e`
- `paper16_m1/BO_FC_TRANSPORT_PLAN.md`: `7d12837c02a88ca131ed3f2e20906549c5785a410669850f258146eed423c184`
- `paper16_m1/code/extra_tests.py`: `26f99c1f4e28f8a601749d1ae335f00efb208cad2d3251efe1d6965590970b2d`
- `paper16_m1/code/planning.py`: `720bc1fbb6bb516bfe874fbf6f2cf6af2adcd11a61d75bd6eb88374fbe1ca204`
- `paper16_m1/code/spec.py`: `7ca31f4e7421cc11f9a2a3028951045436e890d4cf8592b649690e31f28be7b3`
- `paper16_m1/code/stimulus_metadata.py`: `8a45738aeb026ad02bf21f2970e1e8e51aff4e8750067e617ce4b1d812654976`
- `paper16_m1/code/test_spec.py`: `7158739c0d2d0c344717965210ef3213e4010dea677188aa1358aec3b60dd118`
- `paper16_m1/code/verify.py`: `d65a2b9a04a12ac4bf24d0ee2259528f0e9ba0e1344eb01b97fa5bd1093e2bd5`
- `paper16_m1/controls.json`: `7974a714181d3a42e47e2ad7c3c63fd0f64a5c5a524fd8af1528f0dbea5260d7`
- `paper16_m1/EVALUATION_BOUNDARY.md`: `9a34f3e6fac88b816258f6f4d05ea5552d1c650a243f2a91aea52489a913fbc5`
- `paper16_m1/FALSIFICATION_AND_SENSITIVITY_PLAN.md`: `73a7f9b097955371edbafe2368e7938972a5650fa39327e4b801163b17294f6d`
- `paper16_m1/FEATURE_AND_MODEL_EQUATIONS.md`: `e3c913873e6f1b47a2e01e4306859bd59e6b2dc51c71eaa620068ce3f8c8e5fc`
- `paper16_m1/FROZEN_COHORT.csv`: `3eef8e3fa9dda4f23855a27f46f074d5f9728ff55652c923531641f34ef333a9`
- `paper16_m1/M1_SCIENTIFIC_PROTOCOL.md`: `e9dc0dfb14bb59b4432fbb902fc6f69f2a7aace854d08095d97ed5fa5680f7ab`
- `paper16_m1/metadata/FLASH_NATIVE_760345702.json`: `6b75795ee61e34033bf2cb8ab01054bd0b34cd336148e5b3fd31d02512f061b3`
- `paper16_m1/metadata/FLASH_NATIVE_760345702.npz`: `26675be0e3e25fdfd11bdbcbcbf5d76a891ff53957a2b910565d423c9cfe9978`
- `paper16_m1/metadata/FLASH_NATIVE_829720705.json`: `8c69ec3bbfd50c0989e133bdae74b792f053c55fae232e39b5aed77dd4a422b7`
- `paper16_m1/metadata/FLASH_NATIVE_829720705.npz`: `f1702998efb3c0e31b67a83fae9613b9c6f0c90fa20843d90da06d61462cb439`
- `paper16_m1/metadata/flashes.json`: `a4488ee67d96dff0a6d36b703329814ba3e0820ca3f486cbfb5a1f4feb39039a`
- `paper16_m1/metadata/flashes.py.source`: `94cde65da1c3856c23d4b7f15f600a8ae8325854174b826d00a29f55645752f1`
- `paper16_m1/metadata/nwb_writer.json`: `99c6d52b9ba1c953678ebd15ab4396939a2226e6ad19062487bde1f78e7efe07`
- `paper16_m1/metadata/nwb_writer.py.source`: `eaa99cc3149379075d02c09fa88a6f40a9151c5a5966ac371e2ee3888be83dbf`
- `paper16_m1/metadata/running_extract.json`: `c74ee317a65fb67b32a42ccdaf17080a12192324d5044a9e37a22590565813b8`
- `paper16_m1/metadata/running_extract.py.source`: `73e59cbbaaf8a6619f04d470a689c2037ccbebb20cc727cb1e6bd096287ee731`
- `paper16_m1/metadata/running_schema.json`: `97d8b4b004149f09a4ba696d88d327de717d6caeb0b5b22f25962d1bf9cc507f`
- `paper16_m1/metadata/running_schema.py.source`: `9c522f9fc621e7db7c41f25ef06ba04f34c5689280c6fa6bd0e91085be1c5a8b`
- `paper16_m1/metadata/SDK_LICENSE.txt`: `0f69bc05c13b866a357469e9058c15d5d679d48e4e6a63b3d507d965bb240955`
- `paper16_m1/NUMERICAL_POLICY.json`: `06c4553cd2afdb34a130c145ab4a51d3eb24f9758730e4195d4888ed6c8f6f11`
- `paper16_m1/PRECISION_POWER_SCENARIOS.csv`: `0d2c8546b2f89252b5807d88130e7907fac86e211dcce3ebcc67d4915d86077a`
- `paper16_m1/protocol.json`: `c34144181c49798c8b1297a063a194ba3facfdf28d1edba2fdb71e223d82ca0b`
- `paper16_m1/README.md`: `1a56ee8a3944d42d97d2e97457f35e6534410d1af5ca44c234d75a6b658a96dc`
- `paper16_m1/reproduce.ps1`: `d9f3a8a00c39f7776f0ea2abf5ad1ccb3ef197ff998d6ece55cbed9860a81e44`
- `paper16_m1/requirements.txt`: `abaa4f4f418884388ac3c5a6a1dfb641c5ce6c3b46225347e05939cab643a700`
- `paper16_m1/SOURCE_OBSERVATION_QC.md`: `61e466310e85b5f2525ccaf81b4801932cd4cce3c43ef133996e8b1bc0141eda`
- `paper16_m1/STATISTICAL_ANALYSIS_PLAN.md`: `2050feff29810d52cb5da7f8b1ff1aed5d47730e5f1b72e17d3b5ebf97f21c79`
- `paper16_m1/STIMULUS_CONTRACT.md`: `283ba7325700bdd8e33a527353384b82a26a6cf40b8042ce8add25f8f070e709`
- `paper16_m0/P16_M0_REPORT.md`: `5beee84c0a987408b12060bbe180a00f6e6ed8214f3deb4c26a089fb50784e06`
- `paper16_m0/M1_SCIENTIFIC_HANDOFF.md`: `a532a1da2bc065e4fefd17f4875db150069935f2c055f734ecb26ca2b18748c6`
- `paper16_m0/FEASIBILITY_REGISTRATION.json`: `fc0475a5bdef84ac94b2ead49e5103f11cdae763885eaf3d91a2e1360c5b421d`
- `paper16_m0/SOURCE_COMPATIBILITY.md`: `6d7ab6e0a63cfb05e4bcd79af8622c42d2f9dd82bef8d8747fc07d28b1eb4260`
- `paper16_m0/SPIKE_STIMULUS_BEHAVIOR_ALIGNMENT.md`: `8210e22a5f722e615639da77e9bb2f59731acfbd1cab1795d1bfabf99c3c740d`
- `paper16_m0/results/ROLE_ALLOCATION.json`: `463ed226d1f8c385934f1c7cda87481d5465702592c54d9e7e162fe14e50fb9a`
- `paper16_m0/results/COMMON_GRATING_PARAMETER_SUPPORT.json`: `6d3891b27e8f2bbed17f8b6ef9dcacd1064ba1af1d69a6420c6af45db325c833`
- `paper16_m1/M1_FREEZE_MANIFEST.json`: `c86c7e97b1893322189dc64ab46be0a186d05e899f5ec6989622cec44387eb9b`
- `ops/evidence/2026-10-18/p16-m1-visual-neurodynamics-protocol-freeze/OWNER_REQUEST.txt`: `456c687231a27dc8f8cd450c11f586e9e4c21262bd427eee69c20d55c30cd050`
- `ops/evidence/2026-10-18/p16-m1-visual-neurodynamics-protocol-freeze/baseline.json`: `ab4511618956eeaebdf072f0646601e03efdeb5fea0eca9f63746cb27b4e928e`
- `ops/evidence/2026-10-18/p16-m1-visual-neurodynamics-protocol-freeze/ATOMIC_ACCEPTANCE.csv`: `e6fa2aded657dc69e042e8754016888244553cdaa0df4a90c39db89e99462bae`
- `ops/evidence/2026-10-18/p16-m1-visual-neurodynamics-protocol-freeze/REQUIREMENT_TRACE.csv`: `558650129fb065eb8e42e747ed0ab56228da45375095953cdc090a8b459cf64f`
- `ops/evidence/2026-10-18/p16-m1-visual-neurodynamics-protocol-freeze/LOCAL_STIMULUS_METADATA_ACCESS_PLAN.json`: `0297c544167a5144e06e1e69c0bf261d8e310fc95d87177c178565104fb774a7`
- `ops/evidence/2026-10-18/p16-m1-visual-neurodynamics-protocol-freeze/REPAIR_HISTORY.md`: `05ec5f8c674678cd13a2b48d091df642aa0fbb8a105e50363ad299c7edff53af`
- `ops/evidence/2026-10-18/p16-m1-visual-neurodynamics-protocol-freeze/TEST_ORACLE_CORRECTION.md`: `095a465bf9502ce0995fde6e0db129a0324afe1827747427c9d5fb45a8d679cf`
- `ops/evidence/2026-10-18/p16-m1-visual-neurodynamics-protocol-freeze/SAVED_REPRODUCTION_4.log`: `88f4c29981e1ae7dbe21b61aa533ae6dbf4dbb19856ce916151b1e89ea2bcec1`
