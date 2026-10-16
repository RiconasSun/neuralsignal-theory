# Discrete and Continuous Predictive Representations of Curated Prelimbic Activity during Aversive-task Pre-tone Epochs

Descriptive, post-amendment research manuscript. Author names, affiliations, contributions, conflicts and submission approval require owner review. This is a secondary analysis of an existing animal dataset; no new animal procedure was performed here.

## Abstract

Population prediction can compare compact representations without identifying biological state primitives. We compared a two-state conditional Poisson model, a fixed two-dimensional leaky-history model and five Poisson baselines in curated provider-labeled prelimbic (PL) activity during aversive-task pre-tone windows. A frozen allocation selected ten development and nine held-out animals from an original 25-animal source denominator, with eight operationally screened units per admitted mouse. Development A fitted models, B selected configurations, and E supplied exploratory evidence. Final models were fitted from scratch on C and scored once on D. This final stage is explicitly descriptive: its pre-D amendment was informed by development E, a failed conditional-B* generator and insufficient recent-event sensitivity coverage. It is not fully preregistered confirmatory validation. {{ABSTRACT_RESULTS}} All six primary/guard comparisons, negative evidence and retained controls are reported. The unavailable conditional reference and six-of-nine recent-event coverage failure permanently prevent affected broad confirmatory or validated temporal claims.

## 1. Introduction

Conditional neural prediction separates the information in spike history, other recorded units and observed context from the additional structure supplied by a representation. GLM formulations offer a transparent account of those covariates [2,3]. Our goal is a bounded comparison of specific predictive models, not a general discrete-versus-continuous ontology. Hidden-state likelihoods can represent persistent shared variation, while fixed leaky-history features provide a tractable continuous comparator [4]. Neither family is a comprehensive model of cortical dynamics.

We reanalyzed DANDI 000473 release 0.230417.1502, associated with Calvigioni and colleagues [1]. The present source target is curated PL population activity in recording-supported aversive-task pre-tone epochs. The source study's intervention-based findings are not findings of this secondary predictive comparison. We do not certify awake-only state, passive sensory coding or decision/choice mechanisms in these selected windows.

The three original comparisons are Discrete minus B4, Continuous minus B4 and Discrete minus Continuous. Interpretation guards compare each family with the strongest B-selected baseline B*, and Discrete with the static state-mixture comparator S. The latter includes the same history-dependent B4 offset: it is static in the added state transition, not a model without spike-history dependence.

## 2. Methods

### 2.1 Dataset, admission and allocation

The source release contains 25 animals in the retained disposition denominator. Source, recording support, known masks and anatomical eligibility yielded 19 fixed candidates: ten development and nine final mice, without replacement after neural QC. One simultaneously recorded probe and one recording per mouse are used. PL includes provider laminar PL labels; labels and sorting are not independent histological or single-neuron-purity certificates. Source assets, ETags, release and unit/epoch identities are frozen in the accompanying manifests.

For each candidate the first 120 eligible nonoverlapping three-second pre-tone epochs were retained. Development uses A60/B30/E30; final mice use C60/D60. Partitions are chronological and expose extrapolation/drift. No final D outcome enters admission, unit ranking, scaling, fitting or selection. The selected eight units are the first passing numeric unit IDs. A/C-only operational QC requires at least 50 spikes, 30 valid within-epoch adjacent intervals, 12 occupied epochs, rate 0.1-100 Hz, refractory fraction for intervals below 1.5 ms at most 0.01, finite timestamps and strictly ordered within-window times. All 211 original attempted unit screens, including 59 failures, remain recorded; 152 units passed across 19 admitted mice.

### 2.2 Counts, history and nuisance features

Counts use half-open 100-ms bins, 30 per epoch. Five initial bins warm up history/filtering;25bins are scored, including zeros. E has 6,000 nominal curated-release unit-bins/mouse; C and D each have 12,000. Scores are joint Poisson log predictive likelihoods including log-factorials, divided by actual nominal unit-bins. They are not nats/spike or evidence for an isolated biological neuron.

History uses strictly past own/other-unit sums in lag groups1,2-3,4-5, with epoch reset. B3 retains all seven other units separately. The11nuisance covariates comprise epoch clock v,v-squared,sin/cos; session order u,u-squared; log1p prior-tone age capped60s; and preceding30s tone/noise/air-puff/opto onset counts, all strictly prior to the bin. Pre-tone sampling conditions on a future tone offline and does not establish real-time anticipation. Non-intercept features use A/C population means/SDs, including warmup; zero-SD coordinates become0. B/E/D transformations use those frozen scalers without evaluation-based clipping.

### 2.3 Models, selection and estimation

B0 has 8 stationary intercepts; B1 adds context (96 parameters), B2 own-history (32), B3 other-unit history (176), and B4 context plus own/other histories (288). The Poisson mean is exp(eta), per100-ms bin. The mean scored negative log likelihood adds ridge/(2*8) times squared non-intercept coefficients; intercepts are unpenalized. All fitted coefficients are bounded[-8,8]. Development B one-SE rules select among ridges 0.1/1/10, with fixed complexity/larger-ridge/seed tie rules. B*=B2. Selected baseline ridges are B0=.1placeholder,B1=10,B2=.1,B3=1,B4=1; these and all model choices were frozen before D, with no E/D tuning.

Discrete adds 16 emission shifts to the same frozen B4offset. A two-state transition matrix has diagonal p and off-diagonal1-p; p=.9was B-selected from .5/.9/.98. The epoch prior is(.5,.5). Exact causal log-sum-exp forward prediction precedes current-count assimilation; no smoothing is used. S uses p=.5with the same 16 coefficients/B4offset. Its ridge and Discrete ridge are.1.

Continuous adds 16 readout coefficients from a fixed 2D leaky-history state. Counts are standardized with A/C-only moments; a positive-diagonal QR projection Q is fixed by selected seed 23. The state uses strictly previous counts, h_t=R*h_(t-1)+(I-R)*Q-transpose*z_(t-1), R=diag(exp(-.1/tau)), tau=(.1,.3) seconds. State moments also come only from A/C. Its ridge is 1 and readout initialization is zero. Fixed projection/timescales are model choices, not uncounted fitted recurrent parameters. The families compare restricted representations with matched 16 added coefficients, not unrestricted dynamical classes.

All original fitting budgets and numerical checks remain unchanged. L-BFGS-B uses maxiter 2000, total calls 100000, maxls 40, maxcor 10, ftol 1e-12, gtol 1e-5 [5]. Original outward-bound projected gradient must be<=.001. Analytical derivatives are independently checked with Autograd 1.8.0 and bound-aware fixed-h 1e-4 finite differences at initialization, first callback and endpoint, tolerance<=1e-5. A step scan is diagnostic only. Final calibration has 15 baseline + 3 Discrete + 3 S + 1 Continuous fits/mouse, 198 total: seeds 11/23/37 for each baseline/emission model, minimum C-objective/lower-seed tie choice; selected Continuous projection has one zero-start fit. No development coefficient transfer, averaging, optimizer rescue or repeated failed fitting is allowed.

### 2.4 Prospective descriptive amendment and access

Before any final C model fit or final D outcome, a separate owner-authorized descriptive protocol preserved the original M6failure, the documented B* generator instability and the recent-event six-of-nine versus required eight-mouse failure. Original broad confirmatory restrictions remain INCONCLUSIVE. Only the failed four-null completion execution prerequisite was removed from the new descriptive route. The original gate records were not edited or upgraded. This amendment was explicitly informed by already examined development E and these failures; it cannot be presented as an untouched confirmatory design.

Complete C states, numerical certificates, units, scalers, masks, original epochs and sensitivity definitions were sealed and independently reviewed before D. A trusted local once-only marker precedes D extraction/scoring; no second evaluation or post-D retuning is permitted. The original NWB reader transiently decodes selected units' full-record timestamp arrays under owner permission, then cuts authorized windows; zero underlying D-byte access before extraction is not claimed. Final D outcomes were withheld from fitting/selection. Hash-bound logs are research controls, not independent third-party custody or malicious-administrator protection.

### 2.5 Statistics and controls

Mouse is the independent unit, with equal-mouse mean paired gains. Exact inclusive enumeration has2^9final sign patterns and 2^10 development patterns. Its validity requires fair conditional signs/joint sign symmetry, not merely a zero population mean; model labels were not randomized. Two separate Holm families contain the three primaries and three guards [6]. Joint 10,000 whole-mouse resamples use seed 130041 and linear percentile 95%intervals [7]. Direction counts,>=75%criterion and all leave-one-mouse-out means are retained. Sampling/sign assumptions are limitations, and neither significance alone nor a failed test establishes biological validity or equivalence.

Three unchanged 999-replicate stress procedures use seeds 130101/102/103: per-unit/per-epoch permutation within six 500-ms strata; history/filter donors from another same-partition epoch within original ordinal quartiles; and permutation of the entire nuisance trajectory within partition. Counts/target outcomes and causal HMM update ordering follow the original definitions. These are assumption-dependent stress references, not automatically randomized biological null tests. Exact dyadic mouse-effect totals and exact nominal95%linear reference quantiles retain strict comparison rules.

The original fourth control sequentially simulated B*=B2with seed 130104. It failed on the first replicate's fourth mouse and is FAILED/UNAVAILABLE, with no replacement or computed conditional p/Holm2value. A separately authorized one-prefix diagnostic matched all nine earlier score labels for each of the first three mice and reproduced an original count-feedback path: mouse 156130, epoch 94, unit 191, bin 15; previous count 9,702,754 produced eta 3,478,515.735 above log(float64max)709.783. Scaling, lag construction and update order matched the intended generator. This finite-path numerical instability is not an asymptotic theorem or biological runaway. Diagnostic draws never entered M6reference statistics. No clipping, alternative seed/draw or new baseline was used.

### 2.6 Sensitivities

Mandatory panels retain first4units, four nearest training-median-rate units, stricter refractory<=.005, PL5/PL6a, time shifts-0.1/+0.1s, and strict whole-epoch recent-event exclusion. At least 8 final mice must each retain>=10epochs and>=4units. Thresholds, masks and subthreshold rows are unchanged. Unit omission uses original source masks/standardized zero, restricted shared B4offset and retained-unit emissions. Shifted windows retain original parent/partition, reject support/mask/overlap/cross-partition violations, reset history and score only full bins ending by original tone; +.1typically has29full bins/24scored. Recent-event restriction excludes epochs with known onsets in[start-5,stop), with target tone at stop excluded and lower boundary included; no duration or replacement epoch is invented. Only 6 of 9 mice meet its coverage, permanently withholding affected broad confirmation.

Session-order quartiles, provider-active status, laminar labels, raw-DV rank and documented source condition are descriptive. Genotype was not decoded, not certified absent; coordinate physical units are unverified. With one probe/mouse, leave-probe-out repeats leave-mouse-out and is not independent probe replication.

## 3. Results

### 3.1 Calibration and complete reporting

{{CALIBRATION_RESULTS}}

### 3.2 All primary and guard contrasts

{{CONTRAST_TABLE}}

{{RESULT_INTERPRETATION}}

![Equal-mouse descriptive effects in development E and final D. Intervals are whole-mouse percentile 95%; development and final animals differ. No confirmation status is inferred from interval position.](figures/effects.png)

### 3.3 Animal-level heterogeneity

{{MOUSE_RESULTS}}

![All final mouse effects for the original three primaries. Points represent mice, not neurons or independent probes. No animal is removed because its effect is unfavorable.](figures/mice.png)

### 3.4 Retained controls and unavailable reference

{{NULL_RESULTS}}

### 3.5 Mandatory sensitivities

{{SENSITIVITY_RESULTS}}

## 4. Discussion

{{DISCUSSION_RESULTS}}

The final assessment addresses conditional prediction by specific small representations in selected curated PL windows. A Discrete-versus-B4gain, if present, need not survive comparison with the strongest B-selected baseline or static state mixture; all guards are shown rather than substituted for a failed primary. Persistent-state filtering could capture omitted arousal, movement, shared input, trial structure or memory, without supporting biological discrete primitives. Continuous is a fixed low-dimensional feature family rather than a general continuous latent process. These comparisons do not adjudicate the ontology of neural computation.

### 4.1 Limitations and failures

The descriptive scope was amended after development E and two required failures were known. The final animals provide held-out-animal descriptive evidence under fixed models, but not complete original confirmatory validation. The conditional reference is unavailable, recent-event coverage fails unchanged 8-mouse admission, and broad positive/validated-temporal claims remain INCONCLUSIVE even for significant component tests. Single-lab, selected animals, one probe, limited unit count, provider anatomy/sorting, unverified coordinate units, genotype not decoded from the saved source and unknown state/movement restrict generalization. Bootstrap precision and sign-test assumptions are not independently established by model convergence.

Historical P12 M4 optimization failures remain INCONCLUSIVE; this tractable P13fixed-model track does not rescue them. Original P13 source/admission and M6numerical failures remain archived. Passing current numerical fitting or completing a descriptive D bundle cannot upgrade those scientific verdicts. No causal mechanism, independent-laboratory or human replication, NAP/CWPproof, physical state atom or equivalence is claimed.

## 5. Conclusion

{{CONCLUSION_RESULTS}} The useful endpoint is a complete description of predictive scores, uncertainty, guards, retained controls and unresolved references. Affected broad confirmation and validated temporal claims remain withheld.

## Data and code availability

DANDI 000473 release 0.230417.1502, DOI 10.48324/dandi.000473/0.230417.1502, is the frozen public source [1]. This analysis preserves asset/ETag/epoch/unit identities, saved numerical evidence and historical failures in https://github.com/RiconasSun/neuralsignal-theory on the reviewed test history. Current task files are in paper13_descriptive_final1. Raw full-record caches are excluded from Git. Saved results, tables, figures and hash manifests reproduce reporting independently of any new fit or D evaluation. Real C/Dentry points are consumed and must not be rerun. See the supplement for exact commands and scope.

## Ethics, contributions and disclosures

This is analysis of an existing curated animal-data release; source-study approvals and source documentation govern its original experiments. No new ethical approval or exemption is invented for this manuscript. The project owner must verify applicable secondary-use obligations, author identities/affiliations/contributions, conflicts, acknowledgments and the final submission text. Internal independent review is engineering/scientific review by a separate agent, not external peer review or independent laboratory replication. Manuscript completion does not authorize submission or establish original scientific validation.

## References

[1] Calvigioni D, Fuzik J, Le Merre P, et al.(2023). Esr1+ hypothalamic-habenula neurons shape aversive states. Nature Neuroscience 26:1245-1255. https://doi.org/10.1038/s41593-023-01367-8. Data: https://doi.org/10.48324/dandi.000473/0.230417.1502.

[2] Nelder JA, Wedderburn RWM(1972). Generalized Linear Models. JRSS A 135:370-384. https://doi.org/10.2307/2344614.

[3] Truccolo W, Eden UT, Fellows MR, Donoghue JP, Brown EN(2005). A point process framework for relating neural spiking activity to spiking history, neural ensemble, and extrinsic covariate effects. J Neurophysiol 93:1074-1089. https://doi.org/10.1152/jn.00697.2004.

[4] Rabiner LR(1989). A tutorial on hidden Markov models and selected applications in speech recognition. Proceedings of the IEEE 77:257-286. https://doi.org/10.1109/5.18626.

[5] Byrd RH, Lu P, Nocedal J, Zhu C(1995). A limited memory algorithm for bound constrained optimization. SIAM J Sci Comput 16:1190-1208. https://doi.org/10.1137/0916069.

[6] Holm S(1979). A simple sequentially rejective multiple test procedure. Scandinavian J Statistics 6:65-70. https://www.jstor.org/stable/4615733.

[7] Efron B(1979). Bootstrap methods: another look at the jackknife. Annals of Statistics 7:1-26. https://doi.org/10.1214/aos/1176344552.
