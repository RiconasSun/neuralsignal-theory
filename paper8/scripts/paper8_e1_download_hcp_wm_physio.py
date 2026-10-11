from __future__ import annotations

import csv
import json
from pathlib import Path

import boto3


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
P5 = PROJECT / "paper5"
SECRETS = P5 / ".secrets" / "hcp_balsa_s3_credentials.json"
DOWNLOADS = P5 / "data_hcp_ya_2025" / "downloads"
REMOTE_AUDIT = ROOT / "dataset_audit" / "p8_e0_remote_hcp_physio_key_audit.csv"
RESULTS = ROOT / "results"
BUCKET = "hcp-openaccess"


def client():
    payload = json.loads(SECRETS.read_text(encoding="utf-8"))
    return boto3.client(
        "s3",
        aws_access_key_id=payload["access_key_id"],
        aws_secret_access_key=payload["secret_access_key"],
    )


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    if not REMOTE_AUDIT.exists():
        raise SystemExit(f"Missing E0 remote audit: {REMOTE_AUDIT}")
    rows = list(csv.DictReader(REMOTE_AUDIT.open("r", encoding="utf-8", newline="")))
    items = [
        row for row in rows
        if row.get("kind") == "preprocessed_physio_log" and row.get("exists") == "True" and row.get("key")
    ]
    c = client()
    downloaded = []
    errors = []
    for row in items:
        key = row["key"]
        target = DOWNLOADS / key
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            if not target.exists() or target.stat().st_size == 0:
                c.download_file(BUCKET, key, str(target))
                status = "downloaded"
            else:
                status = "exists"
            downloaded.append({
                "subject": row["subject"],
                "run": row["run"],
                "key": key,
                "local_path": str(target),
                "size_bytes": target.stat().st_size,
                "status": status,
            })
        except Exception as exc:  # noqa: BLE001
            errors.append({"key": key, "error": type(exc).__name__, "message": str(exc)[:300]})
    payload = {
        "experiment": "P8-E1-download-hcp-wm-physio",
        "status": "PASS_E1_PHYSIO_DOWNLOADED" if downloaded and not errors else "PARTIAL_OR_FAIL",
        "n_items": len(items),
        "n_downloaded_or_existing": len(downloaded),
        "n_errors": len(errors),
        "downloaded": downloaded,
        "errors": errors,
        "secrets_printed": False,
    }
    (RESULTS / "p8_e1_hcp_wm_physio_download.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    if errors or not downloaded:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
