from __future__ import annotations

import argparse
import os
import subprocess
import sys

from common import root_path


def run(cmd: list[str]) -> None:
    print("+ " + " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Paper 1 E1-E4 in order.")
    parser.add_argument("--events-glob", default=root_path("data_manifest", "**", "*events.tsv"))
    parser.add_argument("--timeseries-glob", default=root_path("state_extraction", "input_timeseries", "**", "*.csv"))
    parser.add_argument("--bold-glob", default="")
    parser.add_argument("--atlas-img", default="")
    parser.add_argument("--tr", default="")
    parser.add_argument("--hrf-lag", default="4.0")
    parser.add_argument("--baseline-seconds", default="4.0")
    parser.add_argument("--epochs", default="500")
    parser.add_argument("--lr", default="0.02")
    parser.add_argument("--ridge", default="0.001")
    args = parser.parse_args()

    scripts = root_path("scripts")
    py = sys.executable
    run(
        [
            py,
            os.path.join(scripts, "e1_extract_states.py"),
            "--events-glob",
            args.events_glob,
            "--timeseries-glob",
            args.timeseries_glob,
            "--bold-glob",
            args.bold_glob,
            "--atlas-img",
            args.atlas_img,
            "--hrf-lag",
            args.hrf_lag,
            "--baseline-seconds",
            args.baseline_seconds,
        ]
        + (["--tr", args.tr] if args.tr else [])
    )
    run([py, os.path.join(scripts, "e2_cwp_existence.py"), "--states", root_path("state_extraction", "stage_states.csv")])
    common = ["--states", root_path("state_extraction", "stage_states.csv"), "--epochs", args.epochs, "--lr", args.lr, "--ridge", args.ridge]
    run([py, os.path.join(scripts, "e3_task_vs_cwp.py"), *common])
    run([py, os.path.join(scripts, "e4_unseen_combination.py"), *common])


if __name__ == "__main__":
    main()
