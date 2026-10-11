from __future__ import annotations

import argparse
import csv
import json
import shlex
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
HCP = PROJECT / "paper5" / "data_hcp_ya_2025" / "downloads" / "HCP_1200"
SUBJECT_MANIFEST = PROJECT / "paper5" / "data_hcp_ya_2025" / "hcp_ya_2025_100_unrelated_subjects_browser_manifest.csv"
RESULTS = ROOT / "results"
DATA_MANIFEST = ROOT / "data_manifest"
OUT_ROOT = ROOT / "structural_connectomes" / "mrtrix_act_sift2_smoke"
FREESURFER_LUT = ROOT / "resources" / "FreeSurferColorLUT.txt"
WSL_DISTRO = "Ubuntu"
MAMBA_PREFIX = "$HOME/mamba-envs/p7-neuro"
MRTRIX_FS_DEFAULT = "/home/a5993/mamba-envs/p7-neuro/share/mrtrix3/labelconvert/fs_default.txt"


def to_wsl_path(path: Path) -> str:
    resolved = str(path.resolve())
    drive = resolved[0].lower()
    rest = resolved[2:].replace("\\", "/")
    return f"/mnt/{drive}{rest}"


def run_wsl(command: str, timeout_seconds: int = 1800) -> dict:
    wrapped = (
        f'$HOME/.local/bin/micromamba run -p "{MAMBA_PREFIX}" '
        f"bash -lc {shlex.quote(command)}"
    )
    started = time.time()
    proc = subprocess.run(
        ["wsl.exe", "-d", WSL_DISTRO, "--", "bash", "-lc", wrapped],
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
    )
    return {
        "command": command,
        "returncode": proc.returncode,
        "duration_seconds": round(time.time() - started, 3),
        "stdout_tail": proc.stdout[-5000:],
        "stderr_tail": proc.stderr[-5000:],
    }


def read_manifest_subjects(limit: int) -> list[str]:
    if not SUBJECT_MANIFEST.exists():
        raise FileNotFoundError(SUBJECT_MANIFEST)
    rows = list(csv.DictReader(SUBJECT_MANIFEST.open("r", encoding="utf-8-sig", newline="")))
    return [row["Subject ID"] for row in rows if row.get("Subject ID")][:limit]


def file_complete(path: Path, min_bytes: int = 1) -> bool:
    return path.exists() and path.stat().st_size >= min_bytes


def connectome_qc(connectome: Path, assignments: Path) -> dict:
    if not connectome.exists():
        return {"exists": False}
    n_rows = 0
    n_cols = 0
    nonzero_edges = 0
    total_weight = 0.0
    max_weight = 0.0
    with connectome.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            n_rows += 1
            n_cols = max(n_cols, len(row))
            for value in row:
                try:
                    weight = float(value)
                except ValueError:
                    continue
                if weight != 0.0:
                    nonzero_edges += 1
                    total_weight += weight
                    max_weight = max(max_weight, weight)
    assignment_rows = 0
    if assignments.exists():
        with assignments.open("r", encoding="utf-8", errors="ignore") as f:
            assignment_rows = sum(1 for line in f if line.strip())
    return {
        "exists": True,
        "bytes": connectome.stat().st_size,
        "rows": n_rows,
        "columns": n_cols,
        "nonzero_edges": nonzero_edges,
        "total_weight": total_weight,
        "max_weight": max_weight,
        "assignments_rows": assignment_rows,
    }


def step(name: str, command: str, target: Path, min_bytes: int, timeout: int) -> dict:
    if file_complete(target, min_bytes):
        return {
            "step": name,
            "command": command,
            "returncode": 0,
            "skipped_existing_output": True,
            "target": str(target),
            "target_bytes": target.stat().st_size,
        }
    result = run_wsl(command, timeout_seconds=timeout)
    result["step"] = name
    result["target"] = str(target)
    result["target_exists_after"] = target.exists()
    result["target_bytes_after"] = target.stat().st_size if target.exists() else 0
    if result["returncode"] == 0 and not file_complete(target, min_bytes):
        result["returncode"] = 3
        result["error"] = "TargetMissingOrTooSmallAfterSuccessfulCommand"
    return result


def run_subject(subject: str) -> dict:
    subject_root = HCP / subject
    out_root = OUT_ROOT / subject
    aparc_aseg = subject_root / "T1w" / "aparc+aseg.nii.gz"
    wmfod = out_root / "wmfod_ext4.mif"
    tracks = out_root / "tracks_5k_ext4_msmt.tck"
    weights = out_root / "sift2_weights_ext4_msmt.txt"
    missing = [
        name
        for name, path in {
            "aparc_aseg": aparc_aseg,
            "FreeSurferColorLUT": FREESURFER_LUT,
            "wmfod_ext4": wmfod,
            "tracks_5k_ext4_msmt": tracks,
            "sift2_weights_ext4_msmt": weights,
        }.items()
        if not path.exists()
    ]
    if missing:
        return {"subject": subject, "status": "BLOCKED_MISSING_INPUTS_FOR_LABELCONVERT_QC", "missing": missing}

    nodes_fsdefault = out_root / "nodes_fsdefault.mif"
    nodes_fsdefault_dwi = out_root / "nodes_fsdefault_dwi.mif"
    connectome = out_root / "connectome_sift2_ext4_msmt_fsdefault84_smoke.csv"
    assignments = out_root / "assignments_ext4_msmt_fsdefault84.csv"
    p = {
        "aparc_aseg": shlex.quote(to_wsl_path(aparc_aseg)),
        "freesurfer_lut": shlex.quote(to_wsl_path(FREESURFER_LUT)),
        "wmfod": shlex.quote(to_wsl_path(wmfod)),
        "tracks": shlex.quote(to_wsl_path(tracks)),
        "weights": shlex.quote(to_wsl_path(weights)),
        "nodes_fsdefault": shlex.quote(to_wsl_path(nodes_fsdefault)),
        "nodes_fsdefault_dwi": shlex.quote(to_wsl_path(nodes_fsdefault_dwi)),
        "connectome": shlex.quote(to_wsl_path(connectome)),
        "assignments": shlex.quote(to_wsl_path(assignments)),
    }
    commands = [
        (
            "labelconvert_fsdefault84",
            f"labelconvert {p['aparc_aseg']} {p['freesurfer_lut']} {MRTRIX_FS_DEFAULT} {p['nodes_fsdefault']} -force",
            nodes_fsdefault,
            1_000_000,
            1800,
        ),
        (
            "nodes_fsdefault_resample_to_dwi",
            f"mrtransform {p['nodes_fsdefault']} -template {p['wmfod']} {p['nodes_fsdefault_dwi']} -interp nearest -force",
            nodes_fsdefault_dwi,
            1_000_000,
            1800,
        ),
        (
            "tck2connectome_fsdefault84",
            f"tck2connectome {p['tracks']} {p['nodes_fsdefault_dwi']} {p['connectome']} -tck_weights_in {p['weights']} -symmetric -zero_diagonal -out_assignment {p['assignments']} -force",
            connectome,
            1,
            1800,
        ),
    ]
    results = []
    for name, command, target, min_bytes, timeout in commands:
        result = step(name, command, target, min_bytes, timeout)
        results.append(result)
        if result["returncode"] != 0:
            return {"subject": subject, "status": "FAILED_LABELCONVERT_CONNECTOME_QC", "failed_step": name, "commands": results}
    stderr = "\n".join(result.get("stderr_tail", "") for result in results)
    load_bearing_warning = any(
        marker in stderr
        for marker in [
            "do not have any streamlines assigned",
            "poor parcellation image preparation",
            "poor registration",
        ]
    )
    return {
        "subject": subject,
        "status": "PASS_LABELCONVERT_CONNECTOME_QC",
        "connectome": str(connectome),
        "connectome_qc": connectome_qc(connectome, assignments),
        "load_bearing_tck2connectome_warning": load_bearing_warning,
        "commands": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subjects", nargs="*")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    subjects = args.subjects or read_manifest_subjects(args.limit)
    RESULTS.mkdir(parents=True, exist_ok=True)
    DATA_MANIFEST.mkdir(parents=True, exist_ok=True)
    result_path = RESULTS / "p7_e5_labelconvert_connectome_qc.json"
    subject_results = []
    for subject in subjects:
        result = run_subject(subject)
        subject_results.append(result)
        result_path.write_text(
            json.dumps(
                {
                    "paper": "Paper 7",
                    "experiment": "P7-E5-labelconvert-connectome-QC",
                    "status": "RUNNING_OR_PARTIAL_LABELCONVERT_CONNECTOME_QC",
                    "subjects": subjects,
                    "subject_results": subject_results,
                    "claim_boundary": "Atlas/label-conversion QC only. This does not test structural prediction.",
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        if not result["status"].startswith("PASS"):
            break

    all_pass = len(subject_results) == len(subjects) and all(row["status"] == "PASS_LABELCONVERT_CONNECTOME_QC" for row in subject_results)
    load_bearing_warnings = [row["subject"] for row in subject_results if row.get("load_bearing_tck2connectome_warning")]
    payload = {
        "paper": "Paper 7",
        "experiment": "P7-E5-labelconvert-connectome-QC",
        "status": "PASS_LABELCONVERT_CONNECTOME_QC" if all_pass else "FAILED_LABELCONVERT_CONNECTOME_QC",
        "subjects": subjects,
        "n_subjects": len(subjects),
        "n_subjects_pass": sum(row["status"] == "PASS_LABELCONVERT_CONNECTOME_QC" for row in subject_results),
        "load_bearing_tck2connectome_warning_subjects": load_bearing_warnings,
        "all_load_bearing_tck2connectome_warnings_removed": all_pass and not load_bearing_warnings,
        "subject_results": subject_results,
        "allowed_claim": "FreeSurfer aparc+aseg labels were converted to MRtrix fs_default84 node labels and used to regenerate 5k-streamline SIFT2-weighted connectomes for the tested subjects.",
        "forbidden_claims": [
            "This atlas is final for 100-subject structural prediction.",
            "The P7 structural hypothesis was tested.",
            "Subject-specific structural grounding is supported.",
        ],
    }
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    csv_rows = []
    for row in subject_results:
        qc = row.get("connectome_qc", {})
        csv_rows.append(
            {
                "subject": row.get("subject"),
                "status": row.get("status"),
                "connectome": row.get("connectome"),
                "rows": qc.get("rows"),
                "columns": qc.get("columns"),
                "nonzero_edges": qc.get("nonzero_edges"),
                "total_weight": qc.get("total_weight"),
                "max_weight": qc.get("max_weight"),
                "assignments_rows": qc.get("assignments_rows"),
                "load_bearing_tck2connectome_warning": row.get("load_bearing_tck2connectome_warning"),
            }
        )
    with (DATA_MANIFEST / "p7_e5_labelconvert_connectome_qc_summary.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0]) if csv_rows else ["subject"])
        writer.writeheader()
        writer.writerows(csv_rows)
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not all_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
