from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import nibabel as nib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
P5 = PROJECT / "paper5"
HCP = P5 / "data_hcp_ya_2025" / "downloads" / "HCP_1200"
RESULTS = ROOT / "results"
STATES = ROOT / "state_extraction" / "hcp_physio_ladder"
NUI = ROOT / "physiology" / "hcp_physio_ladder"

TR = 0.72
PHYSIO_HZ = 400.0
PRE_TRS = 4
POST_START_TRS = 6
POST_STOP_TRS = 14


def zscore(x: np.ndarray) -> np.ndarray:
    mu = np.nanmean(x, axis=0, keepdims=True)
    sd = np.nanstd(x, axis=0, keepdims=True)
    sd[~np.isfinite(sd) | (sd == 0)] = 1.0
    return (x - mu) / sd


def residualize(y: np.ndarray, confounds: np.ndarray | None) -> np.ndarray:
    if confounds is None or confounds.size == 0:
        return zscore(y)
    n = min(y.shape[0], confounds.shape[0])
    y = y[:n]
    confounds = confounds[:n]
    x = np.column_stack([np.ones(n), zscore(confounds)])
    beta, *_ = np.linalg.lstsq(x, zscore(y), rcond=None)
    return zscore(y) - x @ beta


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


def load_motion(path: Path) -> np.ndarray:
    motion = np.loadtxt(path)
    deriv = np.vstack([np.zeros((1, motion.shape[1])), np.diff(motion, axis=0)])
    squared = motion ** 2
    deriv_squared = deriv ** 2
    return np.column_stack([motion, deriv, squared, deriv_squared])


def load_physio(path: Path, n_trs: int) -> np.ndarray:
    raw = np.loadtxt(path)
    raw = raw[:, :3]
    tr_index = np.floor(np.arange(raw.shape[0]) / PHYSIO_HZ / TR).astype(int)
    rows = []
    for tr in range(n_trs):
        seg = raw[tr_index == tr]
        if seg.size == 0:
            rows.append(np.zeros(9, dtype=float))
            continue
        trigger = seg[:, 0]
        resp = seg[:, 1]
        pulse = seg[:, 2]
        rows.append(
            np.array(
                [
                    trigger.mean(),
                    trigger.std(),
                    resp.mean(),
                    resp.std(),
                    np.percentile(resp, 90) - np.percentile(resp, 10),
                    pulse.mean(),
                    pulse.std(),
                    np.percentile(pulse, 90) - np.percentile(pulse, 10),
                    len(seg),
                ],
                dtype=float,
            )
        )
    features = np.vstack(rows)
    deriv = np.vstack([np.zeros((1, features.shape[1])), np.diff(features, axis=0)])
    return np.column_stack([features, deriv])


def load_block_events(ev_dir: Path) -> list[dict]:
    events = []
    for label in ["0bk", "2bk"]:
        for domain in ["body", "faces", "places", "tools"]:
            path = ev_dir / f"{label}_{domain}.txt"
            if not path.exists() or path.stat().st_size == 0:
                continue
            arr = np.loadtxt(path)
            arr = np.atleast_2d(arr)
            for onset, duration, amp in arr[:, :3]:
                events.append(
                    {
                        "onset": float(onset),
                        "duration": float(duration),
                        "amplitude": float(amp),
                        "transition_label": f"{label}_block_start",
                        "domain": domain,
                    }
                )
    return sorted(events, key=lambda row: row["onset"])


def transition_features(states: np.ndarray, events: list[dict], subject: str, run: str) -> list[dict]:
    rows = []
    for event in events:
        onset_tr = int(round(event["onset"] / TR))
        pre_start = onset_tr - PRE_TRS
        pre_stop = onset_tr
        post_start = onset_tr + POST_START_TRS
        post_stop = onset_tr + POST_STOP_TRS
        if pre_start < 0 or post_stop > states.shape[0]:
            continue
        vec = states[post_start:post_stop].mean(axis=0) - states[pre_start:pre_stop].mean(axis=0)
        row = {
            "subject": subject,
            "run": run,
            "group": f"{subject}_{run}",
            "transition_label": event["transition_label"],
            "domain": event["domain"],
            "onset": event["onset"],
        }
        for idx, value in enumerate(vec):
            row[f"roi_{idx:03d}"] = float(value)
        rows.append(row)
    return rows


def centroid_similarity(rows: list[dict], feature_cols: list[str]) -> dict:
    by_label = {}
    for row in rows:
        by_label.setdefault(row["transition_label"], []).append(np.array([row[c] for c in feature_cols], dtype=float))
    if len(by_label) < 2:
        return {"same_transition_similarity": None, "different_transition_similarity": None, "contrast": None}
    same = []
    cents = {}
    for label, mats in by_label.items():
        mat = np.vstack(mats)
        odd = mat[::2].mean(axis=0)
        even = mat[1::2].mean(axis=0)
        same.append(cosine(odd, even))
        cents[label] = mat.mean(axis=0)
    labels = sorted(cents)
    diff = cosine(cents[labels[0]], cents[labels[1]])
    return {
        "same_transition_similarity": float(np.nanmean(same)),
        "different_transition_similarity": float(diff),
        "contrast": float(np.nanmean(same) - diff),
    }


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    den = np.linalg.norm(a) * np.linalg.norm(b)
    return float(a @ b / den) if den else float("nan")


def classify(rows: list[dict], feature_cols: list[str]) -> dict:
    x = np.asarray([[row[c] for c in feature_cols] for row in rows], dtype=float)
    y = np.asarray([row["transition_label"] for row in rows])
    groups = np.asarray([row["group"] for row in rows])
    logo = LeaveOneGroupOut()
    preds = []
    truth = []
    folds = []
    for train, test in logo.split(x, y, groups):
        model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, solver="liblinear", random_state=8))
        model.fit(x[train], y[train])
        pred = model.predict(x[test])
        preds.extend(pred.tolist())
        truth.extend(y[test].tolist())
        folds.append({"heldout_group": str(groups[test][0]), "n_test": int(len(test)), "accuracy": float(accuracy_score(y[test], pred))})
    return {"accuracy": float(accuracy_score(truth, preds)), "n_predictions": len(preds), "n_folds": len(folds), "folds": folds}


def sign_flip_p(values: np.ndarray) -> float:
    obs = float(np.mean(values))
    rng = np.random.default_rng(8)
    null = []
    for _ in range(10000):
        signs = rng.choice([-1, 1], size=values.size)
        null.append(float(np.mean(values * signs)))
    return float((sum(v >= obs for v in null) + 1) / (len(null) + 1))


def write_feature_csv(name: str, rows: list[dict]) -> Path:
    path = STATES / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return path
    fields = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    STATES.mkdir(parents=True, exist_ok=True)
    NUI.mkdir(parents=True, exist_ok=True)
    subjects = []
    for subject_dir in sorted(HCP.iterdir()):
        if not subject_dir.is_dir():
            continue
        lr = subject_dir / "MNINonLinear/Results/tfMRI_WM_LR/tfMRI_WM_LR_Physio_log.txt"
        rl = subject_dir / "MNINonLinear/Results/tfMRI_WM_RL/tfMRI_WM_RL_Physio_log.txt"
        if lr.exists() and rl.exists():
            subjects.append(subject_dir.name)
    if not subjects:
        raise SystemExit("No subjects with local HCP WM Physio_log files found.")

    missing_required = []
    for subject in subjects:
        subject_root = HCP / subject
        dlabel = subject_root / "MNINonLinear" / "fsaverage_LR32k" / f"{subject}.aparc.32k_fs_LR.dlabel.nii"
        if not dlabel.exists():
            missing_required.append(str(dlabel))
        for run in ["tfMRI_WM_LR", "tfMRI_WM_RL"]:
            run_dir = subject_root / "MNINonLinear" / "Results" / run
            required = [
                run_dir / f"{run}_Atlas_MSMAll.dtseries.nii",
                run_dir / "Movement_Regressors.txt",
                run_dir / f"{run}_Physio_log.txt",
                run_dir / "EVs",
            ]
            for path in required:
                if not path.exists():
                    missing_required.append(str(path))
    if missing_required:
        existing_result = RESULTS / "p8_e1_e6_hcp_physio_ladder_smoke.json"
        payload = {
            "experiment": "P8-E1-E6-HCP-WM-measured-physio-ladder-smoke",
            "status": "NEED_HCP_CIFTI_AND_MATCHED_RUN_FILES_FOR_RAW_REPRODUCTION",
            "n_subjects_with_physio_logs": len(subjects),
            "n_missing_required_paths": len(missing_required),
            "missing_required_paths_preview": missing_required[:40],
            "existing_result_available": existing_result.exists(),
            "existing_result_path": str(existing_result) if existing_result.exists() else None,
            "claim_boundary": "The HCP measured-physiology ladder cannot be regenerated from raw CIFTI inputs in this environment because matched large HCP dtseries/dlabel/EV/motion files are incomplete locally. Existing result artifacts may be used for package assembly, but this step is not a fresh raw-data rerun.",
        }
        (RESULTS / "p8_e1_e6_hcp_physio_ladder_preflight_blocker.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(payload, indent=2, sort_keys=True))
        sys.exit(0 if existing_result.exists() else 2)

    ladder = {
        "N0_raw_basic": {"motion": False, "resp": False, "pulse": False},
        "N1_motion": {"motion": True, "resp": False, "pulse": False},
        "N2_respiration": {"motion": False, "resp": True, "pulse": False},
        "N3_cardiac_pulse": {"motion": False, "resp": False, "pulse": True},
        "N4_motion_respiration_cardiac": {"motion": True, "resp": True, "pulse": True},
    }
    all_results = {}
    feature_files = {}
    for rung, cfg in ladder.items():
        rows = []
        nuisance_meta = []
        for subject in subjects:
            subject_root = HCP / subject
            dlabel = subject_root / "MNINonLinear" / "fsaverage_LR32k" / f"{subject}.aparc.32k_fs_LR.dlabel.nii"
            for run in ["tfMRI_WM_LR", "tfMRI_WM_RL"]:
                run_dir = subject_root / "MNINonLinear" / "Results" / run
                states, parcel_ids = parcellate_cortex(run_dir / f"{run}_Atlas_MSMAll.dtseries.nii", dlabel)
                confs = []
                if cfg["motion"]:
                    confs.append(load_motion(run_dir / "Movement_Regressors.txt"))
                if cfg["resp"] or cfg["pulse"]:
                    phys = load_physio(run_dir / f"{run}_Physio_log.txt", states.shape[0])
                    if cfg["resp"] and cfg["pulse"]:
                        confs.append(phys)
                    elif cfg["resp"]:
                        confs.append(phys[:, [2, 3, 4, 11, 12, 13]])
                    elif cfg["pulse"]:
                        confs.append(phys[:, [5, 6, 7, 14, 15, 16]])
                conf = np.column_stack(confs) if confs else None
                cleaned = residualize(states, conf)
                events = load_block_events(run_dir / "EVs")
                rows.extend(transition_features(cleaned, events, subject, run))
                nuisance_meta.append(
                    {
                        "subject": subject,
                        "run": run,
                        "n_timepoints": int(states.shape[0]),
                        "n_parcels": int(len(parcel_ids)),
                        "n_confounds": int(conf.shape[1]) if conf is not None else 0,
                        "n_events": len(events),
                    }
                )
        feature_cols = [c for c in rows[0] if c.startswith("roi_")] if rows else []
        sim = centroid_similarity(rows, feature_cols)
        clf = classify(rows, feature_cols) if rows else {"accuracy": None}
        by_subject = []
        for subject in subjects:
            subj_rows = [row for row in rows if row["subject"] == subject]
            if subj_rows:
                by_subject.append({"subject": subject, **centroid_similarity(subj_rows, feature_cols)})
        contrasts = np.array([r["contrast"] for r in by_subject if r.get("contrast") is not None], dtype=float)
        stats = {
            "subject_mean_transition_contrast": float(np.mean(contrasts)) if contrasts.size else None,
            "subject_bootstrap_ci95": None,
            "subject_sign_flip_p": sign_flip_p(contrasts) if contrasts.size else None,
            "n_subjects_with_contrast": int(contrasts.size),
        }
        if contrasts.size:
            rng = np.random.default_rng(8)
            boots = [float(np.mean(rng.choice(contrasts, size=contrasts.size, replace=True))) for _ in range(5000)]
            stats["subject_bootstrap_ci95"] = [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]
        feature_path = write_feature_csv(f"p8_{rung}_transition_features.csv", rows)
        feature_files[rung] = str(feature_path)
        all_results[rung] = {
            "n_rows": len(rows),
            "n_subjects": len(subjects),
            "nuisance_meta": nuisance_meta,
            "same_vs_different_transition": sim,
            "leave_one_run_out_classification": clf,
            "subject_level_statistics": stats,
        }

    gates = {
        "Gate_A_raw_transition_reproduced": bool(all_results["N0_raw_basic"]["same_vs_different_transition"]["contrast"] and all_results["N0_raw_basic"]["same_vs_different_transition"]["contrast"] > 0),
        "Gate_B_measured_motion_survival": bool(all_results["N1_motion"]["same_vs_different_transition"]["contrast"] and all_results["N1_motion"]["same_vs_different_transition"]["contrast"] > 0),
        "Gate_C_measured_physiology_survival": bool(all_results["N4_motion_respiration_cardiac"]["same_vs_different_transition"]["contrast"] and all_results["N4_motion_respiration_cardiac"]["same_vs_different_transition"]["contrast"] > 0),
        "Gate_D_aggressive_nuisance_survival": False,
        "Gate_E_external_replication": False,
    }
    payload = {
        "experiment": "P8-E1-E6-HCP-WM-measured-physio-ladder-smoke",
        "status": "PASS_P8_E1_E6_MEASURED_PHYSIO_SMOKE" if gates["Gate_A_raw_transition_reproduced"] else "FAIL_RAW_TRANSITION_NOT_REPRODUCED",
        "scope": f"{len(subjects)}-subject / {len(subjects) * 2}-run HCP-YA WM measured-physiology smoke using available downloaded Physio_log files; not full Paper 8 final.",
        "subjects": subjects,
        "rung_results": all_results,
        "feature_files": feature_files,
        "gates": gates,
        "claim_boundary": "This is a measured-physiology smoke test only. It cannot support full P8 survival, physiology-elimination, or neural-origin claims.",
        "forbidden_claims": [
            "physiology eliminated",
            "motion fully excluded",
            "neural origin proven",
            "CWP validated",
            "NAP validated",
            "Paper 8 is complete",
        ],
    }
    (RESULTS / "p8_e1_e6_hcp_physio_ladder_smoke.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
