from __future__ import annotations

import argparse
from collections import Counter

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
    parser = argparse.ArgumentParser(description="E4: leave-one-combination-out compositionality test.")
    add_common_model_args(parser)
    parser.add_argument("--min-test", type=int, default=2)
    parser.add_argument("--out", default=root_path("results", "e4_unseen_combination_metrics.csv"))
    args = parser.parse_args()

    rows, roi_cols = load_stage_states(args.states)
    meta, x_state, y_state = build_transitions(rows, roi_cols)
    counts = Counter(m["cell_id"] for m in meta)
    cells = sorted(cell for cell, count in counts.items() if count >= args.min_test)
    if len(cells) < 2:
        fail("E4 requires at least two Domain x Load x CWP cells with enough transitions")

    results = []
    specs = model_specs()
    for cell in cells:
        train_idx = [i for i, m in enumerate(meta) if m["cell_id"] != cell]
        test_idx = [i for i, m in enumerate(meta) if m["cell_id"] == cell]
        if not train_idx or len(test_idx) < args.min_test:
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
            row["heldout_cell"] = cell
            row["experiment"] = "E4"
            results.append(row)
    if not results:
        fail("E4 produced no leave-one-cell folds")
    write_table(args.out, results)
    by_model = {}
    for model in specs:
        vals = [float(r["mse"]) for r in results if r["model"] == model]
        by_model[model] = sum(vals) / len(vals) if vals else None
    write_json(
        root_path("results", "e4_unseen_combination_summary.json"),
        {
            "experiment": "E4",
            "status": "completed_not_claim_validated",
            "cell_counts": counts,
            "mean_mse_by_model": by_model,
        },
    )
    print(f"E4 wrote metrics to {args.out}")


if __name__ == "__main__":
    main()
