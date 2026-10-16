# Supplementary information

Predictive Structure of Neural Population Activity Across Mouse Hippocampal Subfields

Complete A1-A10; all reported animal and conditional-control outcomes.

## A1 Frozen protocol

# Predictive Structure of Neural Population Activity Across Mouse Hippocampal Subfields

Mission P12-PREDICTIVE-STRUCTURE-V2; exact base c6384a114c1a7ced2045d07edf56545f160508f2.
This is a separately registered exploratory Method Paper track. It cannot clear original M4 failures, establish a dynamical regime, identify a causal mechanism, or validate NAP/CWP.

## Exposure and preservation

All prior P12 commits, numerical diagnoses, failed attempts and scientific gates remain immutable. The frozen 26-mouse allocation (13 development,13 final), trial identities, source masks, unit QC/cap/hash ranking, excluded probe and final holdout policy remain unchanged. Development A/B and some model scores have already been examined; all development inference is exploratory, including analyses registered here. Final D remains unexposed and locked; no C fitting or final release is authorized here. Only copied development A/B may enter the existing zero-capability native analysis role. Public metadata must be restricted to these 13 mice before export.

## Models and primary estimands

Reuse all 1,638 converged amended M3 fit records and all 78 converged shared-offset states after exact hash, identity, numerical and scoring audits. Successful M3/offset fits are not rerun. Report all six old models and all ridge/seed scores. Fixed-ridge descriptive comparison uses ridge 0.1 and the equal mean over seeds 11/23/37; stationary uses the same seed mean. Old population includes own history and old combined duplicates it; neither estimates a clean conditional contribution.

Register new small nested Poisson GLMs. Let O be intercept + provider trial order/599 and its square. Let C be seven condition indicators and nineteen nominal within-trial bin indicators. H is five causal log(1+own count) lags, reset at each trial. P is the mean of the five log-count histories of all OTHER selected same-ROI units, excluding the target. N=O+C, NH=N+H, NP=N+P, F=N+H+P, OHP=O+H+P. Features have a shared A-only scaler, intercept unscaled. The maximum dimension is 39 per unit. P defines a specific aggregated other-unit representation, not arbitrary complete population information. No interactions are implied. N reuses the frozen all-seed mean offset weights where data/features are identical; O,NH,NP,F,OHP are new fits.

Primary gains on B: own=LL(F)-LL(NP); other-population=LL(F)-LL(NH); stimulus/time=LL(F)-LL(OHP); combined=LL(F)-LL(O). Secondary joint history=LL(F)-LL(N), total=LL(F)-LL(stationary). Scores include the full Poisson log factorial and divide by actual scored nominal curated-release unit-bins. Each unit-bin is one 0.1-second nominal bin in the first two seconds of a fixed trial. Subsets use their actual K units, with K matched across ROIs; unscored units are never imputed into denominators. Regularized training objective is negative full Poisson LL/(A trials*20) per unit plus 0.1/2 times squared non-intercept coefficients. Bounds [-8,8]. Reduced models embed with zeros into the same full scaled basis, preserving the original new-track likelihood, penalty and bounds exactly. This new GLM architecture is separate from the original M4 architecture.

## Frozen numerical policy

Deterministic per-unit box-constrained Newton with exact Hessian, initial intercept log A mean clipped to bounds, other coefficients zero. Maximum 100 accepted iterations, 4,000 objective calls per fit. At each step freeze outward-gradient active-bound coordinates, solve free Hessian Newton equation; use projected gradient descent if the Newton direction is not descending. Project to [-8,8]. Armijo coefficient 1e-4, step 1 halved at most 40 times. No objective-only early stopping. Internal PG target 1e-7; scientific PG <=0.001, optimizer success, finite objective/score, bounds and independent gradient scaled error <=1e-5 are mandatory. Independently propagate exp derivatives and ridge derivatives at each new endpoint; central FD at fixed 1e-5 and 1e-6 on synthetic full-coordinate fixtures, plus independent scalar Poisson and causal/nesting/order oracles. Analytic Poisson oracle <=1e-12, future perturbation <=1e-12 and batching/order <=1e-10 are unchanged. Total phase wall limit 43,200 seconds, one fit attempt per registered case; no replacement models, fit retries or budget increases. A critical numerical/data/custody failure stops new scientific evaluation and is retained. Historical recurrent FD instability is not retroactively waived.

## Mouse-level analysis

Thirteen fixed development mice; CA1 minus DG paired within mouse. Equal weight per mouse, not per unit, trial or probe. Four primary two-sided paired sign-flip tests enumerate all 2^13 sign assignments; Holm correction across the four primary tests. Whole-mouse paired bootstrap 10,000 resamples, percentile 95% exploratory intervals, RNG seed 120214. Also report all 13 leave-one-mouse-out means, every signed effect, negative/mixed/inconclusive results and all unadjusted and corrected p values. Sign-flip symmetry/exchangeability is an assumption, not established by repeated units. At least eight eligible paired mice are required for any group contrast; no reallocation/replenishment. No development p value becomes confirmatory.

## Frozen sensitivities and nuisance controls

Primary equal 32-unit cap is audited; repeat with first 16 hash-ranked eligible units per ROI. A-rate matching: greedily pair CA1/DG units in frozen hash order to the closest unused A-rate DG unit, tie by frozen order, only absolute log rate ratio <=log(2); at least five pairs. Report remaining rate mismatch and changed estimand; matching is not perfect rate equalization. Anatomy proxy excludes units with undefined nearest-other-label vertical distance or distance <=20, then <=40 micrometers. Equal K=min eligible counts across ROIs by frozen hash rank; >=5 per ROI. Each boundary and rate sensitivity needs >=8 paired mice, otherwise STOP with exact scientific limitation. Distances are channel-label proxies, not independent histology or true anatomical boundaries.

Probe dependence: report every selected unit/probe composition. For each mouse assess a shared-probe-only view using the probe maximizing min(CA1,DG count), deterministic numeric-probe-ID tie break; report availability with >=5 per ROI. Leave one probe out for each original selected probe when >=5 units remain per ROI, equal K. Do not claim independent-probe replication from unavailable strata. These probe views are assessments with explicit coverage, not substitute animal sample size. For unchanged target outcomes/context/H, reuse O,N,NH exact selected coefficient rows; refit only NP,F,OHP when the other-unit pool changes. No unselected unit is added, no B-dependent selection. All views use identical trial identities/masks. Stimulus/time/order confounds are addressed by the nested contrasts and registered disruption controls, not by causal attribution.

## Registered falsification

999 fixed-reference B disruptions per mouse/ROI/suite, RNG derived from SHA256(mission|session|region|suite|replicate). These are fixed-predictor falsification tests, not the original M5 refit nulls and not exact model-free randomization inference. No null fits or model selection. A-fit/scaler/predictors remain frozen, B trial identities and assignments stay fixed.

T: for each B trial/unit preserve its integer total exactly and redistribute across its 20 bins with multinomial probabilities proportional to the A-fitted N rate profile; recompute causal H/P and full scores. This tests temporal-history predictions under a conditional nuisance-only count model, with possible nuisance misspecification/conditioning-induced dependence disclosed. S: permute condition labels within each fixed block floor(provider order/100), outcomes/time/H/P unchanged. B: permute within-trial bin labels independently, outcomes/causal H/P/order unchanged. O: permute provider order values within each condition, outcomes/time/H/P unchanged. None reassigns a trial between A and B or alters primary trial membership. Count-preserving invariants and finite predictions are mandatory. Report each suite's mean gain and CA1-DG reference distributions for all four primary contrasts; one-sided pooled-gain exceedance p=(1+number(null>=observed))/1000 and two-sided centered regional-reference exceedance with absolute statistic. Holm across 16 pooled-gain tests and separately across 16 regional-reference tests. These p values are exploratory stress-test summaries conditional on the stated null assumptions. Unsuccessful falsification yields unsupported/mixed hypotheses, never hidden or relabeled. Technical critical failure stops the track. No claim requires a favorable null.

## Stopping, manuscript and final boundary

Before any new scientific evaluation, seal this protocol, atomic baseline, preserved-artifact manifest and implementation identities. First audit historical compatibility and sensitivity coverage. A critical source integrity, fixed-cohort, mandatory coverage, custody or numerical gate failure stops subsequent fits/analysis with the exact limitation; do not fabricate a complete results manuscript. If gates pass, complete an exploratory manuscript, scientific figures, A1-A10, saved-only one-command PowerShell reproduction and review. Freeze all four hypotheses, six new model definitions, ridge/bounds/numeric policy, trial/unit policies, nulls/statistics and analysis code for a separate final-mouse plan: fit only final calibration C after separately authorized access, score D once under the protected role, no D tuning. Do not unlock final evaluation in this mission. Stop after the draft/freeze or an earlier critical scientific stop. No Discrete/Continuous/Hybrid rescue or M4 competition is authorized.


# Locked final-mouse validation plan — authorization required

No calibration C fitting, final D export, decryption, scoring, neural QC or final evaluation is authorized by this file or mission. This is a prospective plan, not an access grant. The final 13 mice remain exactly those in the frozen 26-mouse allocation. No new mice, allocations, trials or units may replace excluded cases.

After separate final-evaluation authorization under the existing custody policy, a trusted custodian may issue calibration C only to the zero-capability role. Apply the frozen metadata masks, C-only unit QC, salted unit cap, causal features and C-only scaler. The five new fitted models O/NH/NP/F/OHP use the identical registered ridge, bounds, initialization and box-Newton policy; their scientific acceptance uses accepted_fit.py and the ORIGINAL outward-gradient PG definition, not the solver's internal projection-step norm. N must be calibrated on C rather than borrowing development weights: preserve the exact 29-feature offset fit policy from paper12_m4offset1/patched/task_offset.py and optimizer_amendment.json (ridge0.1, seeds11/23/37, L-BFGS-B ftol1e-10, gtol1e-5, maxiter2000, maxfun80000, no retries), require all three seed fits to pass the unchanged numerical gates, and use their fixed coefficient mean with an independent original-PG/AD certificate. No new numerical policy or winning seed is substituted. Preserve all calibration failures and stop if any critical numerical or coverage gate fails. No D counts or scores may choose models, ridge, seeds, features, numerical settings, units, trial masks or hypotheses. Freeze successful C states, source/configuration hashes and all trial/unit selections before any D scoring.

The four registered two-sided primary contrasts, their sign convention CA1-minus-DG, equal-mouse aggregation, 10,000 whole-mouse bootstrap and four-test Holm/sign-flip family remain frozen regardless of development p values. All four contrasts must be reported once, not only development-significant hypotheses. Sensitivities use C-only rates or metadata with original minimum5/8 gates; probe assessments remain descriptive. The proposed single final assessment includes all four fixed-predictor D falsification suites with999 replicates and the same separate16-test families; the separate authorization must approve the complete plan before D release. No optional or result-selected D control is added later.

Frozen proposed positive-claim criteria: complete source/custody/numerical/coverage gates; at least8 paired final mice in every mandatory view; D primary two-sided four-test Holm p<=0.05 with whole-mouse95% interval excluding zero; a D effect sign consistent with the frozen development point estimate (own positive, population negative, stimulus/time negative, combined negative); the same sign in the four fixed unit/rate/boundary sensitivity means and all leave-one-mouse-out primary means. These sign checks are prospective replication/robustness conditions, not one-sided replacements for the two-sided tests. A relevant registered conditional falsification also must pass its already-frozen16-test correction: T for own/population; S or B for the joint stimulus/time contrast; T or S or B for combined. Require both pooled-gain and centered regional-reference corrected p<=0.05 for the relevant suite. These disjunctions are frozen now and every suite remains reported. O is a mandatory reported nuisance-order assessment and cannot replace a failed relevant control. Conditional-null assumptions remain limitations even if these criteria pass. If any condition fails, retain a negative/mixed/inconclusive result and do not call the particular regional contrast reproducible. No equivalence or causal claim follows from a failure or a pass.

One protected D assessment uses fixed trial assignments and actual nominal unit-bin denominators. Report every mouse, all positive/negative/mixed/inconclusive results and all failed calibration cases. No D retuning or second exposure to select replacements. A final scientific claim requires complete relevant data/numerical/coverage gates and the registered inferential criterion; successful software execution alone is not validation. Failure to replicate, nuisance-control failure or anatomical/probe limitation is retained as such. One-cohort curated-release validation remains distinct from independently labeled histology, another laboratory, causal mechanism or human translation.

The code/config/hypothesis freeze manifest produced at closeout will identify the exact candidate for any separately authorized final protocol. This plan does not resume original M4, M5, M6 or recurrent optimizer rescue. Stop now for separate authorization.


The new owner trusted-host amendment changes governance only; historical authorization restrictions above remain historical, not current permission. See mission human_authorization.txt and registration.json.

## A2 Dataset manifest


|Final mouse|Session|D trials|Primary CA1 units|Primary DG units|
|---|---|---|---|---|
|754477358|768515987|240|32|32|
|759711152|774875821|240|32|32|
|760938797|778240327|240|32|32|
|759674770|778998620|240|32|32|
|760960653|779839471|240|32|32|
|760946813|781842082|240|32|32|
|763884103|786091066|240|32|32|
|763236014|787025148|240|32|32|
|774672366|794812542|240|32|32|
|791857608|816200189|240|32|32|
|795770036|819701982|240|32|32|
|800250057|821695405|240|32|32|
|821469666|839557629|240|32|32|


Exact 26-mouse allocation and unit/trial metadata hashes are recorded in preflight_receipt.json. No reshuffling, replenishment or new acquisition.

## A3 Full pipeline

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



Execution source hashes and software versions are in the registration/preflight/run receipts. Original scientific evaluator and mathematical source bytes remain unchanged.

## A4 Baselines and all case results


|Contrast|CA1 gain|DG gain|CA1-DG|95% CI|Exact p|Holm p|
|---|---|---|---|---|---|---|
|Own history|0.03047404|0.03970089|-0.00922685|[-0.02871643, 0.01001067]|0.3894043|0.3894043|
|Other-unit history|0.001711799|0.004664711|-0.002952912|[-0.00542441, -0.0008724256]|0.01586914|0.06347656|
|Stimulus/time|0.0008911144|0.003963222|-0.003072108|[-0.005989451, -0.0008027204]|0.02148438|0.06445312|
|Combined features|0.03507601|0.05864403|-0.02356802|[-0.04708026, -0.00143493]|0.07055664|0.1411133|


|Contrast|Development mean|Development Holm|Final mean|Final Holm|
|---|---|---|---|---|
|Own history|0.00262621|1|-0.00922685|0.3894043|
|Other-unit history|-0.001151693|0.06933594|-0.002952912|0.06347656|
|Stimulus/time|-0.0007189372|1|-0.003072108|0.06445312|
|Combined features|-0.003170721|1|-0.02356802|0.1411133|


All original 1,638 M3 and 78 development shared-offset fits remain in paper12_predictive_v2/supplements/all_old_baseline_fits.csv and reuse evidence. Final coefficients were separately calibrated on C. The full 290-case score/denominator/gain table is all_290_case_scores.csv. No unrun final legacy-baseline competition is claimed.

## A5 Holdout and governance audit

One actual D assessment after scientific preflight; no result-based rerun. Exact exposure/custody limitations are in Methods 2.5 and registration.json. Original failures remain immutable. Trusted-local-host permission is prospective and does not clear failed older security gates. No independently enforced cryptographic entitlement or third-party custodian exists in this workflow.


|Field|Value|
|---|---|
|Real evaluation|Yes|
|Final mice|13|
|New C fits|0|
|Run receipt SHA256|757322b92a0f8157d98c5a2b79b8702f743c23c02ec39ef720275a9b408e3fac|
|Frozen protocol SHA256|eaa97bcf10e6dd6a4b7045826eacf14ab91baf4437ebd8df35289bf99f345906|



## A6 Complete mouse-level statistics


|Contrast|CA1 gain|DG gain|CA1-DG|95% CI|Exact p|Holm p|
|---|---|---|---|---|---|---|
|Own history|0.03047404|0.03970089|-0.00922685|[-0.02871643, 0.01001067]|0.3894043|0.3894043|
|Other-unit history|0.001711799|0.004664711|-0.002952912|[-0.00542441, -0.0008724256]|0.01586914|0.06347656|
|Stimulus/time|0.0008911144|0.003963222|-0.003072108|[-0.005989451, -0.0008027204]|0.02148438|0.06445312|
|Combined features|0.03507601|0.05864403|-0.02356802|[-0.04708026, -0.00143493]|0.07055664|0.1411133|


|Contrast|Registered classification|Holm criterion met|CI excludes zero|Development direction|Sensitivity signs|All LOMO signs|Relevant corrected control|
|---|---|---|---|---|---|---|---|
|Own history|NOT VALIDATED / MIXED|No|No|No|No|No|Yes|
|Other-unit history|NOT VALIDATED / MIXED|No|Yes|Yes|Yes|Yes|Yes|
|Stimulus/time|NOT VALIDATED / MIXED|No|Yes|Yes|Yes|Yes|Yes|
|Combined features|NOT VALIDATED / MIXED|No|Yes|Yes|Yes|Yes|Yes|


|View|Mice|Own history|Other-unit history|Stimulus/time|Combined features|
|---|---|---|---|---|---|
|primary|13|-0.00922685|-0.002952912|-0.003072108|-0.02356802|
|matched16|13|-0.004035165|-0.003010425|-0.002592174|-0.0194676|
|rate_matched|13|-0.004815319|-0.003177447|-0.001965921|-0.02125817|
|boundary20|13|-0.007661279|-0.002821908|-0.002913629|-0.02104586|
|boundary40|13|-0.009246422|-0.002630431|-0.003074468|-0.02246293|



|Mouse|Contrast|CA1-DG|LOMO mean|
|---|---|---|---|
|754477358|own|-0.03091637|-0.00741939|
|759674770|own|-0.01499735|-0.008745975|
|759711152|own|-0.009195046|-0.009229501|
|760938797|own|-0.05122769|-0.00572678|
|760946813|own|-0.002966891|-0.009748514|
|760960653|own|-0.0809922|-0.003246404|
|763236014|own|0.01077918|-0.01089402|
|763884103|own|-0.04092648|-0.006585215|
|774672366|own|0.01058148|-0.01087754|
|791857608|own|0.01771626|-0.01147211|
|795770036|own|-0.02041736|-0.008294308|
|800250057|own|0.06063844|-0.01504896|
|821469666|own|0.03197498|-0.01266034|
|754477358|population|-0.001095404|-0.003107705|
|759674770|population|0.001902957|-0.003357568|
|759711152|population|0.0001699575|-0.003213151|
|760938797|population|-0.00236982|-0.003001503|
|760946813|population|-0.002031911|-0.003029662|
|760960653|population|-0.006944503|-0.00262028|
|763236014|population|-0.0002869037|-0.00317508|
|763884103|population|-0.002193965|-0.003016158|
|774672366|population|-0.01318483|-0.002100253|
|791857608|population|-0.009028124|-0.002446645|
|795770036|population|-0.002696688|-0.002974264|
|800250057|population|-0.002543486|-0.002987031|
|821469666|population|0.00191486|-0.00335856|
|754477358|stimulus_time|-0.005608881|-0.00286071|
|759674770|stimulus_time|-0.004652006|-0.00294045|
|759711152|stimulus_time|0.002126869|-0.003505356|
|760938797|stimulus_time|-0.0003776211|-0.003296648|
|760946813|stimulus_time|-0.003289222|-0.003054015|
|760960653|stimulus_time|-0.01665674|-0.001940055|
|763236014|stimulus_time|0.0001451961|-0.003340216|
|763884103|stimulus_time|-0.003503834|-0.003036131|
|774672366|stimulus_time|-0.007842932|-0.002674539|
|791857608|stimulus_time|-0.001235093|-0.003225192|
|795770036|stimulus_time|0.0001125557|-0.003337496|
|800250057|stimulus_time|-0.0001096409|-0.00331898|
|821469666|stimulus_time|0.0009539445|-0.003407612|
|754477358|combined|-0.04458625|-0.0218165|
|759674770|combined|0.001613137|-0.02566645|
|759711152|combined|-0.004552229|-0.02515267|
|760938797|combined|-0.0519301|-0.02120452|
|760946813|combined|-0.01722208|-0.02409685|
|760960653|combined|-0.1146769|-0.01597562|
|763236014|combined|0.005870898|-0.02602127|
|763884103|combined|-0.05940097|-0.02058194|
|774672366|combined|-0.06209813|-0.02035718|
|791857608|combined|-0.01516343|-0.02426841|
|795770036|combined|-0.02206679|-0.02369313|
|800250057|combined|0.04536696|-0.0293126|
|821469666|combined|0.03246158|-0.02823716|


All group-eligible view mouse differences and bootstrap intervals: all_mouse_view_differences.csv. All 8192 sign assignments and 10000 bootstrap replicates use unchanged code; saved result JSON includes the exact effect vectors and LOMO means.

### Per-mouse probe dependence


|Mouse|Contrast|Shared-probe effect|LOPO views|LOPO min|LOPO max|Max absolute shift|
|---|---|---|---|---|---|---|
|754477358|own|-0.0727949|6|-0.0414367|-0.01725325|0.04187853|
|754477358|population|-0.001059859|6|-0.002215038|-0.0004052564|0.001119635|
|754477358|stimulus_time|-0.002635785|6|-0.009769743|-0.003202393|0.004160863|
|754477358|combined|-0.08816057|6|-0.05601582|-0.03057356|0.04357432|
|759711152|own|-0.02520551|6|-0.02008462|0.006575658|0.01601047|
|759711152|population|-0.0009553764|6|-0.0006858396|0.001079542|0.001125334|
|759711152|stimulus_time|-3.950937e-05|6|0.0003580485|0.004804122|0.002677252|
|759711152|combined|-0.0269917|6|-0.01802458|0.00350959|0.02243947|
|760938797|own|-0.03587188|6|-0.06233279|-0.03846997|0.01535581|
|760938797|population|-0.003905501|6|-0.002429006|-0.001181182|0.00153568|
|760938797|stimulus_time|-0.002227937|6|-0.001471055|0.0003263066|0.001850316|
|760938797|combined|-0.04007233|6|-0.06164029|-0.0406208|0.01185777|
|759674770|own|0.03048895|6|-0.05335282|0.05771702|0.07271437|
|759674770|population|-0.009751161|6|0.0005368766|0.002888768|0.01165412|
|759674770|stimulus_time|-0.004262209|6|-0.01094949|0.006174096|0.0108261|
|759674770|combined|0.003099253|6|-0.04500601|0.07364582|0.07203269|
|760960653|own|0.008906332|6|-0.1198398|0.01668552|0.09767772|
|760960653|population|-0.01037886|6|-0.0106424|-0.005097794|0.003697899|
|760960653|stimulus_time|-0.003747744|6|-0.02200419|-0.002392547|0.01426419|
|760960653|combined|-0.04405326|6|-0.1492983|-0.02917393|0.08550297|
|760946813|own|-0.02549075|6|-0.01560945|0.001649762|0.02252386|
|760946813|population|-0.0006887466|6|-0.002577329|-0.001698975|0.001343164|
|760946813|stimulus_time|-0.001694887|6|-0.004405663|-0.002397556|0.001594334|
|760946813|combined|-0.0297396|6|-0.02794889|-0.01429291|0.01251752|
|763884103|own|-0.05339637|5|-0.04810463|-0.02929245|0.01246989|
|763884103|population|0.001418068|5|-0.003594107|-0.0003154037|0.003612033|
|763884103|stimulus_time|-0.007200976|5|-0.005396391|5.369787e-06|0.003697142|
|763884103|combined|-0.09020428|5|-0.06865137|-0.0332403|0.03080331|
|763236014|own|0.00644447|5|0.01034065|0.01579439|0.005015206|
|763236014|population|-0.0003359776|5|-0.002356136|0.001380143|0.002069232|
|763236014|stimulus_time|0.0006129672|5|-0.0003447934|0.002093034|0.001947838|
|763236014|combined|0.003764048|5|-0.0003128732|0.01169972|0.006183771|
|774672366|own|None|5|0.002677542|0.0131871|0.007903935|
|774672366|population|None|5|-0.01721835|-0.01042003|0.004033527|
|774672366|stimulus_time|None|5|-0.0101553|-0.006176919|0.002312373|
|774672366|combined|None|5|-0.08880657|-0.04432025|0.02670844|
|791857608|own|-0.01591026|5|0.0107402|0.02954344|0.03362652|
|791857608|population|-0.004290628|5|-0.009931554|-0.008062957|0.004737496|
|791857608|stimulus_time|-0.001346303|5|-0.001991619|-0.0002243543|0.001010739|
|791857608|combined|-0.03079777|5|-0.02187664|-0.006309101|0.01563434|
|795770036|own|-0.03636837|5|-0.03036813|-0.01350878|0.01595101|
|795770036|population|-0.004924068|5|-0.003931098|-0.0006321454|0.002227379|
|795770036|stimulus_time|-0.001545607|5|-0.0004703248|0.0003908591|0.001658163|
|795770036|combined|-0.03877374|5|-0.03176909|-0.01553134|0.01670694|
|800250057|own|0.00498954|3|0.04513018|0.08792441|0.0556489|
|800250057|population|-0.0001144776|3|-0.00539576|2.061834e-05|0.002852274|
|800250057|stimulus_time|0.0004978995|3|-0.0004896117|0.0008048013|0.0009144422|
|800250057|combined|-0.005315468|3|0.02439114|0.08130169|0.05068243|
|821469666|own|0.04122751|4|0.01799516|0.03928592|0.01397982|
|821469666|population|0.00444542|4|0.001298843|0.003225836|0.00253056|
|821469666|stimulus_time|0.002309982|4|-0.001144019|0.001627932|0.002097964|
|821469666|combined|0.04151541|4|0.01515479|0.04072616|0.0173068|


All available shared/leave-probe effects, including views without enough mice for group inference: all_mouse_probe_assessment.csv and saved probe_assessment.json. Missing strata are reported as None, not imputed.

### C-only rate matching residuals


|Mouse|Matched pairs|Median absolute log ratio|Maximum absolute log ratio|Within log(2)|
|---|---|---|---|---|
|754477358|27|0.1101253|0.6821581|Yes|
|759711152|26|0.03905211|0.5295178|Yes|
|760938797|28|0.1156496|0.6699801|Yes|
|759674770|21|0.09729891|0.6839981|Yes|
|760960653|27|0.193379|0.6544263|Yes|
|760946813|27|0.07743445|0.4997412|Yes|
|763884103|28|0.1800638|0.6884633|Yes|
|763236014|26|0.09568973|0.5910108|Yes|
|774672366|29|0.09381876|0.6757554|Yes|
|791857608|30|0.1084884|0.5710265|Yes|
|795770036|23|0.1148929|0.6681294|Yes|
|800250057|25|0.05854242|0.6520956|Yes|
|821469666|25|0.08713038|0.6850674|Yes|


Every matched pair log-ratio is retained in all_C_rate_matching.csv. These are calibration rates only, not D-derived QC or rate-based exclusions.

## A7 All four falsification suites


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



|Mouse|Region|Suite|Contrast|Observed|Null mean|
|---|---|---|---|---|---|
|754477358|CA1|B|own|0.01092217|0.01012709|
|754477358|CA1|B|population|0.001710043|0.001731088|
|754477358|CA1|B|stimulus_time|0.001830216|-0.003522973|
|754477358|CA1|B|combined|0.01926348|0.01391029|
|754477358|CA1|O|own|0.01092217|0.0179471|
|754477358|CA1|O|population|0.001710043|0.002014888|
|754477358|CA1|O|stimulus_time|0.001830216|0.001944711|
|754477358|CA1|O|combined|0.01926348|0.02680447|
|754477358|CA1|S|own|0.01092217|0.01130179|
|754477358|CA1|S|population|0.001710043|0.001721765|
|754477358|CA1|S|stimulus_time|0.001830216|0.0008261422|
|754477358|CA1|S|combined|0.01926348|0.01825941|
|754477358|CA1|T|own|0.01092217|0.009977621|
|754477358|CA1|T|population|0.001710043|0.0003095282|
|754477358|CA1|T|stimulus_time|0.001830216|0.002666426|
|754477358|CA1|T|combined|0.01926348|0.01513381|
|754477358|DG|B|own|0.04183854|0.04069333|
|754477358|DG|B|population|0.002805447|0.004403018|
|754477358|DG|B|stimulus_time|0.007439096|-0.00966394|
|754477358|DG|B|combined|0.06384973|0.04674669|
|754477358|DG|O|own|0.04183854|0.05693987|
|754477358|DG|O|population|0.002805447|0.003438818|
|754477358|DG|O|stimulus_time|0.007439096|0.009096783|
|754477358|DG|O|combined|0.06384973|0.08026677|
|754477358|DG|S|own|0.04183854|0.04327725|
|754477358|DG|S|population|0.002805447|0.002887272|
|754477358|DG|S|stimulus_time|0.007439096|0.005544052|
|754477358|DG|S|combined|0.06384973|0.06195469|
|754477358|DG|T|own|0.04183854|0.01302811|
|754477358|DG|T|population|0.002805447|0.002297451|
|754477358|DG|T|stimulus_time|0.007439096|0.007470793|
|754477358|DG|T|combined|0.06384973|0.02871678|
|759674770|CA1|B|own|0.06124223|0.05450051|
|759674770|CA1|B|population|0.003576719|0.001247551|
|759674770|CA1|B|stimulus_time|0.007108676|-0.02302593|
|759674770|CA1|B|combined|0.0821226|0.051988|
|759674770|CA1|O|own|0.06124223|0.1163736|
|759674770|CA1|O|population|0.003576719|0.009525253|
|759674770|CA1|O|stimulus_time|0.007108676|0.01354925|
|759674770|CA1|O|combined|0.0821226|0.1545704|
|759674770|CA1|S|own|0.06124223|0.06200987|
|759674770|CA1|S|population|0.003576719|0.00344278|
|759674770|CA1|S|stimulus_time|0.007108676|0.006379912|
|759674770|CA1|S|combined|0.0821226|0.08139384|
|759674770|CA1|T|own|0.06124223|0.05845153|
|759674770|CA1|T|population|0.003576719|0.003720301|
|759674770|CA1|T|stimulus_time|0.007108676|0.009991127|
|759674770|CA1|T|combined|0.0821226|0.08290908|
|759674770|DG|B|own|0.07623958|0.04237726|
|759674770|DG|B|population|0.001673762|0.008045889|
|759674770|DG|B|stimulus_time|0.01176068|-0.03328068|
|759674770|DG|B|combined|0.08050947|0.0354681|
|759674770|DG|O|own|0.07623958|0.1493498|
|759674770|DG|O|population|0.001673762|0.001861387|
|759674770|DG|O|stimulus_time|0.01176068|0.01289226|
|759674770|DG|O|combined|0.08050947|0.1557111|
|759674770|DG|S|own|0.07623958|0.07709422|
|759674770|DG|S|population|0.001673762|0.001720817|
|759674770|DG|S|stimulus_time|0.01176068|0.01143725|
|759674770|DG|S|combined|0.08050947|0.08018604|
|759674770|DG|T|own|0.07623958|0.06955925|
|759674770|DG|T|population|0.001673762|0.001746916|
|759674770|DG|T|stimulus_time|0.01176068|0.01260156|
|759674770|DG|T|combined|0.08050947|0.07667744|
|759711152|CA1|B|own|0.02679795|0.03254354|
|759711152|CA1|B|population|0.002739864|0.01275034|
|759711152|CA1|B|stimulus_time|0.003637366|-0.01242464|
|759711152|CA1|B|combined|0.03956741|0.02350541|
|759711152|CA1|O|own|0.02679795|0.03847341|
|759711152|CA1|O|population|0.002739864|0.002545278|
|759711152|CA1|O|stimulus_time|0.003637366|0.004284992|
|759711152|CA1|O|combined|0.03956741|0.05182246|
|759711152|CA1|S|own|0.02679795|0.02735654|
|759711152|CA1|S|population|0.002739864|0.002741487|
|759711152|CA1|S|stimulus_time|0.003637366|0.002990758|
|759711152|CA1|S|combined|0.03956741|0.0389208|
|759711152|CA1|T|own|0.02679795|0.02233999|
|759711152|CA1|T|population|0.002739864|0.0005452648|
|759711152|CA1|T|stimulus_time|0.003637366|0.004646694|
|759711152|CA1|T|combined|0.03956741|0.03041611|
|759711152|DG|B|own|0.035993|0.03877925|
|759711152|DG|B|population|0.002569906|0.00469832|
|759711152|DG|B|stimulus_time|0.001510497|-0.006395326|
|759711152|DG|B|combined|0.04411964|0.03621382|
|759711152|DG|O|own|0.035993|0.04791293|
|759711152|DG|O|population|0.002569906|0.003245865|
|759711152|DG|O|stimulus_time|0.001510497|0.001663538|
|759711152|DG|O|combined|0.04411964|0.05842718|
|759711152|DG|S|own|0.035993|0.03809329|
|759711152|DG|S|population|0.002569906|0.002624189|
|759711152|DG|S|stimulus_time|0.001510497|0.0008242659|
|759711152|DG|S|combined|0.04411964|0.04343341|
|759711152|DG|T|own|0.035993|0.02202517|
|759711152|DG|T|population|0.002569906|0.0009753829|
|759711152|DG|T|stimulus_time|0.001510497|0.002485602|
|759711152|DG|T|combined|0.04411964|0.02761038|
|760938797|CA1|B|own|0.0158136|0.01475669|
|760938797|CA1|B|population|0.0002870447|0.001011324|
|760938797|CA1|B|stimulus_time|0.0002667109|-0.002939906|
|760938797|CA1|B|combined|0.01764873|0.01444211|
|760938797|CA1|O|own|0.0158136|0.01985809|
|760938797|CA1|O|population|0.0002870447|0.0003977837|
|760938797|CA1|O|stimulus_time|0.0002667109|0.0002976829|
|760938797|CA1|O|combined|0.01764873|0.02208051|
|760938797|CA1|S|own|0.0158136|0.01770248|
|760938797|CA1|S|population|0.0002870447|0.0003261664|
|760938797|CA1|S|stimulus_time|0.0002667109|-0.0009869647|
|760938797|CA1|S|combined|0.01764873|0.01639505|
|760938797|CA1|T|own|0.0158136|0.01169031|
|760938797|CA1|T|population|0.0002870447|-0.000141618|
|760938797|CA1|T|stimulus_time|0.0002667109|0.001591547|
|760938797|CA1|T|combined|0.01764873|0.01471044|
|760938797|DG|B|own|0.06704129|0.0641041|
|760938797|DG|B|population|0.002656865|0.008728906|
|760938797|DG|B|stimulus_time|0.0006443321|-0.005842166|
|760938797|DG|B|combined|0.06957883|0.06309233|
|760938797|DG|O|own|0.06704129|0.1053979|
|760938797|DG|O|population|0.002656865|0.002065411|
|760938797|DG|O|stimulus_time|0.0006443321|0.004004396|
|760938797|DG|O|combined|0.06957883|0.1092993|
|760938797|DG|S|own|0.06704129|0.06878392|
|760938797|DG|S|population|0.002656865|0.002695056|
|760938797|DG|S|stimulus_time|0.0006443321|-0.0004263267|
|760938797|DG|S|combined|0.06957883|0.06850817|
|760938797|DG|T|own|0.06704129|0.04691867|
|760938797|DG|T|population|0.002656865|0.0002805024|
|760938797|DG|T|stimulus_time|0.0006443321|0.001860203|
|760938797|DG|T|combined|0.06957883|0.04839405|
|760946813|CA1|B|own|0.0148761|0.01525755|
|760946813|CA1|B|population|0.001324475|0.001175381|
|760946813|CA1|B|stimulus_time|-0.0005803034|-0.003249888|
|760946813|CA1|B|combined|0.01744238|0.0147728|
|760946813|CA1|O|own|0.0148761|0.0252433|
|760946813|CA1|O|population|0.001324475|0.002299432|
|760946813|CA1|O|stimulus_time|-0.0005803034|4.12403e-05|
|760946813|CA1|O|combined|0.01744238|0.03132918|
|760946813|CA1|S|own|0.0148761|0.01494506|
|760946813|CA1|S|population|0.001324475|0.001313689|
|760946813|CA1|S|stimulus_time|-0.0005803034|-0.0007096442|
|760946813|CA1|S|combined|0.01744238|0.01731304|
|760946813|CA1|T|own|0.0148761|0.01204373|
|760946813|CA1|T|population|0.001324475|0.0009871047|
|760946813|CA1|T|stimulus_time|-0.0005803034|0.001356253|
|760946813|CA1|T|combined|0.01744238|0.01635767|
|760946813|DG|B|own|0.01784299|0.01568494|
|760946813|DG|B|population|0.003356386|0.001259303|
|760946813|DG|B|stimulus_time|0.002708918|-0.00606683|
|760946813|DG|B|combined|0.03466447|0.02588872|
|760946813|DG|O|own|0.01784299|0.02633992|
|760946813|DG|O|population|0.003356386|0.002640211|
|760946813|DG|O|stimulus_time|0.002708918|0.002980987|
|760946813|DG|O|combined|0.03466447|0.04310073|
|760946813|DG|S|own|0.01784299|0.01778518|
|760946813|DG|S|population|0.003356386|0.003320654|
|760946813|DG|S|stimulus_time|0.002708918|0.002651795|
|760946813|DG|S|combined|0.03466447|0.03460734|
|760946813|DG|T|own|0.01784299|0.01614104|
|760946813|DG|T|population|0.003356386|0.004624833|
|760946813|DG|T|stimulus_time|0.002708918|0.004204898|
|760946813|DG|T|combined|0.03466447|0.03481773|
|760960653|CA1|B|own|0.02746109|0.02722265|
|760960653|CA1|B|population|0.001436633|0.001200013|
|760960653|CA1|B|stimulus_time|-0.0006705078|-0.003067986|
|760960653|CA1|B|combined|0.02946726|0.02706978|
|760960653|CA1|O|own|0.02746109|0.0380183|
|760960653|CA1|O|population|0.001436633|0.001808716|
|760960653|CA1|O|stimulus_time|-0.0006705078|-0.0006267753|
|760960653|CA1|O|combined|0.02946726|0.04066704|
|760960653|CA1|S|own|0.02746109|0.02753364|
|760960653|CA1|S|population|0.001436633|0.001453412|
|760960653|CA1|S|stimulus_time|-0.0006705078|-0.0009464669|
|760960653|CA1|S|combined|0.02946726|0.0291913|
|760960653|CA1|T|own|0.02746109|0.0222576|
|760960653|CA1|T|population|0.001436633|-0.000210665|
|760960653|CA1|T|stimulus_time|-0.0006705078|0.001076699|
|760960653|CA1|T|combined|0.02946726|0.02337019|
|760960653|DG|B|own|0.1084533|0.04997513|
|760960653|DG|B|population|0.008381136|0.01490516|
|760960653|DG|B|stimulus_time|0.01598623|-0.04957793|
|760960653|DG|B|combined|0.1441442|0.07857999|
|760960653|DG|O|own|0.1084533|0.2188411|
|760960653|DG|O|population|0.008381136|0.006655942|
|760960653|DG|O|stimulus_time|0.01598623|0.02371214|
|760960653|DG|O|combined|0.1441442|0.2556795|
|760960653|DG|S|own|0.1084533|0.1087651|
|760960653|DG|S|population|0.008381136|0.008397107|
|760960653|DG|S|stimulus_time|0.01598623|0.01585997|
|760960653|DG|S|combined|0.1441442|0.1440179|
|760960653|DG|T|own|0.1084533|0.09308228|
|760960653|DG|T|population|0.008381136|0.008266786|
|760960653|DG|T|stimulus_time|0.01598623|0.01788525|
|760960653|DG|T|combined|0.1441442|0.1197922|
|763236014|CA1|B|own|0.02503814|0.02499892|
|763236014|CA1|B|population|0.001920921|0.002343647|
|763236014|CA1|B|stimulus_time|6.581798e-05|-0.003959682|
|763236014|CA1|B|combined|0.02894393|0.02491843|
|763236014|CA1|O|own|0.02503814|0.0350352|
|763236014|CA1|O|population|0.001920921|0.002370299|
|763236014|CA1|O|stimulus_time|6.581798e-05|0.0002531575|
|763236014|CA1|O|combined|0.02894393|0.04037627|
|763236014|CA1|S|own|0.02503814|0.02562073|
|763236014|CA1|S|population|0.001920921|0.001922057|
|763236014|CA1|S|stimulus_time|6.581798e-05|-0.000311854|
|763236014|CA1|S|combined|0.02894393|0.02856626|
|763236014|CA1|T|own|0.02503814|0.01940588|
|763236014|CA1|T|population|0.001920921|-0.0001401969|
|763236014|CA1|T|stimulus_time|6.581798e-05|0.001630756|
|763236014|CA1|T|combined|0.02894393|0.02083879|
|763236014|DG|B|own|0.01425896|0.01400782|
|763236014|DG|B|population|0.002207824|0.001506744|
|763236014|DG|B|stimulus_time|-7.937811e-05|-0.003297027|
|763236014|DG|B|combined|0.02307303|0.01985538|
|763236014|DG|O|own|0.01425896|0.02195857|
|763236014|DG|O|population|0.002207824|0.003092295|
|763236014|DG|O|stimulus_time|-7.937811e-05|0.0001277877|
|763236014|DG|O|combined|0.02307303|0.03609274|
|763236014|DG|S|own|0.01425896|0.01414266|
|763236014|DG|S|population|0.002207824|0.002232389|
|763236014|DG|S|stimulus_time|-7.937811e-05|-0.0002342805|
|763236014|DG|S|combined|0.02307303|0.02291813|
|763236014|DG|T|own|0.01425896|0.01022268|
|763236014|DG|T|population|0.002207824|0.00175609|
|763236014|DG|T|stimulus_time|-7.937811e-05|0.002291316|
|763236014|DG|T|combined|0.02307303|0.01768291|
|763884103|CA1|B|own|0.01740096|0.0160308|
|763884103|CA1|B|population|0.001595902|0.005631967|
|763884103|CA1|B|stimulus_time|0.001043259|-0.002893681|
|763884103|CA1|B|combined|0.02331541|0.01937847|
|763884103|CA1|O|own|0.01740096|0.03991127|
|763884103|CA1|O|population|0.001595902|0.003620792|
|763884103|CA1|O|stimulus_time|0.001043259|-7.734737e-05|
|763884103|CA1|O|combined|0.02331541|0.04612935|
|763884103|CA1|S|own|0.01740096|0.02335727|
|763884103|CA1|S|population|0.001595902|0.001855416|
|763884103|CA1|S|stimulus_time|0.001043259|-0.002280227|
|763884103|CA1|S|combined|0.02331541|0.01999192|
|763884103|CA1|T|own|0.01740096|0.009324995|
|763884103|CA1|T|population|0.001595902|-0.0008123522|
|763884103|CA1|T|stimulus_time|0.001043259|0.002317486|
|763884103|CA1|T|combined|0.02331541|0.01493167|
|763884103|DG|B|own|0.05832744|0.07662443|
|763884103|DG|B|population|0.003789867|0.00858507|
|763884103|DG|B|stimulus_time|0.004547093|-0.01071375|
|763884103|DG|B|combined|0.08271638|0.06745553|
|763884103|DG|O|own|0.05832744|0.09030459|
|763884103|DG|O|population|0.003789867|0.005241947|
|763884103|DG|O|stimulus_time|0.004547093|0.005038863|
|763884103|DG|O|combined|0.08271638|0.1163018|
|763884103|DG|S|own|0.05832744|0.06395191|
|763884103|DG|S|population|0.003789867|0.003752626|
|763884103|DG|S|stimulus_time|0.004547093|-0.001970367|
|763884103|DG|S|combined|0.08271638|0.07619892|
|763884103|DG|T|own|0.05832744|0.0170509|
|763884103|DG|T|population|0.003789867|-0.001065479|
|763884103|DG|T|stimulus_time|0.004547093|0.006581123|
|763884103|DG|T|combined|0.08271638|0.03767909|
|774672366|CA1|B|own|0.02047243|0.01965068|
|774672366|CA1|B|population|0.0005664499|0.001939162|
|774672366|CA1|B|stimulus_time|-0.0008131872|-0.003019225|
|774672366|CA1|B|combined|0.0203823|0.01817626|
|774672366|CA1|O|own|0.02047243|0.02502936|
|774672366|CA1|O|population|0.0005664499|0.0006665405|
|774672366|CA1|O|stimulus_time|-0.0008131872|-0.0007817645|
|774672366|CA1|O|combined|0.0203823|0.02493717|
|774672366|CA1|S|own|0.02047243|0.02070855|
|774672366|CA1|S|population|0.0005664499|0.0005935053|
|774672366|CA1|S|stimulus_time|-0.0008131872|-0.0009317383|
|774672366|CA1|S|combined|0.0203823|0.02026375|
|774672366|CA1|T|own|0.02047243|0.0180687|
|774672366|CA1|T|population|0.0005664499|7.147263e-05|
|774672366|CA1|T|stimulus_time|-0.0008131872|0.001170211|
|774672366|CA1|T|combined|0.0203823|0.01904104|
|774672366|DG|B|own|0.009890954|0.01043729|
|774672366|DG|B|population|0.01375128|0.008475743|
|774672366|DG|B|stimulus_time|0.007029745|-0.01341337|
|774672366|DG|B|combined|0.08248043|0.06203731|
|774672366|DG|O|own|0.009890954|0.01629313|
|774672366|DG|O|population|0.01375128|0.01251167|
|774672366|DG|O|stimulus_time|0.007029745|0.007008565|
|774672366|DG|O|combined|0.08248043|0.09512874|
|774672366|DG|S|own|0.009890954|0.01001777|
|774672366|DG|S|population|0.01375128|0.01372974|
|774672366|DG|S|stimulus_time|0.007029745|0.006753059|
|774672366|DG|S|combined|0.08248043|0.08220374|
|774672366|DG|T|own|0.009890954|0.005242133|
|774672366|DG|T|population|0.01375128|0.01730646|
|774672366|DG|T|stimulus_time|0.007029745|0.01023036|
|774672366|DG|T|combined|0.08248043|0.07936128|
|791857608|CA1|B|own|0.02788284|0.02545196|
|791857608|CA1|B|population|0.001393532|0.004382754|
|791857608|CA1|B|stimulus_time|-0.0005002832|-0.003861816|
|791857608|CA1|B|combined|0.0268824|0.02352087|
|791857608|CA1|O|own|0.02788284|0.04884169|
|791857608|CA1|O|population|0.001393532|0.002975458|
|791857608|CA1|O|stimulus_time|-0.0005002832|-0.0002426924|
|791857608|CA1|O|combined|0.0268824|0.04860923|
|791857608|CA1|S|own|0.02788284|0.02753267|
|791857608|CA1|S|population|0.001393532|0.001444207|
|791857608|CA1|S|stimulus_time|-0.0005002832|-0.0006368712|
|791857608|CA1|S|combined|0.0268824|0.02674581|
|791857608|CA1|T|own|0.02788284|0.02747259|
|791857608|CA1|T|population|0.001393532|0.0002454831|
|791857608|CA1|T|stimulus_time|-0.0005002832|0.001018996|
|791857608|CA1|T|combined|0.0268824|0.02679921|
|791857608|DG|B|own|0.01016658|0.009874135|
|791857608|DG|B|population|0.01042166|0.009260742|
|791857608|DG|B|stimulus_time|0.0007348096|-0.004177648|
|791857608|DG|B|combined|0.04204583|0.03713337|
|791857608|DG|O|own|0.01016658|0.01235229|
|791857608|DG|O|population|0.01042166|0.009725976|
|791857608|DG|O|stimulus_time|0.0007348096|0.0008619649|
|791857608|DG|O|combined|0.04204583|0.04389145|
|791857608|DG|S|own|0.01016658|0.01025343|
|791857608|DG|S|population|0.01042166|0.0103363|
|791857608|DG|S|stimulus_time|0.0007348096|0.0007332408|
|791857608|DG|S|combined|0.04204583|0.04204426|
|791857608|DG|T|own|0.01016658|0.006295032|
|791857608|DG|T|population|0.01042166|0.007330676|
|791857608|DG|T|stimulus_time|0.0007348096|0.003670352|
|791857608|DG|T|combined|0.04204583|0.02896013|
|795770036|CA1|B|own|0.01612762|0.0128904|
|795770036|CA1|B|population|0.0007015575|0.00766197|
|795770036|CA1|B|stimulus_time|0.0005348186|-0.004921251|
|795770036|CA1|B|combined|0.01690577|0.0114497|
|795770036|CA1|O|own|0.01612762|0.02890527|
|795770036|CA1|O|population|0.0007015575|0.0008977795|
|795770036|CA1|O|stimulus_time|0.0005348186|0.0005848432|
|795770036|CA1|O|combined|0.01690577|0.02974456|
|795770036|CA1|S|own|0.01612762|0.01675775|
|795770036|CA1|S|population|0.0007015575|0.0007660242|
|795770036|CA1|S|stimulus_time|0.0005348186|-0.0002159062|
|795770036|CA1|S|combined|0.01690577|0.01615505|
|795770036|CA1|T|own|0.01612762|0.0108266|
|795770036|CA1|T|population|0.0007015575|8.010975e-05|
|795770036|CA1|T|stimulus_time|0.0005348186|0.001656561|
|795770036|CA1|T|combined|0.01690577|0.01233815|
|795770036|DG|B|own|0.03654498|0.03449633|
|795770036|DG|B|population|0.003398246|0.01685855|
|795770036|DG|B|stimulus_time|0.0004222629|-0.005274687|
|795770036|DG|B|combined|0.03897256|0.03327561|
|795770036|DG|O|own|0.03654498|0.1017449|
|795770036|DG|O|population|0.003398246|0.01298997|
|795770036|DG|O|stimulus_time|0.0004222629|0.0009599808|
|795770036|DG|O|combined|0.03897256|0.1053419|
|795770036|DG|S|own|0.03654498|0.03706649|
|795770036|DG|S|population|0.003398246|0.00343197|
|795770036|DG|S|stimulus_time|0.0004222629|-0.0002288431|
|795770036|DG|S|combined|0.03897256|0.03832146|
|795770036|DG|T|own|0.03654498|0.02477281|
|795770036|DG|T|population|0.003398246|0.0006423806|
|795770036|DG|T|stimulus_time|0.0004222629|0.001242632|
|795770036|DG|T|combined|0.03897256|0.0257714|
|800250057|CA1|B|own|0.07819137|0.07556386|
|800250057|CA1|B|population|0.001579337|0.004437766|
|800250057|CA1|B|stimulus_time|-0.0004838941|-0.005945944|
|800250057|CA1|B|combined|0.07784705|0.072385|
|800250057|CA1|O|own|0.07819137|0.08953906|
|800250057|CA1|O|population|0.001579337|0.001704835|
|800250057|CA1|O|stimulus_time|-0.0004838941|-0.0005397447|
|800250057|CA1|O|combined|0.07784705|0.08962872|
|800250057|CA1|S|own|0.07819137|0.07740577|
|800250057|CA1|S|population|0.001579337|0.001530954|
|800250057|CA1|S|stimulus_time|-0.0004838941|-0.000228377|
|800250057|CA1|S|combined|0.07784705|0.07810257|
|800250057|CA1|T|own|0.07819137|0.07035855|
|800250057|CA1|T|population|0.001579337|0.00043702|
|800250057|CA1|T|stimulus_time|-0.0004838941|0.001507508|
|800250057|CA1|T|combined|0.07784705|0.06646254|
|800250057|DG|B|own|0.01755293|0.01769158|
|800250057|DG|B|population|0.004122824|0.003840355|
|800250057|DG|B|stimulus_time|-0.0003742532|-0.002849574|
|800250057|DG|B|combined|0.03248009|0.03000477|
|800250057|DG|O|own|0.01755293|0.02127253|
|800250057|DG|O|population|0.004122824|0.003919546|
|800250057|DG|O|stimulus_time|-0.0003742532|-0.0004416148|
|800250057|DG|O|combined|0.03248009|0.03608332|
|800250057|DG|S|own|0.01755293|0.01781606|
|800250057|DG|S|population|0.004122824|0.004147521|
|800250057|DG|S|stimulus_time|-0.0003742532|-0.0005727042|
|800250057|DG|S|combined|0.03248009|0.03228164|
|800250057|DG|T|own|0.01755293|0.01034997|
|800250057|DG|T|population|0.004122824|0.002416335|
|800250057|DG|T|stimulus_time|-0.0003742532|0.001283916|
|800250057|DG|T|combined|0.03248009|0.02144313|
|821469666|CA1|B|own|0.05393602|0.05286202|
|821469666|CA1|B|population|0.003420913|0.01358099|
|821469666|CA1|B|stimulus_time|0.0001457983|-0.005446243|
|821469666|CA1|B|combined|0.05619934|0.0506073|
|821469666|CA1|O|own|0.05393602|0.1101455|
|821469666|CA1|O|population|0.003420913|0.007679359|
|821469666|CA1|O|stimulus_time|0.0001457983|0.001392533|
|821469666|CA1|O|combined|0.05619934|0.1161032|
|821469666|CA1|S|own|0.05393602|0.05459829|
|821469666|CA1|S|population|0.003420913|0.003406179|
|821469666|CA1|S|stimulus_time|0.0001457983|-0.0003692684|
|821469666|CA1|S|combined|0.05619934|0.05568428|
|821469666|CA1|T|own|0.05393602|0.0416178|
|821469666|CA1|T|population|0.003420913|0.001120547|
|821469666|CA1|T|stimulus_time|0.0001457983|0.00190755|
|821469666|CA1|T|combined|0.05619934|0.04282949|
|821469666|DG|B|own|0.02196104|0.02132367|
|821469666|DG|B|population|0.001506053|0.00287431|
|821469666|DG|B|stimulus_time|-0.0008081462|-0.002463136|
|821469666|DG|B|combined|0.02373776|0.02208277|
|821469666|DG|O|own|0.02196104|0.02624036|
|821469666|DG|O|population|0.001506053|0.001605806|
|821469666|DG|O|stimulus_time|-0.0008081462|-0.0008879553|
|821469666|DG|O|combined|0.02373776|0.0281055|
|821469666|DG|S|own|0.02196104|0.02226171|
|821469666|DG|S|population|0.001506053|0.0014995|
|821469666|DG|S|stimulus_time|-0.0008081462|-0.001078895|
|821469666|DG|S|combined|0.02373776|0.02346701|
|821469666|DG|T|own|0.02196104|0.01900888|
|821469666|DG|T|population|0.001506053|0.0005136811|
|821469666|DG|T|stimulus_time|-0.0008081462|0.001626713|
|821469666|DG|T|combined|0.02373776|0.0225072|


All104 complete999x4 replicate arrays remain in saved results. No null fitting, selected suite replacement or trial repartitioning. These conditional reference distributions have nuisance/exchangeability assumptions.

## A8 QC and leakage audit

The exact immutable C bundle and failed partial bundle were hash-checked; the original complete C provenance/numerical validator passed. C-only QC, unit/scaler/trial selections and source masks were not recalculated using D. All required views retain13 mice; no D-derived QC, normalization or exclusions. Synthetic transport tests used artificial counts, authenticated envelopes, exact masks, ordered-unit canaries, tamper/wrong-key negatives, and no real source. Existing exposure records are evidence of recorded isolation, not proof against unlogged administrator activity. Whole-session upstream sorting remains a limitation.

## A9 Failures, limitations and claim audit


|Contrast|Registered classification|Holm criterion met|CI excludes zero|Development direction|Sensitivity signs|All LOMO signs|Relevant corrected control|
|---|---|---|---|---|---|---|---|
|Own history|NOT VALIDATED / MIXED|No|No|No|No|No|Yes|
|Other-unit history|NOT VALIDATED / MIXED|No|Yes|Yes|Yes|Yes|Yes|
|Stimulus/time|NOT VALIDATED / MIXED|No|Yes|Yes|Yes|Yes|Yes|
|Combined features|NOT VALIDATED / MIXED|No|Yes|Yes|Yes|Yes|Yes|


All original scientific M4 and prerelease failures, finite-difference diagnosis, three nonconvergent conditioning candidates, partial seal/import failure and later repairs remain immutable. This mission does not retroactively validate them. Development is exploratory, anatomy is provider-proxy based, selected-unit populations and rate residuals remain confounds, and controls are conditional. Scientific claim status follows every original gate, with no equivalence/causal/human/NAP/CWP/independent-laboratory claim. Author declarations require owner review before submission.

## A10 Saved-only reproduction

From repository root:

```powershell
& ./paper12_sciencefinal1/reproduce_all.ps1
```

This runs synthetic numerical/transport regressions, verifies final scalar-result hashes, reaggregates all primary/view statistics and both complete null families through the frozen implementation, and regenerates manuscript/figures/PDFs in a fresh ignored work directory. It performs zero fits and opens no raw counts, C states or D key/cipher. It is not permission or a method for repeating the one-shot D assessment. Original execution provenance is certified by saved preflight/run receipts; environment identity is recorded separately. Core scalar-only checks are also available through reproduce.ps1. Artifact generation requires the recorded Matplotlib environment, bundled ReportLab/PyPDF runtime and Windows Arial fonts; missing dependencies fail explicitly, without synthetic substitution.
