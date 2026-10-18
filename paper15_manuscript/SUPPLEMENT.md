# Supplementary Methods, Results and Reproducibility

Companion to "Predictive Contributions of Local Spike History in Mouse Primary Motor Cortex: A Development and Independent-Animal Descriptive Evaluation."

**Scientific status: Development exploratory; independent-animal Final DESCRIPTIVE ONLY.** The original positive-claim conjunction was not met. This document reports saved evidence; it is not a new neural analysis, external peer review or a second Final assessment. Main Figures 1-7 and all CSV supplements are part of the package.

## S1. Source versions, original cohort and attrition

The provider is the International Brain Laboratory. The actual neural source is native ONE/ALF in the public AWS bucket `ibl-brain-wide-map-public`, region `us-east-1`, under CC BY 4.0. The source's Brainwidemap documentation describes 139 mice, 459 sessions and 699 insertions. The analysis is a small MOp subset; those global numbers are not this study's sample size. Relevant original task and source publications and official licence are cited in the main references [1,2,10-12]. Access dates in the bibliography refer to document verification, not a new data release.

The metadata eligibility screen used `2024_Q2_IBL_et_al_BWM` cluster/trial aggregates and `2023_12_bwm_release` insertions. Native sorting was `alf/{probe}/pykilosort/#2024-05-06#/`; the native trial table was `alf/#2025-03-03#/_ibl_trials.table.*.pqt`. Native wheel files were uniquely matched unrevisioned `alf/_ibl_wheel.*` objects. Original sync, AP headers and `_iblqc_ephysSaturationAP.samples` came from the selected probe's raw-ephys collection. Unrevisioned objects were still individually pinned by UUID, ETag, byte size and source/header identity. No latest-version fallback, other-probe substitution or DANDI conversion was used. Prior data-source packages retain native inventory details, not an invented monolithic new release number.

Provider mapping definitions were audited against frozen ibllib revision `3eced8ed26c2dfb6d149472c7ff2246f27d2bfb3`; the old eligibility loader source was pinned at `118fc36cb3602934466ad2c6087c2b3b441f9f1f`. Original native access used ONE-api3.6.1 public unsigned S3 and ALF readers; a prior anonymous metadata-query403 did not cause a dataset substitution. No raw AP/LFP, waveform or video analysis was performed in the predictive study. Header/support checks are not a re-extraction of the provider's spike sorting.

Original fixed allocation:20 mice,12 Development and8 Final. Ten Development/eight laboratories and six Final/four laboratories were admitted. Development exclusions were NYU-37(B=31<40) and CSHL059(sync domain[0,1]s; zero covered epochs). Final exclusions were NYU-21(non-strict wheel timestamps;16,485 equal adjacent pairs) and UCLA033(6 C-qualified units<8). No replacement mouse/session/probe or eligibility definition was introduced. The following inventory gives every original mouse, lab, date, session, probe, eid and pid; long identifiers are placed on separate lines for readability. The exact CSV is `tables/SOURCE_COHORT_IDENTITIES.csv`.

**NYU-37** - DEVELOPMENT; angelakilab; 2021-01-26; session 1; probe01. Admitted: False. Exclusion: 31 B epochs, below40 frozen minimum.

Session eid: `f88d4dd4-ccd7-400e-9035-fa00be3bcfa8`

Probe pid: `decc8d40-cf74-4263-ae9d-a0cc68b47e86`

**CSHL059** - DEVELOPMENT; churchlandlab; 2020-03-03; session 1; probe00. Admitted: False. Exclusion: sync domain[0,1] yields zero covered epochs.

Session eid: `d2f5a130-b981-4546-8858-c94ae1da75ff`

Probe pid: `79628a45-c2e3-4206-97df-4c91edaff90f`

**UCLA037** - FINAL_RESERVED; churchlandlab_ucla; 2022-02-09; session 1; probe00. Admitted: True. No exclusion.

Session eid: `8d316998-28c3-4265-b029-e2ca82375b2f`

Probe pid: `5245b505-d0e7-4942-94d1-b33a084fab03`

**KS046** - DEVELOPMENT; cortexlab; 2020-12-05; session 1; probe00. Admitted: True. No exclusion.

Session eid: `aa3432cd-62bd-40bc-bc1c-a12d53bcbdcf`

Probe pid: `41ea689a-7e05-463b-915a-90e63b8c0572`

**DY_014** - FINAL_RESERVED; danlab; 2020-07-17; session 1; probe00. Admitted: True. No exclusion.

Session eid: `bd456d8f-d36e-434a-8051-ff3997253802`

Probe pid: `d258bca2-bf18-4491-8d57-5322f705caec`

**PL033** - DEVELOPMENT; hausserlab; 2022-10-04; session 2; probe00. Admitted: True. No exclusion.

Session eid: `62902992-8432-46fb-af12-6392012e58c7`

Probe pid: `edc82c06-83fd-44be-a41e-52fdeea728b4`

**SWC_043** - DEVELOPMENT; hoferlab; 2020-09-19; session 1; probe00. Admitted: True. No exclusion.

Session eid: `88d24c31-52e4-49cc-9f32-6adbeb9eba87`

Probe pid: `3fd2d2b3-9415-4b6e-b392-40427fb1c388`

**ZFM-01576** - FINAL_RESERVED; mainenlab; 2020-12-03; session 1; probe00. Admitted: True. No exclusion.

Session eid: `9e9c6fc0-4769-4d83-9ea4-b59a1230510e`

Probe pid: `6eb8be8d-d089-43c6-b2e4-a6558ca16dcf`

**SWC_038** - DEVELOPMENT; mrsicflogellab; 2020-08-01; session 1; probe01. Admitted: True. No exclusion.

Session eid: `03063955-2523-47bd-ae57-f7489dd40f15`

Probe pid: `7bd5627e-b02e-47f1-b476-4bf8eaa726b3`

**NR_0027** - FINAL_RESERVED; steinmetzlab; 2022-08-23; session 1; probe01. Admitted: True. No exclusion.

Session eid: `ae8787b1-4229-4d56-b0c2-566b61a25b77`

Probe pid: `310c60b6-d68f-4018-a86a-3668ce296837`

**CSH_ZAD_026** - DEVELOPMENT; zadorlab; 2020-08-17; session 1; probe01. Admitted: True. No exclusion.

Session eid: `81a78eac-9d36-4f90-a73a-7eb3ad7f770b`

Probe pid: `03d2d8d1-a116-4763-8425-4ef7b1c1bd35`

**NYU-30** - DEVELOPMENT; angelakilab; 2020-10-20; session 1; probe00. Admitted: True. No exclusion.

Session eid: `77e6dc6a-66ed-433c-b1a2-778c914f523c`

Probe pid: `7b05cccc-44f6-4491-a0ea-e38d6e95513d`

**UCLA033** - FINAL_RESERVED; churchlandlab_ucla; 2022-02-17; session 1; probe00. Admitted: False. Exclusion: FEWER_THAN_8_C_QUALIFIED_UNITS.

Session eid: `5455a21c-1be7-4cae-ae8e-8853a8d5f55e`

Probe pid: `e96cbd77-5fdf-4a35-81f4-4a6361bded65`

**KS051** - DEVELOPMENT; cortexlab; 2021-05-13; session 1; probe01. Admitted: True. No exclusion.

Session eid: `7082d8ff-255a-47d7-a839-bf093483ec30`

Probe pid: `2122d807-13ab-494e-a1cc-e55cf24d3e9f`

**DY_011** - FINAL_RESERVED; danlab; 2020-01-31; session 1; probe00. Admitted: True. No exclusion.

Session eid: `7bee9f09-a238-42cf-b499-f51f765c6ded`

Probe pid: `26118c10-35dd-4ab1-9f0f-b9a89a1da070`

**ZFM-01937** - DEVELOPMENT; mainenlab; 2021-04-08; session 1; probe00. Admitted: True. No exclusion.

Session eid: `113c5b6c-940e-4b21-b462-789b4c2be0e5`

Probe pid: `af2a0072-e17e-4368-b80b-1359bf6d4647`

**CSH_ZAD_019** - DEVELOPMENT; zadorlab; 2020-08-16; session 1; probe00. Admitted: True. No exclusion.

Session eid: `5adab0b7-dfd0-467d-b09d-43cb7ca5d59c`

Probe pid: `b4131145-9675-4433-88e1-9ae016c701dd`

**NYU-21** - FINAL_RESERVED; angelakilab; 2020-08-13; session 2; probe00. Admitted: False. Exclusion: NATIVE_WHEEL_NOT_STRICTLY_INCREASING.

Session eid: `8c33abef-3d3e-4d42-9f27-445e9def08f9`

Probe pid: `f475ae14-9415-453e-b800-1480ea1c868d`

**UCLA035** - DEVELOPMENT; churchlandlab_ucla; 2022-02-18; session 1; probe01. Admitted: True. No exclusion.

Session eid: `6f36868f-5cc1-450c-82fa-6b9829ce0cfe`

Probe pid: `7c94d733-b913-4064-83f2-37422712204c`

**ZFM-01936** - FINAL_RESERVED; mainenlab; 2021-01-20; session 1; probe00. Admitted: True. No exclusion.

Session eid: `4aa1d525-5c7d-4c50-a147-ec53a9014812`

Probe pid: `fddceb2e-82ba-493d-baba-c5d8af65981f`

## S2. Source support, native anatomy and unit QC

Anatomy was native MOp parent/layers1,2/3,4,5,6a,6b only. Map cluster channels to native channel atlas entries; do not positionally match an aggregate region array. Source/native annotation differences are retained in the original metadata records. Source label1 is upstream provider-good curation over the recording, not an A/C-only metric. No layer-specific causal or histological-distance claim was registered.

AP duration, sample rate, saved channel count and source header/file-size accounting defined recording support. Source sync was finite, Nx2 and strictly increasing in both clocks. Piecewise-linear probe-to-session mapping followed the provider convention and did not extrapolate eligible epochs. Authorized-role spike times were finite, nondecreasing and inside support to one AP sample. Essential inconsistencies stopped admission; they were not dropped or converted to zeros. Invalid/saturation intervals were mapped from sample bounds through the same clock. Only known selected-probe annotations were available; absence of another annotation is unknown artifact burden, not a guarantee of lossless or artifact-free acquisition.

Physiology used A or C warm-up-plus-score exposure, with no ISI crossing an epoch/gap. Required rate0.5-100Hz inclusive,>=100spikes,>=99 adjacent within-epoch ISI pairs, refractory fraction(ISI<1ms)<=0.005; each original A/C quartile required>=10s exposure and>=0.1Hz. Rank by refractory fraction ascending, rate descending, UUID lexical. Primary first8 units were fixed before B/E/D scoring. Final source/C totals and all48 selected unit IDs/UUIDs with C-only metrics follow; achieved quartile values are retained exactly in the companion CSV, not inferred from Final D.

|Mouse|C epochs|D metadata epochs|C-qualified|Admitted|
|---|---|---|---|---|
|UCLA037|222|171|169|True|
|DY_014|335|218|49|True|
|ZFM-01576|601|402|29|True|
|NR_0027|484|191|17|True|
|UCLA033|263|154|6|False|
|DY_011|227|154|17|True|
|NYU-21|not read|not read|not read|False|
|ZFM-01936|336|224|66|True|

|Mouse/rank|Cluster ID|Selected UUID|C Hz|ISI fraction|
|---|---|---|---|---|
|UCLA037/1|174|3f1a042f-c9a0-4a4c-a2b8-1c9b15f56ac6|71.68919|0|
|UCLA037/2|506|8c5f533b-2f67-466f-a578-9206f5138335|49.84685|0|
|UCLA037/3|68|75ac4123-0520-49f7-ac09-72a02219d441|39.93694|0|
|UCLA037/4|234|35a1c54a-e339-44bd-a5c9-c42f9b7fbfe4|37.02703|0|
|UCLA037/5|35|af921fbd-50ab-4ed3-afab-4ee7e45b120d|23.75676|0|
|UCLA037/6|387|53760695-9471-44a3-a831-76870f9884d9|20.54054|0|
|UCLA037/7|349|876b6a1a-6fe1-4dd0-b011-1652f6efb783|19.62162|0|
|UCLA037/8|558|ea8c0b64-364c-4bba-8739-37dec45347e3|19.48198|0|
|DY_014/1|516|9f801920-7ad3-48d8-8f56-5614fab4b2cd|48.82985|0|
|DY_014/2|512|70e70cac-416e-41f0-8130-864a56753e59|30.53134|0|
|DY_014/3|475|8301a68c-1188-4623-93c2-a2eaa9c58b22|20.69552|0|
|DY_014/4|557|837d26bc-4d00-4664-8c9b-65b62027d901|19.80896|0|
|DY_014/5|436|0d872743-4a9f-4fa5-a176-df8016ef0d09|16.83881|0|
|DY_014/6|568|a4c5418d-4f4b-453e-a25d-a8a368df3465|15.60597|0|
|DY_014/7|511|c8606f83-b535-49f2-b9aa-585d97ea0ea0|15.53731|0|
|DY_014/8|561|4be80f2b-5114-42c1-8ebc-9ebbde69c0eb|15.15224|0|
|ZFM-01576/1|361|5294eedb-36a1-4b35-b0da-b3eac35aa23a|17.18636|0|
|ZFM-01576/2|409|d3976615-c44a-4013-944a-e7ba50475409|14.13977|0|
|ZFM-01576/3|410|1c091af3-9f35-4dae-929d-a04fcca8ff1f|13.50083|0|
|ZFM-01576/4|355|4035f8e5-d057-4c70-9511-a13f30e2337b|6.575707|0|
|ZFM-01576/5|442|251ae6cc-9060-49df-af73-7dbaf4c3fe4e|5.44426|0|
|ZFM-01576/6|365|694534c9-0692-4846-88c5-2c4626c2a0ea|5.069884|0|
|ZFM-01576/7|400|3d745e26-768a-4155-9266-46bf2accb861|4.104825|0|
|ZFM-01576/8|372|02c5be99-098a-4e72-b738-86a36f19ac8d|3.745424|0|
|NR_0027/1|398|4dff9d81-8f12-441f-ac7a-001271f97d90|7.553719|0|
|NR_0027/2|469|a02d8b2e-2bbb-4146-be2c-c37609ec5a5d|6.237603|0|
|NR_0027/3|384|6003e131-a4c6-4100-8a59-54fa641db907|5.183884|0|
|NR_0027/4|368|13a1235d-7f8d-4d9e-9337-d217f2f937b0|4.020661|0|
|NR_0027/5|768|a0aef07f-9539-4f4d-a216-b401a01a87ea|1.801653|0|
|NR_0027/6|478|78f54d3a-7e73-45c7-a003-b1f29869794b|1.692149|0|
|NR_0027/7|404|8e5e647b-1ca8-4bf3-976c-00cd2b020339|1.692149|0|
|NR_0027/8|356|47234cc4-2f2e-43c5-adcf-7b7cd455cc3e|1.545455|0|
|DY_011/1|451|f99bb337-2301-4f09-b364-a88edac0e6d8|36.44493|0|
|DY_011/2|436|05a19746-fd06-422b-8d36-fe66fdb7f55e|9.242291|0|
|DY_011/3|434|59ed37ff-4f1f-4658-9aa8-757c101ba6f6|7.973568|0|
|DY_011/4|383|f68e3d9a-864d-414c-ad4c-44af05e26f73|4.39207|0|
|DY_011/5|568|3157dcaf-9e70-4e36-b395-e38a7da8fe5b|3.651982|0|
|DY_011/6|571|aec45486-7a59-4524-93ca-bc22a69a2538|3.599119|0|
|DY_011/7|423|2cccc7c6-2f2b-466f-a973-874e7ee9a9c7|1.837004|0|
|DY_011/8|580|f918decf-0572-42dc-bdda-48065ff54101|1.682819|0|
|ZFM-01936/1|605|e1750c6b-84fc-49a1-870f-a2643607244d|31.42262|0|
|ZFM-01936/2|625|812b9053-cae4-4f32-ba9c-18fd7b53cc12|26.71429|0|
|ZFM-01936/3|930|bd9471e7-0d36-4f1d-9ea1-8b506ab4c015|17.91071|0|
|ZFM-01936/4|590|42048ed9-f4dd-4bbb-b14e-5415b576f48c|12.38095|0|
|ZFM-01936/5|589|eb501e08-0ac5-4f80-b7ea-88e36a500a57|12.05357|0|
|ZFM-01936/6|517|11c62a4e-c880-4ba8-a194-fa718a1a4905|9.931548|0|
|ZFM-01936/7|708|039e9921-ca1c-4881-a9b9-302b60b4ce19|9.491071|0|
|ZFM-01936/8|632|e9308ba8-3ff0-43d3-bdf2-ed1c75fbbf25|9.136905|0|

The full CSV retains C spike counts, exposure, all four quartile rates/exposures and rank. C-level summaries include UCLA033's source-pass/QC-fail state. NYU-21 had no C-neural projection because its source gate failed. Main Figure7 and `FINAL_ANATOMY_LAYER_PROXY.csv` retain primary/sensitivity anatomy and root/unknown categories; native depth was unavailable. Neighboring contact-index checks use±2 positions and are not physical distance estimates.

## S3. Trial roles, observation masks and strictly past support

For original native trial count N, Development cuts are floor(0.6N) and floor(0.8N); Final cut is floor(0.6N). Role intervals are half-open original-row ranges. Drop the last trial before and first trial after each cut from adjoining roles. Never reindex or recut after invalid rows. Native ordinal, event values, missingness, saturation clock and role masks are frozen in `paper15_r1/metadata/*_task.json` and `paper15_final1/metadata/*_task.json`; original source hashes are in SOURCE_HASHES.json. The full original masks remain audit inputs, not regenerated from a guessed trial count.

A primary epoch spans stimulus−0.5s through stimulus+0.5s, with ten50-ms warm-up and ten score bins. Its neural interval lies within the trial/support/sync domain and cannot overlap another epoch. Finite start/stim/goCue/feedback/end obey source ordering(start<=stim<=feedback<=end; goCue inside trial before feedback), without an arbitrary cue/stim ordering assumption. Known invalid or saturation overlap excludes the whole epoch for all models. For behavioral predictors, the extra predecessor support spans stimulus−1s through stimulus+0.5s and lies within the permitted chronological role and recording. Neural history still resets at epochStart; behavioral predecessors may precede the current trial. Zero counts in valid bins remain observations.

All events/samples satisfy time<binStart before contributing. Equality is unavailable at the boundary. Wheel positions are backward sample-and-hold, not interpolated through future observations. Current choice/reward appears only after its source event. Prior completed-trial codes are frozen at epochStart and use already observed task events. A stimulus exactly at a bin start enters only later predictor rows; stimulus-aligned analysis windows are an offline sampling design, not a guarantee of live prediction at unknown future stimuli.

Minimum Development admission was80A/40B/40E epochs and8units, with>=8mice/>=4labs. Final needed80C/60D metadata-valid epochs and8C-qualified units;>=8mice was required for confirmation,6-7 only descriptive,<6 stopped D. D-neural quality/score was not an eligibility screen. Any essential integrity failure discovered during the one batch could not trigger replacement, recalibration or retry. The actual six-mouse fallback was fixed before observing D results.

## S4. Native binary64 correction and complete attempt ledger

The original Development source implementation serialized native numeric task data with ten decimal places. That altered strict-past wheel-derived inputs in5/10admitted mice; the execution stopped at its source-implementation gate. Original358 completed fits had numerical endpoint certificates on rounded inputs, one STARTED attempt lacked an endpoint, and251 planned main fits were unattempted. No original coefficient was reused as a corrected fit, and numerical success was not called scientific source validity.

A separately prospective corrective mission retained exact binary64 task values and native absent-side missingness. Source audit checked96,642finite numeric table cells(not distinct timestamps) and382,487strict predecessor queries. PL033 trial224's equal-time wheel event was excluded under strict<. The corrected Development study completed610main+525sensitivity=1,135starts. Historical359+corrective1,135=1,494before Final; Final72+320=392; full historical total1,886. The original aggregate ceiling1,928remains in the frozen protocol; separate corrective and Final authorizations are disclosed rather than claiming retrospective budget compliance. Final explicit caps were96main/440sensitivity; no retry or post-D fitting occurred.

The earlier source failure, numerical stops, review failures, partial execution and subsequent archive/self-log formatting incidents remain in the old evidence directories. Their exact bytes/hashes are preserved. Writing this paper does not retrospectively relabel any failed scientific gate. It introduces no optimizer rescue or new data.

## S5. Full predictor definitions and transforms

Let b be binStart; I(condition) its indicator; clip(a, L)=max(0, min(a, L)). Unobserved events have zero indicator/elapsed/value columns. The following are the37 non-intercept nuisance columns before training-only standardization. Values are source observations available strictly before b.

|Columns|Raw definition|
|---|---|
|1-2|e=clip(b−trialStart,10)/10 and e squared|
|3-5|r=I(stim<b)clip(b−stim,1), r squared, r cubed|
|6-7|I(stim<b) times left/right contrast; source-absent side becomes0|
|8-9|I(stim<b) times left/right positive-contrast indicator|
|10-11|Columns6/7 multiplied by r|
|12-13|I(goCue<b), I(goCue<b)clip(b−goCue,1)|
|14-17|I(response<b), signed choice times response indicator, I(feedback<b), feedback type times feedback indicator|
|18-19|Reward code and signed choice of most recent completed trial with corresponding event before epochStart; frozen at reset|
|20-21|Original trial ordinal/1000 and its square|
|22-23|Session time b/3600 and its square|
|24|Backward-held wheel position at b minus position at epochStart, radians|
|25-28|Signed past displacement over0.05,0.1,0.25,0.5s|
|29-32|Total absolute observed encoder increments over the same four intervals, including the preceding held value|
|33-36|Squared signed wheel velocity: (displacement/h)^2, for each interval|
|37|Indicator absolute0.05-s displacement>0.001radians|

For columns33-36, the exact operation is (signed displacement/h) squared. No current-bin response or retrospective firstMovement estimate is used. Source-NaN on exactly one contrast side means absent and is mapped to0; both absent/unknown or a finite value outside[0,1] excludes that trial. Trial ordinal is not normalized by the future trial count. Source previous-trial codes are behavior, not inherited neural state.

Four disjoint neural windows are [b−0.05, b),[b−0.1, b−0.05),[b−0.2, b−0.1),[b−0.5, b−0.2). Count/windowDuration gives Hz, with all outside-epoch neural history zero. Four features per unit create4U history columns. No within-bin target count is a predictor.

Nonconstant ordinary inputs use A/C score-row population means and SDs, then±3clipping. SD<1e-8 gives an identically zero input and a fixed-zero coefficient; intercepts are not standardized. Persist nominal/active maps, scales, units, trial IDs and masks. C first standardizes microbin rates by A/C score-row mean/SD without clipping; its projected history q then receives a separate A/C score-row transform and±3clipping. These are feature transforms, not predicted-rate or generated-count clipping.

## S6. Full model equations, gauges and parameter counts

For joint population bins, Poisson exposure is explicit and factorials remain in reported likelihood:

$$\mu_{tu}=\Delta e^{\eta_{tu}},\qquad \ell_t=\sum_{u=1}^{U}\left[y_{tu}\log\mu_{tu}-\mu_{tu}-\log(y_{tu}!)\right].$$

With nuisance x and unit/window history h, the frozen linear predictors are:

$$\eta^{B0}_{tu}=\alpha_u,\qquad \eta^{B1}_{tu}=\alpha_u+\beta_u^{\mathsf{T}}x_t.$$

$$\eta^{B2}_{tu}=\eta^{B1}_{tu}+\sum_l a_{ul}h_{t, u, l}.$$

$$\eta^{B3}_{tu}=\eta^{B1}_{tu}+\sum_{v\ne u, l}c_{uvl}h_{t, v, l},\qquad \eta^{B4}_{tu}=\eta^{B2}_{tu}+\sum_{v\ne u, l}c_{uvl}h_{t, v, l}.$$

Nominal counts are qB0=U, qB1=38U, qB2=42U, qB3=U[38+4(U−1)], qB4=U(38+4U). For U8:8,304,336,528,560. S10 has41 rather than37 nuisance columns; unit-count cases substitute their actual U. Actual active/free counts are separately retained in all certificates; stored coefficient-vector length is not automatically a nominal count when columns are fixed.

D has a reference-zero state offset, softmax transition rows(reference last logit0) and initial probabilities with the same gauge:

$$g_t(k)=\prod_u \mathrm{Pois}\left(y_{tu};\Delta e^{\eta^{B4}_{tu}+\delta_{ku}}\right),\qquad \delta_{0u}=0.$$

$$p_t(y_t)=\sum_k a_t(k)g_t(k),\qquad r_t(k)=\frac{a_t(k)g_t(k)}{\sum_j a_t(j)g_t(j)},\qquad a_{t+1}=r_t P.$$

Reset a to pi at every epoch; process warm-up without score LL. Conditional score LL equals logL(warm+score)−logL(warm), including the warm-up derivative. Log normalizers are accumulated in float64. Whole-sequence likelihoods are not exponentiated; no posterior smoothing/current-bin plug-in is used. At all delta0, D recovers B4. qD=qB4+(K−1)U+K(K−1)+(K−1), giving571(K2)or584(K3)at U8.

C projects standardized strictly past50-ms microbin rates z through the first r orthonormal DCT-II columns over frozen unit order:

$$R_{v0}=U^{-1/2},\qquad R_{vj}=\sqrt{2/U}\cos\left(\pi(v+1/2)j/U\right)\quad(j>0).$$

$$q_t=\sum_{j=1}^{10}w_jR^{\mathsf{T}}z_{t-j},\qquad w_j=\frac{e^{-(j-1)0.05/\tau}}{\sum_{i=1}^{10}e^{-(i-1)0.05/\tau}},\qquad \eta^C_{tu}=\eta^{B4}_{tu}+\gamma_u^{\mathsf{T}}\widetilde q_t.$$

Here tilde q denotes the separately calibrated state transform. qC=qB4+Ur,568(r1)or576(r2)at U8. Tau is0.1or0.25s and state history truncates at0.5s. No recurrent learned integration, autonomous simulation or estimated projection is present. Added coefficients0 recover B4.

S is an independent per-bin mixture with B4 emissions and constant weights:

$$p_S(y_t)=\sum_{k=1}^{K_S}\pi_k g_t(k),\qquad q_S=q_{B4}+(K_S-1)U+(K_S-1).$$

The capacity pair is KS=KD+1, so qS578(K3)or587(K4)at U8. The selected D3/S4 pair has584/587parameters per seed. A same-K HMM whose transition rows all equal pi reproduces the IID mixture mathematically; the registered synthetic identity is separate from this larger static guard. D and S each ensemble three pre-bin joint masses uniformly, maintaining each D seed's own filter. Do not average state coefficients or infer equal effective capacity from the nominal count.

## S7. Selection grids, initialization and numerical gates

The objective is normalized by population score bins T:

$$J(\theta)=-\frac{1}{T}\sum_{t\in\mathrm{score}}\ell_t(\theta)+\frac{\lambda}{2}\sum_{i\in\mathrm{nonintercept}}\theta_i^2.$$

Intercepts are unpenalized; all non-intercept free coefficients, including mixture/transition logits and state offsets, are penalized. B0 is the constrained stationary MLE:log(total count/(TDelta)), bounded to[-8,8]; all-zero target optimum−8. Other intercept initialization is log[(training score count+0.5)/(TDelta)], projected to the same box. The0.5pseudocount is only initialization, not a likelihood change. Other linear terms start0. D/S seed11/23/37 offsets are independent Uniform[-0.05,0.05], pi logits0; D's free transition logit in row i and column j is 2 I(i=j) - 2 I(i=K-1), with the last reference column fixed to zero. This is the frozen diagonal preference, not a tuned initializer. No mouse borrows another's fitted coefficients and no Final fit borrows Development coefficients.

Bounds:intercepts[-8,8], linear[-1,1], state offset[-2,2], free logits[-4,4]. B4 penalties and transformations are shared in D/C/S. No predicted rate clipping. All fits use float64. L-BFGS-B maxiter2000, maxfun80000, maxls40, ftol1e-12, gtol1e-6; no retries, alternative solver or budget amendment. B0's closed form is still checked numerically.

For a minimization problem, the frozen outward-gradient projected coordinate is zero only at a lower bound with g>0 or at an upper bound with g<0; otherwise retain g. PG is the infinity norm. Acceptance is PG<=0.001. Independent real endpoint AD and every central finite-difference step1e-4,1e-5,1e-6 must satisfy max coordinate |g−gref|/max(1,|g|,|gref|)<=1e-5; no favorable-step selection. Synthetic analytic/AD error is<=1e-8. At bounds, finite differences compare the mathematical extension's unconstrained derivative before PG is applied. A finite-difference explanation does not clear failure of its original gate. Every optimizer termination, failed seed and partial start remains recorded.

Development grid:ridge0.01/0.1/1; D K2/3 with3seeds; C r1/2 andtau0.1/0.25; S K3/4 with3seeds. Per mouse:1B0+12otherbaseline+18D+12C+18S=61starts. The corrected ten-mouse main total was610. Each candidate required all fixed animals/starts; B selection used equal-mouse LL/Q. Ties within1e-6 favored fewer nominal parameters, stronger ridge, smaller K/r, smaller tau, then lexical ID. S was selected across ridge only at KD+1. No E or Final choice altered that grid.

Selected policies:B0; B1_l0.01; B2_l0.01; B3_l1.0; B4_l0.1; C_r1_t0.1_l0.1; D_k3_l0.01; S_k4_l0.01. Final used12main fits per admitted mouse and no search. The complete table of37 seed-grouped candidates representing61 optimizer starts per mouse follows, including unselected configurations and nominal counts; the immutable original table is copied byte-for-byte.

|Configuration|B LL/unit-bin|Nominal q|Selected|
|---|---|---|---|
|B0|-0.9915065395|8|True|
|B1_l0.01|-0.8989816559|304|True|
|B1_l0.1|-0.8991664954|304|False|
|B1_l1.0|-0.9001828796|304|False|
|B2_l0.01|-0.8543851683|336|True|
|B2_l0.1|-0.8547361175|336|False|
|B2_l1.0|-0.8708143614|336|False|
|B3_l0.01|-0.8996660688|528|False|
|B3_l0.1|-0.8886034998|528|False|
|B3_l1.0|-0.8871836557|528|True|
|B4_l0.01|-0.8572680559|560|False|
|B4_l0.1|-0.8503982647|560|True|
|B4_l1.0|-0.8634147755|560|False|
|D_k2_l0.01|-0.8437139809|571|False|
|D_k2_l0.1|-0.8481113974|571|False|
|D_k2_l1.0|-0.8634147756|571|False|
|D_k3_l0.01|-0.8410101819|584|True|
|D_k3_l0.1|-0.845886661|584|False|
|D_k3_l1.0|-0.8634147719|584|False|
|C_r1_t0.1_l0.01|-0.8573305244|568|False|
|C_r1_t0.1_l0.1|-0.850480291|568|True|
|C_r1_t0.1_l1.0|-0.8629618939|568|False|
|C_r1_t0.25_l0.01|-0.8573687475|568|False|
|C_r1_t0.25_l0.1|-0.8504835277|568|False|
|C_r1_t0.25_l1.0|-0.8630530237|568|False|
|C_r2_t0.1_l0.01|-0.8574176475|576|False|
|C_r2_t0.1_l0.1|-0.8505600675|576|False|
|C_r2_t0.1_l1.0|-0.8625424985|576|False|
|C_r2_t0.25_l0.01|-0.8574485586|576|False|
|C_r2_t0.25_l0.1|-0.8505151442|576|False|
|C_r2_t0.25_l1.0|-0.8625945622|576|False|
|S_k3_l0.01|-0.8407447671|578|False|
|S_k3_l0.1|-0.8458782343|578|False|
|S_k3_l1.0|-0.8634147785|578|False|
|S_k4_l0.01|-0.8391156589|587|True|
|S_k4_l0.1|-0.844934764|587|False|
|S_k4_l1.0|-0.8634147785|587|False|

## S8. Complete Final numerical acceptance

All72main and320sensitivity C fits passed; no retries occurred. There are392endpoint certificates. Full path, source SHA, status, active/free count, stored coefficient-vector length, PG, AD, max of the three FD errors and iterations are supplied in `tables/FINAL_NUMERICAL_CERTIFICATES.csv`; original main/sensitivity attempts are also copied unchanged. The following table includes every completed endpoint, with compact identifiers. Configuration names identify original seed/ridge/rank; baseline sensitivity policies use their unchanged selected ridges. Scientific positive-claim status remains independent of numerical success.

|C fit group|Endpoints|Largest PG|Largest AD|Largest FD|
|---|---|---|---|---|
|Main|72|1.329192e-05|2.37113e-14|2.040363e-08|
|Sensitivity|320|1.239118e-05|2.608161e-14|3.215293e-08|

|Mouse/case/configuration|Free q|PG|AD error|FD max|Iter|
|---|---|---|---|---|---|
|DY_011/PRIMARY/B0|8|3.823e-15|3.777e-15|3.473e-09|0|
|DY_011/PRIMARY/B1_l0.01|304|8.105e-07|7.75e-17|8.452e-09|272|
|DY_011/PRIMARY/B2_l0.01|336|9.674e-07|6.072e-17|8.424e-09|283|
|DY_011/PRIMARY/B3_l1.0|528|1.244e-06|1.527e-16|8.458e-09|71|
|DY_011/PRIMARY/B4_l0.1|560|1.085e-06|6.072e-17|8.4e-09|115|
|DY_011/PRIMARY/C_r1_t0.1_l0.1|568|7.559e-07|7.633e-17|8.405e-09|117|
|DY_011/PRIMARY/D_k3_l0.01_s11|584|9.38e-07|7.878e-16|8.385e-09|354|
|DY_011/PRIMARY/D_k3_l0.01_s23|584|7.706e-07|7.677e-16|8.38e-09|401|
|DY_011/PRIMARY/D_k3_l0.01_s37|584|9.675e-07|4.881e-16|8.372e-09|407|
|DY_011/PRIMARY/S_k4_l0.01_s11|587|8.713e-07|1.087e-16|8.374e-09|396|
|DY_011/PRIMARY/S_k4_l0.01_s23|587|9.663e-07|1.61e-16|8.376e-09|342|
|DY_011/PRIMARY/S_k4_l0.01_s37|587|8.783e-07|4.171e-16|8.373e-09|361|
|DY_014/PRIMARY/B0|8|1.846e-14|1.879e-14|3.97e-09|0|
|DY_014/PRIMARY/B1_l0.01|304|1.861e-06|4.341e-16|1.118e-08|261|
|DY_014/PRIMARY/B2_l0.01|336|3.574e-06|2.22e-16|1.118e-08|267|
|DY_014/PRIMARY/B3_l1.0|528|2.658e-06|3.782e-16|1.09e-08|47|
|DY_014/PRIMARY/B4_l0.1|560|1.329e-06|2.884e-16|1.115e-08|108|
|DY_014/PRIMARY/C_r1_t0.1_l0.1|568|4.558e-06|1.995e-16|1.116e-08|108|
|DY_014/PRIMARY/D_k3_l0.01_s11|584|2.617e-06|3.894e-15|1.038e-08|647|
|DY_014/PRIMARY/D_k3_l0.01_s23|584|2.537e-06|6.281e-15|1.045e-08|400|
|DY_014/PRIMARY/D_k3_l0.01_s37|584|1.483e-06|3.699e-15|1.045e-08|403|
|DY_014/PRIMARY/S_k4_l0.01_s11|587|2.047e-06|4.605e-16|1.059e-08|347|
|DY_014/PRIMARY/S_k4_l0.01_s23|587|2.208e-06|3.851e-16|1.058e-08|413|
|DY_014/PRIMARY/S_k4_l0.01_s37|587|6.462e-06|3.669e-16|1.059e-08|452|
|NR_0027/PRIMARY/B0|8|7.219e-15|7.033e-15|1.07e-09|0|
|NR_0027/PRIMARY/B1_l0.01|304|7.069e-07|8.929e-17|3.033e-09|128|
|NR_0027/PRIMARY/B2_l0.01|336|8.927e-07|7.86e-17|3.026e-09|132|
|NR_0027/PRIMARY/B3_l1.0|528|7.8e-07|2.776e-16|3.048e-09|60|
|NR_0027/PRIMARY/B4_l0.1|560|9.4e-07|1.006e-16|3.044e-09|70|
|NR_0027/PRIMARY/C_r1_t0.1_l0.1|568|9.464e-07|1.362e-16|3.042e-09|82|
|NR_0027/PRIMARY/D_k3_l0.01_s11|584|9.542e-07|5.742e-16|2.977e-09|219|
|NR_0027/PRIMARY/D_k3_l0.01_s23|584|9.993e-07|3.162e-16|2.987e-09|179|
|NR_0027/PRIMARY/D_k3_l0.01_s37|584|8.267e-07|5.612e-16|2.985e-09|165|
|NR_0027/PRIMARY/S_k4_l0.01_s11|587|9.068e-07|7.3e-16|2.987e-09|175|
|NR_0027/PRIMARY/S_k4_l0.01_s23|587|9.322e-07|4.229e-16|2.987e-09|189|
|NR_0027/PRIMARY/S_k4_l0.01_s37|587|8.48e-07|5.046e-16|2.988e-09|167|
|UCLA037/PRIMARY/B0|8|1.218e-14|1.225e-14|5.818e-09|0|
|UCLA037/PRIMARY/B1_l0.01|304|1.329e-05|2.333e-16|1.971e-08|266|
|UCLA037/PRIMARY/B2_l0.01|336|2.611e-06|2.793e-16|1.97e-08|283|
|UCLA037/PRIMARY/B3_l1.0|528|7.557e-07|3.192e-16|2.04e-08|40|
|UCLA037/PRIMARY/B4_l0.1|560|6.572e-06|2.307e-16|1.985e-08|107|
|UCLA037/PRIMARY/C_r1_t0.1_l0.1|568|1.662e-06|2.051e-16|1.985e-08|107|
|UCLA037/PRIMARY/D_k3_l0.01_s11|584|1.503e-06|6.807e-15|1.961e-08|408|
|UCLA037/PRIMARY/D_k3_l0.01_s23|584|1.092e-05|4.341e-15|1.959e-08|599|
|UCLA037/PRIMARY/D_k3_l0.01_s37|584|1.415e-06|1.352e-14|1.959e-08|569|
|UCLA037/PRIMARY/S_k4_l0.01_s11|587|7.834e-06|3.771e-16|1.963e-08|352|
|UCLA037/PRIMARY/S_k4_l0.01_s23|587|3.685e-06|4.369e-16|1.964e-08|340|
|UCLA037/PRIMARY/S_k4_l0.01_s37|587|2.413e-06|4.778e-16|1.964e-08|347|
|ZFM-01576/PRIMARY/B0|8|2.326e-14|2.371e-14|1.878e-09|0|
|ZFM-01576/PRIMARY/B1_l0.01|304|9.506e-07|9.845e-17|5.151e-09|163|
|ZFM-01576/PRIMARY/B2_l0.01|336|1.919e-06|1.082e-16|5.149e-09|168|
|ZFM-01576/PRIMARY/B3_l1.0|528|1.141e-06|3.747e-16|4.809e-09|39|
|ZFM-01576/PRIMARY/B4_l0.1|560|7.655e-07|1.83e-16|5.101e-09|66|
|ZFM-01576/PRIMARY/C_r1_t0.1_l0.1|568|6.054e-07|1.639e-16|5.109e-09|68|
|ZFM-01576/PRIMARY/D_k3_l0.01_s11|584|8.133e-07|1.531e-15|4.841e-09|254|
|ZFM-01576/PRIMARY/D_k3_l0.01_s23|584|9.593e-07|4.593e-16|4.847e-09|251|
|ZFM-01576/PRIMARY/D_k3_l0.01_s37|584|9.952e-07|5.277e-16|4.832e-09|294|
|ZFM-01576/PRIMARY/S_k4_l0.01_s11|587|9.269e-07|2.977e-16|4.867e-09|263|
|ZFM-01576/PRIMARY/S_k4_l0.01_s23|587|3.417e-06|1.141e-15|4.867e-09|320|
|ZFM-01576/PRIMARY/S_k4_l0.01_s37|587|9.659e-07|7.594e-16|4.869e-09|300|
|ZFM-01936/PRIMARY/B0|8|4.363e-15|4.777e-15|2.567e-09|0|
|ZFM-01936/PRIMARY/B1_l0.01|304|1.345e-06|1.002e-16|7.28e-09|192|
|ZFM-01936/PRIMARY/B2_l0.01|336|9.31e-07|9.584e-17|7.284e-09|194|
|ZFM-01936/PRIMARY/B3_l1.0|528|1.599e-06|1.874e-16|6.665e-09|37|
|ZFM-01936/PRIMARY/B4_l0.1|560|7.346e-07|1.37e-16|7e-09|71|
|ZFM-01936/PRIMARY/C_r1_t0.1_l0.1|568|8.077e-07|9.714e-17|7.002e-09|71|
|ZFM-01936/PRIMARY/D_k3_l0.01_s11|584|8.762e-07|5.333e-15|7.288e-09|218|
|ZFM-01936/PRIMARY/D_k3_l0.01_s23|584|8.273e-07|8.389e-15|7.289e-09|216|
|ZFM-01936/PRIMARY/D_k3_l0.01_s37|584|3.193e-06|9.527e-15|7.289e-09|209|
|ZFM-01936/PRIMARY/S_k4_l0.01_s11|587|8.982e-07|7.761e-16|7.28e-09|203|
|ZFM-01936/PRIMARY/S_k4_l0.01_s23|587|9.716e-07|5.593e-16|7.284e-09|204|
|ZFM-01936/PRIMARY/S_k4_l0.01_s37|587|2.009e-06|4.869e-16|7.28e-09|204|
|DY_011/S01/B0|5|3.823e-15|3.777e-15|3.482e-09|0|
|DY_011/S01/B1|190|9.702e-07|7.566e-17|8.459e-09|176|
|DY_011/S01/B2|210|1.954e-06|6.072e-17|8.425e-09|186|
|DY_011/S01/B3|270|6.787e-07|1.388e-16|8.454e-09|41|
|DY_011/S01/B4|290|1.244e-06|6.105e-17|8.409e-09|70|
|DY_011/S02/B0|12|3.823e-15|3.777e-15|4.361e-09|0|
|DY_011/S02/B1|456|1.652e-06|8.804e-17|1.044e-08|368|
|DY_011/S02/B2|504|1.07e-05|1.367e-16|1.045e-08|364|
|DY_011/S02/B3|984|2.626e-06|2.082e-16|1.072e-08|97|
|DY_011/S02/B4|1032|1.579e-06|1.791e-16|1.049e-08|176|
|DY_011/S04/B0|8|3.994e-15|4.082e-15|6.954e-09|0|
|DY_011/S04/B1|304|8.208e-06|1.644e-16|1.548e-08|328|
|DY_011/S04/B2|336|1.239e-05|1.778e-16|1.545e-08|356|
|DY_011/S04/B3|528|5.406e-06|1.943e-16|1.564e-08|79|
|DY_011/S04/B4|560|1.146e-06|9.714e-17|1.551e-08|157|
|DY_011/S05/B0|8|4.914e-15|5.083e-15|3.446e-09|0|
|DY_011/S05/B1|304|8.701e-07|1.426e-16|7.951e-09|264|
|DY_011/S05/B2|336|7.481e-07|1.66e-16|7.939e-09|221|
|DY_011/S05/B3|528|2.511e-06|4.163e-16|7.956e-09|66|
|DY_011/S05/B4|560|1.609e-06|1.659e-16|7.922e-09|95|
|DY_011/S06/B0|8|3.823e-15|3.777e-15|3.473e-09|0|
|DY_011/S06/B1|304|8.105e-07|7.75e-17|8.452e-09|272|
|DY_011/S06/B2|336|9.674e-07|6.072e-17|8.424e-09|283|
|DY_011/S06/B3|528|1.244e-06|1.527e-16|8.458e-09|71|
|DY_011/S06/B4|560|1.085e-06|6.072e-17|8.4e-09|115|
|DY_011/S07/B0|8|9.901e-16|9.002e-16|4.441e-10|0|
|DY_011/S07/B1|304|9.451e-07|3.86e-17|8.663e-10|99|
|DY_011/S07/B2|336|8.51e-07|2.819e-17|1.233e-09|95|
|DY_011/S07/B3|528|7.97e-07|1.318e-16|7.133e-10|35|
|DY_011/S07/B4|560|9.077e-07|7.286e-17|9.576e-10|46|
|DY_011/S08/B0|8|3.823e-15|3.777e-15|3.473e-09|0|
|DY_011/S08/B1|304|8.105e-07|7.75e-17|8.452e-09|272|
|DY_011/S08/B2|336|9.674e-07|6.072e-17|8.424e-09|283|
|DY_011/S08/B3|528|1.244e-06|1.527e-16|8.458e-09|71|
|DY_011/S08/B4|560|1.085e-06|6.072e-17|8.4e-09|115|
|DY_011/S09/B0|8|3.823e-15|3.777e-15|3.473e-09|0|
|DY_011/S09/B1|304|8.105e-07|7.75e-17|8.452e-09|272|
|DY_011/S09/B2|336|9.674e-07|6.072e-17|8.424e-09|283|
|DY_011/S09/B3|528|1.244e-06|1.527e-16|8.458e-09|71|
|DY_011/S09/B4|560|1.085e-06|6.072e-17|8.4e-09|115|
|DY_011/S10/B0|8|3.823e-15|3.777e-15|3.473e-09|0|
|DY_011/S10/B1|336|7.803e-07|6.559e-17|8.458e-09|310|
|DY_011/S10/B2|368|6.901e-06|5.421e-17|8.42e-09|292|
|DY_011/S10/B3|560|1.273e-06|2.22e-16|8.458e-09|71|
|DY_011/S10/B4|592|7.377e-07|1.076e-16|8.406e-09|143|
|DY_011/S11/B0|5|3.823e-15|3.777e-15|3.482e-09|0|
|DY_011/S11/B1|190|9.702e-07|7.566e-17|8.459e-09|176|
|DY_011/S11/B2|210|1.954e-06|6.072e-17|8.425e-09|186|
|DY_011/S11/B3|270|6.787e-07|1.388e-16|8.454e-09|41|
|DY_011/S11/B4|290|1.244e-06|6.105e-17|8.409e-09|70|
|DY_014/S01/B0|5|1.846e-14|1.879e-14|3.961e-09|0|
|DY_014/S01/B1|190|1.382e-06|3.888e-16|1.118e-08|255|
|DY_014/S01/B2|210|1.351e-06|2.558e-16|1.116e-08|265|
|DY_014/S01/B3|270|1.249e-06|4.441e-16|1.089e-08|37|
|DY_014/S01/B4|290|3.156e-06|2.285e-16|1.115e-08|104|
|DY_014/S02/B0|12|1.846e-14|1.879e-14|3.961e-09|0|
|DY_014/S02/B1|456|5.328e-06|4.704e-16|1.117e-08|262|
|DY_014/S02/B2|504|3.343e-06|1.874e-16|1.116e-08|267|
|DY_014/S02/B3|984|1.913e-06|4.545e-16|1.089e-08|52|
|DY_014/S02/B4|1032|4.03e-06|2.68e-16|1.113e-08|112|
|DY_014/S03/B0|20|1.846e-14|1.879e-14|3.944e-09|0|
|DY_014/S03/B1|760|6.179e-06|3.205e-16|1.119e-08|259|
|DY_014/S03/B2|840|9.001e-06|2.955e-16|1.116e-08|268|
|DY_014/S03/B3|2280|7.097e-06|4.614e-16|1.086e-08|103|
|DY_014/S03/B4|2360|2.099e-06|2.238e-16|1.116e-08|152|
|DY_014/S04/B0|8|6.477e-15|6.703e-15|7.923e-09|0|
|DY_014/S04/B1|304|9.034e-06|5.972e-16|2.314e-08|364|
|DY_014/S04/B2|336|7.064e-06|2.732e-16|2.314e-08|373|
|DY_014/S04/B3|528|3.371e-06|5.204e-16|2.237e-08|51|
|DY_014/S04/B4|560|2.172e-06|4.137e-16|2.302e-08|148|
|DY_014/S05/B0|8|1.446e-14|1.46e-14|4.006e-09|0|
|DY_014/S05/B1|304|9.282e-06|4.189e-16|1.082e-08|239|
|DY_014/S05/B2|336|5.944e-06|2.591e-16|1.079e-08|262|
|DY_014/S05/B3|528|2.48e-06|2.914e-16|1.068e-08|42|
|DY_014/S05/B4|560|1.765e-06|3.053e-16|1.072e-08|110|
|DY_014/S06/B0|8|1.846e-14|1.879e-14|3.97e-09|0|
|DY_014/S06/B1|304|1.861e-06|4.341e-16|1.118e-08|261|
|DY_014/S06/B2|336|3.574e-06|2.22e-16|1.118e-08|267|
|DY_014/S06/B3|528|2.658e-06|3.782e-16|1.09e-08|47|
|DY_014/S06/B4|560|1.329e-06|2.884e-16|1.115e-08|108|
|DY_014/S07/B0|8|5.595e-16|5.842e-16|4.441e-10|0|
|DY_014/S07/B1|304|9.521e-07|4.571e-17|1.019e-09|77|
|DY_014/S07/B2|336|7.887e-07|5.317e-17|1.022e-09|79|
|DY_014/S07/B3|528|7.85e-07|7.633e-17|8.94e-10|30|
|DY_014/S07/B4|560|7.933e-07|4.597e-17|9.971e-10|35|
|DY_014/S08/B0|8|1.846e-14|1.879e-14|3.97e-09|0|
|DY_014/S08/B1|304|1.861e-06|4.341e-16|1.118e-08|261|
|DY_014/S08/B2|336|3.574e-06|2.22e-16|1.118e-08|267|
|DY_014/S08/B3|528|2.658e-06|3.782e-16|1.09e-08|47|
|DY_014/S08/B4|560|1.329e-06|2.884e-16|1.115e-08|108|
|DY_014/S09/B0|8|1.846e-14|1.879e-14|3.97e-09|0|
|DY_014/S09/B1|304|1.861e-06|4.341e-16|1.118e-08|261|
|DY_014/S09/B2|336|3.574e-06|2.22e-16|1.118e-08|267|
|DY_014/S09/B3|528|2.658e-06|3.782e-16|1.09e-08|47|
|DY_014/S09/B4|560|1.329e-06|2.884e-16|1.115e-08|108|
|DY_014/S10/B0|8|1.846e-14|1.879e-14|3.97e-09|0|
|DY_014/S10/B1|336|1.911e-06|4.163e-16|1.117e-08|267|
|DY_014/S10/B2|368|6.037e-06|2.099e-16|1.117e-08|263|
|DY_014/S10/B3|560|4.482e-06|3.608e-16|1.09e-08|46|
|DY_014/S10/B4|592|1.899e-06|3.665e-16|1.115e-08|103|
|DY_014/S11/B0|5|1.846e-14|1.879e-14|3.961e-09|0|
|DY_014/S11/B1|190|1.382e-06|3.888e-16|1.118e-08|255|
|DY_014/S11/B2|210|1.351e-06|2.558e-16|1.116e-08|265|
|DY_014/S11/B3|270|1.249e-06|4.441e-16|1.089e-08|37|
|DY_014/S11/B4|290|3.156e-06|2.285e-16|1.115e-08|104|
|NR_0027/S01/B0|5|7.219e-15|7.033e-15|1.07e-09|0|
|NR_0027/S01/B1|190|9.249e-07|1.075e-16|3.031e-09|129|
|NR_0027/S01/B2|210|8.792e-07|1.134e-16|3.029e-09|126|
|NR_0027/S01/B3|270|6.593e-07|1.735e-16|3.059e-09|36|
|NR_0027/S01/B4|290|6.196e-07|1.232e-16|3.046e-09|54|
|NR_0027/S02/B0|12|7.219e-15|7.033e-15|1.07e-09|0|
|NR_0027/S02/B1|456|7.15e-07|9.498e-17|3.037e-09|124|
|NR_0027/S02/B2|504|6.64e-07|1.119e-16|3.031e-09|131|
|NR_0027/S02/B3|984|9.845e-07|2.22e-16|3.485e-09|63|
|NR_0027/S02/B4|1032|3.659e-06|1.132e-16|3.811e-09|86|
|NR_0027/S04/B0|8|1.004e-14|9.645e-15|2.145e-09|0|
|NR_0027/S04/B1|304|3.063e-06|9.867e-17|6.827e-09|189|
|NR_0027/S04/B2|336|7.197e-07|2.086e-16|6.841e-09|191|
|NR_0027/S04/B3|528|1.134e-06|4.025e-16|6.946e-09|62|
|NR_0027/S04/B4|560|9.696e-07|1.18e-16|6.875e-09|83|
|NR_0027/S05/B0|8|1.316e-14|1.275e-14|1.075e-09|0|
|NR_0027/S05/B1|304|8.879e-07|1.475e-16|3.132e-09|130|
|NR_0027/S05/B2|336|8.726e-07|8.11e-17|3.129e-09|131|
|NR_0027/S05/B3|528|1.116e-06|2.429e-16|3.204e-09|43|
|NR_0027/S05/B4|560|8.286e-07|8.5e-17|3.154e-09|51|
|NR_0027/S06/B0|8|7.219e-15|7.033e-15|1.07e-09|0|
|NR_0027/S06/B1|304|7.069e-07|8.929e-17|3.033e-09|128|
|NR_0027/S06/B2|336|8.927e-07|7.86e-17|3.026e-09|132|
|NR_0027/S06/B3|528|7.8e-07|2.776e-16|3.048e-09|60|
|NR_0027/S06/B4|560|9.4e-07|1.006e-16|3.044e-09|70|
|NR_0027/S07/B0|8|3.843e-15|3.974e-15|2.687e-10|0|
|NR_0027/S07/B1|304|9.154e-07|4.38e-17|9.842e-10|74|
|NR_0027/S07/B2|336|9.108e-07|6.137e-17|1.133e-09|81|
|NR_0027/S07/B3|528|9.312e-07|2.009e-16|7.569e-10|40|
|NR_0027/S07/B4|560|9.703e-07|6.072e-17|9.78e-10|43|
|NR_0027/S08/B0|8|7.219e-15|7.033e-15|1.07e-09|0|
|NR_0027/S08/B1|304|7.069e-07|8.929e-17|3.033e-09|128|
|NR_0027/S08/B2|336|8.927e-07|7.86e-17|3.026e-09|132|
|NR_0027/S08/B3|528|7.8e-07|2.776e-16|3.048e-09|60|
|NR_0027/S08/B4|560|9.4e-07|1.006e-16|3.044e-09|70|
|NR_0027/S09/B0|8|7.219e-15|7.033e-15|1.07e-09|0|
|NR_0027/S09/B1|304|7.069e-07|8.929e-17|3.033e-09|128|
|NR_0027/S09/B2|336|8.927e-07|7.86e-17|3.026e-09|132|
|NR_0027/S09/B3|528|7.8e-07|2.776e-16|3.048e-09|60|
|NR_0027/S09/B4|560|9.4e-07|1.006e-16|3.044e-09|70|
|NR_0027/S10/B0|8|7.219e-15|7.033e-15|1.07e-09|0|
|NR_0027/S10/B1|336|9.249e-07|1.145e-16|3.032e-09|134|
|NR_0027/S10/B2|368|8.79e-07|1.42e-16|3.027e-09|142|
|NR_0027/S10/B3|560|7.64e-07|2.082e-16|3.056e-09|64|
|NR_0027/S10/B4|592|9.641e-07|8.63e-17|3.041e-09|85|
|NR_0027/S11/B0|5|7.219e-15|7.033e-15|1.07e-09|0|
|NR_0027/S11/B1|190|9.249e-07|1.075e-16|3.031e-09|129|
|NR_0027/S11/B2|210|8.792e-07|1.134e-16|3.029e-09|126|
|NR_0027/S11/B3|270|6.593e-07|1.735e-16|3.059e-09|36|
|NR_0027/S11/B4|290|6.196e-07|1.232e-16|3.046e-09|54|
|UCLA037/S01/B0|5|1.218e-14|1.225e-14|5.826e-09|0|
|UCLA037/S01/B1|190|8.397e-06|2.713e-16|1.969e-08|262|
|UCLA037/S01/B2|210|1.362e-06|2.072e-16|1.97e-08|279|
|UCLA037/S01/B3|270|2.826e-06|5.482e-16|2.036e-08|37|
|UCLA037/S01/B4|290|7.966e-06|2.472e-16|1.983e-08|100|
|UCLA037/S02/B0|12|1.218e-14|1.225e-14|5.809e-09|0|
|UCLA037/S02/B1|456|1.084e-05|2.535e-16|1.969e-08|266|
|UCLA037/S02/B2|504|7.909e-06|2.407e-16|1.968e-08|279|
|UCLA037/S02/B3|984|2.748e-06|2.776e-16|2.044e-08|49|
|UCLA037/S02/B4|1032|1.327e-06|2.351e-16|1.984e-08|108|
|UCLA037/S03/B0|20|1.218e-14|1.225e-14|5.809e-09|0|
|UCLA037/S03/B1|760|2.671e-06|3.157e-16|1.974e-08|282|
|UCLA037/S03/B2|840|2.208e-06|2.55e-16|1.968e-08|288|
|UCLA037/S03/B3|2280|2.119e-06|2.776e-16|2.047e-08|60|
|UCLA037/S03/B4|2360|1.709e-06|2.463e-16|1.985e-08|123|
|UCLA037/S04/B0|8|7.899e-15|8.03e-15|1.164e-08|0|
|UCLA037/S04/B1|304|6.1e-06|3.502e-16|3.215e-08|383|
|UCLA037/S04/B2|336|2.532e-06|3.733e-16|3.213e-08|396|
|UCLA037/S04/B3|528|2.753e-06|5.482e-16|3.192e-08|51|
|UCLA037/S04/B4|560|2.896e-06|3.779e-16|3.211e-08|148|
|UCLA037/S05/B0|8|1.616e-14|1.649e-14|5.871e-09|0|
|UCLA037/S05/B1|304|1.007e-05|3.036e-16|1.974e-08|255|
|UCLA037/S05/B2|336|1.636e-06|2.136e-16|1.973e-08|281|
|UCLA037/S05/B3|528|3.116e-06|3.261e-16|2.042e-08|39|
|UCLA037/S05/B4|560|1.481e-06|2.661e-16|1.986e-08|104|
|UCLA037/S06/B0|8|1.218e-14|1.225e-14|4.947e-09|0|
|UCLA037/S06/B1|304|5.634e-06|1.921e-16|1.732e-08|244|
|UCLA037/S06/B2|336|4.879e-06|2.011e-16|1.731e-08|261|
|UCLA037/S06/B3|528|9.282e-06|2.706e-16|1.697e-08|37|
|UCLA037/S06/B4|560|1.611e-06|2.073e-16|1.731e-08|101|
|UCLA037/S07/B0|8|5.31e-16|5.754e-16|4.441e-10|0|
|UCLA037/S07/B1|304|7.968e-07|2.976e-17|1.006e-09|67|
|UCLA037/S07/B2|336|6.819e-07|1.952e-17|1.006e-09|64|
|UCLA037/S07/B3|528|9.237e-07|7.286e-17|8.706e-10|21|
|UCLA037/S07/B4|560|4.443e-07|3.209e-17|9.868e-10|27|
|UCLA037/S08/B0|8|5.259e-15|5.252e-15|5.8e-09|0|
|UCLA037/S08/B1|304|2.222e-06|2.323e-16|1.962e-08|274|
|UCLA037/S08/B2|336|8.455e-06|2.257e-16|1.96e-08|273|
|UCLA037/S08/B3|528|2.53e-06|4.103e-16|2.032e-08|40|
|UCLA037/S08/B4|560|1.585e-06|2.086e-16|1.974e-08|106|
|UCLA037/S09/B0|8|1.18e-14|1.112e-14|5.782e-09|0|
|UCLA037/S09/B1|304|1.639e-06|3.831e-16|1.956e-08|275|
|UCLA037/S09/B2|336|1.778e-06|2.608e-16|1.956e-08|288|
|UCLA037/S09/B3|528|2.48e-06|4.302e-16|2.029e-08|39|
|UCLA037/S09/B4|560|4.441e-06|2.741e-16|1.971e-08|110|
|UCLA037/S10/B0|8|1.218e-14|1.225e-14|5.818e-09|0|
|UCLA037/S10/B1|336|1.978e-06|1.649e-16|1.971e-08|292|
|UCLA037/S10/B2|368|2.413e-06|2.248e-16|1.969e-08|294|
|UCLA037/S10/B3|560|4.046e-06|3.053e-16|2.042e-08|41|
|UCLA037/S10/B4|592|1.577e-06|2.172e-16|1.983e-08|114|
|UCLA037/S11/B0|5|1.218e-14|1.225e-14|5.826e-09|0|
|UCLA037/S11/B1|190|8.397e-06|2.713e-16|1.969e-08|262|
|UCLA037/S11/B2|210|1.362e-06|2.072e-16|1.97e-08|279|
|UCLA037/S11/B3|270|2.826e-06|5.482e-16|2.036e-08|37|
|UCLA037/S11/B4|290|7.966e-06|2.472e-16|1.983e-08|100|
|ZFM-01576/S01/B0|5|2.326e-14|2.371e-14|1.883e-09|0|
|ZFM-01576/S01/B1|190|3.389e-06|1.028e-16|5.156e-09|152|
|ZFM-01576/S01/B2|210|8.536e-07|1.379e-16|5.147e-09|159|
|ZFM-01576/S01/B3|270|1.082e-06|3.053e-16|4.779e-09|32|
|ZFM-01576/S01/B4|290|8.64e-07|1.631e-16|5.098e-09|62|
|ZFM-01576/S02/B0|12|2.326e-14|2.371e-14|1.883e-09|0|
|ZFM-01576/S02/B1|456|9.616e-07|6.592e-17|5.163e-09|166|
|ZFM-01576/S02/B2|504|9.834e-07|1.193e-16|5.161e-09|164|
|ZFM-01576/S02/B3|984|1.755e-06|3.886e-16|4.817e-09|62|
|ZFM-01576/S02/B4|1032|9.005e-07|1.7e-16|5.099e-09|81|
|ZFM-01576/S03/B0|20|2.326e-14|2.371e-14|1.874e-09|0|
|ZFM-01576/S03/B1|760|3.863e-06|1.119e-16|5.156e-09|172|
|ZFM-01576/S03/B2|840|7.711e-07|9.649e-17|5.15e-09|182|
|ZFM-01576/S03/B3|2280|1.849e-06|4.58e-16|4.826e-09|102|
|ZFM-01576/S03/B4|2360|8.506e-07|1.475e-16|5.098e-09|142|
|ZFM-01576/S04/B0|8|1.676e-14|1.647e-14|3.766e-09|0|
|ZFM-01576/S04/B1|304|1.178e-06|9.064e-17|9.927e-09|228|
|ZFM-01576/S04/B2|336|7.178e-06|1.186e-16|9.928e-09|231|
|ZFM-01576/S04/B3|528|3.34e-06|6.523e-16|9.669e-09|43|
|ZFM-01576/S04/B4|560|8.425e-07|1.9e-16|9.912e-09|93|
|ZFM-01576/S05/B0|8|2.595e-14|2.608e-14|1.878e-09|0|
|ZFM-01576/S05/B1|304|1.143e-06|1.606e-16|5.152e-09|176|
|ZFM-01576/S05/B2|336|8.973e-07|1.72e-16|5.153e-09|176|
|ZFM-01576/S05/B3|528|1.716e-06|2.942e-16|4.824e-09|42|
|ZFM-01576/S05/B4|560|8.818e-07|3.747e-16|5.109e-09|68|
|ZFM-01576/S06/B0|8|2.326e-14|2.371e-14|1.878e-09|0|
|ZFM-01576/S06/B1|304|9.506e-07|9.845e-17|5.151e-09|163|
|ZFM-01576/S06/B2|336|1.919e-06|1.082e-16|5.149e-09|168|
|ZFM-01576/S06/B3|528|1.141e-06|3.747e-16|4.809e-09|39|
|ZFM-01576/S06/B4|560|7.655e-07|1.83e-16|5.101e-09|66|
|ZFM-01576/S07/B0|8|4.478e-15|4.456e-15|4.441e-10|0|
|ZFM-01576/S07/B1|304|9.623e-07|5.204e-17|9.561e-10|65|
|ZFM-01576/S07/B2|336|8.764e-07|3.61e-17|9.69e-10|64|
|ZFM-01576/S07/B3|528|6.66e-07|1.457e-16|9.662e-10|20|
|ZFM-01576/S07/B4|560|6.229e-07|7.806e-17|9.232e-10|28|
|ZFM-01576/S08/B0|8|2.326e-14|2.371e-14|1.878e-09|0|
|ZFM-01576/S08/B1|304|9.506e-07|9.845e-17|5.151e-09|163|
|ZFM-01576/S08/B2|336|1.919e-06|1.082e-16|5.149e-09|168|
|ZFM-01576/S08/B3|528|1.141e-06|3.747e-16|4.809e-09|39|
|ZFM-01576/S08/B4|560|7.655e-07|1.83e-16|5.101e-09|66|
|ZFM-01576/S09/B0|8|2.326e-14|2.371e-14|1.878e-09|0|
|ZFM-01576/S09/B1|304|9.506e-07|9.845e-17|5.151e-09|163|
|ZFM-01576/S09/B2|336|1.919e-06|1.082e-16|5.149e-09|168|
|ZFM-01576/S09/B3|528|1.141e-06|3.747e-16|4.809e-09|39|
|ZFM-01576/S09/B4|560|7.655e-07|1.83e-16|5.101e-09|66|
|ZFM-01576/S10/B0|8|2.326e-14|2.371e-14|1.878e-09|0|
|ZFM-01576/S10/B1|336|2.593e-06|7.264e-17|5.154e-09|171|
|ZFM-01576/S10/B2|368|9.985e-07|1.529e-16|5.152e-09|174|
|ZFM-01576/S10/B3|560|2.557e-06|3.608e-16|4.813e-09|42|
|ZFM-01576/S10/B4|592|7.687e-07|1.344e-16|5.102e-09|68|
|ZFM-01576/S11/B0|5|2.326e-14|2.371e-14|1.883e-09|0|
|ZFM-01576/S11/B1|190|3.389e-06|1.028e-16|5.156e-09|152|
|ZFM-01576/S11/B2|210|8.536e-07|1.379e-16|5.147e-09|159|
|ZFM-01576/S11/B3|270|1.082e-06|3.053e-16|4.779e-09|32|
|ZFM-01576/S11/B4|290|8.64e-07|1.631e-16|5.098e-09|62|
|ZFM-01936/S01/B0|5|4.363e-15|4.777e-15|2.554e-09|0|
|ZFM-01936/S01/B1|190|8.909e-07|8.544e-17|6.783e-09|182|
|ZFM-01936/S01/B2|210|9.648e-07|7.644e-17|6.785e-09|177|
|ZFM-01936/S01/B3|270|8.103e-07|3.088e-16|6.621e-09|29|
|ZFM-01936/S01/B4|290|8.901e-07|1.301e-16|6.758e-09|67|
|ZFM-01936/S02/B0|12|6.741e-15|6.529e-15|2.549e-09|0|
|ZFM-01936/S02/B1|456|1.124e-06|1.35e-16|7.301e-09|193|
|ZFM-01936/S02/B2|504|6.123e-06|1.041e-16|7.299e-09|188|
|ZFM-01936/S02/B3|984|3.133e-06|3.712e-16|6.712e-09|43|
|ZFM-01936/S02/B4|1032|9.278e-07|1.509e-16|7.018e-09|73|
|ZFM-01936/S03/B0|20|6.741e-15|6.529e-15|3.553e-09|0|
|ZFM-01936/S03/B1|760|4.294e-06|2.16e-16|7.285e-09|201|
|ZFM-01936/S03/B2|840|1.208e-06|1.182e-16|7.293e-09|203|
|ZFM-01936/S03/B3|2280|1.864e-06|2.776e-16|6.8e-09|67|
|ZFM-01936/S03/B4|2360|1.334e-06|1.284e-16|6.997e-09|96|
|ZFM-01936/S04/B0|8|1.733e-14|1.662e-14|5.107e-09|0|
|ZFM-01936/S04/B1|304|3.902e-06|1.427e-16|1.293e-08|260|
|ZFM-01936/S04/B2|336|4.21e-06|1.563e-16|1.294e-08|267|
|ZFM-01936/S04/B3|528|1.482e-06|2.776e-16|1.279e-08|38|
|ZFM-01936/S04/B4|560|6.785e-06|1.266e-16|1.292e-08|99|
|ZFM-01936/S05/B0|8|6.741e-15|6.529e-15|2.558e-09|0|
|ZFM-01936/S05/B1|304|9.098e-07|8.197e-17|7.282e-09|190|
|ZFM-01936/S05/B2|336|1.655e-06|1.206e-16|7.273e-09|191|
|ZFM-01936/S05/B3|528|1.915e-06|5.551e-16|6.664e-09|34|
|ZFM-01936/S05/B4|560|7.323e-07|1.006e-16|6.992e-09|71|
|ZFM-01936/S06/B0|8|4.363e-15|4.777e-15|2.567e-09|0|
|ZFM-01936/S06/B1|304|1.345e-06|1.002e-16|7.28e-09|192|
|ZFM-01936/S06/B2|336|9.31e-07|9.584e-17|7.284e-09|194|
|ZFM-01936/S06/B3|528|1.599e-06|1.874e-16|6.665e-09|37|
|ZFM-01936/S06/B4|560|7.346e-07|1.37e-16|7e-09|71|
|ZFM-01936/S07/B0|8|5.736e-16|5.934e-16|6.661e-10|0|
|ZFM-01936/S07/B1|304|6.873e-07|2.407e-17|1.378e-09|64|
|ZFM-01936/S07/B2|336|9.446e-07|3.112e-17|1.376e-09|62|
|ZFM-01936/S07/B3|528|4.738e-07|8.327e-17|9.408e-10|24|
|ZFM-01936/S07/B4|560|9.686e-07|3.123e-17|1.243e-09|27|
|ZFM-01936/S08/B0|8|4.363e-15|4.777e-15|2.567e-09|0|
|ZFM-01936/S08/B1|304|1.345e-06|1.002e-16|7.28e-09|192|
|ZFM-01936/S08/B2|336|9.31e-07|9.584e-17|7.284e-09|194|
|ZFM-01936/S08/B3|528|1.599e-06|1.874e-16|6.665e-09|37|
|ZFM-01936/S08/B4|560|7.346e-07|1.37e-16|7e-09|71|
|ZFM-01936/S09/B0|8|9.387e-15|8.776e-15|2.558e-09|0|
|ZFM-01936/S09/B1|304|4.327e-06|1.228e-16|7.269e-09|187|
|ZFM-01936/S09/B2|336|1.139e-06|9.458e-17|7.257e-09|186|
|ZFM-01936/S09/B3|528|3.949e-06|3.261e-16|6.651e-09|35|
|ZFM-01936/S09/B4|560|9.272e-07|1.18e-16|6.969e-09|70|
|ZFM-01936/S10/B0|8|4.363e-15|4.777e-15|2.567e-09|0|
|ZFM-01936/S10/B1|336|1.537e-06|6.939e-17|7.298e-09|200|
|ZFM-01936/S10/B2|368|1.212e-06|1.128e-16|7.284e-09|202|
|ZFM-01936/S10/B3|560|1.068e-06|2.845e-16|6.664e-09|39|
|ZFM-01936/S10/B4|592|3.648e-06|9.714e-17|6.995e-09|73|
|ZFM-01936/S11/B0|5|4.363e-15|4.777e-15|2.554e-09|0|
|ZFM-01936/S11/B1|190|8.909e-07|8.544e-17|6.783e-09|182|
|ZFM-01936/S11/B2|210|9.648e-07|7.644e-17|6.785e-09|177|
|ZFM-01936/S11/B3|270|8.103e-07|3.088e-16|6.621e-09|29|
|ZFM-01936/S11/B4|290|8.901e-07|1.301e-16|6.758e-09|67|

## S9. All contrasts, animal-level effects and uncertainty

Mouse is the independent statistical unit; units/trials/probes are not independent replicates. Gains retain full LL, exposure and actual scored nominal unit-bin denominators. Fixed contrast order is primary B4-B1, own B4-B3, other B4-B2, D-B4, C-B4, D-S. Development and Final are never pooled. The following two tables give original exact saved values; allFinal rows remain DESCRIPTIVE ONLY. Original CSV order is preserved separately in source copies, while this reporting view follows the original hypothesis order.

**Development: exploratory; 10 mice from eight laboratories.**

|Contrast|Mean gain|95% whole-mouse CI|Raw p|Holm5 p|
|---|---|---|---|---|
|B4-B1|0.1125291851306621|[0.06745810552609997, 0.16368155129436163]|0.0009765625|not in family|
|B4-B3|0.03930120524139896|[0.01734158461894405, 0.06278710159999801]|0.01171875|0.05859375|
|B4-B2|0.026306579812766885|[0.0050302065057874785, 0.05501082886164163]|0.044921875|0.1796875|
|D-B4|-0.01477973215700219|[-0.03601613299004298, 0.0021497034444591255]|0.19921875|0.59765625|
|C-B4|0.00010824211289161302|[-0.000400099229921444, 0.000568692298035778]|0.685546875|0.859375|
|D-S|-0.0019684110379102277|[-0.0059149205271999674, 0.00047306207126944814]|0.4296875|0.859375|

**Final: DESCRIPTIVE ONLY; six mice from four laboratories.**

|Contrast|Mean gain|95% whole-mouse CI|Raw p|Holm5 p|
|---|---|---|---|---|
|B4-B1|0.08658239652342035|[0.04944033234175033, 0.14110164811873427]|0.015625|not in family|
|B4-B3|0.05208972400526927|[0.03441612054329819, 0.07346442266178636]|0.03125|0.15625|
|B4-B2|0.006353386392021677|[-0.008903428833930957, 0.022405637931404047]|0.53125|1.0|
|D-B4|0.00235862122254638|[-0.003948272203674794, 0.009196280435455508]|0.53125|1.0|
|C-B4|0.00013410738971923112|[-5.783408566630739e-05, 0.00034291798308512485]|0.28125|1.0|
|D-S|0.0016697806796088692|[-0.00030445108225563776, 0.0051111034674382804]|0.5625|1.0|

Original tests enumerate all2^n sign vectors. Primary uses mean(s*d)>=mean(d); secondary uses absolute means, with the frozen1e-14equality stabilization. No Monte Carlo correction is added to the exhaustive test. Interpretation requires independent sign-exchangeable symmetric zero-centered effects, not an arbitrary unrestricted null mean. There are64signs at n6, so minimum one-/two-sided p=0.015625/0.03125, and smallest Holm5secondary p=0.15625. Missing families retain p1slots. Holm adjustment is the cumulative maximum of ordered (5−rank+1)*p, capped1, with stable original-slot restoration.

The10,000whole-mouse draws use PCG64seed150101, arithmetic means, linear0.025/0.975quantiles. Each contrast reuses its specified fixed index stream. SD has n−1denominator; IQR uses linear quartiles. Original leave-one-mouse/lab, labmeans andequal-lab mean are saved diagnostics. The lab-block bootstrap uses seed150102, draws the original number of labs with replacement, and aggregates included mice's effect sums divided by included mouse counts; it is not an equal-lab primary estimator. Its small lab denominator is disclosed. No new cross-cohort or own-versus-other test is added by this supplement.

|Cohort|Mouse|Contrast|Effect|Scored unit-bins|
|---|---|---|---|---|
|Dev|KS046|B4-B1|0.08052120076|9520|
|Dev|PL033|B4-B1|0.01895552682|9120|
|Dev|SWC_043|B4-B1|0.0297892462|7920|
|Dev|SWC_038|B4-B1|0.06548543728|12800|
|Dev|CSH_ZAD_026|B4-B1|0.2304086549|12960|
|Dev|NYU-30|B4-B1|0.0600708051|10000|
|Dev|KS051|B4-B1|0.264325883|6080|
|Dev|ZFM-01937|B4-B1|0.1345940559|6960|
|Dev|CSH_ZAD_019|B4-B1|0.1551709411|9200|
|Dev|UCLA035|B4-B1|0.08597010028|13760|
|Dev|KS046|B4-B3|0.05819635041|9520|
|Dev|PL033|B4-B3|0.01235773129|9120|
|Dev|SWC_043|B4-B3|0.02035371395|7920|
|Dev|SWC_038|B4-B3|0.03707496984|12800|
|Dev|CSH_ZAD_026|B4-B3|-0.02603455397|12960|
|Dev|NYU-30|B4-B3|0.05204759639|10000|
|Dev|KS051|B4-B3|0.01132994605|6080|
|Dev|ZFM-01937|B4-B3|0.03571423848|6960|
|Dev|CSH_ZAD_019|B4-B3|0.07860768589|9200|
|Dev|UCLA035|B4-B3|0.1133643741|13760|
|Dev|KS046|B4-B2|0.01828854523|9520|
|Dev|PL033|B4-B2|-0.02051362974|9120|
|Dev|SWC_043|B4-B2|0.007251290257|7920|
|Dev|SWC_038|B4-B2|0.01009090225|12800|
|Dev|CSH_ZAD_026|B4-B2|0.1380739421|12960|
|Dev|NYU-30|B4-B2|0.01063712653|10000|
|Dev|KS051|B4-B2|0.04754134899|6080|
|Dev|ZFM-01937|B4-B2|0.04220873531|6960|
|Dev|CSH_ZAD_019|B4-B2|0.01100047266|9200|
|Dev|UCLA035|B4-B2|-0.00151293544|13760|
|Dev|KS046|D-B4|0.004160042777|9520|
|Dev|PL033|D-B4|-0.03870847584|9120|
|Dev|SWC_043|D-B4|-0.009813369484|7920|
|Dev|SWC_038|D-B4|0.002351203746|12800|
|Dev|CSH_ZAD_026|D-B4|0.01855069352|12960|
|Dev|NYU-30|D-B4|-0.0011866799|10000|
|Dev|KS051|D-B4|-0.09508395869|6080|
|Dev|ZFM-01937|D-B4|-0.03552402696|6960|
|Dev|CSH_ZAD_019|D-B4|0.008564880997|9200|
|Dev|UCLA035|D-B4|-0.00110763174|13760|
|Dev|KS046|C-B4|-0.000195086033|9520|
|Dev|PL033|C-B4|0.001048917521|9120|
|Dev|SWC_043|C-B4|-4.082760353e-05|7920|
|Dev|SWC_038|C-B4|-0.0002416324679|12800|
|Dev|CSH_ZAD_026|C-B4|0.0008202170878|12960|
|Dev|NYU-30|C-B4|0.0001353345891|10000|
|Dev|KS051|C-B4|0.0001550140577|6080|
|Dev|ZFM-01937|C-B4|-0.001637741622|6960|
|Dev|CSH_ZAD_019|C-B4|0.001298190818|9200|
|Dev|UCLA035|C-B4|-0.0002599652185|13760|
|Dev|KS046|D-S|0.0002515342479|9520|
|Dev|PL033|D-S|0.0007118957586|9120|
|Dev|SWC_043|D-S|8.254664174e-08|7920|
|Dev|SWC_038|D-S|-0.001757812083|12800|
|Dev|CSH_ZAD_026|D-S|-0.01867244828|12960|
|Dev|NYU-30|D-S|0.0001041095974|10000|
|Dev|KS051|D-S|-0.001937933648|6080|
|Dev|ZFM-01937|D-S|0.002402706443|6960|
|Dev|CSH_ZAD_019|D-S|-0.0005221152163|9200|
|Dev|UCLA035|D-S|-0.0002641297404|13760|
|Fin|UCLA037|B4-B1|0.09113110645|13680|
|Fin|DY_014|B4-B1|0.0747880607|17440|
|Fin|ZFM-01576|B4-B1|0.215114199|32160|
|Fin|NR_0027|B4-B1|0.03500649848|15280|
|Fin|DY_011|B4-B1|0.05506809263|12320|
|Fin|ZFM-01936|B4-B1|0.04838642187|17920|
|Fin|UCLA037|B4-B3|0.04017741117|13680|
|Fin|DY_014|B4-B3|0.06586010317|17440|
|Fin|ZFM-01576|B4-B3|0.04838456595|32160|
|Fin|NR_0027|B4-B3|0.02591083568|15280|
|Fin|DY_011|B4-B3|0.1002103437|12320|
|Fin|ZFM-01936|B4-B3|0.03199508434|17920|
|Fin|UCLA037|B4-B2|0.009146492357|13680|
|Fin|DY_014|B4-B2|0.002673076108|17440|
|Fin|ZFM-01576|B4-B2|0.0390199347|32160|
|Fin|NR_0027|B4-B2|0.008926726412|15280|
|Fin|DY_011|B4-B2|-0.02472228929|12320|
|Fin|ZFM-01936|B4-B2|0.003076378064|17920|
|Fin|UCLA037|D-B4|0.008419415286|13680|
|Fin|DY_014|D-B4|0.01398749592|17440|
|Fin|ZFM-01576|D-B4|0.01000539177|32160|
|Fin|NR_0027|D-B4|-0.005457865318|15280|
|Fin|DY_011|D-B4|-0.007593098119|12320|
|Fin|ZFM-01936|D-B4|-0.005209612205|17920|
|Fin|UCLA037|C-B4|9.305915588e-05|13680|
|Fin|DY_014|C-B4|8.682844193e-05|17440|
|Fin|ZFM-01576|C-B4|0.0005426344254|32160|
|Fin|NR_0027|C-B4|-0.0002606538652|15280|
|Fin|DY_011|C-B4|0.0003156948268|12320|
|Fin|ZFM-01936|C-B4|2.708135353e-05|17920|
|Fin|UCLA037|D-S|0.01005989983|13680|
|Fin|DY_014|D-S|-0.0005442196321|17440|
|Fin|ZFM-01576|D-S|0.001031289859|32160|
|Fin|NR_0027|D-S|-0.0001591523655|15280|
|Fin|DY_011|D-S|-0.0003689846995|12320|
|Fin|ZFM-01936|D-S|-1.489151692e-07|17920|

## S10. All eleven baseline-only sensitivity panels

Only B0-B4 were sensitivity-refitted. D/C/S have primary-configuration-only evidence. All source/QC/ranking transforms were A/C-defined before later scoring. S01/S04-S11 are nine mandatory cases; S02/S03 are capacity-conditional panels, retained even when unavailable. The frozen rules are:

|Case|Frozen intervention|Interpretation and coverage|
|---|---|---|
|S01|First5 qualified ranked units|Mandatory minimum6pairedFinal mice|
|S02|First12 of same ranking|Capacity-conditional minimum6|
|S03|First20 of same ranking|Final4mice; aggregateunavailable|
|S04|100-ms bins; physical historywindows;5score bins|Different nats/bin scale; not directly comparable as an equal rate|
|S05|History edges0,0.05,0.1,0.2,0.25s;0.25s neural warm-up|Narrower history estimand; behavior supportunchanged|
|S06|Rate1-50Hz; ISI<=0.0025;>=100spikes; quartile>=0.2Hz|First8 under original training-only ranking|
|S07|p=min(1,2/r) per spike from unthinnedA/C rate|Independent role-local stream; expected2Hzcap, not exact matching|
|S08|Known saturation endpoints dilated±10ms|No unknown-artifact certification|
|S09|Known saturation endpoints dilated±50ms|No source-missing interval invented|
|S10|Trial/session cubic+quartic drift terms|41 nuisance columns; not added behavioral sensors|
|S11|First5qualified units with target±2nativecontact indicesallMOp|Anatomical boundaryproxy; not histologicaldistance|

S07 uses the first eight bytes, big-endian, of SHA256 of UTF8 `P15-M1|150108|S07|subject|unit_uuid|role`, using PCG64. One uniform is consumed per source spike in original native within-role row order, including spikes outside retained epochs; duplicate timestamps retain source order. Retain iff uniform<p. A, B, E, C and D streams are independent and processed only when authorized. There is one realization, with no favorable redraw. Score data do not change eligibility, rank or retention probability. Achieved A/C rate evidence remains in original case states; D rates were not used for matching.

Development has 33 contrast-by-case summaries. Final has 33 summaries and 66 mouse-case states: 64 available and two capacity-unavailable. Final S02 has six mice; S03 has four. All nine mandatory Final cases have six paired mice and positive primary/own/other mean gains, without repairing the failed cohort, assumption or precision conditions. The two full tables below retain coverage, status, mean and interval, including unavailable entries.

|Case|Contrast|Mice|Mean|95% whole-mouse CI|Status|
|---|---|---|---|---|---|
|S01|B4-B1|10|0.12195633|[0.067087561,0.18925188]|DESCRIPTIVE_SENSITIVITY|
|S01|B4-B3|10|0.055910131|[0.016218275,0.096893846]|DESCRIPTIVE_SENSITIVITY|
|S01|B4-B2|10|0.024848328|[-0.0026289962,0.059608829]|DESCRIPTIVE_SENSITIVITY|
|S02|B4-B1|9|0.11871086|[0.06663047,0.17904306]|DESCRIPTIVE_SENSITIVITY|
|S02|B4-B3|9|0.037484085|[0.02667183,0.050808617]|DESCRIPTIVE_SENSITIVITY|
|S02|B4-B2|9|0.027270244|[0.00659337,0.057527593]|DESCRIPTIVE_SENSITIVITY|
|S03|B4-B1|6|0.13378186|[0.077903632,0.1986272]|DESCRIPTIVE_SENSITIVITY|
|S03|B4-B3|6|0.03422748|[0.020131188,0.052595157]|DESCRIPTIVE_SENSITIVITY|
|S03|B4-B2|6|0.038781023|[0.012669258,0.085918538]|DESCRIPTIVE_SENSITIVITY|
|S04|B4-B1|10|0.23351777|[0.12665491,0.35957399]|DESCRIPTIVE_SENSITIVITY|
|S04|B4-B3|10|0.04918818|[0.0032783582,0.096177838]|DESCRIPTIVE_SENSITIVITY|
|S04|B4-B2|10|0.057045412|[0.01142023,0.11414502]|DESCRIPTIVE_SENSITIVITY|
|S05|B4-B1|10|0.098553662|[0.062695405,0.13913796]|DESCRIPTIVE_SENSITIVITY|
|S05|B4-B3|10|0.035406593|[0.021129919,0.04922488]|DESCRIPTIVE_SENSITIVITY|
|S05|B4-B2|10|0.026534894|[0.0099243809,0.048079332]|DESCRIPTIVE_SENSITIVITY|
|S06|B4-B1|10|0.11258296|[0.067513227,0.16372615]|DESCRIPTIVE_SENSITIVITY|
|S06|B4-B3|10|0.039130592|[0.017141294,0.0626932]|DESCRIPTIVE_SENSITIVITY|
|S06|B4-B2|10|0.026367954|[0.0050640205,0.055061618]|DESCRIPTIVE_SENSITIVITY|
|S07|B4-B1|10|0.025252439|[0.01258791,0.040195612]|DESCRIPTIVE_SENSITIVITY|
|S07|B4-B3|10|0.010126573|[0.0023467699,0.017613963]|DESCRIPTIVE_SENSITIVITY|
|S07|B4-B2|10|0.0089023893|[0.0022852183,0.016294652]|DESCRIPTIVE_SENSITIVITY|
|S08|B4-B1|10|0.11251173|[0.06718657,0.16381417]|DESCRIPTIVE_SENSITIVITY|
|S08|B4-B3|10|0.039291897|[0.017355773,0.062769816]|DESCRIPTIVE_SENSITIVITY|
|S08|B4-B2|10|0.026221412|[0.0049920568,0.054839626]|DESCRIPTIVE_SENSITIVITY|
|S09|B4-B1|10|0.11301509|[0.06718638,0.16462682]|DESCRIPTIVE_SENSITIVITY|
|S09|B4-B3|10|0.039287748|[0.017363144,0.062733514]|DESCRIPTIVE_SENSITIVITY|
|S09|B4-B2|10|0.026798957|[0.0049954436,0.056555106]|DESCRIPTIVE_SENSITIVITY|
|S10|B4-B1|10|0.11066839|[0.061743828,0.16774678]|DESCRIPTIVE_SENSITIVITY|
|S10|B4-B3|10|0.037996857|[0.019582701,0.057262161]|DESCRIPTIVE_SENSITIVITY|
|S10|B4-B2|10|0.028352243|[0.0044851042,0.058368412]|DESCRIPTIVE_SENSITIVITY|
|S11|B4-B1|10|0.12195633|[0.067087561,0.18925188]|DESCRIPTIVE_SENSITIVITY|
|S11|B4-B3|10|0.055910131|[0.016218275,0.096893846]|DESCRIPTIVE_SENSITIVITY|
|S11|B4-B2|10|0.024848328|[-0.0026289962,0.059608829]|DESCRIPTIVE_SENSITIVITY|

|Case|Contrast|Mice|Mean|95% whole-mouse CI|Status|
|---|---|---|---|---|---|
|S01|B4-B1|6|0.093219623|[0.059477353,0.13380611]|DESCRIPTIVE_SENSITIVITY|
|S01|B4-B3|6|0.076281462|[0.044802215,0.11470378]|DESCRIPTIVE_SENSITIVITY|
|S01|B4-B2|6|0.0045942683|[-0.0015574551,0.01186073]|DESCRIPTIVE_SENSITIVITY|
|S02|B4-B1|6|0.06849713|[0.041465025,0.10483097]|DESCRIPTIVE_SENSITIVITY|
|S02|B4-B3|6|0.041036095|[0.028188494,0.055409972]|DESCRIPTIVE_SENSITIVITY|
|S02|B4-B2|6|0.0040374913|[-0.011634553,0.015923449]|DESCRIPTIVE_SENSITIVITY|
|S03|B4-B1|4|0.078832882|[0.060301449,0.097364315]|UNAVAILABLE_MINIMUM_PAIRED_MICE|
|S03|B4-B3|4|0.033746473|[0.026167564,0.041325382]|UNAVAILABLE_MINIMUM_PAIRED_MICE|
|S03|B4-B2|4|0.0063502718|[0.00073700623,0.011963537]|UNAVAILABLE_MINIMUM_PAIRED_MICE|
|S04|B4-B1|6|0.16734705|[0.090073244,0.29239782]|DESCRIPTIVE_SENSITIVITY|
|S04|B4-B3|6|0.083931258|[0.053808511,0.12364046]|DESCRIPTIVE_SENSITIVITY|
|S04|B4-B2|6|0.0098894161|[-0.011455824,0.036671838]|DESCRIPTIVE_SENSITIVITY|
|S05|B4-B1|6|0.11767008|[0.046498266,0.23460058]|DESCRIPTIVE_SENSITIVITY|
|S05|B4-B3|6|0.036887241|[0.0043585151,0.066972102]|DESCRIPTIVE_SENSITIVITY|
|S05|B4-B2|6|0.03219263|[-0.010758796,0.10040166]|DESCRIPTIVE_SENSITIVITY|
|S06|B4-B1|6|0.085112878|[0.049440332,0.14055086]|DESCRIPTIVE_SENSITIVITY|
|S06|B4-B3|6|0.053427779|[0.035430162,0.074397594]|DESCRIPTIVE_SENSITIVITY|
|S06|B4-B2|6|0.0062747119|[-0.0089821034,0.022405638]|DESCRIPTIVE_SENSITIVITY|
|S07|B4-B1|6|0.013317139|[0.0027729692,0.027086531]|DESCRIPTIVE_SENSITIVITY|
|S07|B4-B3|6|0.0078230962|[-0.002891691,0.020533788]|DESCRIPTIVE_SENSITIVITY|
|S07|B4-B2|6|0.0039684782|[-0.0014030408,0.010879155]|DESCRIPTIVE_SENSITIVITY|
|S08|B4-B1|6|0.086537756|[0.049478607,0.14103787]|DESCRIPTIVE_SENSITIVITY|
|S08|B4-B3|6|0.052026846|[0.034383137,0.073453428]|DESCRIPTIVE_SENSITIVITY|
|S08|B4-B2|6|0.006254927|[-0.0090018882,0.022405638]|DESCRIPTIVE_SENSITIVITY|
|S09|B4-B1|6|0.08701024|[0.050024445,0.14144132]|DESCRIPTIVE_SENSITIVITY|
|S09|B4-B3|6|0.051676631|[0.034020273,0.073359882]|DESCRIPTIVE_SENSITIVITY|
|S09|B4-B2|6|0.0066430713|[-0.008623008,0.022414902]|DESCRIPTIVE_SENSITIVITY|
|S10|B4-B1|6|0.085416426|[0.049748955,0.13890595]|DESCRIPTIVE_SENSITIVITY|
|S10|B4-B3|6|0.048770873|[0.032664198,0.066353752]|DESCRIPTIVE_SENSITIVITY|
|S10|B4-B2|6|0.006568526|[-0.0070979301,0.021792904]|DESCRIPTIVE_SENSITIVITY|
|S11|B4-B1|6|0.093219623|[0.059477353,0.13380611]|DESCRIPTIVE_SENSITIVITY|
|S11|B4-B3|6|0.076281462|[0.044802215,0.11470378]|DESCRIPTIVE_SENSITIVITY|
|S11|B4-B2|6|0.0045942683|[-0.0015574551,0.01186073]|DESCRIPTIVE_SENSITIVITY|

## S11. Four 999-replicate finite-reference suites and coverage

Each available suite uses 999 frozen reference realizations per mouse and score role, with no null model refitting or recursive count generation. Targets, unit identities, trial assignments, task covariates, valid masks and fitted states remain fixed. A reference alters specified history or wheel inputs. All contrasts reuse the same realization in a bundle.

N1 rotates each 20-bin multivariate warm-up-plus-score sequence by a nonzero offset from 1 to 19, with all units together. Epoch/unit totals are preserved while neural/task alignment changes. History and C features are recomputed; D updates its filter from surrogate past counts while predicting original targets. N2 cyclically shifts history donors within stimulus-side, contrast, order-half and wheel strata, without self-donors. N3 substitutes wheel columns 24-37, omits wheel from the strata, and reports B4 likelihood reliance plus descriptive B4-B1 changes. It is not a separate D/C wheel null. N4 shifts complete five-trial history blocks, preserving within-block order and population synchrony.

N2-N4 require at least 60% eligible-epoch coverage and 30 control epochs per mouse; N4 needs at least two complete blocks. Singleton strata and incomplete blocks are excluded from both original and control exposures, not from primary scoring. No post-score coarsening is allowed. N2's wheel threshold is the ordinary A/C median of absolute strictly past 0.5-s pre-epoch displacement, with ties assigned lower. Side, contrast threshold 0.25 and original role half are metadata-defined. Continuous nuisance imbalance can remain; N4 is not an exact drift-independent counterfactual.

The RNG is PCG64. Its seed is the first eight bytes, big-endian, of SHA256 of UTF8 `P15-M1|150107|suite|subject|partition|replicate`. N1 draws in original trial order; N2/N3 visit lexicographically ordered strata and sorted original trial ordinals; N4 visits complete blocks in original block order. No offset is drawn for a skipped singleton or incomplete panel. No wall-clock or Python-hash seed, replacement seed or repetition is permitted.

For an available suite, p_ref=(1+number of reference means at least the observed mean)/1000 on the same complete control-mouse cohort and exposures. Holm4 retains all four slots separately for each contrast; an unavailable suite has p=1. These are finite destructive references, not exact population, conditional or causal null p-values. Descriptive gates jointly require at least six paired mice, at least ceil(0.75n) above their own reference median, and positive equal-mouse mean degradation. A small reference p does not clear a failed component. N3's repeated B4-likelihood diagnostic is explicitly labelled and is not an additional independent test for each model.

Final N1/N2/N3 each covered six mice. N4 covered only ZFM-01576, DY_011 and ZFM-01936, so its aggregate was unavailable. The Final batch contained 21*999=20,979 available bundles and 24 suite journals, including three unavailable mouse-suite panels. Development N4 covered only five mice: KS046, SWC_043, SWC_038, KS051 and ZFM-01937. The following 48 rows retain six contrasts times four suites in both cohorts. Exact original p-values and statuses remain in the copied CSVs; the coverage table lists each mouse's original availability and coverage.

|Cohort|Contrast|Suite|Mice|Above median|Descriptive gate|p_ref|Holm4|
|---|---|---|---|---|---|---|---|
|Dev|B4-B1|N1|10|7|False|0.001|0.004|
|Dev|B4-B1|N2|10|10|True|0.001|0.004|
|Dev|B4-B1|N3|10|10|wheel LL diagnostic|0.001|0.004|
|Dev|B4-B1|N4|5|unavailable|unavailable|1.0|1.0|
|Dev|B4-B3|N1|10|7|False|0.001|0.004|
|Dev|B4-B3|N2|10|10|True|0.001|0.004|
|Dev|B4-B3|N3|10|10|wheel LL diagnostic|0.001|0.004|
|Dev|B4-B3|N4|5|unavailable|unavailable|1.0|1.0|
|Dev|B4-B2|N1|10|9|True|0.001|0.004|
|Dev|B4-B2|N2|10|9|True|0.001|0.004|
|Dev|B4-B2|N3|10|10|wheel LL diagnostic|0.001|0.004|
|Dev|B4-B2|N4|5|unavailable|unavailable|1.0|1.0|
|Dev|D-B4|N1|10|3|False|0.901|1.0|
|Dev|D-B4|N2|10|7|False|0.001|0.004|
|Dev|D-B4|N3|10|10|wheel LL diagnostic|0.001|0.004|
|Dev|D-B4|N4|5|unavailable|unavailable|1.0|1.0|
|Dev|C-B4|N1|10|7|False|0.001|0.004|
|Dev|C-B4|N2|10|10|True|0.001|0.004|
|Dev|C-B4|N3|10|10|wheel LL diagnostic|0.001|0.004|
|Dev|C-B4|N4|5|unavailable|unavailable|1.0|1.0|
|Dev|D-S|N1|10|7|False|0.001|0.004|
|Dev|D-S|N2|10|5|False|0.059|0.118|
|Dev|D-S|N3|10|10|wheel LL diagnostic|0.001|0.004|
|Dev|D-S|N4|5|unavailable|unavailable|1.0|1.0|
|Fin|B4-B1|N1|6|6|True|0.001|0.004|
|Fin|B4-B1|N2|6|6|True|0.001|0.004|
|Fin|B4-B1|N3|6|6|wheel LL diagnostic|0.001|0.004|
|Fin|B4-B1|N4|3|unavailable|unavailable|1.0|1.0|
|Fin|B4-B3|N1|6|6|True|0.001|0.004|
|Fin|B4-B3|N2|6|6|True|0.001|0.004|
|Fin|B4-B3|N3|6|6|wheel LL diagnostic|0.001|0.004|
|Fin|B4-B3|N4|3|unavailable|unavailable|1.0|1.0|
|Fin|B4-B2|N1|6|5|True|0.001|0.004|
|Fin|B4-B2|N2|6|5|True|0.001|0.004|
|Fin|B4-B2|N3|6|6|wheel LL diagnostic|0.001|0.004|
|Fin|B4-B2|N4|3|unavailable|unavailable|1.0|1.0|
|Fin|D-B4|N1|6|5|True|0.001|0.004|
|Fin|D-B4|N2|6|4|False|0.871|1.0|
|Fin|D-B4|N3|6|6|wheel LL diagnostic|0.001|0.004|
|Fin|D-B4|N4|3|unavailable|unavailable|1.0|1.0|
|Fin|C-B4|N1|6|5|True|0.001|0.004|
|Fin|C-B4|N2|6|5|True|0.001|0.004|
|Fin|C-B4|N3|6|6|wheel LL diagnostic|0.001|0.004|
|Fin|C-B4|N4|3|unavailable|unavailable|1.0|1.0|
|Fin|D-S|N1|6|4|False|0.001|0.004|
|Fin|D-S|N2|6|2|False|0.622|1.0|
|Fin|D-S|N3|6|6|wheel LL diagnostic|0.001|0.004|
|Fin|D-S|N4|3|unavailable|unavailable|1.0|1.0|

|Cohort|Mouse|Suite|Eligible / total epochs|Available|
|---|---|---|---|---|
|Dev|CSH_ZAD_019|N1|115 / 115|True|
|Dev|CSH_ZAD_019|N2|112 / 115|True|
|Dev|CSH_ZAD_019|N3|115 / 115|True|
|Dev|CSH_ZAD_019|N4|65 / 115|False|
|Dev|CSH_ZAD_026|N1|162 / 162|True|
|Dev|CSH_ZAD_026|N2|160 / 162|True|
|Dev|CSH_ZAD_026|N3|162 / 162|True|
|Dev|CSH_ZAD_026|N4|50 / 162|False|
|Dev|KS046|N1|119 / 119|True|
|Dev|KS046|N2|119 / 119|True|
|Dev|KS046|N3|119 / 119|True|
|Dev|KS046|N4|75 / 119|True|
|Dev|KS051|N1|76 / 76|True|
|Dev|KS051|N2|74 / 76|True|
|Dev|KS051|N3|75 / 76|True|
|Dev|KS051|N4|65 / 76|True|
|Dev|NYU-30|N1|125 / 125|True|
|Dev|NYU-30|N2|123 / 125|True|
|Dev|NYU-30|N3|125 / 125|True|
|Dev|NYU-30|N4|50 / 125|False|
|Dev|PL033|N1|114 / 114|True|
|Dev|PL033|N2|111 / 114|True|
|Dev|PL033|N3|114 / 114|True|
|Dev|PL033|N4|65 / 114|False|
|Dev|SWC_038|N1|160 / 160|True|
|Dev|SWC_038|N2|159 / 160|True|
|Dev|SWC_038|N3|160 / 160|True|
|Dev|SWC_038|N4|115 / 160|True|
|Dev|SWC_043|N1|99 / 99|True|
|Dev|SWC_043|N2|98 / 99|True|
|Dev|SWC_043|N3|99 / 99|True|
|Dev|SWC_043|N4|70 / 99|True|
|Dev|UCLA035|N1|172 / 172|True|
|Dev|UCLA035|N2|171 / 172|True|
|Dev|UCLA035|N3|172 / 172|True|
|Dev|UCLA035|N4|90 / 172|False|
|Dev|ZFM-01937|N1|87 / 87|True|
|Dev|ZFM-01937|N2|83 / 87|True|
|Dev|ZFM-01937|N3|86 / 87|True|
|Dev|ZFM-01937|N4|80 / 87|True|
|Fin|DY_011|N1|154 / 154|True|
|Fin|DY_011|N2|151 / 154|True|
|Fin|DY_011|N3|154 / 154|True|
|Fin|DY_011|N4|100 / 154|True|
|Fin|DY_014|N1|218 / 218|True|
|Fin|DY_014|N2|218 / 218|True|
|Fin|DY_014|N3|218 / 218|True|
|Fin|DY_014|N4|105 / 218|False|
|Fin|NR_0027|N1|191 / 191|True|
|Fin|NR_0027|N2|189 / 191|True|
|Fin|NR_0027|N3|191 / 191|True|
|Fin|NR_0027|N4|30 / 191|False|
|Fin|UCLA037|N1|171 / 171|True|
|Fin|UCLA037|N2|168 / 171|True|
|Fin|UCLA037|N3|171 / 171|True|
|Fin|UCLA037|N4|60 / 171|False|
|Fin|ZFM-01576|N1|402 / 402|True|
|Fin|ZFM-01576|N2|402 / 402|True|
|Fin|ZFM-01576|N3|402 / 402|True|
|Fin|ZFM-01576|N4|395 / 402|True|
|Fin|ZFM-01936|N1|224 / 224|True|
|Fin|ZFM-01936|N2|224 / 224|True|
|Fin|ZFM-01936|N3|224 / 224|True|
|Fin|ZFM-01936|N4|215 / 224|True|

## S12. Failed conditions and exact scientific verdicts

The primary positive-claim conjunction required at least eight Final mice and four labs, no lab over 50%, defensible independence/sign symmetry, valid source/numerical gates, mean at least 0.001, positive CI lower bound, width at most 0.01, one-sided p at most 0.05, at least 75% positive mice, positive leave-one-mouse/lab-out means, all nine mandatory sensitivities with six mice and positive means, and N1/N2 descriptive gates. Final failed its cohort, width and confirmation-assumption requirements despite positive effects and passing primary N1/N2 descriptive conditions. Its mandatory label remains DESCRIPTIVE ONLY.

Secondary conditions add Holm5 two-sided p at most 0.05 and the same cohort, precision and stability requirements. Own/other history require their nine baseline sensitivities and N1/N2; D-B4 and D-S add N4; C-B4 requires N1/N2 without borrowing baseline sensitivity credit; D-S also requires its paired S state. Persistent-state wording would require both D-B4 and D-S conjunctions and the IID identity/N4 conditions. None was met. All five Holm5 tests were nonsignificant. No equivalence, absence of biology, model winner or biological-state claim follows.

Development primary N1 had 7/10, below the required eight, and CI width 0.0962234458 exceeded 0.01; N2 had 10/10. Final primary N1/N2 at 6/6 do not erase that failure. Final D-B4 N2 had 4/6 above median and negative mean degradation. Final D-S N1 had 4/6, below five; N2 had 2/6 and negative degradation. N4 aggregate was unavailable in both cohorts, not negative or passed. These failures also appear in the abstract, Results, Discussion and Limitations.

## S13. Animal/laboratory heterogeneity and anatomy

All 16 admitted mice's effects are listed above. The following table gives all six contrasts in each cohort, with minimum, maximum, median, SD, positive count, equal-lab mean and lab-block CI. The companion CSV/JSON retains original leave-out vectors and lab means with their original order. These are previously registered saved diagnostics, not new hypothesis tests. Main Figure 7 describes native anatomy and Final lab means without an added association p-value.

|Cohort|Contrast|Min / max|Median|SD|Positive|Equal-lab mean|Lab-block CI95|
|---|---|---|---|---|---|---|---|
|Dev|B4-B1|0.0189555 / 0.264326|0.0832457|0.0826907|10|0.0950098|[0.0545127,0.154958]|
|Dev|B4-B3|-0.0260346 / 0.113364|0.0363946|0.0390211|9|0.0414953|[0.0259242,0.0605343]|
|Dev|B4-B2|-0.0205136 / 0.138074|0.0108188|0.0438836|8|0.0194517|[0.00238277,0.0476615]|
|Dev|D-B4|-0.095084 / 0.0185507|-0.00114716|0.0335925|4|-0.0144866|[-0.0321446,0.00200076]|
|Dev|C-B4|-0.00163774 / 0.00129819|4.72535e-05|0.000832089|5|5.40665e-06|[-0.000486935,0.000612221]|
|Dev|D-S|-0.0186724 / 0.00240271|-0.000132024|0.00599496|5|-0.00115545|[-0.005144,0.000595433]|
|Fin|B4-B1|0.0350065 / 0.215114|0.0649281|0.0660188|6|0.080704|[0.0490377,0.118211]|
|Fin|B4-B3|0.0259108 / 0.10021|0.044281|0.027386|6|0.0473283|[0.0316224,0.0748746]|
|Fin|B4-B2|-0.0247223 / 0.0390199|0.00600155|0.0203544|5|0.00702419|[-0.00814302,0.0193165]|
|Fin|D-B4|-0.0075931 / 0.0139875|0.0016049|0.00946414|3|0.00213916|[-0.00199584,0.00601081]|
|Fin|C-B4|-0.000260654 / 0.000542634|8.99438e-05|0.000272426|5|7.96312e-05|[-8.37974e-05,0.000257458]|
|Fin|D-S|-0.00054422 / 0.0100599|-7.96506e-05|0.00414714|2|0.00248993|[-0.000357452,0.00624217]|

|Cohort|Mouse|Population|Units|Superficial|Middle|Deep|Root/unknown|
|---|---|---|---|---|---|---|---|
|Dev|KS046|PRIMARY8|8|0|0|8|0|
|Dev|KS046|S11_BOUNDARY5|5|0|0|5|0|
|Dev|PL033|PRIMARY8|8|0|0|8|0|
|Dev|PL033|S11_BOUNDARY5|5|0|0|5|0|
|Dev|SWC_043|PRIMARY8|8|0|0|8|0|
|Dev|SWC_043|S11_BOUNDARY5|5|0|0|5|0|
|Dev|SWC_038|PRIMARY8|8|0|0|8|0|
|Dev|SWC_038|S11_BOUNDARY5|5|0|0|5|0|
|Dev|CSH_ZAD_026|PRIMARY8|8|0|0|8|0|
|Dev|CSH_ZAD_026|S11_BOUNDARY5|5|0|0|5|0|
|Dev|NYU-30|PRIMARY8|8|0|0|8|0|
|Dev|NYU-30|S11_BOUNDARY5|5|0|0|5|0|
|Dev|KS051|PRIMARY8|8|4|0|4|0|
|Dev|KS051|S11_BOUNDARY5|5|3|0|2|0|
|Dev|ZFM-01937|PRIMARY8|8|3|0|5|0|
|Dev|ZFM-01937|S11_BOUNDARY5|5|3|0|2|0|
|Dev|CSH_ZAD_019|PRIMARY8|8|0|0|8|0|
|Dev|CSH_ZAD_019|S11_BOUNDARY5|5|0|0|5|0|
|Dev|UCLA035|PRIMARY8|8|5|0|3|0|
|Dev|UCLA035|S11_BOUNDARY5|5|3|0|2|0|
|Fin|UCLA037|PRIMARY8|8|2|0|6|0|
|Fin|UCLA037|S11_BOUNDARY5|5|1|0|4|0|
|Fin|DY_014|PRIMARY8|8|0|0|8|0|
|Fin|DY_014|S11_BOUNDARY5|5|0|0|5|0|
|Fin|ZFM-01576|PRIMARY8|8|1|0|7|0|
|Fin|ZFM-01576|S11_BOUNDARY5|5|1|0|4|0|
|Fin|NR_0027|PRIMARY8|8|0|0|8|0|
|Fin|NR_0027|S11_BOUNDARY5|5|0|0|5|0|
|Fin|DY_011|PRIMARY8|8|0|0|8|0|
|Fin|DY_011|S11_BOUNDARY5|5|0|0|5|0|
|Fin|ZFM-01936|PRIMARY8|8|1|0|7|0|
|Fin|ZFM-01936|S11_BOUNDARY5|5|0|0|5|0|

## S14. Access, leakage controls and one-shot integrity

Model policies, unit ranking, QC, scalers and sensitivity configurations used A/C only. Upstream whole-session provider labels are disclosed. M0/M1 statements about unaccessed Final data describe those historical stages; the later authorized M6 D assessment is now complete. Those old scope statements are not presented as current unexposed status.

Final C's trusted local reader had explicit authorization for underlying whole-record ALF decoding solely to classify/export C. It did not use D neural counts, finite/range summaries, scales, QC, selection or thinning streams for calibration. This is ordinary local access discipline, not third-party custody or protection against malicious administrators. Complete C states were sealed, and independent reviews bound the 546-input candidate before the one-shot gate.

The C seal SHA256 was `4a6fb543eaed33fb7ef58c01677eab520128de5f2b001a682c481d323b3e4c67`; pre-D candidate SHA256 was `d59df6d55cb904267ee4ed08e6dcfae187529cd6a170d6553f048860c0b743e2`; pre-D gate SHA256 was `1c66ae3519130b6cb94f890ddc485a0ab1a03f5ec9c9611af7d83fe79590cd82`. The completed D claim SHA256 was `95108b1b992ae69185f083826dc67b0a79765afec3ee195449afd49017a8b726`. Each is checked against the immutable archive, not generated from an assumed result.

The execution receipt and consumed claim record the complete six-mouse batch. Registered references belong to that one assessment, not alternative Final draws. Manuscript production cannot refit C/D models, select policies after D or repeat D. The original processing workflow is documented for audit; the paper's reproduction command cannot invoke it.

## S15. Source-to-claim and A1-A10 coverage

`A1_A10_CLAIM_AUDIT.md` maps the frozen question, source/licence/cohort, recording/physiology, models, role isolation, effects/statistics, controls/sensitivities, one-shot integrity, negative findings and reproduction to saved artifacts and Main Figures 1-7/Supplement sections. `AUTHOR_SCIENTIFIC_REVIEW.md` checks all ten author questions A-J. These are internal consistency reviews, not external peer review. Authorship, funding, ethics and conflicts still require human author verification before external submission.

No causal connectivity, motor-command mechanism, all-movement independence, persistent biological states, discrete neural atoms, CWP/NAP, human/BCI validation or independent-laboratory replication is supported. A positive mean and small conditional p do not replace the failed registered conjunction.

## S16. Reproduction, environment and source archive

Run from repository root: `powershell -NoProfile -ExecutionPolicy Bypass -File paper15_manuscript/reproduce.ps1`. On another Windows machine, install the exact document dependencies in `requirements.txt` and pass `-Python` with that interpreter. Poppler tools must be available for page rendering. `REPRODUCIBILITY.md` separates saved-result reproduction from independent raw-data fit reproduction.

The command verifies source hashes, denies network and NumPy array loading, blocks old scientific-package imports, checks original mouse-level means/sign flips/bootstrap/Holm arithmetic, recopies unchanged tables, renders seven figures and rebuilds both PDFs. It checks PDF text, page numbers, glyphs and private paths. It does not query neural datasets, fit a model, compute likelihoods or call a prediction worker. No new hypothesis or statistical family is introduced. Original processing and access documentation are an audit trail, not permission to reuse the consumed D assessment.

The scientific base is `bdec0e19621cc8018abe11c5633ce76aff611443`. All five scientific packages and source/review dependencies retain original hashes. Manuscript commits contain only the new package and its mission evidence/current daily prefix. Live current commit/remote/clean proof is external to its own tracked bytes, avoiding a recursive commit claim. Original failures remain immutable.

## References

[1] International Brain Laboratory et al. (2025). A brain-wide map of neural activity during complex behaviour. Nature 645:177-191. https://doi.org/10.1038/s41586-025-09235-0

[2] International Brain Laboratory et al. (2021). Standardized and reproducible measurement of decision-making in mice. eLife 10:e63711. https://doi.org/10.7554/eLife.63711

[3] Truccolo W, Eden UT, Fellows MR, Donoghue JP, Brown EN (2005). A point process framework for relating neural spiking activity to spiking history, neural ensemble, and extrinsic covariate effects. Journal of Neurophysiology 93:1074-1089. https://doi.org/10.1152/jn.00697.2004

[4] Pillow JW, Shlens J, Paninski L, Sher A, Litke AM, Chichilnisky EJ, Simoncelli EP (2008). Spatio-temporal correlations and visual signalling in a complete neuronal population. Nature 454:995-999. https://doi.org/10.1038/nature07140

[5] Rabiner LR (1989). A tutorial on hidden Markov models and selected applications in speech recognition. Proceedings of the IEEE 77:257-286. https://doi.org/10.1109/5.18626

[6] Holm S (1979). A simple sequentially rejective multiple test procedure. Scandinavian Journal of Statistics 6:65-70. https://www.jstor.org/stable/4615733

[7] Hemerik J, Goeman J (2018). Exact testing with random permutations. TEST 27:811-825. https://doi.org/10.1007/s11749-017-0571-1

[8] Efron B (1979). Bootstrap methods: another look at the jackknife. The Annals of Statistics 7:1-26. https://doi.org/10.1214/aos/1176344552

[9] Musall S, Kaufman MT, Juavinett AL, Gluf S, Churchland AK (2019). Single-trial neural dynamics are dominated by richly varied movements. Nature Neuroscience 22:1677-1686. https://doi.org/10.1038/s41593-019-0502-4

[10] International Brain Laboratory / Registry of Open Data on AWS (n.d.). IBL Neuropixels Brainwide Map on AWS. Official public data registry (accessed 18 October 2026). https://registry.opendata.aws/ibl-brain-wide-map/

[11] International Brain Laboratory (n.d.). 2025 - Brain Wide Map. Official IBL Library release documentation (accessed 18 October 2026). https://docs.internationalbrainlab.org/notebooks_external/2025_data_release_brainwidemap.html

[12] Creative Commons (n.d.). Attribution 4.0 International (CC BY 4.0). Official license deed (accessed 18 October 2026). https://creativecommons.org/licenses/by/4.0/
