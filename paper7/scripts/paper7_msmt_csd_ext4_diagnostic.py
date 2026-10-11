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
STATUS_FILE = RESULTS / "p7_msmt_csd_ext4_diagnostic.json"
WSL_WORK = "$HOME/p7_msmt_csd_ext4_diagnostic/100307"


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
            "stdout_tail": proc.stdout[-6000:],
            "stderr_tail": proc.stderr[-6000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returncode": 124,
            "duration_seconds": round(time.time() - started, 3),
            "stdout_tail": (exc.stdout or "")[-6000:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": (exc.stderr or "")[-6000:] if isinstance(exc.stderr, str) else "",
            "timeout_seconds": timeout_seconds,
            "error": "TimeoutExpired",
        }


def write_status(payload: dict) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    subject_root = HCP / SUBJECT
    smoke_root = OUT_ROOT / SUBJECT
    required = {
        "source_dwi": smoke_root / "dwi.mif",
        "source_wm": smoke_root / "wm.txt",
        "source_gm": smoke_root / "gm.txt",
        "source_csf": smoke_root / "csf.txt",
        "source_mask": subject_root / "T1w" / "Diffusion" / "nodif_brain_mask.nii.gz",
    }
    missing = [name for name, path in required.items() if not path.exists()]
    if missing:
        payload = {
            "paper": "Paper 7",
            "experiment": "P7-MSMT-CSD-ext4-diagnostic",
            "status": "BLOCKED_MISSING_INPUT_FILES",
            "subject": SUBJECT,
            "missing": missing,
            "claim_boundary": "No final-route structural claim can be made without MSMT-CSD inputs.",
        }
        write_status(payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        raise SystemExit(2)

    p = {name: shlex.quote(to_wsl_path(path)) for name, path in required.items()}
    commands = [
        {
            "name": "prepare_ext4_workspace",
            "timeout": 3600,
            "command": (
                f"mkdir -p {WSL_WORK} && "
                f"test -s {WSL_WORK}/dwi.mif || cp {p['source_dwi']} {WSL_WORK}/dwi.mif && "
                f"test -s {WSL_WORK}/wm.txt || cp {p['source_wm']} {WSL_WORK}/wm.txt && "
                f"test -s {WSL_WORK}/gm.txt || cp {p['source_gm']} {WSL_WORK}/gm.txt && "
                f"test -s {WSL_WORK}/csf.txt || cp {p['source_csf']} {WSL_WORK}/csf.txt && "
                f"test -s {WSL_WORK}/mask.nii.gz || cp {p['source_mask']} {WSL_WORK}/mask.nii.gz"
            ),
        },
        {
            "name": "inspect_shells_and_gradients",
            "timeout": 600,
            "command": (
                f"cd {WSL_WORK} && "
                "mrinfo dwi.mif -shell_bvalues -shell_sizes && "
                "mrinfo dwi.mif -dwgrad | head -n 10 && "
                "mrstats dwi.mif -mask mask.nii.gz -output mean -output std -output min -output max"
            ),
        },
        {
            "name": "msmt_csd_ext4_explicit_shells",
            "timeout": 14400,
            "command": (
                f"cd {WSL_WORK} && "
                "dwi2fod msmt_csd dwi.mif wm.txt wmfod_ext4.mif gm.txt gm_ext4.mif "
                "csf.txt csf_ext4.mif -mask mask.nii.gz -shells 5,998,1998,2996 -force -nthreads 1"
            ),
        },
        {
            "name": "stats_ext4_msmt_outputs",
            "timeout": 1200,
            "command": (
                f"cd {WSL_WORK} && "
                "mrstats wmfod_ext4.mif -output mean -output std -output min -output max && "
                "mrstats gm_ext4.mif -output mean -output std -output min -output max && "
                "mrstats csf_ext4.mif -output mean -output std -output min -output max"
            ),
        },
        {
            "name": "export_ext4_msmt_outputs_to_workspace",
            "timeout": 3600,
            "command": (
                f"cp {WSL_WORK}/wmfod_ext4.mif {shlex.quote(to_wsl_path(smoke_root / 'wmfod_ext4.mif'))} && "
                f"cp {WSL_WORK}/gm_ext4.mif {shlex.quote(to_wsl_path(smoke_root / 'gm_ext4.mif'))} && "
                f"cp {WSL_WORK}/csf_ext4.mif {shlex.quote(to_wsl_path(smoke_root / 'csf_ext4.mif'))}"
            ),
        },
    ]

    results = []
    status = "PASS_MSMT_CSD_EXT4_DIAGNOSTIC_RAN"
    for step in commands:
        result = run_wsl(step["command"], timeout_seconds=step["timeout"])
        result["step"] = step["name"]
        results.append(result)
        write_status({
            "paper": "Paper 7",
            "experiment": "P7-MSMT-CSD-ext4-diagnostic",
            "status": "RUNNING_OR_PARTIAL_MSMT_CSD_EXT4_DIAGNOSTIC",
            "subject": SUBJECT,
            "completed_steps": [row["step"] for row in results if row["returncode"] == 0],
            "last_step": step["name"],
            "commands": results,
            "claim_boundary": "Diagnostic only. Nonzero MSMT-CSD is required before final-route ACT/iFOD2/SIFT2 can proceed.",
        })
        if result["returncode"] != 0:
            status = "FAILED_MSMT_CSD_EXT4_DIAGNOSTIC"
            break

    payload = {
        "paper": "Paper 7",
        "experiment": "P7-MSMT-CSD-ext4-diagnostic",
        "status": status,
        "subject": SUBJECT,
        "wsl_workdir": WSL_WORK,
        "completed_steps": [row["step"] for row in results if row["returncode"] == 0],
        "commands": results,
        "next_action": "If ext4 MSMT-CSD is nonzero, switch the final-route smoke to wmfod_ext4.mif and rerun ACT/iFOD2/SIFT2. If it remains zero, diagnose response/mask/shell compatibility before cohort expansion.",
        "claim_boundary": "This diagnostic does not test the Paper 7 structural hypothesis.",
    }
    write_status(payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    if status != "PASS_MSMT_CSD_EXT4_DIAGNOSTIC_RAN":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
