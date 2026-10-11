from __future__ import annotations

import argparse
from typing import List

from common import (
    add_common_model_args,
    build_transitions,
    evaluate_model,
    fail,
    load_stage_states,
    model_specs,
    root_path,
    write_json,
    write_table,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="E3: run M0-M4 faceoff with leave-one-subject-out evaluation.")
    add_common_model_args(parser)
    parser.add_argument("--out", default=root_path("results", "e3_m0_m4_metrics.csv"))
    args = parser.parse_args()

    rows, roi_cols = load_stage_states(args.states)
    meta, x_state, y_state = build_transitions(rows, roi_cols)
    subjects = sorted({m["subject"] for m in meta if m["subject"]})
    if len(subjects) < 2:
        fail("E3 requires at least two subjects for leave-one-subject-out evaluation")

    results = []
    specs = model_specs()
    for subject in subjects:
        train_idx = [i for i, m in enumerate(meta) if m["subject"] != subject]
        test_idx = [i for i, m in enumerate(meta) if m["subject"] == subject]
        if not train_idx or not test_idx:
            continue
        train_meta = [meta[i] for i in train_idx]
        test_meta = [meta[i] for i in test_idx]
        train_x = [x_state[i] for i in train_idx]
        test_x = [x_state[i] for i in test_idx]
        train_y = [y_state[i] for i in train_idx]
        test_y = [y_state[i] for i in test_idx]
        for model_name, fields in specs.items():
            row = evaluate_model(
                model_name,
                train_meta,
                test_meta,
                train_x,
                test_x,
                train_y,
                test_y,
                fields,
                epochs=args.epochs,
                lr=args.lr,
                ridge=args.ridge,
            )
            row["heldout_subject"] = subject
            row["experiment"] = "E3"
            results.append(row)
    if not results:
        fail("E3 produced no folds")
    write_table(args.out, results)
    by_model = {}
    for model in specs:
        vals = [float(r["mse"]) for r in results if r["model"] == model]
        by_model[model] = sum(vals) / len(vals) if vals else None
    write_json(
        root_path("results", "e3_m0_m4_summary.json"),
        {"experiment": "E3", "status": "completed_not_claim_validated", "mean_mse_by_model": by_model},
    )
    print(f"E3 wrote metrics to {args.out}")


if __name__ == "__main__":
    main()
