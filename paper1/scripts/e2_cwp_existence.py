from __future__ import annotations

import argparse
import math
from collections import Counter, defaultdict
from typing import Dict, List, Sequence

from common import accuracy, fail, load_stage_states, macro_f1, mean_vector, root_path, vector_from_row, write_json, write_table


def nearest_centroid_predict(train_x: Sequence[Sequence[float]], train_y: Sequence[str], test_x: Sequence[Sequence[float]]) -> List[str]:
    by_label: Dict[str, List[Sequence[float]]] = defaultdict(list)
    for x, y in zip(train_x, train_y):
        by_label[y].append(x)
    centroids = {label: mean_vector(rows) for label, rows in by_label.items()}
    preds = []
    for x in test_x:
        best_label = None
        best_dist = float("inf")
        for label, centroid in centroids.items():
            dist = sum((a - b) ** 2 for a, b in zip(x, centroid))
            if dist < best_dist:
                best_dist = dist
                best_label = label
        preds.append(best_label or "NA")
    return preds


def main() -> None:
    parser = argparse.ArgumentParser(description="E2: test ENCODE/MAINTAIN/PROBE separability with held-out subjects or runs.")
    parser.add_argument("--states", default=root_path("state_extraction", "stage_states.csv"))
    parser.add_argument("--split", choices=["subject", "run"], default="subject")
    parser.add_argument("--out", default=root_path("results", "e2_cwp_existence_metrics.csv"))
    args = parser.parse_args()

    rows, roi_cols = load_stage_states(args.states)
    rows = [r for r in rows if r.get("cwp") in {"ENCODE", "MAINTAIN", "PROBE"}]
    if len(rows) < 6:
        fail("E2 needs at least 6 ENCODE/MAINTAIN/PROBE rows")
    key = "subject" if args.split == "subject" else "run"
    groups = sorted({r.get(key, "") for r in rows if r.get(key, "")})
    if len(groups) < 2:
        fail(f"E2 needs at least two {key} groups for held-out evaluation")

    fold_rows = []
    all_true: List[str] = []
    all_pred: List[str] = []
    for group in groups:
        train = [r for r in rows if r.get(key) != group]
        test = [r for r in rows if r.get(key) == group]
        train_labels = sorted({r["cwp"] for r in train})
        test_labels = sorted({r["cwp"] for r in test})
        if len(train_labels) < 2 or not set(test_labels).issubset(set(train_labels)):
            continue
        train_x = [vector_from_row(r, roi_cols) for r in train]
        test_x = [vector_from_row(r, roi_cols) for r in test]
        train_y = [r["cwp"] for r in train]
        test_y = [r["cwp"] for r in test]
        pred = nearest_centroid_predict(train_x, train_y, test_x)
        all_true.extend(test_y)
        all_pred.extend(pred)
        fold_rows.append(
            {
                "heldout_group": group,
                "n_train": len(train),
                "n_test": len(test),
                "accuracy": accuracy(test_y, pred),
                "macro_f1": macro_f1(test_y, pred),
                "train_labels": ";".join(train_labels),
                "test_labels": ";".join(test_labels),
            }
        )
    if not fold_rows:
        fail("no valid E2 folds; check that each held-out group contains labels represented in training")
    summary = {
        "experiment": "E2",
        "split": args.split,
        "n_folds": len(fold_rows),
        "n_rows": len(rows),
        "overall_accuracy": accuracy(all_true, all_pred),
        "overall_macro_f1": macro_f1(all_true, all_pred),
        "label_counts": Counter(all_true),
        "status": "completed_not_claim_validated",
    }
    write_table(args.out, fold_rows)
    write_json(root_path("results", "e2_cwp_existence_summary.json"), summary)
    print(f"E2 wrote metrics to {args.out}")


if __name__ == "__main__":
    main()
