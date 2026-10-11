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
OUT_ROOT = ROOT / "structural_connectomes" / "mrtrix_act_sift2_smoke"
FREESURFER_LUT = ROOT / "resources" / "FreeSurferColorLUT.txt"
SUBJECTS = ["100307", "100408", "101107"]
WSL_DISTRO = "Ubuntu"
MAMBA_PREFIX = "$HOME/mamba-envs/p7-neuro"


def to_wsl_path(path: Path) -> str:
    resolved = str(path.resolve())
    drive = resolved[0].lower()
    rest = resolved[2:].replace("\\", "/")
    return f"/mnt/{drive}{rest}"


def run_wsl(command: str, timeout_seconds: int = 3600) -> dict:
    wrapped = (
        f'$HOME/.local/bin/micromamba run -p "{MAMBA_PREFIX}" '
        f"bash -lc {shlex.quote(command)}"
    )
    started = time.time()
    try:
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
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returncode": 124,
            "duration_seconds": round(time.time() - started, 3),
            "stdout_tail": (exc.stdout or "")[-5000:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": (exc.stderr or "")[-5000:] if isinstance(exc.stderr, str) else "",
            "timeout_seconds": timeout_seconds,
            "error": "TimeoutExpired",
        }


def write_status(path: Path, payload: dict) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def file_complete(path: Path, min_bytes: int = 1) -> bool:
    return path.exists() and path.stat().st_size >= min_bytes


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


def subject_files(subject: str) -> dict:
    subject_root = HCP / subject
    return {
        "dwi": subject_root / "T1w" / "Diffusion" / "data.nii.gz",
        "bvecs": subject_root / "T1w" / "Diffusion" / "bvecs",
        "bvals": subject_root / "T1w" / "Diffusion" / "bvals",
        "mask": subject_root / "T1w" / "Diffusion" / "nodif_brain_mask.nii.gz",
        "aparc_aseg": subject_root / "T1w" / "aparc+aseg.nii.gz",
        "freesurfer_lut": FREESURFER_LUT,
    }


def read_manifest_subjects(limit: int) -> list[str]:
    if not SUBJECT_MANIFEST.exists():
        return SUBJECTS[:limit]
    rows = list(csv.DictReader(SUBJECT_MANIFEST.open("r", encoding="utf-8-sig", newline="")))
    subjects = [row["Subject ID"] for row in rows if row.get("Subject ID")]
    return subjects[:limit]


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
    assignments_rows = 0
    if assignments.exists():
        with assignments.open("r", encoding="utf-8", errors="ignore") as f:
            assignments_rows = sum(1 for line in f if line.strip())
    return {
        "exists": True,
        "bytes": connectome.stat().st_size,
        "rows": n_rows,
        "columns": n_cols,
        "nonzero_edges": nonzero_edges,
        "total_weight": total_weight,
        "max_weight": max_weight,
        "assignments_rows": assignments_rows,
    }


def run_subject(subject: str) -> dict:
    files = subject_files(subject)
    out_root = OUT_ROOT / subject
    out_root.mkdir(parents=True, exist_ok=True)
    ext4_ready = out_root / ".ext4_inputs_ready"
    ext4_inputs_reusable = ext4_ready.exists()
    missing = []
    for name, path in files.items():
        if path.exists():
            continue
        if ext4_inputs_reusable and name in {"dwi", "mask"}:
            continue
        missing.append(name)
    if missing:
        return {"subject": subject, "status": "BLOCKED_MISSING_INPUT_FILES", "missing": missing}

    p = {name: shlex.quote(to_wsl_path(path)) for name, path in files.items()}
    out = {name: shlex.quote(to_wsl_path(out_root / name)) for name in [
        "dwi.mif",
        "wm.txt",
        "gm.txt",
        "csf.txt",
        "5tt.mif",
        "5tt_dwi.mif",
        "nodes_dwi.mif",
        "gmwmi_seed.mif",
        "wmfod_ext4.mif",
        "gm_ext4.mif",
        "csf_ext4.mif",
        "tracks_5k_ext4_msmt.tck",
        "sift2_weights_ext4_msmt.txt",
        "connectome_sift2_ext4_msmt_smoke.csv",
        "assignments_ext4_msmt.csv",
        ".ext4_dwi_ready",
        ".ext4_inputs_ready",
    ]}
    ext4 = f"$HOME/p7_msmt_csd_ext4_diagnostic/{subject}"
    results = []
    if ext4_inputs_reusable:
        results.append({
            "step": "reuse_ext4_inputs",
            "returncode": 0,
            "skipped_existing_ext4_inputs": True,
            "target": str(ext4_ready),
            "target_bytes": ext4_ready.stat().st_size,
            "claim_boundary": "Recovery path only: reuses previously copied WSL ext4 DWI/mask inputs after local cache cleanup.",
        })
    commands = []
    if not ext4_inputs_reusable:
        commands.extend([
        ("mrconvert_ext4", f"mkdir -p {ext4} && mrconvert {p['dwi']} {ext4}/dwi.mif -fslgrad {p['bvecs']} {p['bvals']} -force && touch {out['.ext4_dwi_ready']}", out_root / ".ext4_dwi_ready", 0, 3600),
        ("prepare_ext4_inputs", f"mkdir -p {ext4} && if [ ! -s {ext4}/mask.nii.gz ]; then cp {p['mask']} {ext4}/mask.nii.gz; fi && touch {out['.ext4_inputs_ready']}", out_root / ".ext4_inputs_ready", 0, 3600),
        ])
    commands.extend([
        ("dwi2response_ext4", f"cd {ext4} && dwi2response dhollander dwi.mif wm.txt gm.txt csf.txt -mask mask.nii.gz -force -nthreads 4 && cp wm.txt {out['wm.txt']} && cp gm.txt {out['gm.txt']} && cp csf.txt {out['csf.txt']}", out_root / "wm.txt", 1, 7200),
        ("5ttgen_freesurfer", f"5ttgen freesurfer {p['aparc_aseg']} {out['5tt.mif']} -lut {p['freesurfer_lut']} -force -nocrop", out_root / "5tt.mif", 1_000_000, 3600),
        ("dwi2fod_msmt_csd_ext4", f"cd {ext4} && dwi2fod msmt_csd dwi.mif wm.txt wmfod_ext4.mif gm.txt gm_ext4.mif csf.txt csf_ext4.mif -mask mask.nii.gz -shells 5,998,1998,2996 -force -nthreads 4 && cp wmfod_ext4.mif {out['wmfod_ext4.mif']} && cp gm_ext4.mif {out['gm_ext4.mif']} && cp csf_ext4.mif {out['csf_ext4.mif']}", out_root / "wmfod_ext4.mif", 100_000_000, 14400),
        ("5tt_resample_to_dwi", f"mrtransform {out['5tt.mif']} -template {out['wmfod_ext4.mif']} {out['5tt_dwi.mif']} -interp nearest -force", out_root / "5tt_dwi.mif", 1_000_000, 1800),
        ("nodes_resample_to_dwi", f"mrtransform {p['aparc_aseg']} -template {out['wmfod_ext4.mif']} {out['nodes_dwi.mif']} -interp nearest -force", out_root / "nodes_dwi.mif", 1_000_000, 1800),
        ("5tt2gmwmi", f"5tt2gmwmi {out['5tt_dwi.mif']} {out['gmwmi_seed.mif']} -force", out_root / "gmwmi_seed.mif", 1_000_000, 1800),
        ("tckgen_iFOD2_ACT_5k", f"tckgen {out['wmfod_ext4.mif']} {out['tracks_5k_ext4_msmt.tck']} -algorithm iFOD2 -act {out['5tt_dwi.mif']} -backtrack -crop_at_gmwmi -seed_gmwmi {out['gmwmi_seed.mif']} -select 5000 -maxlength 250 -cutoff 0.01 -force -nthreads 1", out_root / "tracks_5k_ext4_msmt.tck", 100_000, 3600),
        ("tcksift2", f"tcksift2 {out['tracks_5k_ext4_msmt.tck']} {out['wmfod_ext4.mif']} {out['sift2_weights_ext4_msmt.txt']} -act {out['5tt_dwi.mif']} -force -nthreads 4", out_root / "sift2_weights_ext4_msmt.txt", 1, 3600),
        ("tck2connectome", f"tck2connectome {out['tracks_5k_ext4_msmt.tck']} {out['nodes_dwi.mif']} {out['connectome_sift2_ext4_msmt_smoke.csv']} -tck_weights_in {out['sift2_weights_ext4_msmt.txt']} -symmetric -zero_diagonal -out_assignment {out['assignments_ext4_msmt.csv']} -force", out_root / "connectome_sift2_ext4_msmt_smoke.csv", 1, 3600),
    ])

    for name, command, target, min_bytes, timeout in commands:
        result = step(name, command, target, min_bytes, timeout)
        results.append(result)
        if result["returncode"] != 0:
            return {"subject": subject, "status": "FAILED_SUBJECT_FINAL_ROUTE_SMOKE", "failed_step": name, "commands": results}
        if name == "prepare_ext4_inputs" and ext4_ready.exists() and files["dwi"].exists():
            local_dwi = files["dwi"].resolve()
            hcp_root = HCP.resolve()
            if hcp_root in local_dwi.parents:
                local_size = local_dwi.stat().st_size
                local_dwi.unlink()
                results.append({
                    "step": "drop_local_raw_dwi_after_ext4_inputs",
                    "returncode": 0,
                    "removed_path": str(local_dwi),
                    "removed_bytes": local_size,
                    "claim_boundary": "Lean-storage cache cleanup only: raw HCP DWI can be re-downloaded from authorized access; final connectome outputs are preserved.",
                })

    connectome = out_root / "connectome_sift2_ext4_msmt_smoke.csv"
    assignments = out_root / "assignments_ext4_msmt.csv"
    warnings = []
    for result in results:
        stderr_tail = result.get("stderr_tail", "")
        for marker in ["warning", "unassigned", "missing", "No streamline"]:
            if marker.lower() in stderr_tail.lower():
                warnings.append({"step": result.get("step"), "marker": marker, "stderr_tail": stderr_tail[-1200:]})
                break
    return {
        "subject": subject,
        "status": "PASS_SUBJECT_FINAL_ROUTE_SMOKE",
        "connectome": str(connectome),
        "connectome_bytes": connectome.stat().st_size if connectome.exists() else 0,
        "connectome_qc": connectome_qc(connectome, assignments),
        "qc_warnings": warnings,
        "commands": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subjects", nargs="*", help="Explicit HCP subjects to run.")
    parser.add_argument("--limit", type=int, default=None, help="Use the first N locked manifest subjects.")
    parser.add_argument("--label", default=None, help="Result label, e.g. e4_ten_subject_qc.")
    args = parser.parse_args()

    if args.subjects:
        subjects = args.subjects
    elif args.limit:
        subjects = read_manifest_subjects(args.limit)
    else:
        subjects = SUBJECTS
    label = args.label or ("e4_ten_subject_qc" if len(subjects) == 10 else "e3_three_subject_final_route_smoke")
    status_file = RESULTS / f"p7_{label}.json"
    experiment = f"P7-{label.replace('_', '-')}"

    RESULTS.mkdir(parents=True, exist_ok=True)
    subject_results = []
    for subject in subjects:
        result = run_subject(subject)
        subject_results.append(result)
        write_status(status_file, {
            "paper": "Paper 7",
            "experiment": experiment,
            "status": f"RUNNING_OR_PARTIAL_{label.upper()}",
            "subjects": subjects,
            "subject_results": subject_results,
            "claim_boundary": "ACT/iFOD2/SIFT2 engineering/QC scale-up only. This does not test the P7 structural hypothesis.",
        })
        if not result["status"].startswith("PASS"):
            break

    all_pass = len(subject_results) == len(subjects) and all(row["status"] == "PASS_SUBJECT_FINAL_ROUTE_SMOKE" for row in subject_results)
    if all_pass and len(subjects) == 10:
        status = "PASS_10_SUBJECT_CONNECTOME_QC_SMOKE"
    elif all_pass and len(subjects) == 3:
        status = "PASS_THREE_SUBJECT_FINAL_ROUTE_SMOKE"
    elif all_pass:
        status = f"PASS_{len(subjects)}_SUBJECT_FINAL_ROUTE_SMOKE"
    else:
        status = f"FAILED_{label.upper()}"
    payload = {
        "paper": "Paper 7",
        "experiment": experiment,
        "status": status,
        "subjects": subjects,
        "n_subjects": len(subjects),
        "subject_results": subject_results,
        "allowed_claim": "High-fidelity-route ACT/iFOD2/SIFT2 engineering/QC scale-up completed only if status is PASS. This remains pre-hypothesis-test readiness and does not test structural prediction.",
        "forbidden_claims": [
            "100-subject cohort connectomes generated",
            "P7 structural hypothesis tested",
            "subject-specific structural grounding supported",
            "CWP validated",
            "NAP structurally grounded",
        ],
        "next_action": "If the 10-subject QC passes, freeze atlas/label QC and only then prepare the 100-subject final structural prediction test.",
    }
    write_status(status_file, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not all_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
