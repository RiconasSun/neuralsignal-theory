# Frozen conditional B* root-cause evidence

Mission P13-BSTAR-CONDITIONAL-NULL-DIAGNOSIS-1. BASE c7ae3d4753f94ba50134d1f15a4a62dcb101d842.

**Diagnosis: DOCUMENTED_GENERATOR_INSTABILITY.** One identical, prospectively registered failed-prefix replay documents a concrete excessive count-feedback path of the intended B2 generator. No implementation discrepancy was found. This is a realized finite-horizon simulation-path diagnosis, not a theorem of almost-sure/global instability, nor a biological mechanism. The original conditional-B* control remains FAILED / UNAVAILABLE and original M6 remains scientifically failed. Engineering diagnosis is not a retrospective scientific PASS.

## D1: static mathematical identity

Registered B2 has32coefficients: per-unit intercept plus three own-history terms. Strictly prior groups are lag1,lag2+lag3,lag4+lag5; all histories reset at each epoch. A-only mean/populationSD are fixed. Interceptmean0/SD1; zeroSDfeature0. No nuisance, other-unit, current-bin or future-bin term enters B2. Coefficient bounds[-8,8], ridge and finite observed-data fitting do not bound the support of generated history counts. The exposure is100ms, so eta is log expected count per bin and no Hz multiplier belongs in exp.

For unit u the inverse transformation is beta_k=theta_k/sd_k (zeroSD beta0), alpha=theta_intercept-sum_k beta_k*mean_k. Thus eta_t=alpha+beta1*y_(t-1)+beta2*(y_(t-2)+y_(t-3))+beta3*(y_(t-4)+y_(t-5)). Independent scalar-loop lag construction, inverse coefficients and original baseline_eta agree within4.44e-16 on saved development E inputs; causal/reset/future/zeroSD tests also pass.

The original generator starts count0, computes eta_t from already generated past bins, computes exp(eta_t), samples Poisson then assigns current counts. All30bins including5warmup are generated under this ordering. This matches the registered generator; scaling/update exposure or parameter interpretation is not repaired or altered. Static signs alone could not establish actual failure, since the original receipt lacked the generated prefix. D1 explicitly recorded this limitation before D2.

## D2: one identity-verified diagnostic replay

Independent prereplay review accepted the frozen observer. Python3.11.15, NumPy2.4.6, SciPy1.17.1; original conditional seed130104/default_rng PCG64; replicate0; sorted prefix147465,152417,152419,156130. Other suites have independent RNG resets, so none were restarted. Original core.replicate and conditional_counts source, frozen E arrays, qmetadata and model/scaler bundles were unchanged. Python line observation read original eta/count locals and produced no draw. Synthetic observer tests gave exact output and RNG-state equality for3fixed seeds.

First3mice each reproduced all9completed score labels byte-for-byte before the fourth mouse was allowed. RNG-before/after states, per-bin finite traces and matching rows are saved. A single exclusive durable ATTEMPT was consumed before real RNG use. The fourth mouse reproduced the same original FloatingPointError in exp at original control_core.py line45; no draw at failing bin, later mouse, later replicate, clipping or scientific replacement followed. Native diagnostic exit0 means the expected failure was recorded successfully, not that a scientific null completed. Original scientific native exit1 and failure files remain untouched.

Failure identity: mouse156130, replicate0, original epoch ordinal94 (Eepoch index3 zero-based), selected unit191(index0), zero-based bin14 / one-based bin15. Its start is1.4s after epoch reset; the15th100-ms bin remains inside the same3s epoch. All diagnostic eta and saved counts are finite before the failing exponential operation. Exactly one epoch/unit eta crossed the float64 exponential boundary.

| Unit191 / epoch94 bin (one-based) | Original eta | Finite Poisson mean | Generated count |
|---|---:|---:|---:|
|10|0.34717022666086805|1.415057585397146|3|
|11|1.1131398796243737|3.043900887831873|2|
|12|1.2197211888367059|3.3862434795094387|7|
|13|3.3620918397984187|28.849476286211893|36|
|14|16.08830666042862|9706503.283525605|9702754|
|15|3478515.7353549777|exp overflow; no finite mean|NOT DRAWN|

The9,702,754count at bin14 is the saved draw from a finite mean9,706,503.2835; it is not an int64 overflow or count clipping artifact. It is below2^53 and is exactly representable in the float64 history sum. The next step's lag1group alone contributes3,478,498.699523015to eta. Frozen raw-coordinate equation at the failure:

alpha=-2.2342861252985204

beta=[0.3585063271235172, 0.407463325839988, 0.3498390153441261]

H=[9702754.0, 43.0, 5.0]

eta = -2.2342861252985204 + 3478498.699523015 + 17.520923011119486 + 1.7491950767206306 = 3478515.7353549777.

log(float64max)=709.782712893384. Synthetic nextafter boundary tests confirm exp at the computed log limit is finite and one representable step higher raises under original over=raise. The actual eta exceeds that boundary by orders of magnitude; choosing another finite-difference step, optimizer tolerance, floating rounding or log-score rearrangement cannot make the same enormous Poisson mean finite in float64. No Poisson sample was attempted at that bin. All earlier stored eta values in this prefix were below the boundary.

Saved-only audit independently reconstructs the same lag sums, inverse slopes, all standardized terms, actual eta and precise overflow cell from failure_prefix.npz without any simulation or new score. Generatedprefix is [0,0,0,1,1,2,1,1,2,3,2,7,36,9702754]. Observed E counts for this mouse had maximum8 across all units; that comparison describes extrapolation beyond the observed path, not a biological runaway or evidence of contamination.

## Original versus proposed implementation

| Surface | Original scientific implementation | This diagnostic / proposal |
|---|---|---|
| B2math/scalers/bounds/link/ordering | Frozen original | Identical; no mathematical source repair |
| Random draws | Original conditional seed/schedule | One diagnostic prefix only, no changed draw |
| Observability | Original failure stored no generatedprefix | External read-only line observer + separate diagnostic artifacts |
| Original null reference | Required999replicates | FAILED / UNAVAILABLE, never replaced by diagnostic data |
| Future science | Original M6 numericalSTOP | Separate nonexecuting descriptive-final option only; new approval/registration needed |

No mathematically equivalent scientific repair is proposed because no verified implementation defect exists. Rate/count clipping, censoring, replacing B*, altered links, seed selection, shorter simulation or a stationary history restriction would define a different generator, not repair this one. A hypothetical higher-range exp alone would still face an enormous unrepresentable Poisson mean and is not established as a valid solution; no such experiment or optimizer rescue was run.

## Scientific decision and limits

Preserve all historical source freezes/partial arrays/native receipts and original M4/M6 failures. The three earlier999Econtrols remain only their original completed scope; the conditional suite still has0complete paired replicates and3mouse rows. No diagnostic count, score, failed sample or replay is incorporated into original M6 statistics. No original null p-value, denominator, model, animal allocation, hypothesis or numerical threshold changes. Original6/9recent-event sensitivity fails unchanged>=8coverage; all associated broad primary claims remain permanently INCONCLUSIVE. Passing B*or S statistical components cannot rescue these missing gates.

PROSPECTIVE_DESCRIPTIVE_FINAL_OPTION.md and DECISION_MEMO.md are options for separate future owner authorization, not active protocols or C/D access. All final C model fits0, new real fits0, final D neural outcomes/export/scoring/evaluation0. No raw neural sources, new dataset, cryptographic custody system or full control restart. All source-access journal hashes and original registered source hashes are unchanged. Realized model-driven feedback is demonstrated only for this frozen stochastic path; probability/prevalence across paths and an asymptotic stability theorem were not estimated. No further replay is authorized.

## Evidence and reproducibility

D1_STATIC.json/report; REPLAY_FREEZE/APPROVAL and PREREPLAY_REVIEW_r1; replay/ATTEMPT, first3MATCH/RNG/TRACEfiles, fourthTRACE, RESULT and failure_prefix.npz; SAVED_AUDIT.json; D2_NATIVE_EXECUTION/EXIT. Twelve bounded synthetic tests plus saved-only prefix/contribution audit. First synthetic temp-directory ACL failures and prior test source remain preserved; fixed only local synthetic output location, no scientific attempt consumed there.

Saved-only PowerShell: & .\paper13_bstar_diag1\reproduce.ps1. It verifies frozen identity/matrix, bounded synthetic tests and stored diagnostic evidence. It never replays the real generator. Real replay.py entry point is consumed and must not be invoked again. Independent final review and exact origin/test commit/push/allfilehash readback/clean are administrative completion conditions, certified only by actual final receipts. No external peer review or scientific M6 PASS.
