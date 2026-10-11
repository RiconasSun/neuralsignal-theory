from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DATA_MANIFEST = ROOT / "data_manifest"
SOURCE = RESULTS / "p7_e4_ten_subject_connectome_qc.json"
CSV_OUT = DATA_MANIFEST / "p7_e4_ten_subject_connectome_qc_summary.csv"
JSON_OUT = RESULTS / "p7_e4_ten_subject_connectome_qc_summary.json"


def warning_types(subject_result: dict) -> list[str]:
    types: list[str] = []
    for warning in subject_result.get("qc_warnings", []):
        tail = warning.get("stderr_tail", "")
        if "do not have any streamlines assigned" in tail:
            types.append("nodes_without_streamlines")
        elif "poor parcellation image preparation" in tail:
            types.append("parcellation_or_registration_warning")
        elif "existing output files will be overwritten" in tail:
            types.append("overwrite_warning")
        else:
            types.append(warning.get("marker", "warning"))
    return sorted(set(types))


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    DATA_MANIFEST.mkdir(parents=True, exist_ok=True)
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = []
    for subject_result in payload.get("subject_results", []):
        qc = subject_result.get("connectome_qc", {})
        rows.append(
            {
                "subject": subject_result.get("subject"),
                "status": subject_result.get("status"),
                "connectome": subject_result.get("connectome"),
                "connectome_bytes": qc.get("bytes", subject_result.get("connectome_bytes")),
                "rows": qc.get("rows"),
                "columns": qc.get("columns"),
                "nonzero_edges": qc.get("nonzero_edges"),
                "total_weight": qc.get("total_weight"),
                "max_weight": qc.get("max_weight"),
                "assignments_rows": qc.get("assignments_rows"),
                "warning_types": ";".join(warning_types(subject_result)),
                "n_qc_warnings_raw": len(subject_result.get("qc_warnings", [])),
            }
        )

    fieldnames = [
        "subject",
        "status",
        "connectome",
        "connectome_bytes",
        "rows",
        "columns",
        "nonzero_edges",
        "total_weight",
        "max_weight",
        "assignments_rows",
        "warning_types",
        "n_qc_warnings_raw",
    ]
    with CSV_OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    pass_rows = [row for row in rows if row["status"] == "PASS_SUBJECT_FINAL_ROUTE_SMOKE"]
    nonzero_edges = [int(row["nonzero_edges"]) for row in pass_rows if row["nonzero_edges"] is not None]
    total_weights = [float(row["total_weight"]) for row in pass_rows if row["total_weight"] is not None]
    summary = {
        "paper": "Paper 7",
        "experiment": "P7-E4-10-subject-connectome-QC-summary",
        "source": str(SOURCE),
        "status": "PASS_10_SUBJECT_QC_SUMMARY_WRITTEN" if len(pass_rows) == 10 else "PARTIAL_10_SUBJECT_QC_SUMMARY",
        "n_subjects": len(rows),
        "n_subjects_pass": len(pass_rows),
        "subjects": [row["subject"] for row in rows],
        "connectome_matrix_shape": "2035x2035" if all(row["rows"] == 2035 and row["columns"] == 2035 for row in pass_rows) else "MIXED_OR_UNKNOWN",
        "assignments_rows_all_5001": all(row["assignments_rows"] == 5001 for row in pass_rows),
        "nonzero_edges_min": min(nonzero_edges) if nonzero_edges else None,
        "nonzero_edges_max": max(nonzero_edges) if nonzero_edges else None,
        "nonzero_edges_mean": sum(nonzero_edges) / len(nonzero_edges) if nonzero_edges else None,
        "total_weight_min": min(total_weights) if total_weights else None,
        "total_weight_max": max(total_weights) if total_weights else None,
        "total_weight_mean": sum(total_weights) / len(total_weights) if total_weights else None,
        "qc_warning_boundary": "Warnings include harmless overwrite warnings and load-bearing tck2connectome node-assignment/parcellation warnings. The latter must be fixed before 100-subject structural prediction.",
        "allowed_claim": "Ten HCP subjects completed the current ACT/iFOD2/SIFT2 engineering QC smoke.",
        "forbidden_claims": [
            "The connectome atlas is final.",
            "The P7 structural hypothesis has been tested.",
            "Subject-specific structure improves brain-state transition prediction.",
        ],
        "csv": str(CSV_OUT),
    }
    JSON_OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
