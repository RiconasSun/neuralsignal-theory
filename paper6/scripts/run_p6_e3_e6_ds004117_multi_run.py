from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.request
import warnings
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("MNE_LOGGING_LEVEL", "WARNING")
warnings.filterwarnings("ignore", message="Complex objects.*")

import mne
import numpy as np
from scipy.signal import welch
from scipy.stats import binomtest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / "data_openneuro" / "downloads" / "ds004117"
RESULTS = ROOT / "results"
FEATURES = ROOT / "features" / "ds004117_multi_run"
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
    request = urllib.request.Request(f"{S3_ROOT}/{rel_path}", headers={"User-Agent": "NSI-Paper6-E3E6/0.1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        local_path.write_bytes(response.read())
    return local_path


def load_windows(max_runs: int | None, subjects: list[str] | None) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    with (RESULTS / "e2_ds004117_transition_windows.csv").open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if subjects and row["subject"] not in subjects:
                continue
            grouped[row["event_file"]].append(row)
    selected = dict(sorted(grouped.items()))
    if max_runs:
        selected = dict(list(selected.items())[:max_runs])
    return selected


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


def bandpower_vector(segment: np.ndarray, sfreq: float) -> np.ndarray:
    nperseg = min(segment.shape[1], int(round(sfreq)))
    freqs, psd = welch(segment, fs=sfreq, nperseg=max(8, nperseg), axis=1)
    values = []
    for lo, hi in BANDS.values():
        mask = (freqs >= lo) & (freqs < hi)
        if not np.any(mask):
            values.append(np.full(segment.shape[0], np.nan, dtype=float))
        else:
            values.append(np.log10(np.mean(psd[:, mask], axis=1) + 1e-20))
    return np.concatenate(values, axis=0)


def phase_randomize_segment(segment: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    spectrum = np.fft.rfft(segment, axis=1)
    if spectrum.shape[1] <= 2:
        return segment.copy()
    random_phase = rng.uniform(0.0, 2.0 * np.pi, size=spectrum[:, 1:-1].shape)
    randomized = spectrum.copy()
    randomized[:, 1:-1] = np.abs(spectrum[:, 1:-1]) * np.exp(1j * random_phase)
    return np.fft.irfft(randomized, n=segment.shape[1], axis=1)


def feature_names(channel_names: list[str]) -> list[str]:
    names = []
    for band in BANDS:
        for channel in channel_names:
            names.append(f"delta_{band}_{channel}")
    return names


def make_feature_row(window: dict, event_file: str, vec: np.ndarray) -> dict:
    return {
        "dataset": "ds004117",
        "subject": window["subject"],
        "session": window["session"],
        "run": window["run"],
        "trial": int(window["trial"]),
        "event_file": event_file,
        "transition": window["transition"],
        "memory_cond": window["memory_cond"],
        "feature_vector": vec.astype(np.float32),
    }


def extract_run_features(
    event_file: str,
    windows: list[dict],
    timeout: int,
    random_windows_per_transition: int,
    time_shift_seconds: float,
    rng: np.random.Generator,
) -> tuple[list[dict], list[dict], list[dict], list[dict], dict, list[str]]:
    stem = event_file.replace("_events.tsv", "")
    for rel_path in [event_file, f"{stem}_eeg.set", f"{stem}_eeg.fdt", f"{stem}_eeg.json", f"{stem}_channels.tsv"]:
        download_file(rel_path, timeout)
    raw_path = DOWNLOADS / f"{stem}_eeg.set"
    raw = mne.io.read_raw_eeglab(raw_path, preload=True, verbose="ERROR")
    raw.pick_types(eeg=True, exclude=[])
    raw.filter(l_freq=1.0, h_freq=55.0, verbose="ERROR")
    sfreq = float(raw.info["sfreq"])
    channel_names = list(raw.ch_names)
    names = feature_names(channel_names)
    rows = []
    phase_rows = []
    time_shift_rows = []
    skipped = 0
    for idx, window in enumerate(windows):
        pre = safe_segment(raw, float(window["pre_start_s"]), float(window["pre_end_s"]))
        post = safe_segment(raw, float(window["post_start_s"]), float(window["post_end_s"]))
        if pre is None or post is None:
            skipped += 1
            continue
        vec = bandpower_vector(post, sfreq) - bandpower_vector(pre, sfreq)
        if not np.isfinite(vec).all():
            skipped += 1
            continue
        rows.append(make_feature_row(window, event_file, vec))

        phase_vec = bandpower_vector(phase_randomize_segment(post, rng), sfreq) - bandpower_vector(phase_randomize_segment(pre, rng), sfreq)
        if np.isfinite(phase_vec).all():
            phase_rows.append(make_feature_row(window, event_file, phase_vec))

        shifted_boundary = float(window["boundary_onset_s"]) + time_shift_seconds
        shifted_pre = safe_segment(raw, shifted_boundary - 1.0, shifted_boundary)
        shifted_post = safe_segment(raw, shifted_boundary, shifted_boundary + 1.0)
        if shifted_pre is not None and shifted_post is not None:
            shifted_vec = bandpower_vector(shifted_post, sfreq) - bandpower_vector(shifted_pre, sfreq)
            if np.isfinite(shifted_vec).all():
                time_shift_rows.append(make_feature_row(window, event_file, shifted_vec))

    random_rows = []
    duration = raw.n_times / sfreq
    labels = ["encoding_to_maintenance", "maintenance_to_probe"]
    n_by_label = {label: sum(1 for row in rows if row["transition"] == label) for label in labels}
    for label in labels:
        n = min(random_windows_per_transition, n_by_label[label])
        for idx in range(n):
            boundary = float(rng.uniform(2.0, max(2.1, duration - 2.0)))
            pre = safe_segment(raw, boundary - 1.0, boundary)
            post = safe_segment(raw, boundary, boundary + 1.0)
            if pre is None or post is None:
                continue
            vec = bandpower_vector(post, sfreq) - bandpower_vector(pre, sfreq)
            if not np.isfinite(vec).all():
                continue
            random_rows.append(
                {
                    "dataset": "ds004117",
                    "subject": rows[0]["subject"] if rows else "",
                    "session": rows[0]["session"] if rows else "",
                    "run": rows[0]["run"] if rows else "",
                    "trial": idx,
                    "event_file": event_file,
                    "transition": label,
                    "memory_cond": "random",
                    "feature_vector": vec.astype(np.float32),
                }
            )
    meta = {
        "event_file": event_file,
        "n_channels": len(channel_names),
        "sfreq": sfreq,
        "duration_s": float(duration),
        "windows_requested": len(windows),
        "windows_extracted": len(rows),
        "windows_skipped": skipped,
        "random_windows_extracted": len(random_rows),
    }
    meta["phase_randomized_windows_extracted"] = len(phase_rows)
    meta["time_shift_windows_extracted"] = len(time_shift_rows)
    meta["time_shift_seconds"] = float(time_shift_seconds)
    return rows, random_rows, phase_rows, time_shift_rows, meta, names


def rows_to_arrays(rows: list[dict]) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
    x = np.vstack([row["feature_vector"] for row in rows])
    y = np.array([row["transition"] for row in rows])
    groups = np.array([row["event_file"] for row in rows])
    subjects = [row["subject"] for row in rows]
    return x, y, groups, subjects


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return float("nan")
    return float(np.dot(a, b) / denom)


def split_centroid_similarity(rows: list[dict]) -> float:
    scores = []
    for transition in sorted({row["transition"] for row in rows}):
        subset = sorted([row for row in rows if row["transition"] == transition], key=lambda r: (r["event_file"], r["trial"]))
        if len(subset) < 4:
            continue
        a = np.vstack([row["feature_vector"] for idx, row in enumerate(subset) if idx % 2 == 0]).mean(axis=0)
        b = np.vstack([row["feature_vector"] for idx, row in enumerate(subset) if idx % 2 == 1]).mean(axis=0)
        scores.append(cosine(a, b))
    return float(np.nanmean(scores)) if scores else float("nan")


def leave_one_run_accuracy(x: np.ndarray, y: np.ndarray, groups: np.ndarray) -> dict:
    logo = LeaveOneGroupOut()
    preds = []
    truth = []
    fold_rows = []
    for train_idx, test_idx in logo.split(x, y, groups):
        if len(np.unique(y[train_idx])) < 2 or len(np.unique(y[test_idx])) < 2:
            continue
        model = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=1000, class_weight="balanced", solver="liblinear", random_state=17),
        )
        model.fit(x[train_idx], y[train_idx])
        pred = model.predict(x[test_idx])
        preds.extend(pred.tolist())
        truth.extend(y[test_idx].tolist())
        fold_rows.append({"heldout_group": str(groups[test_idx][0]), "accuracy": float(accuracy_score(y[test_idx], pred)), "n_test": int(len(test_idx))})
    return {
        "accuracy": float(accuracy_score(truth, preds)) if truth else float("nan"),
        "n_predictions": int(len(truth)),
        "n_folds": int(len(fold_rows)),
        "folds": fold_rows,
        "truth": truth,
        "predictions": preds,
    }


def permutation_null_accuracy(x: np.ndarray, y: np.ndarray, groups: np.ndarray, n_perm: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    observed_result = leave_one_run_accuracy(x, y, groups)
    observed = observed_result["accuracy"]
    truth = np.array(observed_result["truth"], dtype=object)
    predictions = np.array(observed_result["predictions"], dtype=object)
    null = []
    for _ in range(n_perm):
        shuffled = truth.copy()
        rng.shuffle(shuffled)
        null.append(float(accuracy_score(shuffled, predictions)))
    null_arr = np.array(null, dtype=float)
    return {
        "observed_accuracy": float(observed),
        "null_mean_accuracy": float(np.nanmean(null_arr)),
        "null_ci95": [float(np.nanpercentile(null_arr, 2.5)), float(np.nanpercentile(null_arr, 97.5))],
        "p_one_sided_observed_greater": float((np.count_nonzero(null_arr >= observed) + 1) / (len(null_arr) + 1)),
        "n_perm": int(n_perm),
        "null_mode": "heldout_prediction_label_shuffle",
    }


def subject_level_accuracy(rows: list[dict]) -> dict:
    subject_payload = []
    for subject in sorted({row["subject"] for row in rows}):
        subset = [row for row in rows if row["subject"] == subject]
        if len({row["event_file"] for row in subset}) < 2:
            continue
        sx, sy, sgroups, _ = rows_to_arrays(subset)
        result = leave_one_run_accuracy(sx, sy, sgroups)
        subject_payload.append(
            {
                "subject": subject,
                "accuracy": result["accuracy"],
                "n_predictions": result["n_predictions"],
                "n_folds": result["n_folds"],
            }
        )
    values = np.array([row["accuracy"] for row in subject_payload if np.isfinite(row["accuracy"])], dtype=float)
    if len(values) == 0:
        return {"subjects": subject_payload, "mean_accuracy": float("nan"), "median_accuracy": float("nan"), "binomial_p_gt_chance": float("nan")}
    return {
        "subjects": subject_payload,
        "mean_accuracy": float(np.mean(values)),
        "median_accuracy": float(np.median(values)),
        "n_subjects": int(len(values)),
        "n_subjects_above_chance": int(np.count_nonzero(values > 0.5)),
        "binomial_p_gt_chance": float(binomtest(int(np.count_nonzero(values > 0.5)), len(values), p=0.5, alternative="greater").pvalue),
    }


def bootstrap_mean_ci(values: list[float], seed: int, n_boot: int = 5000) -> dict:
    arr = np.array([value for value in values if np.isfinite(value)], dtype=float)
    if len(arr) == 0:
        return {"mean": float("nan"), "ci95": [float("nan"), float("nan")], "n": 0}
    rng = np.random.default_rng(seed)
    means = [float(np.mean(rng.choice(arr, size=len(arr), replace=True))) for _ in range(n_boot)]
    return {
        "mean": float(np.mean(arr)),
        "ci95": [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))],
        "n": int(len(arr)),
        "n_boot": int(n_boot),
    }


def compact_accuracy_result(result: dict) -> dict:
    return {key: value for key, value in result.items() if key not in {"truth", "predictions"}}


def write_feature_table(rows: list[dict], names: list[str], path: Path) -> None:
    fields = ["dataset", "subject", "session", "run", "trial", "event_file", "transition", "memory_cond"] + names
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            payload = {field: row.get(field) for field in fields[:8]}
            payload.update({name: float(value) for name, value in zip(names, row["feature_vector"])})
            writer.writerow(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Paper 6 E3-E6 ds004117 multi-run fast-dynamics analysis.")
    parser.add_argument("--max-runs", type=int, default=12, help="Number of event files/runs to analyze; use 0 for all available runs.")
    parser.add_argument("--subjects", nargs="*", default=None)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--random-windows-per-transition", type=int, default=20)
    parser.add_argument("--n-perm", type=int, default=200)
    parser.add_argument("--time-shift-seconds", type=float, default=10.0)
    parser.add_argument("--analysis-label", default="multi_run")
    args = parser.parse_args()

    rng = np.random.default_rng(20260902)
    max_runs = None if args.max_runs == 0 else args.max_runs
    grouped = load_windows(max_runs, args.subjects)
    if len(grouped) < 3:
        raise SystemExit("Need at least 3 event files/runs for E3-E6 multi-run analysis.")

    all_rows: list[dict] = []
    all_random_rows: list[dict] = []
    all_phase_rows: list[dict] = []
    all_time_shift_rows: list[dict] = []
    metas = []
    names: list[str] | None = None
    for event_file, windows in grouped.items():
        rows, random_rows, phase_rows, time_shift_rows, meta, feature_name_list = extract_run_features(
            event_file,
            windows,
            args.timeout,
            args.random_windows_per_transition,
            args.time_shift_seconds,
            rng,
        )
        if names is None:
            names = feature_name_list
        elif names != feature_name_list:
            raise RuntimeError("Channel/feature order mismatch across runs; aborting to avoid invalid pooling.")
        all_rows.extend(rows)
        all_random_rows.extend(random_rows)
        all_phase_rows.extend(phase_rows)
        all_time_shift_rows.extend(time_shift_rows)
        metas.append(meta)
        print(f"processed {event_file}: windows={len(rows)} random={len(random_rows)} phase={len(phase_rows)} shifted={len(time_shift_rows)}", flush=True)

    if names is None or len(all_rows) == 0:
        raise SystemExit("No features extracted.")

    x, y, groups, subjects = rows_to_arrays(all_rows)
    rx, ry, rgroups, _ = rows_to_arrays(all_random_rows)
    e4_real = split_centroid_similarity(all_rows)
    e4_random = split_centroid_similarity(all_random_rows)
    e5 = leave_one_run_accuracy(x, y, groups)
    e6_label_null = permutation_null_accuracy(x, y, groups, args.n_perm, seed=31)
    e6_random_window = leave_one_run_accuracy(rx, ry, rgroups)
    px, py, pgroups, _ = rows_to_arrays(all_phase_rows)
    tx, ty, tgroups, _ = rows_to_arrays(all_time_shift_rows)
    e6_phase_randomized = leave_one_run_accuracy(px, py, pgroups)
    e6_time_shift = leave_one_run_accuracy(tx, ty, tgroups)
    e5_subject = subject_level_accuracy(all_rows)
    subject_bootstrap = bootstrap_mean_ci([row["accuracy"] for row in e5_subject.get("subjects", [])], seed=43)

    FEATURES.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    label = args.analysis_label.replace("/", "_").replace("\\", "_")
    feature_csv = FEATURES / f"ds004117_{label}_bandpower_delta_features.csv"
    write_feature_table(all_rows, names, feature_csv)
    random_feature_csv = FEATURES / f"ds004117_{label}_random_window_bandpower_delta_features.csv"
    write_feature_table(all_random_rows, names, random_feature_csv)
    phase_feature_csv = FEATURES / f"ds004117_{label}_phase_randomized_bandpower_delta_features.csv"
    write_feature_table(all_phase_rows, names, phase_feature_csv)
    time_shift_feature_csv = FEATURES / f"ds004117_{label}_time_shift_bandpower_delta_features.csv"
    write_feature_table(all_time_shift_rows, names, time_shift_feature_csv)

    gates = {
        "E4_existence_real_similarity_gt_random_windows": bool(np.isfinite(e4_real) and np.isfinite(e4_random) and e4_real > e4_random),
        "E5_specificity_accuracy_gt_label_shuffle_ci95": bool(e5["accuracy"] > e6_label_null["null_ci95"][1]),
        "E6_specificity_accuracy_gt_random_windows": bool(e5["accuracy"] > e6_random_window["accuracy"]),
        "E6_specificity_accuracy_gt_time_shift": bool(e5["accuracy"] > e6_time_shift["accuracy"]),
    }
    if max_runs is None:
        status = "PASS_E3_E6_FULL_COHORT" if all(gates.values()) else "PARTIAL_OR_NEGATIVE_E3_E6_FULL_COHORT"
        scope = "Full available ds004117 EEG cohort from transition-window manifest; no cross-dataset replication."
    else:
        status = "PASS_E3_E6_INITIAL" if all(gates.values()) else "PARTIAL_OR_NEGATIVE_E3_E6_INITIAL"
        scope = "Initial multi-run ds004117 EEG analysis; not full-cohort final holdout; no cross-dataset replication."
    payload = {
        "experiment": "P6-E3-E6-ds004117-multi-run",
        "status": status,
        "scope": scope,
        "dataset": "ds004117",
        "n_event_files": len(grouped),
        "n_subjects": len(set(subjects)),
        "n_windows": len(all_rows),
        "n_random_windows": len(all_random_rows),
        "n_phase_randomized_windows": len(all_phase_rows),
        "n_time_shift_windows": len(all_time_shift_rows),
        "feature_file": str(feature_csv.relative_to(ROOT.parent)),
        "random_feature_file": str(random_feature_csv.relative_to(ROOT.parent)),
        "phase_randomized_feature_file": str(phase_feature_csv.relative_to(ROOT.parent)),
        "time_shift_feature_file": str(time_shift_feature_csv.relative_to(ROOT.parent)),
        "feature_family": "per-channel 1-second pre/post transition log bandpower deltas",
        "bands": BANDS,
        "run_meta": metas,
        "e4_existence": {
            "same_transition_odd_even_centroid_similarity": e4_real,
            "random_window_odd_even_centroid_similarity": e4_random,
            "delta_similarity": float(e4_real - e4_random),
        },
        "e5_specificity": compact_accuracy_result(e5),
        "e5_subject_level": e5_subject,
        "e5_subject_accuracy_bootstrap": subject_bootstrap,
        "e6_nulls": {
            "label_shuffle_accuracy_null": e6_label_null,
            "random_window_specificity_accuracy": compact_accuracy_result(e6_random_window),
            "time_shift_specificity_accuracy": compact_accuracy_result(e6_time_shift),
            "phase_randomized_bandpower_specificity_accuracy": compact_accuracy_result(e6_phase_randomized),
            "phase_randomization_note": "This control preserves Fourier amplitude by design; with bandpower-delta features it tests phase-insensitivity of the current feature family, not phase-specific neural dynamics.",
        },
        "gates": gates,
        "claim_audit": {
            "can_claim_fast_dynamics_existence": bool(gates["E4_existence_real_similarity_gt_random_windows"]),
            "can_claim_transition_specificity": bool(gates["E5_specificity_accuracy_gt_label_shuffle_ci95"] and gates["E6_specificity_accuracy_gt_random_windows"]),
            "can_claim_nap_exists": False,
            "can_claim_cross_dataset_replication": False,
            "allowed_current_claim": "Initial ds004117 multi-run EEG analysis has been run; any positive finding is preliminary until full cohort and external replication.",
            "forbidden_claims": [
                "NAP is validated.",
                "CWP maps to NAP.",
                "Fast neural dynamics are universal primitives.",
                "P6 is complete.",
            ],
        },
    }
    result_path = RESULTS / f"e3_e6_ds004117_{label}_results.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if label == "multi_run":
        (RESULTS / "e3_e6_ds004117_multi_run_results.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
