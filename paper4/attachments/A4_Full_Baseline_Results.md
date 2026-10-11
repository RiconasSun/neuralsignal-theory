# A4 Full Baseline / Competing-Explanation Results

## Proxy nuisance prediction

| dataset | model | fields | n_subject_folds | mean_subject_mse |
| --- | --- | --- | --- | --- |
| ds001634 | time_only | time_bin | 19 | 1.102542204027051 |
| ds001634 | proxy_nuisance_only | subject+run+time_bin+domain+load+context | 19 | 1.107666018132102 |
| ds001634 | transition_only | transition_type | 19 | 0.9334138088938118 |
| ds001634 | transition_plus_proxy_nuisance | transition_type+subject+run+time_bin+domain+load+context | 19 | 1.012541654807853 |
| ds001635 | time_only | time_bin | 16 | 1.421295410801802 |
| ds001635 | proxy_nuisance_only | subject+run+time_bin+domain+load+context | 16 | 1.4242927942776298 |
| ds001635 | transition_only | transition_type | 16 | 1.2624410776089086 |
| ds001635 | transition_plus_proxy_nuisance | transition_type+subject+run+time_bin+domain+load+context | 16 | 1.372610866672272 |
| ds004469 | time_only | time_bin | 63 | 14889.418656722277 |
| ds004469 | proxy_nuisance_only | subject+run+time_bin+domain+load+context | 63 | 14889.41865672223 |
| ds004469 | transition_only | transition_type | 63 | 14752.680597490122 |
| ds004469 | transition_plus_proxy_nuisance | transition_type+subject+run+time_bin+domain+load+context | 63 | 14892.532824580438 |

## Timing tests

| dataset | test | transition_same_minus_different | time_bin_same_minus_different | time_baseline_status | transition_exceeds_time_baseline | n_time_same | n_time_different |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ds001634 | time_bin_same_vs_different | 1.4457584051670238 | nan | INCONCLUSIVE_NO_SPLIT_HALF_TIME_BIN_GROUPS | nan | 0 | 0 |
| ds001635 | time_bin_same_vs_different | 1.1387585471361532 | nan | INCONCLUSIVE_NO_SPLIT_HALF_TIME_BIN_GROUPS | nan | 0 | 0 |
| ds004469 | time_bin_same_vs_different | 0.8106250238842029 | nan | INCONCLUSIVE_NO_SPLIT_HALF_TIME_BIN_GROUPS | nan | 0 | 378 |
| ds001634 | transition_after_time_bin_residualization | 1.1781439536656932 | nan | RESIDUALIZATION_TEST | True | 114 | 57 |
| ds001635 | transition_after_time_bin_residualization | 0.8036665610609246 | nan | RESIDUALIZATION_TEST | True | 96 | 48 |
| ds004469 | transition_after_time_bin_residualization | 1.1388472358283668 | nan | RESIDUALIZATION_TEST | True | 126 | 63 |
