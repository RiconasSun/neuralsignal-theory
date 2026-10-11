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
    parser = argparse.ArgumentParser(description="E5: train on one domain and test on an unseen domain.")
    add_common_model_args(parser)
    parser.add_argument("--min-test", type=int, default=2)
    parser.add_argument("--out", default=root_path("results", "e5_unseen_domain_metrics.csv"))
    args = parser.parse_args()

    rows, roi_cols = load_stage_states(args.states)
    meta, x_state, y_state = build_transitions(rows, roi_cols)
    domains = sorted({m["domain"] for m in meta if m["domain"] and m["domain"] != "NA"})
    if len(domains) < 2:
        fail("E5 requires at least two domains")

    results = []
    specs = model_specs()
    for heldout_domain in domains:
        train_idx = [i for i, m in enumerate(meta) if m["domain"] != heldout_domain]
        test_idx = [i for i, m in enumerate(meta) if m["domain"] == heldout_domain]
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
            row["heldout_domain"] = heldout_domain
            row["experiment"] = "E5"
            results.append(row)
    if not results:
        fail("E5 produced no unseen-domain folds")
    write_table(args.out, results)
    write_json(
        root_path("results", "e5_unseen_domain_summary.json"),
        {
            "experiment": "E5",
            "status": "completed_not_claim_validated",
            "domain_counts": Counter(m["domain"] for m in meta),
            "heldout_domains": domains,
            "output": args.out,
        },
    )
    print(f"E5 wrote metrics to {args.out}")


if __name__ == "__main__":
    main()
