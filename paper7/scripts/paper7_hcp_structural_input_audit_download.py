from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import ClientError


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
P5 = PROJECT / "paper5"
SECRETS = P5 / ".secrets" / "hcp_balsa_s3_credentials.json"
HCP_DATA = P5 / "data_hcp_ya_2025"
HCP_DOWNLOADS = HCP_DATA / "downloads" / "HCP_1200"
SUBJECT_MANIFEST = HCP_DATA / "hcp_ya_2025_100_unrelated_subjects_browser_manifest.csv"
RESULTS = ROOT / "results"
DATA_MANIFEST = ROOT / "data_manifest"
BUCKET = "hcp-openaccess"
PREFIX_ROOT = "HCP_1200"

REQUIRED_RELS = {
    "dwi": Path("T1w/Diffusion/data.nii.gz"),
    "bvals": Path("T1w/Diffusion/bvals"),
    "bvecs": Path("T1w/Diffusion/bvecs"),
    "mask": Path("T1w/Diffusion/nodif_brain_mask.nii.gz"),
    "aparc_aseg": Path("T1w/aparc+aseg.nii.gz"),
    "wmparc": Path("T1w/wmparc.nii.gz"),
    "wm_lr_dtseries": Path("MNINonLinear/Results/tfMRI_WM_LR/tfMRI_WM_LR_Atlas_MSMAll.dtseries.nii"),
    "wm_rl_dtseries": Path("MNINonLinear/Results/tfMRI_WM_RL/tfMRI_WM_RL_Atlas_MSMAll.dtseries.nii"),
    "wm_lr_motion": Path("MNINonLinear/Results/tfMRI_WM_LR/Movement_Regressors.txt"),
    "wm_rl_motion": Path("MNINonLinear/Results/tfMRI_WM_RL/Movement_Regressors.txt"),
}


def read_subjects(limit: int) -> list[str]:
    if not SUBJECT_MANIFEST.exists():
        return []
    rows = list(csv.DictReader(SUBJECT_MANIFEST.open("r", encoding="utf-8-sig", newline="")))
    subjects = [row["Subject ID"] for row in rows if row.get("Subject ID")]
    return subjects[:limit]


def read_client():
    if not SECRETS.exists():
        return None
    payload = json.loads(SECRETS.read_text(encoding="utf-8"))
    if not payload.get("access_key_id") or not payload.get("secret_access_key"):
        return None
    return boto3.client(
        "s3",
        aws_access_key_id=payload["access_key_id"],
        aws_secret_access_key=payload["secret_access_key"],
    )


def remote_head(client: Any, key: str) -> dict:
    try:
        meta = client.head_object(Bucket=BUCKET, Key=key)
        return {"remote_exists": True, "remote_size_bytes": meta.get("ContentLength", 0), "remote_error": ""}
    except ClientError as exc:
        return {
            "remote_exists": False,
            "remote_size_bytes": 0,
            "remote_error": exc.response.get("Error", {}).get("Code", type(exc).__name__),
        }


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def audit_subject(subject: str, client: Any | None, download: bool) -> tuple[list[dict], list[dict]]:
    rows: list[dict] = []
    downloads: list[dict] = []
    for name, rel in REQUIRED_RELS.items():
        local = HCP_DOWNLOADS / subject / rel
        key = f"{PREFIX_ROOT}/{subject}/{rel.as_posix()}"
        local_exists_before = local.exists() and local.stat().st_size > 0
        row = {
            "subject": subject,
            "kind": name,
            "key": key,
            "local_path": str(local),
            "local_exists_before": local_exists_before,
            "local_size_bytes_before": local.stat().st_size if local.exists() else 0,
            "remote_checked": client is not None,
            "download_requested": download,
            "download_status": "not_requested",
        }
        if client:
            row.update(remote_head(client, key))
        if download and client and not local_exists_before and row.get("remote_exists"):
            local.parent.mkdir(parents=True, exist_ok=True)
            try:
                client.download_file(BUCKET, key, str(local))
                row["download_status"] = "downloaded"
                downloads.append({"subject": subject, "kind": name, "key": key, "local_path": str(local), "size_bytes": local.stat().st_size})
            except Exception as exc:  # noqa: BLE001
                row["download_status"] = "error"
                row["download_error"] = f"{type(exc).__name__}: {str(exc)[:240]}"
        elif download and local_exists_before:
            row["download_status"] = "already_local"
        row["local_exists_after"] = local.exists() and local.stat().st_size > 0
        row["local_size_bytes_after"] = local.stat().st_size if local.exists() else 0
        rows.append(row)
    return rows, downloads


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=3, help="Number of locked unrelated HCP subjects to audit.")
    parser.add_argument("--download", action="store_true", help="Download missing required files for audited subjects.")
    args = parser.parse_args()

    RESULTS.mkdir(parents=True, exist_ok=True)
    DATA_MANIFEST.mkdir(parents=True, exist_ok=True)
    subjects = read_subjects(args.limit)
    client = read_client()
    rows: list[dict] = []
    downloads: list[dict] = []
    for subject in subjects:
        subject_rows, subject_downloads = audit_subject(subject, client, args.download)
        rows.extend(subject_rows)
        downloads.extend(subject_downloads)

    ready_subjects = []
    for subject in subjects:
        subject_rows = [row for row in rows if row["subject"] == subject]
        if subject_rows and all(row["local_exists_after"] for row in subject_rows):
            ready_subjects.append(subject)

    status = "PASS_P7_STRUCTURAL_INPUTS_READY_FOR_REQUESTED_LIMIT" if len(ready_subjects) == len(subjects) and subjects else "PARTIAL_P7_STRUCTURAL_INPUTS_READY"
    payload = {
        "paper": "Paper 7",
        "experiment": "P7-HCP-structural-input-audit-download",
        "status": status,
        "subjects_requested": subjects,
        "n_subjects_requested": len(subjects),
        "n_subjects_ready_after": len(ready_subjects),
        "ready_subjects_after": ready_subjects,
        "download_requested": args.download,
        "n_files_downloaded": len(downloads),
        "credentials_available": client is not None,
        "secrets_printed": False,
        "claim_boundary": "This audit/download step only prepares P7 inputs for the current FreeSurfer-5TT high-fidelity route. It does not generate ACT/SIFT2 connectomes and does not test the structural hypothesis.",
        "next_scale_steps": [
            "1 subject ACT/iFOD2/SIFT2 smoke",
            "3 subject smoke",
            "10 subject connectome QC",
            "100 subject frozen structural hypothesis test with thresholds fixed before final holdout",
        ],
    }
    write_csv(DATA_MANIFEST / "p7_hcp_structural_input_audit.csv", rows)
    write_csv(DATA_MANIFEST / "p7_hcp_structural_downloads.csv", downloads)
    (RESULTS / "p7_hcp_structural_input_audit_download.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not subjects or client is None:
        raise SystemExit(2)
    if args.download and status != "PASS_P7_STRUCTURAL_INPUTS_READY_FOR_REQUESTED_LIMIT":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
