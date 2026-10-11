from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
STATES = ROOT / "state_extraction" / "hcp_physio_ladder"


def read_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    den = np.linalg.norm(a) * np.linalg.norm(b)
    return float(a @ b / den) if den else float("nan")


def centroid_contrast(x: np.ndarray, y: np.ndarray) -> float:
    labels = sorted(set(y.tolist()))
    if len(labels) != 2:
        return float("nan")
    same = []
    cents = {}
    for label in labels:
        mat = x[y == label]
        odd = mat[::2].mean(axis=0)
        even = mat[1::2].mean(axis=0)
        same.append(cosine(odd, even))
        cents[label] = mat.mean(axis=0)
    return float(np.nanmean(same) - cosine(cents[labels[0]], cents[labels[1]]))


def logo_accuracy(x: np.ndarray, y: np.ndarray, groups: np.ndarray) -> float:
    preds = []
    truth = []
    for train, test in LeaveOneGroupOut().split(x, y, groups):
        model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, solver="liblinear", random_state=8))
        model.fit(x[train], y[train])
        preds.extend(model.predict(x[test]).tolist())
        truth.extend(y[test].tolist())
    return float(accuracy_score(truth, preds))


def metadata_matrix(rows: list[dict]) -> np.ndarray:
    domains = sorted(set(row["domain"] for row in rows))
    runs = sorted(set(row["run"] for row in rows))
    arr = []
    for row in rows:
        vals = [float(row["onset"])]
        vals.extend(1.0 if row["domain"] == d else 0.0 for d in domains)
        vals.extend(1.0 if row["run"] == r else 0.0 for r in runs)
        arr.append(vals)
    return np.asarray(arr, dtype=float)


def permutation_p(observed: float, null: list[float], greater: bool = True) -> float:
    if greater:
        return float((sum(v >= observed for v in null) + 1) / (len(null) + 1))
    return float((sum(v <= observed for v in null) + 1) / (len(null) + 1))


def analyze_rung(name: str, n_perm: int = 100) -> dict:
    rows = read_rows(STATES / f"p8_{name}_transition_features.csv")
    feature_cols = [c for c in rows[0] if c.startswith("roi_")]
    x = np.asarray([[float(row[c]) for c in feature_cols] for row in rows], dtype=float)
    y = np.asarray([row["transition_label"] for row in rows])
    groups = np.asarray([row["group"] for row in rows])
    meta = metadata_matrix(rows)
    rng = np.random.default_rng(88)

    true_contrast = centroid_contrast(x, y)
    true_accuracy = logo_accuracy(x, y, groups)
    metadata_accuracy = logo_accuracy(meta, y, groups)

    label_shuffle_contrasts = []
    pseudo_contrasts = []
    label_shuffle_acc = []
    domain_preserving_acc = []
    for _ in range(n_perm):
        shuffled = y.copy()
        rng.shuffle(shuffled)
        label_shuffle_contrasts.append(centroid_contrast(x, shuffled))
        label_shuffle_acc.append(logo_accuracy(x, shuffled, groups))

        pseudo = y.copy()
        rng.shuffle(pseudo)
        pseudo_contrasts.append(centroid_contrast(x, pseudo))

        dp = y.copy()
        for domain in sorted(set(row["domain"] for row in rows)):
            idx = np.asarray([i for i, row in enumerate(rows) if row["domain"] == domain])
            vals = dp[idx].copy()
            rng.shuffle(vals)
            dp[idx] = vals
        domain_preserving_acc.append(logo_accuracy(x, dp, groups))

    return {
        "rung": name,
        "n_permutations": n_perm,
        "n_rows": len(rows),
        "n_groups": len(set(groups.tolist())),
        "true_same_minus_different_contrast": true_contrast,
        "true_logo_classification_accuracy": true_accuracy,
        "metadata_only_logo_accuracy": metadata_accuracy,
        "label_shuffle_contrast_mean": float(np.mean(label_shuffle_contrasts)),
        "label_shuffle_contrast_ci95": [float(np.percentile(label_shuffle_contrasts, 2.5)), float(np.percentile(label_shuffle_contrasts, 97.5))],
        "true_contrast_vs_label_shuffle_p_greater": permutation_p(true_contrast, label_shuffle_contrasts, greater=True),
        "pseudo_ontology_contrast_mean": float(np.mean(pseudo_contrasts)),
        "pseudo_ontology_contrast_ci95": [float(np.percentile(pseudo_contrasts, 2.5)), float(np.percentile(pseudo_contrasts, 97.5))],
        "classification_label_shuffle_mean": float(np.mean(label_shuffle_acc)),
        "classification_label_shuffle_ci95": [float(np.percentile(label_shuffle_acc, 2.5)), float(np.percentile(label_shuffle_acc, 97.5))],
        "classification_vs_label_shuffle_p_greater": permutation_p(true_accuracy, label_shuffle_acc, greater=True),
        "classification_domain_preserving_shuffle_mean": float(np.mean(domain_preserving_acc)),
        "classification_domain_preserving_shuffle_ci95": [float(np.percentile(domain_preserving_acc, 2.5)), float(np.percentile(domain_preserving_acc, 97.5))],
        "classification_vs_domain_preserving_shuffle_p_greater": permutation_p(true_accuracy, domain_preserving_acc, greater=True),
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    rungs = ["N0_raw_basic", "N4_motion_respiration_cardiac"]
    results = {rung: analyze_rung(rung) for rung in rungs}
    payload = {
        "paper": "Paper 8 v2",
        "experiment": "P8-v2-signal-separation-audit",
        "status": "PASS_SIGNAL_SEPARATION_AUDIT",
        "purpose": "Separate preregistered same-transition reproducibility failure from secondary condition-classification signal.",
        "results": results,
        "allowed_claim": "The primary same-transition reproducibility endpoint remains unsupported, while the secondary 0/2-back condition-classification signal exceeds simple label-shuffle nulls in this HCP smoke set.",
        "forbidden_claims": [
            "physiology eliminated",
            "neural origin proven",
            "transition reproducibility rescued by classification",
            "CWP validated",
            "NAP validated",
        ],
    }
    (RESULTS / "p8_v2_signal_separation_audit.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
