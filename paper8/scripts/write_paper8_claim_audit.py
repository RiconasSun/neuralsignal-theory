from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    e0 = read_json(RESULTS / "p8_e0_public_dataset_physio_audit.json")
    e1 = read_json(RESULTS / "p8_e1_hcp_wm_physio_download.json")
    hcp_preflight = read_json(RESULTS / "p8_e1_e6_hcp_physio_ladder_preflight_blocker.json")
    ladder = read_json(RESULTS / "p8_e1_e6_hcp_physio_ladder_smoke.json")
    extension_manifest = read_json(RESULTS / "p8_final_extension_ds005795_manifest_audit.json")
    extension_download = read_json(RESULTS / "p8_final_extension_ds005795_smoke_download.json")
    extension_features = read_json(RESULTS / "p8_final_extension_ds005795_physio_feature_smoke.json")
    extension_ladder = read_json(RESULTS / "p8_final_extension_ds005795_nuisance_ladder_smoke.json")
    extension_streaming = read_json(RESULTS / "p8_final_extension_ds005795_streaming_nuisance_ladder.json")
    extension_streaming_figure = read_json(RESULTS / "p8_ds005795_streaming_figure.json")
    manuscript_pdf = read_json(RESULTS / "p8_manuscript_pdf.json")
    p8_ready = str(e0.get("status", "")).startswith("PASS_E0")
    raw_reproduced = bool(ladder.get("gates", {}).get("Gate_A_raw_transition_reproduced"))
    motion_survival = bool(ladder.get("gates", {}).get("Gate_B_measured_motion_survival"))
    physiology_survival = bool(ladder.get("gates", {}).get("Gate_C_measured_physiology_survival"))
    ladder_status = ladder.get("status")
    if ladder_status == "FAIL_RAW_TRANSITION_NOT_REPRODUCED":
        status = "P8_E1_E6_HCP_PHYSIO_SMOKE_RAW_GATE_FAILED"
        allowed = "Paper 8 found HCP WM measured physiology files and ran an 18-subject measured-physiology ladder smoke, but the preregistered raw SameTransition > DifferentTransition gate was not reproduced. No physiological-survival claim is allowed."
    elif raw_reproduced:
        status = "P8_E1_E6_HCP_PHYSIO_SMOKE_RAW_GATE_REPRODUCED"
        allowed = "Paper 8 found HCP WM measured physiology files and ran a measured-physiology ladder smoke. Claims remain limited until full nuisance ladder and final holdout are run."
    elif p8_ready:
        status = "P8_E0_PHYSIO_DATASET_AUDIT_READY"
        allowed = "Paper 8 has a frozen measured-physiology falsification protocol and an E0 public dataset/physio availability audit, but no valid E1-E6 nuisance-ladder result is present in the current result bundle."
    else:
        status = "P8_E0_PHYSIO_DATASET_AUDIT_BLOCKED"
        allowed = "Paper 8 has a frozen measured-physiology falsification protocol, but measured physiology availability is blocked."
    payload = {
        "paper": "Paper 8",
        "status": status,
        "can_claim_raw_transition_reproduced": raw_reproduced,
        "can_claim_measured_motion_survival": motion_survival,
        "can_claim_measured_physiology_survival": physiology_survival,
        "can_claim_aggressive_nuisance_survival": False,
        "can_claim_neural_origin_proven": False,
        "allowed_current_claim": allowed,
        "blockers": e0.get("blockers", []),
        "e0_status": e0.get("status"),
        "e1_download_status": e1.get("status"),
        "e1_e6_raw_reproduction_preflight": {
            "status": hcp_preflight.get("status"),
            "n_missing_required_paths": hcp_preflight.get("n_missing_required_paths"),
            "existing_result_available": hcp_preflight.get("existing_result_available"),
            "claim_boundary": hcp_preflight.get("claim_boundary"),
        },
        "e1_e6_ladder_status": ladder_status,
        "ds005795_extension": {
            "role": "convergent measured-physiology validation, not direct Encode/Maintain/Probe replication",
            "manifest_status": extension_manifest.get("status"),
            "download_status": extension_download.get("status"),
            "feature_status": extension_features.get("status"),
            "ladder_status": extension_ladder.get("status"),
            "subjects": extension_ladder.get("subjects", extension_download.get("subjects", [])),
            "n_subjects": extension_ladder.get("n_subjects"),
            "aggregate_results": extension_ladder.get("aggregate_results", {}),
            "allowed_claim": "The ds005795 extension has a three-subject BOLD/physiology/metadata interface smoke. It does not establish physiology-robust transition dynamics.",
        },
        "ds005795_streaming_extension": {
            "role": "convergent measured-physiology nuisance-ladder analysis over global BOLD signal; not direct Encode/Maintain/Probe replication",
            "status": extension_streaming.get("status"),
            "n_subjects_requested": extension_streaming.get("n_subjects_requested"),
            "n_subjects_passed": extension_streaming.get("n_subjects_passed"),
            "subjects_passed": extension_streaming.get("subjects_passed", []),
            "subjects_requested": extension_streaming.get("subjects_requested", []),
            "aggregate_results": extension_streaming.get("aggregate_results", {}),
            "delta_vs_state_only": extension_streaming.get("delta_vs_state_only", {}),
            "figure_status": extension_streaming_figure.get("status"),
            "figure_png": extension_streaming_figure.get("figure_png"),
            "claim_boundary": extension_streaming.get("claim_boundary"),
            "allowed_claim": "The ds005795 streaming extension completed all manifest-available learning subjects with complete BOLD/physio/events files. It shows physiology regressors improve global-signal prediction in this convergent task, but it does not rescue the failed HCP primary transition-reproducibility gate.",
        },
        "ladder_gates": ladder.get("gates", {}),
        "ladder_scope": ladder.get("scope"),
        "manuscript_pdf": {
            "status": manuscript_pdf.get("status"),
            "pdf": manuscript_pdf.get("pdf"),
            "n_pages": manuscript_pdf.get("n_pages"),
            "claim_boundary": manuscript_pdf.get("claim_boundary"),
        },
        "forbidden_claims": [
            "physiology eliminated",
            "motion fully excluded",
            "neural origin proven",
            "CWP validated",
            "NAP validated",
        ],
    }
    (RESULTS / "p8_e8_claim_audit.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
