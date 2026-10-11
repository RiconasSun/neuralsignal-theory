from __future__ import annotations

import json
import argparse
from pathlib import Path

import nibabel as nib
import numpy as np
from sklearn.linear_model import RidgeCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data_hcp_ya_2025" / "downloads" / "HCP_1200"
RESULTS = ROOT / "results"
STATES = ROOT / "state_extraction" / "hcp_smoke"
TR = 0.72
PRIMARY_LAG = 4


def zscore(x: np.ndarray) -> np.ndarray:
    mu = np.nanmean(x, axis=0, keepdims=True)
    sd = np.nanstd(x, axis=0, keepdims=True)
    sd[sd == 0] = 1.0
    return (x - mu) / sd


def residualize(y: np.ndarray, confounds: np.ndarray) -> np.ndarray:
    x = np.column_stack([np.ones(confounds.shape[0]), zscore(confounds)])
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    return y - x @ beta


def parcellate_cortex(dtseries: Path, dlabel: Path) -> tuple[np.ndarray, np.ndarray]:
    data = np.asarray(nib.load(str(dtseries)).get_fdata(dtype=np.float32))
    labels = np.asarray(nib.load(str(dlabel)).get_fdata()).astype(int).ravel()
    cortical = data[:, : labels.size]
    parcel_ids = np.array([label for label in np.unique(labels) if label > 0], dtype=int)
    states = np.zeros((data.shape[0], parcel_ids.size), dtype=np.float32)
    for idx, label in enumerate(parcel_ids):
        mask = labels == label
        states[:, idx] = cortical[:, mask].mean(axis=1)
    return states, parcel_ids


def run_subject(subject: str) -> dict:
    subject_root = DATA / subject
    dlabel = subject_root / "MNINonLinear" / "fsaverage_LR32k" / f"{subject}.aparc.32k_fs_LR.dlabel.nii"
    runs = []
    for run in ["tfMRI_WM_LR", "tfMRI_WM_RL"]:
        run_dir = subject_root / "MNINonLinear" / "Results" / run
        states, parcel_ids = parcellate_cortex(run_dir / f"{run}_Atlas_MSMAll.dtseries.nii", dlabel)
        motion = np.loadtxt(run_dir / "Movement_Regressors.txt")
        residual = residualize(zscore(states), motion)
        runs.append({"run": run, "states": residual, "parcel_ids": parcel_ids})

    all_states = np.vstack([r["states"] for r in runs])
    x = all_states[:-PRIMARY_LAG]
    y = all_states[PRIMARY_LAG:]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.35, random_state=5, shuffle=False)
    model = RidgeCV(alphas=np.logspace(-3, 3, 13))
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    mse = float(mean_squared_error(y_test, pred))
    r2 = float(r2_score(y_test, pred, multioutput="variance_weighted"))
    null = np.repeat(y_train.mean(axis=0, keepdims=True), y_test.shape[0], axis=0)
    null_mse = float(mean_squared_error(y_test, null))

    STATES.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        STATES / f"{subject}_aparc_cortical_wm_states.npz",
        states=all_states.astype(np.float32),
        parcel_ids=runs[0]["parcel_ids"],
        primary_lag=PRIMARY_LAG,
        tr=TR,
    )
    return {
        "subject": subject,
        "status": "PASS",
        "n_runs": len(runs),
        "n_timepoints": int(all_states.shape[0]),
        "n_parcels": int(all_states.shape[1]),
        "state_file": str((STATES / f"{subject}_aparc_cortical_wm_states.npz").relative_to(ROOT.parent)),
        "state_representation": "aparc cortical CIFTI parcel means, first 59412 cortical grayordinates only; subcortex excluded in smoke",
        "motion_residualized": True,
        "primary_lag_tr": PRIMARY_LAG,
        "primary_lag_seconds": PRIMARY_LAG * TR,
        "ridge_alpha": float(model.alpha_),
        "mse": mse,
        "null_mean_mse": null_mse,
        "mse_improvement_vs_mean_null": float(null_mse - mse),
        "r2": r2,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract HCP WM cortical aparc states and run E3 no-structure smoke baselines.")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    subjects = sorted(p.name for p in DATA.iterdir() if p.is_dir())
    if not subjects:
        raise SystemExit("No downloaded HCP subject directories found.")
    if args.limit:
        subjects = subjects[: args.limit]
    rows = []
    errors = []
    for subject in subjects:
        try:
            rows.append(run_subject(subject))
            print(f"processed {subject}", flush=True)
        except Exception as exc:  # noqa: BLE001
            errors.append({"subject": subject, "error": type(exc).__name__, "message": str(exc)[:300]})
    payload = {
        "experiment": "P5-HCP-E2-E3-smoke",
        "status": "PASS" if rows and not errors and all(r["status"] == "PASS" for r in rows) else "PARTIAL_OR_FAIL",
        "scope": "downloaded-cohort cortical-state/no-structure baseline; not a structural-connectome hypothesis test",
        "n_subjects_processed": len(rows),
        "n_errors": len(errors),
        "errors": errors,
        "subjects": rows,
        "subject_level_mean_r2": float(np.mean([r["r2"] for r in rows])) if rows else None,
        "subject_level_median_r2": float(np.median([r["r2"] for r in rows])) if rows else None,
        "subject_level_mean_mse_improvement_vs_mean_null": float(np.mean([r["mse_improvement_vs_mean_null"] for r in rows])) if rows else None,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "hcp_e2_e3_smoke_states.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
