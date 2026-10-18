# Independent internal statistics review 1

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Review date: 2026-10-18 UTC.

Decision: **REPAIR_REQUIRED_BEFORE_E_ANALYSIS_INTEGRATION**. Open P0: 0. Open P1: 1. This unsuccessful review is retained. No real effects, scores, B/E observations, raw data/cache, source/network request or fit was accessed or computed. Only this review artifact was written.

## P1-01: analysis accepts duplicate mice and silently shrinks comparison cohorts

`statistics.analyze` does not require unique subject identities or an explicit expected cohort. It builds each comparison by filtering only rows containing both model keys. A missing required primary model is silently dropped, and duplicate subject rows are counted as independent mice. The result remains labeled EXPLORATORY_PREDICTIVE_COMPARISON. Exploratory interpretation does not permit pseudoreplication or selection of an easier subset of the frozen admitted Development mice.

Independent synthetic reproductions:

- Eight distinct positive-effect mice plus a duplicate of the first mouse were reported as n_mice=9 with sign-flip p=0.001953125 (1/512), rather than rejecting the duplicate. The registered unit is one mouse, once.
- Eight input mice with B4 missing for one mouse were silently reported as a seven-mouse primary comparison with status EXPLORATORY_PREDICTIVE_COMPARISON, rather than failing the incomplete primary gate. No explicit missing-subject accounting accompanied the shrink.

Frozen M1 requires one equal weight per mouse, fixed admission/partitions, global Development candidate availability on every admitted mouse, and retention of unavailable comparisons with p=1 in the fixed correction family. Primary eligibility cannot change because a model/output is missing. A preregistered per-contrast cohort must be explicit and source-defined before scoring; it cannot be inferred from whichever model outputs happen to be present.

Minimal repair: require unique subjects and explicit expected cohort identities at the analysis boundary; reject incomplete required primary input; retain an unavailable secondary slot with p=1 when the required globally available family/cohort is incomplete, unless an explicitly registered per-contrast cohort has been provided and verified. Preserve exact subject/exclusion identities. Do not reweight, deduplicate arbitrarily, or choose a favorable subset after E. The pre-E integration must also ensure bootstrap index streams refer to the registered common mouse cohort rather than silently reseeding a changed subset.

Required synthetic tests: duplicate subject, unexpected/missing expected subject, incomplete B1/B4 primary, secondary unavailable on one required mouse retaining its correction slot, and a complete valid fixed cohort. These require no real E values or policy amendment.

## Contract-consistent numerical/statistical surfaces reviewed

For valid complete unique-mouse inputs, the source implements equal-mouse LL/Q effects, exhaustive one-sided primary and two-sided secondary sign enumeration, and the frozen equality stabilization already present in the M1 synthetic oracle. It retains the fixed five-secondary Holm family with p=1 for wholly unavailable comparisons. The same PCG64 seed150101 and 10,000 n-mouse index draws are regenerated for each same-sized cohort, yielding the same index stream for registered common cohorts; percentile intervals use linear quantiles. Lab-block seed150102 is separate, and the lab-block resample includes whole lab clusters; equal-lab means and LOMO/LOLO diagnostics are distinct from the primary mouse mean. These diagnostics do not establish independent-laboratory replication.

The result labels explicitly retain exploratory=true, heldout_animal_confirmation=false and validated=false. The source states the independent sign-exchangeable symmetric-zero-centered assumption and lab/asymmetry limitation. This matches A6's requirement to distinguish exact sign enumeration from assumption-free population inference. No pretest, power claim, confirmatory predicate relaxation or positive-claim promotion is implemented here.

Fresh reviewer execution: all **5 test_statistics tests PASS** with ResourceWarning as error. They cover sign enumeration/frozen oracle, fixed Holm slots, equal-mouse versus pooled-bin weighting, bootstrap/lab reproducibility and denominator mismatch. The two additional synthetic counterexamples above demonstrate a coverage gap in those tests; their success does not close P1-01.

## Exact reviewed SHA256 identities

| File | SHA256 |
|---|---|
| paper15_dev/statistics.py | 8d532687ee52c5f252d705d31f95e9ff679e39cbdd97ea9466fabe87777f849a |
| paper15_dev/test_statistics.py | fc927af72de9667779bb63e2af297baaec256934217c10e21c8b25192d45a303 |
| paper15_m1/STATISTICS_CONTROLS.md | 3a2665cc43cffac9af7e33ae5c61d937f7caf9cb4ca89c4e692ae4dc39fa0254 |
| paper15_m1/A1_A10_CLAIM_AUDIT.md | 6a4fe5369cf908b801ab65bd856e8c2c4619781a5ed9c70f09551fc5adbd8273 |

Repair and independently review cohort enforcement before the full pre-E gate. This finding does not change or invalidate unchanged running A fits, authorize B/E access, or approve Final inference.
