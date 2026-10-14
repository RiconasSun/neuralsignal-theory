# Complete exploratory Development results

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

## Probe, rate and mixed-control interpretation

[Complete per-mouse probe assessment](PROBE_DEPENDENCE.md) reports every selected shared-probe value and every available leave-probe-out range. Maximum within-mouse shifts from primary are0.09764899 (own),0.01908291 (population),0.01053225 (stimulus/time) and0.09438581 (combined) nats per nominal unit-bin. These shifts can exceed the corresponding cohort-average regional contrast; probe/selected-population dependence is a substantive limitation. They are not extra independent replicates or a basis for choosing a favorable probe.

[Training-rate matching audit](RATE_MATCHING.md) shows22–30 matched pairs per mouse and residual maximum absolute log-rate ratios up tolog(2). Matching is therefore approximate. The16-unit view reverses the stimulus/time and combined mean contrast signs relative to primary. Population mean direction remains negative across the five main views, but this does not overcome the corrected primary p0.0693 or establish probe-independent anatomy.

Temporal redistribution retains substantial own-history pooled gain: reference0.02495026 versus observed0.03110484. Thus own-history gain alone is not a pure within-trial temporal-dependence metric; preserved trial-count heterogeneity and conditioning are viable contributors. The temporal references for own/population/combined differ from observed under the conditional tests, while the stimulus/time temporal reference exceeds observed. Order disruption increases the own/population/combined pooled gains, and bin-label disruption increases the population gain. These mixed and negative controls preclude a simple universal feature hierarchy. Condition/bin controls detect some pooled context prediction without corrected regional context support. All contrasts and controls remain reported; no favorable control changes the nonsignificant primary conclusion.
