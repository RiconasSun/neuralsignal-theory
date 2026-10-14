# Predictive Structure of Neural Population Activity Across Mouse Hippocampal Subfields

Exploratory Method Paper draft — P12-PREDICTIVE-STRUCTURE-V2. Draft completion is distinct from scientific validation. Authors, affiliations and submission declarations: [DECISION REQUIRED before submission].

## Abstract

We asked whether CA1 and DG differ in the predictive contributions of own spike history, other-unit population history and known stimulus/time context. We preserved a frozen 26-mouse allocation and used only the 13 development mice; all development inference is exploratory because A/B data and some scores had previously been examined. We reused 1,638 baseline fits and 78 shared-offset fits, and evaluated small, causally indexed nested Poisson GLMs with fixed ridge and numerical acceptance. Both subfields showed positive mean predictive gains from own history and combined features. None of four primary CA1-minus-DG contrasts passed the registered four-test Holm correction; the smallest corrected p was 0.0693 for other-unit mean history. Whole-mouse uncertainty, fixed unit/rate/anatomy/probe sensitivities and all four 999-replicate fixed-predictor controls are reported. These results do not establish a reproducible subfield difference or a causal mechanism. Original recurrent M4 failures remain unchanged. Final evaluation is unexposed and requires separate authorization.

## 1. Introduction

Population activity can be predictively structured by a unit's own past, the recent activity of other selected units, and known trial context. A fitted population model can improve prediction without identifying an anatomical mechanism or a causal interaction. This study asks whether these measured contributions differ between provider-labeled CA1 and DG in a frozen curated-release mouse cohort. The original P12 recurrent-model comparison stopped at numerical convergence gates. The present track instead uses small nested Poisson representations, retains the complete historical failure record, and targets a narrower observational predictive question.

The falsifiable exploratory hypotheses are four two-sided animal-level differences in conditional own-history, other-unit mean-history, stimulus/time and combined-feature gains. Nuisance-controlled contrasts are fixed before new scientific evaluation. The study contributes a transparent predictive decomposition, full mouse-level uncertainty and explicit tests against context/order and conditional temporal references. It does not claim a preferred recurrent regime, neural mechanism, independently confirmed anatomy or final validation.

## 2. Methods

The unit of independent replication is the mouse. This secondary analysis uses a curated release of Allen Visual Coding Neuropixels recordings and provider CA1/DG labels, restricted to the functional-connectivity drifting-grating repeated presentation block. Allen documentation describes spike-sorted units, quality metrics and the visual stimulus sets; it also cautions that a unit need not represent a perfectly isolated neuron. [AllenSDK documentation](https://allensdk.readthedocs.io/en/latest/visual_coding_neuropixels.html).

The frozen inventory contains 26 mice, allocated by the original salted mouse-identity hash to 13 development and 13 final mice. The current track uses only development A/B. Across eight stimulus conditions, the frozen assignment design reserves 45 trials per condition for A and 30 for B. Metadata exclusion masks remove unsupported trials without replenishment, so actual trial numbers can be smaller than 360/240. The preserved minimum is 24 A and 16 B trials per condition, with identical CA1/DG trial masks. Within each admitted trial, counts cover the first two nominal seconds in twenty half-open 0.1-second bins. This is a nominal curated-release exposure, not proof of continuous native acquisition or lossless original spike recovery.

Units have finite CCF coordinates and the frozen provider subfield mapping (DG includes designated DG sublabels); quarantined probe 846401834 and invalid exported-rate metadata remain excluded. A-only physiological QC requires 0.1â€“100 Hz, active-trial fraction at least 0.1 and refractory-interval violations at most 0.01, together with source timestamp integrity checks. The existing QC receipts and source hashes establish these decisions; this track does not repeat source acquisition or invent missing raw integrity proof. Within each ROI the original salted unit hash selects at most 32 eligible units, with at least five required. All 13 current development mice have 32 selected units per ROI. The population covariate includes only this fixed selected ROI pool, not every recorded unit.

Development A/B and existing model scores have previously been examined. The present registration prevents adaptation within this new run but does not restore developmental naivety. Every development p value, confidence interval and inferred contrast is exploratory. Final evaluation D has not been opened. Upstream provider spike sorting may use whole-session information; protected downstream holdout access is not equivalent to entirely naive upstream acquisition/processing.

Poisson representations predict current-bin count from known condition, known nominal within-trial time, provider trial order and only within-trial lagged observed counts. Trial-start history is zero, and no current/future response enters its own predictor. H contains five log(1+count) lags; P contains the average of other selected same-ROI units' five log-count histories, explicitly excluding the target. Poisson GLMs provide a transparent predictive decomposition; related population-history models have been used in other systems, but their retinal findings do not establish hippocampal physiology here. [Pillow et al. (2008)](https://www.columbia.edu/cu/neurotheory/pdfs/Pillow_et_al_2008.pdf).

The new nested basis has at most 39 features: intercept; seven condition indicators; nineteen bin indicators; linear and quadratic provider order; five own-history and five other-unit mean-history features. All six nested models share per-target A-only feature means/scales, with zero-variance scale set to one and the intercept unscaled. N is context+order; O removes context; NH adds own history; NP adds other-unit history; F adds both; OHP removes context from F. Unpenalized B log likelihood includes the Poisson log factorial and divides by the actual scored B trialÃ—20Ã—unit count. Training minimizes negative full likelihood per target-unit exposure plus ridge 0.1/2 on non-intercept coefficients. All coefficients remain within [-8,8]. Zero embedding into the same scaled basis establishes mathematical nesting, including the penalty. These are predictive contrasts between regularized fitted representations, not likelihood-ratio tests or estimates of uniquely attributable causal information. Correlated predictors, omitted interactions and regularization affect the estimand.

The original 1,638 amended M3 fits comprise stationary, own-history, full selected-population history, event context, trial drift and combined models over the frozen ridge grid and seeds. Their full records are reused, with exact manifest hashes, convergence and score denominators audited. Fixed-ridge 0.1 descriptive comparisons average all three seeds, with no selection against B. Stationary B scores are independently recomputed exactly. Other original fit weights were not saved; their old scores are verified against immutable records, numerical admission evidence and unchanged scorer code, not claimed freshly reconstructed from absent weights. Old population includes own history; old combined repeats own-history columns. Those representations remain unchanged and cannot identify a clean conditional own-versus-other contribution.

All 78 shared offsets were fitted on A at ridge 0.1, across 13 miceÃ—two ROIsÃ—three seeds. Their protected state hashes and exact training-array bindings are audited. The new N uses the mean of the three frozen coefficient matrices in the identical context/order basis; its full PG and independent endpoint derivatives are checked again without refitting. This mean is not a new selected seed or a new offset fitting policy. The remaining five new models use the preregistered deterministic box-Newton policy, independently checked per target-unit fit. Optimizer success alone is insufficient: finite values, physical bounds, full PG <=0.001 and independent derivative scaled error <=1e-5 are mandatory. Synthetic scalar-Poisson, causal, nesting, ridge, FD, bound and batch/order tests retain the original relevant tolerances.

CA1-minus-DG gains are paired within mouse, with equal weight for each mouse regardless of units, trials or probes. Four primary contrasts are Fâˆ’NP (own), Fâˆ’NH (other-population), Fâˆ’OHP (stimulus/time) and Fâˆ’O (combined). Joint history Fâˆ’N and overall Fâˆ’stationary are secondary descriptive contrasts. Primary paired tests enumerate every sign assignment and require the paired-difference symmetry assumption. Holm adjusts the four two-sided primary tests. Percentile whole-mouse bootstrap intervals use 10,000 paired resamples with fixed seed 120214; these are exploratory intervals rather than simultaneous confirmatory coverage. Leave-one-mouse-out means expose dependence on individual animals.

Sensitivity selections use A rates or frozen metadata, never B scores. The 16-unit view uses fixed hash order. Rate matching greedily pairs available units within absolute log-rate ratio <=log(2), with at least five pairs; residual mismatch and selected-population changes are reported. Boundary views exclude undefined or <=20/<=40 micrometer nearest-other-label channel distances, then match unit count across ROIs. These distances are provider-channel label proxies, not independently registered histological confidence intervals or true subfield distances. All required rate/boundary views require at least eight paired mice. Probe composition, same-probe-only availability and leave-one-probe-out cases assess sampling dependence; probes are not independent animals. Unavailable probe strata remain explicit. Sensitivity intervals are descriptive and no favorable subset is selected for the primary claim.

Four fixed-predictor B stress-test suites use 999 replicates per mouse/ROI, fixed hashes for RNG identities and unchanged A fits/scalers. The temporal suite redistributes each trial/unit's exact count total across bins under the A-fitted nuisance rate profile, recomputing causal histories. It tests a conditional nuisance-only temporal reference and can be affected by nuisance-model misspecification and conditioning-induced dependence. Condition labels are shuffled within fixed order blocks; bin labels within fixed trials; order values within condition. These controls preserve trial membership and count totals, but their exchangeability assumptions are not experimentally guaranteed. Their p values are exploratory reference-exceedance summaries, not exact causal tests or completion of the original M5 refit null protocol. Holm separately adjusts 16 pooled-gain and 16 regional-reference comparisons. The registered regional statistic is centered on the null regional mean. All control outcomes, including negative or uninformative controls, remain reported.

Native Windows AppContainer analysis uses zero capabilities, a copied read-only runtime and only copied development A/B plus development metadata. Fresh source/key/DACL/network/custodian-memory negative probes and process cleanup certify the analysis role; the trusted controller retains ordinary OS authority and procedural responsibility. This is not protection from a malicious machine administrator or an independent human data custodian. Final calibration/evaluation counts are never input to this mission.

The original M4 recurrent models remain numerically stopped. The Continuous CA1 d4/ridge0.001/seed11 endpoint PG was about 0.693; its original fixed FD checker exceeded 1e-5. A later diagnosis attributed the checker discrepancy to FD instability while preserving genuine nonconvergence. All three subsequent bounded conditioning/optimizer candidates remained above PG<=0.001, so no method was promoted and no cohort rescue succeeded. This track neither repairs nor retroactively validates those models.


## 3. Results

Nats per actual nominal curated-release unit-bin; equal weighting of 13 paired mice. Development A/B and some scores were examined before this new registration. These results are exploratory. No final evaluation.

| Contribution | CA1 gain | DG gain | CA1âˆ’DG | 95% mouse bootstrap CI | Raw paired p | Holm p |
|---|---|---|---|---|---|---|
| own | 0.03241794 | 0.02979173 | 0.00262621 | [-0.01227097, 0.01986089] | 0.76708984 | 1.00000000 |
| population | 0.00294569 | 0.00409738 | -0.00115169 | [-0.00212237, -0.00033627] | 0.01733398 | 0.06933594 |
| stimulus_time | 0.00190028 | 0.00261922 | -0.00071894 | [-0.00206251, 0.00047196] | 0.34155273 | 1.00000000 |
| combined | 0.04017709 | 0.04334781 | -0.00317072 | [-0.01875171, 0.01407416] | 0.72070312 | 1.00000000 |

No primary contrast passes Holm<=0.05. The other-unit-history raw p is below 0.05, but its corrected p is not. A percentile interval excluding zero is not a substitute for the registered multiplicity gate. Both ROIs have positive mean history/combined predictive gains; cross-ROI differences are heterogeneous and do not demonstrate reproducibility.

## Reused baselines

| Old representation | CA1 mean gain over stationary | DG mean gain over stationary |
|---|---|---|
| stationary | 0.00000000 | 0.00000000 |
| history | 0.06094216 | 0.05515729 |
| population | 0.07999827 | 0.07708141 |
| event | -0.00229385 | -0.00103368 |
| drift | 0.03933039 | 0.03127409 |
| combined | 0.08576643 | 0.08448630 |

All 1,638 scores, including every ridge and seed, remain in results/reused_M3_records.json and the original immutable files. The table uses preregistered fixed ridge0.1, all-three-seed mean. Old population includes own history; old combined duplicates own history.

## Fixed sensitivities

| View | Paired mice | own | population | stimulus_time | combined |
|---|---|---|---|---|---|
| primary | 13 | 0.00262621 | -0.00115169 | -0.00071894 | -0.00317072 |
| matched16 | 13 | 0.01021771 | -0.00120443 | 0.00039235 | 0.00748803 |
| rate_matched | 13 | 0.00437393 | -0.00135667 | -0.00076361 | -0.00275658 |
| boundary20 | 13 | 0.00229442 | -0.00113222 | -0.00051198 | -0.00351559 |
| boundary40 | 13 | 0.00126875 | -0.00107765 | -0.00072535 | -0.00489061 |

Shared-probe-only views are available for 13/13 mice; leave-probe-out views for 13/13. All per-mouse probe composition and all available views are retained, including unavailable group coverage. The probe views do not establish independent-probe replication. Sensitivity intervals are descriptive and are not selected to rescue the primary result.

## All registered fixed-predictor controls

| Control | Contrast | Observed pooled gain | Reference pooled mean | Pooled Holm p | Regional centered Holm p |
|---|---|---|---|---|---|
| B | combined | 0.04176245 | 0.03213130 | 0.0160 | 1.0000 |
| B | own | 0.03110484 | 0.02981267 | 0.0160 | 0.0160 |
| B | population | 0.00352154 | 0.00464138 | 1.0000 | 0.0160 |
| B | stimulus_time | 0.00225975 | -0.00737140 | 0.0160 | 1.0000 |
| O | combined | 0.04176245 | 0.08131440 | 1.0000 | 0.0160 |
| O | own | 0.03110484 | 0.05576699 | 1.0000 | 0.0160 |
| O | population | 0.00352154 | 0.00693066 | 1.0000 | 0.0160 |
| O | stimulus_time | 0.00225975 | 0.00442804 | 1.0000 | 1.0000 |
| S | combined | 0.04176245 | 0.04105627 | 0.0160 | 1.0000 |
| S | own | 0.03110484 | 0.03170945 | 1.0000 | 1.0000 |
| S | population | 0.00352154 | 0.00352305 | 1.0000 | 1.0000 |
| S | stimulus_time | 0.00225975 | 0.00155357 | 0.0160 | 1.0000 |
| T | combined | 0.04176245 | 0.03387704 | 0.0160 | 0.0160 |
| T | own | 0.03110484 | 0.02495026 | 0.0160 | 0.0160 |
| T | population | 0.00352154 | 0.00221319 | 0.0160 | 0.0160 |
| T | stimulus_time | 0.00225975 | 0.00375255 | 1.0000 | 0.4880 |

These 999-replicate control distributions preserve fixed trial membership. Temporal totals are exactly preserved. Condition/bin/order controls are conditional stress tests with exchangeability limitations. Control-specific p values are not independent confirmation of a CA1/DG biological difference and are not original M5 refit nulls. Complete distributions and confidence ranges are retained in exploratory_statistics.json and the native null JSON files.

## Numerical audit

{
  "original_definition_max_PG": 9.991795320990482e-08,
  "AD_original_definition_max_PG": 9.991795324806874e-08,
  "max_AD_scaled_error": 3.865431651951668e-15,
  "max_AD_objective_error": 1.3322676295501878e-15,
  "new_scientific_model_cases": 910,
  "new_scientific_unit_fit_attempts": 21476,
  "necessary_identical_endpoint_reconstruction_model_cases": 910,
  "necessary_identical_endpoint_reconstruction_unit_fits": 21476,
  "total_new_track_optimizer_unit_fit_executions": 42952,
  "original_M3_refits": 0,
  "original_offset_refits": 0,
  "all_910_coefficient_hashes_identical": true,
  "final_access": false
}

The first accepted implementation used a projected-step norm. A prospective supplemental certificate rebuilt identical endpoints and applied the unchanged original outward-gradient PG oracle. All 910 coefficient hashes match exactly; both executions remain counted. No original M3 or offset fit was repeated. Initial no-fit preflight failures caused by the incorrect nominal trial-count assertion, and the observability replay, are preserved with corrected exact-manifest checks and a regression.


### Figures

![Figure 1: Mouse-level primary differences](figures/primary_mouse_effects.png)

Figure 1. Individual mouse differences, equal-mouse means and whole-mouse percentile intervals. None of the four Holm-adjusted paired tests meets 0.05.

![Figure 2: Reused baselines](figures/reused_baselines.png)

Figure 2. All-three-seed mean scores at the registered common ridge; mouse bootstrap uncertainty. Full grids remain in A4.

![Figure 3: Registered sensitivities](figures/sensitivities.png)

Figure 3. Five frozen views, all with 13 eligible paired mice. No view replaces the primary test.

![Figure 4: Fixed-predictor falsification](figures/falsification.png)

Figure 4. Pooled reference means and 95% replicate ranges, compared with observed gain. Reference intervals are conditional null distributions, not mouse bootstrap uncertainty or independent experiments.

## 4. Discussion

The tractable representations show that past counts predict nominal curated-release activity in both provider-labeled subfields. The primary regional differences are mixed or inconclusive after the registered correction. The small other-unit mean-history contrast trends toward greater DG gain, but its corrected p value does not pass the four-hypothesis gate. This result cannot be promoted by its unadjusted p value, a descriptive interval or a favorable sensitivity. The own-history and combined contrasts vary substantially across mice. Negative, mixed and inconclusive evidence is part of the result rather than a reason to select another model or threshold.

Predictive dependence may reflect shared input, stimulus modulation, latent behavioral state, sampling, preprocessing and omitted interactions. Rate matching changes the selected population and does not exactly equalize rates. Boundary distances are label-based channel proxies; no independent histological assignment has been obtained. Multiple units and probes do not increase the independent mouse count. Conditional temporal and label/order stress tests depend on modeling/exchangeability assumptions and do not establish causality. Curated nominal exposure and whole-session upstream sorting prevent claims of native continuity or a completely naive acquisition pipeline.

The original recurrent-model numerical failures remain a separate limitation. Gradient validity did not make those optimizers converge, and the subsequent three-policy conditioning study remained inconclusive. The present GLM success does not retrospectively clear M4, complete original M5/M6, or validate NAP/CWP. The transparent PG-oracle implementation correction and all deterministic certification replays are retained, with exact coefficient equality and original thresholds.

Generalization is restricted to an exploratory within-release development cohort. All four hypotheses, model definitions, analysis code and acceptance criteria are frozen for a later protected final-mouse assessment. Final C/D are locked in this mission. A negative or inconclusive final assessment must be retained; no final-based replacement selection is permitted. An external cohort, independent anatomical registration and causal intervention would be separate future work.

## 5. Conclusion

This complete exploratory draft provides a numerically audited, narrower predictive analysis. It does not establish reproducibly different CA1/DG contributions under the registered primary multiplicity gate. Final validation remains prospective and unauthorized.

## Reproducibility and declarations

A1-A10 accompany the draft. Public saved-evidence reproduction regenerates mouse statistics and verifies all numerical/custody/hash records without opening neural counts or final data. Full neural reruns require the protected custodian/runtime and a fresh authorized execution registration; cached successful fits are deliberately reused. Provider data-access terms and institutional secondary-analysis declarations must be confirmed by the authors before submission; this draft does not invent an ethics approval, independent custodian or unrestricted raw-data redistribution license.
