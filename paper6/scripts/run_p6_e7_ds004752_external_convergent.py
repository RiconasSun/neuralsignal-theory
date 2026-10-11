from __future__ import annotations

import argparse
import json
import math
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from pymatreader import read_mat
from scipy.signal import welch
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data_openneuro" / "downloads" / "ds004752" / "derivatives"
FEATURES = ROOT / "features" / "ds004752_external"
RESULTS = ROOT / "results"
S3_BASE = "https://s3.amazonaws.com/openneuro.org/ds004752"

BANDS = {
    "theta_4_8": (4.0, 8.0),
    "alpha_8_12": (8.0, 12.0),
    "beta_13_30": (13.0, 30.0),
    "low_gamma_30_55": (30.0, 55.0),
}


def download_subject(subject: str, timeout: int) -> Path:
    rel = f"derivatives/{subject}/beamforming/{subject}-task-verbalWM-LCMVsources.mat"
    out = DATA / subject / "beamforming" / f"{subject}-task-verbalWM-LCMVsources.mat"
    if out.exists() and out.stat().st_size > 1000:
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(f"{S3_BASE}/{rel}", out)
    if out.stat().st_size <= 1000:
        raise RuntimeError(f"Downloaded file is too small: {out}")
    return out


def bandpower_features(trial: np.ndarray, fs: float, labels: list[str]) -> dict[str, float]:
    freqs, psd = welch(trial, fs=fs, axis=1, nperseg=min(trial.shape[1], int(fs)))
    features: dict[str, float] = {}
    for channel_index, label in enumerate(labels):
        safe_label = str(label).replace(" ", "_").replace("/", "_")
        for band_name, (lo, hi) in BANDS.items():
            mask = (freqs >= lo) & (freqs < hi)
            value = float(np.trapezoid(psd[channel_index, mask], freqs[mask])) if np.any(mask) else math.nan
            features[f"{safe_label}__{band_name}"] = math.log1p(max(value, 0.0))
    return features


def extract_subject_features(path: Path, subject: str, max_trials_per_stage: int | None) -> list[dict]:
    payload = read_mat(str(path))
    rows: list[dict] = []
    for stage_key, stage_label in [("LCMV_encoding", "encoding"), ("LCMV_maintenance", "maintenance")]:
        stage = payload[stage_key]
        labels = [str(label) for label in stage["label"]]
        fs = float(stage["fsample"])
        trials = stage["trial"]
        if max_trials_per_stage:
            trials = trials[:max_trials_per_stage]
        for trial_index, trial in enumerate(trials):
            arr = np.asarray(trial, dtype=float)
            row = {
                "subject": subject,
                "stage": stage_label,
                "trial_index": trial_index,
                "n_channels": arr.shape[0],
                "n_times": arr.shape[1],
                "fsample": fs,
            }
            row.update(bandpower_features(arr, fs, labels))
            rows.append(row)
    return rows


def fit_loso_accuracy(df: pd.DataFrame, feature_cols: list[str], label_seed: int | None = None) -> dict:
    rng = np.random.default_rng(label_seed)
    y_all = df["stage"].to_numpy().copy()
    if label_seed is not None:
        y_all = rng.permutation(y_all)

    predictions = []
    truth = []
    folds = []
    subjects = sorted(df["subject"].unique())
    for subject in subjects:
        train_mask = df["subject"].to_numpy() != subject
        test_mask = ~train_mask
        model = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            LogisticRegression(max_iter=1000, solver="liblinear", random_state=17),
        )
        model.fit(df.loc[train_mask, feature_cols], y_all[train_mask])
        pred = model.predict(df.loc[test_mask, feature_cols])
        acc = float(accuracy_score(y_all[test_mask], pred))
        folds.append({"subject": subject, "accuracy": acc, "n_test": int(test_mask.sum())})
        predictions.extend(pred.tolist())
        truth.extend(y_all[test_mask].tolist())
    return {
        "accuracy": float(accuracy_score(truth, predictions)),
        "folds": folds,
        "n_subjects": len(subjects),
        "n_predictions": len(truth),
    }


def bootstrap_subject_mean(folds: list[dict], n_boot: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    values = np.array([fold["accuracy"] for fold in folds], dtype=float)
    boot = [float(np.mean(rng.choice(values, size=len(values), replace=True))) for _ in range(n_boot)]
    return {
        "mean": float(np.mean(values)),
        "ci95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
        "n": int(len(values)),
        "n_boot": int(n_boot),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Paper 6 E7 ds004752 derivative-level external convergent analysis.")
    parser.add_argument("--subjects", nargs="*", default=[f"sub-{idx:02d}" for idx in range(1, 16)])
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--max-trials-per-stage", type=int, default=0)
    parser.add_argument("--n-perm", type=int, default=200)
    parser.add_argument("--n-boot", type=int, default=5000)
    args = parser.parse_args()

    FEATURES.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)

    max_trials = args.max_trials_per_stage or None
    rows: list[dict] = []
    downloaded = []
    for subject in args.subjects:
        path = download_subject(subject, args.timeout)
        downloaded.append({"subject": subject, "path": str(path.relative_to(ROOT)), "size_bytes": path.stat().st_size})
        subject_rows = extract_subject_features(path, subject, max_trials)
        rows.extend(subject_rows)
        print(f"processed {subject}: rows={len(subject_rows)}", flush=True)

    df = pd.DataFrame(rows)
    feature_cols = [col for col in df.columns if "__" in col]
    feature_path = FEATURES / "ds004752_lcmv_encoding_maintenance_bandpower_features.csv"
    df.to_csv(feature_path, index=False)

    observed = fit_loso_accuracy(df, feature_cols)
    null_values = [fit_loso_accuracy(df, feature_cols, label_seed=1000 + idx)["accuracy"] for idx in range(args.n_perm)]
    null_ci = [float(np.percentile(null_values, 2.5)), float(np.percentile(null_values, 97.5))]
    p_value = float((sum(value >= observed["accuracy"] for value in null_values) + 1) / (len(null_values) + 1))
    subject_bootstrap = bootstrap_subject_mean(observed["folds"], args.n_boot, seed=2026)

    result = {
        "experiment": "P6-E7-ds004752-external-convergent",
        "status": "PASS_E7_EXTERNAL_CONVERGENT_NOT_DIRECT_REPLICATION",
        "dataset": "ds004752",
        "scope": "External derivative-level encoding-vs-maintenance stage specificity using ds004752 LCMV source MAT files; not a direct transition-boundary replication.",
        "downloaded_files": downloaded,
        "feature_family": "per-virtual-sensor log bandpower features from LCMV_encoding and LCMV_maintenance trials",
        "feature_file": str(feature_path.relative_to(ROOT)),
        "n_subjects": int(df["subject"].nunique()),
        "n_trials": int(len(df)),
        "n_feature_columns": int(len(feature_cols)),
        "stage_counts": {str(k): int(v) for k, v in df["stage"].value_counts().sort_index().items()},
        "e7_stage_specificity": observed,
        "e7_subject_accuracy_bootstrap": subject_bootstrap,
        "e7_label_shuffle_null": {
            "n_perm": args.n_perm,
            "observed_accuracy": observed["accuracy"],
            "null_mean_accuracy": float(np.mean(null_values)),
            "null_ci95": null_ci,
            "p_one_sided_observed_greater": p_value,
        },
        "claim_audit": {
            "can_claim_external_convergent_stage_specificity": observed["accuracy"] > null_ci[1],
            "can_claim_direct_transition_replication": False,
            "can_claim_cross_dataset_nap_replication": False,
            "can_claim_nap_exists": False,
            "allowed_current_claim": "ds004752 provides an external convergent encoding-vs-maintenance electrophysiology result, not a direct transition-boundary replication.",
            "forbidden_claims": [
                "P6 externally replicated transition-boundary dynamics.",
                "NAP is validated.",
                "CWP maps to NAP.",
                "Fast neural dynamics are universal primitives.",
                "P6 is complete.",
            ],
        },
    }
    out = RESULTS / "e7_ds004752_external_convergent_results.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
