# Exact native alias and value-interface regressions

The current19 synthetic tests were independently accepted in PREACCESS_REVIEW_2.md. That exact source/interface candidate is pinned by PREACCESS_APPROVAL.json. Original17 tests are retained; new unknown-phase and actual child hard-kill tests repair two independently reproduced defects. A test setup missing `sys` import was preserved and fixed without changing its kill/byte assertions.

|Required behavior|Executable oracle|
|---|---|
|Hard canonical paths and original hard timestamp aliases|test_valid_soft_and_hard_alias_exact_object_identity_and_reads|
|Only the fixed literal SoftLink alias, exact same-file/object ID/address|Same test and actual per-source component/structure audit|
|Every missing component/unexpected Dataset parent rejected|test_external_cycle_relative_spoofed_missing_and_dataset_parent_denied|
|External file never opened; cycle/relative/spoofed/neural target denied|Same test, exact-literal-before-dereference logic|
|No unauthorized/neural path or unrestricted dataset value API|test_unknown_path_neural_values_and_unrestricted_value_apis_denied|
|Clock, units, scaling, native dtype and distinct false timestamp object rejected|test_units_scaling_clock_dtype_and_fake_timestamp_identity_denied|
|Other/altered/Final sources denied before open|test_final_altered_and_unregistered_source_denied|
|Float32 finite extremes/subnormal/signedzero roundtrip exact|test_exact_float32_extremes_subnormal_signed_zero|
|Native float64 rotation retained; first source must match known float32|test_float64_rotation_preserved_and_first_dtype_fixed|
|Nonfinite/unsupported/order/row/duration errors stop|test_nonfinite_unsupported_order_correspondence_duration_rejected|
|Strictpast, invalid intervals, stale/long intervals, zero/missing distinction|test_strict_past_invalid_long_interval_and_removed_rows_missing; test_zero_rows_retained_and_float64_overflow_not_silently_saturated|
|Actual transport/source/save interface with fixed masks/features/floors|test_full_synthetic_source_interface_pass_and_native_bit_preservation; test_frozen_features_bits_masks_and_all_role_color_coverage|
|First direct-coverage failure cannot continue/retry|test_valid_source_with_failed_first_coverage_stops_without_retry|
|Missing/failed/incomplete independent first review blocks remaining|test_first_actual_review_gate_missing_or_failed_cannot_unlock_remaining plus reviewer14 artifact-omission checks|
|Unknown worker phase rejected before any review/stage/source effect|test_unknown_worker_phase_denied_before_review_or_stage_mutation|
|Hard-kill during next vector read retains prior original vector|test_external_hardkill_retains_completed_native_vector_before_next_read|
|No redirect/retry/bulk; exact range/header; partial accounting|test_HTTP_ranges_no_redirect_retry_cache_and_partial_accounting|
|Original per-source/global/request/deadline ceilings and external timeout|test_per_object_global_request_and_cache_deadline_limits; test_watchdog_duplicate_and_cohort_floors_not_physiology|

These are engineering oracles, not actual source-wide success or scientific evidence. The first actual source received its own independent saved-state numerical review. All remaining source outcomes require complete saved-state and final cohort review; no first-source extrapolation.
