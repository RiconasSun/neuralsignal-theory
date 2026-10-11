from __future__ import annotations

import argparse
import csv
import gzip
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from statistics import mean, pstdev

import nibabel as nib
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
AUDIT = ROOT / "dataset_audit"
STATE = ROOT / "state_extraction" / "ds005795_physio_extension"
DATA = ROOT / "data_ds005795_smoke"
SELECTED = AUDIT / "p8_final_extension_ds005795_selected_files.csv"
DATASET = "ds005795"
TAG = "1.0.0"
TASK = "learning"
DEFAULT_SUBJECTS = [f"sub-{idx:02d}" for idx in range(1, 11)]


def candidate_urls(path: str) -> list[str]:
    encoded = urllib.parse.quote(path, safe="/")
    return [
        f"https://openneuro.org/crn/datasets/{DATASET}/snapshots/{TAG}/files/{encoded}",
        f"https://s3.amazonaws.com/openneuro.org/{DATASET}/{path}",
        f"https://s3.amazonaws.com/openneuro.org/{DATASET}/{TAG}/{path}",
    ]


def download(path: str, target: Path) -> dict:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size > 0:
        return {"path": path, "target": str(target), "status": "exists", "size_bytes": target.stat().st_size}
    errors = []
    for url in candidate_urls(path):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "nsi-paper8-ds005795-streaming/0.1"})
            with urllib.request.urlopen(req, timeout=180) as resp:
                target.write_bytes(resp.read())
            return {
                "path": path,
                "target": str(target),
                "status": "downloaded",
                "size_bytes": target.stat().st_size,
                "url_used": url,
            }
        except (urllib.error.URLError, TimeoutError) as exc:
            errors.append({"url": url, "error": f"{type(exc).__name__}: {str(exc)[:200]}"})
    return {"path": path, "target": str(target), "status": "failed", "size_bytes": 0, "errors": errors}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_physio(path: Path) -> list[tuple[float, float, float]]:
    rows = []
    with gzip.open(path, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 3:
                try:
                    rows.append((float(parts[0]), float(parts[1]), float(parts[2])))
                except ValueError:
                    continue
    return rows


def read_events(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def summarize(values: list[float]) -> tuple[float, float, float, float]:
    if not values:
        return 0.0, 0.0, 0.0, 0.0
    return mean(values), pstdev(values) if len(values) > 1 else 0.0, min(values), max(values)


def build_physio_features(subject: str, task: str) -> Path:
    STATE.mkdir(parents=True, exist_ok=True)
    func = DATA / subject / "func"
    physio_path = func / f"{subject}_task-{task}_physio.tsv.gz"
    events_path = func / f"{subject}_task-{task}_events.tsv"
    bold_json = read_json(func / f"{subject}_task-{task}_bold.json")
    tr = float(bold_json.get("RepetitionTime", 2.0))
    physio = read_physio(physio_path)
    events = read_events(events_path)
    duration = physio[-1][0] - physio[0][0] if physio else 0.0
    n_tr = int(duration // tr)
    rows = []
    for idx in range(n_tr):
        start = idx * tr
        end = start + tr
        chunk = [row for row in physio if start <= row[0] < end]
        cardiac = [row[1] for row in chunk]
        resp = [row[2] for row in chunk]
        c_mean, c_sd, c_min, c_max = summarize(cardiac)
        r_mean, r_sd, r_min, r_max = summarize(resp)
        event_types = [
            row.get("trial_type", "")
            for row in events
            if row.get("onset") not in {"", "n/a"} and start <= float(row["onset"]) < end
        ]
        rows.append({
            "subject": subject,
            "task": task,
            "tr_index": idx,
            "time_start": start,
            "time_end": end,
            "n_physio_samples": len(chunk),
            "cardiac_mean": c_mean,
            "cardiac_sd": c_sd,
            "cardiac_min": c_min,
            "cardiac_max": c_max,
            "respiratory_mean": r_mean,
            "respiratory_sd": r_sd,
            "respiratory_min": r_min,
            "respiratory_max": r_max,
            "n_events": len(event_types),
            "event_types": "|".join(sorted(set(event_types))),
        })
    out_csv = STATE / f"p8_ds005795_{subject.replace('-', '')}_{task}_physio_tr_features.csv"
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)
    return out_csv


def read_feature_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def make_design(rows: list[dict], include_physio: bool, include_metadata: bool) -> np.ndarray:
    numeric = []
    for row in rows:
        values = [float(row["tr_index"]), float(row["n_events"])]
        if include_physio:
            values.extend([
                float(row["cardiac_mean"]),
                float(row["cardiac_sd"]),
                float(row["respiratory_mean"]),
                float(row["respiratory_sd"]),
            ])
        numeric.append(values)
    x_num = np.asarray(numeric, dtype=float)
    if not include_metadata:
        return x_num
    labels = np.asarray([[row["event_types"] or "none"] for row in rows], dtype=object)
    enc = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    x_cat = enc.fit_transform(labels)
    return np.hstack([x_num, x_cat])


def fit_eval(x: np.ndarray, y: np.ndarray) -> dict:
    n = len(y)
    split = max(10, int(n * 0.7))
    x_train, x_test = x[:split], x[split:]
    y_train, y_test = y[:split], y[split:]
    scaler = StandardScaler()
    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)
    model = Ridge(alpha=10.0)
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    return {
        "train_rows": int(len(y_train)),
        "test_rows": int(len(y_test)),
        "mse": float(mean_squared_error(y_test, pred)),
        "r2": float(r2_score(y_test, pred)),
    }


def required_paths(subject: str, task: str) -> list[str]:
    return [
        "physio.json",
        f"{subject}/func/{subject}_task-{task}_events.tsv",
        f"{subject}/func/{subject}_task-{task}_physio.tsv.gz",
        f"{subject}/func/{subject}_task-{task}_bold.json",
        f"{subject}/func/{subject}_task-{task}_bold.nii.gz",
    ]


def load_available_manifest() -> set[str]:
    if not SELECTED.exists():
        raise SystemExit(f"Missing selected file manifest: {SELECTED}")
    with SELECTED.open("r", encoding="utf-8", newline="") as f:
        return {row["path"] for row in csv.DictReader(f)}


def run_subject(subject: str, task: str, keep_bold: bool, available: set[str]) -> dict:
    downloads = []
    missing = []
    for rel_path in required_paths(subject, task):
        if rel_path not in available:
            missing.append(rel_path)
            continue
        downloads.append(download(rel_path, DATA / rel_path))
    if missing or any(row["status"] not in {"downloaded", "exists"} for row in downloads):
        return {"subject": subject, "status": "failed_download_or_manifest", "missing": missing, "downloads": downloads}

    bold_path = DATA / subject / "func" / f"{subject}_task-{task}_bold.nii.gz"
    feature_path = build_physio_features(subject, task)
    bold_json = read_json(DATA / subject / "func" / f"{subject}_task-{task}_bold.json")
    img = nib.load(str(bold_path))
    data = np.asanyarray(img.dataobj)
    finite_mask = np.isfinite(data[..., 0])
    brain_mask = finite_mask & (np.nanstd(data, axis=3) > 0)
    global_signal = np.nanmean(data[brain_mask, :], axis=0).astype(float)
    rows = read_feature_rows(feature_path)
    usable = min(len(rows), len(global_signal) - 1)
    rows = rows[:usable]
    y = global_signal[1:usable + 1]
    state_t = global_signal[:usable].reshape(-1, 1)
    trend = np.arange(usable, dtype=float).reshape(-1, 1)
    designs = {
        "N0_state_only": np.hstack([state_t, trend]),
        "N1_state_plus_cardiac_resp": np.hstack([state_t, make_design(rows, include_physio=True, include_metadata=False)]),
        "N2_state_plus_metadata": np.hstack([state_t, make_design(rows, include_physio=False, include_metadata=True)]),
        "N3_state_plus_physio_metadata": np.hstack([state_t, make_design(rows, include_physio=True, include_metadata=True)]),
    }
    results = {name: fit_eval(x, y) for name, x in designs.items()}
    bold_size = bold_path.stat().st_size if bold_path.exists() else 0
    if not keep_bold and bold_path.exists():
        bold_path.unlink()
    return {
        "subject": subject,
        "task": task,
        "status": "PASS_STREAMING_SUBJECT_LADDER",
        "downloads": downloads,
        "bold_size_bytes": bold_size,
        "bold_removed_after_processing": not keep_bold,
        "feature_path": str(feature_path),
        "bold_shape": list(data.shape),
        "repetition_time": bold_json.get("RepetitionTime"),
        "brain_mask_voxels": int(np.sum(brain_mask)),
        "usable_transition_rows": int(usable),
        "results": results,
    }


def aggregate(subject_results: list[dict]) -> dict:
    passed = [row for row in subject_results if row.get("status") == "PASS_STREAMING_SUBJECT_LADDER"]
    if not passed:
        return {}
    out = {}
    for design in sorted(passed[0]["results"]):
        mses = [row["results"][design]["mse"] for row in passed]
        r2s = [row["results"][design]["r2"] for row in passed]
        out[design] = {
            "mean_mse": float(np.mean(mses)),
            "mean_r2": float(np.mean(r2s)),
            "n_subjects": len(passed),
        }
    return out


def deltas(aggregate_results: dict) -> dict:
    n0 = aggregate_results.get("N0_state_only", {})
    return {
        name: {
            "delta_mse_vs_state_only": float(n0.get("mean_mse", np.nan) - values["mean_mse"]),
            "delta_r2_vs_state_only": float(values["mean_r2"] - n0.get("mean_r2", np.nan)),
        }
        for name, values in aggregate_results.items()
        if name != "N0_state_only"
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Streaming ds005795 measured physiology nuisance ladder.")
    parser.add_argument("--subjects", nargs="+", default=DEFAULT_SUBJECTS)
    parser.add_argument("--task", default=TASK)
    parser.add_argument("--keep-bold", action="store_true")
    args = parser.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    available = load_available_manifest()
    subject_results = [run_subject(subject, args.task, args.keep_bold, available) for subject in args.subjects]
    passed = [row for row in subject_results if row.get("status") == "PASS_STREAMING_SUBJECT_LADDER"]
    aggregate_results = aggregate(subject_results)
    payload = {
        "paper": "Paper 8",
        "experiment": "P8-final-extension-ds005795-streaming-nuisance-ladder",
        "status": "PASS_DS005795_STREAMING_NUISANCE_LADDER" if len(passed) == len(args.subjects) else "PARTIAL_DS005795_STREAMING_NUISANCE_LADDER",
        "subjects_requested": args.subjects,
        "subjects_passed": [row["subject"] for row in passed],
        "n_subjects_requested": len(args.subjects),
        "n_subjects_passed": len(passed),
        "task": args.task,
        "aggregate_results": aggregate_results,
        "delta_vs_state_only": deltas(aggregate_results),
        "subject_results": subject_results,
        "claim_boundary": "This is a convergent ds005795 measured-physiology nuisance-ladder analysis over global BOLD signal. It is not a direct HCP working-memory transition replication and does not rescue the failed P8 HCP primary gate.",
    }
    (RESULTS / "p8_final_extension_ds005795_streaming_nuisance_ladder.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    if payload["status"].startswith("PARTIAL"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
