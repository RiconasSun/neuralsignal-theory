from __future__ import annotations

import argparse
import csv
import glob
import json
import math
import os
import random
import re
from collections import Counter, defaultdict
from typing import Dict, List, Sequence, Tuple


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def root_path(*parts: str) -> str:
    return os.path.join(ROOT, *parts)


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def read_table(path: str) -> List[Dict[str, str]]:
    delimiter = "\t" if path.lower().endswith(".tsv") else ","
    with open(path, "r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=delimiter))


def write_table(path: str, rows: Sequence[Dict[str, object]], fieldnames: Sequence[str] | None = None) -> None:
    ensure_dir(os.path.dirname(path))
    if fieldnames is None:
        fields: List[str] = []
        seen = set()
        for row in rows:
            for key in row.keys():
                if key not in seen:
                    seen.add(key)
                    fields.append(key)
        fieldnames = fields
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: str, payload: object) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def expand_glob(pattern: str) -> List[str]:
    matches = sorted(glob.glob(pattern, recursive=True))
    return [m for m in matches if os.path.isfile(m)]


def as_float(value: str | None, default: float | None = None) -> float:
    if value is None or value == "":
        if default is None:
            raise ValueError("missing float")
        return default
    if value.lower() in {"n/a", "na", "nan"}:
        if default is None:
            raise ValueError("missing float")
        return default
    return float(value)


def safe_time_bin(value: str | None, width: float = 5.0) -> str:
    try:
        return str(int(as_float(value, default=0.0) // width))
    except Exception:
        return "NA"


def parse_subject_run(path: str, row: Dict[str, str] | None = None) -> Tuple[str, str]:
    row = row or {}
    subject = row.get("subject") or row.get("participant_id") or row.get("sub")
    run = row.get("run")
    if not subject:
        m = re.search(r"sub-([A-Za-z0-9]+)", path)
        subject = f"sub-{m.group(1)}" if m else "unknown_subject"
    if not run:
        m = re.search(r"run-([A-Za-z0-9]+)", path)
        run = f"run-{m.group(1)}" if m else "run-unknown"
    return subject, run


def normalize_label(value: str | None) -> str:
    if not value:
        return "NA"
    return re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_").upper() or "NA"


def infer_cwp(row: Dict[str, str]) -> str:
    raw = (
        row.get("cwp")
        or row.get("processing_stage")
        or row.get("stage")
        or row.get("trial_phase")
        or row.get("condition")
        or ""
    ).lower()
    if "enc" in raw:
        return "ENCODE"
    if "maint" in raw or "delay" in raw:
        return "MAINTAIN"
    if "probe" in raw or "retriev" in raw:
        return "PROBE"
    if "cue" in raw:
        return "CUE"
    if "rest" in raw or "baseline" in raw:
        return "REST"
    return normalize_label(raw)


def infer_domain(row: Dict[str, str]) -> str:
    raw = " ".join(
        [
            row.get("domain", ""),
            row.get("trial_type", ""),
            row.get("stimulus_type", ""),
            row.get("condition", ""),
        ]
    ).lower()
    if any(x in raw for x in ["num", "number", "digit", "add"]):
        return "NUMBER"
    if any(x in raw for x in ["pos", "spatial", "rot", "location"]):
        return "SPATIAL"
    if "fractal" in raw:
        return "FRACTAL"
    return normalize_label(row.get("domain") or row.get("trial_type") or "NA")


def infer_load(row: Dict[str, str]) -> str:
    raw = (row.get("load") or row.get("load_type") or row.get("memory_load") or "").lower()
    if "low" in raw or raw in {"1", "one"}:
        return "LOW"
    if "high" in raw or raw in {"2", "3", "four", "4"}:
        return "HIGH"
    return normalize_label(raw)


def infer_context(row: Dict[str, str]) -> str:
    raw = row.get("context") or row.get("trial_type") or row.get("operation") or row.get("condition") or "NA"
    return normalize_label(raw)


def task_id(domain: str, load: str, cwp: str, context: str = "NA") -> str:
    return "__".join([domain, load, cwp, context])


def roi_columns(rows: Sequence[Dict[str, str]]) -> List[str]:
    if not rows:
        return []
    cols = list(rows[0].keys())
    preferred = [c for c in cols if c.lower().startswith(("roi_", "parcel_", "region_"))]
    if preferred:
        return preferred
    excluded = {
        "subject",
        "participant_id",
        "sub",
        "run",
        "time",
        "tr",
        "frame",
        "onset",
        "duration",
        "trial_id",
        "stage",
        "cwp",
        "domain",
        "load",
        "context",
        "task_id",
    }
    numeric: List[str] = []
    for col in cols:
        if col.lower() in excluded:
            continue
        try:
            as_float(rows[0].get(col), default=None)
            numeric.append(col)
        except Exception:
            pass
    return numeric


def vector_from_row(row: Dict[str, str], cols: Sequence[str]) -> List[float]:
    return [as_float(row.get(c), default=0.0) for c in cols]


def mean_vector(vectors: Sequence[Sequence[float]]) -> List[float]:
    if not vectors:
        return []
    n = len(vectors)
    d = len(vectors[0])
    out = [0.0] * d
    for vec in vectors:
        for i, value in enumerate(vec):
            out[i] += value
    return [x / n for x in out]


def sub_vec(a: Sequence[float], b: Sequence[float]) -> List[float]:
    return [x - y for x, y in zip(a, b)]


def mse(y_true: Sequence[Sequence[float]], y_pred: Sequence[Sequence[float]]) -> float:
    total = 0.0
    count = 0
    for yt, yp in zip(y_true, y_pred):
        for a, b in zip(yt, yp):
            total += (a - b) ** 2
            count += 1
    return total / max(count, 1)


def r2_score(y_true: Sequence[Sequence[float]], y_pred: Sequence[Sequence[float]]) -> float:
    flat = [v for row in y_true for v in row]
    if not flat:
        return float("nan")
    mean_y = sum(flat) / len(flat)
    ss_res = sum((a - b) ** 2 for yt, yp in zip(y_true, y_pred) for a, b in zip(yt, yp))
    ss_tot = sum((a - mean_y) ** 2 for yt in y_true for a in yt)
    return 1.0 - ss_res / ss_tot if ss_tot else float("nan")


def cosine_similarity(y_true: Sequence[Sequence[float]], y_pred: Sequence[Sequence[float]]) -> float:
    vals = []
    for yt, yp in zip(y_true, y_pred):
        dot = sum(a * b for a, b in zip(yt, yp))
        na = math.sqrt(sum(a * a for a in yt))
        nb = math.sqrt(sum(b * b for b in yp))
        if na and nb:
            vals.append(dot / (na * nb))
    return sum(vals) / len(vals) if vals else float("nan")


def macro_f1(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    labels = sorted(set(y_true) | set(y_pred))
    scores = []
    for label in labels:
        tp = sum(1 for a, b in zip(y_true, y_pred) if a == label and b == label)
        fp = sum(1 for a, b in zip(y_true, y_pred) if a != label and b == label)
        fn = sum(1 for a, b in zip(y_true, y_pred) if a == label and b != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        scores.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return sum(scores) / len(scores) if scores else float("nan")


def accuracy(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    return sum(1 for a, b in zip(y_true, y_pred) if a == b) / max(len(y_true), 1)


def load_stage_states(path: str) -> Tuple[List[Dict[str, str]], List[str]]:
    rows = read_table(path)
    cols = [c for c in rows[0].keys() if c.startswith("roi_")] if rows else []
    if not rows:
        fail(f"no rows found in {path}")
    if not cols:
        fail(f"no roi_* columns found in {path}; run E1 or provide compatible state CSV")
    return rows, cols


def build_transitions(rows: Sequence[Dict[str, str]], roi_cols: Sequence[str]) -> Tuple[List[Dict[str, str]], List[List[float]], List[List[float]]]:
    by_trial: Dict[Tuple[str, str, str], List[Dict[str, str]]] = defaultdict(list)
    for row in rows:
        trial = row.get("trial_id") or row.get("trial")
        if not trial:
            continue
        by_trial[(row.get("subject", ""), row.get("run", ""), trial)].append(row)
    stage_order = {"ENCODE": 0, "MAINTAIN": 1, "PROBE": 2}
    meta: List[Dict[str, str]] = []
    x_state: List[List[float]] = []
    y_state: List[List[float]] = []
    for key, trial_rows in by_trial.items():
        valid = [r for r in trial_rows if r.get("cwp") in stage_order]
        valid.sort(key=lambda r: stage_order[r.get("cwp", "")])
        for cur, nxt in zip(valid, valid[1:]):
            m = {
                "subject": cur.get("subject", ""),
                "run": cur.get("run", ""),
                "trial_id": cur.get("trial_id", ""),
                "source_cwp": cur.get("cwp", ""),
                "target_cwp": nxt.get("cwp", ""),
                "domain": cur.get("domain", ""),
                "load": cur.get("load", ""),
                "context": cur.get("context", ""),
                "task_id": cur.get("task_id", ""),
                "cell_id": "__".join([cur.get("domain", ""), cur.get("load", ""), cur.get("cwp", "")]),
                "source_onset": cur.get("onset", ""),
                "target_onset": nxt.get("onset", ""),
                "time_bin": safe_time_bin(cur.get("onset")),
            }
            meta.append(m)
            x_state.append(vector_from_row(cur, roi_cols))
            y_state.append(vector_from_row(nxt, roi_cols))
    if not meta:
        fail("could not build transitions; stage_states.csv needs subject/run/trial_id/cwp rows for ENCODE/MAINTAIN/PROBE")
    return meta, x_state, y_state


class FeatureEncoder:
    def __init__(self, fields: Sequence[str]):
        self.fields = list(fields)
        self.levels: Dict[str, List[str]] = {}
        self.dim = 0

    def fit(self, rows: Sequence[Dict[str, str]]) -> "FeatureEncoder":
        self.levels = {}
        for field in self.fields:
            self.levels[field] = sorted({r.get(field, "NA") or "NA" for r in rows})
        self.dim = sum(len(v) for v in self.levels.values())
        return self

    def transform_row(self, row: Dict[str, str]) -> List[float]:
        out: List[float] = []
        for field in self.fields:
            value = row.get(field, "NA") or "NA"
            out.extend([1.0 if level == value else 0.0 for level in self.levels[field]])
        return out

    def transform(self, rows: Sequence[Dict[str, str]]) -> List[List[float]]:
        return [self.transform_row(r) for r in rows]


def standardize_train_test(train: List[List[float]], test: List[List[float]]) -> Tuple[List[List[float]], List[List[float]]]:
    if not train:
        return train, test
    d = len(train[0])
    means = [sum(row[j] for row in train) / len(train) for j in range(d)]
    stds = []
    for j in range(d):
        var = sum((row[j] - means[j]) ** 2 for row in train) / max(len(train) - 1, 1)
        stds.append(math.sqrt(var) or 1.0)

    def scale(mat: List[List[float]]) -> List[List[float]]:
        return [[(row[j] - means[j]) / stds[j] for j in range(d)] for row in mat]

    return scale(train), scale(test)


class LinearMultiOutputGD:
    def __init__(self, ridge: float = 1e-3, epochs: int = 600, lr: float = 0.03, seed: int = 13):
        self.ridge = ridge
        self.epochs = epochs
        self.lr = lr
        self.seed = seed
        self.weights: List[List[float]] = []
        self.y_mean: List[float] = []

    def fit(self, x: List[List[float]], y: List[List[float]]) -> "LinearMultiOutputGD":
        if not x or not y:
            fail("empty training matrix")
        n = len(x)
        p = len(x[0]) + 1
        d = len(y[0])
        self.y_mean = [sum(row[k] for row in y) / n for k in range(d)]
        yc = [[row[k] - self.y_mean[k] for k in range(d)] for row in y]
        rng = random.Random(self.seed)
        self.weights = [[rng.uniform(-0.001, 0.001) for _ in range(d)] for _ in range(p)]
        xb = [[1.0] + row for row in x]
        lr = self.lr
        for _ in range(self.epochs):
            grad = [[0.0 for _ in range(d)] for _ in range(p)]
            for xi, yi in zip(xb, yc):
                pred = [sum(xi[j] * self.weights[j][k] for j in range(p)) for k in range(d)]
                for j, xij in enumerate(xi):
                    for k in range(d):
                        grad[j][k] += (pred[k] - yi[k]) * xij / n
            for j in range(1, p):
                for k in range(d):
                    grad[j][k] += self.ridge * self.weights[j][k]
            for j in range(p):
                for k in range(d):
                    self.weights[j][k] -= lr * grad[j][k]
        return self

    def predict(self, x: List[List[float]]) -> List[List[float]]:
        xb = [[1.0] + row for row in x]
        d = len(self.y_mean)
        return [
            [self.y_mean[k] + sum(xi[j] * self.weights[j][k] for j in range(len(xi))) for k in range(d)]
            for xi in xb
        ]


class RidgeMultiOutput:
    def __init__(self, ridge: float = 1e-3):
        self.ridge = ridge
        self.model = None

    def fit(self, x: List[List[float]], y: List[List[float]]) -> "RidgeMultiOutput":
        if not x or not y:
            fail("empty training matrix")
        try:
            from sklearn.linear_model import Ridge
        except Exception:
            self.model = LinearMultiOutputGD(ridge=self.ridge, epochs=300, lr=0.02).fit(x, y)
            return self
        self.model = Ridge(alpha=self.ridge, fit_intercept=True).fit(x, y)
        return self

    def predict(self, x: List[List[float]]) -> List[List[float]]:
        if self.model is None:
            fail("model has not been fit")
        pred = self.model.predict(x)
        return pred.tolist() if hasattr(pred, "tolist") else pred


def make_design(
    states: List[List[float]],
    meta: Sequence[Dict[str, str]],
    categorical_fields: Sequence[str],
    fit_meta: Sequence[Dict[str, str]] | None = None,
) -> Tuple[List[List[float]], FeatureEncoder]:
    encoder = FeatureEncoder(categorical_fields).fit(fit_meta or meta)
    cats = encoder.transform(meta)
    design = [list(s) + c for s, c in zip(states, cats)]
    return design, encoder


def evaluate_model(
    name: str,
    train_meta: Sequence[Dict[str, str]],
    test_meta: Sequence[Dict[str, str]],
    train_x_state: List[List[float]],
    test_x_state: List[List[float]],
    train_y: List[List[float]],
    test_y: List[List[float]],
    categorical_fields: Sequence[str],
    epochs: int,
    lr: float,
    ridge: float,
) -> Dict[str, object]:
    encoder = FeatureEncoder(categorical_fields).fit(train_meta)
    train_design = [list(s) + c for s, c in zip(train_x_state, encoder.transform(train_meta))]
    test_design = [list(s) + c for s, c in zip(test_x_state, encoder.transform(test_meta))]
    train_design, test_design = standardize_train_test(train_design, test_design)
    model = RidgeMultiOutput(ridge=ridge).fit(train_design, train_y)
    pred = model.predict(test_design)
    return {
        "model": name,
        "n_train": len(train_y),
        "n_test": len(test_y),
        "mse": mse(test_y, pred),
        "r2": r2_score(test_y, pred),
        "cosine_similarity": cosine_similarity(test_y, pred),
        "categorical_fields": "+".join(categorical_fields) or "none",
    }


def model_specs() -> Dict[str, Sequence[str]]:
    return {
        "M0_state": [],
        "M1_flat_task": ["task_id"],
        "M2_strong_task": ["task_id", "domain", "load"],
        "M3_cwp": ["source_cwp", "domain", "load"],
        "M4_task_plus_cwp": ["task_id", "source_cwp", "domain", "load"],
    }


def subset_by_indices(items: Sequence, indices: Sequence[int]) -> List:
    return [items[i] for i in indices]


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def grouped_mean(rows: Sequence[Dict[str, object]], group_field: str, value_field: str) -> Dict[str, float]:
    buckets: Dict[str, List[float]] = defaultdict(list)
    for row in rows:
        group = str(row.get(group_field, "NA"))
        try:
            buckets[group].append(float(row[value_field]))
        except Exception:
            pass
    return {k: mean(v) for k, v in buckets.items()}


def subject_metric_differences(
    rows: Sequence[Dict[str, str]],
    baseline_model: str,
    comparison_model: str,
    metric: str = "mse",
    subject_field: str = "heldout_subject",
) -> List[Dict[str, object]]:
    by_subject_model: Dict[Tuple[str, str], List[float]] = defaultdict(list)
    for row in rows:
        subject = row.get(subject_field) or row.get("subject") or "NA"
        model = row.get("model", "")
        if model not in {baseline_model, comparison_model}:
            continue
        try:
            by_subject_model[(subject, model)].append(float(row[metric]))
        except Exception:
            continue
    out = []
    subjects = sorted({s for s, _ in by_subject_model})
    for subject in subjects:
        b = by_subject_model.get((subject, baseline_model), [])
        c = by_subject_model.get((subject, comparison_model), [])
        if b and c:
            baseline = mean(b)
            comparison = mean(c)
            out.append(
                {
                    "subject": subject,
                    "baseline_model": baseline_model,
                    "comparison_model": comparison_model,
                    "metric": metric,
                    "baseline": baseline,
                    "comparison": comparison,
                    "difference_comparison_minus_baseline": comparison - baseline,
                    "improvement_for_error_metric": baseline - comparison,
                }
            )
    return out


def bootstrap_ci(values: Sequence[float], n_boot: int = 2000, seed: int = 13, alpha: float = 0.05) -> Tuple[float, float]:
    if not values:
        return float("nan"), float("nan")
    rng = random.Random(seed)
    boots = []
    vals = list(values)
    for _ in range(n_boot):
        sample = [rng.choice(vals) for _ in vals]
        boots.append(mean(sample))
    boots.sort()
    lo = boots[max(0, int((alpha / 2) * len(boots)) - 1)]
    hi = boots[min(len(boots) - 1, int((1 - alpha / 2) * len(boots)))]
    return lo, hi


def sign_flip_p(values: Sequence[float], n_perm: int = 10000, seed: int = 13) -> float:
    vals = list(values)
    if not vals:
        return float("nan")
    observed = abs(mean(vals))
    rng = random.Random(seed)
    extreme = 0
    for _ in range(n_perm):
        flipped = [v if rng.random() < 0.5 else -v for v in vals]
        if abs(mean(flipped)) >= observed:
            extreme += 1
    return (extreme + 1) / (n_perm + 1)


def fdr_bh(p_values: Sequence[float]) -> List[float]:
    indexed = [(i, p) for i, p in enumerate(p_values) if not math.isnan(p)]
    m = len(indexed)
    q = [float("nan")] * len(p_values)
    if m == 0:
        return q
    indexed.sort(key=lambda x: x[1])
    prev = 1.0
    for rank, (idx, p) in reversed(list(enumerate(indexed, start=1))):
        val = min(prev, p * m / rank)
        q[idx] = val
        prev = val
    return q


def add_common_model_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--states", default=root_path("state_extraction", "stage_states.csv"))
    parser.add_argument("--epochs", type=int, default=500)
    parser.add_argument("--lr", type=float, default=0.02)
    parser.add_argument("--ridge", type=float, default=1e-3)
