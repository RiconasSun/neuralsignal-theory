from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path

from paper7_e5_labelconvert_connectome_qc import connectome_qc, run_wsl, to_wsl_path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT_ROOT = ROOT / "structural_connectomes" / "mrtrix_act_sift2_smoke"


def run_subject_sensitivity(subject: str, streamlines: int) -> dict:
    out_root = OUT_ROOT / subject
    wmfod = out_root / "wmfod_ext4.mif"
    five_tt = out_root / "5tt_dwi.mif"
    gmwmi = out_root / "gmwmi_seed.mif"
    nodes = out_root / "nodes_fsdefault_dwi.mif"
    missing = [
        name
        for name, path in {
            "wmfod_ext4": wmfod,
            "5tt_dwi": five_tt,
            "gmwmi_seed": gmwmi,
            "nodes_fsdefault_dwi": nodes,
        }.items()
        if not path.exists()
    ]
    if missing:
        return {"subject": subject, "status": "BLOCKED_MISSING_INPUTS_FOR_STREAMLINE_SENSITIVITY", "missing": missing}

    tracks = out_root / f"tracks_{streamlines}_ext4_msmt_sensitivity.tck"
    weights = out_root / f"sift2_weights_{streamlines}_ext4_msmt_sensitivity.txt"
    connectome = out_root / f"connectome_sift2_ext4_msmt_fsdefault84_{streamlines}_sensitivity.csv"
    assignments = out_root / f"assignments_ext4_msmt_fsdefault84_{streamlines}_sensitivity.csv"
    p = {
        "wmfod": shlex.quote(to_wsl_path(wmfod)),
        "5tt": shlex.quote(to_wsl_path(five_tt)),
        "gmwmi": shlex.quote(to_wsl_path(gmwmi)),
        "nodes": shlex.quote(to_wsl_path(nodes)),
        "tracks": shlex.quote(to_wsl_path(tracks)),
        "weights": shlex.quote(to_wsl_path(weights)),
        "connectome": shlex.quote(to_wsl_path(connectome)),
        "assignments": shlex.quote(to_wsl_path(assignments)),
    }
    commands = [
        {
            "step": f"tckgen_iFOD2_ACT_{streamlines}",
            "result": run_wsl(
                f"tckgen {p['wmfod']} {p['tracks']} -algorithm iFOD2 -act {p['5tt']} -backtrack -crop_at_gmwmi -seed_gmwmi {p['gmwmi']} -select {streamlines} -maxlength 250 -cutoff 0.01 -force -nthreads 1",
                timeout_seconds=7200,
            ),
        },
        {
            "step": f"tcksift2_{streamlines}",
            "result": run_wsl(
                f"tcksift2 {p['tracks']} {p['wmfod']} {p['weights']} -act {p['5tt']} -force -nthreads 4",
                timeout_seconds=7200,
            ),
        },
        {
            "step": f"tck2connectome_fsdefault84_{streamlines}",
            "result": run_wsl(
                f"tck2connectome {p['tracks']} {p['nodes']} {p['connectome']} -tck_weights_in {p['weights']} -symmetric -zero_diagonal -out_assignment {p['assignments']} -force",
                timeout_seconds=1800,
            ),
        },
    ]
    for command in commands:
        if command["result"]["returncode"] != 0:
            return {
                "subject": subject,
                "streamlines": streamlines,
                "status": "FAILED_STREAMLINE_SENSITIVITY",
                "failed_step": command["step"],
                "commands": commands,
            }
    stderr = "\n".join(command["result"].get("stderr_tail", "") for command in commands)
    load_bearing_warning = any(
        marker in stderr
        for marker in [
            "do not have any streamlines assigned",
            "poor parcellation image preparation",
            "poor registration",
        ]
    )
    return {
        "subject": subject,
        "streamlines": streamlines,
        "status": "PASS_STREAMLINE_SENSITIVITY",
        "connectome": str(connectome),
        "connectome_qc": connectome_qc(connectome, assignments),
        "load_bearing_tck2connectome_warning": load_bearing_warning,
        "commands": commands,
        "allowed_claim": "This sensitivity tests whether the 100307 labelconvert warning is partly a low-streamline-count smoke artifact.",
        "forbidden_claims": [
            "The final P7 tractography streamline count is fixed.",
            "P7 structural prediction was tested.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", default="100307")
    parser.add_argument("--streamlines", type=int, default=20000)
    args = parser.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    payload = run_subject_sensitivity(args.subject, args.streamlines)
    out = RESULTS / f"p7_e5_{args.subject}_streamline_{args.streamlines}_sensitivity.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not payload["status"].startswith("PASS"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
