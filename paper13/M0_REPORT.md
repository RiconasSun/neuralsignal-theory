# Paper 13 M0 feasibility stop

Mission: `P13-PFC-LOCAL-PREDICTIVE-DYNAMICS`.
Research question: whether local PFC discrete or continuous dynamics add predictive information beyond strong causal firing-rate/history/task/time/behavior baselines.

**Scientific gate: FAIL / DATA INSUFFICIENT under the original P13 M0 registration.** This is a limitation of this dataset, region granularity and registered eligibility route together. It does not establish that the IBL dataset generally lacks useful PFC data or that local dynamics lack predictive information. No model comparison was attempted.

## Prospective decisions and source identity

M0 was registered at 2026-10-16T03:24:39.601911+00:00 (2026-10-15 Pacific). Before coverage decoding, the rule fixed ACAd then ORBvl then PL, exact provider Allen labels or laminar descendants, no regional or probe pooling, at least20 provider-good units on one simultaneously recorded probe, at least400 usable curated trials, and at least8 independent mice in each development/final group (target12/group). Twenty good units was an analyst-chosen local-population feasibility floor, not supplied by the user or justified as a universal physiological threshold. Four hundred trials provided room for separate within-session fitting and scoring partitions; no model fit/power guarantee follows. The minima are retained after observing failure. No lower-cutoff sensitivity or alternate model route was searched.

With8 final mice the smallest possible two-sided exact sign-flip p-value is2/256=.0078125; a three-comparison Holm minimum is.0234375. This only shows that a confirmatory route is arithmetically possible at the floor, not adequately powered for a particular effect. Target12 improves precision. All eligibility and source choices are disclosed as metadata-informed.

Provider `Brainwidemap` documentation identifies the 2025 release. Frozen source commit: `118fc36cb3602934466ad2c6087c2b3b441f9f1f`; insertion fixture `2023_12_bwm_release`; original published aggregate tag `2024_Q2_IBL_et_al_BWM`; sorting revision referenced by provider `2024-05-06`. The current provider source also offers a later2026 cluster tag. P13 explicitly pinned the original paired cluster/trial aggregates before coverage inspection rather than silently joining different aggregate revisions. All699 fixture probes and459 sessions joined exactly; all cluster UUIDs and(pid,cluster_id) pairs were unique.

Object receipts, ETags, sizes and downloaded-column SHA256 hashes are saved. Clusters object:91,555,529 bytes, ETag `b89fac76289f3a3d585910711f1eef41`; trials:24,212,510 bytes, multipart ETag `eafa5476b9938819a2a089c8d4ae32a1-2`. A multipart ETag is not a content MD5. Full aggregate checksums were not locally recomputed because only whitelisted columns were read. Transport checked exact Content-Range and unchanged ETag, and saved each received range hash plus each decoded CSV hash. Do not present these as full-object checksum verification or independent anatomical validation.

## Complete denominator and observed coverage

The exact frozen release contains139 mice,459 sessions,699 probes,621,733 clusters,75,708 provider-good clusters and295,920 task trials. No fixture probe lacks cluster metadata; no session lacks trial metadata; no aggregate identity lies outside the fixture. Atlas ID0 is unassigned for12,215 clusters and does not contribute to any candidate region. Provider quality labels are derived summaries, explicitly accessed for metadata feasibility; no spike trains, count arrays or predictive scores were accessed.

| Candidate | Anatomical mice | Labeled units | Provider-good units | Mice with ≥20 good units on one probe | Mice also meeting ≥400 usable trials | Maximum smaller split |
|---|---:|---:|---:|---:|---:|---:|
| ACAd |18|1,960|369|6|4|2|
| ORBvl |9|3,060|669|6|4|2|
| PL |16|2,165|420|8|7|3|

Every candidate fails the required16-mouse total even **before** trial, movement, complete observation-support or training-only physiological QC gates. The trial-filter result cannot rescue or cause the independent unit-coverage shortfall. The139 global subjects are not an eligible regional cohort;16 anatomical PL mice are not16 physiologically eligible simultaneous populations.

All2,097 probe×region rows,139 mouse rows,459 session rows, and7,185 candidate unit identities are retained. The compressed cluster metadata enumerates all621,733 cluster identities. No primary region was chosen and no development/final allocation was made. Fully admitted animals=0; the table gives upper bounds, not admission.

## Timing, masks and access limits

Saved trial fields include interval boundaries, stimulus/go-cue/feedback/response/first-movement timestamps, prior-probability context, provider `bwm_include`, and seven saturation flags. A usable M0 trial requires finite interval/stimulus/go-cue/feedback timestamps, stimulus and go-cue inside the interval before feedback, duration≥100ms, and provider inclusion. The complete reason counts and saturation counts per session are saved in `M0_audit.json`. Provider `bwm_include` itself has curated behavioral/event criteria; it is not a neural observation certificate. Saturation flags were counted, not silently converted into a full-session gap certificate or additional exclusion rule.

After the decisive unit-count failure, no further wheel/video availability, ephys clock, raw saturation-interval, behavioral-covariate completeness or full scoring-window support acquisition was performed. Their essential gates remain unverified. No assumption of hardware-packet completeness was imposed. Current-trial behavioral event values were not used as predictors; their timestamps were inspected as authorized metadata only. Training-only physiological QC, fitted scaling and causal neural features were not reached.

## Stopped stages and scientific claim boundary

M1–M7 are blocked by M0. Frozen scientific models, grids, trial assignments, tests and nulls for a viable cohort have not been registered or executed. Baseline/dynamical predictive scores, animal effects, confidence intervals, p-values and null results are **NOT RUN**, not zero or nonsignificant. No final mouse outcomes were opened. No manuscript or supplement PDF is claimed complete. This feasibility report is not a generic firing-rate benchmark or a baseline-only substitute for the requested dynamics comparison.

No thresholds, sample, anatomical boundaries or quality labels were changed after failure. All P1–P12 scientific failures and artifacts remain intact. No P12 data or fitted states were reused. This does not revive any P12 M4 optimization route.

## Separate-dataset assessment, without another dataset search

The user-supplied PFC-map article describes a separate KI cohort and public NWB releases, with99 recording sessions in its data-availability statement. That establishes a reason to consider **one separately registered metadata feasibility audit**, not evidence that16 independent mice satisfy the present single-region/task/nuisance requirements. Its KI recordings span different behavioral settings and include tone presentations; importing them would require different task/covariate definitions. Its IBL task subset is the same underlying IBL source, not a new independent cohort. No DANDI inventory or neural file was requested, and no alternate cohort was admitted.

Recommendation: preserve this stop. If the owner wishes to continue, separately register one bounded KI/PFC metadata audit with its own fixed estimand, subject/region/task/support rules and minimum independent-mouse gate before any new neural access. Neither a smaller-unit IBL route nor a different dataset is authorized to replace this failed protocol automatically.

## References and reproduction

- [IBL official release documentation](https://docs.internationalbrainlab.org/notebooks_external/2025_data_release_brainwidemap.html).
- [Frozen IBL provider source](https://github.com/int-brain-lab/paper-brain-wide-map/tree/118fc36cb3602934466ad2c6087c2b3b441f9f1f).
- [A brain-wide map of neural activity during complex behaviour](https://www.nature.com/articles/s41586-025-09235-0).
- [Brain-wide representations of prior information in mouse decision-making](https://www.nature.com/articles/s41586-025-09226-1); direct article retrieval failed in this audit, title/link corroborated by provider README; no uninspected result attributed.
- [A prefrontal cortex map based on single-neuron activity](https://www.nature.com/articles/s41593-025-02190-z), methods and data availability inspected only for the limited alternative-protocol assessment above.

Run `& .\paper13\reproduce.ps1` from the repository root. A successful saved-only run reproduces the scientific stop, not a completed study. Review, exact Git closure and unresolved requirement states are in the mission evidence folder. No external peer review or journal action is claimed.
