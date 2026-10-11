from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SMOKE_ROOT = ROOT / "structural_connectomes" / "mrtrix_act_sift2_smoke" / "100307"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def file_info(name: str) -> dict:
    path = SMOKE_ROOT / name
    return {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    smoke = read_json(RESULTS / "p7_e2_wsl_mrtrix_smoke.json")
    input_audit = read_json(RESULTS / "p7_hcp_structural_input_audit_download.json")
    tracked_files = {
        name: file_info(name)
        for name in [
            "dwi.mif",
            "wm.txt",
            "gm.txt",
            "csf.txt",
            "wmfod.mif",
            "wmfod_msmt_explicit.mif",
            "wm_tournier.txt",
            "wmfod_csd_smoke.mif",
            "5tt.mif",
            "5tt_dwi.mif",
            "nodes_dwi.mif",
            "gmwmi_seed.mif",
            "tracks_5k.tck",
            "tracks_5k_csd_diagnostic.tck",
            "sift2_weights_csd_diagnostic.txt",
            "connectome_sift2_csd_diagnostic.csv",
            "assignments_csd_diagnostic.csv",
            "connectome_sift2_smoke.csv",
        ]
    }
    payload = {
        "paper": "Paper 7",
        "experiment": "P7-ACT-SIFT2-engineering-diagnostic",
        "status": "P7_HIGH_FIDELITY_ROUTE_PARTIAL_5TT_READY_TRACTOGRAPHY_NOT_READY",
        "input_audit_status": input_audit.get("status"),
        "ready_subjects_after_input_audit": input_audit.get("ready_subjects_after", []),
        "smoke_status": smoke.get("status"),
        "smoke_completed_steps": smoke.get("completed_steps", []),
        "tracked_files": tracked_files,
        "diagnostic_findings": [
            "HCP 100307 DWI, gradients, mask, aparc+aseg, wmparc, WM dtseries, and movement files are locally available for the current FreeSurfer-5TT route.",
            "WSL user-space MRtrix3 can generate DWI MIF, tissue response files, MSMT-CSD output files, FreeSurfer 5TT, DWI-grid 5TT, and DWI-grid parcellation intermediates.",
            "Initial MSMT-CSD WM FOD output was all zero under the completed smoke run, making ACT/iFOD2 tractography invalid.",
            "Explicit-shell MSMT-CSD was attempted but exceeded the interactive runtime window and was interrupted before a usable replacement FOD could be validated.",
            "Single-tissue CSD generated a nonzero diagnostic FOD, and diagnostic ACT/iFOD2/SIFT2/tck2connectome completed. This proves the MRtrix back half can execute, but it is not the frozen P7 final-route MSMT-CSD result and cannot support a structural hypothesis claim.",
        ],
        "next_required_engineering_step": "Resolve MSMT-CSD zero-FOD/runtime issue, then rerun checkpointed E2 until ACT/iFOD2/SIFT2 connectome_sift2_smoke.csv exists for 100307 before scaling to 3 subjects.",
        "claim_boundary": "P7 remains open. The high-fidelity structural hypothesis has not been tested and no subject-specific structural-grounding result is available.",
        "forbidden_claims": [
            "P7 high-fidelity cohort connectomes generated",
            "P7 structural hypothesis supported",
            "P7 structural hypothesis falsified",
            "single-tissue diagnostic FOD equals the frozen MSMT-CSD pipeline",
        ],
    }
    (RESULTS / "p7_act_sift2_engineering_diagnostic.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = [
        "# P7 ACT/SIFT2 Engineering Diagnostic",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Findings",
        "",
        *[f"- {item}" for item in payload["diagnostic_findings"]],
        "",
        "## Next Required Step",
        "",
        payload["next_required_engineering_step"],
        "",
        "## Claim Boundary",
        "",
        payload["claim_boundary"],
        "",
    ]
    (RESULTS / "P7_ACT_SIFT2_ENGINEERING_DIAGNOSTIC.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
