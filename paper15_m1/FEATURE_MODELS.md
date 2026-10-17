# Exact feature and model equations

Notation: U=8 primary units ordered by frozen A/C unit ranking, Δ=.05s, y_tu the observed half-open bin count, b_t its start. All input events/samples satisfy time **< b_t**. Equality at the boundary is deferred to the next bin, avoiding ambiguous event latency. A source photodiode stimulus timestamp exactly at b_t is not considered available until after that boundary; at subsequent bins use its source value. Trial start and bin schedule are design-known. No current-bin neural observation enters a predictor or an HMM pre-bin probability.

## 37 non-intercept nuisance columns x_t

`clip(a,L)=max(0,min(a,L))`. Before an event is observed, its indicator and elapsed/value columns are0. All columns then receive the frozen A/C standardization/±3 clipping from SOURCE_QC.md.

| Columns | Exact definition before standardization |
|---|---|
| 1–2 | e=clip(b−trialStart,10)/10, e² |
| 3–5 | r=I(stim<b)clip(b−stim,1), r², r³ |
| 6–7 | I(stim<b)×contrastLeft, contrastRight, absent side=0; missing essential stimulus metadata excludes trial |
| 8–9 | I(stim<b)×I(left/right contrast>0) |
| 10–11 | columns6/7 multiplied by r |
| 12–13 | I(goCue<b), I(goCue<b)clip(b−goCue,1) |
| 14–17 | I(response<b), signed choice×I(response<b), I(feedback<b), feedbackType(±1)×I(feedback<b) |
| 18–19 | reward code and signed choice of most recent completed trial with feedback/response strictly before epochStart;0 if none; values frozen at epochStart |
| 20–21 | original trial ordinal/1000 and its square (not normalized by future trial count) |
| 22–23 | session time b/3600 and its square |
| 24 | backward-held wheel position(b−) minus backward-held position(epochStart−), radians |
| 25–28 | signed wheel displacement over h∈{.05,.1,.25,.5}s: w(b−)−w((b−h)−) |
| 29–32 | total absolute observed encoder increments within each of the same past intervals, including the increment from the preceding held value |
| 33–36 | square of signed displacement/h for those four intervals |
| 37 | I(abs(displacement over.05s)>.001rad) |

An epoch's wheel history support includes the extra.5s preceding epochStart where needed for nuisance columns25–36; this support must be inside recording and the permitted chronological role, with predecessor encoder samples and known-invalid exclusion. Past behavioral samples may precede the current trial; neural history still resets at each epoch. Thus behavioral support is [stim−1,stim+.5), while the neural warm-up remains.5s and must lie inside the current trial. This support is checked prospectively, not replaced by zero movement. Previous completed-trial event codes are source task observations, not previous neural states. No current choice/reward is known before its actual event, no future smoothing/firstMovement feature. Exactly one contrast side may be source-NaN meaning absent; map that side to0. If both sides are absent/unknown or a finite contrast is outside[0,1], exclude that trial.

## History h_t,v,l

Four disjoint strictly past windows are `[b−.05,b)`, `[b−.10,b−.05)`, `[b−.20,b−.10)`, `[b−.50,b−.20)`. Each raw feature is spike count/window duration (Hz), with outside-epoch history fixed0 at reset. At scored bins all history is observed after warm-up. Standardize/clip each unit/window using A/C score rows only, same maps across models. There are4U columns. The within-bin count is never a lagged feature. No row deletion depends on a model's predictions.

## Poisson baselines

μ_tu=Δ exp(η_tu); log p(y_tu)=y_tu log μ_tu−μ_tu−lgamma(y_tu+1). Joint bin likelihood is product over units.

B0: η_tu=α_u. B1: α_u+β_uᵀx_t. B2 adds Σ_l a_ul h_t,u,l. B3 adds Σ_{v≠u,l} c_uvl h_t,v,l. B4 includes both. Setting added coefficients0 gives exact B1⊂B2/B3⊂B4, with same offsets, transformations, unit order and masks. Own and other history do not overlap. B0 is the zero-nuisance submodel of B1. Nominal parameter counts: B0 U; B1 38U; B2 42U; B3 U[38+4(U−1)]; B4 U(38+4U). At U8: **8,304,336,528,560**. Constant columns have zero free coefficients; report actual active count separately.

Objective J=−LL_score/T + λ/2 Σ(non-intercept free coefficients)², where T is the number of valid population score bins, **not T×U**. Thus J is a sum of per-unit mean losses, and its full gradient is not artificially divided by U. Evaluation still uses LL/(T×U). All coefficients except intercepts are bounded[-1,1], intercepts[-8,8]. B0 constrained MLE is log(sum y/(TΔ)), projected onto its intercept box (all-zero target optimum−8). No factorial terms dropped from reported LL. Initialization uses only A/C rates with pseudocount.5 for finite initialization, not a modified likelihood. No output rate clipping.

## D: conditional Poisson HMM

K∈{2,3}. Shared B4 predictor η⁴_tu plus state offset δ_ku, δ_0u=0. Conditional joint emission g_t(k)=Π_u Pois(y_tu;Δ exp(η⁴_tu+δ_ku)). Transition rows P_ij=softmax(row logits with last reference0); initial π analogous. Free transition/initial logits bounded[-4,4], free offsets[-2,2]; B4 bounds unchanged. All non-intercept free variables including logits/offsets get λ ridge. Counts q_D=U(38+4U)+(K−1)U+K(K−1)+(K−1): **571 or584** at U8.

At epoch start pre-bin state weights areπ. Predictive joint log mass is logΣ_k a_t(k)g_t(k); only **after** scoring/observing all units' counts update r_t(k)∝a_t(k)g_t(k), then a_{t+1}=r_t P. Process10 warm-up bins without adding their LL to objective; compute derivatives through warm-up filtering. Equivalently conditional score LL=logL(warm+score)−logL(warm). No posterior smoothing or current-bin posterior plug-in into its own prediction. Sum log normalizers in float64; never exp a whole sequence likelihood. At fixed parameters exact enumeration must match forward conditional LL on tiny fixtures. B4 is recovered when allδ=0, irrespective of transition parameters.

## C: fixed low-dimensional causal history state

Ranks r∈{1,2}, τ∈{.1,.25}s. R is the first r columns of the orthonormal DCT-II basis over the **frozen unit order**: first column1/√U; columnj>0 =√(2/U)cos[π(v+.5)j/U]. No PCA, random favorable projection or training on scoring data. For the ten past50ms microbins, q_t=Σ_{j=1..10} w_j Rᵀ z_{t−j}, w_j∝exp(−(j−1).05/τ), sum w=1. Here z are microbin firing rates standardized with A/C only, zero before epoch reset; persist these scales separately. Normalize/clip resulting q with A/C score statistics. Finite history is.5s, with no learned recurrent integration or roll-forward count generation.

η^C_tu=η⁴_tu+γ_uᵀq_t. Boundsγ[-1,1], same ridge on all non-intercept coefficients; q_C=q_B4+Ur =**568 or576**. Added coefficients0 recover B4. The state is deterministic given strictly past observed counts; no state optimization and no access to future y.

## S: capacity-controlled IID static mixture

S uses the same B4 predictor, offsets/gauge, initial mixture logits and penalties as D but each pre-bin latent draw is IID with constantπ, without transition persistence or filtering carry-over. log p_S(y_t)=logΣ_kπ_k g_t(k). Its state cannot borrow current-bin posterior weights for prediction. q_S=q_B4+(K_S−1)U+(K_S−1). Pair a chosen D_K with **K_S=K+1** (3 or4), giving **578 or587** parameters, respectively, at U8—at least the paired D capacity. S has more emission components, D has transitions; parameter count alone does not equalize effective capacity. Freeze/search both S sizes and report that asymmetry, all attempts, and B scores. D−S must compare the prescribed pair, not an unfavorable post-hoc S. An IID transition HMM with P rows=π and the *same* K/emissions equals S mathematically; test this identity separately from the larger capacity guard.

Three-seed D/S predictive ensemble: fit all frozen starts independently, require each to pass; mix their **pre-bin predictive joint masses** uniformly, logmeanexp of the3 log masses, with each HMM's own causal filter. This is a fixed sequential ensemble predictor, not averaged label-switched coefficients. Baselines/C are convex fixed-design fits with one deterministic start. All primary/sensitivity reports retain actual parameter/search counts and do not claim equal effective capacity.
