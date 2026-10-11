from __future__ import annotations

import json
from pathlib import Path

import nibabel as nib
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data_hcp_ya_2025" / "downloads" / "HCP_1200"
RESULTS = ROOT / "results"


def load_text_matrix(path: Path) -> tuple[int, int]:
    arr = np.loadtxt(path)
    if arr.ndim == 1:
        return int(arr.shape[0]), 1
    return int(arr.shape[0]), int(arr.shape[1])


def validate_subject(subject: str) -> dict:
    base = DATA / subject
    wm = base / "MNINonLinear" / "Results"
    diffusion = base / "T1w"
    checks: dict[str, object] = {"subject": subject, "files": {}}

    for run in ["tfMRI_WM_LR", "tfMRI_WM_RL"]:
        run_dir = wm / run
        dt = run_dir / f"{run}_Atlas_MSMAll.dtseries.nii"
        img = nib.load(str(dt))
        shape = tuple(int(x) for x in img.shape)
        checks["files"][f"{run}_dtseries"] = {"path": str(dt.relative_to(ROOT.parent)), "shape": shape}
        motion = run_dir / "Movement_Regressors.txt"
        checks["files"][f"{run}_motion"] = {"path": str(motion.relative_to(ROOT.parent)), "shape": load_text_matrix(motion)}
        ev_dir = run_dir / "EVs"
        ev_files = sorted(ev_dir.glob("*.txt"))
        checks["files"][f"{run}_ev_count"] = len(ev_files)
        checks["files"][f"{run}_ev_names"] = [p.name for p in ev_files]
        tab_files = sorted(run_dir.glob("WM_run*_TAB.txt"))
        checks["files"][f"{run}_tab"] = [str(p.relative_to(ROOT.parent)) for p in tab_files]

    for name in ["dyads1.nii.gz", "dyads2.nii.gz", "dyads3.nii.gz"]:
        p = diffusion / "Diffusion.bedpostX" / name
        img = nib.load(str(p))
        checks["files"][name] = {"path": str(p.relative_to(ROOT.parent)), "shape": tuple(int(x) for x in img.shape)}

    for name in ["bvals", "bvecs"]:
        p = diffusion / "Diffusion" / name
        checks["files"][f"dwi_{name}"] = {"path": str(p.relative_to(ROOT.parent)), "shape": load_text_matrix(p)}

    status_checks = [
        checks["files"]["tfMRI_WM_LR_dtseries"]["shape"][0] > 0,
        checks["files"]["tfMRI_WM_RL_dtseries"]["shape"][0] > 0,
        checks["files"]["tfMRI_WM_LR_motion"]["shape"][0] == checks["files"]["tfMRI_WM_LR_dtseries"]["shape"][0],
        checks["files"]["tfMRI_WM_RL_motion"]["shape"][0] == checks["files"]["tfMRI_WM_RL_dtseries"]["shape"][0],
        checks["files"]["tfMRI_WM_LR_ev_count"] > 0,
        checks["files"]["tfMRI_WM_RL_ev_count"] > 0,
    ]
    checks["status"] = "PASS" if all(status_checks) else "FAIL"
    checks["note"] = "Smoke validates HCP WM CIFTI, motion regressors, EVs/TAB, and BedpostX orientation outputs. It is not a structural-connectome hypothesis test."
    return checks


def main() -> None:
    subjects = sorted(p.name for p in DATA.iterdir() if p.is_dir())
    if not subjects:
        raise SystemExit("No downloaded HCP subject directories found.")
    payload = {"experiment": "P5-HCP-smoke-validate", "subjects": [validate_subject(subjects[0])]}
    payload["status"] = "PASS" if all(row["status"] == "PASS" for row in payload["subjects"]) else "FAIL"
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "hcp_smoke_validate.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
