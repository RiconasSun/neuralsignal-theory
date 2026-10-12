# Predictive Representations of Human Hippocampal Spiking: An Exploratory Benchmark of Discrete, Continuous, and Hybrid Models

NEURALSIGNAL INSTITUTE | Separately authorized manuscript-closeout track

Research status: exploratory development benchmark. Original P11-v2 R2 remains FAIL / DATA_INSUFFICIENT; original R3 is NOT EXECUTED. This document is not independent scientific validation.

## Abstract

Predictive neural representations can be compared without assuming that the brain physically implements a particular state-space architecture. We report an exploratory benchmark of human hippocampal population spiking from nine development patients, 23 sessions and 592 session-local units during verbal working memory. The frozen development analysis used 100-ms bins, causal observed histories and scheduled task covariates, with matched Poisson observation scores for strong baselines, a discrete hidden Markov model, a deterministic continuous recurrent model and a switching autoregressive hybrid. All 3,887 prescribed candidate/initialization fits across 57 configurations completed with recorded optimizer success. Exact small-model and gradient checks support numerical implementation, not biological validity or globally optimal fitting. For the strongest combined Poisson baseline and the three frozen family one-standard-error selections, patient-weighted development log likelihoods were -0.534921, -0.547176 (discrete), -0.568089 (continuous) and -0.546237 (hybrid) nats/unit-bin. Raw development maxima for larger discrete and hybrid configurations exceeded the baseline, demonstrating substantial selection-rule sensitivity rather than a stable regime verdict. Patient-level effects and saved confidence intervals are exploratory and postselection because development data were previously exposed. Required null suites were incomplete, and external admission failed when complete recording support could not be established for five of 52 candidate sessions. No final holdout or independent predictive validation was executed. This evidence-bounded benchmark supports transparent comparison of tractable predictive representations, but not a preferred hippocampal physical regime, neural primitives, NAP or CWP validation. [C01-C08]

## 1. Introduction

Human hippocampal recordings allow high-resolution investigation of working-memory population activity, but a statistical representation and a neural implementation are different objects. Persistent hippocampal firing and hippocampal-cortical coupling have been investigated in verbal working memory [1,2], and companion electrophysiological analyses examine interregional information flow [3]. Those findings motivate predictive modeling; they do not make discrete, continuous or hybrid latent descriptions mutually exclusive biological mechanisms.

The question here is deliberately narrower: under a specified observation model, causal context and development-data split, how well do several tractable predictive representations score the same hippocampal spike-count populations? A strong rate/history/task baseline is essential: additional dynamical structure should not be credited for predictive information that ordinary covariates already encode. Comparative prediction is potentially falsifiable through matched scores, rate-preserving controls and independent evaluation. In this study only the development comparison and its numerical/statistical documentation reached completion; the remaining requirements did not. [C03,C06,C07]

The manuscript closes an existing exploratory evidence record. It does not amend a failed gate, reopen a holdout or retrospectively label exploratory data as confirmatory. Its contribution is a fully disclosed benchmark and an auditable account of where numerical and external-data feasibility stopped. [C08,C09]

## 2. Related Work

The primary dataset is a derivative of the human medial temporal lobe recordings described by Boran and colleagues [1], with a related working-memory report [2]. The source material includes hippocampal, entorhinal and amygdala units; only explicitly hippocampal units enter this benchmark. Source spike sorting and curation precede the present development split, and the source does not distinguish single- from multi-unit activity for every exported unit. A relevant sorting-method reference is Niediek et al. [4]. These upstream decisions are source properties, not new train-only preprocessing guarantees. [C01,C10]

The external recognition-memory candidate was the NWB release associated with Chandravadia et al. [5]. Its task differs from verbal working memory, so a valid future test would be convergent evidence rather than direct task replication. Previously completed alternative-cohort audits considered natural-object recognition [6] and multielement episodic memory [7]; neither was admitted. This closeout performs no further dataset search. [C07,C08]

Our models instantiate distinct computational descriptions. Finite-state mixtures permit exact forward marginalization; deterministic observed-history recurrences provide a continuous predictive state without continuous-latent integration; switching autoregression combines categorical states with state-specific observed-history terms. These definitions follow the archived protocol and reference implementations [8], not a claim of new model theory. The limited source-grounded literature coverage is not an exhaustive review of hippocampal dynamics or proof of novelty. [C02,C09]

## 3. Data and Cohort

The primary source is NEMAR nm000363 v1.0.0, pinned at commit b054fbef57f9c4fb93477ecc5c88c6114dbc5662. OpenNeuro ds004752 v1.0.1 is a companion recording modality from the same patients, not an independent cohort. Subject and session identities follow the release crosswalk. The admitted development subset comprises nine independent patients and 23 sessions, with 592 session-local units. This number is not a count of unique neurons persisting across recording days. There were 622 training and 201 development-validation whole trials. [C01,C10]

Admission used explicit hippocampal anatomy, at least five train-selected units/session and at least 20 training spikes/unit. An explicitly authorized, metadata-coverage-based amendment changed the minimum development trials from 40 to 32, requiring at least 24 training and eight development trials. The original 40-trial failure was preserved. This amendment did not lower the external candidate's separate 40-trial requirement. No entorhinal/amygdala unit was silently pooled as hippocampus. [C01,C08]

{{PATIENT_COVERAGE_TABLE}}

Table 1. Coverage aggregated by patient. Unit counts sum session-local identities; sessions, trials and units are not independent population-inference observations. The complete 23-session table and frozen input hashes are in the supplement and A2.

![Figure 1](figures/F1_design_coverage.png)

Figure 1. Study design and coverage. The progression ends at exploratory reporting, not external validation. All patient/session coverage comes from saved QC summaries. [C01,C07]

## 4. Mathematical Model Definitions

For trial r, bin t and session-local unit u, y(r,t,u) is a nonnegative count and m(r,t,u) the expected count in a 100-ms bin. The common observation log probability includes factorial terms:

$$\log p(y\mid m)=y\log m-m-\log\Gamma(y+1).$$

Counts, not rates in hertz, are scored. A rate would be m/0.1; the frozen code's offsets already represent log expected counts. Conditional independence across units defines the joint population emission, while shared hidden states can induce marginal dependence. History and states reset at each trial. [C02,C03]

### 4.1 Strong Poisson Baselines

The stationary baseline uses each unit's training mean count. Regularized GLMs include own-unit log1p history at lags 1-5, scheduled task/elapsed-time context, trial-position drift, their combined design, and a full-population observed-history design. The covariate vector includes an intercept; event context contains elapsed time and its square, encoding/maintenance indicators, permitted set-size context and scheduled boundary impulses. The set-size term is enabled only when encoding begins. Context variation masks, load scaling and trial-position scaling are fitted on training data alone. [C02,C03]

$$\log m_{r,t,u}=w_u^{\mathrm{T}}x_{r,t,u}.$$

The stationary fit is unpenalized; the other baseline coefficients, including intercepts, use the registered ridge penalty. No response correctness, confidence, response time, future event or current scored count enters a causal predictor. [C03]

### 4.2 Discrete Representation

The discrete model has K=2 or 4 categorical states with an initial distribution and transition matrix. Its emission log mean is the shared train-fitted combined-GLM offset o plus a state-specific unit bias b:

$$\log m_{r,t,u}(s)=o_{r,t,u}+b_{s,u}.$$

The predictive state distribution is computed from prior observed counts. Current population emissions are scored before assimilation. With a predictive state prior pi(t), the increment is:

$$\ell_t=\log\sum_s \pi_t(s)\prod_u p(y_{t,u}\mid m_{t,u}(s)).$$

The forward recursion marginalizes all finite state paths exactly in log space; smoothing quantities are used for training gradients, not as future-informed validation predictions. Although the discrete extra emission has zero history lags, its shared combined offset still includes causal history. [C02,C04]

### 4.3 Continuous Predictive Representation

The continuous model is a deterministic observed-history recurrent state h of dimension d=1,2 or 4, not a stochastic Poisson latent dynamical system. Its initial prior state is zero, but known current context can make the first predicted state nonzero:

$$h_t=\tanh(Ah_{t-1}+B\log(1+y_{t-1})+Dx_t).$$

$$\log m_{t,u}=o_{t,u}+(Ch_t)_u.$$

Its score is an exact conditional product-Poisson score given observed past counts. There is no particle integration, plug-in latent posterior, variational bound or sampled continuous state. It measures causal one-step prediction, not a free-running six-second forecast. [C02,C04]

### 4.4 Hybrid Representation and Complexity

The hybrid model uses K=2 or 4 finite states and state-specific own-unit history coefficients with L=1 or 5:

$$\log m_{t,u}(s)=o_{t,u}+b_{s,u}+\sum_{l=1}^{L}a_{s,u,l}\log(1+y_{t-l,u}).$$

Observed-history conditioning leaves a finite-state exact forward marginal. This is switching autoregressive Poisson prediction, not a stochastic switching latent dynamical system. For U units and X context dimensions, extra free coefficients are (K-1)+K(K-1)+KU(1+L) for state models, and d squared +2dU+dX for the recurrence. The discrete model has L=0. Total reported complexity adds the shared-offset coefficients; it is a nominal coefficient count, not effective degrees of freedom or measured manifold dimension. [C02,C05]

![Figure 2](figures/F2_architectures.png)

Figure 2. Code-grounded architectures. All families use matched count observations and causal inputs, but their predictive states have different mathematical meanings. The continuous recurrent model is not the archived v1 PLDS. [C02]

## 5. Numerical Verification

The separately registered P11-v2 R1 code track recorded 220 oracle cases, 54 causal checks and 169 controlled fit runs. Its maximum normalized state score discrepancy was 1.1102230246251565e-15 and recurrent discrepancy 4.440892098500626e-16. R2's batch/scalar/exhaustive verification recorded 108 cases, score discrepancy 1.1102230246251565e-15 nats/unit-bin and finite-difference gradient discrepancy 3.1667389197020945e-11. These are controlled implementation checks, not experimental observations or global optimizer guarantees. The closeout copies this evidence; it does not rerun model fitting or numerical experiments. [C04]

Archived P11-v1 attempted stochastic latent inference with an unchanged 0.001-nats/unit-bin verification threshold. Original M4 and NUM-1/2/3 failures remain final. NUM-1's d=2 bootstrap evaluation failed; NUM-2 stopped at a controlled proposal oracle; NUM-3's independent quadrature comparisons and improved randomized evaluation still failed the registered conservative per-bin criterion. At 131,072 particles, the empirical NUM-3 acceptance statistic was 0.0011686586847694219, above 0.001. Agreement of finite references is not a proof of absolute accuracy, and high ESS is not likelihood accuracy. No v1 full-cohort hybrid/PLDS competition or preferred-regime result is inferred from these attempts. [C09]

![Figure 3](figures/F3_numerical_verification.png)

Figure 3. Numerical evidence and limits. The left panel contains saved normalized tractable score discrepancies; the right contains archived controlled NUM-3 empirical acceptance statistics. The latter are neither calibrated simultaneous confidence bounds nor biological measurements. [C04,C09]

## 6. Experimental Design

The evaluation retained the pre-existing training/development whole-trial partitions and excluded the old final test. All 60 bins of the pre-probe interval [-6,0) were scored. History is zero-padded at trial boundaries. A trial's normalized score sums log conditional population PMFs and divides by bins times units. Session means average whole trials; patient means average sessions equally; population summaries average the nine patients equally. This weighting avoids treating sessions or units as independent patients. [C01,C03,C06]

There were 57 configurations: 21 baselines, eight discrete, 12 continuous and 16 hybrid. All nonstationary candidates retained seeds 11,23,37; stationary had one exact fit/session. Thus each session had 169 fits, giving 3,887 prescribed fits overall. Ridge values were 0.001,0.01,0.1,1. Training minimized normalized negative log likelihood plus one-half ridge times squared coefficient norm, using bounded L-BFGS-B (coefficients within [-8,8], at most 500 iterations, ftol and gtol 1e-5). Initialization choice used training objective only; no favorable validation seed was substituted. [C03,C05]

The one-SE rule admits candidates within the hierarchical standard error of the best candidate's absolute development score. It prefers fewer total nominal parameters, then stronger ridge, then frozen order. This is not a paired-gain SE. The shared family offset is combined ridge 0.01; the strongest baseline comparator is combined ridge 0.001. Separately, the baseline-wide one-SE rule selected stationary Poisson (-0.5412912375626756). The cross-dynamical-family one-SE selection was the discrete K=2/ridge 0.01 model. These distinct recorded roles must not be interchanged. [C05]

## 7. Exploratory Results

### 7.1 Recorded Selected and Reference Scores

{{SELECTED_TABLE}}

Table 2. Four scores underlying the saved patient statistics. Higher log likelihood is better. The baseline is the strongest raw development-score reference, not the baseline-wide one-SE selection. The three dynamical rows are frozen family one-SE selections. Nominal parameters are equal-session/equal-patient means, including offsets. [C05,C06]

The strongest baseline scored above the selected discrete and hybrid models for eight of nine patients and above the selected continuous model for all nine. Mean selected-family gains over that baseline were -0.012255 (discrete), -0.033167 (continuous) and -0.011316 (hybrid) nats/unit-bin. Selected hybrid exceeded selected discrete by only 0.000939 on average, below the protocol's 0.01 practical-gain scale. These negative selected contrasts do not imply that every discrete or hybrid configuration performed worse. [C06]

### 7.2 Raw Maxima and Selection Sensitivity

{{RAW_MAX_TABLE}}

Table 3. Descriptive raw development-score maxima, distinct from frozen selections. The larger discrete and hybrid maxima exceed the strongest baseline. Their scores must not replace the selected candidates in the saved paired tests. The raw continuous maximum uses d=4 rather than selected d=1. All 57 configurations, including poorly performing high-ridge candidates, appear in Supplementary Table S1 and the full-precision CSV. [C05]

![Figure 4](figures/F4_predictive_performance.png)

Figure 4. Recorded summaries versus raw maxima. Circles and diamonds answer different selection questions. The vertical stationary reference marks the baseline-wide one-SE result. No independent holdout preference follows from either ranking. [C05,C06]

### 7.3 Patient Heterogeneity and Computational Diagnostics

{{PATIENT_EFFECTS_TABLE}}

Table 4. All saved patient-level paired effects, left-minus-right nats/unit-bin. D=discrete, C=continuous recurrent, H=hybrid, B=strongest combined baseline. Patient 05 shows positive D-B and H-B effects, unlike the other eight. Exact full-precision scores and effects are supplied; no individual interval is inferred from a population CI. [C06]

All 3,887 fits have recorded optimizer success, with no dropped failed seed. Aggregate saved fit time was 805.5225947985891 seconds; this is hardware/environment-specific cumulative training time, not a reproducible speed benchmark. The diagnostics include {{ONE_ITERATION_COUNT}} one-iteration records and {{FTOL_COUNT}} relative-objective termination records. Optimizer success can be ftol rather than small-gradient convergence; it does not certify identifiability, a unique solution or global optimality. Recorded design rank applies only to the first unit's design, not the joint population design. [C05]

![Figure 5](figures/F5_patient_heterogeneity.png)

Figure 5. All six paired effects across nine patients and their saved exploratory population confidence intervals. The heatmap has no bin/trial-level significance markings. [C06]

![Figure 6](figures/F6_complexity_frontier.png)

Figure 6. Every tested configuration on the nominal parameter/performance plane. The low-complexity one-SE selections and high-score raw maxima are both visible. Raw coefficient counts do not measure intrinsic hippocampal dimension. [C05]

### 7.4 Incomplete Null Tests and Failed Independent Admission

The registered null plan required 200 replicas for each of count-preserving bin permutation, circular time shift and task/event timing controls. Only eight full count-permutation cohort replicas completed before STOP. A total of 2,896 saved converged null fit records, including partial work, were preserved. The remaining count-null suite and circular/time-context suites were not completed. No null-calibrated significance, full null distribution or claim of surviving all controls is reported. The strong task/drift/history baselines are controls already in the development comparison, not substitutes for those missing null suites. [C07]

DANDI 000004 release 0.220126.1852 retained 52 frozen candidate sessions. Forty-seven had documented limited support envelopes; five had unresolved complete recording boundaries. First TTL markers in those five were four stimulus-onset code 1 events and one undefined code 99 event, not acquisition-start evidence. R2-C failed, R2-B stopped incomplete, and original R2 remained FAIL / DATA_INSUFFICIENT with R3 NOT EXECUTED. The later all-session metadata audit was INCONCLUSIVE and did not repair the gate. The original 60/40 external calibration/final split remained unchanged; no external spike training or final scores were accessed. [C07,C08]

The already completed OSF VH5KQ audit inventoried 2,585 files, 46 session labels and 15 patient filename labels; its published narrative/table discrepancy and missing unit/support/clock linkage prevented admission despite eleven published unit-count potentials. The Figshare multielement-memory candidate exposed one approximately 12.26-GB mixed archive without a verified session/recording metadata bundle. Both feasibility gates were INCONCLUSIVE. They are failed admission evidence for this project, not evidence that those biological recordings are absent or that a model family is false. No new search or alternative-cohort execution occurred during closeout. [C08]

![Figure 7](figures/F7_evidence_boundaries.png)

Figure 7. Completed evidence versus scientific boundaries. Controlled verification and development prediction are separate from incomplete nulls, failed external admission and unexecuted final validation. [C04,C07,C08]

## 8. Statistical Analysis

All population comparisons use one paired difference per patient (n=9). The saved analysis used 10,000 paired patient bootstrap resamples (seed 20261011), two-sided exact enumeration of 512 sign configurations, and Holm adjustment across six specified contrasts. Percentile intervals are 95% exploratory intervals; conditional patient/session intervals resample whole trials within sessions and are descriptive, not additional independent population tests. Symmetry/exchangeability is required for the paired sign-flip null. [C06]

{{CONTRASTS_TABLE}}

Table 5. Saved patient-level comparisons. P values and intervals are reported for transparency, not as confirmatory discovery. These calculations condition on previously selected configurations and do not repeat model selection inside the bootstrap. Holm adjustment does not remove development exposure, postselection bias, incomplete null controls, small-cohort uncertainty or absent external validation. [C06,C07]

Selection uncertainty is substantial: the one-SE criterion uses hierarchical uncertainty in absolute score, not the typically smaller uncertainty of paired gains. It can select strongly regularized candidates whose raw score is markedly below the grid maximum. These data therefore do not establish an ontology that survives alternative reasonable complexity policies, even though the recorded policy itself is reproducible. [C05,C06]

## 9. Limitations and Falsification Boundaries

First, development data were previously exposed through v1 and v2 engineering and analysis. A frozen later workflow cannot make earlier exposure disappear; the current comparisons are exploratory. No unused development subset or genuinely independent final result is claimed. Second, nine clinical patients are the population-inference denominator; repeated sessions, thousands of fits and hundreds of units cannot increase that denominator. Source curation includes both SUA/MUA without complete labels, clinically determined sampling and whole-session sorting. Trial-windowed spikes and anatomical metadata do not establish dropout-free per-unit observation. [C01,C06,C10]

Third, exact finite-state or deterministic likelihoods avoid the v1 continuous-latent numerical bottleneck by changing the model class. They do not validate stochastic PLDS/SLDS models or negate the archived numerical failures. Controlled oracle checks are finite and low-dimensional. Optimizer success is not global-optimum evidence, and nominal parameter counts are not effective complexity. Fourth, the shared offset and strongest-baseline ridge differ; history enters even the discrete model through that offset. The reported contrasts test complete frozen predictive pipelines, not a pure isolated effect of a categorical state. [C02,C04,C05,C09]

Fifth, the larger discrete/hybrid raw maxima outperform the baseline while the family one-SE selections do not. Any preference is conditional on grid, regularization and selection rule. Sixth, the required null suites did not finish, so firing-rate/event explanations were not exhausted. Seventh, external source-support uncertainty prevented independent physiological admission and prediction. Different tasks could support convergence but not direct replication. Missing metadata is not proof of unusable neural data. These limitations are central findings, not supplementary caveats. [C05,C07,C08]

The falsifiable stronger claim would require a locked independent predictive comparison, complete registered rate/time/context null suites and robust complexity-controlled advantages. Those prerequisites are unfulfilled. We make no causal neural-mechanism assertion and no claim that NAP, CWP or hippocampal neural primitives are validated. [C07-C09]

## 10. Discussion

This benchmark separates three questions often conflated in dynamical modeling: whether code scores the specified distribution correctly, whether a chosen representation predicts exposed development observations, and whether a biological hypothesis generalizes under independent controls. The first two have bounded evidence here; the third does not. A reproducible negative or incomplete benchmark is preferable to a preferred-regime narrative that bypasses a recording-support or numerical gate. [C04-C09]

The strongest baseline's competitive development score suggests that causal history, timing and drift deserve explicit comparison before crediting more elaborate dynamics. At the same time, the larger discrete/hybrid maxima show that the selected baseline advantage is not invariant across the grid. The right conclusion is sensitivity of predictive rankings to complexity/regularization policy, not universal superiority of a baseline or physical discreteness/continuity. One patient's reversed selected effects further cautions against treating a group average as a homogeneous hippocampal law. [C05,C06]

Future scientific interpretation would require genuinely independent recording-support metadata, a separately registered validation arm and completed controls. This sentence identifies missing evidence only; this mission authorizes none of those activities. The closeout ends with an exploratory manuscript, not a rescue workflow. [C08,C11]

## 11. Conclusion

A saved-evidence benchmark of nine patients and 23 hippocampal sessions permits transparent comparisons among 57 predictive configurations. The strongest baseline outscored the three family one-SE selections, while raw larger discrete/hybrid maxima exceeded it. This selection-sensitive exploratory finding does not establish a preferred hippocampal physical regime. Numerical verification, incomplete null tests and unsuccessful external admission are preserved together. MANUSCRIPT_COMPLETE is a documentation verdict; SCIENTIFIC_VALIDATION_PASS is false. [C01,C05-C09,C11]

## 12. References

{{REFERENCES}}

## 13. Supplementary Methods and Results

The companion supplement contains the full 57-configuration table, all patient scores and six paired effects, 36 conditional patient intervals, 92 conditional session intervals, 23-session coverage, optimizer summaries and a complete failure/holdout audit. Full-precision CSVs retain all 3,887 optimizer records. A1-A10 provide the frozen source/protocol map, dataset inventory, pipelines, baselines, holdout isolation, statistics, incomplete null record, QC/leakage, numerical limitations and one-command saved-only reproduction. Figure sidecars map every plot or schematic to explicit frozen input paths and SHA256 values. [C01-C11]

### Data, Code and Reproducibility

Only existing released-data derivatives and saved summaries are reused. The primary dataset's source metadata specifies CC-BY-SA-4.0; the relevant provenance and limitations accompany this package. Figures and tables regenerate offline from allowlisted saved summary files; no raw spike arrays, model training, new statistics, nulls or external scores are generated. Saved-only reproduction is not reproduction of experiments that never executed. Source implementation is available in the repository's preserved test-branch history [8].

### Ethics and Declarations

This closeout collected no new participant data. The primary source metadata reports informed consent and Zurich ethics approval PB-2016-02055 [1]. Public-data reuse does not certify every source preprocessing choice or future validation claim. Named authors, author contributions, funding, competing interests and submission approval were not provided for this manuscript; no assertion of absent conflicts or funding is invented. These administrative declarations require author confirmation before journal or preprint submission. Scientific content completion does not imply submission readiness. [C10,C11]
