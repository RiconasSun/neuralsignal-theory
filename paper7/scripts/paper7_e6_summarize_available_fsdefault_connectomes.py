from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONNECTOME_ROOT = ROOT / "structural_connectomes" / "mrtrix_act_sift2_smoke"
RESULTS = ROOT / "results"
DATA_MANIFEST = ROOT / "data_manifest"
FINAL_CONNECTOME = "connectome_sift2_ext4_msmt_fsdefault84_smoke.csv"


def summarize_matrix(path: Path) -> dict:
    if not path.exists():
        return {"exists": False}
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append([float(x) for x in line.split(",")])
    values = [x for row in rows for x in row]
    return {
        "exists": True,
        "rows": len(rows),
        "columns": len(rows[0]) if rows else 0,
        "bytes": path.stat().st_size,
        "nonzero_edges": sum(1 for x in values if abs(x) > 0),
        "total_weight": sum(values),
        "max_weight": max(values) if values else None,
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    DATA_MANIFEST.mkdir(parents=True, exist_ok=True)
    records = []
    for subject_dir in sorted(p for p in CONNECTOME_ROOT.iterdir() if p.is_dir()):
        subject = subject_dir.name
        path = subject_dir / FINAL_CONNECTOME
        qc = summarize_matrix(path)
        if qc["exists"]:
            records.append({"subject": subject, **qc})

    nonzero = [row["nonzero_edges"] for row in records]
    status = "PASS_AVAILABLE_FSDEFAULT_CONNECTOME_SUMMARY" if records else "NO_FSDEFAULT_CONNECTOMES_FOUND"
    payload = {
        "paper": "Paper 7",
        "experiment": "P7-E6-available-fsdefault-connectome-summary",
        "status": status,
        "n_subjects_with_fsdefault_connectome": len(records),
        "subjects": [row["subject"] for row in records],
        "nonzero_edges_min": min(nonzero) if nonzero else None,
        "nonzero_edges_max": max(nonzero) if nonzero else None,
        "nonzero_edges_mean": sum(nonzero) / len(nonzero) if nonzero else None,
        "records": records,
        "claim_boundary": "Available connectome inventory only. This does not test the structural hypothesis.",
    }
    (RESULTS / "p7_e6_available_fsdefault_connectome_summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    csv_path = DATA_MANIFEST / "p7_e6_available_fsdefault_connectome_summary.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["subject", "rows", "columns", "bytes", "nonzero_edges", "total_weight", "max_weight"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in records:
            writer.writerow({key: row.get(key) for key in fieldnames})
    print(json.dumps(payload, indent=2, sort_keys=True))
    if status != "PASS_AVAILABLE_FSDEFAULT_CONNECTOME_SUMMARY":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
