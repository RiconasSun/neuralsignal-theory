from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / ".matplotlib"))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from nibabel.processing import resample_from_to
from sklearn.linear_model import RidgeCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data_hcp_ya_2025" / "downloads" / "HCP_1200"
STATES = ROOT / "state_extraction" / "hcp_smoke"
CONNECTOMES = ROOT / "hcp_connectomes" / "bedpostx_dyad_proxy"
RESULTS = ROOT / "results"
FIGURES = ROOT / "results" / "figures"
PRIMARY_LAG = 4


def stable_seed(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)


def aparc_label_for_parcel(parcel_id: int) -> int | None:
    """Map HCP fs_LR aparc dlabel IDs to FreeSurfer aparc+aseg cortical IDs."""
    if 1 <= parcel_id <= 35:
        return 1000 + parcel_id
    if 36 <= parcel_id <= 70:
        return 2000 + (parcel_id - 35)
    return None


def zscore(x: np.ndarray) -> np.ndarray:
    mu = np.nanmean(x, axis=0, keepdims=True)
    sd = np.nanstd(x, axis=0, keepdims=True)
    sd[sd == 0] = 1.0
    return (x - mu) / sd


def normalize_connectome(g: np.ndarray) -> np.ndarray:
    g = np.asarray(g, dtype=np.float32)
    g = g + g.T
    np.fill_diagonal(g, 0.0)
    if g.max() > 0:
        g = np.log1p(g)
    row_sum = g.sum(axis=1, keepdims=True)
    row_sum[row_sum == 0] = 1.0
    return g / row_sum


def load_parcel_volume(subject: str, parcel_ids: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    subject_root = DATA / subject
    mask_img = nib.load(str(subject_root / "T1w" / "Diffusion" / "nodif_brain_mask.nii.gz"))
    aparc_img = nib.load(str(subject_root / "T1w" / "aparc+aseg.nii.gz"))
    aparc_dwi = np.asarray(resample_from_to(aparc_img, mask_img, order=0).dataobj).astype(np.int32)
    labels = np.full(aparc_dwi.shape, -1, dtype=np.int16)
    fs_to_idx = {}
    for idx, parcel in enumerate(parcel_ids.astype(int).tolist()):
        fs_id = aparc_label_for_parcel(parcel)
        if fs_id is not None:
            fs_to_idx[fs_id] = idx
            labels[aparc_dwi == fs_id] = idx
    mask = np.asarray(mask_img.dataobj) > 0
    return labels, mask


def follow_direction(
    start: np.ndarray,
    start_label: int,
    dyads: np.ndarray,
    labels: np.ndarray,
    mask: np.ndarray,
    sign: float,
    max_steps: int,
    min_steps: int,
    step_size_vox: float,
) -> int | None:
    pos = start.astype(np.float32) + 0.5
    direction_memory: np.ndarray | None = None
    shape = np.array(mask.shape)
    for step in range(max_steps):
        voxel = np.floor(pos).astype(int)
        if np.any(voxel < 0) or np.any(voxel >= shape) or not mask[tuple(voxel)]:
            return None
        direction = np.asarray(dyads[tuple(voxel)], dtype=np.float32)
        norm = float(np.linalg.norm(direction))
        if norm < 1e-4:
            return None
        direction = direction / norm
        if step == 0:
            direction = direction * sign
        elif direction_memory is not None and float(np.dot(direction, direction_memory)) < 0:
            direction = -direction
        direction_memory = direction
        pos = pos + direction * step_size_vox
        next_voxel = np.floor(pos).astype(int)
        if np.any(next_voxel < 0) or np.any(next_voxel >= shape) or not mask[tuple(next_voxel)]:
            return None
        end_label = int(labels[tuple(next_voxel)])
        if step >= min_steps and end_label >= 0 and end_label != start_label:
            return end_label
    return None


def build_connectome(subject: str, seeds_per_parcel: int, max_steps: int, min_steps: int, step_size_vox: float) -> dict:
    state_file = STATES / f"{subject}_aparc_cortical_wm_states.npz"
    if not state_file.exists():
        raise FileNotFoundError(f"missing state file: {state_file}")
    state_npz = np.load(state_file)
    parcel_ids = state_npz["parcel_ids"].astype(int)
    n = int(parcel_ids.size)
    labels, mask = load_parcel_volume(subject, parcel_ids)
    dyads_path = DATA / subject / "T1w" / "Diffusion.bedpostX" / "dyads1.nii.gz"
    dyads = np.asarray(nib.load(str(dyads_path)).dataobj, dtype=np.float32)
    rng = np.random.default_rng(stable_seed(subject))

    matrix = np.zeros((n, n), dtype=np.float32)
    seed_counts = []
    successful_paths = 0
    attempted_paths = 0
    for parcel_idx in range(n):
        coords = np.argwhere(labels == parcel_idx)
        seed_counts.append(int(coords.shape[0]))
        if coords.size == 0:
            continue
        if coords.shape[0] > seeds_per_parcel:
            coords = coords[rng.choice(coords.shape[0], size=seeds_per_parcel, replace=False)]
        for coord in coords:
            for sign in (1.0, -1.0):
                attempted_paths += 1
                end_label = follow_direction(coord, parcel_idx, dyads, labels, mask, sign, max_steps, min_steps, step_size_vox)
                if end_label is not None:
                    matrix[parcel_idx, end_label] += 1.0
                    successful_paths += 1

    normalized = normalize_connectome(matrix)
    CONNECTOMES.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        CONNECTOMES / f"{subject}_aparc68_bedpostx_dyad_proxy_connectome.npz",
        raw_counts=matrix,
        connectome=normalized,
        parcel_ids=parcel_ids,
        seeds_per_parcel=seeds_per_parcel,
        max_steps=max_steps,
        min_steps=min_steps,
        step_size_vox=step_size_vox,
    )
    density = float(np.count_nonzero(matrix) / (n * (n - 1)))
    return {
        "subject": subject,
        "connectome_file": str((CONNECTOMES / f"{subject}_aparc68_bedpostx_dyad_proxy_connectome.npz").relative_to(ROOT.parent)),
        "n_parcels": n,
        "attempted_paths": attempted_paths,
        "successful_paths": successful_paths,
        "success_rate": float(successful_paths / attempted_paths) if attempted_paths else 0.0,
        "density": density,
        "nonzero_edges": int(np.count_nonzero(matrix)),
        "min_seed_voxels_per_parcel": int(np.min(seed_counts)) if seed_counts else 0,
        "median_seed_voxels_per_parcel": float(np.median(seed_counts)) if seed_counts else 0.0,
    }


def load_connectome(subject: str) -> np.ndarray:
    path = CONNECTOMES / f"{subject}_aparc68_bedpostx_dyad_proxy_connectome.npz"
    return np.load(path)["connectome"].astype(np.float32)


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


def run_models(subjects: list[str], rng_seed: int) -> dict:
    connectomes = {subject: load_connectome(subject) for subject in subjects}
    group_mean = normalize_connectome(np.mean([connectomes[s] for s in subjects], axis=0))
    rng = np.random.default_rng(rng_seed)
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
        g_random = g_true[perm][:, perm]

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
                np.column_stack([base_train, graph_features(base_train, g_random)]),
                np.column_stack([base_test, graph_features(base_test, g_random)]),
            ),
        }
        metrics = {name: fit_predict(xtr, y_train, xte, y_test) for name, (xtr, xte) in feature_sets.items()}
        row = {
            "subject": subject,
            "swap_subject": swap_subject,
            "primary_lag_tr": PRIMARY_LAG,
            "primary_lag_seconds": PRIMARY_LAG * 0.72,
            "metrics": metrics,
            "delta_mse_true_vs_no_structure": metrics["M1_no_structure"]["mse"] - metrics["M3_true_subject"]["mse"],
            "delta_mse_true_vs_group_mean": metrics["M2_group_mean"]["mse"] - metrics["M3_true_subject"]["mse"],
            "delta_mse_true_vs_swap": metrics["Mswap_other_subject"]["mse"] - metrics["M3_true_subject"]["mse"],
            "delta_mse_true_vs_rewire": metrics["Mrewire_node_permuted"]["mse"] - metrics["M3_true_subject"]["mse"],
        }
        rows.append(row)
    return {"rows": rows}


def sign_flip_pvalue(values: np.ndarray, n_perm: int, seed: int) -> float:
    rng = np.random.default_rng(seed)
    observed = float(np.mean(values))
    signs = rng.choice([-1.0, 1.0], size=(n_perm, values.size))
    null = (signs * values[None, :]).mean(axis=1)
    return float((np.count_nonzero(null >= observed) + 1) / (n_perm + 1))


def summarize_rows(rows: list[dict], n_perm: int, seed: int) -> dict:
    comparisons = [
        "delta_mse_true_vs_no_structure",
        "delta_mse_true_vs_group_mean",
        "delta_mse_true_vs_swap",
        "delta_mse_true_vs_rewire",
    ]
    out = {}
    rng = np.random.default_rng(seed)
    for comp in comparisons:
        values = np.array([r[comp] for r in rows], dtype=float)
        boot = np.array([np.mean(rng.choice(values, size=values.size, replace=True)) for _ in range(5000)])
        out[comp] = {
            "mean": float(values.mean()),
            "median": float(np.median(values)),
            "ci95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
            "sign_flip_p_one_sided_greater_than_zero": sign_flip_pvalue(values, n_perm, seed + len(comp)),
            "n_positive_subjects": int(np.count_nonzero(values > 0)),
            "n_subjects": int(values.size),
        }
    return out


def make_figure(summary: dict, rows: list[dict]) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    labels = [
        ("vs no structure", "delta_mse_true_vs_no_structure"),
        ("vs group mean", "delta_mse_true_vs_group_mean"),
        ("vs swapped", "delta_mse_true_vs_swap"),
        ("vs rewired", "delta_mse_true_vs_rewire"),
    ]
    means = [summary[key]["mean"] for _, key in labels]
    lows = [summary[key]["mean"] - summary[key]["ci95"][0] for _, key in labels]
    highs = [summary[key]["ci95"][1] - summary[key]["mean"] for _, key in labels]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.axhline(0, color="#333333", linewidth=1)
    ax.bar([x[0] for x in labels], means, color=["#4666a5", "#6e9c5d", "#b1734f", "#8a6fb0"])
    ax.errorbar([x[0] for x in labels], means, yerr=[lows, highs], fmt="none", color="#111111", capsize=4)
    ax.set_ylabel("MSE reduction of true subject G")
    ax.set_title("Paper 5 E4-E7 structural proxy model comparisons")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(FIGURES / "paper5_e4_e7_structural_proxy_comparisons.png", dpi=180)
    plt.close(fig)

    metric_names = ["M1_no_structure", "M2_group_mean", "M3_true_subject", "Mswap_other_subject", "Mrewire_node_permuted"]
    mse = {name: [r["metrics"][name]["mse"] for r in rows] for name in metric_names}
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    ax.boxplot([mse[name] for name in metric_names], tick_labels=["M1", "M2", "M3", "swap", "rewire"], showfliers=False)
    ax.set_ylabel("Held-out MSE")
    ax.set_title("Held-out prediction error by structural model")
    fig.tight_layout()
    fig.savefig(FIGURES / "paper5_e4_e7_model_mse_boxplot.png", dpi=180)
    plt.close(fig)


def write_tables(rows: list[dict], connectome_qc: list[dict]) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    metric_names = ["M1_no_structure", "M2_group_mean", "M3_true_subject", "Mswap_other_subject", "Mrewire_node_permuted"]
    lines = [
        "subject,swap_subject,delta_mse_true_vs_no_structure,delta_mse_true_vs_group_mean,delta_mse_true_vs_swap,delta_mse_true_vs_rewire,"
        + ",".join([f"{m}_mse,{m}_r2,{m}_alpha" for m in metric_names])
    ]
    for r in rows:
        values = [
            r["subject"],
            r["swap_subject"],
            f"{r['delta_mse_true_vs_no_structure']:.10g}",
            f"{r['delta_mse_true_vs_group_mean']:.10g}",
            f"{r['delta_mse_true_vs_swap']:.10g}",
            f"{r['delta_mse_true_vs_rewire']:.10g}",
        ]
        for m in metric_names:
            values.extend([
                f"{r['metrics'][m]['mse']:.10g}",
                f"{r['metrics'][m]['r2']:.10g}",
                f"{r['metrics'][m]['alpha']:.10g}",
            ])
        lines.append(",".join(values))
    (RESULTS / "paper5_e4_e7_structural_proxy_subject_metrics.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    qc_lines = ["subject,n_parcels,attempted_paths,successful_paths,success_rate,density,nonzero_edges,min_seed_voxels_per_parcel,median_seed_voxels_per_parcel,connectome_file"]
    for q in connectome_qc:
        qc_lines.append(
            ",".join(
                [
                    q["subject"],
                    str(q["n_parcels"]),
                    str(q["attempted_paths"]),
                    str(q["successful_paths"]),
                    f"{q['success_rate']:.10g}",
                    f"{q['density']:.10g}",
                    str(q["nonzero_edges"]),
                    str(q["min_seed_voxels_per_parcel"]),
                    f"{q['median_seed_voxels_per_parcel']:.10g}",
                    q["connectome_file"],
                ]
            )
        )
    (RESULTS / "paper5_e4_connectome_proxy_qc.csv").write_text("\n".join(qc_lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Paper 5 E4-E8 with a frozen BedpostX dyad structural-connectome proxy.")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--seeds-per-parcel", type=int, default=60)
    parser.add_argument("--max-steps", type=int, default=96)
    parser.add_argument("--min-steps", type=int, default=2)
    parser.add_argument("--step-size-vox", type=float, default=1.0)
    parser.add_argument("--n-perm", type=int, default=10000)
    parser.add_argument("--rebuild-connectomes", action="store_true")
    args = parser.parse_args()

    subjects = sorted(p.name.split("_", 1)[0] for p in STATES.glob("*_aparc_cortical_wm_states.npz"))
    if args.limit:
        subjects = subjects[: args.limit]
    if len(subjects) < 3:
        raise SystemExit("Need at least 3 subjects with extracted states.")

    connectome_qc = []
    for subject in subjects:
        out_path = CONNECTOMES / f"{subject}_aparc68_bedpostx_dyad_proxy_connectome.npz"
        if args.rebuild_connectomes or not out_path.exists():
            qc = build_connectome(subject, args.seeds_per_parcel, args.max_steps, args.min_steps, args.step_size_vox)
        else:
            z = np.load(out_path)
            raw = z["raw_counts"]
            qc = {
                "subject": subject,
                "connectome_file": str(out_path.relative_to(ROOT.parent)),
                "n_parcels": int(raw.shape[0]),
                "attempted_paths": int(2 * args.seeds_per_parcel * raw.shape[0]),
                "successful_paths": int(raw.sum()),
                "success_rate": float(raw.sum() / max(1, 2 * args.seeds_per_parcel * raw.shape[0])),
                "density": float(np.count_nonzero(raw) / (raw.shape[0] * (raw.shape[0] - 1))),
                "nonzero_edges": int(np.count_nonzero(raw)),
                "min_seed_voxels_per_parcel": -1,
                "median_seed_voxels_per_parcel": -1.0,
            }
        connectome_qc.append(qc)
        print(f"connectome ready {subject} success_rate={qc['success_rate']:.3f} density={qc['density']:.3f}", flush=True)

    model_payload = run_models(subjects, rng_seed=17)
    rows = model_payload["rows"]
    summary = summarize_rows(rows, n_perm=args.n_perm, seed=23)
    gates = {
        "Gate_A_structure_matters_M3_gt_M1": bool(summary["delta_mse_true_vs_no_structure"]["ci95"][0] > 0),
        "Gate_B_individual_structure_matters_M3_gt_M2": bool(summary["delta_mse_true_vs_group_mean"]["ci95"][0] > 0),
        "Gate_C_anatomical_specificity_M3_gt_swap_and_rewire": bool(
            summary["delta_mse_true_vs_swap"]["ci95"][0] > 0 and summary["delta_mse_true_vs_rewire"]["ci95"][0] > 0
        ),
        "Gate_D_locked_replication": False,
    }
    status = "STRUCTURAL_PROXY_TEST_COMPLETE"
    if all(gates.values()):
        conclusion = "All gates passed for the BedpostX dyad proxy analysis."
    elif gates["Gate_A_structure_matters_M3_gt_M1"] and not gates["Gate_B_individual_structure_matters_M3_gt_M2"]:
        conclusion = "Proxy structural features may improve prediction over no-structure, but subject-specific superiority over group mean is not supported."
    else:
        conclusion = "The BedpostX dyad proxy analysis does not support the strong subject-specific structural-constraint hypothesis."

    payload = {
        "experiment": "P5-HCP-E4-E8-structural-proxy",
        "status": status,
        "scope": "HCP-YA 2025 100 unrelated subjects; cortical aparc68 fMRI states; subject-level structural proxy from BedpostX dyad1 tract propagation; not MRtrix ACT/SIFT2 gold-standard tractography",
        "n_subjects": len(subjects),
        "subjects": subjects,
        "primary_lag_tr": PRIMARY_LAG,
        "primary_lag_seconds": PRIMARY_LAG * 0.72,
        "connectome_method": {
            "name": "BedpostX dyad tract-propagation proxy",
            "atlas": "aparc cortical 68 parcels aligned to fMRI state order",
            "seeds_per_parcel": args.seeds_per_parcel,
            "max_steps": args.max_steps,
            "min_steps": args.min_steps,
            "step_size_vox": args.step_size_vox,
            "limitations": [
                "uses dyads1 endpoint propagation rather than full probabilistic tractography",
                "cortical-only aparc68 state representation",
                "no ACT/SIFT2 filtering",
                "no independent second HCP holdout beyond the current 100 unrelated public package",
            ],
        },
        "connectome_qc_summary": {
            "mean_success_rate": float(np.mean([q["success_rate"] for q in connectome_qc])),
            "median_success_rate": float(np.median([q["success_rate"] for q in connectome_qc])),
            "mean_density": float(np.mean([q["density"] for q in connectome_qc])),
            "median_density": float(np.median([q["density"] for q in connectome_qc])),
        },
        "summary": summary,
        "gates": gates,
        "claim_audit": {
            "can_claim_subject_specific_structural_constraint": bool(all(gates.values())),
            "can_claim_gold_standard_connectome_test": False,
            "can_claim_hcp_ya_2025_data_access_and_100_subject_state_pipeline": True,
            "allowed_conclusion": conclusion,
            "forbidden_claims": [
                "Subject-specific structural connectivity constrains brain-state dynamics in a gold-standard tractography analysis.",
                "All Paper 5 gates passed.",
                "CWP/NAP structural grounding is established.",
            ],
        },
    }
    write_tables(rows, connectome_qc)
    make_figure(summary, rows)
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "paper5_e4_e8_structural_proxy_results.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
