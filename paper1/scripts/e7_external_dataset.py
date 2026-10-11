from __future__ import annotations

import argparse

from common import build_transitions, evaluate_model, fail, load_stage_states, model_specs, root_path, write_json, write_table


def main() -> None:
    parser = argparse.ArgumentParser(description="E7: train/develop on ds001635 states and test unchanged on external dataset states.")
    parser.add_argument("--train-states", default=root_path("state_extraction", "stage_states.csv"))
    parser.add_argument("--external-states", default=root_path("external_validation", "stage_states_external.csv"))
    parser.add_argument("--epochs", type=int, default=500)
    parser.add_argument("--lr", type=float, default=0.02)
    parser.add_argument("--ridge", type=float, default=1e-3)
    parser.add_argument("--out", default=root_path("external_validation", "e7_external_dataset_metrics.csv"))
    args = parser.parse_args()

    train_rows, train_roi = load_stage_states(args.train_states)
    ext_rows, ext_roi = load_stage_states(args.external_states)
    if train_roi != ext_roi:
        fail("E7 requires identical roi_* columns between training and external states")
    train_meta, train_x, train_y = build_transitions(train_rows, train_roi)
    ext_meta, ext_x, ext_y = build_transitions(ext_rows, ext_roi)
    if not train_meta or not ext_meta:
        fail("E7 needs train and external transitions")

    results = []
    for model_name, fields in model_specs().items():
        row = evaluate_model(
            model_name,
            train_meta,
            ext_meta,
            train_x,
            ext_x,
            train_y,
            ext_y,
            fields,
            epochs=args.epochs,
            lr=args.lr,
            ridge=args.ridge,
        )
        row["experiment"] = "E7"
        row["train_states"] = args.train_states
        row["external_states"] = args.external_states
        row["external_subject"] = "ALL_EXTERNAL"
        results.append(row)

    external_subjects = sorted({m["subject"] for m in ext_meta if m["subject"]})
    for external_subject in external_subjects:
        test_idx = [i for i, m in enumerate(ext_meta) if m["subject"] == external_subject]
        if not test_idx:
            continue
        for model_name, fields in model_specs().items():
            row = evaluate_model(
                model_name,
                train_meta,
                [ext_meta[i] for i in test_idx],
                train_x,
                [ext_x[i] for i in test_idx],
                train_y,
                [ext_y[i] for i in test_idx],
                fields,
                epochs=args.epochs,
                lr=args.lr,
                ridge=args.ridge,
            )
            row["experiment"] = "E7"
            row["train_states"] = args.train_states
            row["external_states"] = args.external_states
            row["external_subject"] = external_subject
            results.append(row)

    write_table(args.out, results)
    write_json(
        root_path("external_validation", "e7_external_dataset_summary.json"),
        {
            "experiment": "E7",
            "status": "completed_not_claim_validated",
            "train_states": args.train_states,
            "external_states": args.external_states,
            "output": args.out,
            "ontology_changed": False,
        },
    )
    print(f"E7 wrote metrics to {args.out}")


if __name__ == "__main__":
    main()
