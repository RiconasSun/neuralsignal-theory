from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import binomtest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
FEATURES = ROOT / "features" / "ds004117_multi_run"
RESULTS = ROOT / "results"


def load_feature_csv(path: Path) -> tuple[list[dict], list[str]]:
    rows = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return rows, []
        feature_names = [name for name in reader.fieldnames if name.startswith("delta_")]
        for row in reader:
            vec = np.array([float(row[name]) for name in feature_names], dtype=np.float32)
            rows.append(
                {
                    "dataset": row["dataset"],
                    "subject": row["subject"],
                    "session": row["session"],
                    "run": row["run"],
                    "trial": int(row["trial"]),
                    "event_file": row["event_file"],
                    "transition": row["transition"],
                    "memory_cond": row["memory_cond"],
                    "feature_vector": vec,
                }
            )
    return rows, feature_names


def load_many(paths: list[Path]) -> tuple[list[dict], list[str]]:
    all_rows = []
    expected_names: list[str] | None = None
    for path in paths:
        rows, names = load_feature_csv(path)
        if expected_names is None:
            expected_names = names
        elif expected_names != names:
            raise RuntimeError(f"Feature columns mismatch: {path}")
        all_rows.extend(rows)
    return all_rows, expected_names or []


def rows_to_arrays(rows: list[dict]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return (
        np.vstack([row["feature_vector"] for row in rows]),
        np.array([row["transition"] for row in rows], dtype=object),
        np.array([row["event_file"] for row in rows], dtype=object),
    )


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


def leave_one_run_accuracy(rows: list[dict]) -> dict:
    x, y, groups = rows_to_arrays(rows)
    logo = LeaveOneGroupOut()
    preds = []
    truth = []
    folds = []
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
        folds.append({"heldout_group": str(groups[test_idx][0]), "accuracy": float(accuracy_score(y[test_idx], pred)), "n_test": int(len(test_idx))})
    return {
        "accuracy": float(accuracy_score(truth, preds)) if truth else float("nan"),
        "n_predictions": int(len(truth)),
        "n_folds": int(len(folds)),
        "folds": folds,
        "truth": truth,
        "predictions": preds,
    }


def compact(result: dict) -> dict:
    return {key: value for key, value in result.items() if key not in {"truth", "predictions"}}


def heldout_prediction_label_null(result: dict, n_perm: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    truth = np.array(result["truth"], dtype=object)
    pred = np.array(result["predictions"], dtype=object)
    observed = float(result["accuracy"])
    null = []
    for _ in range(n_perm):
        shuffled = truth.copy()
        rng.shuffle(shuffled)
        null.append(float(accuracy_score(shuffled, pred)))
    null_arr = np.array(null, dtype=float)
    return {
        "observed_accuracy": observed,
        "null_mean_accuracy": float(np.nanmean(null_arr)),
        "null_ci95": [float(np.nanpercentile(null_arr, 2.5)), float(np.nanpercentile(null_arr, 97.5))],
        "p_one_sided_observed_greater": float((np.count_nonzero(null_arr >= observed) + 1) / (len(null_arr) + 1)),
        "n_perm": int(n_perm),
        "null_mode": "heldout_prediction_label_shuffle",
    }


def subject_level(rows: list[dict]) -> dict:
    subjects = []
    for subject in sorted({row["subject"] for row in rows}):
        subset = [row for row in rows if row["subject"] == subject]
        if len({row["event_file"] for row in subset}) < 2:
            continue
        result = compact(leave_one_run_accuracy(subset))
        subjects.append({"subject": subject, "accuracy": result["accuracy"], "n_predictions": result["n_predictions"], "n_folds": result["n_folds"]})
    values = np.array([row["accuracy"] for row in subjects if np.isfinite(row["accuracy"])], dtype=float)
    return {
        "subjects": subjects,
        "n_subjects": int(len(values)),
        "mean_accuracy": float(np.mean(values)) if len(values) else float("nan"),
        "median_accuracy": float(np.median(values)) if len(values) else float("nan"),
        "n_subjects_above_chance": int(np.count_nonzero(values > 0.5)),
        "binomial_p_gt_chance": float(binomtest(int(np.count_nonzero(values > 0.5)), len(values), p=0.5, alternative="greater").pvalue) if len(values) else float("nan"),
    }


def bootstrap_subject_mean(subject_payload: dict, seed: int, n_boot: int) -> dict:
    values = np.array([row["accuracy"] for row in subject_payload["subjects"] if np.isfinite(row["accuracy"])], dtype=float)
    if len(values) == 0:
        return {"n": 0, "mean": float("nan"), "ci95": [float("nan"), float("nan")]}
    rng = np.random.default_rng(seed)
    means = np.array([np.mean(rng.choice(values, size=len(values), replace=True)) for _ in range(n_boot)], dtype=float)
    return {
        "n": int(len(values)),
        "mean": float(np.mean(values)),
        "ci95": [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))],
        "n_boot": int(n_boot),
    }


def count_by_subject(rows: list[dict]) -> dict:
    counts = defaultdict(int)
    for row in rows:
        counts[row["subject"]] += 1
    return dict(sorted(counts.items()))


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate batched Paper 6 ds004117 E3-E6 feature files.")
    parser.add_argument("--label-prefix", default="batch")
    parser.add_argument("--analysis-label", default="full_cohort_batched")
    parser.add_argument("--n-perm", type=int, default=200)
    parser.add_argument("--n-boot", type=int, default=5000)
    args = parser.parse_args()

    real_paths = sorted(
        path
        for path in FEATURES.glob(f"ds004117_{args.label_prefix}*_bandpower_delta_features.csv")
        if "_random_window_" not in path.name and "_phase_randomized_" not in path.name and "_time_shift_" not in path.name
    )
    random_paths = sorted(FEATURES.glob(f"ds004117_{args.label_prefix}*_random_window_bandpower_delta_features.csv"))
    phase_paths = sorted(FEATURES.glob(f"ds004117_{args.label_prefix}*_phase_randomized_bandpower_delta_features.csv"))
    shift_paths = sorted(FEATURES.glob(f"ds004117_{args.label_prefix}*_time_shift_bandpower_delta_features.csv"))
    if not real_paths:
        raise SystemExit(f"No batch feature files found for prefix {args.label_prefix!r}.")

    rows, names = load_many(real_paths)
    random_rows, _ = load_many(random_paths)
    phase_rows, _ = load_many(phase_paths)
    shift_rows, _ = load_many(shift_paths)

    e4_real = split_centroid_similarity(rows)
    e4_random = split_centroid_similarity(random_rows)
    e5 = leave_one_run_accuracy(rows)
    e6_label_null = heldout_prediction_label_null(e5, args.n_perm, seed=31)
    e6_random = leave_one_run_accuracy(random_rows)
    e6_phase = leave_one_run_accuracy(phase_rows)
    e6_shift = leave_one_run_accuracy(shift_rows)
    e5_subject = subject_level(rows)
    e5_subject_bootstrap = bootstrap_subject_mean(e5_subject, seed=43, n_boot=args.n_boot)

    gates = {
        "E4_existence_real_similarity_gt_random_windows": bool(np.isfinite(e4_real) and np.isfinite(e4_random) and e4_real > e4_random),
        "E5_specificity_accuracy_gt_label_shuffle_ci95": bool(e5["accuracy"] > e6_label_null["null_ci95"][1]),
        "E6_specificity_accuracy_gt_random_windows": bool(e5["accuracy"] > e6_random["accuracy"]),
        "E6_specificity_accuracy_gt_time_shift": bool(e5["accuracy"] > e6_shift["accuracy"]),
    }
    payload = {
        "experiment": "P6-E3-E6-ds004117-full-cohort-batched",
        "status": "PASS_E3_E6_FULL_COHORT_BATCHED" if all(gates.values()) else "PARTIAL_OR_NEGATIVE_E3_E6_FULL_COHORT_BATCHED",
        "scope": "Full available ds004117 EEG cohort assembled from batched subject-level feature extraction; no external dataset replication.",
        "dataset": "ds004117",
        "batch_real_feature_files": [str(path.relative_to(ROOT.parent)) for path in real_paths],
        "n_feature_columns": len(names),
        "n_event_files": len({row["event_file"] for row in rows}),
        "n_subjects": len({row["subject"] for row in rows}),
        "n_windows": len(rows),
        "n_random_windows": len(random_rows),
        "n_phase_randomized_windows": len(phase_rows),
        "n_time_shift_windows": len(shift_rows),
        "windows_by_subject": count_by_subject(rows),
        "feature_family": "per-channel 1-second pre/post transition log bandpower deltas",
        "e4_existence": {
            "same_transition_odd_even_centroid_similarity": e4_real,
            "random_window_odd_even_centroid_similarity": e4_random,
            "delta_similarity": float(e4_real - e4_random),
        },
        "e5_specificity": compact(e5),
        "e5_subject_level": e5_subject,
        "e5_subject_accuracy_bootstrap": e5_subject_bootstrap,
        "e6_nulls": {
            "label_shuffle_accuracy_null": e6_label_null,
            "random_window_specificity_accuracy": compact(e6_random),
            "time_shift_specificity_accuracy": compact(e6_shift),
            "phase_randomized_bandpower_specificity_accuracy": compact(e6_phase),
            "phase_randomization_note": "Bandpower-delta features are expected to be insensitive to phase randomization; this is a feature-family limitation and not a phase-dynamics test.",
        },
        "gates": gates,
        "claim_audit": {
            "can_claim_fast_dynamics_existence": bool(gates["E4_existence_real_similarity_gt_random_windows"]),
            "can_claim_transition_specificity": bool(gates["E5_specificity_accuracy_gt_label_shuffle_ci95"] and gates["E6_specificity_accuracy_gt_random_windows"] and gates["E6_specificity_accuracy_gt_time_shift"]),
            "can_claim_nap_exists": False,
            "can_claim_cross_dataset_replication": False,
            "allowed_current_claim": "Full available ds004117 cohort supports transition-aligned EEG bandpower-delta structure if gates pass; cross-dataset and NAP claims remain forbidden.",
            "forbidden_claims": [
                "NAP is validated.",
                "CWP maps to NAP.",
                "Fast neural dynamics are universal primitives.",
                "P6 is complete.",
            ],
        },
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / f"e3_e6_ds004117_{args.analysis_label}_results.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
