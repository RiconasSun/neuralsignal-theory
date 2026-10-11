from __future__ import annotations

import argparse
import copy
import os
import random
from collections import defaultdict
from typing import Dict, List

from common import (
    build_transitions,
    evaluate_model,
    fail,
    load_stage_states,
    mean,
    model_specs,
    root_path,
    write_json,
    write_table,
)


def permute_labels(meta: List[Dict[str, str]], seed: int) -> List[Dict[str, str]]:
    rng = random.Random(seed)
    out = copy.deepcopy(meta)
    labels = [m["source_cwp"] for m in out]
    rng.shuffle(labels)
    for m, label in zip(out, labels):
        m["source_cwp"] = label
    return out


def domain_load_preserving_shuffle(meta: List[Dict[str, str]], seed: int) -> List[Dict[str, str]]:
    rng = random.Random(seed)
    out = copy.deepcopy(meta)
    buckets: Dict[tuple[str, str], List[int]] = defaultdict(list)
    for i, m in enumerate(out):
        buckets[(m["domain"], m["load"])].append(i)
    for indices in buckets.values():
        labels = [out[i]["source_cwp"] for i in indices]
        rng.shuffle(labels)
        for i, label in zip(indices, labels):
            out[i]["source_cwp"] = label
    return out


def pseudo_cwp(meta: List[Dict[str, str]], seed: int) -> List[Dict[str, str]]:
    rng = random.Random(seed)
    out = copy.deepcopy(meta)
    labels = [m["source_cwp"] for m in out]
    rng.shuffle(labels)
    for m, label in zip(out, labels):
        m["source_cwp"] = f"PSEUDO_{label}"
    return out


def subject_shuffle(meta: List[Dict[str, str]], seed: int) -> List[Dict[str, str]]:
    rng = random.Random(seed)
    out = copy.deepcopy(meta)
    by_subject = defaultdict(list)
    for m in out:
        by_subject[m["subject"]].append(m["source_cwp"])
    subjects = sorted(by_subject)
    labels_by_subject = {s: list(by_subject[s]) for s in subjects}
    shuffled_subjects = subjects[:]
    rng.shuffle(shuffled_subjects)
    replacement = dict(zip(subjects, shuffled_subjects))
    counters = defaultdict(int)
    for m in out:
        source = replacement[m["subject"]]
        labels = labels_by_subject[source]
        idx = counters[source] % len(labels)
        counters[source] += 1
        m["source_cwp"] = labels[idx]
    return out


def evaluate_holdout_cells(meta, x_state, y_state, altered_meta, fields, epochs, lr, ridge, max_cells):
    cells = sorted({m["cell_id"] for m in meta})
    if max_cells:
        cells = cells[:max_cells]
    mses = []
    for cell in cells:
        train_idx = [i for i, m in enumerate(meta) if m["cell_id"] != cell]
        test_idx = [i for i, m in enumerate(meta) if m["cell_id"] == cell]
        if not train_idx or not test_idx:
            continue
        row = evaluate_model(
            "M3_cwp",
            [altered_meta[i] for i in train_idx],
            [altered_meta[i] for i in test_idx],
            [x_state[i] for i in train_idx],
            [x_state[i] for i in test_idx],
            [y_state[i] for i in train_idx],
            [y_state[i] for i in test_idx],
            fields,
            epochs,
            lr,
            ridge,
        )
        mses.append(float(row["mse"]))
    return mean(mses)


def main() -> None:
    parser = argparse.ArgumentParser(description="E6: run available null/falsification tests against CWP labels.")
    parser.add_argument("--states", default=root_path("state_extraction", "stage_states.csv"))
    parser.add_argument("--epochs", type=int, default=300)
    parser.add_argument("--lr", type=float, default=0.02)
    parser.add_argument("--ridge", type=float, default=1e-3)
    parser.add_argument("--permutations", type=int, default=100)
    parser.add_argument("--max-cells", type=int, default=0)
    parser.add_argument("--out", default=root_path("results", "e6_null_falsification_metrics.csv"))
    args = parser.parse_args()

    rows, roi_cols = load_stage_states(args.states)
    meta, x_state, y_state = build_transitions(rows, roi_cols)
    fields = model_specs()["M3_cwp"]

    metrics = []
    true_mse = evaluate_holdout_cells(meta, x_state, y_state, meta, fields, args.epochs, args.lr, args.ridge, args.max_cells)
    metrics.append({"null_test": "true_cwp", "iteration": 0, "mse": true_mse, "status": "completed"})

    transforms = {
        "label_shuffle": permute_labels,
        "pseudo_cwp_ontology": pseudo_cwp,
        "domain_load_preserving_label_shuffle": domain_load_preserving_shuffle,
        "subject_shuffle": subject_shuffle,
    }
    for name, fn in transforms.items():
        for i in range(args.permutations):
            altered = fn(meta, seed=1000 + i)
            null_mse = evaluate_holdout_cells(meta, x_state, y_state, altered, fields, args.epochs, args.lr, args.ridge, args.max_cells)
            metrics.append({"null_test": name, "iteration": i + 1, "mse": null_mse, "status": "completed"})

    time_fields = ["time_bin"]
    time_mse = evaluate_holdout_cells(meta, x_state, y_state, meta, time_fields, args.epochs, args.lr, args.ridge, args.max_cells)
    metrics.append({"null_test": "time_only_baseline", "iteration": 0, "mse": time_mse, "status": "completed"})

    metrics.append(
        {
            "null_test": "motion_only_model",
            "iteration": 0,
            "mse": "",
            "status": "blocked_missing_confounds",
            "note": "requires motion/confound columns or confounds.tsv integration",
        }
    )
    metrics.append(
        {
            "null_test": "boundary_jitter",
            "iteration": 0,
            "mse": "",
            "status": "blocked_requires_e1_rerun",
            "note": "requires event-level boundary perturbation before E1 state extraction",
        }
    )

    pseudo = [float(r["mse"]) for r in metrics if r["null_test"] == "pseudo_cwp_ontology"]
    percentile = sum(1 for x in pseudo if true_mse < x) / len(pseudo) if pseudo else float("nan")
    write_table(args.out, metrics)
    write_json(
        root_path("results", "e6_null_falsification_summary.json"),
        {
            "experiment": "E6",
            "status": "completed_available_nulls_not_claim_validated",
            "true_cwp_mse": true_mse,
            "pseudo_cwp_survival_percentile": percentile,
            "required_survival_percentile": 0.99,
            "blocked_nulls": ["motion_only_model", "boundary_jitter"],
            "output": os.path.abspath(args.out),
        },
    )
    print(f"E6 wrote metrics to {args.out}")


if __name__ == "__main__":
    main()
