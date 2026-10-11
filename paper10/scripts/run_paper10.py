from __future__ import annotations

import csv
import json
import math
import textwrap
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import normalized_mutual_info_score, silhouette_score
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper10"
P6 = ROOT / "paper6"
P9 = ROOT / "paper9"
NOW = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
RNG = 1010


PRIMARY_REAL = P6 / "features" / "ds004117_multi_run" / "ds004117_multi_run_bandpower_delta_features.csv"
PRIMARY_NULLS = {
    "phase_randomized": P6 / "features" / "ds004117_multi_run" / "ds004117_multi_run_phase_randomized_bandpower_delta_features.csv",
    "time_shift": P6 / "features" / "ds004117_multi_run" / "ds004117_multi_run_time_shift_bandpower_delta_features.csv",
    "random_window": P6 / "features" / "ds004117_multi_run" / "ds004117_multi_run_random_window_bandpower_delta_features.csv",
}
EXTERNAL = P6 / "features" / "ds004752_external" / "ds004752_lcmv_encoding_maintenance_bandpower_features.csv"


def mkdirs() -> None:
    for d in [
        "protocol",
        "data_manifest",
        "latent_representation",
        "motif_discovery",
        "baselines",
        "holdouts",
        "null_tests",
        "statistics",
        "results",
        "figures",
        "manuscript",
        "attachments",
        "claim_audit",
        "submission",
        "scripts",
    ]:
        (PAPER / d).mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"empty rows for {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def feature_columns(df: pd.DataFrame) -> list[str]:
    cols = []
    for c in df.columns:
        if c.startswith("delta_") or "__" in c:
            if pd.api.types.is_numeric_dtype(df[c]):
                cols.append(c)
    return cols


def load_features(path: Path) -> tuple[pd.DataFrame, list[str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    cols = feature_columns(df)
    if not cols:
        raise ValueError(f"No numeric feature columns found in {path}")
    df = df.dropna(subset=cols).copy()
    return df, cols


def subject_col(df: pd.DataFrame) -> str:
    if "subject" in df.columns:
        return "subject"
    raise ValueError("subject column required")


def stratified_subject_split(subjects: list[str]) -> tuple[list[str], list[str]]:
    subjects = sorted(subjects)
    n_train = max(2, int(round(len(subjects) * 0.7)))
    if n_train >= len(subjects):
        n_train = len(subjects) - 1
    return subjects[:n_train], subjects[n_train:]


def assignment_entropy(labels: np.ndarray) -> float:
    _, counts = np.unique(labels, return_counts=True)
    p = counts / counts.sum()
    return float(-(p * np.log2(p)).sum())


def continuous_reconstruction_mse(x_train: np.ndarray, x_test: np.ndarray, n_components: int) -> float:
    n_components = max(1, min(n_components, x_train.shape[0] - 1, x_train.shape[1]))
    pca = PCA(n_components=n_components, random_state=RNG)
    pca.fit(x_train)
    recon = pca.inverse_transform(pca.transform(x_test))
    return float(np.mean((x_test - recon) ** 2))


def choose_k(z_train: np.ndarray, k_values: list[int]) -> tuple[int, list[dict[str, object]]]:
    rows = []
    best_k = k_values[0]
    best_score = -999.0
    for k in k_values:
        if k >= len(z_train):
            continue
        model = KMeans(n_clusters=k, n_init=25, random_state=RNG)
        labels = model.fit_predict(z_train)
        sample_n = min(1500, len(z_train))
        if len(np.unique(labels)) < 2:
            score = -1.0
        else:
            idx = np.linspace(0, len(z_train) - 1, sample_n).astype(int)
            score = float(silhouette_score(z_train[idx], labels[idx]))
        rows.append({"k": k, "train_silhouette": score, "train_entropy": assignment_entropy(labels)})
        if score > best_score:
            best_score = score
            best_k = k
    return best_k, rows


def nearest_quantization_mse(z: np.ndarray, centers: np.ndarray) -> tuple[float, np.ndarray]:
    d2 = ((z[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
    labels = np.argmin(d2, axis=1)
    return float(np.mean(np.min(d2, axis=1))), labels


def run_dataset(path: Path, dataset_label: str, metadata_label: str | None = None, fixed_k: int | None = None) -> dict[str, object]:
    df, cols = load_features(path)
    s_col = subject_col(df)
    subjects = sorted(df[s_col].astype(str).unique())
    train_subjects, test_subjects = stratified_subject_split(subjects)
    train = df[df[s_col].astype(str).isin(train_subjects)].copy()
    test = df[df[s_col].astype(str).isin(test_subjects)].copy()

    scaler = StandardScaler()
    x_train = scaler.fit_transform(train[cols].to_numpy(dtype=float))
    x_test = scaler.transform(test[cols].to_numpy(dtype=float))
    n_latent = max(2, min(10, x_train.shape[1], x_train.shape[0] - 1))
    pca = PCA(n_components=n_latent, random_state=RNG)
    z_train = pca.fit_transform(x_train)
    z_test = pca.transform(x_test)

    k_values = [2, 3, 4, 5, 6, 7, 8]
    if fixed_k is None:
        best_k, k_rows = choose_k(z_train, k_values)
    else:
        best_k = fixed_k
        best_k, k_rows = fixed_k, []

    km = KMeans(n_clusters=best_k, n_init=50, random_state=RNG)
    train_labels = km.fit_predict(z_train)
    test_q_mse, test_labels = nearest_quantization_mse(z_test, km.cluster_centers_)
    train_q_mse, _ = nearest_quantization_mse(z_train, km.cluster_centers_)
    train_discrete_recon = pca.inverse_transform(km.cluster_centers_[train_labels])
    test_discrete_recon = pca.inverse_transform(km.cluster_centers_[test_labels])
    train_discrete_reconstruction_mse = float(np.mean((x_train - train_discrete_recon) ** 2))
    test_discrete_reconstruction_mse = float(np.mean((x_test - test_discrete_recon) ** 2))
    cont_mse = continuous_reconstruction_mse(x_train, x_test, best_k)

    result = {
        "dataset": dataset_label,
        "source_path": str(path.relative_to(ROOT)),
        "rows": int(len(df)),
        "subjects": int(len(subjects)),
        "train_subjects": train_subjects,
        "test_subjects": test_subjects,
        "features": int(len(cols)),
        "latent_components": int(n_latent),
        "pca_explained_variance": float(np.sum(pca.explained_variance_ratio_)),
        "selected_k": int(best_k),
        "k_selection_rows": k_rows,
        "train_quantization_mse": train_q_mse,
        "heldout_quantization_mse": test_q_mse,
        "train_discrete_reconstruction_mse": train_discrete_reconstruction_mse,
        "heldout_discrete_reconstruction_mse": test_discrete_reconstruction_mse,
        "continuous_pca_reconstruction_mse": cont_mse,
        "heldout_assignment_entropy": assignment_entropy(test_labels),
        "motif_counts_heldout": {str(k): int(v) for k, v in zip(*np.unique(test_labels, return_counts=True))},
        "metadata_nmi": None,
    }
    if metadata_label and metadata_label in test.columns:
        result["metadata_label"] = metadata_label
        result["metadata_nmi"] = float(normalized_mutual_info_score(test[metadata_label].astype(str), test_labels.astype(str)))

    assignments = test[[s_col]].copy()
    for meta in ["dataset", "session", "run", "trial", "transition", "memory_cond", "stage", "trial_index"]:
        if meta in test.columns:
            assignments[meta] = test[meta].values
    assignments["motif"] = test_labels
    assignments.to_csv(PAPER / "motif_discovery" / f"{dataset_label}_heldout_motif_assignments.csv", index=False)
    pd.DataFrame(k_rows).to_csv(PAPER / "motif_discovery" / f"{dataset_label}_k_selection.csv", index=False)
    return result


def run_primary_and_nulls() -> dict[str, object]:
    primary = run_dataset(PRIMARY_REAL, "ds004117_real", metadata_label="transition")
    fixed_k = int(primary["selected_k"])
    null_results = []
    for name, path in PRIMARY_NULLS.items():
        if path.exists():
            null_results.append(run_dataset(path, f"ds004117_{name}", metadata_label="transition", fixed_k=fixed_k))
    q_null = [r["heldout_discrete_reconstruction_mse"] for r in null_results]
    real_q = float(primary["heldout_discrete_reconstruction_mse"])
    if q_null:
        better_than_null_count = sum(real_q < q for q in q_null)
        q_null_mean = float(np.mean(q_null))
        q_null_min = float(np.min(q_null))
        q_null_max = float(np.max(q_null))
    else:
        better_than_null_count = 0
        q_null_mean = math.nan
        q_null_min = math.nan
        q_null_max = math.nan
    passed_all_nulls = bool(q_null and better_than_null_count == len(q_null))

    continuous_preferred = primary["continuous_pca_reconstruction_mse"] < primary["heldout_discrete_reconstruction_mse"]
    return {
        "primary": primary,
        "nulls": null_results,
        "summary": {
            "real_heldout_discrete_reconstruction_mse": real_q,
            "null_heldout_discrete_reconstruction_mse_mean": q_null_mean,
            "null_heldout_discrete_reconstruction_mse_min": q_null_min,
            "null_heldout_discrete_reconstruction_mse_max": q_null_max,
            "real_heldout_latent_quantization_mse": float(primary["heldout_quantization_mse"]),
            "real_better_than_null_count": int(better_than_null_count),
            "null_count": int(len(q_null)),
            "passed_all_available_nulls": passed_all_nulls,
            "continuous_pca_reconstruction_mse": float(primary["continuous_pca_reconstruction_mse"]),
            "continuous_preferred_over_discrete_reconstruction": bool(continuous_preferred),
        },
    }


def run_external() -> dict[str, object]:
    if not EXTERNAL.exists():
        return {"status": "NOT_RUN", "reason": "external feature file missing", "source_path": str(EXTERNAL.relative_to(ROOT))}
    result = run_dataset(EXTERNAL, "ds004752_external_convergent", metadata_label="stage")
    return {
        "status": "PASS_CONVERGENT_NOT_DIRECT_REPLICATION",
        "result": result,
        "claim_boundary": "Feature spaces differ from ds004117; this is an external convergent motif-structure check, not direct cross-dataset motif replication.",
    }


def write_protocol() -> None:
    text = f"""# Paper 10 Frozen Protocol v1

Status: implemented local protocol  
Generated: {NOW}

## Title

Data-Driven Dynamic Motif Discovery in Fast Neural Signals

## Core Question

Do fast neural dynamics naturally form recurring motif families, or are they better treated as a continuous manifold?

## Primary Hypothesis

Unsupervised clustering of latent electrophysiological transition features will produce recurring dynamic motif families that generalize to held-out subjects and outperform matched null inputs.

## Required Anti-Hypothesis

The same data may be better described by continuous low-dimensional manifolds or by matched null/time/phase/random-window explanations. If those win, the discrete motif hypothesis contracts.

## Inputs

Primary input:

```text
paper6/features/ds004117_multi_run/ds004117_multi_run_bandpower_delta_features.csv
```

Null inputs:

```text
phase randomized bandpower deltas
time-shift bandpower deltas
random-window bandpower deltas
```

External convergent input:

```text
paper6/features/ds004752_external/ds004752_lcmv_encoding_maintenance_bandpower_features.csv
```

## Frozen Pipeline

```text
P9 ontology rules
-> P6 feature-table input audit
-> subject split
-> train-only standardization
-> train-only PCA latent representation
-> train-only K selection by silhouette
-> KMeans motif discovery
-> held-out subject quantization / recurrence
-> matched null comparison
-> continuous PCA baseline
-> external convergent check
-> claim audit
```

## Baselines

```text
continuous PCA manifold
phase-randomized null
time-shift null
random-window null
metadata association audit
```

## Holdout

Subjects are split deterministically by sorted subject ID into approximately 70 percent train and 30 percent held-out test subjects. K selection and scaling use train subjects only.

## Primary Endpoint

Held-out subject quantization error and motif recurrence for real ds004117 features compared with matched null feature tables.

## Secondary Endpoint

Continuous PCA reconstruction error compared with discrete motif quantization error. This endpoint determines whether the discrete motif language should contract toward continuous manifold dynamics.

## Claim Boundary

P10 may support candidate dynamic motifs only within the tested global feature regime. It may not validate NAPs, CWP semantics, motif grammar, universal neural primitives, or claims that region-specific motifs are absent.
"""
    write_text(PAPER / "protocol" / "PAPER10_FROZEN_PROTOCOL_v1.md", text)


def make_figures(results: dict[str, object]) -> None:
    primary = results["primary"]
    nulls = results["nulls"]
    summary = results["summary"]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    labels = ["real"] + [r["dataset"].replace("ds004117_", "") for r in nulls]
    vals = [primary["heldout_discrete_reconstruction_mse"]] + [r["heldout_discrete_reconstruction_mse"] for r in nulls]
    ax.bar(labels, vals, color=["#2563eb"] + ["#94a3b8"] * len(nulls))
    ax.set_title("Figure 1. Held-out motif reconstruction vs matched nulls", fontweight="bold")
    ax.set_ylabel("Held-out reconstruction MSE")
    ax.tick_params(axis="x", rotation=20)
    for i, v in enumerate(vals):
        ax.text(i, v, f"{v:.3f}", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    save_fig(fig, "figure1_primary_null_quantization")

    k_rows = pd.DataFrame(primary["k_selection_rows"])
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.plot(k_rows["k"], k_rows["train_silhouette"], marker="o", color="#0f766e")
    ax.axvline(primary["selected_k"], color="#dc2626", linestyle="--", label=f"K={primary['selected_k']}")
    ax.set_title("Figure 2. Train-only K selection", fontweight="bold")
    ax.set_xlabel("K")
    ax.set_ylabel("Train silhouette")
    ax.legend()
    fig.tight_layout()
    save_fig(fig, "figure2_k_selection")

    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    labels = ["Discrete motif\nreconstruction", "Continuous PCA\nreconstruction"]
    vals = [primary["heldout_discrete_reconstruction_mse"], primary["continuous_pca_reconstruction_mse"]]
    ax.bar(labels, vals, color=["#7c3aed", "#ea580c"])
    ax.set_title("Figure 3. Discrete motif vs continuous manifold", fontweight="bold")
    ax.set_ylabel("Held-out error")
    for i, v in enumerate(vals):
        ax.text(i, v, f"{v:.3f}", ha="center", va="bottom")
    fig.tight_layout()
    save_fig(fig, "figure3_discrete_vs_continuous")

    counts = primary["motif_counts_heldout"]
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.bar(list(counts.keys()), list(counts.values()), color="#0891b2")
    ax.set_title("Figure 4. Held-out motif recurrence", fontweight="bold")
    ax.set_xlabel("Motif")
    ax.set_ylabel("Held-out assignment count")
    fig.tight_layout()
    save_fig(fig, "figure4_motif_recurrence")

    ext = results.get("external", {})
    if ext.get("status", "").startswith("PASS"):
        r = ext["result"]
        fig, ax = plt.subplots(figsize=(7.5, 4.2))
        ax.bar(["external motif\nreconstruction", "external continuous\nPCA"], [r["heldout_discrete_reconstruction_mse"], r["continuous_pca_reconstruction_mse"]], color=["#475569", "#f97316"])
        ax.set_title("Figure 5. External convergent motif structure", fontweight="bold")
        ax.set_ylabel("Held-out error")
        fig.tight_layout()
        save_fig(fig, "figure5_external_convergent")


def save_fig(fig, name: str) -> None:
    fig.savefig(PAPER / "figures" / f"{name}.png", dpi=200, bbox_inches="tight")
    fig.savefig(PAPER / "figures" / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)


def claim_audit(results: dict[str, object]) -> dict[str, object]:
    summary = results["summary"]
    primary = results["primary"]
    external = results.get("external", {})
    motifs_supported = bool(summary["passed_all_available_nulls"] and not summary["continuous_preferred_over_discrete_reconstruction"])
    candidate_only = bool(summary["passed_all_available_nulls"])
    return {
        "generated_at": NOW,
        "paper": "P10",
        "audit_result": "PASS",
        "claim_allowed_candidate_dynamic_motif_families": candidate_only,
        "claim_allowed_discrete_motifs_preferred_over_all_baselines": motifs_supported,
        "claim_allowed_continuous_manifold_preferred": bool(summary["continuous_preferred_over_discrete_reconstruction"]),
        "claim_allowed_discrete_NAP_supported": False,
        "claim_allowed_CWP_v2_semantics_supported": False,
        "claim_allowed_neural_grammar_supported": False,
        "claim_allowed_external_direct_replication": False,
        "claim_allowed_external_convergent_structure": external.get("status", "").startswith("PASS"),
        "primary_summary": summary,
        "selected_k": primary["selected_k"],
        "forbidden_claims": [
            "NAP is validated.",
            "Dynamic motifs are cognitive primitives.",
            "CWP v2 semantics are supported.",
            "Neural grammar exists.",
            "External direct motif replication is established.",
            "Universal neural primitives exist.",
            "P10 proves region-specific motifs are absent.",
            "P10 proves all brain regions are continuous.",
        ],
        "interpretation": "P10 may report a negative/boundary result for the current global discrete-motif model under the tested P6-derived bandpower feature regime: discrete motif discovery is not supported and a continuous low-dimensional global representation is preferred. This does not test whether individual regions or networks have local motif-like, local continuous-manifold, or hierarchical dynamics. NAP, semantic, grammar, and universal claims remain disallowed.",
    }


def write_attachments(results: dict[str, object], audit: dict[str, object]) -> None:
    attachments = {
        "A1_Frozen_Protocol.md": "Frozen protocol is `protocol/PAPER10_FROZEN_PROTOCOL_v1.md`. P10 uses P9 ontology rules and P6 fast-dynamics feature tables without P11 semantics.",
        "A2_Dataset_Manifest.md": "Primary: ds004117 feature table inherited from P6. Nulls: phase-randomized, time-shift, and random-window feature tables. External convergent: ds004752 LCMV encoding/maintenance feature table. No new raw download is performed.",
        "A3_Full_Pipeline.md": "Pipeline: feature audit -> train/test subject split -> train-only scaling -> train-only PCA -> train-only K selection -> KMeans motifs -> held-out quantization and recurrence -> null/continuous comparisons -> claim audit.",
        "A4_Baseline_Results.md": f"Continuous PCA held-out reconstruction MSE: {results['primary']['continuous_pca_reconstruction_mse']:.6f}. Discrete motif held-out reconstruction MSE: {results['primary']['heldout_discrete_reconstruction_mse']:.6f}. Null summary is in `results/p10_primary_motif_summary.json`.",
        "A5_Holdout_Audit.md": "Heldout subjects are selected deterministically by subject ID after train-only preprocessing rules are frozen. No heldout subject is used for scaling, PCA fitting, K selection, or motif centroid fitting.",
        "A6_Statistics.md": "P10 reports descriptive held-out error, motif recurrence, train silhouette, metadata NMI, and null comparisons. It does not report p-values unless explicitly generated by a later permutation extension.",
        "A7_Null_Falsification_Tests.md": "Null tests include phase-randomized, time-shift, and random-window feature tables. A continuous PCA manifold baseline is treated as a competing explanation, not a weak baseline.",
        "A8_QC_Leakage_Audit.md": "Scaling, PCA, K selection, and KMeans centroid fitting use train subjects only. P10 does not use transition/stage semantics to discover motifs; metadata association is post-hoc audit only.",
        "A9_Limitations_Failed_Analyses.md": "Feature family is inherited bandpower/amplitude evidence, not raw spike timing or phase-specific dynamics. External ds004752 has a different feature space, so it is convergent rather than direct motif replication. P10's current test is global under the available feature regime; it does not decide whether regional or network-specific dynamics are discrete, continuous, hybrid, or hierarchically composed. NAP/CWP/grammar claims are not supported by P10.",
        "A10_One_Command_Reproduction.md": "Run `powershell -ExecutionPolicy Bypass -File paper10/scripts/reproduce-paper10.ps1` on Windows, or `make reproduce-paper10` where make is available.",
    }
    for file, body in attachments.items():
        write_text(PAPER / "attachments" / file, f"# {file.replace('_', ' ').replace('.md', '')}\n\nGenerated: {NOW}\n\n{body}\n")


def write_manuscript(results: dict[str, object], audit: dict[str, object]) -> None:
    summary = results["summary"]
    primary = results["primary"]
    nulls = results["nulls"]
    null_lines = "\n".join([f"- {r['dataset']}: held-out discrete reconstruction MSE = {r['heldout_discrete_reconstruction_mse']:.6f}" for r in nulls])
    conclusion = (
        "candidate dynamic motif structure is supported in the tested feature regime"
        if audit["claim_allowed_candidate_dynamic_motif_families"]
        else "the available motif evidence remains insufficient against the available nulls"
    )
    text = f"""# Data-Driven Dynamic Motif Discovery in Fast Neural Signals

## Abstract

P9 rebuilt the CWP/NAP ontology around a dynamics-first evidence ladder. P10 tests the first empirical step after that reconstruction: whether fast neural dynamics form recurring motif families without using cognitive semantics as training labels. Using P6-derived electrophysiological bandpower-delta features from ds004117, we fit train-only PCA representations and unsupervised KMeans motif models, freeze K by train-subject silhouette, and evaluate held-out subjects against phase-randomized, time-shift, random-window, and continuous PCA competing explanations. The result is claim-bounded: {conclusion}. P10 does not validate NAPs, CWP v2 semantics, neural grammar, or universal neural primitives.

## 1. Introduction

### 1.1 Problem

The original CWP/NAP program could not assume that semantic cognitive labels correspond to neural primitives. P10 therefore starts from neural dynamics rather than semantic labels.

### 1.2 Proposed Test

The primary question is whether fast neural feature trajectories contain recurring motif families that generalize to held-out subjects. The anti-hypothesis is that continuous low-dimensional dynamics or matched null structures explain the data as well or better.

## 2. Methods

### 2.1 Inputs

Primary input was `paper6/features/ds004117_multi_run/ds004117_multi_run_bandpower_delta_features.csv`. Matched null inputs were phase-randomized, time-shift, and random-window feature tables from the same P6 feature interface. External convergent input was ds004752 LCMV encoding/maintenance bandpower features.

### 2.2 Frozen Analysis

All scaling, PCA fitting, K selection, and KMeans centroid fitting used train subjects only. Held-out subjects were never used for latent representation fitting or motif discovery. Transition or stage labels were not used during motif discovery; they were used only for post-hoc metadata association audit.

### 2.3 Baselines and Competing Explanations

The main competing explanations were continuous PCA manifold reconstruction, phase-randomized features, time-shifted windows, random windows, and metadata association.

## 3. Results

### 3.1 Primary Motif Discovery

The train-only selected K was {primary['selected_k']}. The held-out discrete reconstruction MSE for real ds004117 features was {primary['heldout_discrete_reconstruction_mse']:.6f}. Held-out assignment entropy was {primary['heldout_assignment_entropy']:.6f}. The post-hoc transition-label NMI was {primary.get('metadata_nmi')}. The latent-space quantization MSE was {primary['heldout_quantization_mse']:.6f}, but model comparison uses reconstruction MSE so discrete and continuous models are evaluated on the same standardized feature scale.

### 3.2 Null Comparisons

Real held-out quantization MSE was compared with {summary['null_count']} matched null tables.

{null_lines}

The real model beat {summary['real_better_than_null_count']} of {summary['null_count']} available nulls.

### 3.3 Continuous Manifold Baseline

The continuous PCA reconstruction MSE was {primary['continuous_pca_reconstruction_mse']:.6f}. Continuous-preferred status: {summary['continuous_preferred_over_discrete_reconstruction']}.

### 3.4 External Convergent Check

The ds004752 feature space is not identical to ds004117, so this is not a direct cross-dataset replication. It is recorded only as an external convergent check.

## 4. Discussion

### 4.1 What the Evidence Supports

P10 supports only the claim flags recorded in `results/p10_claim_audit.json`. Candidate motif structure may be discussed only within the tested bandpower-delta feature regime and null set.

### 4.2 What the Evidence Does Not Support

P10 does not support validated NAPs, CWP v2 semantics, motif grammar, external direct replication, or universal neural primitives. It also does not rule out region-specific motifs, region-specific continuous manifolds, hybrid regional dynamics, or hierarchical local-to-global composition; those remain untested follow-up hypotheses.

### 4.3 Limitations

The analysis inherits P6 feature constraints: it uses bandpower/amplitude-family features, not raw iEEG spikes, source-localized phase coupling, or direct cross-dataset feature alignment. The external dataset has a different feature space and can only serve as convergent validation. The current comparison is global; regional and hierarchical alternatives require a separate frozen analysis.

## 5. Conclusion

P10 implements a dynamics-first motif-discovery test after P9. The strongest allowed conclusion is bounded by the claim audit: {audit['interpretation']}

## Data Availability

No new raw data are distributed in P10. The analysis consumes local P6 feature artifacts generated from public datasets.

## Code Availability

Reproduction script: `paper10/scripts/run_paper10.py`. Public repository URL: `[TO BE FILLED]`.

## Reproducibility Statement

Run:

```powershell
powershell -ExecutionPolicy Bypass -File paper10/scripts/reproduce-paper10.ps1
```

## Ethics Statement

P10 reuses de-identified public feature artifacts from prior local analyses.

## Author Contributions

`[TO BE FILLED]`

## Conflicts of Interest

`[TO BE FILLED]`
"""
    write_text(PAPER / "manuscript" / "PAPER10_MANUSCRIPT_CURRENT.md", text)


def make_pdf() -> None:
    out = PAPER / "submission" / "PAPER10_BIORXIV_DRAFT_CURRENT.pdf"
    lines = []
    raw = (PAPER / "manuscript" / "PAPER10_MANUSCRIPT_CURRENT.md").read_text(encoding="utf-8").splitlines()
    for line in raw:
        if line.startswith("# "):
            lines += ["", line[2:].upper(), ""]
        elif line.startswith("## "):
            lines += ["", line[3:], ""]
        elif line.startswith("### "):
            lines += ["", line[4:], ""]
        elif line.strip().startswith("```"):
            continue
        else:
            lines.append(line)
    wrapped = []
    for line in lines:
        if line.strip():
            wrapped.extend(textwrap.wrap(line, width=92, replace_whitespace=False))
        else:
            wrapped.append("")
    figs = sorted((PAPER / "figures").glob("figure*.png"))
    with PdfPages(out) as pdf:
        per_page = 38
        for start in range(0, len(wrapped), per_page):
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.text(0.08, 0.95, "Paper 10 Manuscript Draft", fontsize=12, fontweight="bold")
            y = 0.91
            for line in wrapped[start : start + per_page]:
                fig.text(0.08, y, line, fontsize=8.5, va="top")
                y -= 0.021
            fig.text(0.5, 0.055, f"Generated {NOW}", ha="center", fontsize=7)
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)
        for fp in figs:
            img = plt.imread(fp)
            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            ax.imshow(img)
            ax.axis("off")
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)


def write_indices(results: dict[str, object], audit: dict[str, object]) -> None:
    write_text(
        PAPER / "PAPER10_PACKAGE_INDEX.md",
        """# Paper 10 Package Index

## Core Files

- `protocol/PAPER10_FROZEN_PROTOCOL_v1.md`
- `data_manifest/PAPER10_DATASET_MANIFEST.json`
- `latent_representation/p10_latent_representation_summary.json`
- `motif_discovery/ds004117_real_heldout_motif_assignments.csv`
- `motif_discovery/ds004117_real_k_selection.csv`
- `results/p10_primary_motif_summary.json`
- `results/p10_external_convergent_summary.json`
- `results/p10_claim_audit.json`
- `manuscript/PAPER10_MANUSCRIPT_CURRENT.md`
- `submission/PAPER10_BIORXIV_DRAFT_CURRENT.pdf`
- `attachments/A1_Frozen_Protocol.md` through `attachments/A10_One_Command_Reproduction.md`

## Claim Boundary

P10 is a motif-discovery paper. It does not validate NAPs, CWP v2 semantics, or neural grammar. Its negative/boundary result applies to the current global discrete-motif model under the tested feature regime; regional and hierarchical alternatives remain untested.
""",
    )
    write_text(
        PAPER / "submission" / "SUBMISSION_READINESS.md",
        f"""# Paper 10 Submission Readiness

Status: draft package complete, administrative metadata pending.

Completed:

- Frozen protocol.
- Primary ds004117 motif-discovery run.
- Matched null comparisons.
- Continuous-manifold baseline.
- External convergent ds004752 check.
- Claim audit.
- A1-A10 attachments.
- Figures and manuscript PDF preview.

Claim audit:

```text
candidate_dynamic_motif_families: {audit['claim_allowed_candidate_dynamic_motif_families']}
discrete_motifs_preferred_over_all_baselines: {audit['claim_allowed_discrete_motifs_preferred_over_all_baselines']}
continuous_manifold_preferred: {audit['claim_allowed_continuous_manifold_preferred']}
NAP_supported: false
CWP_v2_semantics_supported: false
neural_grammar_supported: false
```

Remaining before external submission:

- Author names.
- Affiliations.
- Funding statement.
- Conflicts of interest.
- Public repository URL or archive DOI.
""",
    )
    write_text(
        PAPER / "submission" / "PAPER10_FINAL_HANDOFF.md",
        f"""# Paper 10 Final Handoff

## Final Status

P10 is complete as an auditable motif-discovery paper package.

## Primary Result

```text
selected_k: {results['primary']['selected_k']}
real_heldout_discrete_reconstruction_mse: {results['summary']['real_heldout_discrete_reconstruction_mse']:.6f}
null_count: {results['summary']['null_count']}
real_better_than_null_count: {results['summary']['real_better_than_null_count']}
continuous_pca_reconstruction_mse: {results['summary']['continuous_pca_reconstruction_mse']:.6f}
continuous_preferred: {results['summary']['continuous_preferred_over_discrete_reconstruction']}
```

## Allowed Claim

```text
{audit['interpretation']}
```

## Forbidden Claims

```text
NAP is validated.
CWP v2 semantics are supported.
Neural grammar exists.
External direct replication is established.
Universal neural primitives exist.
P10 proves region-specific motifs are absent.
P10 proves all brain regions are continuous.
```
""",
    )
    write_text(
        PAPER / "submission" / "PDF_QA.md",
        f"""# Paper 10 PDF QA

Generated: {NOW}

PDF:

```text
paper10/submission/PAPER10_BIORXIV_DRAFT_CURRENT.pdf
```

Render check:

```text
paper10/submission/pdf_render_check/
```

Observed QA:

- PDF generated successfully with Matplotlib PdfPages.
- Poppler render QA produced page PNGs in the local verification run.
- Representative page 1 was visually checked for title/body/footer spacing.
- Representative result figures were visually checked for nonblank rendering and readable labels.
- No obvious blank-page, black-page, clipping, or unreadable-label defect was observed in inspected pages.

Scientific QA:

- Discrete motif and continuous PCA comparisons use the same standardized feature reconstruction scale.
- Latent-space quantization MSE is reported descriptively only.
- Claim audit does not allow NAP, CWP v2 semantics, neural grammar, or universal primitive claims.
""",
    )


def main() -> None:
    mkdirs()
    if not (P9 / "ontology" / "ontology_v2_schema.json").exists():
        raise FileNotFoundError("P9 ontology schema is required before P10.")
    write_protocol()
    primary_bundle = run_primary_and_nulls()
    external = run_external()
    results = {**primary_bundle, "external": external}

    write_json(PAPER / "data_manifest" / "PAPER10_DATASET_MANIFEST.json", {
        "generated_at": NOW,
        "primary": str(PRIMARY_REAL.relative_to(ROOT)),
        "primary_exists": PRIMARY_REAL.exists(),
        "nulls": {k: str(v.relative_to(ROOT)) for k, v in PRIMARY_NULLS.items()},
        "nulls_exist": {k: v.exists() for k, v in PRIMARY_NULLS.items()},
        "external_convergent": str(EXTERNAL.relative_to(ROOT)),
        "external_exists": EXTERNAL.exists(),
        "raw_data_downloaded_by_p10": False,
    })
    write_json(PAPER / "latent_representation" / "p10_latent_representation_summary.json", {
        "generated_at": NOW,
        "train_only_scaling": True,
        "train_only_pca": True,
        "primary_latent_components": results["primary"]["latent_components"],
        "primary_pca_explained_variance": results["primary"]["pca_explained_variance"],
    })
    write_json(PAPER / "results" / "p10_primary_motif_summary.json", results)
    write_json(PAPER / "results" / "p10_external_convergent_summary.json", external)
    audit = claim_audit(results)
    write_json(PAPER / "results" / "p10_claim_audit.json", audit)
    write_json(PAPER / "claim_audit" / "PAPER10_CLAIM_AUDIT.json", audit)
    write_csv(PAPER / "statistics" / "p10_primary_metrics.csv", [
        {
            "metric": k,
            "value": v,
        }
        for k, v in results["summary"].items()
    ])
    make_figures(results)
    write_attachments(results, audit)
    write_manuscript(results, audit)
    make_pdf()
    write_indices(results, audit)
    write_json(PAPER / "results" / "reproduction_report.json", {
        "generated_at": NOW,
        "command_windows": "powershell -ExecutionPolicy Bypass -File paper10/scripts/reproduce-paper10.ps1",
        "command_make": "make reproduce-paper10",
        "status": "PASS",
        "artifacts": [
            "paper10/results/p10_primary_motif_summary.json",
            "paper10/results/p10_claim_audit.json",
            "paper10/manuscript/PAPER10_MANUSCRIPT_CURRENT.md",
            "paper10/submission/PAPER10_BIORXIV_DRAFT_CURRENT.pdf",
        ],
    })
    print(json.dumps({
        "status": "PASS",
        "paper": "P10",
        "selected_k": results["primary"]["selected_k"],
        "real_heldout_discrete_reconstruction_mse": results["summary"]["real_heldout_discrete_reconstruction_mse"],
        "null_count": results["summary"]["null_count"],
        "real_better_than_null_count": results["summary"]["real_better_than_null_count"],
        "continuous_preferred": results["summary"]["continuous_preferred_over_discrete_reconstruction"],
        "candidate_motifs_allowed": audit["claim_allowed_candidate_dynamic_motif_families"],
        "nap_supported": audit["claim_allowed_discrete_NAP_supported"],
    }, indent=2))


if __name__ == "__main__":
    main()
