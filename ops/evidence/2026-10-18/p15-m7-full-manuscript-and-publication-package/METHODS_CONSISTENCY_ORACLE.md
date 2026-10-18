# Independent Methods consistency oracle

Mission: P15-M7-FULL-MANUSCRIPT-AND-PUBLICATION-PACKAGE. Reviewer: /root/pivot_review.
Status: **REVIEW_PREPARATION_ONLY**. This is an independent source-grounded reference for later manuscript review, not manuscript authorship or final document acceptance. No open source-definition P0/P1 was identified. The manuscript and rendered PDFs have not yet been reviewed.

The companion JSON records the full rules and exact source hashes. I verified the 29 listed relevant source documents/code/tables against the new SOURCE_HASHES lock, which inventories3,099 original saved artifacts. I did not claim a new independent rehash of all3,099 entries. Only static saved text/JSON/CSV was read; no scientific executable imports, neural arrays, model workers, fits, likelihood/AD/FD, selection, new scientific tests or D reassessment occurred. External primary bibliography/license links are inherited from the verified archived source record; fresh online bibliographic verification remains a separate manuscript requirement.

## Exact scientific and source contract

- Classification: methods-oriented empirical secondary analysis, exploratory Development and **DESCRIPTIVE ONLY** independent-animal evaluation. The source is native IBL Brain Wide Map ONE/ALF public AWS, **not DANDI**. Data CC BY4.0 does not relicense provider code. Global139 mice/459 sessions/699 insertions are inventory denominators, not the analyzed MOp cohort.
- Metadata screen:2024_Q2_IBL_et_al_BWM cluster/trial aggregates paired with2023_12_bwm_release insertion roster. Native sorting:pykilosort/#2024-05-06#; native task:#2025-03-03#. Unique unrevisioned wheel and original AP/sync/saturation files are individually pinned. No revision/session/probe substitution.
- Original20 mice=12Development/8Final-reserved; actual10Development/8labs and6Final/4labs. Development exclusions NYU-37(B31<40),CSHL059(no covered epochs under native sync domain[0,1]); Final exclusions NYU-21(native wheel strict-order failure,16,485 equal pairs),UCLA033(six qualified C units<eight). No replacements.
- MOp parent/1/2-3/4/5/6a/6b via native channels[clusters.channels]. No MOs or neighboring-region pooling. Provider-good label1/anatomy are upstream **whole-session** release curation; only new physiology/ranking/scalers are A/C-only. Atlas layers/contact neighborhoods are proxies, not histology.

## Observation, QC and causal features

Original native trial ordinals determine A/B/E60/20/20 and C/D60/40 before exclusions; drop last original trial before and first after every boundary. Never re-cut after QC. Primary50-ms count bins:10warm-up bins[stim-.5,stim),10score bins[stim,stim+.5). Warm-up initializes filters/history but adds no likelihood. Reset neural history/C/HMM prior each epoch; no neural cross-trial/gap history. Behavioral support can begin stim-1 and precede trial onset, with strict predecessor wheel samples and authorized-role/support coverage.

AP metadata/fs/sample counts and monotone probe-to-session sync define support; no extrapolation or first/last-spike support estimate. Valid epochs require full trial/support containment and no known saturation/invalid overlap. GoCue is within trial before feedback; no arbitrary goCue-versus-stimulus order. Count targets are half-open; every predictor event/sample must be strictly earlier than its bin start. Equal-time wheel/stimulus events are unavailable at that boundary. Wheel is backward sample-and-hold, not future interpolation. No firstMovement predictor or all-movement coverage claim.

C/A physiology:rate0.5-100Hz inclusive,>=100spikes,within-epoch ISI<1ms fraction<=.005 with>=99adjacent pairs; each original chronological role quartile>=10s exposure and>=.1Hz. Never bridge ISIs across gaps. Rank refractory fraction ascending,rate descending,UUID lexical; select exactly8. Mean/population SD from A/C **score rows**,SD<1e-8 fixed zero. Nuisance/history inputs standardized and clipped±3,not predicted rates/counts.

There are37 nuisance columns:trial/stimulus elapsed functions and contrasts,observed cue/response/feedback,completed previous-trial codes,original trial/session-time drift,and14 strictly past wheel columns24-37. Four disjoint history windows are0-.05,.05-.10,.10-.20,.20-.50s,raw count/window duration in Hz for every unit. Own/other attribution is conditional predictive ablation. It is not a synaptic mechanism.

## Mathematical and numerical checks to enforce in manuscript

Poisson mean mu=Delta exp(eta); likelihood includes y log(mu)-mu-lgamma(y+1). **Training objective is -LL_score/T+lambda/2 times squared non-intercept free coefficients,where T is population time bins.** Effect denominator is **actual scored Q=T*U**,with identical within-contrast units/masks. These are different normalizations.

| Model | Definition | Nominal primary parameters |
|---|---|---:|
|B0|Unit intercept|8|
|B1|Intercept+37 measured nuisance columns|304|
|B2|B1+own4-lag history|336|
|B3|B1+other-unit4-lag history|528|
|B4|B1+all32 history columns|560|
|D2/D3|B4+conditional Poisson HMM offsets/transition/initial logits|571/584|
|C1/C2|B4+fixed DCT causal finite-history projection|568/576|
|S3/S4|B4+IID static emission mixture|578/587|

Report actual active counts separately; constant columns have fixed-zero coefficients. D offsets have reference state0; pi/P use reference-last logits. Score pre-bin joint predictive mass,then assimilate counts and transition. Differentiate through warm-up; conditional LL=logL(warm+score)-logL(warm). No current-bin posterior prediction or future smoothing.

C is a **fixed**,first-r orthonormal DCT-II projection in frozen unit order,using ten past50-ms microbins and normalized exp(-(j-1)*.05/tau) weights. It is not a learned recurrent integration/state-optimization model. Micro-rate z is A/C score-row standardized but **not clipped**; resulting q receives its own A/C scale and±3 clipping. S is IID,not filtering carry-over. Chosen D3 is paired with larger S4; same-K IID-HMM identity is a separate mathematical oracle. Nominal count alone does not equalize effective capacity.

Ridge grid .01/.1/1;D K2/3;C rank1/2,tau.1/.25;S K3/4. D/S each have all seeds11/23/37. **Ensemble pre-bin joint masses uniformly via logmeanexp**,with each HMM's causal filter;never average label-switched coefficients. Development61 A starts/mouse in37 grouped candidates. B selection maximizes equal-mouse B LL/Q;ties1e-6 resolve fewer nominal parameters,stronger ridge,smaller K/r,tau,lexicalID. This is not a one-SE rule. No E selection,A+B refit or individualized Final model search.

Selected B1/B2 ridge.01,B3=1,B4=.1,D3=.01,C rank1/tau.1/ridge.1,S4=.01. Final coefficients are independently C-fitted;no Development coefficients reused. Box intercept[-8,8],linear[-1,1],state offsets[-2,2],pi/transition logits[-4,4]. Nonintercepts/logits/offsets penalized;no output clipping. L-BFGS-B maxiter2000,maxfun80000,maxls40,ftol1e-12,gtol1e-6,float64,no retry. PG outward removal:at lower remove g>0,upper remove g<0;infinity norm<=.001. Synthetic analytic/AD scaled-coordinate<=1e-8;real endpoints<=1e-5;all FD scales1e-4/1e-5/1e-6<=1e-5. Optimizer success or favorable checker step is insufficient.

Historical359starts(358completed numerical PASS on rounded inputs+one STARTED,251unattempted of610) are **not corrected scientific fits**. Corrective1,135=610main+525sensitivity;Final392=72main+320sensitivity;cumulative1,886,with separate prospective budgets. Do not retrospectively assert the original1,928 aggregate ceiling certified all later maxima. Timestamp repair preserved binary64 bits/hex,missingness/original ordinals and actual strict-past predecessor indices;PL033 equal-time wheel trial224 remains excluded.96,642 audited finite table cells were not96,642 distinct timestamps.

## Statistics, references and sensitivity gates

Mouse is the independent unit,equal weight. Ordered comparisons:primary B4-B1;secondary **B4-B3,B4-B2,D-B4,C-B4,D-S**. Exhaustive2^n signs,one-sided primary/two-sided absolute-mean secondary,including observed assignment/equality;not a MonteCarlo plus-one test. Fixed Holm5 retains unavailable p1 slots. Whole-mouse10,000 percentile bootstrap,PCG64seed150101,linear quantiles,same index stream across contrasts. Lab-block bootstrap seed150102 and equal-lab/LOMO/leave-lab results are dependence diagnostics,not independent-laboratory replication. Inference is conditional on independence and symmetric sign-exchangeable null effects;no outcome-selected assumption pretest.

At six mice,minimum two-sided p=2/64 and minimum possible Holm5=.15625. This resolution is not empirical power or equivalence. Complete confirmation additionally required>=8mice,4labs,no lab>50%,mean>=.001,positive95%lower,width<=.01,registeredp<=.05,>=75%positive,positive everyLOMO/leave-labmean,mandatory sensitivity/reference/source/numerical/assumption conjunction. Final primary width0.0916613158 exceeds.01;all six verdicts remainDESCRIPTIVE ONLY regardless of positive primary interval/rawp.

All11 sensitivity cases are B0-B4 refits only,no new grid:D/C/S have no sensitivity-refit credit. Mandatory9=S01five units and S04-11;each requires>=6paired andpositive baseline contrast means. S02twelve units is actually available in all6Final mice;S03twenty units has4 and is aggregate unavailable. S04=100ms/do not equate nats/bin across widths;S05=250ms history;S06strictQC;S07A/C-rate p=min(1,2/r),original-unit independent role streams;S08/09saturation±10/50ms;S10**higher-order trial/session drift**;S11five-unit±2native-contact MOp proxy. S07 exact SHA256/PCG64 stream identity is in JSON;consume every original within-role spike ordinal including outside retained epochs,never D during C.

Four999-draw suites use original PCG64/SHA256 schedules and shared surrogate realization across all contrasts. N1 rotates all units together within20-bin warm+score epoch(nonzero1-19),preserving trial/unit counts but breaking order/alignment. N2 donors are nonself cyclic epoch shifts within frozen side/contrast/order-half/A-C-wheel strata;singletons removed from both original/reference control exposures. N3 omits wheel stratum and substitutes wheel columns:formal statistic is **B4 LL/Q**,copied/labeled across contrast slots,with B4-B1 gain-change diagnostic;not D/C wheel evidence. N4 cyclic complete5-original-trial blocks preserves within-block order. N2/N3/N4 require>=60%coverage and>=30epochs/mouse;aggregate>=6. No recursively generated counts or null refits.

Reference p=(1+#reference means>=original)/1000,Holm4 per contrast;missing p1/unavailable. N1/N2 gate requires>=75%mouse original>median reference **and** positive equal-mouse degradation with valid coverage;small referencep alone cannot clear it. DevelopmentN1=7/10<8 failed,FinalN1/N2=6/6passed;N4Development5/Final3 both aggregate unavailable. Failed D-B4/N2 and D-S/N1/N2 remain explicit. N4 is additionally required for persistent-state predictive wording;no persistent biological-state claim. All are finite destructive references,not assumption-free causal/mechanistic nulls.

## Writing and final-review cautions

Do not copy old M0/M1 noFinalaccess statements as current status:they describe earlier mission boundaries. Current M6 D claim is complete and consumed. Do not infer bothS02/S03 failed from generic report wording;read actual tables. Never infer equivalence,no biology,all-movement independence,causal/motor-command mechanism,discrete neural atoms,CWP/NAP,human/BCI validation or independent-lab replication. Keep all failed criteria in main narrative. Manuscript author/licence/bibliographic review and final rendered-document consistency review remain pending. Saved-result reproduction is not independent raw-data/fit reproduction and cannot rerun old workers/tests under this writing-only mission.

## Verified source identities

- `paper15_final1/C_FIT_PLAN.json` — `7d654270c7a443102be67e0db5dc0e9099ea08f50fc054500a24441d6d9f1722`
- `paper15_final1/D_BATCH_CLAIM.json` — `95108b1b992ae69185f083826dc67b0a79765afec3ee195449afd49017a8b726`
- `paper15_final1/FINAL_SCIENTIFIC_REPORT.md` — `3c084064202a232f9dee9f63f5cf2f7ad31ae8917157f14ed51edfa5c6d479fa`
- `paper15_final1/ONE_SHOT_D_SPECIFICATION.json` — `4782744a789740d945095b50897138d3bf60e46643ccc11435aa0126b9fef8a4`
- `paper15_final1/anatomy_report.py` — `7372f92ff30682f9a8b7a44525880d0035a39c17fa91f7081a13d629b5705ddf`
- `paper15_final1/final_statistics.py` — `4d6489625c661eb5782e7d0426762ca51e0c31fb15828301bdec9a7789d0dc20`
- `paper15_final1/requirements.txt` — `28bfda2c15d2a46a6c9dc91cacc2a328aef9e24a9ed3d6224ee3c80cd64606a2`
- `paper15_final1/results/FINAL_DELIVERY.json` — `c10468848589b33fd577b23d99097711b3682a53d0a90530abbd493210874d64`
- `paper15_final1/statistics.py` — `a62ba9119624b293ff0ffcc8a6679120b3956dc10e63a47bf66d9d29c1c54382`
- `paper15_final1/tables/FINAL_CONTRASTS.csv` — `e6a5cf8d3929be1dd443dc0daa572f0da046ee577dfc9bb30babbae36832bf9f`
- `paper15_final1/tables/FINAL_CONTROLS.csv` — `3f9d749446e94e29432c6faa5961ba32bd18fefe7dc13690934d3897c2d2cb79`
- `paper15_final1/tables/FINAL_SENSITIVITIES.csv` — `4d9d0debb7bde3f331dca0cf045f12dddb993d0c3e41c41c66d4ec0d05938101`
- `paper15_final1/tables/FINAL_SOURCE_AND_C_QC.csv` — `d2f1ec91513cbd4fed793421870afac5a9edc179c9305ff24698fd6b4f7a248a`
- `paper15_m0/SOURCE_REGISTRY.md` — `daaf68b84b8081717c4d8be1c15a764b6849ae21f28c24be63e809a05bb15bc0`
- `paper15_m1/COHORT.csv` — `b1b29b6f70f81bee2d96884670f1b2105610b676bc489a58a479b253d7fc148c`
- `paper15_m1/FEATURE_MODELS.md` — `37ef100353913eb2a99d92ffb9404093b2d850ce326fd6b497dec31ec2453b4e`
- `paper15_m1/NUMERICAL_POLICY.json` — `cc0c926b04540f1787e0a005f6566bf42225cb2bca159fd9accdd3e74ab0358e`
- `paper15_m1/NUMERICAL_SELECTION.md` — `6580c55effc5ce13f07649279a39a009a66734407312413681d40e941a16bbef`
- `paper15_m1/PROTOCOL_FREEZE.json` — `298c8e9892db22b4ce130c745c54a73734891706654c15dfc2c2cf4272fa48c1`
- `paper15_m1/SCIENTIFIC_PROTOCOL.md` — `fbdc36c393456b02a87b7e23b15bf7aa422458478ff1a621a0e6f1bdf2da03cc`
- `paper15_m1/SOURCE_QC.md` — `da5ca1a926df11cdce32f786a6e1de5ea9ed7648a5ca73045a4bbead4b8407e7`
- `paper15_m1/STATISTICS_CONTROLS.md` — `3a2665cc43cffac9af7e33ae5c61d937f7caf9cb4ca89c4e692ae4dc39fa0254`
- `paper15_r1/DEVELOPMENT_REPORT.md` — `3f6d5cf6dbdc4b78b2fbced8267ca0dcf0042d6a272a670df77667fc52130979`
- `paper15_r1/SELECTION_FREEZE.json` — `58acfc619525b32500f60519675eb1d75fcef81ffd532932bfa108c116278bda`
- `paper15_r1/features.py` — `30d17b3a902429537e8b83fc9ac5a483933bdb8080ff890c5f43c6fc5f4dd3fd`
- `paper15_r1/native_table.py` — `fb7ca090776f2096a9ec3fd102afd0cc115d0bca3d01b57a8c6defabbc637aaf`
- `paper15_r1/source.py` — `ad8d0f786690d414f07568556d017e0bdb14edd0137fb246789e7ffb7cedddbb`
- `paper15_r1/tables/B_SELECTION.csv` — `e312db9bfd77fb0fec73d6e1896da115ae19bc11cbe824ec4e41a95a4b033c1b`
- `paper15_r1/tables/COHORT_FINAL_NATIVE_QC.csv` — `14ccaa4a410d1f8397c87ae73ed835909c254bc9101c1eaddd37c7ebccd613b9`

Companion JSON SHA256: `46a1caa12e31c49b1ea4866994111bc82101721378319b32ac5da335859eac17`.
