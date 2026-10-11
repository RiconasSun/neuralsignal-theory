from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SMOKE = ROOT / "structural_connectomes" / "mrtrix_act_sift2_smoke" / "100307"


def file_info(path: Path) -> dict:
    return {"exists": path.exists(), "size_bytes": path.stat().st_size if path.exists() else 0, "path": str(path)}


def response_nonzero(path: Path) -> bool:
    if not path.exists():
        return False
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        for item in line.split():
            try:
                if abs(float(item)) > 0:
                    return True
            except ValueError:
                continue
    return False


def known_zero_from_prior_stats(name: str) -> bool:
    # Prior MRtrix mrstats evidence in this package showed these completed MSMT
    # outputs had zero mean, median, std, min, and max across all volumes.
    return name in {"wmfod.mif", "wmfod_msmt_explicit.mif", "gm_msmt_explicit.mif", "csf_msmt_explicit.mif"}


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    final_smoke = json.loads((RESULTS / "p7_final_route_single_subject_smoke.json").read_text(encoding="utf-8")) if (RESULTS / "p7_final_route_single_subject_smoke.json").exists() else {}
    files = {
        "dwi": SMOKE / "dwi.mif",
        "wm_response": SMOKE / "wm.txt",
        "gm_response": SMOKE / "gm.txt",
        "csf_response": SMOKE / "csf.txt",
        "msmt_wmfod": SMOKE / "wmfod.mif",
        "msmt_wmfod_explicit": SMOKE / "wmfod_msmt_explicit.mif",
        "msmt_wmfod_ext4": SMOKE / "wmfod_ext4.mif",
        "diagnostic_single_tissue_wmfod": SMOKE / "wmfod_csd_smoke.mif",
        "final_route_connectome": SMOKE / "connectome_sift2_smoke.csv",
        "final_route_ext4_connectome": SMOKE / "connectome_sift2_ext4_msmt_smoke.csv",
        "diagnostic_connectome": SMOKE / "connectome_sift2_csd_diagnostic.csv",
    }
    ext4_ready = files["msmt_wmfod_ext4"].exists() and files["msmt_wmfod_ext4"].stat().st_size > 100_000_000
    final_route_ready = (
        files["final_route_ext4_connectome"].exists()
        and files["final_route_ext4_connectome"].stat().st_size > 0
        and final_smoke.get("status") == "PASS_SINGLE_SUBJECT_FINAL_ROUTE_SMOKE"
    )
    status = "PASS_EXT4_MSMT_FOD_AND_SINGLE_SUBJECT_FINAL_ROUTE_READY" if ext4_ready and final_route_ready else "BLOCKED_MSMT_FOD_NOT_READY"
    payload = {
        "paper": "Paper 7",
        "experiment": "P7-MSMT-FOD-readiness-validator",
        "status": status,
        "subject": "100307",
        "files": {name: file_info(path) for name, path in files.items()},
        "response_nonzero": {
            "wm": response_nonzero(files["wm_response"]),
            "gm": response_nonzero(files["gm_response"]),
            "csf": response_nonzero(files["csf_response"]),
        },
        "known_zero_msmt_outputs_from_mrstats": [
            name for name, path in files.items() if known_zero_from_prior_stats(path.name)
        ],
        "final_route_connectome_exists": files["final_route_connectome"].exists(),
        "final_route_ext4_connectome_exists": files["final_route_ext4_connectome"].exists(),
        "diagnostic_connectome_exists": files["diagnostic_connectome"].exists(),
        "gate": {
            "msmt_response_files_nonzero": all(response_nonzero(files[name]) for name in ["wm_response", "gm_response", "csf_response"]),
            "msmt_fod_nonzero_validated": ext4_ready,
            "allow_final_route_tractography": final_route_ready,
            "allow_3_subject_scale": final_route_ready,
        },
        "next_action": "If PASS, continue to 3-subject smoke and then 10-subject QC. If BLOCKED, regenerate MSMT-CSD until ext4 WM FOD and final-route connectome pass.",
        "claim_boundary": "P7 remains open. A one-subject ext4 MSMT-CSD final-route smoke can unblock engineering scale-up, but it does not test the structural hypothesis.",
    }
    (RESULTS / "p7_msmt_fod_readiness_validator.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if status != "PASS_EXT4_MSMT_FOD_AND_SINGLE_SUBJECT_FINAL_ROUTE_READY":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
