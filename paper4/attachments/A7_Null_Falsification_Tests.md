# A7 Null / Falsification Tests

## Synthetic noise

| dataset | noise_sigma_multiplier | n_repeats | mean_same_minus_different | min_same_minus_different | survival_rate_positive | survives_synthetic_noise |
| --- | --- | --- | --- | --- | --- | --- |
| ds001634 | 0.25 | 100 | 0.0241606175256049 | -0.0010335285637067 | 0.98 | True |
| ds001635 | 0.25 | 100 | 0.0148935636945761 | -0.0117566166992293 | 0.88 | False |
| ds004469 | 0.25 | 100 | 0.1018887460922906 | 0.0766737369752745 | 1.0 | True |
| ds001634 | 0.5 | 100 | 0.0060250838178819 | -0.0272643793690153 | 0.7 | False |
| ds001635 | 0.5 | 100 | 0.0029779219278882 | -0.0223358378279149 | 0.6 | False |
| ds004469 | 0.5 | 100 | 0.0951802586476669 | 0.0734292915604024 | 1.0 | True |
| ds001634 | 1.0 | 100 | 0.0025925816669255 | -0.0255285100230348 | 0.55 | False |
| ds001635 | 1.0 | 100 | -0.0013367492896809 | -0.0328325281152923 | 0.45 | False |
| ds004469 | 1.0 | 100 | 0.0925356640316873 | 0.0692538699109151 | 1.0 | True |
| ds001634 | 2.0 | 100 | 0.0018548836465265 | -0.0327295812580163 | 0.58 | False |
| ds001635 | 2.0 | 100 | 0.0005884128074812 | -0.0290157376254446 | 0.52 | False |
| ds004469 | 2.0 | 100 | 0.0865606109908813 | 0.0661411645659979 | 1.0 | True |

## Label shuffle

| dataset | null_test | observed_same_minus_different | n_permutations | null_mean | null_99th_percentile | observed_percentile_vs_null | upper_tail_p | survives_99_percent_null |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ds001634 | frequency_preserving_transition_label_shuffle | 1.4457584051670238 | 500 | -0.2309452072495131 | -0.078055431122446 | 1.0 | 0.0019960079840319 | True |
| ds001635 | frequency_preserving_transition_label_shuffle | 1.1387585471361532 | 500 | -0.2119220246084444 | -0.0645128474127131 | 1.0 | 0.0019960079840319 | True |
| ds004469 | frequency_preserving_transition_label_shuffle | 0.8106250238842029 | 500 | -0.1768136830244614 | -0.0435188081710145 | 1.0 | 0.0019960079840319 | True |
