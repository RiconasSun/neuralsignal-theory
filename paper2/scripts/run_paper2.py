from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import CCA
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
PAPER1 = WORKSPACE / "paper1"
sys.path.insert(0, str(PAPER1 / "scripts"))

from common import build_transitions, load_stage_states, model_specs, write_json  # noqa: E402


RESULTS = ROOT / "results"
MANIFEST = ROOT / "data_manifest"


def ensure_dirs() -> None:
    for path in [RESULTS, MANIFEST, ROOT / "external_holdout"]:
        path.mkdir(parents=True, exist_ok=True)


def load_transitions(path: Path) -> Tuple[List[Dict[str, str]], np.ndarray, np.ndarray]:
    rows, roi_cols = load_stage_states(str(path))
    meta, x, y = build_transitions(rows, roi_cols)
    return meta, np.asarray(x, dtype=float), np.asarray(y, dtype=float)


def one_hot(train_meta: Sequence[Dict[str, str]], test_meta: Sequence[Dict[str, str]], fields: Sequence[str]) -> Tuple[np.ndarray, np.ndarray, int]:
    levels: Dict[str, List[str]] = {}
    for field in fields:
        levels[field] = sorted({m.get(field, "NA") or "NA" for m in train_meta})

    def encode(rows: Sequence[Dict[str, str]]) -> np.ndarray:
        if not fields:
            return np.zeros((len(rows), 0))
        out = []
        for row in rows:
            encoded = []
            for field in fields:
                value = row.get(field, "NA") or "NA"
                encoded.extend([1.0 if level == value else 0.0 for level in levels[field]])
            out.append(encoded)
        return np.asarray(out, dtype=float)

    dim = sum(len(v) for v in levels.values())
    return encode(train_meta), encode(test_meta), dim


def fit_predict(
    train_meta: Sequence[Dict[str, str]],
    test_meta: Sequence[Dict[str, str]],
    train_x: np.ndarray,
    test_x: np.ndarray,
    train_y: np.ndarray,
    test_y: np.ndarray,
    fields: Sequence[str],
    ridge: float,
) -> Tuple[np.ndarray, Dict[str, float]]:
    train_cat, test_cat, dim = one_hot(train_meta, test_meta, fields)
    x_train = np.hstack([train_x, train_cat])
    x_test = np.hstack([test_x, test_cat])
    scaler = StandardScaler().fit(x_train)
    x_train_s = scaler.transform(x_train)
    x_test_s = scaler.transform(x_test)
    model = Ridge(alpha=ridge, fit_intercept=True).fit(x_train_s, train_y)
    pred = model.predict(x_test_s)
    return pred, {
        "mse": mse(test_y, pred),
        "r2": r2(test_y, pred),
        "cosine_similarity": cosine(test_y, pred),
        "categorical_dim": dim,
    }


def mse(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean((y - pred) ** 2))


def r2(y: np.ndarray, pred: np.ndarray) -> float:
    denom = float(np.sum((y - np.mean(y)) ** 2))
    if denom == 0:
        return float("nan")
    return float(1.0 - np.sum((y - pred) ** 2) / denom)


def cosine(y: np.ndarray, pred: np.ndarray) -> float:
    num = np.sum(y * pred, axis=1)
    den = np.linalg.norm(y, axis=1) * np.linalg.norm(pred, axis=1)
    valid = den > 0
    return float(np.mean(num[valid] / den[valid])) if np.any(valid) else float("nan")


def subject_mse_rows(
    meta: Sequence[Dict[str, str]],
    y: np.ndarray,
    predictions: Dict[str, np.ndarray],
) -> list[dict[str, object]]:
    by_subject: Dict[str, list[int]] = defaultdict(list)
    for idx, row in enumerate(meta):
        by_subject[row.get("subject", "NA")].append(idx)

    rows: list[dict[str, object]] = []
    for subject, indices in sorted(by_subject.items()):
        subject_row: dict[str, object] = {"subject": subject, "n_transitions": len(indices)}
        for model_name, pred in predictions.items():
            subject_row[f"{model_name}_mse"] = float(np.mean((y[indices] - pred[indices]) ** 2))
        if "M2_strong_task" in predictions and "CWP_v2_medium" in predictions:
            subject_row["cwp_v2_minus_strong_task_mse"] = (
                float(subject_row["CWP_v2_medium_mse"]) - float(subject_row["M2_strong_task_mse"])
            )
        if "RandomOntology" in predictions and "CWP_v2_medium" in predictions:
            subject_row["cwp_v2_minus_random_ontology_mse"] = (
                float(subject_row["CWP_v2_medium_mse"]) - float(subject_row["RandomOntology_mse"])
            )
        rows.append(subject_row)
    return rows


def write_csv(path: Path, rows: Sequence[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(list(rows)).to_csv(path, index=False)


def evaluate_models(
    experiment: str,
    variant: str,
    train_meta: Sequence[Dict[str, str]],
    test_meta: Sequence[Dict[str, str]],
    train_x: np.ndarray,
    test_x: np.ndarray,
    train_y: np.ndarray,
    test_y: np.ndarray,
    ridge: float,
    model_names: Iterable[str] | None = None,
) -> List[Dict[str, object]]:
    specs = model_specs()
    names = list(model_names or specs.keys())
    rows: List[Dict[str, object]] = []
    for name in names:
        pred, metrics = fit_predict(train_meta, test_meta, train_x, test_x, train_y, test_y, specs[name], ridge)
        row = {
            "experiment": experiment,
            "variant": variant,
            "model": name,
            "n_train": len(train_meta),
            "n_test": len(test_meta),
            "mse": metrics["mse"],
            "r2": metrics["r2"],
            "cosine_similarity": metrics["cosine_similarity"],
            "categorical_fields": "+".join(specs[name]) or "none",
            "categorical_dim": metrics["categorical_dim"],
        }
        rows.append(row)
    return rows


def source_standardized(train_x: np.ndarray, test_x: np.ndarray, train_y: np.ndarray, test_y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    sx = StandardScaler().fit(train_x)
    sy = StandardScaler().fit(train_y)
    return sx.transform(train_x), sx.transform(test_x), sy.transform(train_y), sy.transform(test_y)


def target_to_source_moment_aligned(train_x: np.ndarray, test_x: np.ndarray, train_y: np.ndarray, test_y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    sx_src = StandardScaler().fit(train_x)
    sx_tgt = StandardScaler().fit(test_x)
    sy_src = StandardScaler().fit(train_y)
    sy_tgt = StandardScaler().fit(test_y)
    return sx_src.transform(train_x), sx_tgt.transform(test_x), sy_src.transform(train_y), sy_tgt.transform(test_y)


def network_reduce(x: np.ndarray, groups: int = 12) -> np.ndarray:
    chunks = np.array_split(np.arange(x.shape[1]), groups)
    return np.column_stack([x[:, idx].mean(axis=1) for idx in chunks])


def subject_normalize(meta: Sequence[Dict[str, str]], x: np.ndarray) -> np.ndarray:
    out = np.zeros_like(x)
    by_subject: Dict[str, List[int]] = defaultdict(list)
    for i, m in enumerate(meta):
        by_subject[m.get("subject", "NA")].append(i)
    for indices in by_subject.values():
        block = x[indices]
        scaler = StandardScaler().fit(block)
        out[indices] = scaler.transform(block)
    return out


def pca_reduce(train_x: np.ndarray, test_x: np.ndarray, train_y: np.ndarray, test_y: np.ndarray, n_components: int = 32) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n = min(n_components, train_x.shape[0] - 1, train_x.shape[1])
    if n < 2:
        return train_x, test_x, train_y, test_y
    px = PCA(n_components=n, random_state=13).fit(train_x)
    py = PCA(n_components=n, random_state=13).fit(train_y)
    return px.transform(train_x), px.transform(test_x), py.transform(train_y), py.transform(test_y)


def cca_reduce(train_x: np.ndarray, test_x: np.ndarray, train_y: np.ndarray, test_y: np.ndarray, n_components: int = 16) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n = min(n_components, train_x.shape[0] - 1, test_x.shape[0] - 1, train_x.shape[1], test_x.shape[1])
    if n < 2:
        return train_x, test_x, train_y, test_y
    train_scaled, test_scaled, train_y_scaled, test_y_scaled = source_standardized(train_x, test_x, train_y, test_y)
    pair_n = min(len(train_scaled), len(test_scaled))
    cca = CCA(n_components=n, max_iter=500)
    cca.fit(train_scaled[:pair_n], test_scaled[:pair_n])
    return cca.transform(train_scaled), cca.transform(test_scaled), train_y_scaled, test_y_scaled


def with_ontology(meta: Sequence[Dict[str, str]], mode: str) -> List[Dict[str, str]]:
    rows = [dict(m) for m in meta]
    for row in rows:
        cwp = row.get("source_cwp", "NA")
        domain = row.get("domain", "NA")
        context = row.get("context", "NA")
        if mode == "coarse":
            row["source_cwp"] = cwp
        elif mode == "medium":
            row["source_cwp"] = f"{domain}_{cwp}"
        elif mode == "fine":
            row["source_cwp"] = f"{domain}_{row.get('load', 'NA')}_{context}_{cwp}"
        elif mode == "random":
            key = f"{row.get('subject', '')}|{row.get('run', '')}|{row.get('trial_id', '')}|{row.get('source_cwp', '')}"
            bucket = int(hashlib.sha1(key.encode("utf-8")).hexdigest(), 16) % 3
            row["source_cwp"] = f"PSEUDO_{bucket}"
    return rows


def descriptor(meta: Dict[str, str]) -> set[str]:
    keys = ["source_cwp", "target_cwp", "domain", "load", "context", "time_bin"]
    return {f"{k}:{meta.get(k, 'NA')}" for k in keys if meta.get(k, "NA")}


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a or b else 0.0


def task_context_shift(train_meta, test_meta, train_x, test_x, train_y, test_y, ridge) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    pred, _ = fit_predict(train_meta, test_meta, train_x, test_x, train_y, test_y, model_specs()["M3_cwp"], ridge)
    train_desc = [descriptor(m) for m in train_meta]
    rows = []
    for i, m in enumerate(test_meta):
        desc = descriptor(m)
        nearest = max(jaccard(desc, td) for td in train_desc)
        err = float(np.mean((test_y[i] - pred[i]) ** 2))
        rows.append(
            {
                "experiment": "E9.3",
                "external_subject": m.get("subject", "NA"),
                "source_cwp": m.get("source_cwp", "NA"),
                "domain": m.get("domain", "NA"),
                "load": m.get("load", "NA"),
                "context": m.get("context", "NA"),
                "nearest_train_context_similarity": nearest,
                "m3_cwp_row_mse": err,
            }
        )
    corr = float(pd.DataFrame(rows)[["nearest_train_context_similarity", "m3_cwp_row_mse"]].corr().iloc[0, 1])
    summary = [{"experiment": "E9.3", "variant": "task_context_similarity", "correlation_similarity_vs_error": corr, "n_test": len(rows)}]
    return rows, summary


def e9_0(train_meta, test_meta, train_x, test_x, train_y, test_y, ridge) -> List[Dict[str, object]]:
    rows = evaluate_models("E9.0", "raw_failure_reproduction", train_meta, test_meta, train_x, test_x, train_y, test_y, ridge)
    m2 = next(r for r in rows if r["model"] == "M2_strong_task")
    m3 = next(r for r in rows if r["model"] == "M3_cwp")
    status = "REPRODUCED_FAILURE" if float(m3["mse"]) > float(m2["mse"]) else "FAILURE_NOT_REPRODUCED"
    write_json(
        str(RESULTS / "e9_0_failure_reproduction_summary.json"),
        {"experiment": "E9.0", "status": status, "m2_mse": m2["mse"], "m3_mse": m3["mse"], "n_train": len(train_meta), "n_test": len(test_meta)},
    )
    return rows


def e9_1(train_meta, test_meta, train_x, test_x, train_y, test_y, ridge) -> List[Dict[str, object]]:
    variants = {
        "raw": (train_x, test_x, train_y, test_y),
        "source_standardized": source_standardized(train_x, test_x, train_y, test_y),
        "target_to_source_moment_aligned": target_to_source_moment_aligned(train_x, test_x, train_y, test_y),
    }
    rows: List[Dict[str, object]] = []
    for variant, mats in variants.items():
        rows.extend(evaluate_models("E9.1", variant, train_meta, test_meta, *mats, ridge, model_names=["M2_strong_task", "M3_cwp", "M4_task_plus_cwp"]))
    return rows


def e9_2(train_meta, test_meta, train_x, test_x, train_y, test_y, ridge) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    variants = {
        "R0_native_grid_216": (train_x, test_x, train_y, test_y),
        "R2_network_12_mean": (network_reduce(train_x), network_reduce(test_x), network_reduce(train_y), network_reduce(test_y)),
        "R3_subject_normalized": (subject_normalize(train_meta, train_x), subject_normalize(test_meta, test_x), subject_normalize(train_meta, train_y), subject_normalize(test_meta, test_y)),
        "R_shared_pca_32": pca_reduce(train_x, test_x, train_y, test_y),
        "R_shared_cca_16": cca_reduce(train_x, test_x, train_y, test_y),
    }
    for variant, mats in variants.items():
        rows.extend(evaluate_models("E9.2", variant, train_meta, test_meta, *mats, ridge, model_names=["M2_strong_task", "M3_cwp", "M4_task_plus_cwp"]))
    return rows


def e9_4(train_meta, test_meta, train_x, test_x, train_y, test_y, ridge) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    complexities = {"coarse": 3, "medium": None, "fine": None, "random": 3}
    for ontology in ["coarse", "medium", "fine", "random"]:
        tr = with_ontology(train_meta, ontology)
        te = with_ontology(test_meta, ontology)
        eval_rows = evaluate_models("E9.4", f"ontology_{ontology}", tr, te, train_x, test_x, train_y, test_y, ridge, model_names=["M2_strong_task", "M3_cwp"])
        levels = len({m["source_cwp"] for m in tr})
        for row in eval_rows:
            row["ontology_levels"] = complexities[ontology] or levels
        rows.extend(eval_rows)
    return rows


def summarize_attribution(all_rows: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    raw_m2 = [
        r for r in all_rows if r.get("experiment") == "E9.0" and r.get("variant") == "raw_failure_reproduction" and r.get("model") == "M2_strong_task"
    ][0]
    raw_m3 = [
        r for r in all_rows if r.get("experiment") == "E9.0" and r.get("variant") == "raw_failure_reproduction" and r.get("model") == "M3_cwp"
    ][0]
    raw_gap = float(raw_m3["mse"]) - float(raw_m2["mse"])
    out = []
    variants = sorted(
        {
            (str(r.get("experiment")), str(r.get("variant")))
            for r in all_rows
            if r.get("experiment") in {"E9.1", "E9.2", "E9.4"}
        }
    )
    for experiment, variant in variants:
        m2 = next((r for r in all_rows if r.get("experiment") == experiment and r.get("variant") == variant and r.get("model") == "M2_strong_task"), None)
        m3 = next((r for r in all_rows if r.get("experiment") == experiment and r.get("variant") == variant and r.get("model") == "M3_cwp"), None)
        if not m2 or not m3:
            continue
        cwp_minus_task_gap = float(m3["mse"]) - float(m2["mse"])
        gap_reduction = raw_gap - cwp_minus_task_gap
        factor = {"E9.1": "measurement", "E9.2": "state_representation", "E9.4": "ontology"}[experiment]
        out.append(
            {
                "experiment": "E9.5",
                "factor_family": factor,
                "variant": variant,
                "raw_cwp_minus_task_mse_gap": raw_gap,
                "variant_cwp_minus_task_mse_gap": cwp_minus_task_gap,
                "gap_reduction_vs_raw": gap_reduction,
                "interpretation": "positive means the intervention reduced the CWP disadvantage relative to the strong task baseline within the same metric space",
            }
        )
    return sorted(out, key=lambda r: float(r["gap_reduction_vs_raw"]), reverse=True)


def freeze_v2(attribution_rows: Sequence[Dict[str, object]]) -> Dict[str, object]:
    positive = [
        r
        for r in attribution_rows
        if float(r["gap_reduction_vs_raw"]) > 0 and "random" not in str(r.get("variant", "")).lower()
    ]
    random_best = bool(attribution_rows) and "random" in str(attribution_rows[0].get("variant", "")).lower()
    selected = positive[0] if positive else None
    payload = {
        "experiment": "E9.6",
        "status": "FROZEN_V2_CANDIDATE_WITH_NULL_RISK" if selected and random_best else "FROZEN_V2_CANDIDATE_FROM_A_B_DIAGNOSTICS" if selected else "NO_IMPROVING_V2_CANDIDATE_FOUND",
        "selected_variant": selected["variant"] if selected else None,
        "selected_factor_family": selected["factor_family"] if selected else None,
        "null_risk": "random ontology produced the largest apparent gap reduction" if random_best else "",
        "rule": "This is a Dataset A/B diagnostic v2 candidate only. It is not an independent replication result.",
    }
    write_json(str(RESULTS / "e9_6_frozen_v2_candidate.json"), payload)
    return payload


def dataset_c_holdout(dataset_c_states: str | None, ridge: float) -> Dict[str, object]:
    if not dataset_c_states:
        metadata_audit = ROOT / "external_holdout" / "dataset_c_metadata_audit.json"
        if metadata_audit.exists():
            audit = json.loads(metadata_audit.read_text(encoding="utf-8"))
            payload = {
                "experiment": "E9.7",
                "status": "DATASET_C_LOCKED_NOT_EVALUATED",
                "dataset_id": audit.get("dataset_id"),
                "version": audit.get("version"),
                "dataset_doi": audit.get("dataset_doi"),
                "metadata_audit": str(metadata_audit.relative_to(WORKSPACE)),
                "final_performance_inspected": False,
                "bold_nii_downloaded_for_final_evaluation": False,
                "reason": "Dataset C has been selected and metadata-audited, but final BOLD/state extraction and performance evaluation have not been run.",
            }
            write_json(str(RESULTS / "e9_7_dataset_c_holdout_summary.json"), payload)
            return payload
        payload = {
            "experiment": "E9.7",
            "status": "BLOCKED_DATASET_C_NOT_SPECIFIED",
            "reason": "Dataset C must be a never-seen final external holdout selected and frozen before final performance is inspected.",
        }
        write_json(str(RESULTS / "e9_7_dataset_c_holdout_summary.json"), payload)
        return payload

    c_meta, c_x, c_y = load_transitions(Path(dataset_c_states))
    a_meta, a_x, a_y = load_transitions(PAPER1 / "state_extraction" / "stage_states.csv")
    b_meta, b_x, b_y = load_transitions(PAPER1 / "external_validation" / "stage_states_external.csv")
    train_meta = a_meta + b_meta
    train_x = np.vstack([a_x, b_x])
    train_y = np.vstack([a_y, b_y])

    rows: list[dict[str, object]] = []
    rows.extend(
        evaluate_models(
            "E9.7",
            "dataset_c_cwp_v1",
            train_meta,
            c_meta,
            train_x,
            c_x,
            train_y,
            c_y,
            ridge=ridge,
            model_names=["M2_strong_task", "M3_cwp", "M4_task_plus_cwp"],
        )
    )
    rows.extend(
        evaluate_models(
            "E9.7",
            "dataset_c_cwp_v2_medium",
            with_ontology(train_meta, "medium"),
            with_ontology(c_meta, "medium"),
            train_x,
            c_x,
            train_y,
            c_y,
            ridge=ridge,
            model_names=["M3_cwp"],
        )
    )
    rows[-1]["model"] = "CWP_v2_medium"
    rows.extend(
        evaluate_models(
            "E9.7",
            "dataset_c_random_ontology",
            with_ontology(train_meta, "random"),
            with_ontology(c_meta, "random"),
            train_x,
            c_x,
            train_y,
            c_y,
            ridge=ridge,
            model_names=["M3_cwp"],
        )
    )
    rows[-1]["model"] = "RandomOntology"
    write_csv(RESULTS / "e9_7_dataset_c_model_comparison.csv", rows)

    specs = model_specs()
    m2_pred, _ = fit_predict(train_meta, c_meta, train_x, c_x, train_y, c_y, specs["M2_strong_task"], ridge)
    v1_pred, _ = fit_predict(train_meta, c_meta, train_x, c_x, train_y, c_y, specs["M3_cwp"], ridge)
    v2_pred, _ = fit_predict(
        with_ontology(train_meta, "medium"),
        with_ontology(c_meta, "medium"),
        train_x,
        c_x,
        train_y,
        c_y,
        specs["M3_cwp"],
        ridge,
    )
    random_pred, _ = fit_predict(
        with_ontology(train_meta, "random"),
        with_ontology(c_meta, "random"),
        train_x,
        c_x,
        train_y,
        c_y,
        specs["M3_cwp"],
        ridge,
    )
    subject_rows = subject_mse_rows(
        c_meta,
        c_y,
        {
            "M2_strong_task": m2_pred,
            "M3_cwp": v1_pred,
            "CWP_v2_medium": v2_pred,
            "RandomOntology": random_pred,
        },
    )
    write_csv(RESULTS / "e9_7_dataset_c_subject_effects.csv", subject_rows)

    by_model = {str(row["model"]): row for row in rows}
    m2 = by_model["M2_strong_task"]
    v2 = by_model["CWP_v2_medium"]
    random_ontology = by_model["RandomOntology"]
    cwp_v1 = by_model["M3_cwp"]
    v2_beats_strong = float(v2["mse"]) < float(m2["mse"])
    v2_beats_random = float(v2["mse"]) < float(random_ontology["mse"])
    status = "DATASET_C_CWP_SPECIFIC_SUCCESS" if v2_beats_strong and v2_beats_random else "DATASET_C_CWP_SPECIFIC_NOT_SUPPORTED"

    payload = {
        "experiment": "E9.7",
        "status": status,
        "dataset_c_states": dataset_c_states,
        "n_train_ab_transitions": len(train_meta),
        "n_dataset_c_transitions": len(c_meta),
        "models_csv": str((RESULTS / "e9_7_dataset_c_model_comparison.csv").relative_to(WORKSPACE)),
        "subject_effects_csv": str((RESULTS / "e9_7_dataset_c_subject_effects.csv").relative_to(WORKSPACE)),
        "strong_task_mse": m2["mse"],
        "cwp_v1_mse": cwp_v1["mse"],
        "cwp_v2_medium_mse": v2["mse"],
        "random_ontology_mse": random_ontology["mse"],
        "subject_mean_cwp_v2_minus_strong_task_mse": float(
            np.mean([float(row["cwp_v2_minus_strong_task_mse"]) for row in subject_rows])
        ),
        "subject_mean_cwp_v2_minus_random_ontology_mse": float(
            np.mean([float(row["cwp_v2_minus_random_ontology_mse"]) for row in subject_rows])
        ),
        "subject_median_cwp_v2_minus_strong_task_mse": float(
            np.median([float(row["cwp_v2_minus_strong_task_mse"]) for row in subject_rows])
        ),
        "subject_median_cwp_v2_minus_random_ontology_mse": float(
            np.median([float(row["cwp_v2_minus_random_ontology_mse"]) for row in subject_rows])
        ),
        "subjects_cwp_v2_better_than_strong_task": int(
            sum(float(row["cwp_v2_minus_strong_task_mse"]) < 0 for row in subject_rows)
        ),
        "subjects_cwp_v2_better_than_random_ontology": int(
            sum(float(row["cwp_v2_minus_random_ontology_mse"]) < 0 for row in subject_rows)
        ),
        "n_dataset_c_subjects_with_transitions": len(subject_rows),
        "cwp_v2_beats_strong_task": v2_beats_strong,
        "cwp_v2_beats_random_ontology": v2_beats_random,
        "claim_boundary": "CWP-specific generalization requires CWP_v2_medium to beat both M2_strong_task and RandomOntology.",
        "scope_boundary": "Dataset C tests ENCODE/MAINTAIN/PROBE stage transfer only, not TRANSFORM.",
    }
    write_json(str(RESULTS / "e9_7_dataset_c_holdout_summary.json"), payload)
    return payload


def claim_audit(e90_status: str, v2: Dict[str, object], dataset_c: Dict[str, object]) -> Dict[str, object]:
    remaining_blockers: list[str] = []
    if dataset_c["status"] == "BLOCKED_DATASET_C_NOT_SPECIFIED":
        remaining_blockers.append("Dataset C not specified")
    elif dataset_c["status"] == "DATASET_C_LOCKED_NOT_EVALUATED":
        remaining_blockers.append("Dataset C BOLD/state extraction and final holdout evaluation not run")

    dataset_c_success = dataset_c["status"] == "DATASET_C_CWP_SPECIFIC_SUCCESS"
    payload = {
        "experiment": "E9.8",
        "status": "completed_with_dataset_c" if dataset_c["status"].startswith("DATASET_C_CWP_SPECIFIC") else "completed_partial_without_dataset_c",
        "e9_0_failure_reproduction": e90_status,
        "dataset_b_role": "failure-analysis dataset, not final holdout",
        "dataset_c_status": dataset_c["status"],
        "v2_candidate_status": v2["status"],
        "claim_allowed_failure_explained": False,
        "claim_allowed_failure_diagnostic_candidate_identified": e90_status == "REPRODUCED_FAILURE" and v2["status"] in {"FROZEN_V2_CANDIDATE_FROM_A_B_DIAGNOSTICS", "FROZEN_V2_CANDIDATE_WITH_NULL_RISK"},
        "claim_allowed_cwp_specific_fix": False,
        "claim_allowed_generic_composition_possible": v2["status"] == "FROZEN_V2_CANDIDATE_WITH_NULL_RISK",
        "semantic_specificity_rule": "CWP-specific generalization requires CWP_v2 to beat both StrongTask and Random/PseudoOntology on Dataset C.",
        "claim_allowed_cross_dataset_generalization": dataset_c_success,
        "claim_allowed_cwp_rescued": dataset_c_success,
        "remaining_blockers": remaining_blockers,
        "no_invented_results": True,
    }
    write_json(str(RESULTS / "e9_8_claim_audit.json"), payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Paper 2 E9.0-E9.8 failure-decomposition pipeline.")
    parser.add_argument("--dataset-a-states", default=str(PAPER1 / "state_extraction" / "stage_states.csv"))
    parser.add_argument("--dataset-b-states", default=str(PAPER1 / "external_validation" / "stage_states_external.csv"))
    parser.add_argument("--dataset-c-states", default="")
    parser.add_argument("--ridge", type=float, default=1e-3)
    args = parser.parse_args()

    ensure_dirs()
    train_meta, train_x, train_y = load_transitions(Path(args.dataset_a_states))
    test_meta, test_x, test_y = load_transitions(Path(args.dataset_b_states))

    manifest = {
        "dataset_a_states": os.path.abspath(args.dataset_a_states),
        "dataset_b_states": os.path.abspath(args.dataset_b_states),
        "dataset_c_states": os.path.abspath(args.dataset_c_states) if args.dataset_c_states else "",
        "n_dataset_a_transitions": len(train_meta),
        "n_dataset_b_transitions": len(test_meta),
        "n_roi_features_dataset_a": int(train_x.shape[1]),
        "n_roi_features_dataset_b": int(test_x.shape[1]),
    }
    write_json(str(MANIFEST / "paper2_input_manifest.json"), manifest)

    e90 = e9_0(train_meta, test_meta, train_x, test_x, train_y, test_y, args.ridge)
    e91 = e9_1(train_meta, test_meta, train_x, test_x, train_y, test_y, args.ridge)
    e92 = e9_2(train_meta, test_meta, train_x, test_x, train_y, test_y, args.ridge)
    context_rows, context_summary = task_context_shift(train_meta, test_meta, train_x, test_x, train_y, test_y, args.ridge)
    e94 = e9_4(train_meta, test_meta, train_x, test_x, train_y, test_y, args.ridge)

    all_metrics = e90 + e91 + e92 + context_summary + e94
    write_csv(RESULTS / "paper2_primary_metrics.csv", all_metrics)
    write_csv(RESULTS / "e9_3_task_context_shift_rows.csv", context_rows)

    attribution = summarize_attribution(all_metrics)
    write_csv(RESULTS / "e9_5_failure_attribution.csv", attribution)
    v2 = freeze_v2(attribution)
    dataset_c = dataset_c_holdout(args.dataset_c_states or None, args.ridge)
    e90_status = json.loads((RESULTS / "e9_0_failure_reproduction_summary.json").read_text(encoding="utf-8"))["status"]
    audit = claim_audit(e90_status, v2, dataset_c)
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
