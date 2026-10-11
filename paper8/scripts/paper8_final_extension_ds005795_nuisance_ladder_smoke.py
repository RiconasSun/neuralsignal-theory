from __future__ import annotations

import csv
import json
import argparse
from pathlib import Path

import nibabel as nib
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
STATE = ROOT / "state_extraction" / "ds005795_physio_extension"
DATA = ROOT / "data_ds005795_smoke"
SUBJECT = "sub-01"
TASK = "learning"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_feature_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def make_design(rows: list[dict], include_physio: bool, include_metadata: bool) -> np.ndarray:
    numeric = []
    for row in rows:
        values = [
            float(row["tr_index"]),
            float(row["n_events"]),
        ]
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a ds005795 global-signal physiology nuisance-ladder smoke test.")
    parser.add_argument("--subjects", nargs="+", default=[SUBJECT], help="BIDS subject IDs, e.g. sub-01 sub-02")
    parser.add_argument("--task", default=TASK)
    return parser.parse_args()


def run_subject(subject: str, task: str) -> dict:
    bold_path = DATA / subject / "func" / f"{subject}_task-{task}_bold.nii.gz"
    feature_path = STATE / f"p8_ds005795_{subject.replace('-', '')}_{task}_physio_tr_features.csv"
    legacy_feature_path = STATE / "p8_ds005795_sub01_learning_physio_tr_features.csv"
    if not feature_path.exists() and subject == SUBJECT and task == TASK and legacy_feature_path.exists():
        feature_path = legacy_feature_path
    bold_json = read_json(DATA / subject / "func" / f"{subject}_task-{task}_bold.json")
    img = nib.load(str(bold_path))
    data = np.asanyarray(img.dataobj)
    if data.ndim != 4:
        raise SystemExit(f"Expected 4D BOLD, got shape {data.shape}")
    finite_mask = np.isfinite(data[..., 0])
    brain_mask = finite_mask & (np.nanstd(data, axis=3) > 0)
    global_signal = np.nanmean(data[brain_mask, :], axis=0)
    global_signal = np.asarray(global_signal, dtype=float)
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
    return {
        "subject": subject,
        "task": task,
        "bold_path": str(bold_path),
        "feature_path": str(feature_path),
        "bold_shape": list(data.shape),
        "repetition_time": bold_json.get("RepetitionTime"),
        "brain_mask_voxels": int(np.sum(brain_mask)),
        "usable_transition_rows": int(usable),
        "results": results,
    }


def aggregate(subject_results: list[dict]) -> dict:
    designs = sorted(subject_results[0]["results"].keys()) if subject_results else []
    out = {}
    for design in designs:
        mses = [row["results"][design]["mse"] for row in subject_results]
        r2s = [row["results"][design]["r2"] for row in subject_results]
        out[design] = {
            "mean_mse": float(np.mean(mses)),
            "mean_r2": float(np.mean(r2s)),
            "n_subjects": len(subject_results),
        }
    return out


def main() -> None:
    args = parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    subject_results = [run_subject(subject, args.task) for subject in args.subjects]
    payload = {
        "paper": "Paper 8",
        "experiment": "P8-final-extension-ds005795-nuisance-ladder-smoke",
        "status": "PASS_DS005795_MULTI_SUBJECT_NUISANCE_LADDER_INTERFACE_SMOKE",
        "subjects": args.subjects,
        "task": args.task,
        "n_subjects": len(subject_results),
        "subject_results": subject_results,
        "aggregate_results": aggregate(subject_results),
        "primary_interpretation": "interface smoke only",
        "claim_boundary": "This multi-subject global-signal smoke validates BOLD/physiology/metadata integration. It is not a transition reproducibility test and cannot support or reject measured-physiology robustness.",
    }
    (RESULTS / "p8_final_extension_ds005795_nuisance_ladder_smoke.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
