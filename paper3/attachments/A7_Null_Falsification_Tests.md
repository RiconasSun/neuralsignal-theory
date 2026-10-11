# A7 Null / Falsification Tests

The primary null test shuffles transition labels within dataset while preserving the extracted delta vectors.

| null_test | dataset | observed_same_minus_different | n_permutations | null_mean | null_99th_percentile | observed_percentile_vs_null | upper_tail_p | survives_99_percent_null |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| within_dataset_label_shuffle | ds001634 | 1.4457584051670238 | 500 | -0.2335545030716123 | -0.0742840244928331 | 1.0 | 0.0019960079840319 | True |
| within_dataset_label_shuffle | ds001635 | 1.1387585471361532 | 500 | -0.2163100000112396 | -0.0531863944680163 | 1.0 | 0.0019960079840319 | True |
| within_dataset_label_shuffle | ds004469 | 0.8106250238842029 | 500 | -0.1766451734613774 | -0.0445604306706864 | 1.0 | 0.0019960079840319 | True |
