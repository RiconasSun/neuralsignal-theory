from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable

import boto3
from botocore.exceptions import ClientError


ROOT = Path(__file__).resolve().parents[1]
SECRETS = ROOT / ".secrets" / "hcp_balsa_s3_credentials.json"
DATA = ROOT / "data_hcp_ya_2025"
DOWNLOADS = DATA / "downloads"
RESULTS = ROOT / "results"
BUCKET = "hcp-openaccess"
PREFIX_ROOT = "HCP_1200"


@dataclass(frozen=True)
class DownloadItem:
    subject: str
    key: str
    role: str
    size_bytes: int | None = None

    @property
    def local_path(self) -> Path:
        return DOWNLOADS / self.key


def read_creds() -> dict[str, str]:
    if not SECRETS.exists():
        raise SystemExit(f"Missing credentials file: {SECRETS}")
    payload = json.loads(SECRETS.read_text(encoding="utf-8"))
    if not payload.get("access_key_id") or not payload.get("secret_access_key"):
        raise SystemExit("Credentials file is present but incomplete.")
    return payload


def s3_client():
    creds = read_creds()
    return boto3.client(
        "s3",
        aws_access_key_id=creds["access_key_id"],
        aws_secret_access_key=creds["secret_access_key"],
    )


def subject_ids(limit: int | None = None) -> list[str]:
    manifest = DATA / "hcp_ya_2025_100_unrelated_subjects_browser_manifest.csv"
    if not manifest.exists():
        raise SystemExit(f"Missing subject manifest: {manifest}")
    rows = list(csv.DictReader(manifest.open("r", encoding="utf-8-sig", newline="")))
    ids = [row["Subject ID"] for row in rows if row.get("Subject ID")]
    return ids[:limit] if limit else ids


def list_keys(client, prefix: str) -> list[dict]:
    paginator = client.get_paginator("list_objects_v2")
    out: list[dict] = []
    for page in paginator.paginate(Bucket=BUCKET, Prefix=prefix):
        out.extend(page.get("Contents", []))
    return out


WM_EV_NAMES = [
    "0bk_body.txt",
    "0bk_cor.txt",
    "0bk_err.txt",
    "0bk_faces.txt",
    "0bk_nlr.txt",
    "0bk_places.txt",
    "0bk_tools.txt",
    "2bk_body.txt",
    "2bk_cor.txt",
    "2bk_err.txt",
    "2bk_faces.txt",
    "2bk_nlr.txt",
    "2bk_places.txt",
    "2bk_tools.txt",
    "all_bk_cor.txt",
    "all_bk_err.txt",
    "Sync.txt",
]


def planned_items_for_subject(client, subject: str, include_dwi_image: bool, fast_template: bool) -> list[DownloadItem]:
    base = f"{PREFIX_ROOT}/{subject}"
    static_keys = [
        (f"{base}/MNINonLinear/Results/tfMRI_WM_LR/tfMRI_WM_LR_Atlas_MSMAll.dtseries.nii", "wm_lr_dtseries"),
        (f"{base}/MNINonLinear/Results/tfMRI_WM_RL/tfMRI_WM_RL_Atlas_MSMAll.dtseries.nii", "wm_rl_dtseries"),
        (f"{base}/MNINonLinear/Results/tfMRI_WM_LR/Movement_Regressors.txt", "wm_lr_motion"),
        (f"{base}/MNINonLinear/Results/tfMRI_WM_RL/Movement_Regressors.txt", "wm_rl_motion"),
        (f"{base}/MNINonLinear/Results/tfMRI_WM_LR/Movement_RelativeRMS.txt", "wm_lr_relative_rms"),
        (f"{base}/MNINonLinear/Results/tfMRI_WM_RL/Movement_RelativeRMS.txt", "wm_rl_relative_rms"),
        (f"{base}/MNINonLinear/Results/tfMRI_WM_LR/WM_run2_TAB.txt", "wm_lr_tab"),
        (f"{base}/MNINonLinear/Results/tfMRI_WM_RL/WM_run1_TAB.txt", "wm_rl_tab"),
        (f"{base}/MNINonLinear/fsaverage_LR32k/{subject}.aparc.32k_fs_LR.dlabel.nii", "aparc_32k_dlabel"),
        (f"{base}/MNINonLinear/fsaverage_LR32k/{subject}.aparc.a2009s.32k_fs_LR.dlabel.nii", "aparc_a2009s_32k_dlabel"),
        (f"{base}/T1w/aparc+aseg.nii.gz", "t1w_aparc_aseg"),
        (f"{base}/T1w/wmparc.nii.gz", "t1w_wmparc"),
        (f"{base}/T1w/Diffusion/bvals", "dwi_bvals"),
        (f"{base}/T1w/Diffusion/bvecs", "dwi_bvecs"),
        (f"{base}/T1w/Diffusion/nodif_brain_mask.nii.gz", "dwi_mask"),
        (f"{base}/T1w/Diffusion.bedpostX/dyads1.nii.gz", "bedpostx_dyads1"),
        (f"{base}/T1w/Diffusion.bedpostX/dyads2.nii.gz", "bedpostx_dyads2"),
        (f"{base}/T1w/Diffusion.bedpostX/dyads3.nii.gz", "bedpostx_dyads3"),
    ]
    if include_dwi_image:
        static_keys.append((f"{base}/T1w/Diffusion/data.nii.gz", "dwi_4d_image"))

    ev_keys: list[tuple[str, str]] = []
    for run in ["tfMRI_WM_LR", "tfMRI_WM_RL"]:
        prefix = f"{base}/MNINonLinear/Results/{run}/EVs/"
        if fast_template:
            ev_keys.extend((f"{prefix}{name}", f"{run.lower()}_ev") for name in WM_EV_NAMES)
        else:
            for obj in list_keys(client, prefix):
                key = obj["Key"]
                if key.endswith(".txt"):
                    ev_keys.append((key, f"{run.lower()}_ev"))

    all_keys = static_keys + ev_keys
    sizes = {}
    if fast_template:
        sizes = {key: None for key, _role in all_keys}
    else:
        for key, _role in all_keys:
            try:
                sizes[key] = client.head_object(Bucket=BUCKET, Key=key)["ContentLength"]
            except ClientError:
                sizes[key] = None
    return [DownloadItem(subject, key, role, sizes[key]) for key, role in all_keys]


def write_manifest(items: Iterable[DownloadItem], name: str) -> Path:
    path = RESULTS / name
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(items)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["subject", "role", "key", "size_bytes", "local_path", "exists"])
        writer.writeheader()
        for item in rows:
            writer.writerow(
                {
                    "subject": item.subject,
                    "role": item.role,
                    "key": item.key,
                    "size_bytes": item.size_bytes,
                    "local_path": str(item.local_path.relative_to(ROOT.parent)),
                    "exists": item.local_path.exists(),
                }
            )
    return path


def _download_one(client, item: DownloadItem) -> tuple[str, int | None, dict | None]:
    item.local_path.parent.mkdir(parents=True, exist_ok=True)
    if item.local_path.exists() and (item.size_bytes is None or item.local_path.stat().st_size == item.size_bytes):
        return "skipped", None, None
    try:
        client.download_file(BUCKET, item.key, str(item.local_path))
        return "downloaded", item.local_path.stat().st_size, None
    except Exception as exc:  # noqa: BLE001
        return "error", None, {"subject": item.subject, "role": item.role, "key": item.key, "error": type(exc).__name__}


def download_items(client, items: list[DownloadItem], max_bytes: int | None = None, workers: int = 1) -> dict:
    downloaded = 0
    skipped = 0
    errors: list[dict] = []
    filtered: list[DownloadItem] = []
    planned = 0
    for item in items:
        if max_bytes is not None and item.size_bytes and planned + item.size_bytes > max_bytes:
            skipped += 1
            continue
        planned += item.size_bytes or 0
        filtered.append(item)

    if workers <= 1:
        for item in filtered:
            status, size, error = _download_one(client, item)
            downloaded += size or 0
            skipped += int(status == "skipped")
            if error:
                errors.append(error)
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_download_one, client, item) for item in filtered]
            for future in as_completed(futures):
                status, size, error = future.result()
                downloaded += size or 0
                skipped += int(status == "skipped")
                if error:
                    errors.append(error)
    return {"downloaded_bytes": downloaded, "skipped_count": skipped, "error_count": len(errors), "errors": errors[:20]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Download authorized HCP-YA 2025 files from BALSA AWS S3.")
    parser.add_argument("--subjects", type=int, default=1)
    parser.add_argument("--include-dwi-image", action="store_true", help="Download full DWI 4D image; large.")
    parser.add_argument("--fast-template", action="store_true", help="Use fixed HCP WM file templates and skip slow remote listing/head checks.")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--max-bytes", type=int, default=None)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()

    client = s3_client()
    selected = subject_ids(args.subjects)
    items: list[DownloadItem] = []
    for subject in selected:
        items.extend(planned_items_for_subject(client, subject, args.include_dwi_image, args.fast_template))
    total_known = sum(item.size_bytes or 0 for item in items)
    manifest_path = write_manifest(items, "hcp_s3_download_manifest.csv")

    summary = {
        "status": "PLANNED",
        "bucket": BUCKET,
        "prefix_root": PREFIX_ROOT,
        "subjects": selected,
        "n_items": len(items),
        "total_known_bytes": total_known,
        "manifest": str(manifest_path.relative_to(ROOT.parent)),
        "include_dwi_image": args.include_dwi_image,
        "fast_template": args.fast_template,
        "secrets_printed": False,
    }
    if args.download:
        result = download_items(client, items, args.max_bytes, max(1, args.workers))
        summary.update(result)
        summary["status"] = "DOWNLOADED_WITH_ERRORS" if result["error_count"] else "DOWNLOADED"
    (RESULTS / "hcp_s3_download_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
