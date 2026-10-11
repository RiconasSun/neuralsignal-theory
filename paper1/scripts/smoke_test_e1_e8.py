from __future__ import annotations

import csv
import math
import os
import shutil
import subprocess
import sys
import tempfile


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def write_rows(path: str, rows: list[dict[str, object]], delimiter: str = ",") -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)


def make_fixture(base: str) -> tuple[str, str]:
    events_dir = os.path.join(base, "events")
    ts_dir = os.path.join(base, "timeseries")
    stages = [("Encode", 0.0), ("Maintain", 10.0), ("Probe", 20.0)]
    subjects = ["sub-01", "sub-02", "sub-03"]
    runs = ["run-1", "run-2"]
    domains = ["Num", "Pos"]
    loads = ["Low", "High"]
    for si, sub in enumerate(subjects):
        for ri, run in enumerate(runs):
            ts_rows = []
            for t in range(0, 45):
                ts_rows.append(
                    {
                        "time": float(t),
                        "roi_001": math.sin(t / 5.0) + si * 0.1,
                        "roi_002": math.cos(t / 7.0) + ri * 0.1,
                        "roi_003": (t % 10) / 10.0,
                    }
                )
            write_rows(os.path.join(ts_dir, sub, f"{sub}_task-wm_{run}_timeseries.csv"), ts_rows)

            ev_rows = []
            trial = 0
            for domain in domains:
                for load in loads:
                    trial += 1
                    for stage, onset in stages:
                        ev_rows.append(
                            {
                                "onset": onset + (trial - 1) * 0.25,
                                "duration": 5.0,
                                "trial_type": domain,
                                "load_type": load,
                                "processing_stage": stage,
                            }
                        )
            write_rows(os.path.join(events_dir, sub, f"{sub}_task-wm_{run}_events.tsv"), ev_rows, delimiter="\t")
    return os.path.join(events_dir, "**", "*events.tsv"), os.path.join(ts_dir, "**", "*.csv")


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def assert_exists(path: str) -> None:
    if not os.path.isfile(path):
        raise AssertionError(f"missing expected output: {path}")


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        events_glob, ts_glob = make_fixture(tmp)
        py = sys.executable
        run([py, "scripts/e1_extract_states.py", "--events-glob", events_glob, "--timeseries-glob", ts_glob, "--hrf-lag", "0"])
        shutil.copyfile(
            os.path.join(ROOT, "state_extraction", "stage_states.csv"),
            os.path.join(ROOT, "external_validation", "stage_states_external.csv"),
        )
        run([py, "scripts/e2_cwp_existence.py", "--states", os.path.join(ROOT, "state_extraction", "stage_states.csv"), "--split", "subject"])
        run([py, "scripts/e3_task_vs_cwp.py", "--states", os.path.join(ROOT, "state_extraction", "stage_states.csv"), "--epochs", "10"])
        run([py, "scripts/e4_unseen_combination.py", "--states", os.path.join(ROOT, "state_extraction", "stage_states.csv"), "--epochs", "10", "--min-test", "1"])
        run([py, "scripts/e5_unseen_domain.py", "--states", os.path.join(ROOT, "state_extraction", "stage_states.csv"), "--epochs", "10", "--min-test", "1"])
        run([py, "scripts/e6_null_falsification.py", "--states", os.path.join(ROOT, "state_extraction", "stage_states.csv"), "--epochs", "10", "--permutations", "3", "--max-cells", "2"])
        run([py, "scripts/e7_external_dataset.py", "--train-states", os.path.join(ROOT, "state_extraction", "stage_states.csv"), "--external-states", os.path.join(ROOT, "external_validation", "stage_states_external.csv"), "--epochs", "10"])
        run([py, "scripts/e8_statistics_reproduction.py", "--bootstrap", "20", "--permutations", "20"])

    expected = [
        os.path.join(ROOT, "results", "e5_unseen_domain_metrics.csv"),
        os.path.join(ROOT, "results", "e6_null_falsification_metrics.csv"),
        os.path.join(ROOT, "external_validation", "e7_external_dataset_metrics.csv"),
        os.path.join(ROOT, "results", "primary_metrics.csv"),
        os.path.join(ROOT, "results", "subject_level_effects.csv"),
        os.path.join(ROOT, "results", "claim_audit.json"),
    ]
    for path in expected:
        assert_exists(path)
    print("smoke_test_e1_e8 passed")


if __name__ == "__main__":
    main()
