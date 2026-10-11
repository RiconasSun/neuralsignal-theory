# A6 Statistics

## E2 reproduction

| dataset | label_field | same_mean_cosine | different_null_mean_cosine | same_minus_different | n_same | n_different | supports_signal |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ds001634 | transition_type | 0.7765306274806373 | -0.6692277776863865 | 1.4457584051670238 | 114 | 57 | True |
| ds001635 | transition_type | 0.6674587699598806 | -0.4712997771762725 | 1.1387585471361532 | 96 | 48 | True |
| ds004469 | transition_type | 0.4939706236331221 | -0.3166544002510807 | 0.8106250238842029 | 126 | 63 | True |

## E4 residualized contrasts

| dataset | label_field | same_mean_cosine | different_null_mean_cosine | same_minus_different | n_same | n_different | supports_signal | residualization_variant | nuisance_fields |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ds001634 | transition_type | 0.6340416141086701 | -0.5441023395570231 | 1.1781439536656932 | 114 | 57 | True | time_only | time_bin |
| ds001635 | transition_type | 0.5073765720278773 | -0.2962899890330473 | 0.8036665610609246 | 96 | 48 | True | time_only | time_bin |
| ds004469 | transition_type | 0.7582223318009584 | -0.3806249040274082 | 1.1388472358283668 | 126 | 63 | True | time_only | time_bin |
| ds001634 | transition_type | 0.7741820688650334 | -0.750132145267457 | 1.5243142141324904 | 114 | 57 | True | domain_load_context | domain+load+context |
| ds001635 | transition_type | 0.6614999591171907 | -0.5494461330608457 | 1.2109460921780364 | 96 | 48 | True | domain_load_context | domain+load+context |
| ds004469 | transition_type | 0.9380131033620716 | 0.8373274514233975 | 0.1006856519386741 | 126 | 63 | True | domain_load_context | domain+load+context |
| ds001634 | transition_type | 0.6355998029042705 | -0.5572159314230517 | 1.1928157343273222 | 114 | 57 | True | run_time_context | run+time_bin+domain+load+context |
| ds001635 | transition_type | 0.507309682839488 | -0.3016320791653386 | 0.8089417620048265 | 96 | 48 | True | run_time_context | run+time_bin+domain+load+context |
| ds004469 | transition_type | 0.7582223318009584 | -0.3806249040274082 | 1.1388472358283666 | 126 | 63 | True | run_time_context | run+time_bin+domain+load+context |
| ds001634 | transition_type | 0.5961254940208494 | -0.7976254154777639 | 1.3937509094986131 | 114 | 57 | True | subject_run_time_context | subject+run+time_bin+domain+load+context |
| ds001635 | transition_type | 0.4142989875526956 | -0.6947780004492086 | 1.1090769880019042 | 96 | 48 | True | subject_run_time_context | subject+run+time_bin+domain+load+context |
| ds004469 | transition_type | 0.6785748718249974 | -0.9999996425701928 | 1.6785745143951902 | 126 | 63 | True | subject_run_time_context | subject+run+time_bin+domain+load+context |
