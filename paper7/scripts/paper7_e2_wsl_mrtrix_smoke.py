from __future__ import annotations

import json
import shlex
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
HCP = PROJECT / "paper5" / "data_hcp_ya_2025" / "downloads" / "HCP_1200"
RESULTS = ROOT / "results"
OUT_ROOT = ROOT / "structural_connectomes" / "mrtrix_act_sift2_smoke"
SUBJECT = "100307"
WSL_DISTRO = "Ubuntu"
MAMBA_PREFIX = "$HOME/mamba-envs/p7-neuro"
STATUS_FILE = RESULTS / "p7_e2_wsl_mrtrix_smoke.json"
FREESURFER_LUT = ROOT / "resources" / "FreeSurferColorLUT.txt"


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
            "stdout_tail": proc.stdout[-4000:],
            "stderr_tail": proc.stderr[-4000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returncode": 124,
            "duration_seconds": round(time.time() - started, 3),
            "stdout_tail": (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": (exc.stderr or "")[-4000:] if isinstance(exc.stderr, str) else "",
            "timeout_seconds": timeout_seconds,
            "error": "TimeoutExpired",
        }


def write_status(payload: dict) -> None:
    STATUS_FILE.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def file_complete(path: Path, min_bytes: int = 1) -> bool:
    return path.exists() and path.stat().st_size >= min_bytes


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    subject_root = HCP / SUBJECT
    out_root = OUT_ROOT / SUBJECT
    out_root.mkdir(parents=True, exist_ok=True)

    files = {
        "dwi": subject_root / "T1w" / "Diffusion" / "data.nii.gz",
        "bvecs": subject_root / "T1w" / "Diffusion" / "bvecs",
        "bvals": subject_root / "T1w" / "Diffusion" / "bvals",
        "mask": subject_root / "T1w" / "Diffusion" / "nodif_brain_mask.nii.gz",
        "aparc_aseg": subject_root / "T1w" / "aparc+aseg.nii.gz",
        "freesurfer_lut": FREESURFER_LUT,
    }
    missing = [name for name, path in files.items() if not path.exists()]
    if missing:
        payload = {
            "paper": "Paper 7",
            "experiment": "P7-E2-WSL-MRtrix-ACT-SIFT2-smoke",
            "status": "BLOCKED_MISSING_INPUT_FILES",
            "subject": SUBJECT,
            "missing": missing,
            "claim_boundary": "No structural claim can be made from a missing-input smoke test.",
        }
        write_status(payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        raise SystemExit(2)

    p = {name: shlex.quote(to_wsl_path(path)) for name, path in files.items()}
    out = {name: shlex.quote(to_wsl_path(out_root / name)) for name in [
        "dwi.mif",
        "wm.txt",
        "gm.txt",
        "csf.txt",
        "wmfod.mif",
        "gm.mif",
        "csf.mif",
        "5tt.mif",
        "5tt_dwi.mif",
        "nodes_dwi.mif",
        "gmwmi_seed.mif",
        "tracks_5k.tck",
        "sift2_weights.txt",
        "connectome_sift2_smoke.csv",
        "assignments.csv",
    ]}

    steps = [
        {
            "name": "mrconvert",
            "target": out_root / "dwi.mif",
            "min_bytes": 1_000_000_000,
            "timeout": 3600,
            "command": f"mrconvert {p['dwi']} {out['dwi.mif']} -fslgrad {p['bvecs']} {p['bvals']} -force",
        },
        {
            "name": "dwi2response",
            "target": out_root / "wm.txt",
            "min_bytes": 1,
            "timeout": 7200,
            "command": f"dwi2response dhollander {out['dwi.mif']} {out['wm.txt']} {out['gm.txt']} {out['csf.txt']} -mask {p['mask']} -force -nthreads 2",
        },
        {
            "name": "dwi2fod",
            "target": out_root / "wmfod.mif",
            "min_bytes": 100_000_000,
            "timeout": 7200,
            "command": f"dwi2fod msmt_csd {out['dwi.mif']} {out['wm.txt']} {out['wmfod.mif']} {out['gm.txt']} {out['gm.mif']} {out['csf.txt']} {out['csf.mif']} -mask {p['mask']} -force -nthreads 2",
        },
        {
            "name": "5ttgen_freesurfer",
            "target": out_root / "5tt.mif",
            "min_bytes": 1_000_000,
            "timeout": 3600,
            "command": f"5ttgen freesurfer {p['aparc_aseg']} {out['5tt.mif']} -lut {p['freesurfer_lut']} -force -nocrop",
        },
        {
            "name": "5tt_resample_to_dwi",
            "target": out_root / "5tt_dwi.mif",
            "min_bytes": 1_000_000,
            "timeout": 1800,
            "command": f"mrtransform {out['5tt.mif']} -template {out['wmfod.mif']} {out['5tt_dwi.mif']} -interp nearest -force",
        },
        {
            "name": "nodes_resample_to_dwi",
            "target": out_root / "nodes_dwi.mif",
            "min_bytes": 1_000_000,
            "timeout": 1800,
            "command": f"mrtransform {p['aparc_aseg']} -template {out['wmfod.mif']} {out['nodes_dwi.mif']} -interp nearest -force",
        },
        {
            "name": "5tt2gmwmi",
            "target": out_root / "gmwmi_seed.mif",
            "min_bytes": 1_000_000,
            "timeout": 1800,
            "command": f"5tt2gmwmi {out['5tt_dwi.mif']} {out['gmwmi_seed.mif']} -force",
        },
        {
            "name": "tckgen_iFOD2_ACT_5k",
            "target": out_root / "tracks_5k.tck",
            "min_bytes": 100_000,
            "timeout": 3600,
            "command": f"tckgen {out['wmfod.mif']} {out['tracks_5k.tck']} -algorithm iFOD2 -act {out['5tt_dwi.mif']} -backtrack -crop_at_gmwmi -seed_gmwmi {out['gmwmi_seed.mif']} -select 5000 -maxlength 250 -cutoff 0.01 -force -nthreads 1",
        },
        {
            "name": "tcksift2",
            "target": out_root / "sift2_weights.txt",
            "min_bytes": 1,
            "timeout": 3600,
            "command": f"tcksift2 {out['tracks_5k.tck']} {out['wmfod.mif']} {out['sift2_weights.txt']} -act {out['5tt_dwi.mif']} -force -nthreads 2",
        },
        {
            "name": "tck2connectome",
            "target": out_root / "connectome_sift2_smoke.csv",
            "min_bytes": 1,
            "timeout": 3600,
            "command": f"tck2connectome {out['tracks_5k.tck']} {out['nodes_dwi.mif']} {out['connectome_sift2_smoke.csv']} -tck_weights_in {out['sift2_weights.txt']} -symmetric -zero_diagonal -out_assignment {out['assignments.csv']} -force",
        },
    ]

    command_results = []
    status = "PASS_WSL_MRTRIX_ACT_SIFT2_SMOKE"
    for step in steps:
        if file_complete(step["target"], step["min_bytes"]):
            result = {
                "command": step["command"],
                "step": step["name"],
                "returncode": 0,
                "skipped_existing_output": True,
                "target": str(step["target"]),
                "target_bytes": step["target"].stat().st_size,
            }
        else:
            result = run_wsl(step["command"], timeout_seconds=step["timeout"])
            result["step"] = step["name"]
            result["target"] = str(step["target"])
            result["target_exists_after"] = step["target"].exists()
            result["target_bytes_after"] = step["target"].stat().st_size if step["target"].exists() else 0
            if result["returncode"] == 0 and not file_complete(step["target"], step["min_bytes"]):
                result["returncode"] = 3
                result["error"] = "TargetMissingOrTooSmallAfterSuccessfulCommand"
        command_results.append(result)
        interim = {
            "paper": "Paper 7",
            "experiment": "P7-E2-WSL-MRtrix-ACT-SIFT2-smoke",
            "status": "RUNNING_OR_PARTIAL_WSL_MRTRIX_ACT_SIFT2_SMOKE",
            "subject": SUBJECT,
            "completed_steps": [r["step"] for r in command_results if r["returncode"] == 0],
            "last_step": step["name"],
            "commands": command_results,
            "secrets_printed": False,
        }
        write_status(interim)
        if result["returncode"] != 0:
            status = "FAILED_WSL_MRTRIX_ACT_SIFT2_SMOKE"
            break

    connectome = out_root / "connectome_sift2_smoke.csv"
    payload = {
        "paper": "Paper 7",
        "experiment": "P7-E2-WSL-MRtrix-ACT-SIFT2-smoke",
        "status": status,
        "subject": SUBJECT,
        "wsl_distro": WSL_DISTRO,
        "toolchain": "micromamba user-space MRtrix3 3.0.8 in WSL Ubuntu",
        "protocol_deviation": "Uses 5ttgen freesurfer from HCP FreeSurfer aparc+aseg, explicit DWI-grid resampling, and 5,000 iFOD2 streamlines for smoke testing; not the frozen final 10M-streamline cohort analysis.",
        "output_root": str(out_root),
        "connectome_csv": str(connectome),
        "connectome_exists": connectome.exists(),
        "connectome_bytes": connectome.stat().st_size if connectome.exists() else 0,
        "completed_steps": [r["step"] for r in command_results if r["returncode"] == 0],
        "commands": command_results,
        "allowed_claim": "A one-subject high-fidelity MRtrix ACT/iFOD2/SIFT2 smoke connectome was generated only if status is PASS. This does not test the Paper 7 structural hypothesis.",
        "forbidden_claims": [
            "P7 cohort connectomes generated",
            "subject-specific structural connectivity improves transition prediction",
            "structural mechanism established",
            "CWP validated",
            "NAP structurally grounded",
        ],
    }
    write_status(payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    if status != "PASS_WSL_MRTRIX_ACT_SIFT2_SMOKE":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
