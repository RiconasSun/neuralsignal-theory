from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SUBJECT = "100307"
OUT_ROOT = ROOT / "structural_connectomes" / "mrtrix_act_sift2_smoke" / SUBJECT


def file_info(name: str) -> dict:
    path = OUT_ROOT / name
    return {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }


def connectome_summary(path: Path) -> dict:
    if not path.exists():
        return {"exists": False}
    values = []
    n_rows = 0
    n_cols = 0
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            n_rows += 1
            n_cols = max(n_cols, len(row))
            for value in row:
                try:
                    values.append(float(value))
                except ValueError:
                    pass
    nonzero = sum(1 for value in values if value != 0.0)
    return {
        "exists": True,
        "n_rows": n_rows,
        "n_cols": n_cols,
        "n_values": len(values),
        "n_nonzero_values": nonzero,
        "nonzero_fraction": nonzero / len(values) if values else 0.0,
        "sum_weights": sum(values),
        "max_weight": max(values) if values else 0.0,
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    files = {
        "msmt_wmfod_ext4": file_info("wmfod_ext4.mif"),
        "tracks": file_info("tracks_5k_ext4_msmt.tck"),
        "sift2_weights": file_info("sift2_weights_ext4_msmt.txt"),
        "connectome": file_info("connectome_sift2_ext4_msmt_smoke.csv"),
        "assignments": file_info("assignments_ext4_msmt.csv"),
        "five_tissue": file_info("5tt_dwi.mif"),
        "gmwmi_seed": file_info("gmwmi_seed.mif"),
        "nodes": file_info("nodes_dwi.mif"),
    }
    connectome = OUT_ROOT / "connectome_sift2_ext4_msmt_smoke.csv"
    summary = connectome_summary(connectome)
    pass_gate = (
        files["msmt_wmfod_ext4"]["size_bytes"] > 100_000_000
        and files["tracks"]["size_bytes"] > 100_000
        and files["sift2_weights"]["size_bytes"] > 0
        and files["connectome"]["size_bytes"] > 0
        and summary.get("n_nonzero_values", 0) > 0
    )
    payload = {
        "paper": "Paper 7",
        "experiment": "P7-final-route-single-subject-ACT-iFOD2-SIFT2-smoke",
        "status": "PASS_SINGLE_SUBJECT_FINAL_ROUTE_SMOKE" if pass_gate else "FAILED_SINGLE_SUBJECT_FINAL_ROUTE_SMOKE",
        "subject": SUBJECT,
        "files": files,
        "connectome_summary": summary,
        "protocol_deviation": "This is a 5,000-streamline smoke test using FreeSurfer-5TT and ext4-generated MSMT-CSD FOD. It is not the planned full-streamline cohort connectome generation.",
        "qc_warning": "Raw aparc+aseg labels were used for the smoke connectome; tck2connectome reported missing/unassigned nodes. A final cohort run still needs a frozen atlas/label conversion QC gate.",
        "allowed_claim": "A one-subject final-route ACT/iFOD2/SIFT2 smoke connectome can be generated from nonzero MSMT-CSD FOD for HCP 100307.",
        "forbidden_claims": [
            "P7 cohort connectomes generated",
            "P7 structural hypothesis tested",
            "subject-specific structural grounding supported",
            "CWP validated",
            "NAP structurally grounded",
        ],
        "next_action": "Scale only to a 3-subject smoke after downloading complete HCP structural inputs and freezing atlas/label-conversion QC handling.",
    }
    out = RESULTS / "p7_final_route_single_subject_smoke.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not pass_gate:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
