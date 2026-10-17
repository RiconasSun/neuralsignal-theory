# Proposed P15 M1 specification — not activated

Recommended source: native IBL Brain Wide Map; target **MOp** (primary motor cortex, Allen parent plus registered laminar descendants on one probe). No pooling with SSp, SSs, other probes, sessions or animals. Exact candidate session/probe IDs and the initial 12-development / 8-final reservation are in results/ALLOCATION.csv. This is an M0 feasibility reservation; all 20 need protocol-consistent native annotation and physiological admission before any final study is claimed viable.

## One primary question

**Does strictly past local MOp spike history improve prediction of future MOp counts beyond a strong causal task, stimulus, wheel-movement and firing-rate baseline?**

This question is selected because MOp has independent-mouse candidate coverage, actual simultaneous spikes and source-clock wheel/task events. It avoids selecting a dynamical winner before fitting. Questions about preparation/execution transitions remain possible secondary analyses requiring prospective M1 registration; M0 selects neither those hypotheses nor a biological primitive. The central estimand is an observational, nuisance-adjusted predictive increment. It does not establish causal connectivity, latent physical states, motor control mechanisms or movement forecasting.

## M1 decisions to freeze before any scientific fitting

1. Pin exact native annotations and task revisions for all selected sessions. Reconcile UUID/quality/anatomy, keep boundary/layer uncertainties, recompute task capacity on native events and known invalid intervals. Do not reuse old bwm masks without verified equivalence. Never replace a pilot after observing neural feasibility or alter reservations using scores. If coverage shrinks below a defensible design, stop or seek a prospective exploratory redesign before outcomes.
2. Define training/calibration-only unit physiological QC (rate, refractory contamination, drift/coverage and finite observations), its frozen thresholds and sensitivity set. Provider label==1 remains the initial whole-session curated sampling frame, explicitly disclosed. Calibration-only fitted scales, offsets and QC decisions cannot use scoring counts. Fix one probe/session per mouse by metadata-only ranking, and apply equal-mouse aggregation.
3. Define supported observation windows, trial masks, native saturation conversion/exclusions and a preregistered neighborhood sensitivity. Count zeros inside covered windows, mark invalid/missing support separately. Do not infer recording support from detected spikes. Fix bin width and history horizon using development feasibility/scientific timescales, then freeze before scoring. The pilot's 50 ms bins are a counting demonstration, not a selected modeling hyperparameter.
4. Use blocked whole-trial development partitions, with history warm-up/guard gaps preventing overlap leakage. Reserve all sessions of the 8 final mice. Later final calibration and scoring must be disjoint chronologically and use one prospective assessment, under ordinary source access policy. No special cryptographic system is proposed. M0 does not authorize any final access.

## Model suitability and causal nuisance control

| Representation | What the data can support | Requirement for M1 |
|---|---|---|
| B0 stationary | Finite simultaneous counts and exposure | Training-only per-unit rate; explicit exposure offsets |
| B1 nuisance | Stimulus/contrast, cue, trial time/order, prior task history and wheel position | Only covariates observed before bin start; no future choice, feedback or current-bin velocity |
| B2 own history | Ordered target-unit spikes | Strict past finite history; reset/guard across excluded gaps |
| B3 other-unit population history | 8+ same-probe good-unit candidates, real 84/22 pilot units | Exclude target/current-bin counts; matched unit-count sensitivity |
| B4 combined | Task/wheel + own/other history | Mathematically nested nuisance-controlled contrasts, regularization and numerics frozen |
| D small discrete | Long recordings and repeated trials make small causal filtered representations plausible | Freeze small state count/budget; filter using past only, no smoothing or fitted scoring states |
| C low-dimensional history | Finite lag features permit tractable regularized projections/history summaries | Freeze capacity/budget; avoid unbounded optimizer rescue; independent gradient/PG checks |
| Static mixture | A useful guard if claiming temporal state dependence | Match capacity/nuisances and use strictly past gating; no automatic temporal-state claim |

No model is implemented or fitted in M0. Neither recurrent Poisson dynamics nor the failed P13 conditional autoregressive generator is required. M1 should prefer tractable convex Poisson baselines and bounded predictive representations, justify normalization/likelihood, set numerical stop criteria, and test causal indexing on synthetic fixtures before real fits. Models that cannot meet frozen numerical gates remain unavailable; no altered thresholds after scoring.

The proposed primary contrast is a nested combined-history increment over the same nuisance baseline, with own-history and other-unit increments separable in secondary contrasts. M1 must decide the exact contrast family, effect normalization, minimum mouse coverage, multiplicity and positive-claim conditions before scientific evaluation. Event-conditioned movement analyses, if included, are offline retrospective estimands; they may not be labeled real-time forecasts. Source first-movement extraction may use future behavior; do not insert it as if online available. Wheel-only adjustment leaves other movements unobserved, so all conclusions remain conditional on measured nuisances.

## Inference and falsification requirements

Mouse is the independent unit; one equal weight per mouse regardless of units/trials/probes. Propose paired mouse-level gains, exact sign flips, whole-mouse bootstrap intervals, multiplicity correction across the prospectively frozen family, leave-one-mouse-out and lab dependence sensitivities. Eight final candidates permit a minimum two-sided exact sign-flip p of 2/256 = 0.0078125 for one contrast; this arithmetic does **not** demonstrate power. With few labs/mice, a positive confirmatory claim needs separately justified effect precision and prospective criteria. Development is exploratory after its first access. No independent-laboratory replication claim.

Essential controls should preserve observations/task structure without unstable recursive Poisson simulation: count-preserving within-trial temporal disruption, task/contrast/order-conditioned trial reassignment, past-only circular/history disruption with explicit gap handling, wheel-matched strata, rate/unit-count matching, and static-mixture comparison if a temporal-state claim is made. A raw shuffle can change nuisance relationships; M1 must specify which null question each control tests, replicate count, matching limitations and correction before results. Also require anatomy-boundary, unit-QC, bin/history and saturation-neighborhood sensitivity, and a confounding assessment for labs/recording date/session choice.

## Stop and handoff

M1 must freeze exact hypotheses, architecture, parameter grid, solver/gradient/PG policies, sample sizes and masks **before fitting**, using this M0 as evidence rather than treating it as a validated protocol. Stop for irreconcilable identity/clock/source error or inadequate admitted coverage. Missing nonessential lossless-hardware certification alone is not a stop. M0's verdict only supports considering Prompt 2. M1–M7, model competition and final neural access are not activated.
