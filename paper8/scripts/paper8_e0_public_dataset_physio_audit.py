from __future__ import annotations

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
AUDIT = ROOT / "dataset_audit"
BUCKET = "hcp-openaccess"
PREFIX_ROOT = "HCP_1200"


def read_subjects(limit: int = 20) -> list[str]:
    if not SUBJECT_MANIFEST.exists():
        return []
    rows = list(csv.DictReader(SUBJECT_MANIFEST.open("r", encoding="utf-8-sig", newline="")))
    return [row["Subject ID"] for row in rows if row.get("Subject ID")][:limit]


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


def head(client: Any, key: str) -> dict:
    try:
        meta = client.head_object(Bucket=BUCKET, Key=key)
        return {"key": key, "exists": True, "size_bytes": meta.get("ContentLength", 0)}
    except ClientError as exc:
        return {"key": key, "exists": False, "size_bytes": 0, "error": exc.response.get("Error", {}).get("Code")}


def list_prefix(client: Any, prefix: str, max_keys: int = 20) -> list[dict]:
    try:
        resp = client.list_objects_v2(Bucket=BUCKET, Prefix=prefix, MaxKeys=max_keys)
    except ClientError as exc:
        return [{"prefix": prefix, "error": exc.response.get("Error", {}).get("Code")}]
    return [
        {"prefix": prefix, "key": item["Key"], "size_bytes": item.get("Size", 0)}
        for item in resp.get("Contents", [])
    ]


def local_subject_status(subject: str) -> dict:
    base = HCP_DOWNLOADS / subject
    rels = {
        "wm_lr_dtseries": Path("MNINonLinear/Results/tfMRI_WM_LR/tfMRI_WM_LR_Atlas_MSMAll.dtseries.nii"),
        "wm_rl_dtseries": Path("MNINonLinear/Results/tfMRI_WM_RL/tfMRI_WM_RL_Atlas_MSMAll.dtseries.nii"),
        "wm_lr_motion": Path("MNINonLinear/Results/tfMRI_WM_LR/Movement_Regressors.txt"),
        "wm_rl_motion": Path("MNINonLinear/Results/tfMRI_WM_RL/Movement_Regressors.txt"),
        "wm_lr_physio": Path("MNINonLinear/Results/tfMRI_WM_LR/tfMRI_WM_LR_Physio_log.txt"),
        "wm_rl_physio": Path("MNINonLinear/Results/tfMRI_WM_RL/tfMRI_WM_RL_Physio_log.txt"),
        "t1w_wmparc": Path("T1w/wmparc.nii.gz"),
        "t1w_aparc_aseg": Path("T1w/aparc+aseg.nii.gz"),
    }
    row = {"subject": subject}
    for name, rel in rels.items():
        path = base / rel
        row[name] = path.exists()
        row[f"{name}_bytes"] = path.stat().st_size if path.exists() else 0
    row["local_ready_without_physio"] = all(row[k] for k in ["wm_lr_dtseries", "wm_rl_dtseries", "wm_lr_motion", "wm_rl_motion"])
    row["local_ready_with_physio"] = row["local_ready_without_physio"] and row["wm_lr_physio"] and row["wm_rl_physio"]
    return row


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    AUDIT.mkdir(parents=True, exist_ok=True)
    subjects = read_subjects(limit=20)
    local_rows = [local_subject_status(s) for s in subjects]

    candidate_rows = [
        {
            "dataset": "HCP-YA 2025",
            "role": "P8-A primary candidate",
            "task_fmri": True,
            "event_structure": "WM task EV/TAB files support 0-back/2-back block/event timing",
            "motion_availability": "Movement_Regressors.txt available in current local cache for downloaded subjects",
            "respiration_availability": "HCP documentation describes .resp / Physio_log records; remote key availability audited here",
            "cardiac_availability": "HCP documentation describes pulse oximetry / .puls records; remote key availability audited here",
            "wm_csf_availability": "T1w wmparc/aparc+aseg available for downloaded subjects",
            "download_feasibility": "authorized HCP/BALSA S3 credentials required",
        },
        {
            "dataset": "OpenNeuro ds006642 Naturalistic Neuroimaging Database 3T+",
            "role": "P8-B candidate",
            "task_fmri": True,
            "event_structure": "movie and functional mapping tasks; transition mapping less direct",
            "motion_availability": "derivative-dependent",
            "respiration_availability": "not confirmed in current package",
            "cardiac_availability": "pulse oximetry mentioned in public metadata",
            "wm_csf_availability": "derivative-dependent",
            "download_feasibility": "public OpenNeuro, but not selected for primary E1 without direct stage transitions",
        },
    ]

    remote_rows: list[dict] = []
    client = read_client()
    if client:
        for subject in subjects:
            for run in ["tfMRI_WM_LR", "tfMRI_WM_RL"]:
                preproc_key = f"{PREFIX_ROOT}/{subject}/MNINonLinear/Results/{run}/{run}_Physio_log.txt"
                remote_rows.append({"subject": subject, "run": run, "kind": "preprocessed_physio_log", **head(client, preproc_key)})
                prefix = f"{PREFIX_ROOT}/{subject}/unprocessed/3T/{run}/LINKED_DATA/PHYSIO/"
                for item in list_prefix(client, prefix, max_keys=20):
                    remote_rows.append({"subject": subject, "run": run, "kind": "unprocessed_physio_prefix", **item})

    found_preprocessed = [row for row in remote_rows if row.get("kind") == "preprocessed_physio_log" and row.get("exists")]
    found_unprocessed = [row for row in remote_rows if row.get("kind") == "unprocessed_physio_prefix" and row.get("key")]
    local_physio_ready = [row for row in local_rows if row["local_ready_with_physio"]]
    local_motion_ready = [row for row in local_rows if row["local_ready_without_physio"]]

    status = (
        "PASS_E0_REMOTE_PHYSIO_FOUND"
        if found_preprocessed or found_unprocessed
        else "BLOCKED_P8_PHYSIO_FILES_NOT_FOUND_IN_AUDITED_REMOTE_KEYS"
    )

    payload = {
        "experiment": "P8-E0-public-dataset-physio-audit",
        "status": status,
        "selected_primary_candidate": "HCP-YA 2025",
        "subjects_audited": subjects,
        "n_local_motion_ready_subjects_in_preview": len(local_motion_ready),
        "n_local_physio_ready_subjects_in_preview": len(local_physio_ready),
        "n_remote_preprocessed_physio_logs_found": len(found_preprocessed),
        "n_remote_unprocessed_physio_objects_found": len(found_unprocessed),
        "remote_audit_used_credentials": client is not None,
        "secrets_printed": False,
        "claim_boundary": "E0 only audits measured-physiology availability. It does not test P3/P4 physiological robustness.",
        "blockers": [] if status.startswith("PASS") else ["No HCP WM physio objects were found in the audited remote key patterns."],
        "source_notes": [
            "HCP documentation states Siemens PMU produces .ext, .puls, .resp, and unused .ecg logs for fMRI/dMRI scans.",
            "HCP documentation states Movement_Regressors.txt contains six rigid-body parameters and temporal derivatives.",
        ],
    }

    write_csv(AUDIT / "p8_e0_dataset_candidates.csv", candidate_rows)
    write_csv(AUDIT / "p8_e0_local_hcp_physio_motion_audit.csv", local_rows)
    write_csv(AUDIT / "p8_e0_remote_hcp_physio_key_audit.csv", remote_rows)
    (RESULTS / "p8_e0_public_dataset_physio_audit.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not status.startswith("PASS"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
