# Predictive Structure of Neural Population Activity Across Mouse Hippocampal Subfields

Complete scientific manuscript draft following one frozen held-out-mouse assessment. Author identities, affiliations, contributions, conflicts, ethics/data-use declarations and submission approval require author review; draft completion is not journal acceptance or independent peer review.

## Abstract

We asked whether provider-labeled mouse hippocampal CA1 and DG differ in predictive contributions from own spike history, other-unit history, stimulus/time context and combined features. We retained a frozen 26-mouse allocation, separated exploratory development evidence (13 mice) from a prospective held-out assessment (13 additional mice), and reused C-calibrated nested Poisson models without retuning. Mouse-level inference used exact paired sign flips, four-hypothesis Holm correction and 10,000 whole-mouse bootstrap resamples. Own history: difference -0.00922685, 95% CI [-0.0287164, 0.0100107], Holm p=0.389404; Other-unit history: difference -0.00295291, 95% CI [-0.00542441, -0.000872426], Holm p=0.0634766; Stimulus/time: difference -0.00307211, 95% CI [-0.00598945, -0.00080272], Holm p=0.0644531; Combined features: difference -0.023568, 95% CI [-0.0470803, -0.00143493], Holm p=0.141113. None of the four regional hypotheses met every registered positive-claim condition. All mandatory sensitivity views and four 999-replicate conditional control suites were retained. Nonsignificance does not establish equivalence. Findings concern observational prediction in one curated release and do not establish causal interactions, independent anatomical localization or a recurrent dynamical regime.

## 1. Introduction

Neural population activity can depend predictively on a unit's recent activity, histories of other sampled units, and known trial context. Distinguishing these fitted contributions from a regional biological mechanism requires held-out prediction, nuisance controls and animal-level uncertainty. Provider subfield labels, selected populations and repeated trials create measurement and sampling constraints even when models predict well. We therefore ask a restricted question: do four predefined predictive gains differ consistently between CA1 and DG in held-out mice from the same curated release?

The original recurrent P12 model competition stopped at numerical gates. A separate tractable GLM track reused audited baselines and adopted nested, causal features. Development comparisons remained exploratory and none passed the four-test Holm threshold. The present evaluation retained all four hypotheses and acceptance conditions despite those outcomes. It contributes a fully reported within-release held-out assessment, including negative and mixed findings, rather than a claim of a new modeling method or a recovered recurrent-model result.

## 2. Methods

### 2.1 Data, allocation and recorded exposure

This is a secondary analysis of the frozen curated Allen Visual Coding Neuropixels release. Provider-labeled CA1 and DG units were analyzed during repeated drifting gratings in the functional-connectivity stimulus block. Allen documentation describes released spike-sorted units and quality metrics and cautions that a unit cannot always be equated with an isolated neuron [1]. We did not acquire a new dataset or claim independent anatomical registration.

The original salted mouse allocation is unchanged: 26 mice, 13 development and 13 final. Development A/B data and earlier scores had already been examined, so every development inference remains exploratory. Final mice were calibrated on their C partitions, and the single D assessment used their frozen evaluation masks. The final analysis covers 3,120 trials, 20 nominal 100-ms bins per trial, and 32 primary selected units per subfield, with identical CA1/DG trial membership. The score denominator is the actual scored nominal curated-release unit-bin count. It does not establish uninterrupted native acquisition or lossless raw spike recovery.

Original C-only unit QC requires finite coordinates and valid provider labels, 0.1-100 Hz, active-trial fraction at least 0.1, refractory-interval violations at most 0.01, and frozen timestamp-integrity requirements. Probe 846401834 and invalid exported-rate metadata remain excluded. Unit ranks, cap, minimum trial-per-condition rules and source/trial masks were frozen before evaluation. Upstream provider whole-session sorting is distinct from downstream held-out outcome isolation.

### 2.2 Frozen predictive representations

The six Poisson representations share a 39-column basis: intercept, seven condition indicators, nineteen within-trial bin indicators, linear and quadratic provider trial order, five log(1+count) own-history lags, and five other-unit mean-history lags. Histories reset at each trial and contain only prior bins. The population feature averages the other selected same-subfield units and excludes the target. It does not represent the full recorded population or a causal interaction. Earlier population GLM work motivates predictive history models in a different system [2]; it provides no hippocampal validation here.

O contains intercept and order; N adds condition/bin context; NH adds own history to N; NP adds other-unit history to N; F contains the full basis; OHP removes condition/bin context from F. All share their target-specific C-only means/scales and zero embedding in this basis. The four conditional gains are F-NP (own), F-NH (other population), F-OHP (stimulus/time) and F-O (combined). Predictive log likelihood includes the Poisson log factorial and is divided by actual scored unit-bins. Penalized fitting and unpenalized evaluation are distinct; these regularized predictive contrasts are not likelihood-ratio tests or a unique causal decomposition.

C coefficients were reused without fitting. Ridge remains 0.1 on non-intercept coefficients, bounds [-8,8], and original outward-gradient PG acceptance <=0.001 with independent derivative scaled error <=1e-5. N uses all three frozen seeds 11/23/37 and their coefficient mean, calibrated on C. Other models retain their registered deterministic solver and initialization. The complete C bundle comprises 290 case states, 21,716 original GLM unit attempts, 78 N seed fits, 26 coefficient-mean certificates and 40,104 endpoint certificates. No final coefficient was borrowed from development. All C states, scalers, selected units, masks and sensitivity configurations were sealed before D access.

### 2.3 Statistical unit, inference and robustness

Mouse is the independent unit. We calculate CA1-minus-DG conditional gains within each mouse and average equally across 13 mice. Two-sided paired sign-flip tests enumerate all 8,192 sign assignments. Their validity depends on paired-difference symmetry; repeated units and probes are not extra independent observations. Holm correction covers exactly four primary hypotheses. Whole-mouse paired percentile intervals use 10,000 bootstrap replicates, seed 120214, and 95% endpoints. Intervals are not simultaneous four-hypothesis coverage and are not equivalence intervals.

Required views are primary, first 16 frozen units, C-rate matching, and 20/40-micrometer boundary proxies. Matching pairs available units within absolute log-rate ratio <=log(2), with at least five units per subfield and at least eight paired mice per mandatory view. It does not exactly equalize rates and changes the selected population. Boundary distances are provider-channel label proxies, not independent histology. All leave-one-mouse-out primary means, shared-probe and leave-probe-out views, unavailable probe strata and residual rate mismatch are reported without favorable subset selection.

### 2.4 Four conditional falsification suites

Each mouse/subfield uses 999 fixed-predictor replicates for each suite. T redistributes each trial/unit total across its 20 bins under its C-fitted N rate profile and rebuilds causal histories. S permutes conditions within fixed provider-order blocks; B permutes bin labels within each unchanged trial; O permutes provider order within condition. Trial membership and assignments stay fixed, and no null model is fitted. T is conditional on the nuisance model and observed count totals; label/order controls require exchangeability assumptions. These are conditional stress tests, not exact causal randomization tests or completion of original M5 refit nulls.

All 104 mouse/subfield suites and 103,896 replicate evaluations are retained. Pooled one-sided exceedance p=(1+number(null>=observed))/1000 and centered two-sided regional-reference exceedance are corrected in separate 16-test Holm families. Reported reference ranges describe null replicates, not bootstrap confidence intervals or independent experiments. O remains a mandatory nuisance assessment and cannot rescue a failed relevant control.

### 2.5 Prospective acceptance and governance amendment

Each positive regional claim requires complete data/provenance/numerical/coverage gates; at least eight paired mice in every mandatory view; primary Holm p<=0.05 and a 95% interval excluding zero; the original development effect direction (own positive, the other three negative); matching directions in every required sensitivity mean and all 13 primary leave-one-mouse-out means; and both pooled and regional corrected p<=0.05 for a relevant common suite. Relevant suites are T for own/population, S or B for stimulus/time, and T or S or B for combined. Neither optimizer success, successful software execution nor a favorable unrelated control substitutes for these conditions. The original acceptance document remains byte-identical.

Before D access, the owner prospectively replaced offline Ed25519 signing, separate physical signing equipment, cryptographic one-time entitlement and multi-principal release with an owner-authorized trusted local host. This reduced technical access-control assurance is disclosed rather than retrospectively clearing past security failures. Existing records showed no prior D outcomes exposed to model-selection analysis, but cannot exclude unlogged administrator actions. Trusted custody had previously decoded whole-session vectors before sealing D. There is no independent third-party custodian and no protection against a malicious machine administrator.

Source identities, complete C hashes, exact D metadata, execution identity and original statistical rules were registered before access. Synthetic numerical oracles and a complete 290-state production-schema synthetic D rehearsal used immutable C coefficients without real D counts. An exclusive durable local reservation preceded real source access and prevented accidental reruns; it is not a cryptographically or independently enforced entitlement. The full assessment used authenticated original D envelopes and frozen selection only. No threshold, exclusion, model, hypothesis, solver, seed or control was chosen from D outcomes. Technical failures and earlier stopped attempts are retained. There was no C refit or recurrent-model rescue in this mission.

## 3. Results

### 3.1 Execution, numerical evidence and coverage

The assessment validly completed 13 final mice, 26 subfields and all 290 registered model/view states. All five mandatory views retained 13 paired mice. All 104 conditional null cases completed 999 replicates, and no model was fitted during evaluation. The immutable C seal passed the original numerical and provenance validator before and after execution. Synthetic execution was reported separately and supplies no biological observations.

### 3.2 Primary held-out regional contrasts


|Contrast|CA1 gain|DG gain|CA1-DG|95% CI|Exact p|Holm p|
|---|---|---|---|---|---|---|
|Own history|0.03047404|0.03970089|-0.00922685|[-0.02871643, 0.01001067]|0.3894043|0.3894043|
|Other-unit history|0.001711799|0.004664711|-0.002952912|[-0.00542441, -0.0008724256]|0.01586914|0.06347656|
|Stimulus/time|0.0008911144|0.003963222|-0.003072108|[-0.005989451, -0.0008027204]|0.02148438|0.06445312|
|Combined features|0.03507601|0.05864403|-0.02356802|[-0.04708026, -0.00143493]|0.07055664|0.1411133|



All values are nats per actual nominal curated-release unit-bin. Positive differences favor larger conditional predictive gain in CA1. The table reports every hypothesis, both p values and mouse uncertainty. Failure of a hypothesis does not establish equal physiology or absence of a biological effect.

### 3.3 Registered verdict and development comparison


|Contrast|Registered classification|Holm criterion met|CI excludes zero|Development direction|Sensitivity signs|All LOMO signs|Relevant corrected control|
|---|---|---|---|---|---|---|---|
|Own history|NOT VALIDATED / MIXED|No|No|No|No|No|Yes|
|Other-unit history|NOT VALIDATED / MIXED|No|Yes|Yes|Yes|Yes|Yes|
|Stimulus/time|NOT VALIDATED / MIXED|No|Yes|Yes|Yes|Yes|Yes|
|Combined features|NOT VALIDATED / MIXED|No|Yes|Yes|Yes|Yes|Yes|



None of the four regional hypotheses met every registered positive-claim condition. A primary statistical threshold alone is insufficient when direction, sensitivity, leave-one-mouse-out or relevant corrected controls fail.

All four final point estimates were negative, indicating larger mean fitted gains in DG in this cohort. Own history reversed the frozen positive development direction; its interval included zero and its sensitivity/leave-one-mouse-out signs were not consistently in that direction. Other-unit history and stimulus/time retained negative development directions, negative means in every mandatory sensitivity and every leave-one-mouse-out primary analysis. Their nominal intervals excluded zero, but their four-test Holm p values were 0.06347656 and 0.06445313. They therefore remain unconfirmed under the original gate. Combined features also retained its negative direction and robust signs, but its adjusted p was 0.1411133.

The combined-feature percentile interval excluded zero although its exact two-sided unadjusted p was 0.07055664. Percentile bootstrap intervals and exact sign-flip tests have different finite-sample calibrations; neither was substituted for the other. The registered rule required both the corrected test and the interval condition, and was applied unchanged. These descriptive intervals are not simultaneous four-comparison coverage.


|Contrast|Development mean|Development Holm|Final mean|Final Holm|
|---|---|---|---|---|
|Own history|0.00262621|1|-0.00922685|0.3894043|
|Other-unit history|-0.001151693|0.06933594|-0.002952912|0.06347656|
|Stimulus/time|-0.0007189372|1|-0.003072108|0.06445312|
|Combined features|-0.003170721|1|-0.02356802|0.1411133|



Development evidence remains exploratory because data and scores were previously examined. Final mice are distinct animals within the same recording release, not independent-laboratory replication. Development and final results were not pooled to select or rescue a claim.

### 3.4 Sensitivity and conditional-control results


|View|Mice|Own history|Other-unit history|Stimulus/time|Combined features|
|---|---|---|---|---|---|
|primary|13|-0.00922685|-0.002952912|-0.003072108|-0.02356802|
|matched16|13|-0.004035165|-0.003010425|-0.002592174|-0.0194676|
|rate_matched|13|-0.004815319|-0.003177447|-0.001965921|-0.02125817|
|boundary20|13|-0.007661279|-0.002821908|-0.002913629|-0.02104586|
|boundary40|13|-0.009246422|-0.002630431|-0.003074468|-0.02246293|



The supplement gives all view intervals, per-mouse differences, leave-one-mouse-out means, probe strata and C-rate residuals. Sensitivities are descriptive checks of the frozen claim, not a search for a replacement significant subset.


|Suite|Contrast|Observed pooled|Null pooled mean|Pooled Holm|Observed CA1-DG|Regional Holm|
|---|---|---|---|---|---|---|
|T|own|0.03508747|0.02644357|0.016|-0.00922685|0.016|
|T|population|0.003188255|0.002050154|0.016|-0.002952912|0.016|
|T|stimulus_time|0.002427168|0.004075867|1|-0.003072108|0.843|
|T|combined|0.04686002|0.036752|0.016|-0.02356802|0.016|
|S|own|0.03508747|0.03600536|1|-0.00922685|0.976|
|S|population|0.003188255|0.003203569|1|-0.002952912|0.976|
|S|stimulus_time|0.002427168|0.00161045|0.016|-0.003072108|0.09|
|S|combined|0.04686002|0.0460433|0.016|-0.02356802|0.09|
|B|own|0.03508747|0.03145869|0.016|-0.00922685|0.016|
|B|population|0.003188255|0.005866771|1|-0.002952912|0.016|
|B|stimulus_time|0.002427168|-0.008895971|0.016|-0.003072108|0.016|
|B|combined|0.04686002|0.03553688|0.016|-0.02356802|0.016|
|O|own|0.03508747|0.05877958|1|-0.00922685|0.016|
|O|population|0.003188255|0.004134664|1|-0.002952912|0.016|
|O|stimulus_time|0.002427168|0.003349915|1|-0.003072108|0.016|
|O|combined|0.04686002|0.0725474|1|-0.02356802|0.016|



Every T/S/B/O result remains reported, including unfavorable and nonsignificant references. Null mean comparisons and corrected exceedance tests answer different questions; none establishes a causal contribution. Full replicate distributions and every animal/subfield control are included in the saved evidence.

All four contrasts passed at least one originally relevant joint pooled-and-regional corrected control: T for own and other-unit history; B for stimulus/time; T and B for combined (both corrected p values 0.016 in each passing suite). This did not rescue any primary Holm failure. Condition-label S controls had pooled adjusted p=0.016 for stimulus/time and combined but regional adjusted p=0.09, so did not meet the required joint condition. Temporal T did not pass for stimulus/time, and order O did not pass the joint condition for any contrast. Bin B did not pass the pooled condition for other-unit history. These mixed nuisance-control outcomes remain explicit rather than selecting a universally favorable reference.

## 4. Discussion

None of the four regional hypotheses met every registered positive-claim condition. The primary estimates, their uncertainty and the individual acceptance failures define the permitted regional interpretation. In particular, a nonsignificant comparison cannot be turned into proof of equivalence, and a significant fitted contrast cannot bypass a failed robustness condition. Positive within-subfield predictive gains and regional differences are distinct estimands. The study's scope is fixed conditional Poisson prediction from a selected subfield population and known context, not information capacity or a comprehensive feature hierarchy.

The consistent negative other-unit and stimulus/time point estimates across development and final mice are a descriptive pattern, not confirmation under Holm correction. Own-history direction reversal and wide mouse-level uncertainty argue against a single stable regional ordering across predictive feature classes. Both subfields had positive average gains for all four fitted contrasts, yet this does not establish a reproducible CA1-versus-DG difference. The final assessment therefore supports a cautious mixed-evidence account: audited conditional prediction in both labeled subfields, directional patterns for some contrasts, and no regional hypothesis validated by every prospective criterion.

Histories may predict activity through shared drive, stimulus modulation, behavioral state, heterogeneous rates, recording or sorting artifacts, and omitted variables. Regularization and correlated covariates affect nested fitted gains. Provider-channel boundary proxies and probe sampling leave anatomical uncertainty. Rate matching retains residual differences and modifies the selected population. Multiple units, trials and probes do not expand the independent animal count. Conditional temporal redistribution preserves trial/unit totals and can retain history gain through count heterogeneity; nuisance-model and exchangeability assumptions remain limitations even for corrected positive controls.

This is a within-release animal holdout, not an independent laboratory or independently acquired cohort. Whole-session upstream processing limits acquisition-level naivety. The trusted-host governance amendment weakened technical separation while retaining frozen science and explicit recorded access history; local reservations do not prove administrator-resistant one-time access. All original prerelease and numerical failures remain visible. These qualifications constrain reproducibility and interpretation without changing the original statistical thresholds.

Original recurrent M4 failures were not repaired: the CA1 Continuous dimension-4, ridge-0.001, seed-11 endpoint had PG about 0.693 against 0.001. Its fixed finite-difference gradient check failed, and a later diagnosis identified finite-difference instability without establishing convergence. All three bounded optimizer/conditioning candidates remained nonconvergent. Tractable GLM evaluation does not retrospectively pass M4, original M5/M6, NAP or CWP. No causal mechanism, human validation or independent histological confirmation is claimed.

## 5. Conclusion

None of the four regional hypotheses met every registered positive-claim condition. The complete held-out effect table and registered decision matrix are the scientific outcome. Negative, mixed and inconclusive conditions remain part of the paper. A separate independently acquired/anatomically verified cohort and causal experiments would address different future questions; this mission performs no additional final assessment or retuning.

## Data and code availability

Original provider data are described by AllenSDK [1]. Exact source receipts, animal/trial/unit locks, calibration manifests, source hashes and all public scalar results accompany the repository. Protected count arrays, decryption keys and copied fitted-state bundles are not redistributed in Git. The public PowerShell command recomputes frozen statistics and validates saved hashes without opening neural arrays or rerunning D. A new checkout requires only public saved scalar evidence for that reproduction; it cannot silently substitute synthetic data for held-out observations.

## Reproducibility and author-review requirements

The A1-A10 supplement records protocol, dataset, pipeline, baselines, holdout audit, statistics, controls, leakage/QC, limitations and saved-only reproduction. Actual execution and saved reproduction are different evidence classes. The manuscript is complete as a draft when its artifacts pass rendering/content checks. The project owner must confirm author order/affiliations, actual contributions, conflicts/funding, provider data-use and any applicable institutional ethics determination before submission. No ethics identifier, trial registration, external custodian, affiliation or independent peer-review approval is invented.

## References

[1] Allen Institute. Visual Coding - Neuropixels, AllenSDK documentation. https://allensdk.readthedocs.io/en/latest/visual_coding_neuropixels.html (accessed 2026-10-15).

[2] Pillow JW, Shlens J, Paninski L, Sher A, Litke AM, Chichilnisky EJ, Simoncelli EP. Spatio-temporal correlations and visual signalling in a complete neuronal population. Nature 454, 995-999 (2008). doi:10.1038/nature07140. https://www.columbia.edu/cu/neurotheory/pdfs/Pillow_et_al_2008.pdf
