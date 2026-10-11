from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import nibabel as nib
import numpy as np
from sklearn.linear_model import RidgeCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
P5 = PROJECT / "paper5"
STATES = P5 / "state_extraction" / "hcp_smoke"
HCP_ROOT = P5 / "data_hcp_ya_2025" / "downloads" / "HCP_1200"
CONNECTOME_ROOT = ROOT / "structural_connectomes" / "mrtrix_act_sift2_smoke"
RESULTS = ROOT / "results"
DATA_MANIFEST = ROOT / "data_manifest"
LUT = ROOT / "resources" / "FreeSurferColorLUT.txt"
FINAL_CONNECTOME = "connectome_sift2_ext4_msmt_fsdefault84_smoke.csv"
PRIMARY_LAG = 4
EXCLUDED_PRIMARY = {"100307"}


FSDEFAULT_LABEL_TO_NAME = {
    1: "ctx-lh-bankssts",
    2: "ctx-lh-caudalanteriorcingulate",
    3: "ctx-lh-caudalmiddlefrontal",
    4: "ctx-lh-cuneus",
    5: "ctx-lh-entorhinal",
    6: "ctx-lh-fusiform",
    7: "ctx-lh-inferiorparietal",
    8: "ctx-lh-inferiortemporal",
    9: "ctx-lh-isthmuscingulate",
    10: "ctx-lh-lateraloccipital",
    11: "ctx-lh-lateralorbitofrontal",
    12: "ctx-lh-lingual",
    13: "ctx-lh-medialorbitofrontal",
    14: "ctx-lh-middletemporal",
    15: "ctx-lh-parahippocampal",
    16: "ctx-lh-paracentral",
    17: "ctx-lh-parsopercularis",
    18: "ctx-lh-parsorbitalis",
    19: "ctx-lh-parstriangularis",
    20: "ctx-lh-pericalcarine",
    21: "ctx-lh-postcentral",
    22: "ctx-lh-posteriorcingulate",
    23: "ctx-lh-precentral",
    24: "ctx-lh-precuneus",
    25: "ctx-lh-rostralanteriorcingulate",
    26: "ctx-lh-rostralmiddlefrontal",
    27: "ctx-lh-superiorfrontal",
    28: "ctx-lh-superiorparietal",
    29: "ctx-lh-superiortemporal",
    30: "ctx-lh-supramarginal",
    31: "ctx-lh-frontalpole",
    32: "ctx-lh-temporalpole",
    33: "ctx-lh-transversetemporal",
    34: "ctx-lh-insula",
    50: "ctx-rh-bankssts",
    51: "ctx-rh-caudalanteriorcingulate",
    52: "ctx-rh-caudalmiddlefrontal",
    53: "ctx-rh-cuneus",
    54: "ctx-rh-entorhinal",
    55: "ctx-rh-fusiform",
    56: "ctx-rh-inferiorparietal",
    57: "ctx-rh-inferiortemporal",
    58: "ctx-rh-isthmuscingulate",
    59: "ctx-rh-lateraloccipital",
    60: "ctx-rh-lateralorbitofrontal",
    61: "ctx-rh-lingual",
    62: "ctx-rh-medialorbitofrontal",
    63: "ctx-rh-middletemporal",
    64: "ctx-rh-parahippocampal",
    65: "ctx-rh-paracentral",
    66: "ctx-rh-parsopercularis",
    67: "ctx-rh-parsorbitalis",
    68: "ctx-rh-parstriangularis",
    69: "ctx-rh-pericalcarine",
    70: "ctx-rh-postcentral",
    71: "ctx-rh-posteriorcingulate",
    72: "ctx-rh-precentral",
    73: "ctx-rh-precuneus",
    74: "ctx-rh-rostralanteriorcingulate",
    75: "ctx-rh-rostralmiddlefrontal",
    76: "ctx-rh-superiorfrontal",
    77: "ctx-rh-superiorparietal",
    78: "ctx-rh-superiortemporal",
    79: "ctx-rh-supramarginal",
    80: "ctx-rh-frontalpole",
    81: "ctx-rh-temporalpole",
    82: "ctx-rh-transversetemporal",
    83: "ctx-rh-insula",
}


def stable_seed(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)


def aparc_label_for_parcel(parcel_id: int) -> int | None:
    if 1 <= parcel_id <= 35:
        return 1000 + parcel_id
    if 36 <= parcel_id <= 70:
        return 2000 + (parcel_id - 35)
    return None


def parse_freesurfer_lut() -> dict[int, str]:
    mapping = {}
    with LUT.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[0].isdigit():
                mapping[int(parts[0])] = parts[1]
    return mapping


def state_parcel_to_fsdefault_indices(parcel_ids: np.ndarray) -> tuple[list[int], list[dict]]:
    fs_lut = parse_freesurfer_lut()
    name_to_fsdefault = {name: label for label, name in FSDEFAULT_LABEL_TO_NAME.items()}
    indices = []
    records = []
    for state_idx, parcel_id in enumerate(parcel_ids.astype(int).tolist()):
        fs_label = aparc_label_for_parcel(parcel_id)
        fs_name = fs_lut.get(fs_label) if fs_label is not None else None
        target_label = name_to_fsdefault.get(fs_name) if fs_name else None
        if target_label is None:
            raise ValueError(f"Could not map parcel_id={parcel_id} fs_label={fs_label} fs_name={fs_name}")
        matrix_index = target_label - 1
        indices.append(matrix_index)
        records.append(
            {
                "state_index": state_idx,
                "parcel_id": parcel_id,
                "freesurfer_label": fs_label,
                "freesurfer_name": fs_name,
                "fsdefault_label": target_label,
                "fsdefault_matrix_index": matrix_index,
            }
        )
    return indices, records


def load_matrix(path: Path) -> np.ndarray:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append([float(x) for x in line.split(",")])
    return np.asarray(rows, dtype=np.float32)


def normalize_connectome(g: np.ndarray) -> np.ndarray:
    g = np.asarray(g, dtype=np.float32)
    g = g + g.T
    np.fill_diagonal(g, 0.0)
    if g.max() > 0:
        g = np.log1p(g)
    row_sum = g.sum(axis=1, keepdims=True)
    row_sum[row_sum == 0] = 1.0
    return g / row_sum


def zscore(x: np.ndarray) -> np.ndarray:
    mu = np.nanmean(x, axis=0, keepdims=True)
    sd = np.nanstd(x, axis=0, keepdims=True)
    sd[sd == 0] = 1.0
    return (x - mu) / sd


def graph_features(states: np.ndarray, g: np.ndarray) -> np.ndarray:
    return states @ g.T


def fit_predict(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray, y_test: np.ndarray) -> dict:
    model = RidgeCV(alphas=np.logspace(-3, 4, 16))
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    return {
        "mse": float(mean_squared_error(y_test, pred)),
        "r2": float(r2_score(y_test, pred, multioutput="variance_weighted")),
        "alpha": float(model.alpha_),
    }


def available_subjects() -> list[str]:
    subjects = []
    for subject_dir in sorted(p for p in CONNECTOME_ROOT.iterdir() if p.is_dir()):
        subject = subject_dir.name
        if subject in EXCLUDED_PRIMARY:
            continue
        if not (subject_dir / FINAL_CONNECTOME).exists():
            continue
        if not (STATES / f"{subject}_aparc_cortical_wm_states.npz").exists():
            continue
        subjects.append(subject)
    return subjects


def load_subject_connectome(subject: str, cortical_indices: list[int]) -> np.ndarray:
    path = CONNECTOME_ROOT / subject / FINAL_CONNECTOME
    g84 = load_matrix(path)
    g68 = g84[np.ix_(cortical_indices, cortical_indices)]
    return normalize_connectome(g68)


def load_subject_distance_graph(subject: str, parcel_ids: np.ndarray) -> np.ndarray:
    aparc_path = HCP_ROOT / subject / "T1w" / "aparc+aseg.nii.gz"
    if not aparc_path.exists():
        raise FileNotFoundError(f"Missing aparc+aseg for distance baseline: {aparc_path}")
    img = nib.load(str(aparc_path))
    data = np.asarray(img.dataobj)
    centroids = []
    for parcel_id in parcel_ids.astype(int).tolist():
        fs_label = aparc_label_for_parcel(parcel_id)
        if fs_label is None:
            raise ValueError(f"Cannot create distance baseline for parcel_id={parcel_id}")
        ijk = np.argwhere(data == fs_label)
        if ijk.size == 0:
            raise ValueError(f"Parcel label {fs_label} missing in {aparc_path}")
        xyz = nib.affines.apply_affine(img.affine, ijk)
        centroids.append(xyz.mean(axis=0))
    centroids = np.asarray(centroids, dtype=np.float32)
    delta = centroids[:, None, :] - centroids[None, :, :]
    dist = np.sqrt(np.sum(delta * delta, axis=2))
    with np.errstate(divide="ignore", invalid="ignore"):
        graph = 1.0 / (dist + 1e-6)
    np.fill_diagonal(graph, 0.0)
    return normalize_connectome(graph.astype(np.float32))


def sign_flip_pvalue(values: np.ndarray, n_perm: int, seed: int) -> float:
    rng = np.random.default_rng(seed)
    observed = float(np.mean(values))
    signs = rng.choice([-1.0, 1.0], size=(n_perm, values.size))
    null = (signs * values[None, :]).mean(axis=1)
    return float((np.count_nonzero(null >= observed) + 1) / (n_perm + 1))


def summarize(rows: list[dict]) -> dict:
    out = {}
    rng = np.random.default_rng(29)
    for comp in [
        "delta_mse_true_vs_no_structure",
        "delta_mse_true_vs_group_mean",
        "delta_mse_true_vs_swap",
        "delta_mse_true_vs_rewire",
        "delta_mse_true_vs_distance",
    ]:
        values = np.asarray([row[comp] for row in rows], dtype=float)
        boot = np.asarray([np.mean(rng.choice(values, size=values.size, replace=True)) for _ in range(5000)])
        out[comp] = {
            "mean": float(values.mean()),
            "median": float(np.median(values)),
            "ci95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
            "sign_flip_p_one_sided_greater_than_zero": sign_flip_pvalue(values, 10000, stable_seed(comp)),
            "n_positive_subjects": int(np.count_nonzero(values > 0)),
            "n_subjects": int(values.size),
        }
    return out


def write_subject_metrics(rows: list[dict]) -> None:
    path = DATA_MANIFEST / "p7_e7_preliminary_structural_model_subject_metrics.csv"
    metric_names = [
        "M1_no_structure",
        "M2_group_mean",
        "M3_true_subject",
        "Mswap_other_subject",
        "Mrewire_node_permuted",
        "Mdistance_anatomical",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "subject",
            "swap_subject",
            "delta_mse_true_vs_no_structure",
            "delta_mse_true_vs_group_mean",
            "delta_mse_true_vs_swap",
            "delta_mse_true_vs_rewire",
            "delta_mse_true_vs_distance",
        ]
        for metric in metric_names:
            fieldnames.extend([f"{metric}_mse", f"{metric}_r2", f"{metric}_alpha"])
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            flat = {key: row[key] for key in fieldnames[:7]}
            for metric in metric_names:
                flat[f"{metric}_mse"] = row["metrics"][metric]["mse"]
                flat[f"{metric}_r2"] = row["metrics"][metric]["r2"]
                flat[f"{metric}_alpha"] = row["metrics"][metric]["alpha"]
            writer.writerow(flat)


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    DATA_MANIFEST.mkdir(parents=True, exist_ok=True)
    subjects = available_subjects()
    if len(subjects) < 3:
        raise SystemExit("Need at least three QC-pass subjects with both states and P7 fs_default84 connectomes.")

    example = np.load(STATES / f"{subjects[0]}_aparc_cortical_wm_states.npz")
    parcel_ids = example["parcel_ids"].astype(int)
    cortical_indices, mapping_records = state_parcel_to_fsdefault_indices(parcel_ids)
    connectomes = {subject: load_subject_connectome(subject, cortical_indices) for subject in subjects}
    distance_graphs = {subject: load_subject_distance_graph(subject, parcel_ids) for subject in subjects}
    group_mean = normalize_connectome(np.mean([connectomes[s] for s in subjects], axis=0))
    rng = np.random.default_rng(37)
    rows = []
    for idx, subject in enumerate(subjects):
        states = np.load(STATES / f"{subject}_aparc_cortical_wm_states.npz")["states"].astype(np.float32)
        states = zscore(states)
        s_t = states[:-PRIMARY_LAG]
        y = states[PRIMARY_LAG:]
        train_idx, test_idx = train_test_split(np.arange(s_t.shape[0]), test_size=0.35, shuffle=False)
        base_train, base_test = s_t[train_idx], s_t[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        g_true = connectomes[subject]
        swap_subject = subjects[(idx + 1) % len(subjects)]
        g_swap = connectomes[swap_subject]
        perm = rng.permutation(g_true.shape[0])
        g_rewire = g_true[perm][:, perm]
        g_distance = distance_graphs[subject]
        feature_sets = {
            "M1_no_structure": (base_train, base_test),
            "M2_group_mean": (
                np.column_stack([base_train, graph_features(base_train, group_mean)]),
                np.column_stack([base_test, graph_features(base_test, group_mean)]),
            ),
            "M3_true_subject": (
                np.column_stack([base_train, graph_features(base_train, g_true)]),
                np.column_stack([base_test, graph_features(base_test, g_true)]),
            ),
            "Mswap_other_subject": (
                np.column_stack([base_train, graph_features(base_train, g_swap)]),
                np.column_stack([base_test, graph_features(base_test, g_swap)]),
            ),
            "Mrewire_node_permuted": (
                np.column_stack([base_train, graph_features(base_train, g_rewire)]),
                np.column_stack([base_test, graph_features(base_test, g_rewire)]),
            ),
            "Mdistance_anatomical": (
                np.column_stack([base_train, graph_features(base_train, g_distance)]),
                np.column_stack([base_test, graph_features(base_test, g_distance)]),
            ),
        }
        metrics = {name: fit_predict(xtr, y_train, xte, y_test) for name, (xtr, xte) in feature_sets.items()}
        rows.append(
            {
                "subject": subject,
                "swap_subject": swap_subject,
                "metrics": metrics,
                "delta_mse_true_vs_no_structure": metrics["M1_no_structure"]["mse"] - metrics["M3_true_subject"]["mse"],
                "delta_mse_true_vs_group_mean": metrics["M2_group_mean"]["mse"] - metrics["M3_true_subject"]["mse"],
                "delta_mse_true_vs_swap": metrics["Mswap_other_subject"]["mse"] - metrics["M3_true_subject"]["mse"],
                "delta_mse_true_vs_rewire": metrics["Mrewire_node_permuted"]["mse"] - metrics["M3_true_subject"]["mse"],
                "delta_mse_true_vs_distance": metrics["Mdistance_anatomical"]["mse"] - metrics["M3_true_subject"]["mse"],
            }
        )
    summary = summarize(rows)
    gates = {
        "smoke_gate_true_greater_than_no_structure": bool(summary["delta_mse_true_vs_no_structure"]["ci95"][0] > 0),
        "smoke_gate_true_greater_than_group_mean": bool(summary["delta_mse_true_vs_group_mean"]["ci95"][0] > 0),
        "smoke_gate_true_greater_than_swap_and_rewire": bool(
            summary["delta_mse_true_vs_swap"]["ci95"][0] > 0
            and summary["delta_mse_true_vs_rewire"]["ci95"][0] > 0
        ),
        "smoke_gate_true_greater_than_distance": bool(summary["delta_mse_true_vs_distance"]["ci95"][0] > 0),
    }
    payload = {
        "paper": "Paper 7",
        "experiment": "P7-E7-preliminary-structural-model-smoke",
        "status": "PASS_PRELIMINARY_STRUCTURAL_MODEL_SMOKE",
        "subjects": subjects,
        "excluded_primary_subjects": sorted(EXCLUDED_PRIMARY),
        "n_subjects": len(subjects),
        "primary_lag_tr": PRIMARY_LAG,
        "primary_lag_seconds": PRIMARY_LAG * 0.72,
        "state_space": "P5 HCP aparc cortical 68 ROI states",
        "connectome_space": "P7 MRtrix fs_default84 cropped by FreeSurfer label-name mapping to cortical 68",
        "mapping_records": mapping_records,
        "summary": summary,
        "smoke_gates": gates,
        "allowed_claim": f"A preliminary {len(subjects)}-subject model-interface smoke was run after excluding 100307 by the frozen QC rule, including an anatomical distance-only baseline derived from subject aparc+aseg parcel centroids.",
        "forbidden_claims": [
            "The 100-subject structural hypothesis was tested.",
            "Subject-specific high-fidelity structure improves brain-state transition prediction.",
            "P7 structural grounding is supported.",
        ],
    }
    write_subject_metrics(rows)
    (RESULTS / "p7_e7_preliminary_structural_model_smoke.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
