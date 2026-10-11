from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.request
from pathlib import Path

os.environ.setdefault("MNE_LOGGING_LEVEL", "WARNING")

import mne
import numpy as np
from scipy.signal import welch


ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / "data_openneuro" / "downloads" / "ds004117"
RESULTS = ROOT / "results"
FEATURES = ROOT / "features" / "ds004117_signal_smoke"
S3_ROOT = "https://s3.amazonaws.com/openneuro.org/ds004117"

BANDS = {
    "theta_4_8": (4.0, 8.0),
    "alpha_8_12": (8.0, 12.0),
    "beta_13_30": (13.0, 30.0),
    "low_gamma_30_55": (30.0, 55.0),
}


def download_file(rel_path: str, timeout: int) -> Path:
    local_path = DOWNLOADS / rel_path
    local_path.parent.mkdir(parents=True, exist_ok=True)
    if local_path.exists() and local_path.stat().st_size > 0:
        return local_path
    url = f"{S3_ROOT}/{rel_path}"
    request = urllib.request.Request(url, headers={"User-Agent": "NSI-Paper6-E3-Smoke/0.1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = response.read()
    local_path.write_bytes(data)
    return local_path


def read_transition_windows(event_file: str, limit_windows: int | None) -> list[dict]:
    manifest = RESULTS / "e2_ds004117_transition_windows.csv"
    rows = []
    with manifest.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["event_file"] == event_file:
                rows.append(row)
    if limit_windows:
        rows = rows[:limit_windows]
    return rows


def safe_segment(raw: mne.io.BaseRaw, start_s: float, end_s: float) -> np.ndarray | None:
    sfreq = float(raw.info["sfreq"])
    start = int(round(start_s * sfreq))
    stop = int(round(end_s * sfreq))
    if start < 0 or stop <= start or stop > raw.n_times:
        return None
    data = raw.get_data(start=start, stop=stop, reject_by_annotation="omit")
    if data.size == 0 or not np.isfinite(data).all():
        return None
    return data


def bandpower(segment: np.ndarray, sfreq: float) -> dict[str, float]:
    nperseg = min(segment.shape[1], int(round(sfreq)))
    freqs, psd = welch(segment, fs=sfreq, nperseg=max(8, nperseg), axis=1)
    out = {}
    for name, (lo, hi) in BANDS.items():
        mask = (freqs >= lo) & (freqs < hi)
        if not np.any(mask):
            out[name] = float("nan")
        else:
            out[name] = float(np.log10(np.mean(psd[:, mask]) + 1e-20))
    return out


def extract_features(raw_path: Path, event_file: str, windows: list[dict]) -> tuple[list[dict], dict]:
    raw = mne.io.read_raw_eeglab(raw_path, preload=True, verbose="ERROR")
    raw.pick_types(eeg=True, exclude=[])
    raw.filter(l_freq=1.0, h_freq=55.0, verbose="ERROR")
    sfreq = float(raw.info["sfreq"])
    rows = []
    skipped = 0
    for idx, window in enumerate(windows):
        pre = safe_segment(raw, float(window["pre_start_s"]), float(window["pre_end_s"]))
        post = safe_segment(raw, float(window["post_start_s"]), float(window["post_end_s"]))
        if pre is None or post is None:
            skipped += 1
            continue
        pre_power = bandpower(pre, sfreq)
        post_power = bandpower(post, sfreq)
        row = {
            "window_index": idx,
            "subject": window["subject"],
            "session": window["session"],
            "run": window["run"],
            "trial": window["trial"],
            "transition": window["transition"],
            "memory_cond": window["memory_cond"],
            "boundary_onset_s": float(window["boundary_onset_s"]),
        }
        for band in BANDS:
            row[f"pre_{band}"] = pre_power[band]
            row[f"post_{band}"] = post_power[band]
            row[f"delta_{band}"] = post_power[band] - pre_power[band]
        rows.append(row)
    meta = {
        "sfreq": sfreq,
        "n_channels": len(raw.ch_names),
        "n_times": int(raw.n_times),
        "duration_s": float(raw.n_times / sfreq),
        "windows_requested": len(windows),
        "windows_extracted": len(rows),
        "windows_skipped": skipped,
    }
    return rows, meta


def write_feature_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Paper 6 E3 ds004117 one-run EEG signal extraction smoke.")
    parser.add_argument("--event-file", default="sub-001/ses-01/eeg/sub-001_ses-01_task-WorkingMemory_run-1_events.tsv")
    parser.add_argument("--limit-windows", type=int, default=None)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    stem = args.event_file.replace("_events.tsv", "")
    required = [
        args.event_file,
        f"{stem}_eeg.set",
        f"{stem}_eeg.fdt",
        f"{stem}_eeg.json",
        f"{stem}_channels.tsv",
    ]
    downloaded = []
    for rel_path in required:
        path = download_file(rel_path, args.timeout)
        downloaded.append({"path": str(path.relative_to(ROOT.parent)), "size_bytes": path.stat().st_size})
        print(f"downloaded/ready {rel_path}", flush=True)

    windows = read_transition_windows(args.event_file, args.limit_windows)
    if not windows:
        raise SystemExit(f"No transition windows found for {args.event_file}; run build_p6_ds004117_transition_windows.py first.")

    feature_rows, signal_meta = extract_features(DOWNLOADS / f"{stem}_eeg.set", args.event_file, windows)
    FEATURES.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    feature_csv = FEATURES / "sub-001_run-1_bandpower_transition_smoke.csv"
    write_feature_csv(feature_rows, feature_csv)
    payload = {
        "experiment": "P6-E3-ds004117-signal-smoke",
        "status": "PASS_SIGNAL_SMOKE" if feature_rows else "FAIL_NO_FEATURES_EXTRACTED",
        "dataset": "ds004117",
        "event_file": args.event_file,
        "downloaded_files": downloaded,
        "signal_meta": signal_meta,
        "feature_file": str(feature_csv.relative_to(ROOT.parent)),
        "feature_family": "1-second pre/post transition log bandpower deltas",
        "claim_audit": {
            "can_claim_fast_dynamics_existence": False,
            "can_claim_transition_specificity": False,
            "can_claim_nap_exists": False,
            "allowed_current_claim": "A one-run E3 signal extraction smoke succeeded; inferential fast-dynamics tests have not been run.",
        },
    }
    (RESULTS / "e3_ds004117_signal_smoke.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "PASS_SIGNAL_SMOKE" else 2


if __name__ == "__main__":
    sys.exit(main())
