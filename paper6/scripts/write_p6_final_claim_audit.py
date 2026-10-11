from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FULL_RESULT = RESULTS / "e3_e6_ds004117_full_cohort_batched_results.json"
E7_RESULT = RESULTS / "e7_ds004752_external_convergent_results.json"
CLAIM_AUDIT = RESULTS / "e8_claim_audit.json"


def main() -> int:
    if not FULL_RESULT.exists():
        raise SystemExit(f"Missing full-cohort result: {FULL_RESULT}")

    result = json.loads(FULL_RESULT.read_text(encoding="utf-8"))
    null = result["e6_nulls"]["label_shuffle_accuracy_null"]
    phase_accuracy = result["e6_nulls"]["phase_randomized_bandpower_specificity_accuracy"]["accuracy"]

    payload = {
        "allowed_current_claim": (
            "P6 has a frozen protocol, public dataset/event-semantics audit, ds004117 transition-window "
            "manifest, one-run real EEG signal extraction smoke, and full available ds004117 E3-E6 positive "
            "within-dataset result. ds004752 provides external convergent encoding-vs-maintenance evidence, "
            "but no direct cross-dataset transition-boundary replication has been run."
        ),
        "can_claim_cross_dataset_replication": False,
        "can_claim_external_convergent_stage_specificity": False,
        "can_claim_fast_dynamics_existence": True,
        "can_claim_nap_exists": False,
        "can_claim_transition_specificity": True,
        "can_run_e3_signal_extraction_after_data_download": True,
        "e0_protocol_frozen": True,
        "e1_dataset_audit": "PASS_INITIAL_E1",
        "e2_event_semantics": "PASS_INITIAL_E2_FOR_ds004117",
        "e2_transition_windows": "PASS_TRANSITION_WINDOWS_READY",
        "e3_signal_smoke": "PASS_SIGNAL_SMOKE",
        "e3_e6_initial_multi_run": "PASS_E3_E6_INITIAL",
        "e3_e6_full_ds004117": result["status"],
        "full_ds004117_scope": {
            "subjects": result["n_subjects"],
            "runs_event_files": result["n_event_files"],
            "transition_windows": result["n_windows"],
            "random_windows": result["n_random_windows"],
            "time_shift_windows": result["n_time_shift_windows"],
            "phase_randomized_windows": result["n_phase_randomized_windows"],
            "feature_family": result["feature_family"],
        },
        "full_ds004117_primary_results": {
            "same_transition_odd_even_centroid_similarity": result["e4_existence"][
                "same_transition_odd_even_centroid_similarity"
            ],
            "random_window_odd_even_centroid_similarity": result["e4_existence"][
                "random_window_odd_even_centroid_similarity"
            ],
            "leave_one_run_out_accuracy": result["e5_specificity"]["accuracy"],
            "subject_mean_accuracy": result["e5_subject_level"]["mean_accuracy"],
            "subject_bootstrap_ci95": result["e5_subject_accuracy_bootstrap"]["ci95"],
            "label_shuffle_null_mean_accuracy": null["null_mean_accuracy"],
            "label_shuffle_null_ci95": null["null_ci95"],
            "label_shuffle_one_sided_p": null["p_one_sided_observed_greater"],
            "random_window_specificity_accuracy": result["e6_nulls"]["random_window_specificity_accuracy"][
                "accuracy"
            ],
            "time_shift_specificity_accuracy": result["e6_nulls"]["time_shift_specificity_accuracy"]["accuracy"],
            "phase_randomized_bandpower_specificity_accuracy": phase_accuracy,
        },
        "scope_limits": [
            "within-dataset ds004117 result only",
            "external ds004752 result is convergent stage specificity, not direct transition-boundary replication",
            "no NAP validation",
            "phase-randomized bandpower specificity remains high",
            "current feature family is amplitude/bandpower-family evidence rather than phase-specific dynamics",
        ],
        "forbidden_claims": [
            "NAP is validated.",
            "CWP maps to NAP.",
            "Macro transitions are mechanistically explained.",
            "Fast neural dynamics are universal primitives.",
            "P6 is complete.",
        ],
    }
    if E7_RESULT.exists():
        e7 = json.loads(E7_RESULT.read_text(encoding="utf-8"))
        e7_null = e7["e7_label_shuffle_null"]
        payload["can_claim_external_convergent_stage_specificity"] = bool(
            e7["claim_audit"]["can_claim_external_convergent_stage_specificity"]
        )
        payload["e7_ds004752_external_convergent"] = e7["status"]
        payload["e7_ds004752_primary_results"] = {
            "subjects": e7["n_subjects"],
            "trials": e7["n_trials"],
            "feature_family": e7["feature_family"],
            "leave_one_subject_out_accuracy": e7["e7_stage_specificity"]["accuracy"],
            "subject_mean_accuracy": e7["e7_subject_accuracy_bootstrap"]["mean"],
            "subject_bootstrap_ci95": e7["e7_subject_accuracy_bootstrap"]["ci95"],
            "label_shuffle_null_mean_accuracy": e7_null["null_mean_accuracy"],
            "label_shuffle_null_ci95": e7_null["null_ci95"],
            "label_shuffle_one_sided_p": e7_null["p_one_sided_observed_greater"],
        }
    CLAIM_AUDIT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {CLAIM_AUDIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
