# Independent static scientific-contract audit 1

MISSION: P16-M3-M5-FROZEN-DEVELOPMENT-R1
Reviewer: /root/r4_policy_review, independent internal scientific-contract review
Timestamp UTC: 2026-10-20T01:52:21.302003+00:00
Required BASE (owner): ed2b52f5ba7a21ed870911e135c194c253b473ab
Decision: CONTRACT_CLARIFICATION_REQUIRED_BEFORE_COMPLETE_PRODUCTION_FREEZE
open_P0: 0
open_P1: 2

## Scope and preservation

Read the complete current owner request, all13 normative M1 files listed in its section2, relevant frozen synthetic feature oracle and accepted M1 independent review2. Verified the12 substantive normative files against the334-entry M1 manifest and bound exact hashes below; did not open neural arrays, acquire a source, fit a model, compute real features/scalers/likelihoods, access B/E or Final outcomes, mutate Git or alter any historical evidence. Only this review is written. This is a static contract audit, not M3 production certification or a rerun of M1/R4. The accepted historical M1 freeze and R4 source PASS remain intact; the findings concern choices needed to implement a complete new production protocol without inventing scientific intent.

No material narrative-versus-machine mathematical contradiction was found in the inspected objectives, models, source/QC, numerical gates, role cuts, ridge selection or inference. Two narrower operators remain materially underspecified: the S07 rate domain and N4 affected feature columns. Both can change scientific panel/control results even while staying A-only and leaving fitted coefficients untouched. Routine array layout, scheduling, serialization and reversible implementation choices are not findings. No unrelated custody/security/cryptography work is requested.

## P1-01: S07 does not identify which of two already defined A/C rate domains ranks the main8

Exact references:

- controls.json:104-117, specifically line106: Use A/C rate-ranked main8 middle4, positions2..5, tie unitID; no rate window, numerator/exposure or mask is named.
- FALSIFICATION_AND_SENSITIVITY_PLAN.md:5 repeats A/C rate-middle4 and forbids D-based rate selection, but does not define the rate domain.
- SOURCE_OBSERVATION_QC.md:9 and protocol.json physiological_QC count_window define A/C physiology over supported [onset,onset+.22) windows.
- SOURCE_OBSERVATION_QC.md:11, NUMERICAL_POLICY.json:22 and76, FEATURE_AND_MODEL_EQUATIONS.md:5 and19, and protocol.json features.B0_and_initialization_rate_domain separately define B0/initialization rates on [100,220)ms scored rows. Their scope explicitly concerns B0 and coefficient initializers, not S07.
- The owner request:429 and437 requires S07 with its exact frozen operator, and section2/line111 rejects choosing a materially favorable interpretation.

At least two scientifically distinct constructions remain compatible with the words A/C rate-ranked: (A) use the saved A/C physiology rate, counts/exposure over [0,220)ms on the original supported QC windows; (B) compute the rate on the registered main common A/C scored rows [100,220)ms. Main8 membership is fixed in both, but their middle4 need not coincide: early-heavy and late-heavy units can reverse rank under these windows. This is a unit-population sensitivity choice, not a harmless optimization or storage detail. The terms middle4 and positions2..5 themselves are resolvable as zero-based sorted ranks2,3,4,5 with unit-ID ties; no extra ambiguity is asserted there.

The source text does not explicitly link S07 to either existing rate definition, and the synthetic oracle has no S07 implementation establishing one. The historical M1 review2:49/52 acknowledges A/C-only ranking and all panels but supplies no missing rate-domain definition. Therefore this review cannot certify either choice as uniquely frozen. Minimum prospective owner decision: specify S07 numerator/exposure window and A/C support mask by explicitly adopting one of the already-defined domains above (or providing another exact authorized definition), while leaving all thresholds, main units and role cuts unchanged. Do not inspect the real ranks or E results to choose the interpretation. No affected S07 fits/control evaluation should proceed before resolution.

## P1-02: N4 color/time maps do not state which B1 feature columns are transformed

Exact references:

- controls.json:239-246, specifically line241:11 fixed wrong feature maps, colorflip0/1 crossed with cyclic time-state shifts0..5 excluding identity, fitted B1 and target masks unchanged.
- FALSIFICATION_AND_SENSITIVITY_PLAN.md:13 repeats wrong nuisance maps without a column-level transformation.
- FEATURE_AND_MODEL_EQUATIONS.md:5 specifies saturated12 condition-time onehots AND12 raw nuisance columns, including current color*r. protocol.json:172-197 lists these exact feature names and scaling rules.
- Frozen code/spec.py:38-44 implements both the color/time PSTH index and current color*r in the B1 constructor; no separate N4 oracle fixes which one is remapped.
- Owner request:445-465 requires the exact deterministic N4 definition, not a newly selected stress test.

Two non-equivalent transformations both satisfy frozen B1/no refit/targets unchanged: (A) permute only the12 PSTH onehot assignments and retain the12 observed nuisance values; (B) apply wrong current-color assignment to both PSTH and current-color-dependent color*r, retaining the other observed nuisance values and original A-fitted scalers. With nonzero interaction coefficient and running value, their linear predictors differ, so this changes the stress-test estimand and scores. A cyclic peri-onset state map also needs to remain an exact registered feature map rather than silently substituting absolute source time; the question is which defined columns participate, not a demand for a new statistical method.

Neither controls narrative nor machine file identifies the affected column set/formulas, and historical M1 review2:52 only states deterministic coding stress. Minimum prospective owner decision: state the exact N4 raw-feature-column mapping, particularly whether color*r changes with the wrong color or only the12 PSTH cells are remapped; preserve unchanged fitted B1 coefficients, A-fitted scalers/active map, target masks,11 operators and no p-value/refit. This fixes a scientific operator before results and is not authority to weaken the baseline. No N4 scoring or complete production-contract acceptance before that mapping is resolved.

## Requested checks resolved without new ambiguity or amendment

### Development versus Final applicability

The new owner request:420-465 explicitly authorizes Development-applicable sensitivity/reference execution and requires Final-specific gate status NOT_EXECUTED_FINAL_BOUNDARY. This is sufficient current authority for the corresponding Development operators/refits after earlier stage gates. No need to demand Final access or to relabel every >=12Final coverage clause as Development failure. Retain per-mouse/per-role/per-color/operator support conditions, original optional-coverage availability rules, registered draws and mandatory attempted-numerical STOP. Report actual Development denominators descriptively; all future Final coverage/positive-claim gates remain unexecuted, never counted as passed. S03 has explicit DevBO>=3/FC>=10 and seeds16043/16044 (controls.json:43-50; BO_FC_TRANSPORT_PLAN.md:7-9), already a Development diagnostic. Other Final-specific claim floors remain future conditions. Optional prefit availability can be UNAVAILABLE only under existing rules; this does not authorize dropping a required Development test or converting an attempted mandatory failure.

The owner's8 labels versus seven-level terminology is also explicitly resolved in section5: report every absolute B0/B1/B2/B3/B4/C/D/S output. No model-count clarification is needed.

### Attempt allocation preserving Final

NUMERICAL_POLICY.json:60-70 gives the full-study16178 ceiling; owner:493-513 explicitly requires a stage-specific applicable allocation and no reallocation of Final reserves. Arithmetic is uniquely determined by frozen model/panel rules, not a material policy question:

- Development main per8-unit mouse:3 B1 lambdas*8 + B2/B3/B4*8 + C*8 + D/S*3 seeds =62 optimizer attempts. B0 is analytic and consumes no optimizer attempt.
- Final main per8-unit mouse: B1/B2/B3/B4/C*8 + D/S*3 =46.
- Each eligible refit panel with U units: B1/B4/C*U + D/S*3 =3U+6; only the8 listed refit panels consume these attempts; same selected lambda, no B1 grid per panel.
- Original loose allocation28Dev*(62+8*30)=8456;27Final*(46+8*30)=7722; sum16178. Keep the full original Final7722 reserve protected and do not spend omitted Development/optional-panel slots on alternatives.
- Current27 admitted Development mice have main1674 attempts. With all8 panels available and all other panels atU8, S06/S07 fixedU4 reduce panels to6*30+2*18=216 per mouse, yielding a tighter maximum27*(62+216)=7506. Exact schedule is1674 + sum over eligible mouse/panel of(3U_panel+6), with S05/S10/S11 availability/subset sizes fixed before each panel fit. A smaller actual schedule is attrition/registered unit-count arithmetic, not a discretionary allowance or a lowered threshold.

The derivative-certificate calls (<=24P fixed-FD objective evaluations +3AD+3analytic per attempt) are separate call accounting inside the same48h stage, not extra optimizer attempts; Final zero real attempts here. All external counters and one-stage wall/process-child enforcement remain production-certification obligations, not a present synthetic/static PASS.

## Minimal next action and review boundary

Resolve only the two explicit scientific operator definitions prospectively, preserve this unsuccessful complete-contract review and the original M1 files, and bind any owner clarification as a separate new-mission interpretation record before the affected production implementation/real fits. This review does not prescribe which option is scientifically preferred and does not amend M1. Safe static identity checks and unambiguous numerical-oracle work need no unrelated policy amendment, but a complete prefit acceptance must account for both findings. Do not restart R3/R4 source recovery, loosen thresholds, run B/E early or access Final to resolve them.

## Independent assessment of parent synthetic witnesses

After the initial static draft, independently read and executed the pure-Python contract_witnesses function and compared its exact JSON with SYNTHETIC_CONTRACT_WITNESSES.json. No source, neural input, fit or production worker was involved. The S07 middle sets reproduce as[3,4,5,6] versus[6,8,1,7], and N4 fixed coefficient examples as eta1.14 versus.86. These are valid demonstrations that the two readings can differ. The10-presentation fixture is explicitly not an admission/QC cohort or a production numerical certificate; it proves mapping dependence, not source or scientific success. The reported counts are nonnegative with scored counts<=full counts; multiplying exposures by the same number of presentations within each domain preserves the differing ranks. The N4 example is an algebraic fixed-feature contribution comparison, not a real fitted/scaled model.

Both pairs are plausible readings of the exact underspecified operator text; the witnesses alone do not authorize either reading. The findings are grounded in the missing window/column definition, not inferred from synthetic score favorability. No further scientific criteria or operator alternatives are invented by these examples.

## Inspected source identities

The334-entry M1 manifest is a static identity registry, not evidence that current production code exists or real fits pass. These inspected normative/current-owner/source-review identities bind this report.

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
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r1/OWNER_REQUEST.txt | 24286 | 1539625353106612ca573e30642a8b0c4adef89cdfea9eba49e6f242104bb992 |
| ops/evidence/2026-10-18/p16-m1-visual-dynamics-protocol-freeze/INDEPENDENT_REVIEW_2.md | 10918 | f22e75108005f28e1256fc1d46dc1796d3f913431d93e86a1c01c5424d36842d |
| paper16_m1/code/spec.py | 7376 | 2e8daa11c9205893c24309f34379218847000d0a6895de8c5ea62eb2f644d01f |
| paper16_development_r1/contract_witnesses.py | 2563 | b1068bc2ec01727555ca0bea4c3b69bc844b9c03371ee208db456a21b93606ac |
| ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r1/SYNTHETIC_CONTRACT_WITNESSES.json | 1193 | ac2c7b1e3edb93fb91b2cfb8a48c2006495d1b7efa24c856808704db09fb5bae |
