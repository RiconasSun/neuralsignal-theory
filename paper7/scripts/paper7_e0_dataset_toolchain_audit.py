from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
P5 = PROJECT / "paper5"
HCP = P5 / "data_hcp_ya_2025" / "downloads" / "HCP_1200"
RESULTS = ROOT / "results"
DATA_MANIFEST = ROOT / "data_manifest"


MRTRIX_COMMANDS = [
    "mrconvert",
    "mrinfo",
    "dwi2response",
    "dwi2fod",
    "5ttgen",
    "tckgen",
    "tcksift2",
    "tck2connectome",
    "labelconvert",
]

FSL_COMMANDS = ["flirt", "bet", "eddy", "topup"]


def command_status(command: str) -> dict:
    path = shutil.which(command)
    return {
        "command": command,
        "available": bool(path),
        "path": path,
    }


def subject_file_status(subject_dir: Path) -> dict:
    sid = subject_dir.name
    rels = {
        "dwi_image": Path("T1w/Diffusion/data.nii.gz"),
        "dwi_bvals": Path("T1w/Diffusion/bvals"),
        "dwi_bvecs": Path("T1w/Diffusion/bvecs"),
        "dwi_mask": Path("T1w/Diffusion/nodif_brain_mask.nii.gz"),
        "t1w_aparc_aseg": Path("T1w/aparc+aseg.nii.gz"),
        "t1w_wmparc": Path("T1w/wmparc.nii.gz"),
        "wm_lr_dtseries": Path("MNINonLinear/Results/tfMRI_WM_LR/tfMRI_WM_LR_Atlas_MSMAll.dtseries.nii"),
        "wm_rl_dtseries": Path("MNINonLinear/Results/tfMRI_WM_RL/tfMRI_WM_RL_Atlas_MSMAll.dtseries.nii"),
        "wm_lr_motion": Path("MNINonLinear/Results/tfMRI_WM_LR/Movement_Regressors.txt"),
        "wm_rl_motion": Path("MNINonLinear/Results/tfMRI_WM_RL/Movement_Regressors.txt"),
    }
    out = {"subject": sid}
    for key, rel in rels.items():
        path = subject_dir / rel
        out[key] = path.exists()
        out[f"{key}_bytes"] = path.stat().st_size if path.exists() else 0
    out["eligible_for_gold_connectome"] = all(
        out[key]
        for key in [
            "dwi_image",
            "dwi_bvals",
            "dwi_bvecs",
            "dwi_mask",
            "t1w_aparc_aseg",
            "t1w_wmparc",
        ]
    )
    out["eligible_for_p7_modeling"] = out["eligible_for_gold_connectome"] and all(
        out[key]
        for key in [
            "wm_lr_dtseries",
            "wm_rl_dtseries",
            "wm_lr_motion",
            "wm_rl_motion",
        ]
    )
    return out


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    DATA_MANIFEST.mkdir(parents=True, exist_ok=True)

    subjects = sorted([p for p in HCP.iterdir() if p.is_dir()]) if HCP.exists() else []
    subject_rows = [subject_file_status(p) for p in subjects]
    tool_rows = [command_status(c) for c in MRTRIX_COMMANDS + FSL_COMMANDS]

    mrtrix_ready = all(row["available"] for row in tool_rows if row["command"] in MRTRIX_COMMANDS)
    fsl_ready = all(row["available"] for row in tool_rows if row["command"] in FSL_COMMANDS)
    eligible_subjects = [row["subject"] for row in subject_rows if row["eligible_for_p7_modeling"]]

    candidates = [
        {
            "dataset": "HCP-YA 2025",
            "source": "ConnectomeDB powered by BALSA / hcp-openaccess S3",
            "role": "P7-A primary",
            "task_fmri": True,
            "diffusion_mri": True,
            "t1w": True,
            "motion": True,
            "local_subject_dirs": len(subject_rows),
            "eligible_local_subjects": len(eligible_subjects),
            "license_access": "HCP/BALSA terms required",
            "status": "SELECTED_IF_TOOLCHAIN_READY",
        },
        {
            "dataset": "Other OpenNeuro task-fMRI+dMRI datasets",
            "source": "not selected",
            "role": "fallback only",
            "task_fmri": "unknown",
            "diffusion_mri": "often absent",
            "t1w": "often present",
            "motion": "dataset-dependent",
            "local_subject_dirs": 0,
            "eligible_local_subjects": 0,
            "license_access": "dataset-dependent",
            "status": "NOT_SELECTED_FOR_P7_E0",
        },
    ]

    blockers = []
    if not subjects:
        blockers.append("No local HCP-YA subject directories found under paper5/data_hcp_ya_2025/downloads/HCP_1200.")
    if not eligible_subjects:
        blockers.append("No local subjects have the complete DWI image, bvals/bvecs, anatomy, WM task-fMRI, and motion files required for P7.")
    if not mrtrix_ready:
        missing = [row["command"] for row in tool_rows if row["command"] in MRTRIX_COMMANDS and not row["available"]]
        blockers.append(f"MRtrix3 command set is incomplete: missing {', '.join(missing)}.")
    if not fsl_ready:
        missing = [row["command"] for row in tool_rows if row["command"] in FSL_COMMANDS and not row["available"]]
        blockers.append(f"FSL command set is incomplete: missing {', '.join(missing)}.")

    status = "PASS_E0_READY_FOR_HIGH_FIDELITY_CONNECTOME" if not blockers else "BLOCKED_HIGH_FIDELITY_TRACTOGRAPHY_REQUIREMENTS"

    payload = {
        "experiment": "P7-E0-dataset-feasibility-toolchain-audit",
        "status": status,
        "selected_dataset": "HCP-YA 2025",
        "release_rule": "Use HCP-YA 2025 only; do not mix with 2017 S1200 processing.",
        "local_hcp_root": str(HCP),
        "n_local_subject_dirs": len(subject_rows),
        "n_subjects_eligible_for_p7_modeling": len(eligible_subjects),
        "eligible_subjects_preview": eligible_subjects[:20],
        "mrtrix_ready": mrtrix_ready,
        "fsl_ready": fsl_ready,
        "toolchain": tool_rows,
        "blockers": blockers,
        "claim_boundary": "P7 cannot run or claim high-fidelity structural grounding until HCP DWI/FreeSurfer/tfMRI inputs and MRtrix3 commands are available.",
        "forbidden_claims": [
            "High-fidelity ACT/iFOD2/SIFT2 connectomes were generated.",
            "Subject-specific structural connectivity constrains brain-state dynamics.",
            "P7 structural mechanism is established.",
            "CWP/NAP structural grounding is established.",
        ],
    }

    write_csv(DATA_MANIFEST / "p7_e0_dataset_candidates.csv", candidates)
    write_csv(DATA_MANIFEST / "p7_e0_hcp_subject_file_audit.csv", subject_rows)
    write_csv(RESULTS / "p7_e0_toolchain_audit.csv", tool_rows)
    (RESULTS / "p7_e0_dataset_toolchain_audit.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))

    if blockers:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
