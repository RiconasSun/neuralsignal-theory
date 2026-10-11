from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import boto3

from paper7_e3_three_subject_final_route_smoke import HCP, RESULTS, read_manifest_subjects, run_subject
from paper7_e5_labelconvert_connectome_qc import run_subject as run_labelconvert_subject


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
SECRETS = PROJECT / "paper5" / ".secrets" / "hcp_balsa_s3_credentials.json"
DATA_MANIFEST = ROOT / "data_manifest"
BUCKET = "hcp-openaccess"
PREFIX_ROOT = "HCP_1200"
FINAL_CONNECTOME_NAME = "connectome_sift2_ext4_msmt_fsdefault84_smoke.csv"


def read_client():
    payload = json.loads(SECRETS.read_text(encoding="utf-8"))
    return boto3.client(
        "s3",
        aws_access_key_id=payload["access_key_id"],
        aws_secret_access_key=payload["secret_access_key"],
    )


def download_dwi_if_missing(client, subject: str) -> dict:
    rel = Path("T1w/Diffusion/data.nii.gz")
    local = HCP / subject / rel
    key = f"{PREFIX_ROOT}/{subject}/{rel.as_posix()}"
    existed_before = local.exists() and local.stat().st_size > 0
    if existed_before:
        return {
            "subject": subject,
            "download_status": "already_local",
            "downloaded_by_this_run": False,
            "local_path": str(local),
            "local_size_bytes": local.stat().st_size,
        }
    ext4_ready = ROOT / "structural_connectomes" / "mrtrix_act_sift2_smoke" / subject / ".ext4_inputs_ready"
    if ext4_ready.exists():
        return {
            "subject": subject,
            "download_status": "reused_ext4_inputs_no_download",
            "downloaded_by_this_run": False,
            "local_path": str(local),
            "local_size_bytes": 0,
            "ext4_ready_marker": str(ext4_ready),
            "claim_boundary": "Recovery path only: raw DWI was already copied into WSL ext4 before local cache cleanup.",
        }
    local.parent.mkdir(parents=True, exist_ok=True)
    client.download_file(BUCKET, key, str(local))
    return {
        "subject": subject,
        "download_status": "downloaded",
        "downloaded_by_this_run": True,
        "key": key,
        "local_path": str(local),
        "local_size_bytes": local.stat().st_size,
    }


def cleanup_subject(subject: str, downloaded_dwi: bool, keep_raw_dwi: bool) -> dict:
    subject_root = ROOT / "structural_connectomes" / "mrtrix_act_sift2_smoke" / subject
    removed = []
    keep = {
        FINAL_CONNECTOME_NAME,
        "assignments_ext4_msmt_fsdefault84.csv",
    }
    large_patterns = [
        "nodes_fsdefault.mif",
        "nodes_fsdefault_dwi.mif",
        "nodes_dwi.mif",
        "dwi.mif",
        ".ext4_dwi_ready",
        "5tt.mif",
        "5tt_dwi.mif",
        "gmwmi_seed.mif",
        "wmfod_ext4.mif",
        "gm_ext4.mif",
        "csf_ext4.mif",
        "tracks_5k_ext4_msmt.tck",
        "sift2_weights_ext4_msmt.txt",
        "connectome_sift2_ext4_msmt_smoke.csv",
        "assignments_ext4_msmt.csv",
    ]
    for name in large_patterns:
        if name in keep:
            continue
        path = subject_root / name
        if path.exists() and path.is_file():
            size = path.stat().st_size
            path.unlink()
            removed.append({"path": str(path), "size_bytes": size})
    dwi = HCP / subject / "T1w" / "Diffusion" / "data.nii.gz"
    if downloaded_dwi and not keep_raw_dwi and dwi.exists():
        size = dwi.stat().st_size
        dwi.unlink()
        removed.append({"path": str(dwi), "size_bytes": size, "reason": "streaming_download_cleanup"})
    return {
        "subject": subject,
        "removed_count": len(removed),
        "removed_bytes": sum(row["size_bytes"] for row in removed),
        "removed": removed,
    }


def final_connectome_exists(subject: str) -> bool:
    path = ROOT / "structural_connectomes" / "mrtrix_act_sift2_smoke" / subject / FINAL_CONNECTOME_NAME
    return path.exists() and path.stat().st_size > 0


def summarize_final_connectome(subject: str) -> dict:
    path = ROOT / "structural_connectomes" / "mrtrix_act_sift2_smoke" / subject / FINAL_CONNECTOME_NAME
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=12, help="Use first N manifest subjects.")
    parser.add_argument("--start-index", type=int, default=10, help="Zero-based index within manifest subject list.")
    parser.add_argument("--count", type=int, default=2, help="Number of subjects to process in this streaming batch.")
    parser.add_argument("--keep-raw-dwi", action="store_true", help="Do not delete DWI downloaded by this run.")
    parser.add_argument("--cleanup-large-intermediates", action="store_true", help="Delete large intermediates after fs_default84 connectome generation.")
    args = parser.parse_args()

    subjects_all = read_manifest_subjects(args.limit)
    subjects = subjects_all[args.start_index : args.start_index + args.count]
    RESULTS.mkdir(parents=True, exist_ok=True)
    DATA_MANIFEST.mkdir(parents=True, exist_ok=True)
    result_path = RESULTS / f"p7_e6_streaming_batch_{args.start_index}_{args.count}.json"
    client = read_client()
    subject_results = []
    for subject in subjects:
        record = {"subject": subject}
        if final_connectome_exists(subject):
            record["status"] = "SKIPPED_FINAL_CONNECTOME_ALREADY_EXISTS"
            record["labelconvert"] = {
                "status": "SKIPPED_FINAL_CONNECTOME_ALREADY_EXISTS",
                "connectome": str(
                    ROOT
                    / "structural_connectomes"
                    / "mrtrix_act_sift2_smoke"
                    / subject
                    / FINAL_CONNECTOME_NAME
                ),
                "connectome_qc": summarize_final_connectome(subject),
                "load_bearing_tck2connectome_warning": None,
            }
        else:
            download = download_dwi_if_missing(client, subject)
            record["download"] = download
            route = run_subject(subject)
            record["route"] = {
                "status": route.get("status"),
                "connectome": route.get("connectome"),
                "connectome_qc": route.get("connectome_qc"),
            }
            if route.get("status") != "PASS_SUBJECT_FINAL_ROUTE_SMOKE":
                record["status"] = "FAILED_FINAL_ROUTE"
                subject_results.append(record)
                break
            label = run_labelconvert_subject(subject)
            record["labelconvert"] = {
                "status": label.get("status"),
                "connectome": label.get("connectome"),
                "connectome_qc": label.get("connectome_qc"),
                "load_bearing_tck2connectome_warning": label.get("load_bearing_tck2connectome_warning"),
            }
            if label.get("status") != "PASS_LABELCONVERT_CONNECTOME_QC":
                record["status"] = "FAILED_LABELCONVERT_ROUTE"
                subject_results.append(record)
                break
            if args.cleanup_large_intermediates:
                record["cleanup"] = cleanup_subject(
                    subject,
                    downloaded_dwi=download.get("downloaded_by_this_run", False),
                    keep_raw_dwi=args.keep_raw_dwi,
                )
            record["status"] = "PASS_STREAMING_SUBJECT_CONNECTOME"
        subject_results.append(record)
        result_path.write_text(
            json.dumps(
                {
                    "paper": "Paper 7",
                    "experiment": "P7-E6-streaming-connectome-batch",
                    "status": "RUNNING_OR_PARTIAL_STREAMING_BATCH",
                    "subjects": subjects,
                    "subject_results": subject_results,
                    "claim_boundary": "Streaming connectome generation only. This does not test the structural prediction hypothesis.",
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    all_pass = len(subject_results) == len(subjects) and all(
        row["status"] in {"PASS_STREAMING_SUBJECT_CONNECTOME", "SKIPPED_FINAL_CONNECTOME_ALREADY_EXISTS"}
        for row in subject_results
    )
    payload = {
        "paper": "Paper 7",
        "experiment": "P7-E6-streaming-connectome-batch",
        "status": "PASS_STREAMING_BATCH" if all_pass else "FAILED_STREAMING_BATCH",
        "subjects": subjects,
        "n_subjects": len(subjects),
        "n_subjects_pass_or_skipped": sum(
            row["status"] in {"PASS_STREAMING_SUBJECT_CONNECTOME", "SKIPPED_FINAL_CONNECTOME_ALREADY_EXISTS"}
            for row in subject_results
        ),
        "cleanup_large_intermediates": args.cleanup_large_intermediates,
        "keep_raw_dwi": args.keep_raw_dwi,
        "subject_results": subject_results,
        "allowed_claim": "The streaming runner can generate final-route and fs_default84 smoke connectomes without retaining every raw DWI locally.",
        "forbidden_claims": [
            "100-subject cohort connectomes are complete.",
            "The structural prediction hypothesis has been tested.",
            "Subject-specific structure improves transition prediction.",
        ],
    }
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    csv_path = DATA_MANIFEST / f"p7_e6_streaming_batch_{args.start_index}_{args.count}.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "subject",
            "status",
            "download_status",
            "route_status",
            "labelconvert_status",
            "labelconvert_warning",
            "nonzero_edges",
            "removed_bytes",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in subject_results:
            label = row.get("labelconvert", {})
            writer.writerow(
                {
                    "subject": row.get("subject"),
                    "status": row.get("status"),
                    "download_status": row.get("download", {}).get("download_status"),
                    "route_status": row.get("route", {}).get("status"),
                    "labelconvert_status": label.get("status"),
                    "labelconvert_warning": label.get("load_bearing_tck2connectome_warning"),
                    "nonzero_edges": label.get("connectome_qc", {}).get("nonzero_edges"),
                    "removed_bytes": row.get("cleanup", {}).get("removed_bytes"),
                }
            )
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not all_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
