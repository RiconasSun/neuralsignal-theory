# Independent internal review — PL contract r1

Mission: `P13-KI-PL-QUALITY-EPOCH-RESOLUTION-1`.
Reviewed UTC: 2026-10-16T05:56:46Z.
Reviewer: separate local reviewer agent; internal scientific/evidence/code review, not external peer review.
Decision: **REQUEST_CHANGES**. Open P0: **0**. Open P1: **5**.

The source-provenance and saved metadata reconstruction are supported. The claimed complete proposed scientific contract still requires the five corrections below before independent review can endorse `PROTOCOL_READY_PENDING_NEURAL_QC`. No spike access, fits or new data search is needed to resolve them. This review does not reclassify prior scientific results and does not authorize implementation or activation.

## Candidate and independently executed checks

Frozen candidate: `paper13_ki_pl_contract1/FREEZE_r1.json`, SHA256 `a8420b53742b005c98aeaa2cf2299a2194f3654f77de5e065451fab3c6771da3`; 82 source/metadata/protocol/output hashes. Read the full user mission, all 97 baseline requirements, golden standards, all five provenance/protocol/claim documents, README/report/config/allocation, audit/QC/tests/verifier, and relevant preserved source definitions.

Executed from repository root:

1. `& .\paper13_ki_pl_contract1\reproduce.ps1` — exit **0**; **32 tests passed**, all **82 hashes** verified, four outputs replayed byte-identically, network connections blocked during audit reconstruction. Reproduction work: `paper13_ki_pl_contract1/work/replay_e91f91420faa4711b05acd211805e6cd`. The verifier's `new_HTTP_requests=20` is the saved cumulative acquisition-journal count, not replay traffic; its original transport total is 1,620,223 bytes. No acquisition entry point ran.
2. Independent PowerShell here-string piped to `python -B -`, without importing production audit/QC/transport: rehashed all 82 files; opened only the selected local `badtints` metadata dataset; independently recounted PL from saved electrode rows; constructed pure-tone windows/support/overlap/spike masks directly from saved header JSON; applied LFP/manual masks; matched saved active intervals; compared every animal tuple to saved outputs. Exit **0**. All **25** animal rows matched. Historical basic epochs **6,155**; paired singleton-null spike saturation records **12**; manual interval **[900,2730]**; bounds **20 raw / 20 basic / 15 active / 19 refined A / 15 refined B**.
3. Independent saved-label scan using `python -B -`: PL labels are `PL5:1064`, `PL6a:754`, `PL2/3:68`, `PL6b:14`; **zero** units and **zero** animals have the exact unsuffixed label `PL`. This is metadata, not physiological measurement.

The independent scripts read only saved JSON/source and the explicitly authorized interval HDF5. No network, original NWB/ZIP, real spike samples, neural scores, fitting or model activation was used. Only this review file is added by the reviewer; ignored reproduction work was permitted.

## P1 findings

### P1 — Resolve the continuous representation's one-bin versus two-bin lag

Evidence: `paper13_ki_pl_contract1/PROPOSED_P13_V2.md:25`, `PROPOSED_P13_V2.md:41`; baseline REQ-042, REQ-052, REQ-060 and REQ-081.

The continuous model defines `z_t` as the standardized **preceding-bin** count vector, then defines `h_t` using `z_(t-1)`. Read literally, the state predicting bin t is driven by counts from t−2. The same paragraph says the state uses only the previous bin and defines bin 1's zero prior, which suggests `z_t` was instead intended to denote counts **in** bin t, followed by the stated `z_(t-1)` recurrence. Both are causal, but they are different frozen predictors, initial conditions and comparisons against the lag-1 baseline. An implementer cannot choose between them as a harmless numerical detail.

Required resolution: define the raw count index, standardized-count index and state/prediction/update order unambiguously, including the first two bins and warm-up. Freeze one exact recurrence and add a small synthetic index/causality oracle before calling the protocol complete. Do not fit data to decide the lag. Preserve this failed review and the original proposal bytes if the scientific definition changes.

### P1 — State the null and assumptions that make mouse sign flips exact

Evidence: `PROPOSED_P13_V2.md:55-57`, `PROPOSED_P13_V2.md:66-68`; baseline REQ-062 through REQ-065 and REQ-068.

The primary test is called an "exact two-sided sign flip" of observed mouse score differences, followed by Holm and bootstrap/consistency gates. Enumeration is computationally exact, but controls type-I error only under an appropriate independent sign-symmetry/randomization null. The mice have paired model predictions, not randomized model assignments; zero average predictive gain alone does not imply sign symmetry. The protocol carefully qualifies the conditional B4 null and stress controls, but never states this corresponding assumption or the primary hypothesis under which sign-flip p-values are valid. Holm cannot repair invalid constituent p-values, and the percentile bootstrap and directional gates are not a substitute for that assumption.

A simple non-neural counterexample illustrates the distinction: independent mouse differences equal +1 with probability .9 and −9 with probability .1 have mean zero. All eight differences equal +1 with probability `.9**8 = .43046721`; on that event the proposed two-sided sign flip gives `2/256 = .0078125`, the bootstrap interval is positive, every mouse direction is positive and every LOMO mean is positive. Thus these ingredients cannot be labeled an exact test of the unrestricted zero-mean null. This is a mathematical diagnostic, not a simulation of this dataset or a prediction of its outcome.

Required resolution: explicitly define the primary inferential null, independent-mouse/sign-symmetry or other needed assumptions, and the claim limits if those assumptions cannot be defended. Alternatively propose a justified test for the intended null, with its estimand and multiplicity effects made explicit. This is a prospective protocol decision, not permission to alter an analysis after outcomes. Keep the existing numerical thresholds and historical results immutable; refresh the proposed config/claim audit and synthetic inferential oracles consistently.

### P1 — Finish the mandatory sensitivity operators and applicability gates

Evidence: `PROPOSED_P13_V2.md:33-35`, `PROPOSED_P13_V2.md:39-41`, `PROPOSED_P13_V2.md:70-72`; independent exact-label census above; baseline REQ-042, REQ-052, REQ-061, REQ-065, REQ-068 and REQ-081.

The sensitivities are declared mandatory parts of the single final bundle, but three material rules remain unresolved:

- Panel (d) requests exact `PL` versus laminar PL separately. The complete saved unit census has **no exact `PL` labels**. The document does not decide whether that empty comparison is a disclosed inapplicable cell or a failed mandatory gate making the claim inconclusive. "For each computable" followed by "Otherwise ... INCONCLUSIVE" permits both readings. The absence is knowable now and must not be resolved by an implementer after scores.
- Reduced-unit panels say to restrict readouts/HMM emissions and rows of Q, but B4's frozen offset still contains each selected unit's own and all seven other-unit histories. It is unspecified whether omitted units remain in that offset, whether corresponding original standardized feature contributions are zeroed/removed, and whether HMM filtering uses retained-unit emissions only. Those choices change both the information available and the likelihood under a purported smaller population. Define the full B0–B4/D/C input, scaling, filtering, target and denominator operator under each unit mask, not only the final output rows.
- Panel (f), "drop all recorded known-stimulus events from preceding5s," does not say whether to censor entire windows, drop scored bins or ablate event covariates. These yield different populations, histories and interpretations. Define the reference time, event/interval overlap rule, retained original epoch/bin identities, reset behavior and minimum-sample gate. Do not let the available score determine the meaning of "drop."

Required resolution: freeze deterministic sensitivity operators and explicit empty/insufficient-data outcomes before activation, with synthetic examples and saved-label applicability checks. Distinguish descriptive/non-applicable cells from mandatory failed claim gates consistently in protocol/config/claim audit. No threshold relaxation, invented anatomy labels, held-out replacement or additional model search is authorized by this finding.

### P1 — Guard the stronger-baseline interpretation with a frozen comparator

Evidence: `PROPOSED_P13_V2.md:7`, `PROPOSED_P13_V2.md:33-35`, `PROPOSED_P13_V2.md:55-57`, `PROPOSED_P13_V2.md:68`; broad preserved P13 prediction question and baseline REQ-054 through REQ-058, REQ-064 and REQ-068.

The primary positive-information gates compare D and C only against B4. B4 is the mandatory richest combined model and its ridge is selected on development data, but richness does not establish strongest held-out prediction. The protocol fits B0-B3 and selects their ridge policies only "for reporting." It therefore allows a positive D/C-versus-B4 result even if a simpler rate/history/context baseline predicts better than both. For example, on the final score scale B0=-1.00, B4=-1.10 and D=-1.05 permits an improvement over B4 while D remains worse than the stationary rate model. This cannot support the broader claim of predictive improvement beyond strong rate/history/context alternatives, even if the three existing tests and stress gates pass.

Required resolution: preserve mandatory B4 and the registered primary comparisons, but define a prospective strongest-baseline comparator/claim guard selected using development data only, including deterministic selection/ties, final calibration policy and the inference/multiplicity consequences. Alternatively explicitly restrict every positive claim to the chosen B4 representation and withhold the broader beyond-baseline claim when the frozen stronger comparator is not exceeded. Do not choose a comparator by final scores, silently delete B0-B3 or add unbounded searches. Freeze the guard and its synthetic counterexample before calling the contract complete.

### P1 — Separate static latent-mixture gain from temporal dynamics

Evidence: `PROPOSED_P13_V2.md:7`, `PROPOSED_P13_V2.md:39`, `PROPOSED_P13_V2.md:43-45`, `PROPOSED_P13_V2.md:55-57`, `PROPOSED_P13_V2.md:63-68`; baseline REQ-059, REQ-061, REQ-065 and REQ-068.

The HMM grid includes p=.5, whose transition rows are identical and whose pre-observation state probabilities are always [.5,.5]. It is a static two-component joint Poisson mixture: it can improve joint prediction through current-bin overdispersion/shared count covariance even when no useful history exists. Selecting p>.5 likewise does not by itself establish that improvement over B4 comes from temporal information rather than the mixture emission family. B4 has conditionally independent Poisson outputs; the comparison changes the current-bin distribution as well as temporal state. The ontology/causal caveats are appropriate but do not address this particular predictive confound. Temporal/history stress controls do not directly compare against the same fitted static mixture and therefore do not isolate the temporal contribution.

Required resolution: prospectively distinguish **representation/joint-distribution gain** from **temporal-dynamics gain**. The existing p=.5 fits provide a natural matched-16-parameter static comparator without increasing the search grid. Freeze its development-only ridge/start selection and calibration/score policy, and any multiplicity-adjusted or clearly assumption-dependent claim guard needed to support temporal language. At minimum withhold temporal-dynamics interpretation when the selected family is static or fails the frozen static comparator, while retaining all original contrasts/results and the limited predictive-family claim. Add synthetic iid-mixture and genuinely persistent-state oracles to the future implementation gates. No additional fitting occurs in this mission.

## Supported provenance, reconstruction and boundaries

The quality report appropriately leaves the two NWB field formulas/units/exporter unresolved, distinguishes the published ISI/presence/amplitude/waveform rules from the separate processed binary flags, and proposes a different training-only operational screen without claiming actual eligible units or single-neuron purity. Its minimum spikes/ISIs/occupancy/rate/refractory definitions are explicit; full-record sorting/curation selection limits remain disclosed.

Pinned `data_classes.py:265-276` supplies the single-pair NaN-empty convention, and the preserved normalizer explains why nonfinite values appear as nulls. The 12 paired-null cases, finite remainder and fail-closed malformed/missing handling are consistent with the documented provider convention; this establishes a source-based convention, not independent artifact-free certification. The manual member and masks independently produce the reported counts. `147463` has 194 historical basic windows and only 55 refined A windows; the 139 manual exclusions are not hidden by its 104 raw PL units. No hardware-packet certificate or awake/movement equivalence is invented.

Anatomy/task boundaries, first-120 chronological rule, proposed 10/9 animal allocation, no replacements, training/calibration-only QC/scaling, minimum 8+8 mice, mandatory combined baseline, exact joint HMM score normalization, equal 16 added free coefficients, bounded numerical gates, fixed fit/search budgets and one-final-bundle boundary are substantively specified. The current tests validate metadata/QC references, not the future HMM/AD/fits/nulls. The proposal says so, and no such future result or scientific PASS is claimed.

The narrower A target can be scientifically defensible despite unresolved historical quality formulas and active-mask creator hashes because it explicitly targets prospectively screened curated-release units and does not admit on active state. The source/data-contract investigation does not need a further open-ended search. However, independent endorsement of the **complete proposed protocol** remains pending the five P1 resolutions above; synthetic replay success cannot certify those unresolved scientific definitions.

**Git/closure:** actual exact-file commit, `origin/test` push, remote readback and clean-tree gate remain pending and are not certified by this review. No `MERGE_ALLOWED` or main promotion is granted. No neural access, M1-M7, final assessment or retrospective historical PASS is authorized. Preserve this review as failed evidence, correct only the scoped contract/test/evidence issues, freeze a new candidate and obtain independent re-review.
