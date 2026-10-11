from __future__ import annotations

import argparse
import os
import subprocess
import sys


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def run(cmd: list[str]) -> None:
    print("RUN", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Paper 1 E1-E8 in protocol order.")
    parser.add_argument("--events-glob", default=os.path.join("data_raw", "ds001635", "**", "*events.tsv"))
    parser.add_argument("--timeseries-glob", default=os.path.join("state_extraction", "input_timeseries", "**", "*.csv"))
    parser.add_argument("--bold-glob", default=os.path.join("data_raw", "ds001635", "**", "*_bold.nii.gz"))
    parser.add_argument("--atlas-img", default="")
    parser.add_argument("--native-grid", action="store_true")
    parser.add_argument("--grid-bins", default="6,6,6")
    parser.add_argument("--tr", default="")
    parser.add_argument("--external-states", default=os.path.join("external_validation", "stage_states_external.csv"))
    parser.add_argument("--external-events-glob", default=os.path.join("data_raw", "ds001634", "**", "*events.tsv"))
    parser.add_argument("--external-bold-glob", default=os.path.join("data_raw", "ds001634", "**", "*_bold.nii.gz"))
    parser.add_argument("--external-timeseries-out-dir", default=os.path.join("external_validation", "input_timeseries"))
    parser.add_argument("--epochs", default="500")
    parser.add_argument("--e6-permutations", default="100")
    args = parser.parse_args()

    py = sys.executable
    e1 = [
        py,
        "scripts/e1_extract_states.py",
        "--events-glob",
        args.events_glob,
        "--timeseries-glob",
        args.timeseries_glob,
    ]
    if args.bold_glob:
        e1.extend(["--bold-glob", args.bold_glob])
    if args.native_grid or args.bold_glob:
        e1.extend(["--native-grid", "--grid-bins", args.grid_bins])
    if args.atlas_img:
        e1.extend(["--atlas-img", args.atlas_img])
    if args.tr:
        e1.extend(["--tr", args.tr])
    run(
        [
            py,
            "scripts/e0_data_qc_audit.py",
            "--events-glob",
            args.events_glob,
            "--timeseries-glob",
            args.timeseries_glob,
            "--external-states",
            args.external_states,
        ]
    )
    run(e1)
    run([py, "scripts/e2_cwp_existence.py", "--states", "state_extraction/stage_states.csv"])
    run([py, "scripts/e3_task_vs_cwp.py", "--states", "state_extraction/stage_states.csv", "--epochs", args.epochs])
    run([py, "scripts/e4_unseen_combination.py", "--states", "state_extraction/stage_states.csv", "--epochs", args.epochs])
    run([py, "scripts/e5_unseen_domain.py", "--states", "state_extraction/stage_states.csv", "--epochs", args.epochs])
    run(
        [
            py,
            "scripts/e6_null_falsification.py",
            "--states",
            "state_extraction/stage_states.csv",
            "--epochs",
            args.epochs,
            "--permutations",
            args.e6_permutations,
        ]
    )
    external_events = os.path.join(ROOT, args.external_events_glob)
    external_bold = os.path.join(ROOT, args.external_bold_glob)
    if args.external_events_glob and args.external_bold_glob:
        run(
            [
                py,
                "scripts/e1_extract_states.py",
                "--events-glob",
                args.external_events_glob,
                "--bold-glob",
                args.external_bold_glob,
                "--native-grid",
                "--grid-bins",
                args.grid_bins,
                "--tr",
                args.tr or "2.0",
                "--timeseries-out-dir",
                args.external_timeseries_out_dir,
                "--out",
                args.external_states,
            ]
        )
    if os.path.isfile(os.path.join(ROOT, args.external_states)):
        run(
            [
                py,
                "scripts/e7_external_dataset.py",
                "--train-states",
                "state_extraction/stage_states.csv",
                "--external-states",
                args.external_states,
                "--epochs",
                args.epochs,
            ]
        )
    else:
        print(f"SKIP E7: external states not found at {args.external_states}")
    run([py, "scripts/e8_statistics_reproduction.py"])


if __name__ == "__main__":
    main()
